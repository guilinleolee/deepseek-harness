/**
 * 卡巴格企业平台 · IdP（Casdoor）→ 平台账号 生命周期对账。
 *
 * 背景：平台与 Casdoor 是**两套身份**——Casdoor 答「人是谁」，平台答「这个人
 * 能用哪个实例、用什么模型、额度多少」。两者靠 accounts.json 的 ssoIds 数组
 * 绑定（格式 `provider:<外部id>`，如 `casdoor:employee`）。
 *
 * 缺口：Casdoor 里冻结/删除一个用户，平台账号**不会**自动失效——离职员工的
 * 平台会话（JWT 30 分钟）与虚拟钥匙仍然有效，配额继续扣。这与角色矩阵里
 * 「同步 IdP·待接入（置灰）」那条遗留一致。本模块补上这一条。
 *
 * 语义（刻意保守）：
 * - **只处理** ssoIds 里带该 provider 前缀的账号；纯手工账号（无 IdP 绑定）不受影响。
 * - Casdoor 用户被禁用/删除 → 禁用平台账号：disabled=true、tokenEpoch+1（旧会话立即失效）、
 *   吊销虚拟钥匙（Relay 立即拒绝）。
 * - Casdoor 用户被重新启用 → **不自动恢复**平台账号（恢复可能是误操作的后果，
 *   交人工在成员页点「启用」，避免"一解冻就自动恢复权限"的提权路径）。
 * - admin 账号永不自动禁用。
 * - Casdoor 拉取失败或返回空列表 → **不做任何禁用**（fail-safe：宁可漏禁，
 *   不可因 IdP 抖动把全员锁死）。
 */
import { getOrCreateSecret, loadAccounts, saveAccounts } from './gateway.mjs'
import { revokeVkey } from './relay.mjs'
import { auditAppend } from './audit.mjs'
import { getSsoSecret, loadSsoConfig } from './sso.mjs'
import { deriveKey } from './totp.mjs'

/** 取 provider 的配置；未启用或缺 clientId 时返回 null（调用方跳过）。 */
function providerConfig(dataDir, provider) {
  const config = loadSsoConfig(dataDir)[provider]
  if (config === undefined || config.enabled !== true) return null
  if (typeof config.clientId !== 'string' || config.clientId === '') return null
  return config
}

/**
 * Casdoor 侧的「不可用」判定。
 *
 * 实测（2026-11-04，Casdoor get-users 返回体）：用户对象**没有** `isDisabled`
 * 这个字段——那是应用级字段，不是用户级。真正控制用户能否登录的是：
 * - `isForbidden`：用户被禁止登录（管理台「禁用用户」置的就是它）
 * - `isDeleted` ：软删除
 * 两个值都可能是布尔或字符串（Casdoor 的 xorm 映射会存 'true'/'false' 字符串）。
 */
function isUserDisabled(user) {
  const truthy = (v) => v === true || v === 'true'
  return truthy(user.isForbidden) || truthy(user.isDeleted)
}

/**
 * 执行一次对账。
 *
 * @param {object} opts
 * @param {string} opts.dataDir 平台数据目录（data/）
 * @param {string} [opts.provider='casdoor'] IdP provider 名
 * @param {Function} [opts.fetchImpl=fetch] HTTP 实现（测试可注入）
 * @param {boolean} [opts.dryRun=false] 只报告不落盘
 * @param {string} [opts.ip] 审计里的来源 IP
 * @returns {Promise<object>} 对账结果
 */
