/**
 * 卡巴格企业平台 · 认证网关（任务书阶段 2）。
 *
 * 职责：登录签发 JWT（HttpOnly Cookie）；按 Host 头把已认证请求反代到
 * 该账号绑定的实例（<实例id>.<portal 主机名> → 127.0.0.1:<实例端口>，
 * 路径不重写，SPA 与 WebSocket 原样穿透）；未登录/未绑定一律拒绝。
 * 实例侧零改动——实例通过自身 `--trusted-host` 信任围栏接受网关转发的
 * Host，且只绑定 127.0.0.1，生产环境员工物理上绕不过网关。
 *
 * 安全语义（对齐任务书决定 5 与阶段 0 矩阵 + 栏目规划 v2 第五节）：
 * - 密码 scrypt 加盐哈希存储；JWT HS256，30 分钟过期；
 * - 登录限速：按「账号+IP」滑动窗口失败计数，达阈值锁定（参数在
 *   data/security.json，security.mjs），成败/限流三种结果都写审计（audit.mjs）；
 * - 撤销 = 账号 tokenEpoch 递增，旧令牌全部失效（设备级撤销走阶段 3 控制面）；
 * - 实时校验账号↔实例绑定：改绑立即生效，无需等令牌过期；
 * - 网关只做身份与绑定判定，不读任何会话/内容正文。
 */
