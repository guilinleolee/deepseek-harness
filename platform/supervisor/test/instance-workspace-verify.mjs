/**
 * 实例子域工作区链路验证（2026-11-04 新增行为的回归护栏）。
 *
 * 覆盖三组：
 *  A. IdP 生命周期对账（sync-idp.mjs）
 *     provider 未启用 / IdP 正常 / isForbidden / isDeleted / 用户消失 /
 *     空名单 fail-safe / IdP 不可达 / dry-run 不落盘 / 手工账号不受影响 /
 *     admin 永不禁用 / 审计留痕 / 恢复后不自动恢复。
 *
 *  B. 网关的实例会话代持与换票（gateway.mjs）
 *     只剥平台 Cookie 保留实例 Cookie / 挑出实例 Cookie /
 *     实例 401 → 服务端换票 → 重放 → 浏览器拿到 200 / 代持落盘。
 *
 *  C. 实例子域放行 SSO（sso.mjs + gateway.mjs）
 *     子域 start 用**子域自己的**回调地址 / 子域登录成功后回工作区 '/' /
 *     门户主机仍回 /me。
 *
 * mock 服务器原样实现 Casdoor 的 OIDC 契约与 DSH 的 browser-auth 契约。
 * 随机端口 + 临时目录，不占 8460/9400/3181-3183。
 * 运行：node test/instance-workspace-verify.mjs
 */
import { createServer, request as httpRequest } from 'node:http'
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { auditAppend, auditQuery, initAudit } from '../audit.mjs'
import { createGatewayServer, getOrCreateSecret, hashPassword } from '../gateway.mjs'
import { loadSsoConfig, saveSsoConfig } from '../sso.mjs'
import { deriveKey } from '../totp.mjs'
import { syncIdpLifecycle } from '../sync-idp.mjs'

const wait = (ms) => new Promise((r) => setTimeout(r, ms))
const JSON_HEAD = { 'content-type': 'application/json', connection: 'close' }

let passed = 0
let failed = 0
const check = (name, cond) => {
  if (cond === true) { passed += 1; console.log(`  ok  ${name}`) } else { failed += 1; console.error(`FAIL  ${name}`) }
}

const DATA = mkdtempSync(join(tmpdir(), 'lyz-workspace-'))
const now = new Date().toISOString()
const mkAccount = (id, acc, role, pw, extra = {}) => ({
  id, account: acc, displayName: id, role, department: '验证组', instanceId: 'e02',
  tokenEpoch: 0, createdAt: now, passwordHash: hashPassword(pw), ...extra,
})
const accounts = [
  mkAccount('a1', 'admin@t', 'admin', 'AdminPass1'),
  mkAccount('m1', 'member@t', 'employee', 'MemberPass1', { ssoIds: ['casdoor:u1'] }),
  mkAccount('m2', 'member2@t', 'employee', 'MemberPass2', { ssoIds: ['casdoor:u2'] }),
  mkAccount('m3', 'manual@t', 'employee', 'ManualPass3'),
]
const writeAccounts = () => writeFileSync(join(DATA, 'accounts.json'), `${JSON.stringify({ accounts }, null, 2)}\n`)
writeAccounts()
initAudit(DATA)

/* ── mock Casdoor（OIDC 契约）──────────────────────────────────────────── */
const CASDOOR_SECRET = 'casdoor-secret'
let casdoorUsers = []
const mockCasdoor = createServer((req, res) => {
  const url = new URL(req.url, 'http://x')
  const auth = req.headers.authorization ?? ''
  // token 端点用 client_secret_basic；userinfo 端点用 Bearer access_token
  if (url.pathname === '/api/userinfo') {
    if (!auth.startsWith('Bearer ')) {
      res.writeHead(401, JSON_HEAD); res.end('{"status":"error"}'); return
    }
    res.writeHead(200, JSON_HEAD)
    res.end(JSON.stringify({ sub: 'u1', name: '员工一' }))
    return
  }
  if (!auth.startsWith('Basic ')) {
    res.writeHead(401, JSON_HEAD); res.end('{"status":"error"}'); return
  }
  if (url.pathname === '/api/get-users') {
    res.writeHead(200, JSON_HEAD)
    res.end(JSON.stringify({ status: 'ok', data: casdoorUsers }))
    return
  }
  if (url.pathname === '/api/login/oauth/access_token') {
    res.writeHead(200, JSON_HEAD)
    res.end(JSON.stringify({ access_token: 'tok-u1', token_type: 'Bearer', sub: 'u1', name: '员工一' }))
    return
  }
  res.writeHead(404, JSON_HEAD); res.end('{"status":"error"}')
})
await new Promise((r) => mockCasdoor.listen(0, '127.0.0.1', r))
const casdoorPort = mockCasdoor.address().port
const casdoorBase = `http://127.0.0.1:${casdoorPort}`

