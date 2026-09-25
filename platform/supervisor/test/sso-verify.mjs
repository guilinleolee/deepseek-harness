/**
 * SSO 骨架（阶段 11C）mock 全流程验证：本地 mock OAuth 服务器（authorize 303
 * 回调 + token JSON + userinfo JSON），sso.json 的 authorizeBase/apiBase 指向
 * mock，curl 等价走通：登录页按钮 → start 303 → authorize → callback（未绑定
 * → 绑定页）→ bind 错密码拒/对密码绑并登录 → 二次 SSO 直达 → state 伪造拒 →
 * 未启用 provider 拒。真实企业微信/钉钉待配置凭证后真机验证。
 *
 * 随机端口 + 临时目录，不占 8460/9400/3181-3183。
 * 运行：node test/sso-verify.mjs
 */
import { createServer } from 'node:http'
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { auditAppend, auditQuery, initAudit } from '../audit.mjs'
import { createGatewayServer, getOrCreateSecret, hashPassword } from '../gateway.mjs'
import { _putPendingStateForTest, SSO_PENDING_LIMIT, resolveSsoIdentity, saveSsoConfig } from '../sso.mjs'
import { deriveKey } from '../totp.mjs'

const wait = (ms) => new Promise((r) => setTimeout(r, ms))
const JSON_HEAD = { 'content-type': 'application/json', connection: 'close' }

let passed = 0
let failed = 0
const check = (name, cond) => {
  if (cond === true) { passed += 1; console.log(`  ok  ${name}`) } else { failed += 1; console.error(`FAIL  ${name}`) }
}

const DATA = mkdtempSync(join(tmpdir(), 'lyz-sso-'))
const now = new Date().toISOString()
const mkAccount = (id, acc, role, pw) => ({
  id, account: acc, displayName: id, role, department: '验证组', instanceId: 'e02',
  tokenEpoch: 0, createdAt: now, passwordHash: hashPassword(pw),
})
writeFileSync(join(DATA, 'accounts.json'), `${JSON.stringify({ accounts: [
  mkAccount('a1', 'admin@t', 'admin', 'AdminPass1'),
  mkAccount('m1', 'member@t', 'employee', 'MemberPass1'),
] }, null, 2)}\n`)
initAudit(DATA)

const manifest = {
  gatewayHost: 'localhost', portalPort: 0, relayPort: 0, repoRoot: '.',
  instances: [
    { id: 'e01', account: 'admin@t', uid: 1, port: 1 },
    { id: 'e02', account: 'member@t', uid: 2, port: 2 },
  ],
}
const gateway = createGatewayServer({ manifest, getState: () => ({ instances: {} }), dataDir: DATA })
await new Promise((r) => gateway.listen(0, '127.0.0.1', r))
const base = `http://127.0.0.1:${gateway.address().port}`
const get = (path, cookie) => fetch(`${base}${path}`, { headers: cookie ? { cookie, connection: 'close' } : { connection: 'close' }, redirect: 'manual' })
const getAbs = (absUrl, cookie) => fetch(absUrl, { headers: cookie ? { cookie, connection: 'close' } : { connection: 'close' }, redirect: 'manual' })
const post = (path, body, cookie) => fetch(`${base}${path}`, { method: 'POST', headers: cookie ? { ...JSON_HEAD, cookie } : JSON_HEAD, body: JSON.stringify(body ?? {}) })
const login = async (acc, pw) => {
  const res = await post('/api/auth/login', { account: acc, password: pw })
  return { status: res.status, cookie: res.headers.getSetCookie()[0]?.split(';')[0], body: await res.json().catch(() => ({})) }
}
const waitForAudit = async (pred, timeoutMs = 4000) => {
  const deadline = Date.now() + timeoutMs
  while (Date.now() < deadline) {
    const e = auditQuery({ limit: 10000 }).find(pred)
    if (e !== undefined) return e
    await wait(40)
  }
  return undefined
}