import { createServer, request as httpRequest } from 'node:http'
import { connect as netConnect } from 'node:net'
import { createHmac, randomBytes, scryptSync, timingSafeEqual } from 'node:crypto'
import { existsSync, readFileSync, renameSync, writeFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'

import { handleConsole } from './console.mjs'
import { handlePortal } from './portal.mjs'
import { createJobRunner } from './plugins-gov.mjs'
import { auditAppend, clientIp, initAudit } from './audit.mjs'
import { createLoginRateGuard, loadSecurityConfig } from './security.mjs'
import { deriveKey, getTwofaRecord, isTwofaEnabled, verifyTwofaForLogin } from './totp.mjs'
import { authenticateServiceToken } from './service-tokens.mjs'
import { handleSso, SSO_PROVIDERS, enabledSsoProviders } from './sso.mjs'

const json = (res, status, value) => {
  try {
    res.writeHead(status, { 'content-type': 'application/json; charset=utf-8' })
    res.end(JSON.stringify(value))
  } catch { /* 已响应 */ }
}

const COOKIE_NAME = 'lyz_session'
const TOKEN_TTL_SECONDS = 30 * 60
const ROLE_RANK = { employee: 1, auditor: 2, admin: 3 }

/* ── 账号存储（data/accounts.json）──────────────────────────────────────── */

export function loadAccounts(dataDir) {
  const file = join(dataDir, 'accounts.json')
  try {
    return JSON.parse(readFileSync(file, 'utf8'))
  } catch {
    return { accounts: [] }
  }
}

export function listAccounts(dataDir) {
  return loadAccounts(dataDir).accounts.map((a) => ({
    account: a.account,
    displayName: a.displayName,
    role: a.role,
    department: a.department,
    instanceId: a.instanceId,
    tokenEpoch: a.tokenEpoch,
    createdAt: a.createdAt,
    disabled: a.disabled === true,
    monthlyTokens: a.monthlyTokens,
  }))
}

/** 管理员重置账号密码：scrypt 重哈希，epoch+1 踢掉该账号全部已登录会话。 */
export function setPassword(dataDir, account, password) {
  const store = loadAccounts(dataDir)
  const record = store.accounts.find((a) => a.account === account)
  if (record === undefined) throw new Error(`账号不存在: ${account}`)
  record.passwordHash = hashPassword(password)
  record.tokenEpoch = (record.tokenEpoch ?? 0) + 1
  saveAccounts(dataDir, store)
  return record.tokenEpoch
}

export function saveAccounts(dataDir, store) {
  const path = join(dataDir, 'accounts.json')
  const tmp = `${path}.tmp`
  writeFileSync(tmp, `${JSON.stringify(store, null, 2)}\n`)
  renameSync(tmp, path)
}

/** 账号/部门等实体名白名单：字母数字、@._- 与中文，1–64 字符（收敛注入面）。 */
export function isValidEntityName(value) {
  return typeof value === 'string' && /^[\w@.\-\u4e00-\u9fa5]{1,64}$/.test(value)
}

export function hashPassword(password) {
  const salt = randomBytes(16).toString('hex')
  const hash = scryptSync(password, salt, 64).toString('hex')
  return { salt, hash, algo: 'scrypt-N32768-r8-p1-dk64' }
}

export function verifyPassword(account, password) {
  if (!account?.passwordHash?.salt || !account?.passwordHash?.hash) return false
  const actual = scryptSync(password, account.passwordHash.salt, 64)
  const expected = Buffer.from(account.passwordHash.hash, 'hex')
  return actual.length === expected.length && timingSafeEqual(actual, expected)
}

export function addAccount(dataDir, { account, instanceId, role, displayName, department, password }) {
  if (!isValidEntityName(account)) {
    throw new Error('账号格式非法（允许字母数字、@._- 与中文，1–64 字符）')
  }
  if (department !== undefined && !isValidEntityName(department)) {
    throw new Error('部门名格式非法（允许字母数字、@._- 与中文，1–64 字符）')
  }
  const store = loadAccounts(dataDir)
  if (store.accounts.some((a) => a.account === account)) {
    throw new Error(`账号已存在: ${account}`)
  }
  const record = {
    id: `acc-${randomBytes(6).toString('hex')}`,
    account,
    displayName: displayName ?? account.split('@')[0],
    role,
    department: department ?? '未分配',
    instanceId,
    tokenEpoch: 0,
    createdAt: new Date().toISOString(),
    passwordHash: hashPassword(password),
  }
  store.accounts.push(record)
  saveAccounts(dataDir, store)
  return record
}

const VALID_ROLES = ['admin', 'auditor', 'employee']

/** 受控变更账号属性（角色/部门/显示名）：角色即时影响控制台与管理员权限。 */
export function updateAccount(dataDir, account, patch) {
  const store = loadAccounts(dataDir)
  const record = store.accounts.find((a) => a.account === account)
  if (record === undefined) throw new Error(`账号不存在: ${account}`)
  if (patch.role !== undefined) {
    if (!VALID_ROLES.includes(patch.role)) throw new Error(`非法角色: ${patch.role}`)
    record.role = patch.role
  }
  if (patch.department !== undefined) {
    if (!isValidEntityName(patch.department)) {
      throw new Error('部门名格式非法（允许字母数字、@._- 与中文，1–64 字符）')
    }
    record.department = patch.department
  }
  if (patch.displayName !== undefined) record.displayName = patch.displayName
  saveAccounts(dataDir, store)
  return record
}

/** 撤销某账号当前全部令牌：epoch 递增，旧 JWT 立即失效。 */
export function revokeAccountTokens(dataDir, account) {
  const store = loadAccounts(dataDir)
  const record = store.accounts.find((a) => a.account === account)
  if (!record) throw new Error(`账号不存在: ${account}`)
  record.tokenEpoch += 1
  saveAccounts(dataDir, store)
  return record.tokenEpoch
}

/* ── JWT（无依赖 HS256）─────────────────────────────────────────────────── */

const b64url = (buf) => Buffer.from(buf).toString('base64url')
const SIGNING_INPUT = (head, payload) => `${b64url(JSON.stringify(head))}.${b64url(JSON.stringify(payload))}`

function signToken(secret, payload) {
  const head = { alg: 'HS256', typ: 'JWT' }
  const input = SIGNING_INPUT(head, payload)
  const sig = createHmac('sha256', secret).update(input).digest('base64url')
  return `${input}.${sig}`
}

function verifyToken(secret, token) {
  if (typeof token !== 'string') return null
  const parts = token.split('.')
  if (parts.length !== 3) return null
  const input = `${parts[0]}.${parts[1]}`
  const expected = createHmac('sha256', secret).update(input).digest()
  let actual
  try {
    actual = Buffer.from(parts[2], 'base64url')
  } catch {
    return null
  }
  if (actual.length !== expected.length || !timingSafeEqual(actual, expected)) return null
  let payload
  try {
    payload = JSON.parse(Buffer.from(parts[1], 'base64url').toString('utf8'))
  } catch {
    return null
  }
  if (typeof payload.exp !== 'number' || payload.exp * 1000 < Date.now()) return null
  return payload
}

/** 读取或创建认证签名密钥（data/auth-secret.key；2FA 密钥派生的根）。 */
export function getOrCreateSecret(dataDir) {
  const file = join(dataDir, 'auth-secret.key')
  if (existsSync(file)) return readFileSync(file, 'utf8').trim()
  const secret = randomBytes(32).toString('hex')
  writeFileSync(file, `${secret}\n`)
  return secret
}

function parseCookies(header) {
  const jar = {}
  for (const part of (header ?? '').split(';')) {
    const idx = part.indexOf('=')
    if (idx > 0) jar[part.slice(0, idx).trim()] = decodeURIComponent(part.slice(idx + 1).trim())
  }
  return jar
}

function authFromRequest(secret, accountsStore, req) {
  const token = parseCookies(req.headers.cookie)[COOKIE_NAME]
  const payload = verifyToken(secret, token)
  if (payload === null) return { error: 'unauthenticated' }
  const record = accountsStore.accounts.find((a) => a.id === payload.sub)
  if (!record) return { error: 'unauthenticated' }
  // epoch 不匹配 = 令牌已被撤销；绑定实时校验，改绑立即生效。
  if (payload.epoch !== record.tokenEpoch) return { error: 'revoked' }
  if (record.disabled) return { error: 'disabled' }
  return { record, payload }
}

/* ── Host 路由 ──────────────────────────────────────────────────────────── */

/** HTML 转义（入口页插值用：账号/实例字段来自 accounts.json 与清单，防回流）。 */
const esc = (s) => String(s)
  .replace(/&/g, '&amp;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;')
  .replace(/'/g, '&#39;')

/** 从 Host 头解析实例 id（"<id>.<portal 主机>[:port]"），非子域返回 null。 */
function instanceIdFromHost(hostHeader, manifest) {
  const host = (hostHeader ?? '').split(':')[0].toLowerCase()
  const portalHost = (manifest.gatewayHost ?? 'localhost').split(':')[0].toLowerCase()
  if (!host.endsWith(`.${portalHost}`)) return null
  const id = host.slice(0, -1 * (portalHost.length + 1))
  return manifest.instances.some((spec) => spec.id === id) ? id : null
}

/* ── 网关服务器 ─────────────────────────────────────────────────────────── */

/**
 * 登录页。portalHostname 供前端区分登录发生地：员工（employee）在 portal
 * 主机上登录成功后跳个人中心 /me（阶段 10），在实例子域上登录则原地刷新
 * 进入工作区；admin/auditor 一律原地刷新（进入管理台或工作区）。
 */
const LOGIN_PAGE = (error = '', portalHostname = '', ssoProviders = []) => `<!doctype html><meta charset="utf-8">
<title>卡巴格 · 登录</title>
<style>body{font-family:system-ui;background:#f6f7f9;color:#1f2937;display:grid;place-items:center;height:100vh;margin:0}
form{background:#ffffff;padding:2rem 2.5rem;border-radius:12px;min-width:280px}
input,button{display:block;width:100%;margin:.5rem 0;padding:.6rem;border-radius:6px;border:1px solid #e5e7eb;background:#ffffff;color:#1f2937;box-sizing:border-box}
button{background:#2563eb;border:none;cursor:pointer;font-weight:600}
a.ssobtn{display:block;margin-top:.5rem;padding:.55rem;border-radius:6px;border:1px solid #e5e7eb;background:#fafafa;color:#374151;text-align:center;text-decoration:none;font-size:.92rem}
.err{color:#ff8a80;font-size:.9rem;min-height:1.2em}</style>
<form onsubmit="login(event)"><h2 style="margin-top:0">卡巴格 · 登录</h2>
<input id="acc" placeholder="账号（邮箱）" autocomplete="username">
<input id="pw" type="password" placeholder="密码" autocomplete="current-password">
<div id="totprow" style="display:none"><input id="tc" inputmode="numeric" placeholder="两步验证码（6 位数字）" autocomplete="one-time-code"></div>
<div class="err" id="msg">${error}</div><button id="btn">登录</button></form>
${ssoProviders.map((provider) => `<a class="ssobtn" href="/api/auth/sso/${provider}/start">使用${SSO_PROVIDERS[provider].label}账号登录</a>`).join('')}
<script>
var STAGE='password';var HOST='${portalHostname}';
async function finish(j){
 if(j.role==='employee' && HOST!=='' && location.hostname===HOST) location.href='/me';
 else location.reload()}
async function login(ev){ev.preventDefault();
 var msg=document.getElementById('msg');msg.textContent='';
 if(STAGE==='totp'){
  var t=await fetch('/api/auth/totp',{method:'POST',headers:{'content-type':'application/json'},
    body:JSON.stringify({account:acc.value,code:tc.value})});
  var tj=await t.json().catch(function(){return{}});
  if(t.ok){finish(tj)}else{msg.textContent=(tj&&tj.error)||'验证码错误'}
  return}
 var r=await fetch('/api/auth/login',{method:'POST',headers:{'content-type':'application/json'},
   body:JSON.stringify({account:acc.value,password:pw.value})});
 var j=await r.json().catch(function(){return{}});
 if(r.ok){
  if(j.totp_required){STAGE='totp';pw.style.display='none';document.getElementById('totprow').style.display='block';document.getElementById('btn').textContent='验证';tc.focus();msg.textContent='请输入认证器中的 6 位验证码';msg.style.color='#6b7280';return}
  if(j.needs_2fa_enrollment){msg.textContent='登录成功。管理员已要求该角色绑定两步验证，请到个人中心完成绑定。';msg.style.color='#d97706';setTimeout(function(){finish(j)},2500);return}
  finish(j)
 }else{msg.textContent='账号或密码错误'}}
</script>`

/**
 * 创建网关服务器。依赖注入：
 * @param manifest - instances.json 的内容（instances / gatewayHost / portalPort）
 * @param getState - () => supervisor 状态（实例 id → port / state）
 * @param dataDir - data/ 目录（accounts.json、auth-secret.key 所在）
 */
export function createGatewayServer({ manifest, getState, dataDir }) {
  initAudit(dataDir)
  const secret = getOrCreateSecret(dataDir)
  // 登录限速参数每次判定时从 security.json 现读：管理台改动即时生效。
  const loginGuard = createLoginRateGuard(() => {
    const config = loadSecurityConfig(dataDir)
    return {
      windowMs: config.loginWindowMinutes * 60_000,
      maxFails: config.loginMaxFails,
      lockoutMs: config.lockoutMinutes * 60_000,
    }
  })
  // 2FA 密钥派生根：签名密钥既已存在，直接派生（阶段 11A）。
  const twofaKey = deriveKey(secret)
  // SSO 登录与密码登录共用同一令牌语义（sub/epoch/TTL/Cookie 参数，阶段 11C）。
  const issueSession = (res, record) => {
    const token = signToken(secret, {
      sub: record.id,
      acc: record.account,
      role: record.role,
      epoch: record.tokenEpoch,
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + TOKEN_TTL_SECONDS,
    })
    res.setHeader('set-cookie',
      `${COOKIE_NAME}=${encodeURIComponent(token)}; HttpOnly; SameSite=Strict; Path=/; Max-Age=${TOKEN_TTL_SECONDS}`)
  }
  const pluginRunner = createJobRunner({ dataDir, manifest, repoRoot: resolve(dirname(dataDir), manifest.repoRoot) })
  const accountsFile = join(dataDir, 'accounts.json')
  const portalHost = manifest.gatewayHost ?? 'localhost'
  // 登录页注入 portal 主机名与已启用的 SSO 按钮（阶段 11C）。
  const loginPage = (error = '') => LOGIN_PAGE(error, portalHost.split(':')[0], enabledSsoProviders(dataDir))
  const instancePortById = () => {
    const state = getState()
    const ports = {}
    for (const spec of manifest.instances) ports[spec.id] = { port: spec.port, state: state.instances[spec.id]?.state ?? 'stopped' }
    return ports
  }

  const server = createServer((req, res) => {
    const hostHeader = req.headers.host ?? ''
    const accountsStore = existsSync(accountsFile)
      ? JSON.parse(readFileSync(accountsFile, 'utf8'))
      : { accounts: [] }
    const url = new URL(req.url, `http://${hostHeader || 'localhost'}`)

    // 1) 登录接口：任何主机名上都可登录（登录发生在目标子域上，Cookie 才有效）。
    // 三种结果（成功/失败/被限流）都写审计；速率限制先于密码校验。
    if (url.pathname === '/api/auth/login' && req.method === 'POST') {
      let body = ''
      req.on('data', (chunk) => { body += chunk })
      req.on('end', async () => {
        let account = ''
        let password = ''
        try {
          const parsed = JSON.parse(body || '{}')
          account = String(parsed.account ?? '')
          password = String(parsed.password ?? '')
        } catch { /* 当作空凭据处理 */ }
        const ip = clientIp(req)
        const record = accountsStore.accounts.find((a) => a.account === account)
        const actor = { account, role: record?.role ?? null, ip }
        const verdict = loginGuard.check(account, ip)
        if (!verdict.allowed) {
          void auditAppend({ actor, action: 'auth.login_rate_limited', target: account, result: 'deny', detail: { retryAfterMinutes: verdict.retryAfterMinutes } })
          res.writeHead(429, { 'content-type': 'application/json; charset=utf-8' })
          res.end(JSON.stringify({ error: `登录尝试过于频繁，账号已临时锁定，请约 ${verdict.retryAfterMinutes} 分钟后再试` }))
          return
        }
        if (record?.disabled) {
          loginGuard.fail(account, ip)
          void auditAppend({ actor, action: 'auth.login_fail', target: account, result: 'deny', detail: { reason: 'disabled' } })
          res.writeHead(401, { 'content-type': 'application/json; charset=utf-8' })
          res.end(JSON.stringify({ error: '账号已禁用，请联系管理员' }))
          return
        }
        if (!record || !verifyPassword(record, password)) {
          loginGuard.fail(account, ip)
          void auditAppend({ actor, action: 'auth.login_fail', target: account, result: 'fail', detail: { reason: 'bad_credentials' } })
          res.writeHead(401, { 'content-type': 'application/json; charset=utf-8' })
          res.end(JSON.stringify({ error: 'invalid credentials' }))
          return
        }
        // 密码因子通过后先查两步验证（阶段 11A + P1-1 fail-closed）：
        // - 记录损坏（auth-secret 轮换/文件损坏）→ 不签发任何 cookie，500 +
        //   security.twofa_broken 审计（攻击者持正确密码也拿不到会话）；
        // - 已启用 → 不发 cookie，前端进入验证码步骤（POST /api/auth/totp）。
        // 密码对但登录未完成时不清零限流计数——TOTP 猜测与密码猜测共享同一桶。
        const twofaRecord = getTwofaRecord(dataDir, twofaKey, record.account)
        if (twofaRecord.state === 'broken') {
          await auditAppend({ actor, action: 'security.twofa_broken', target: record.account, result: 'fail', detail: null })
          res.writeHead(500, { 'content-type': 'application/json; charset=utf-8' })
          res.end(JSON.stringify({ error: '两步验证配置损坏，请联系管理员重置（管理台成员页→重置2FA）' }))
          return
        }
        if (twofaRecord.state === 'ok' && twofaRecord.enabled) {
          res.writeHead(200, { 'content-type': 'application/json; charset=utf-8' })
          res.end(JSON.stringify({ totp_required: true, account: record.account }))
          return
        }
        loginGuard.success(account, ip)
        // 软强制（阶段 11A）：角色被要求绑定 2FA 但尚未绑定——照常放行登录，
        // 仅在响应与 /me 页提醒；硬强制（拒绝无 2FA 登录）属阶段 11b，
        // 避免管理员误配置把自己锁死。
        const needs2faEnrollment = loadSecurityConfig(dataDir).require2faRoles.includes(record.role)
        void auditAppend({ actor: { account: record.account, role: record.role, ip }, action: 'auth.login_success', target: record.account, result: 'ok' })
        const token = signToken(secret, {
          sub: record.id,
          acc: record.account,
          role: record.role,
          epoch: record.tokenEpoch,
          iat: Math.floor(Date.now() / 1000),
          exp: Math.floor(Date.now() / 1000) + TOKEN_TTL_SECONDS,
        })
        res.setHeader('set-cookie',
          `${COOKIE_NAME}=${encodeURIComponent(token)}; HttpOnly; SameSite=Strict; Path=/; Max-Age=${TOKEN_TTL_SECONDS}`)
        res.writeHead(200, { 'content-type': 'application/json; charset=utf-8' })
        res.end(JSON.stringify({ ok: true, account: record.account, role: record.role, instance: record.instanceId, needs_2fa_enrollment: needs2faEnrollment || undefined }))
      })
      return
    }

    // 1b) 两步验证码换取 JWT（阶段 11A）：login 返回 totp_required 后调用。
    // 校验失败计入登录限流同桶（先 check 拒锁定、失败 fail 计数）。
    if (url.pathname === '/api/auth/totp' && req.method === 'POST') {
      let body = ''
      req.on('data', (chunk) => { body += chunk })
      req.on('end', () => {
        let account = ''
        let code = ''
        try {
          const parsed = JSON.parse(body || '{}')
          account = String(parsed.account ?? '')
          code = String(parsed.code ?? '')
        } catch { /* 当作空凭据处理 */ }
        const record = accountsStore.accounts.find((a) => a.account === account)
        const ip = clientIp(req)
        const actor = { account, role: record?.role ?? null, ip }
        const verdict = loginGuard.check(account, ip)
        if (!verdict.allowed) {
          void auditAppend({ actor, action: 'auth.login_rate_limited', target: account, result: 'deny', detail: { retryAfterMinutes: verdict.retryAfterMinutes } })
          res.writeHead(429, { 'content-type': 'application/json; charset=utf-8' })
          res.end(JSON.stringify({ error: `尝试过于频繁，账号已临时锁定，请约 ${verdict.retryAfterMinutes} 分钟后再试` }))
          return
        }
        const totpFail = (reason) => {
          loginGuard.fail(account, ip)
          void auditAppend({ actor, action: 'auth.totp_fail', target: account, result: 'fail', detail: { reason } })
          res.writeHead(401, { 'content-type': 'application/json; charset=utf-8' })
          res.end(JSON.stringify({ error: '账号或验证码错误' }))
        }
        if (!record || record.disabled) { totpFail('bad_account'); return }
        if (!isTwofaEnabled(dataDir, twofaKey, record.account)) { totpFail('not_enabled'); return }
        if (!verifyTwofaForLogin(dataDir, twofaKey, record.account, code)) { totpFail('bad_code'); return }
        loginGuard.success(account, ip)
        void auditAppend({ actor: { account: record.account, role: record.role, ip }, action: 'auth.login_success', target: record.account, result: 'ok', detail: { totp: true } })
        const token = signToken(secret, {
          sub: record.id,
          acc: record.account,
          role: record.role,
          epoch: record.tokenEpoch,
          iat: Math.floor(Date.now() / 1000),
          exp: Math.floor(Date.now() / 1000) + TOKEN_TTL_SECONDS,
        })
        res.setHeader('set-cookie',
          `${COOKIE_NAME}=${encodeURIComponent(token)}; HttpOnly; SameSite=Strict; Path=/; Max-Age=${TOKEN_TTL_SECONDS}`)
        res.writeHead(200, { 'content-type': 'application/json; charset=utf-8' })
        res.end(JSON.stringify({ ok: true, account: record.account, role: record.role, instance: record.instanceId }))
      })
      return
    }

    // 2) 裸 portal 主机：入口页（公开：只有链接与状态，无正文数据）。
    const subdomainId = instanceIdFromHost(hostHeader, manifest)
    if (subdomainId === null) {
      // 认证一次，status/console/portal 三段共用（JWT HMAC 校验开销可忽略）。
      const auth = authFromRequest(secret, accountsStore, req)
      if (url.pathname === '/api/auth/logout') {
        res.setHeader('set-cookie', `${COOKIE_NAME}=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0`)
        res.writeHead(200, { 'content-type': 'text/plain; charset=utf-8' })
        res.end('logged out')
        return
      }
      if (url.pathname === '/status.json') {
        if (auth.error !== undefined || auth.record.role !== 'admin') {
          res.writeHead(401, { 'content-type': 'application/json; charset=utf-8' })
          res.end(JSON.stringify({ error: 'admin only' }))
          return
        }
        res.writeHead(200, { 'content-type': 'application/json; charset=utf-8' })
        res.end(JSON.stringify(getState()))
        return
      }
      // 门户员工侧（阶段 10）：/me 个人中心、/login 直达、/register 邀请注册、
      // /api/register 与 /api/me/* 自服务端点。portal 不响应时 console 接管。
      if (handleSso({ req, res, url, dataDir, issueSession, twofaKey, guard: loginGuard })) return
      if (handlePortal({ req, res, url, auth, dataDir, manifest, loginPage, twofaKey })) return
      // 管理台（总览 + 成员/模型/实例/插件操作页）统一委托 console.mjs：
      // 仅 admin；页面未登录回登录页；POST API 另校验 Origin 同源。
      if (url.pathname === '/console' || url.pathname.startsWith('/console/')) {
        try {
          if (handleConsole({ req, res, url, auth, loginPage, manifest, getState, dataDir, runner: pluginRunner, twofaKey })) return
        } catch (error) {
          console.error('[gateway] console handler error:', error?.message ?? error)
          try { json(res, 500, { error: 'console error' }) } catch { /* 已响应 */ }
          return
        }
      }
      const ports = instancePortById()
      const rows = manifest.instances.map((spec) => {
        const info = ports[spec.id]
        const link = info.state === 'running'
          ? `<a href="http://${spec.id}.${portalHost}:${manifest.portalPort}/">${spec.id} 工作区</a>`
          : `${spec.id}（${info.state}）`
        return `<tr><td>${spec.id}</td><td>${esc(spec.account)}</td><td>${info.state}</td><td>${link}</td></tr>`
      }).join('')
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' })
      res.end(`<!doctype html><meta charset="utf-8"><title>卡巴格 · 入口</title>
<style>body{font-family:system-ui;background:#f6f7f9;color:#1f2937;margin:2rem}table{border-collapse:collapse}td,th{border:1px solid #e5e7eb;padding:.5rem .9rem}a{color:#2563eb}</style>
<h1>卡巴格 · 员工入口</h1><table>
<tr><th>实例</th><th>账号</th><th>状态</th><th>入口</th></tr>${rows}</table>
${auth.error === undefined
    ? `<p><a href="/me">个人中心</a>（${esc(auth.record.account)} 已登录）</p>`
    : '<p style="color:#6b7280">首次进入工作区会先要求登录（账号由管理员发放）。</p>'}
<p><a href="/console">管理台总览（管理员）</a></p>`)
      return
    }

    // 3) 实例子域：必须已登录，且账号绑定该实例。
    const auth = authFromRequest(secret, accountsStore, req)
    if (auth.error === 'disabled') {
      res.writeHead(403, { 'content-type': 'text/plain; charset=utf-8' })
      res.end('账号已禁用，请联系管理员。')
      return
    }
    if (auth.error !== undefined) {
      res.writeHead(401, { 'content-type': 'text/html; charset=utf-8' })
      res.end(loginPage())
      return
    }
    if (auth.record.instanceId !== subdomainId) {
      res.writeHead(403, { 'content-type': 'text/plain; charset=utf-8' })
      res.end(`账号 ${auth.record.account} 绑定的实例不是 ${subdomainId}，拒绝访问。`)
      return
    }

    // 4) 反代到实例（实例只绑 127.0.0.1）。剥掉网关 Cookie 再转发。
    const target = manifest.instances.find((spec) => spec.id === subdomainId)
    const state = getState()
    if (state.instances[subdomainId]?.state !== 'running') {
      res.writeHead(502, { 'content-type': 'text/plain; charset=utf-8' })
      res.end(`实例 ${subdomainId} 未运行（${state.instances[subdomainId]?.state ?? 'unknown'}）`)
      return
    }
    const headers = { ...req.headers }
    delete headers.cookie
    delete headers.connection
    const proxy = httpRequest(
      { host: '127.0.0.1', port: target.port, method: req.method, path: req.url, headers },
      (upstream) => {
        res.writeHead(upstream.statusCode, upstream.headers)
        upstream.pipe(res)
      },
    )
    proxy.on('error', () => {
      res.writeHead(502, { 'content-type': 'text/plain; charset=utf-8' })
      res.end(`实例 ${subdomainId} 连接失败`)
    })
    req.pipe(proxy)
  })

  // WebSocket 升级：同样走认证与绑定，然后原样转发握手并双向接管字节流。
  server.on('upgrade', (req, socket, head) => {
    const hostHeader = req.headers.host ?? ''
    const accountsStore = existsSync(accountsFile)
      ? JSON.parse(readFileSync(accountsFile, 'utf8'))
      : { accounts: [] }
    const deny = (code, reason) => {
      socket.write(`HTTP/1.1 ${code} ${reason}\r\nconnection: close\r\n\r\n`)
      socket.destroy()
    }
    const subdomainId = instanceIdFromHost(hostHeader, manifest)
    if (subdomainId === null) return deny(404, 'not found')
    const auth = authFromRequest(secret, accountsStore, req)
    if (auth.error !== undefined) return deny(401, 'unauthenticated')
    if (auth.record.instanceId !== subdomainId) return deny(403, 'forbidden')
    const target = manifest.instances.find((spec) => spec.id === subdomainId)
    const upstream = netConnect(target.port, '127.0.0.1', () => {
      const lines = [`${req.method} ${req.url} HTTP/1.1`]
      for (let i = 0; i < req.rawHeaders.length; i += 2) {
        const name = req.rawHeaders[i]
        if (name.toLowerCase() === 'cookie') continue
        lines.push(`${name}: ${req.rawHeaders[i + 1]}`)
      }
      upstream.write(`${lines.join('\r\n')}\r\n\r\n`)
      if (head.length > 0) upstream.write(head)
      upstream.pipe(socket)
      socket.pipe(upstream)
    })
    upstream.on('error', () => deny(502, 'bad gateway'))
    socket.on('error', () => upstream.destroy())
  })

  return server
}

export { ROLE_RANK, TOKEN_TTL_SECONDS }