export async function syncIdpLifecycle({ dataDir, provider = 'casdoor', fetchImpl = fetch, dryRun = false, ip = null }) {
  const config = providerConfig(dataDir, provider)
  if (config === null) return { ok: false, reason: 'provider_disabled', disabled: [], reenabled: [], checked: 0 }

  const owner = typeof config.organization === 'string' ? config.organization.trim() : ''
  if (owner === '') return { ok: false, reason: 'no_organization', disabled: [], reenabled: [], checked: 0 }

  const key = deriveKey(getOrCreateSecret(dataDir))
  let secret = ''
  try { secret = getSsoSecret(dataDir, provider, key) } catch { secret = '' }
  if (secret === '') return { ok: false, reason: 'no_secret', disabled: [], reenabled: [], checked: 0 }

  // 1) 拉 IdP 用户（失败 → 什么都不做）
  let users = null
  try {
    const basic = Buffer.from(`${config.clientId}:${secret}`).toString('base64')
    const res = await fetchImpl(`${config.apiBase}/api/get-users?owner=${encodeURIComponent(owner)}`, {
      headers: { authorization: `Basic ${basic}` },
    })
    if (!res.ok) return { ok: false, reason: 'idp_http_error', message: `HTTP ${res.status}`, disabled: [], reenabled: [], checked: 0 }
    const body = await res.json()
    if (body.status !== 'ok' || !Array.isArray(body.data)) {
      return { ok: false, reason: 'idp_bad_payload', message: String(body.msg ?? ''), disabled: [], reenabled: [], checked: 0 }
    }
    users = body.data
  } catch (error) {
    return { ok: false, reason: 'idp_unreachable', message: String(error?.message ?? error), disabled: [], reenabled: [], checked: 0 }
  }

  // 空名单 fail-safe：IdP 异常返回空时不禁用任何人（宁可漏禁，不可全锁）
  if (users.length === 0) {
    return { ok: false, reason: 'idp_empty', message: 'IdP 返回空用户列表，本次不做任何禁用', disabled: [], reenabled: [], checked: 0 }
  }

  // 2) 建立外部 id → 用户 的索引（Casdoor 的 id 与 name 都可能出现在绑定里）
  const byExternalId = new Map()
  for (const u of users) {
    if (typeof u.id === 'string' && u.id !== '') byExternalId.set(u.id, u)
    if (typeof u.name === 'string' && u.name !== '') byExternalId.set(u.name, u)
  }

  // 3) 逐个平台账号判定
  const store = loadAccounts(dataDir)
  const disabled = []
  const checked = []
  let changed = false
  for (const rec of store.accounts) {
    const bindings = Array.isArray(rec.ssoIds) ? rec.ssoIds : []
    const bound = bindings.find((s) => typeof s === 'string' && s.startsWith(`${provider}:`))
    if (bound === undefined) continue // 无 IdP 绑定 → 手工账号，不动
    const externalId = bound.slice(provider.length + 1)
    const user = byExternalId.get(externalId)
    checked.push({ account: rec.account, externalId, found: user !== undefined })
    if (user === undefined) {
      // IdP 里已删除该用户 → 禁用
      if (rec.disabled !== true) {
        rec.disabled = true
        rec.tokenEpoch = (rec.tokenEpoch ?? 0) + 1
        changed = true
        disabled.push(rec.account)
        try { revokeVkey(dataDir, { account: rec.account }) } catch { /* 本来就没钥匙 */ }
      }
      continue
    }
    if (isUserDisabled(user) && rec.disabled !== true) {
      rec.disabled = true
      rec.tokenEpoch = (rec.tokenEpoch ?? 0) + 1
      changed = true
      disabled.push(rec.account)
      try { revokeVkey(dataDir, { account: rec.account }) } catch { /* 本来就没钥匙 */ }
    }
  }

  if (changed && !dryRun) saveAccounts(dataDir, store)

  if (disabled.length > 0) {
    // 必须 await：auditAppend 是异步落盘，CLI 路径若用 void 会在写入完成前就退出，
    // 审计事件直接丢失（实测踩过：事件静默消失）。
    await auditAppend({
      actor: { account: 'svc:idp-sync', role: 'admin', ip },
      action: 'security.idp_sync',
      target: provider,
      result: dryRun ? 'deny' : 'ok',
      detail: { provider, disabled, checked: checked.length, dryRun: dryRun || undefined },
    })
  }

  return { ok: true, disabled, reenabled: [], checked: checked.length, dryRun }
}
