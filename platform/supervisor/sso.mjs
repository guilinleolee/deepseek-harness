/**
 * 卡巴格企业平台 · SSO 骨架（栏目规划 v2 阶段 11C：企业微信 + 钉钉）。
 *
 * 配置驱动：data/sso.json 每个 provider 独立 enabled；secret/appSecret 经
 * AES-256-GCM 加密落盘（密钥派生同 2FA）。authorizeBase / apiBase 可配且
 * 缺省为真实域名——把两者指向本地 mock 服务器即可全流程验证（真实供应商
 * 待配置凭证后真机验证）。
 *
 * 流程（授权码模式）：
 * - GET /api/auth/sso/:provider/start：生成一次性 state（内存 Map，5 分钟
 *   过期，重启即失效——安全语义）→ 303 到 authorize URL；
 * - GET /api/auth/sso/:provider/callback：state 校验（一次性）→ code 换
 *   token → 取用户标识（企业微信 userid / 钉钉 unionId，仅元数据）→ 按
 *   accounts.json 的 ssoIds 数组查绑定 → 命中签发 JWT（审计 auth.sso_login）；
 *   未命中渲染绑定页（bindToken 一次性，5 分钟）；
 * - POST /api/auth/sso/bind：账号+密码验证后写 ssoIds（审计 auth.sso_bind，
 *   密码错误计入登录限流同桶），签发 JWT。
 *
 * 与 gateway 的依赖方向：gateway → 本模块。本模块对 gateway 函数（
 * verifyPassword/saveAccounts）的引用是 hoisted 函数声明的循环引用，ESM
 * 合法且只在请求期调用（模块求值期不触碰）。
 */