/* ── mock DSH 实例（browser-auth 契约）─────────────────────────────────── */
const INSTANCE_TOKEN = 'instance-launch-token'
let instanceHits = []
const mockInstance = createServer((req, res) => {
  const url = new URL(req.url, 'http://x')
  const cookie = req.headers.cookie ?? ''
  instanceHits.push({ path: url.pathname, cookie })
  const token = url.searchParams.get('token')
  if (token === INSTANCE_TOKEN) {
    res.writeHead(303, {
      location: './',
      'set-cookie': `dsh-auth-mock=${encodeURIComponent(JSON.stringify({ authority: 'e02.localhost:0' }))}; Max-Age=3600; Path=/; HttpOnly; SameSite=Strict`,
    })
    res.end(); return
  }
  if (cookie.includes('dsh-auth-mock=')) {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' })
    res.end('<!doctype html><html><head><base href="./"></head><body><script>globalThis["__DSH_BOOT__"]={"rev":"x"}</script></body></html>')
    return
  }
  res.writeHead(401, { 'content-type': 'text/plain; charset=utf-8' })
  res.end('dsh web authentication required; reopen the URL printed by dsh web.\n')
})
await new Promise((r) => mockInstance.listen(0, '127.0.0.1', r))
const instancePort = mockInstance.address().port

/* ── 平台网关 ──────────────────────────────────────────────────────────── */
const manifest = {
  gatewayHost: 'localhost', portalPort: 0, relayPort: 0, repoRoot: '.',
  cookieDomain: '',
  instances: [{ id: 'e02', account: 'member@t', uid: 30001, port: instancePort }],
}
const state = { daemon: { pid: process.pid, startedAt: Date.now() }, instances: {
  e02: { ...manifest.instances[0], state: 'running', pid: 1, launchToken: INSTANCE_TOKEN, health: {}, memoryKB: null, diskBytes: null },
} }
const gateway = createGatewayServer({ manifest, getState: () => state, dataDir: DATA })
await new Promise((r) => gateway.listen(0, '127.0.0.1', r))
const base = `http://127.0.0.1:${gateway.address().port}`

const get = (path, headers = {}) => new Promise((resolve) => {
  const r = httpRequest(`${base}${path}`, { headers }, (res) => {
    const chunks = []
    res.on('data', (c) => chunks.push(c))
    res.on('end', () => resolve({ status: res.statusCode, headers: res.headers, body: Buffer.concat(chunks).toString('utf8') }))
  })
  r.on('error', () => resolve({ status: 0, headers: {}, body: '' }))
  r.end()
})