/* mock OAuth 服务器（企业微信协议形态）*/
const MOCK_USER_ID = 'mock-user-1'
let authorizeHits = 0
let tokenHits = 0
let userinfoHits = 0
const mock = createServer((req, res) => {
  const url = new URL(req.url, 'http://mock')
  if (url.pathname === '/connect/oauth2/authorize') {
    authorizeHits += 1
    const back = `${decodeURIComponent(url.searchParams.get('redirect_uri'))}?code=mock-code-${authorizeHits}&state=${url.searchParams.get('state')}`
    res.writeHead(303, { location: back })
    res.end()
    return
  }
  if (url.pathname === '/gettoken') {
    tokenHits += 1
    res.writeHead(200, { 'content-type': 'application/json' })
    res.end(JSON.stringify({ errcode: 0, access_token: 'mock-access-token' }))
    return
  }
  if (url.pathname === '/auth/getuserinfo') {
    userinfoHits += 1
    res.writeHead(200, { 'content-type': 'application/json' })
    res.end(JSON.stringify({ errcode: 0, userid: MOCK_USER_ID, name: 'Mock 用户' }))
    return
  }
  res.writeHead(404)
  res.end()
})
await new Promise((r) => mock.listen(0, '127.0.0.1', r))
const mockBase = `http://127.0.0.1:${mock.address().port}`