import { randomBytes, createHash } from 'node:crypto'
import { mkdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'

import { writeJsonAtomic } from './atomic-write.mjs'

import { auditAppend, clientIp } from './audit.mjs'
import { addAccount, saveAccounts, verifyPassword } from './gateway.mjs'
import { withAccountLock } from './console.mjs'
import { issueVkey } from './relay.mjs'
import { writeVkeyToHome } from './credentials.mjs'
import { generatePassword } from './security.mjs'
import { decryptText, deriveKey, encryptText } from './totp.mjs'

const SSO_FILE = 'sso.json'
const STATE_TTL_MS = 5 * 60_000
/** state/bindToken 内存上限：达到即拒绝新请求（429），防匿名洪泛撑爆内存。 */
export const SSO_PENDING_LIMIT = 5000

/** 支持的 provider 与登录页按钮文案。 */
export const SSO_PROVIDERS = {
  wecom: { label: '企业微信' },
  dingtalk: { label: '钉钉' },
}

/** 自动开通允许落地的角色（admin 只能由管理台显式授予，绝不自动产生）。 */
const AUTO_ROLES = ['employee', 'auditor']

const DEFAULT_SSO = () => ({
  wecom: {
    enabled: false, corpId: '', agentId: '', secretEnc: '', redirectUri: '',
    authorizeBase: 'https://open.weixin.qq.com', apiBase: 'https://qyapi.weixin.qq.com',
    // 自动开通（免邀请码注册）：企业身份首次登录即建号。
    autoProvision: false, autoRole: 'employee', autoDepartment: '', autoInstance: '',
  },
  dingtalk: {
    enabled: false, appKey: '', redirectUri: '',
    authorizeBase: 'https://login.dingtalk.com', apiBase: 'https://api.dingtalk.com',
    autoProvision: false, autoRole: 'employee', autoDepartment: '', autoInstance: '',
  },
})

function isUnsafeKey(key) {
  return key === '__proto__' || key === 'constructor' || key === 'prototype'
}

function loadSsoRaw(dataDir) {
  try {
    const parsed = JSON.parse(readFileSync(join(dataDir, SSO_FILE), 'utf8'))
    return parsed !== null && typeof parsed === 'object' && !Array.isArray(parsed) ? parsed : {}
  } catch {
    return {}
  }
}

function saveSsoRaw(dataDir, config) {
  mkdirSync(dataDir, { recursive: true })
  const path = join(dataDir, SSO_FILE)
  writeJsonAtomic(path, config)
}

/** 读取 SSO 配置（缺省生成全 disabled；密文不解密）。 */
export function loadSsoConfig(dataDir) {
  const raw = loadSsoRaw(dataDir)
  const merged = DEFAULT_SSO()
  for (const provider of Object.keys(merged)) {
    merged[provider] = { ...merged[provider], ...(raw[provider] ?? {}) }
  }
  return merged
}

/** 已启用的 provider 名列表（登录页按钮数据源）。 */
export function enabledSsoProviders(dataDir) {
  const config = loadSsoConfig(dataDir)
  return Object.keys(SSO_PROVIDERS).filter((provider) => config[provider]?.enabled === true)
}

/** 某 provider 是否启用。 */
export function providerEnabled(dataDir, provider) {
  return enabledSsoProviders(dataDir).includes(provider)
}

/**
 * 合并保存 SSO 配置。patch = { <provider>: { enabled, corpId|appKey, agentId?,
 * secret|appSecret（明文，可选，提供则加密落盘）, redirectUri, authorizeBase?,
 * apiBase? } }。未知 provider / 非法 URL 抛错（调用方转 400 并留审计）。
 */
export function saveSsoConfig(dataDir, patch, key) {
  const config = loadSsoConfig(dataDir)
  for (const [provider, entry] of Object.entries(patch ?? {})) {
    if (isUnsafeKey(provider) || !(provider in SSO_PROVIDERS)) throw new Error(`未知 SSO provider: ${provider}`)
    if (entry === null || typeof entry !== 'object') throw new Error(`${provider} 配置必须是对象`)
    const target = config[provider]
    if (entry.enabled !== undefined) target.enabled = entry.enabled === true
    for (const [field, value] of [['redirectUri', entry.redirectUri], ['authorizeBase', entry.authorizeBase], ['apiBase', entry.apiBase]]) {
      if (value === undefined) continue
      if (typeof value !== 'string' || (value !== '' && !/^https?:\/\//.test(value))) {
        throw new Error(`${provider}.${field} 必须是 http(s) URL`)
      }
      target[field] = value.trim()
    }
    for (const field of ['corpId', 'appKey', 'agentId']) {
      if (entry[field] !== undefined) {
        if (typeof entry[field] !== 'string') throw new Error(`${provider}.${field} 必须是字符串`)
        target[field] = entry[field].trim()
      }
    }
    // 自动开通配置（免邀请码注册）：角色白名单与实例 id 形态校验在此收口，
    // 避免把「任意角色/任意实例」写进配置后被自动开通路径放大。
    if (entry.autoProvision !== undefined) target.autoProvision = entry.autoProvision === true
    if (entry.autoRole !== undefined) {
      if (typeof entry.autoRole !== 'string' || !AUTO_ROLES.includes(entry.autoRole)) {
        throw new Error(`${provider}.autoRole 只支持 ${AUTO_ROLES.join('/')}`)
      }
      target.autoRole = entry.autoRole
    }
    for (const field of ['autoDepartment', 'autoInstance']) {
      if (entry[field] !== undefined) {
        if (typeof entry[field] !== 'string') throw new Error(`${provider}.${field} 必须是字符串`)
        target[field] = entry[field].trim()
      }
    }
    const secretField = provider === 'wecom' ? 'secret' : 'appSecret'
    if (typeof entry[secretField] === 'string' && entry[secretField] !== '') {
      if (key === null) throw new Error('SSO 加密根未初始化（缺 auth-secret）')
      target.secretEnc = encryptText(key, entry[secretField])
    }
  }
  saveSsoRaw(dataDir, config)
  return loadSsoConfig(dataDir)
}

/** 解密 provider 的 app secret（换 token 用）；未配置返回 ''。 */
export function getSsoSecret(dataDir, provider, key) {
  const secretEnc = loadSsoConfig(dataDir)[provider]?.secretEnc
  if (typeof secretEnc !== 'string' || secretEnc === '') return ''
  return decryptText(key, secretEnc)
}

/** 构造 authorize URL（state 由调用方生成并落内存）。 */
export function buildAuthorizeUrl(provider, config, state, redirectUri) {
  const enc = encodeURIComponent
  if (provider === 'wecom') {
    return `${config.authorizeBase}/connect/oauth2/authorize?appid=${enc(config.corpId)}`
      + `&redirect_uri=${enc(redirectUri)}&response_type=code&scope=snsapi_base`
      + `&state=${enc(state)}&agentid=${enc(config.agentId)}#wechat_redirect`
  }
  // users/me 的用户令牌按授权时申请的 scope 发放：必须显式带上 Contact.User.Read
  //（缺失时钉钉 403 Forbidden.AccessDenied.AccessTokenPermissionDenied，应用后台
  // 开通权限只是前提）。个人权限属委托权限点，需用户本人显式同意——prompt=consent
  // 强制进入授权确认页；登录态静默授权不会下发委托 scope。
  return `${config.authorizeBase}/oauth2/auth?client_id=${enc(config.appKey)}`
    + `&redirect_uri=${enc(redirectUri)}&response_type=code&scope=${enc('openid Contact.User.Read')}`
    + `&state=${enc(state)}&prompt=consent`
}

/** 错误响应摘要：供应商失败 body 截断进异常文案——403 类失败的原因（权限/发布状态）只在其 body 里，真机排障必须可见。 */
async function errBody(res) {
  try {
    const text = await res.text()
    return text === '' ? '' : `：${text.slice(0, 300)}`
  } catch {
    return ''
  }
}

/** 用 code 换用户标识。返回 { ssoId, name? }；任一步失败抛错（调用方转 502）。 */
export async function resolveSsoIdentity(provider, code, dataDir, key, fetchImpl = fetch) {
  const config = loadSsoConfig(dataDir)[provider]
  if (config === undefined || config.enabled !== true) throw new Error('SSO provider 未启用')
  if (provider === 'wecom') {
    const secret = getSsoSecret(dataDir, provider, key)
    const tokenRes = await fetchImpl(`${config.apiBase}/gettoken?corpid=${encodeURIComponent(config.corpId)}&corpsecret=${encodeURIComponent(secret)}`, { signal: AbortSignal.timeout(10_000) })
    if (!tokenRes.ok) throw new Error(`企业微信 token 接口失败（HTTP ${tokenRes.status}）${await errBody(tokenRes)}`)
    const accessToken = (await tokenRes.json()).access_token
    if (typeof accessToken !== 'string' || accessToken === '') throw new Error('企业微信 token 接口未返回 access_token')
    const userRes = await fetchImpl(`${config.apiBase}/auth/getuserinfo?access_token=${encodeURIComponent(accessToken)}&code=${encodeURIComponent(code)}`, { signal: AbortSignal.timeout(10_000) })
    if (!userRes.ok) throw new Error(`企业微信用户接口失败（HTTP ${userRes.status}）${await errBody(userRes)}`)
    const userBody = await userRes.json()
    if (typeof userBody.userid !== 'string' || userBody.userid === '') throw new Error('企业微信用户接口未返回 userid')
    return { ssoId: `wecom:${userBody.userid}`, name: userBody.name }
  }
  const secret = getSsoSecret(dataDir, provider, key)
  // 钉钉新版 OAuth2 契约（2026-10-03 真机探针核对）：换用户令牌的端点是
  // /v1.0/oauth2/userAccessToken，字段为驼峰 clientId/clientSecret/grantType；
  // snake_case 或 /v1.0/oauth2/token 均被钉钉拒绝（404 API 不存在 / 缺 clientId）。
  const tokenRes = await fetchImpl(`${config.apiBase}/v1.0/oauth2/userAccessToken`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ clientId: config.appKey, clientSecret: secret, grantType: 'authorization_code', code }),
    signal: AbortSignal.timeout(10_000),
  })
  if (!tokenRes.ok) throw new Error(`钉钉 token 接口失败（HTTP ${tokenRes.status}）${await errBody(tokenRes)}`)
  const accessToken = (await tokenRes.json()).accessToken
  if (typeof accessToken !== 'string' || accessToken === '') throw new Error('钉钉 token 接口未返回 accessToken')
  const userRes = await fetchImpl(`${config.apiBase}/v1.0/contact/users/me`, {
    headers: { 'x-acs-dingtalk-access-token': accessToken },
    signal: AbortSignal.timeout(10_000),
  })
  if (!userRes.ok) throw new Error(`钉钉用户接口失败（HTTP ${userRes.status}）${await errBody(userRes)}`)
  const userBody = await userRes.json()
  const identity = typeof userBody.unionId === 'string' ? userBody.unionId : userBody.openId
  if (typeof identity !== 'string' || identity === '') throw new Error('钉钉用户接口未返回 unionId/openId')
  return { ssoId: `dingtalk:${identity}`, name: userBody.nick }
}

