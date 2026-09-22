/**
 * 卡巴格企业平台 · 认证网关（任务书阶段 2）。
 *
 * 职责：登录签发 JWT（HttpOnly Cookie）；按 Host 头把已认证请求反代到
 * 该账号绑定的实例（<实例id>.<portal 主机名> → 127.0.0.1:<实例端口>，
 * 路径不重写，SPA 与 WebSocket 原样穿透）；未登录/未绑定一律拒绝。
 * 实例侧零改动——实例通过自身 `--trusted-host` 信任围栏接受网关转发的
 * Host，且只绑定 127.0.0.1，生产环境员工物理上绕不过网关。
 *
 * 安全语义（对齐任务书决定 5 与阶段 0 矩阵）：
 * - 密码 scrypt 加盐哈希存储；JWT HS256，30 分钟过期；
 * - 撤销 = 账号 tokenEpoch 递增，旧令牌全部失效（设备级撤销走阶段 3 控制面）；
 * - 实时校验账号↔实例绑定：改绑立即生效，无需等令牌过期；
 * - 网关只做身份与绑定判定，不读任何会话/内容正文。
 */
import { createServer, request as httpRequest } from 'node:http'
import { connect as netConnect } from 'node:net'
import { createHmac, randomBytes, scryptSync, timingSafeEqual } from 'node:crypto'
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'

import { handleConsole } from './console.mjs'
import { createJobRunner } from './plugins-gov.mjs'

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
    instanceId: a.instanceId,
    tokenEpoch: a.tokenEpoch,
    createdAt: a.createdAt,
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
  writeFileSync(join(dataDir, 'accounts.json'), `${JSON.stringify(store, null, 2)}\n`)
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

