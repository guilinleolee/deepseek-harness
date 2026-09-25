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
import { randomBytes } from 'node:crypto'
import { mkdirSync, readFileSync, renameSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'

import { auditAppend, clientIp } from './audit.mjs'
import { saveAccounts, verifyPassword } from './gateway.mjs'
import { withAccountLock } from './console.mjs'
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

const DEFAULT_SSO = () => ({
  wecom: {
    enabled: false, corpId: '', agentId: '', secretEnc: '', redirectUri: '',
    authorizeBase: 'https://open.weixin.qq.com', apiBase: 'https://qyapi.weixin.qq.com',
  },
  dingtalk: {
    enabled: false, appKey: '', appSecretEnc: '', redirectUri: '',
    authorizeBase: 'https://login.dingtalk.com', apiBase: 'https://api.dingtalk.com',
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
  const tmp = `${path}.tmp`
  writeFileSync(tmp, `${JSON.stringify(config, null, 2)}\n`)
  renameSync(tmp, path)
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
  return `${config.authorizeBase}/oauth2/auth?client_id=${enc(config.appKey)}`
    + `&redirect_uri=${enc(redirectUri)}&response_type=code&scope=openid`
    + `&state=${enc(state)}`
}

/** 用 code 换用户标识。返回 { ssoId, name? }；任一步失败抛错（调用方转 502）。 */
export async function resolveSsoIdentity(provider, code, dataDir, key, fetchImpl = fetch) {
  const config = loadSsoConfig(dataDir)[provider]
  if (config === undefined || config.enabled !== true) throw new Error('SSO provider 未启用')
  if (provider === 'wecom') {
    const secret = getSsoSecret(dataDir, provider, key)
    const tokenRes = await fetchImpl(`${config.apiBase}/gettoken?corpid=${encodeURIComponent(config.corpId)}&corpsecret=${encodeURIComponent(secret)}`, { signal: AbortSignal.timeout(10_000) })
    if (!tokenRes.ok) throw new Error(`企业微信 token 接口失败（HTTP ${tokenRes.status}）`)
    const accessToken = (await tokenRes.json()).access_token
    if (typeof accessToken !== 'string' || accessToken === '') throw new Error('企业微信 token 接口未返回 access_token')
    const userRes = await fetchImpl(`${config.apiBase}/auth/getuserinfo?access_token=${encodeURIComponent(accessToken)}&code=${encodeURIComponent(code)}`, { signal: AbortSignal.timeout(10_000) })
    if (!userRes.ok) throw new Error(`企业微信用户接口失败（HTTP ${userRes.status}）`)
    const userBody = await userRes.json()
    if (typeof userBody.userid !== 'string' || userBody.userid === '') throw new Error('企业微信用户接口未返回 userid')
    return { ssoId: `wecom:${userBody.userid}`, name: userBody.name }
  }
  const secret = getSsoSecret(dataDir, provider, key)
  const tokenRes = await fetchImpl(`${config.apiBase}/v1.0/oauth2/token`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ client_id: config.appKey, client_secret: secret, code, grant_type: 'authorization_code' }),
    signal: AbortSignal.timeout(10_000),
  })
  if (!tokenRes.ok) throw new Error(`钉钉 token 接口失败（HTTP ${tokenRes.status}）`)
  const accessToken = (await tokenRes.json()).accessToken
  if (typeof accessToken !== 'string' || accessToken === '') throw new Error('钉钉 token 接口未返回 accessToken')
  const userRes = await fetchImpl(`${config.apiBase}/v1.0/contact/users/me`, {
    headers: { 'x-acs-dingtalk-access-token': accessToken },
    signal: AbortSignal.timeout(10_000),
  })
  if (!userRes.ok) throw new Error(`钉钉用户接口失败（HTTP ${userRes.status}）`)
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
 * SSO 路由（gateway 在裸 portal 主机分支调用）。
 * @param issueSession - (res, record) => void：签发 JWT Cookie（gateway 提供，
 *   与密码登录同一令牌语义：sub/epoch/TTL）。
 * @param twofaKey - 敏感配置派生根（sso secret 加密同源）。
 * @param guard - 登录限流器（绑定密码错误计入同桶；可缺省=不限流，测试用）。
 * @returns true 表示已响应。
 */
export function handleSso({ req, res, url, dataDir, issueSession, twofaKey, guard = null }) {
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
      .then((identity) => {
        const accounts = JSON.parse(readFileSync(join(dataDir, 'accounts.json'), 'utf8'))
        const record = accounts.accounts.find((a) => Array.isArray(a.ssoIds) && a.ssoIds.includes(identity.ssoId))
        if (record !== undefined) {
          if (record.disabled) {
            res.writeHead(403, { 'content-type': 'text/plain; charset=utf-8' })
            res.end('账号已禁用，请联系管理员。')
            return
          }
          void auditAppend({ actor: { account: record.account, role: record.role, ip }, action: 'auth.sso_login', target: record.account, result: 'ok', detail: { provider, ssoId: identity.ssoId } })
          issueSession(res, record)
          res.writeHead(303, { location: record.role === 'employee' ? '/me' : '/' })
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
        issueSession(res, record)
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