/* ── 内存态：state 与 bindToken（daemon 生命周期内有效，重启即失效）───────── */

const pendingStates = new Map()
const bindTokens = new Map()
const TTL_GUARD_SIZE = 1000

function evictExpired(map) {
  if (map.size <= TTL_GUARD_SIZE) return
  const cutoff = Date.now()
  for (const [key, entry] of map) {
    if (entry.expiresAt < cutoff) map.delete(key)
  }
}

const freshToken = () => randomBytes(24).toString('base64url')

function putPendingState(provider) {
  // 洪泛保护：只统计未过期条目，达到上限即拒绝（不挤掉合法在途 state）。
  const cutoff = Date.now()
  let live = 0
  for (const entry of pendingStates.values()) {
    if (entry.expiresAt >= cutoff) live += 1
  }
  if (live >= SSO_PENDING_LIMIT) return null
  const state = freshToken()
  pendingStates.set(state, { provider, expiresAt: Date.now() + STATE_TTL_MS })
  evictExpired(pendingStates)
  return state
}

/** 仅供测试：绕过 HTTP 直接填充在途 state（洪泛上限 429 断言用）。 */
export function _putPendingStateForTest(provider) {
  return putPendingState(provider)
}

/** 一次性取出并校验 state；缺失/不匹配/过期返回 null（取出即删除）。 */
function takePendingState(state, provider) {
  const entry = pendingStates.get(state)
  if (entry === undefined || entry.provider !== provider) return null
  pendingStates.delete(state)
  return entry.expiresAt < Date.now() ? null : entry
}