try {
  /* 0. 未配置：登录页无按钮，start 404 */
  const loginBefore = await (await get('/login')).text()
  check('未配置时登录页无 SSO 按钮', !loginBefore.includes('/api/auth/sso/'))
  check('未启用 provider start 404', (await get('/api/auth/sso/wecom/start')).status === 404)

  /* 1. 配置（apiBase/authorizeBase 指向 mock——mock 验证的关键） */
  const key = deriveKey(getOrCreateSecret(DATA))
  saveSsoConfig(DATA, { wecom: {
    enabled: true, corpId: 'corp-001', agentId: '1000002', secret: 'wecom-secret-plain',
    redirectUri: `${base}/api/auth/sso/wecom/callback`,
    authorizeBase: mockBase, apiBase: mockBase,
  } }, key)
  check('secret 加密落盘（sso.json 不含明文）', !readFileSync(join(DATA, 'sso.json'), 'utf8').includes('wecom-secret-plain'))
  const loginAfter = await (await get('/login')).text()
  check('登录页出现企业微信按钮', loginAfter.includes('/api/auth/sso/wecom/start') && loginAfter.includes('企业微信'))

  /* 2. start → authorize → callback（未绑定 → 绑定页） */
  const start = await get('/api/auth/sso/wecom/start')
  const authorizeUrl = start.headers.get('location')
  check('start 303 到 mock authorize（含 state/redirect_uri）', start.status === 303
    && authorizeUrl.startsWith(`${mockBase}/connect/oauth2/authorize`)
    && authorizeUrl.includes('state=') && authorizeUrl.includes(encodeURIComponent(`${base}/api/auth/sso/wecom/callback`)))
  const authorizeRes = await fetch(authorizeUrl, { redirect: 'manual' })
  check('mock authorize 303 回调（code+state 原样回传）', authorizeRes.status === 303)
  const callbackUrl = authorizeRes.headers.get('location')
  check('回调携带 code 与 state', callbackUrl.includes('code=mock-code-1') && /state=[^&]+/.test(callbackUrl))
  const callback = await getAbs(callbackUrl)
  const callbackText = await callback.text()
  check('未绑定 → 200 绑定页', callback.status === 200 && callbackText.includes('绑定企业微信账号') && callbackText.includes('bindToken'))
  const bindToken = /id="bt" value="([^"]+)"/.exec(callbackText)?.[1]
  check('绑定页含一次性 bindToken', typeof bindToken === 'string' && bindToken.length > 20)
  check('token/userinfo 接口各命中一次', tokenHits === 1 && userinfoHits === 1)

  /* 3. bind：错密码拒 / 对密码绑定并登录 */
  const badBind = await post('/api/auth/sso/bind', { bindToken, account: 'member@t', password: 'WrongPass1' })
  check('错密码 401', badBind.status === 401)
  check('sso_bind fail 留痕', await waitForAudit((e) => e.action === 'auth.sso_bind' && e.result === 'fail' && e.detail?.reason === 'bad_password') !== undefined)
  // bindToken 一次性：失败后已消费，需重新走一遍拿新 token。
  const start2 = await get('/api/auth/sso/wecom/start')
  const cb2 = (await fetch(start2.headers.get('location'), { redirect: 'manual' })).headers.get('location')
  const bindToken2 = /id="bt" value="([^"]+)"/.exec(await (await getAbs(cb2)).text())?.[1]
  const goodBind = await post('/api/auth/sso/bind', { bindToken: bindToken2, account: 'member@t', password: 'MemberPass1' })
  const goodBody = await goodBind.json()
  check('对密码绑定成功 200 + cookie', goodBind.status === 200 && goodBody.ok === true && goodBind.headers.getSetCookie()[0] !== undefined)
  const ssoEvent = await waitForAudit((e) => e.action === 'auth.sso_bind' && e.result === 'ok' && e.target === 'member@t')
  check('sso_bind ok 留痕（含 ssoId）', ssoEvent !== undefined && ssoEvent.detail?.ssoId === `wecom:${MOCK_USER_ID}`)
  const persisted = JSON.parse(readFileSync(join(DATA, 'accounts.json'), 'utf8')).accounts.find((a) => a.account === 'member@t')
  check('ssoIds 落盘 accounts.json', Array.isArray(persisted.ssoIds) && persisted.ssoIds.includes(`wecom:${MOCK_USER_ID}`))
  const meCookie = goodBind.headers.getSetCookie()[0]?.split(';')[0]
  check('绑定后 cookie 可达 /me', (await get('/me', meCookie)).status === 200)

  /* 4. 二次 SSO 登录直达（免绑定） */
  const start3 = await get('/api/auth/sso/wecom/start')
  const cb3 = (await fetch(start3.headers.get('location'), { redirect: 'manual' })).headers.get('location')
  const direct = await getAbs(cb3)
  check('二次 SSO 直达登录（303 + cookie，无绑定页）', direct.status === 303 && direct.headers.getSetCookie()[0] !== undefined && !(await direct.text()).includes('绑定'))
  check('auth.sso_login 留痕', await waitForAudit((e) => e.action === 'auth.sso_login' && e.result === 'ok' && e.actor?.account === 'member@t' && e.detail?.provider === 'wecom') !== undefined)

  /* 4b. P2-2 fetch 超时 signal + P2-3 bind 并发走账号锁（无丢更新） */
  let capturedSignal = null
  const capturingFetch = (url, init) => {
    if (String(url).includes('/gettoken')) capturedSignal = init?.signal ?? null
    return fetch(url, init)
  }
  const identityOk = await resolveSsoIdentity('wecom', 'probe-code', DATA, key, capturingFetch)
  check('resolveSsoIdentity 直调成功', identityOk.ssoId === `wecom:${MOCK_USER_ID}`)
  check('fetch 携带 AbortSignal 超时参数（P2-2）', capturedSignal instanceof AbortSignal)
  const admin2 = await login('admin@t', 'AdminPass1')
  const bindTokenOf = async () => {
    const s = await get('/api/auth/sso/wecom/start')
    const cb = (await fetch(s.headers.get('location'), { redirect: 'manual' })).headers.get('location')
    return /id="bt" value="([^"]+)"/.exec(await (await getAbs(cb)).text())?.[1]
  }
  const [bt1, bt2] = await Promise.all([bindTokenOf(), bindTokenOf()])
  await Promise.all([
    post('/api/auth/sso/bind', { bindToken: bt1, account: 'member@t', password: 'MemberPass1' }),
    post('/api/auth/sso/bind', { bindToken: bt2, account: 'member@t', password: 'MemberPass1' }),
    post('/console/api/member/update', { account: 'member@t', department: '并发组' }, admin2.cookie),
  ])
  const afterConcurrent = JSON.parse(readFileSync(join(DATA, 'accounts.json'), 'utf8')).accounts.find((a) => a.account === 'member@t')
  check('并发 bind×2 + 管理台变更无丢更新（P2-3 同一把账号锁）',
    Array.isArray(afterConcurrent.ssoIds) && afterConcurrent.ssoIds.length === 1 && afterConcurrent.ssoIds[0] === `wecom:${MOCK_USER_ID}`
    && afterConcurrent.department === '并发组')

  /* 4c. state 洪泛上限（P2-1：打满 5000 → start 429；放后面，占满影响 start） */
  for (let i = 0; i < SSO_PENDING_LIMIT; i++) _putPendingStateForTest('wecom')
  check('state 打满上限后 start 429（P2-1）', (await get('/api/auth/sso/wecom/start')).status === 429)

  /* 5. state 伪造拒绝 */
  const fakeState = await get(`/api/auth/sso/wecom/callback?code=x&state=forged-state`)
  check('伪造 state 400', fakeState.status === 400)
  const noState = await get('/api/auth/sso/wecom/callback?code=x')
  check('缺 state 400', noState.status === 400)
} finally {
  gateway.close()
  gateway.closeAllConnections?.()
  mock.close()
  rmSync(DATA, { recursive: true, force: true })
}

console.log(`\n通过 ${passed}，失败 ${failed}`)
process.exit(failed > 0 ? 1 : 0)