export function addAccount(dataDir, { account, instanceId, role, displayName, password }) {
  const store = loadAccounts(dataDir)
  if (store.accounts.some((a) => a.account === account)) {
    throw new Error(`账号已存在: ${account}`)
  }
  const record = {
    id: `acc-${randomBytes(6).toString('hex')}`,
    account,
    displayName: displayName ?? account.split('@')[0],
    role,
    instanceId,
    tokenEpoch: 0,
    createdAt: new Date().toISOString(),
    passwordHash: hashPassword(password),
  }
  store.accounts.push(record)
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

function getOrCreateSecret(dataDir) {
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

/** 从 Host 头解析实例 id（"<id>.<portal 主机>[:port]"），非子域返回 null。 */
function instanceIdFromHost(hostHeader, manifest) {
  const host = (hostHeader ?? '').split(':')[0].toLowerCase()
  const portalHost = (manifest.gatewayHost ?? 'localhost').split(':')[0].toLowerCase()
  if (!host.endsWith(`.${portalHost}`)) return null
  const id = host.slice(0, -1 * (portalHost.length + 1))
  return manifest.instances.some((spec) => spec.id === id) ? id : null
}

/* ── 网关服务器 ─────────────────────────────────────────────────────────── */

const LOGIN_PAGE = (error = '') => `<!doctype html><meta charset="utf-8">
<title>卡巴格 · 登录</title>
<style>body{font-family:system-ui;background:#101426;color:#e8eaf6;display:grid;place-items:center;height:100vh;margin:0}
form{background:#1a2038;padding:2rem 2.5rem;border-radius:12px;min-width:280px}
input,button{display:block;width:100%;margin:.5rem 0;padding:.6rem;border-radius:6px;border:1px solid #39406e;background:#0c101f;color:#e8eaf6;box-sizing:border-box}
button{background:#4f6ef7;border:none;cursor:pointer;font-weight:600}
.err{color:#ff8a80;font-size:.9rem;min-height:1.2em}</style>
<form onsubmit="login(event)"><h2 style="margin-top:0">卡巴格 · 登录</h2>
<input id="acc" placeholder="账号（邮箱）" autocomplete="username">
<input id="pw" type="password" placeholder="密码" autocomplete="current-password">
<div class="err">${error}</div><button>登录</button></form>
<script>
async function login(ev){ev.preventDefault();
 const r=await fetch('/api/auth/login',{method:'POST',headers:{'content-type':'application/json'},
   body:JSON.stringify({account:acc.value,password:pw.value})});
 if(r.ok){location.reload()}else{document.querySelector('.err').textContent='账号或密码错误'}}
</script>`

/**
 * 创建网关服务器。依赖注入：
 * @param manifest - instances.json 的内容（instances / gatewayHost / portalPort）
 * @param getState - () => supervisor 状态（实例 id → port / state）
 * @param dataDir - data/ 目录（accounts.json、auth-secret.key 所在）
 */
export function createGatewayServer({ manifest, getState, dataDir }) {
  const secret = getOrCreateSecret(dataDir)
  const pluginRunner = createJobRunner({ dataDir, manifest, repoRoot: resolve(dirname(dataDir), manifest.repoRoot) })
  const accountsFile = join(dataDir, 'accounts.json')
  const portalHost = manifest.gatewayHost ?? 'localhost'
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
    if (url.pathname === '/api/auth/login' && req.method === 'POST') {
      let body = ''
      req.on('data', (chunk) => { body += chunk })
      req.on('end', () => {
        let account = ''
        let password = ''
        try {
          const parsed = JSON.parse(body || '{}')
          account = String(parsed.account ?? '')
          password = String(parsed.password ?? '')
        } catch { /* 当作空凭据处理 */ }
        const record = accountsStore.accounts.find((a) => a.account === account)
        if (record?.disabled) {
          res.writeHead(401, { 'content-type': 'application/json; charset=utf-8' })
          res.end(JSON.stringify({ error: '账号已禁用，请联系管理员' }))
          return
        }
        if (!record || !verifyPassword(record, password)) {
          res.writeHead(401, { 'content-type': 'application/json; charset=utf-8' })
          res.end(JSON.stringify({ error: 'invalid credentials' }))
          return
        }
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
      if (url.pathname === '/api/auth/logout') {
        res.setHeader('set-cookie', `${COOKIE_NAME}=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0`)
        res.writeHead(200, { 'content-type': 'text/plain; charset=utf-8' })
        res.end('logged out')
        return
      }
      if (url.pathname === '/status.json') {
        const auth = authFromRequest(secret, accountsStore, req)
        if (auth.error !== undefined || auth.record.role !== 'admin') {
          res.writeHead(401, { 'content-type': 'application/json; charset=utf-8' })
          res.end(JSON.stringify({ error: 'admin only' }))
          return
        }
        res.writeHead(200, { 'content-type': 'application/json; charset=utf-8' })
        res.end(JSON.stringify(getState()))
        return
      }
      // 管理台（总览 + 成员/模型/实例/插件操作页）统一委托 console.mjs：
      // 仅 admin；页面未登录回登录页；POST API 另校验 Origin 同源。
      if (url.pathname === '/console' || url.pathname.startsWith('/console/')) {
        const auth = authFromRequest(secret, accountsStore, req)
        try {
          if (handleConsole({ req, res, url, auth, loginPage: LOGIN_PAGE, manifest, getState, dataDir, runner: pluginRunner })) return
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
        return `<tr><td>${spec.id}</td><td>${spec.account}</td><td>${info.state}</td><td>${link}</td></tr>`
      }).join('')
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' })
      res.end(`<!doctype html><meta charset="utf-8"><title>卡巴格 · 入口</title>
<style>body{font-family:system-ui;background:#101426;color:#e8eaf6;margin:2rem}table{border-collapse:collapse}td,th{border:1px solid #39406e;padding:.5rem .9rem}a{color:#8ab4ff}</style>
<h1>卡巴格 · 员工入口</h1><table>
<tr><th>实例</th><th>账号</th><th>状态</th><th>入口</th></tr>${rows}</table>
<p style="color:#9fa8da">首次进入工作区会先要求登录（账号由管理员发放）。</p>
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
      res.end(LOGIN_PAGE())
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