function putBindToken(provider, ssoId, name) {
  const cutoff = Date.now()
  let live = 0
  for (const entry of bindTokens.values()) {
    if (entry.expiresAt >= cutoff) live += 1
  }
  if (live >= SSO_PENDING_LIMIT) return null
  const token = freshToken()
  bindTokens.set(token, { provider, ssoId, name, expiresAt: Date.now() + STATE_TTL_MS })
  evictExpired(bindTokens)
  return token
}

/** 一次性取出绑定上下文；缺失/过期返回 null。 */
function takeBindToken(token) {
  const entry = bindTokens.get(token)
  if (entry === undefined) return null
  bindTokens.delete(token)
  return entry.expiresAt < Date.now() ? null : entry
}

const esc = (s) => String(s)
  .replace(/&/g, '&amp;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;')
  .replace(/'/g, '&#39;')

const BIND_PAGE = (providerLabel, bindToken, error = '') => `<!doctype html><meta charset="utf-8">
<title>卡巴格 · 绑定企业账号</title>
<style>body{font-family:system-ui;background:#f6f7f9;color:#1f2937;display:grid;place-items:center;height:100vh;margin:0}
form{background:#ffffff;padding:2rem 2.5rem;border-radius:12px;min-width:320px}
input,button{display:block;width:100%;margin:.5rem 0;padding:.6rem;border-radius:6px;border:1px solid #e5e7eb;background:#ffffff;color:#1f2937;box-sizing:border-box}
button{background:#2563eb;border:none;cursor:pointer;font-weight:600}
.err{color:#ff8a80;font-size:.9rem;min-height:1.2em}</style>
<form onsubmit="bind(event)"><h2 style="margin-top:0">绑定${esc(providerLabel)}账号</h2>
<p style="font-size:.88rem;color:#6b7280">首次使用：输入已有平台账号与密码完成一次绑定，之后可直接用${esc(providerLabel)}登录。</p>
<input id="acc" placeholder="平台账号（邮箱）" autocomplete="username">
<input id="pw" type="password" placeholder="平台密码" autocomplete="current-password">
<input type="hidden" id="bt" value="${esc(bindToken)}">
<div class="err">${esc(error)}</div><button>绑定并登录</button></form>
<script>
async function bind(ev){ev.preventDefault();
 var r=await fetch('/api/auth/sso/bind',{method:'POST',headers:{'content-type':'application/json'},
   body:JSON.stringify({bindToken:bt.value,account:acc.value,password:pw.value})});
 var j=await r.json().catch(function(){return{}});
 if(r.ok&&j.ok){location.href=j.role==='employee'?'/me':'/'}else{document.querySelector('.err').textContent=(j&&j.error)||'绑定失败'}}
</script>`

/**
 * 企业身份自动开通（免邀请码注册）。
 *
 * 背景：邀请码注册要求管理员先在管理台发码，员工再凭码建号——多一次人工
 * 往返，且码要靠线下传递。企业微信/钉钉已能证明「此人属于本企业」，因此
 * 首次扫码登录即可直接建号（Just-In-Time Provisioning）：
 *   - 身份来源是企业 IdP（可信），不再是线下人工发放的凭据；
 *   - 账号名由 IdP 身份派生（provider + userid/unionId 的稳定摘要），
 *     天然唯一且不与真人邮箱冲突；
 *   - 角色/部门/实例由管理员在 SSO 配置里预先定好（autoRole/autoDepartment/
 *     autoInstance），员工无法自行提权——autoRole 白名单不含 admin；
 *   - 密码是随机生成的不可知值（仅占位，登录只走 SSO），不进任何通知。
 *
 * @returns {{ok:true, record} | {ok:false, reason, message}}
 */
export async function provisionFromSso({ dataDir, provider, identity, config, manifest, ip }) {
  const role = AUTO_ROLES.includes(config.autoRole) ? config.autoRole : 'employee'
  const department = typeof config.autoDepartment === 'string' && config.autoDepartment !== '' ? config.autoDepartment : '未分配'
  // 实例取管理员配置；未配置时回落到清单首个实例（保证账号有归属实例，
  // 否则网关按 instanceId 路由会 403）。
  const instanceId = (typeof config.autoInstance === 'string' && config.autoInstance !== '')
    ? config.autoInstance
    : (manifest?.instances?.[0]?.id ?? '')
  if (instanceId === '') return { ok: false, reason: 'no_instance', message: 'SSO 自动开通未配置目标实例' }

  // 账号名：provider + 身份摘要（sha256 前 12 位十六进制）。
  // 身份原文（unionId/userid）不进账号名——它属于企业目录标识，落进审计与
  // 页面即成个人信息；摘要后既唯一又不可反查。
  const digest = createHash('sha256').update(String(identity.ssoId)).digest('hex').slice(0, 12)
  const account = `${provider}-${digest}`

  return await withAccountLock(async () => {
    const store = JSON.parse(readFileSync(join(dataDir, 'accounts.json'), 'utf8'))
    const existing = store.accounts.find((a) => a.account === account)
    if (existing !== undefined) {
      // 账号已存在（同一身份重复开通）：补齐绑定后直接登录，不重复建号。
      existing.ssoIds = Array.isArray(existing.ssoIds) ? existing.ssoIds : []
      if (!existing.ssoIds.includes(identity.ssoId)) existing.ssoIds.push(identity.ssoId)
      saveAccounts(dataDir, store)
      return { ok: true, record: existing }
    }
    // addAccount 内部自己读改写 accounts.json——它返回后必须重新读一次，
    // 否则拿旧 store 回写会把刚建的账号覆盖掉（丢账号）。
    const created = addAccount(dataDir, {
      account,
      instanceId,
      role,
      displayName: typeof identity.name === 'string' && identity.name.trim() !== '' ? identity.name.trim() : undefined,
      department,
      // 随机不可知密码：只作存储占位，密码登录实际不可用（走 SSO）。
      password: generatePassword(),
    })
    const fresh = JSON.parse(readFileSync(join(dataDir, 'accounts.json'), 'utf8'))
    const record = fresh.accounts.find((a) => a.account === account)
    if (record === undefined) return { ok: false, reason: 'create_failed', message: '账号写入后回读失败' }
    record.ssoIds = [identity.ssoId]
    saveAccounts(dataDir, fresh)
    // 虚拟钥匙 + 实例 home 凭据（与建号链路同一原语，vkey 最后一公里）。
    try {
      const { token } = issueVkey(dataDir, { account, instanceId, models: '*' })
      writeVkeyToHome(dataDir, instanceId, token)
    } catch (error) {
      console.error('[sso] 自动开通后签发 vkey 失败:', error?.message ?? error)
    }
    return { ok: true, record }
  })
}

/**
 * SSO 路由（gateway 在裸 portal 主机分支调用）。
 * @param issueSession - (res, record, ip) => void：签发 JWT Cookie（gateway
 *   提供，与密码登录同一令牌语义：sub/epoch/TTL；传 ip 时同时刷新 lastLogin）。
 * @param twofaKey - 敏感配置派生根（sso secret 加密同源）。
 * @param guard - 登录限流器（绑定密码错误计入同桶；可缺省=不限流，测试用）。
 * @param manifest - 实例清单（自动开通时选目标实例；可缺省=不自动开通）。
 * @returns true 表示已响应。
 */
export function handleSso({ req, res, url, dataDir, issueSession, twofaKey, guard = null, manifest = null }) {
  const ip = clientIp(req)
  const match = /^\/api\/auth\/sso\/(\w+)\/(start|callback)$/.exec(url.pathname)
  if (match !== null) {
    const [, provider, action] = match
    if (!(provider in SSO_PROVIDERS) || !providerEnabled(dataDir, provider)) {
      res.writeHead(404, { 'content-type': 'text/plain; charset=utf-8' })
      res.end('该 SSO 登录方式未启用')
      return true
    }
    if (action === 'start') {
      const config = loadSsoConfig(dataDir)[provider]
      const state = putPendingState(provider)
      if (state === null) {
        res.writeHead(429, { 'content-type': 'text/plain; charset=utf-8' })
        res.end('SSO 登录请求过于繁忙，请稍后重试')
        return true
      }
      res.writeHead(303, { location: buildAuthorizeUrl(provider, config, state, config.redirectUri) })
      res.end()
      return true
    }
    // callback：state 一次性校验 → code 换身份 → 查绑定。
    const code = url.searchParams.get('code') ?? ''
    const stateEntry = takePendingState(url.searchParams.get('state') ?? '', provider)
    if (stateEntry === null || code === '') {
      res.writeHead(400, { 'content-type': 'text/plain; charset=utf-8' })
      res.end('SSO 回调无效（state 过期或不匹配），请重新从登录页发起')
      return true
    }
    void resolveSsoIdentity(provider, code, dataDir, twofaKey)
      .then(async (identity) => {
        const accounts = JSON.parse(readFileSync(join(dataDir, 'accounts.json'), 'utf8'))
        const record = accounts.accounts.find((a) => Array.isArray(a.ssoIds) && a.ssoIds.includes(identity.ssoId))
        if (record !== undefined) {
          if (record.disabled) {
            res.writeHead(403, { 'content-type': 'text/plain; charset=utf-8' })
            res.end('账号已禁用，请联系管理员。')
            return
          }
          void auditAppend({ actor: { account: record.account, role: record.role, ip }, action: 'auth.sso_login', target: record.account, result: 'ok', detail: { provider, ssoId: identity.ssoId } })
          issueSession(res, record, ip)
          res.writeHead(303, { location: record.role === 'employee' ? '/me' : '/' })
          res.end()
          return
        }
        // 未绑定：provider 开启「自动开通」时直接建号（免邀请码注册），
        // 否则回落到「输入账号密码完成绑定」的旧流程。
        const providerConfig = loadSsoConfig(dataDir)[provider]
        if (providerConfig?.autoProvision === true) {
          const provisioned = await provisionFromSso({ dataDir, provider, identity, config: providerConfig, manifest, ip })
          if (provisioned.ok !== true) {
            void auditAppend({ actor: null, action: 'auth.sso_provision', target: null, result: 'fail', detail: { provider, reason: provisioned.reason } })
            res.writeHead(403, { 'content-type': 'text/plain; charset=utf-8' })
            res.end(`账号自动开通失败：${provisioned.message}`)
            return
          }
          const created = provisioned.record
          if (created.disabled) {
            res.writeHead(403, { 'content-type': 'text/plain; charset=utf-8' })
            res.end('账号已禁用，请联系管理员。')
            return
          }
          void auditAppend({ actor: { account: created.account, role: created.role, ip }, action: 'auth.sso_provision', target: created.account, result: 'ok', detail: { provider, role: created.role, instanceId: created.instanceId, department: created.department } })
          issueSession(res, created, ip)
          res.writeHead(303, { location: created.role === 'employee' ? '/me' : '/' })
          res.end()
          return
        }
        const bindToken = putBindToken(provider, identity.ssoId, identity.name)
        if (bindToken === null) {
          res.writeHead(429, { 'content-type': 'text/plain; charset=utf-8' })
          res.end('SSO 绑定请求过于繁忙，请稍后重试')
          return
        }
        res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' })
        res.end(BIND_PAGE(SSO_PROVIDERS[provider].label, bindToken))
      })
      .catch((error) => {
        res.writeHead(502, { 'content-type': 'text/plain; charset=utf-8' })
        res.end(`SSO 身份换取失败: ${error?.message ?? error}`)
      })
    return true
  }

  if (url.pathname === '/api/auth/sso/bind' && req.method === 'POST') {
    let body = ''
    req.on('data', (chunk) => { body += chunk })
    req.on('end', () => {
      let bindToken = ''
      let account = ''
      let password = ''
      try {
        const parsed = JSON.parse(body || '{}')
        bindToken = String(parsed.bindToken ?? '')
        account = String(parsed.account ?? '')
        password = String(parsed.password ?? '')
      } catch { /* 当作空凭据处理 */ }
      const context = takeBindToken(bindToken)
      if (context === null) {
        res.writeHead(400, { 'content-type': 'application/json; charset=utf-8' })
        res.end(JSON.stringify({ error: '绑定会话已过期，请重新发起 SSO 登录' }))
        return
      }
      // 读改写 accounts.json 走管理台同一把账号锁（P2-3：消除与管理台并发
      // 操作的丢更新窗口）。锁内完成校验、写入与响应。
      void withAccountLock(async () => {
        const store = JSON.parse(readFileSync(join(dataDir, 'accounts.json'), 'utf8'))
        const record = store.accounts.find((a) => a.account === account)
        const actor = { account, role: record?.role ?? null, ip }
        const failBind = (reason) => {
          void auditAppend({ actor, action: 'auth.sso_bind', target: account, result: 'fail', detail: { reason, provider: context.provider } })
          res.writeHead(401, { 'content-type': 'application/json; charset=utf-8' })
          res.end(JSON.stringify({ error: '账号或密码错误' }))
        }
        if (record === undefined || record.disabled) {
          if (guard !== null) guard.fail(account, ip)
          failBind('bad_account')
          return
        }
        if (!verifyPassword(record, password)) {
          if (guard !== null) guard.fail(account, ip)
          failBind('bad_password')
          return
        }
        record.ssoIds = Array.isArray(record.ssoIds) ? record.ssoIds : []
        if (!record.ssoIds.includes(context.ssoId)) record.ssoIds.push(context.ssoId)
        saveAccounts(dataDir, store)
        void auditAppend({ actor: { account: record.account, role: record.role, ip }, action: 'auth.sso_bind', target: record.account, result: 'ok', detail: { provider: context.provider, ssoId: context.ssoId } })
        issueSession(res, record, ip)
        res.writeHead(200, { 'content-type': 'application/json; charset=utf-8' })
        res.end(JSON.stringify({ ok: true, account: record.account, role: record.role }))
      }).catch((error) => {
        console.error('[sso] 绑定处理异常:', error?.stack ?? error)
        try {
          res.writeHead(500, { 'content-type': 'application/json; charset=utf-8' })
          res.end(JSON.stringify({ error: '绑定处理异常，请重试' }))
        } catch { /* 已响应 */ }
      })
    })
    return true
  }
  return false
}

/** sso.json 中加密根派生（gateway 持有同一 auth-secret，二者一致）。 */
export function ssoKeyOf(secret) {
  return deriveKey(secret)
}