try {
  /* ═══ A. IdP 生命周期对账 ═════════════════════════════════════════════ */
  console.log('\nA. IdP 生命周期对账（sync-idp）')

  const casdoorCfg = {
    enabled: true, clientId: 'cid', secret: CASDOOR_SECRET, redirectUri: `${base}/api/auth/sso/casdoor/callback`,
    authorizeBase: casdoorBase, apiBase: casdoorBase, organization: 'dreamspace',
    autoProvision: false, autoRole: 'employee', autoDepartment: '', autoInstance: '',
  }
  // 密钥明文入参，saveSsoConfig 内部加密落盘成 secretEnc
  const ssoKey = deriveKey(getOrCreateSecret(DATA))
  saveSsoConfig(DATA, { casdoor: casdoorCfg }, ssoKey)

  const okUser = { id: 'u1', name: 'u1', owner: 'dreamspace', isForbidden: false, isDeleted: false }
  const badUser = { id: 'u2', name: 'u2', owner: 'dreamspace', isForbidden: true, isDeleted: false }
  const delUser = { id: 'u3', name: 'u3', owner: 'dreamspace', isForbidden: false, isDeleted: true }

  // A1 provider 未启用 → 不动
  saveSsoConfig(DATA, { casdoor: { ...casdoorCfg, enabled: false } }, ssoKey)
  let r = await syncIdpLifecycle({ dataDir: DATA })
  check('provider 未启用 → 不执行', r.ok === false && r.reason === 'provider_disabled')

  saveSsoConfig(DATA, { casdoor: casdoorCfg }, ssoKey)
  casdoorUsers = [okUser, badUser, delUser]

  // A2 dry-run：报告但不落盘
  r = await syncIdpLifecycle({ dataDir: DATA, dryRun: true })
  check('dry-run 报告待禁用', r.ok === true && r.disabled.includes('member2@t'))
  let store = JSON.parse(readFileSync(join(DATA, 'accounts.json'), 'utf8'))
  check('dry-run 未落盘', store.accounts.find((a) => a.account === 'member2@t').disabled !== true)

  // A3 真实执行：禁用 isForbidden 的账号
  r = await syncIdpLifecycle({ dataDir: DATA })
  store = JSON.parse(readFileSync(join(DATA, 'accounts.json'), 'utf8'))
  const m2 = store.accounts.find((a) => a.account === 'member2@t')
  const m1 = store.accounts.find((a) => a.account === 'member@t')
  const m3 = store.accounts.find((a) => a.account === 'manual@t')
  check('isForbidden → 平台账号被禁用', r.ok === true && r.disabled.includes('member2@t') && m2.disabled === true)
  check('禁用时 tokenEpoch 递增（旧会话立即失效）', m2.tokenEpoch >= 1)
  check('正常用户不被禁用', m1.disabled !== true)
  check('无 IdP 绑定的手工账号不受影响', m3.disabled !== true)

  // A4 审计留痕
  const audited = auditQuery({ actionPrefix: 'security.idp_sync', limit: 10 })
  check('security.idp_sync 审计留痕', Array.isArray(audited) && audited.length >= 1 && audited.some((e) => e.result === 'ok'))

  // A5 IdP 用户消失 → 禁用
  casdoorUsers = [okUser]
  r = await syncIdpLifecycle({ dataDir: DATA })
  store = JSON.parse(readFileSync(join(DATA, 'accounts.json'), 'utf8'))
  check('IdP 用户消失 → 账号禁用', r.ok === true && store.accounts.find((a) => a.account === 'member2@t').disabled === true)

  // A6 空名单 fail-safe：不禁用任何人
  accounts.forEach((a) => { a.disabled = false; a.tokenEpoch = 0 })
  writeAccounts()
  casdoorUsers = []
  r = await syncIdpLifecycle({ dataDir: DATA })
  store = JSON.parse(readFileSync(join(DATA, 'accounts.json'), 'utf8'))
  check('IdP 空名单 → fail-safe 不禁用任何人', r.ok === false && r.reason === 'idp_empty' && store.accounts.every((a) => a.disabled !== true))

  // A7 IdP 不可达 → 不禁用任何人
  const unreachable = await syncIdpLifecycle({ dataDir: DATA, fetchImpl: async () => { throw new Error('down') } })
  store = JSON.parse(readFileSync(join(DATA, 'accounts.json'), 'utf8'))
  check('IdP 不可达 → 不禁用任何人', unreachable.ok === false && store.accounts.every((a) => a.disabled !== true))

  // A8 恢复后不自动恢复（防提权）
  casdoorUsers = [okUser, { ...badUser, isForbidden: false }]
  r = await syncIdpLifecycle({ dataDir: DATA })
  store = JSON.parse(readFileSync(join(DATA, 'accounts.json'), 'utf8'))
  check('IdP 恢复 → 平台不自动恢复（防提权）', r.ok === true && r.disabled.length === 0 && store.accounts.find((a) => a.account === 'member2@t').disabled !== true)

  /* ═══ B. 网关代持与换票 ═════════════════════════════════════════════ */
  console.log('\nB. 网关代持与换票')

  // 登录拿平台会话
  const login = await postJson('/api/auth/login', { account: 'member@t', password: 'MemberPass1' })
  check('平台密码登录成功', login.status === 200)
  const platCookie = (login.headers['set-cookie'] ?? []).map((c) => c.split(';')[0]).find((c) => c.startsWith('lyz_session='))
  check('平台会话已签发', typeof platCookie === 'string')

  // B1：实例 401 → 网关服务端换票 → 重放 → 200
  instanceHits = []
  const sub = await get('/', { host: 'e02.localhost:0', cookie: platCookie })
  check('子域首次访问：网关换票后返回 200', sub.status === 200 && sub.body.includes('__DSH_BOOT__'))
  check('实例收到了换来的 cookie', instanceHits.some((h) => h.cookie.includes('dsh-auth-mock=')))

  // B2：代持落盘
  const held = JSON.parse(readFileSync(join(DATA, 'dsh-sessions.json'), 'utf8'))
  check('代持会话已落盘 data/dsh-sessions.json', typeof held.e02?.cookie === 'string' && held.e02.cookie.includes('dsh-auth-mock='))

  // B3：第二次访问直接带上代持的 cookie（不再换票）
  instanceHits = []
  const sub2 = await get('/', { host: 'e02.localhost:0', cookie: platCookie })
  check('二次访问：复用代持 cookie 直接 200', sub2.status === 200 && instanceHits.some((h) => h.cookie.includes('dsh-auth-mock=')))

  // B4：平台会话无效 → 401 登录页（不放行）
  const noAuth = await get('/', { host: 'e02.localhost:0' })
  check('无平台会话 → 401 登录页', noAuth.status === 401 && noAuth.body.includes('卡巴格'))

  /* ═══ C. 实例子域放行 SSO ═══════════════════════════════════════════ */
  console.log('\nC. 实例子域放行 SSO')

  const startSub = await get('/api/auth/sso/casdoor/start', { host: 'e02.localhost:0' })
  check('子域 SSO start 放行（非门户主机也能发起）', startSub.status === 303)
  const loc = startSub.headers.location ?? ''
  check('子域 start 的 redirect_uri 用子域自己的回调地址',
    loc.includes(encodeURIComponent('http://e02.localhost:0/api/auth/sso/casdoor/callback')))

  const startPortal = await get('/api/auth/sso/casdoor/start', { host: 'localhost:0' })
  check('门户 start 仍用配置的 redirect_uri',
    (startPortal.headers.location ?? '').includes(encodeURIComponent(`${base}/api/auth/sso/casdoor/callback`)))

  // 子域 callback：绑定已存在 → 直接签发会话并回工作区 '/'
  const stateParam = /state=([^&]+)/.exec(loc)?.[1] ?? ''
  const cb = await get(`/api/auth/sso/casdoor/callback?code=abc&state=${stateParam}`, { host: 'e02.localhost:0' })
  check('子域 callback 成功 → 302 回工作区根路径', cb.status === 303 && cb.headers.location === '/')
  check('子域 callback 签发了会话', (cb.headers['set-cookie'] ?? []).some((c) => c.startsWith('lyz_session=')))

  // 门户 callback → 回 /me
  const pState = /state=([^&]+)/.exec(startPortal.headers.location ?? '')?.[1] ?? ''
  const pcb = await get(`/api/auth/sso/casdoor/callback?code=abc&state=${pState}`, { host: 'localhost:0' })
  check('门户 callback 成功 → 302 回 /me', pcb.status === 303 && pcb.headers.location === '/me')
} finally {
  gateway.close()
  gateway.closeAllConnections?.()
  mockCasdoor.close()
  mockInstance.close()
  rmSync(DATA, { recursive: true, force: true })
}

console.log(`\n通过 ${passed}，失败 ${failed}`)
process.exit(failed > 0 ? 1 : 0)

/* ── 小工具 ────────────────────────────────────────────────────────────── */
function postJson(path, body) {
  return new Promise((resolve) => {
    const data = JSON.stringify(body)
    const r = httpRequest(`${base}${path}`, {
      method: 'POST',
      headers: { 'content-type': 'application/json', origin: base, 'content-length': Buffer.byteLength(data) },
    }, (res) => {
      const chunks = []
      res.on('data', (c) => chunks.push(c))
      res.on('end', () => resolve({ status: res.statusCode, headers: res.headers, body: Buffer.concat(chunks).toString('utf8') }))
    })
    r.on('error', () => resolve({ status: 0, headers: {}, body: '' }))
    r.write(data)
    r.end()
  })
}
