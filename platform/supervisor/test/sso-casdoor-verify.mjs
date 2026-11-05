/**
 * SSO · Casdoor provider mock 全流程验证。
 *
 * 覆盖：配置落盘（clientId + secret 加密）→ 登录页按钮 → start 303 →
 * authorize 303 → callback（未绑定 → 绑定页）→ bind 错密码拒/对密码绑并登录 →
 * 二次 SSO 直达 → state 伪造/缺失 400 → 自动开通（JIT）→ 字段白名单 →
 * token/userinfo 端点失败降级 → resolveSsoIdentity 直调。
 *
 * mock 服务器原样实现 Casdoor 的 OIDC 契约（2026-11-03 discovery 实测）：
 *   - authorize : GET  /login/oauth/authorize
 *   - token     : POST /api/login/oauth/access_token（client_secret_basic）
 *   - userinfo  : GET  /api/userinfo   ← 不是 /api/login/oauth/userinfo（后者 404）
 *
 * 随机端口 + 临时目录，不占 8460/9400/3181-3183。
 * 运行：node test/sso-casdoor-verify.mjs
 */
import { createServer } from 'node:http'
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { auditAppend, auditQuery, initAudit } from '../audit.mjs'
import { createGatewayServer, getOrCreateSecret, hashPassword } from '../gateway.mjs'
import { loadSsoConfig, PROVIDER_FIELDS, resolveSsoIdentity, saveSsoConfig } from '../sso.mjs'
import { deriveKey } from '../totp.mjs'

const wait = (ms) => new Promise((r) => setTimeout(r, ms))
const JSON_HEAD = { 'content-type': 'application/json', connection: 'close' }

let passed = 0
let failed = 0
const check = (name, cond) => {
  if (cond === true) { passed += 1; console.log(`  ok  ${name}`) } else { failed += 1; console.error(`FAIL  ${name}`) }
}

const DATA = mkdtempSync(join(tmpdir(), 'lyz-sso-casdoor-'))
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
const waitForAudit = async (pred, timeoutMs = 4000) => {
  const deadline = Date.now() + timeoutMs
  while (Date.now() < deadline) {
    const e = auditQuery({ limit: 10000 }).find(pred)
    if (e !== undefined) return e
    await wait(40)
  }
  return undefined
}

/* mock OIDC 服务器（Casdoor 契约）*/
const MOCK_SUB = 'mock-casdoor-sub-1'
/** mock 当前返回的 subject：切换它即可模拟「另一个 Casdoor 用户首次登录」。 */
let mockSub = MOCK_SUB
/** mock 是否让 token 端点失败（验证 502 降级）。 */
let mockTokenFail = false
/** mock 是否让 userinfo 返回缺 sub/id 的响应（验证身份解析失败）。 */
let mockUserinfoNoSub = false
let casAuthorizeHits = 0
let casTokenHits = 0
let casUserinfoHits = 0
let casTokenAuth = null
let casTokenBody = null
let casUserinfoAuth = null
const mock = createServer((req, res) => {
  const url = new URL(req.url, 'http://mock')
  if (url.pathname === '/login/oauth/authorize') {
    casAuthorizeHits += 1
    const back = `${decodeURIComponent(url.searchParams.get('redirect_uri'))}?code=mock-casdoor-code-${casAuthorizeHits}&state=${url.searchParams.get('state')}`
    res.writeHead(303, { location: back })
    res.end()
    return
  }
  if (url.pathname === '/api/login/oauth/access_token') {
    casTokenHits += 1
    casTokenAuth = req.headers.authorization ?? null
    let raw = ''
    req.on('data', (chunk) => { raw += chunk })
    req.on('end', () => {
      casTokenBody = Object.fromEntries(new URLSearchParams(raw))
      if (mockTokenFail) {
        res.writeHead(500, { 'content-type': 'application/json' })
        res.end(JSON.stringify({ error: 'server_error', error_description: 'mock 故障' }))
        return
      }
      res.writeHead(200, { 'content-type': 'application/json' })
      res.end(JSON.stringify({ access_token: 'mock-casdoor-access-token', token_type: 'Bearer', expires_in: 3600, id_token: 'mock-id-token' }))
    })
    return
  }
  if (url.pathname === '/api/userinfo') {
    casUserinfoHits += 1
    casUserinfoAuth = req.headers.authorization ?? null
    if (mockUserinfoNoSub) {
      res.writeHead(200, { 'content-type': 'application/json' })
      res.end(JSON.stringify({ name: '无名用户' }))
      return
    }
    res.writeHead(200, { 'content-type': 'application/json' })
    res.end(JSON.stringify({ sub: mockSub, name: 'Mock Casdoor 用户', preferred_username: 'mock_casdoor', email: 'mock@casdoor.test' }))
    return
  }
  res.writeHead(404)
  res.end()
})
await new Promise((r) => mock.listen(0, '127.0.0.1', r))
const mockBase = `http://127.0.0.1:${mock.address().port}`

const CASDOOR_CLIENT_ID = 'mock-casdoor-client-id'
const CASDOOR_SECRET = 'casdoor-secret-plain'

try {
  const key = deriveKey(getOrCreateSecret(DATA))

  /* 0. 未配置：登录页无 Casdoor 按钮，start 404 */
  const loginBefore = await (await get('/login')).text()
  check('未配置时登录页无 Casdoor 按钮', !loginBefore.includes('/api/auth/sso/casdoor/'))
  check('未启用 provider start 404', (await get('/api/auth/sso/casdoor/start')).status === 404)

  /* 1. 配置落盘：clientId 明文（身份标识非密文）+ secret 加密 */
  saveSsoConfig(DATA, { casdoor: {
    enabled: true, clientId: CASDOOR_CLIENT_ID, secret: CASDOOR_SECRET,
    redirectUri: `${base}/api/auth/sso/casdoor/callback`,
    authorizeBase: mockBase, apiBase: mockBase,
  } }, key)
  const ssoRaw = readFileSync(join(DATA, 'sso.json'), 'utf8')
  check('secret 加密落盘（sso.json 不含明文）', !ssoRaw.includes(CASDOOR_SECRET))
  check('clientId 落盘（身份标识不是密文）', ssoRaw.includes(CASDOOR_CLIENT_ID))
  const cfg = loadSsoConfig(DATA).casdoor
  check('clientId 读回正确', cfg.clientId === CASDOOR_CLIENT_ID)
  check('secretEnc 非空且解密不还原为明文以外的形态', typeof cfg.secretEnc === 'string' && cfg.secretEnc.startsWith('enc:'))
  check('未知 provider 拒绝', (() => { try { saveSsoConfig(DATA, { nope: { enabled: true } }, key); return false } catch { return true } })())

  /* 1b. 字段白名单按 provider 收口：给 casdoor 传 appKey 不应落盘 */
  saveSsoConfig(DATA, { casdoor: { appKey: 'wrong-field-should-not-persist' } }, key)
  check('casdoor 不接受 appKey（字段按 provider 白名单）',
    !readFileSync(join(DATA, 'sso.json'), 'utf8').includes('wrong-field-should-not-persist'))

  /* 1c. provider 字段差异表完整性 */
  check('PROVIDER_FIELDS 三个 provider 齐备', ['wecom', 'dingtalk', 'casdoor'].every((p) =>
    typeof PROVIDER_FIELDS[p]?.idField === 'string' && typeof PROVIDER_FIELDS[p]?.secretField === 'string'))
  check('casdoor 身份标识字段为 clientId', PROVIDER_FIELDS.casdoor.idField === 'clientId')

  /* 2. 登录页出现 Casdoor 按钮 */
  const loginAfter = await (await get('/login')).text()
  check('登录页出现 Casdoor 按钮', loginAfter.includes('/api/auth/sso/casdoor/start') && loginAfter.includes('Casdoor'))

  /* 3. start → 303 authorize（OIDC 授权码契约） */
  const start = await get('/api/auth/sso/casdoor/start')
  const authorizeUrl = start.headers.get('location')
  check('start 303 到 mock authorize（client_id/redirect_uri/code/scope/state）', start.status === 303
    && authorizeUrl.startsWith(`${mockBase}/login/oauth/authorize`)
    && authorizeUrl.includes(`client_id=${CASDOOR_CLIENT_ID}`)
    && authorizeUrl.includes('response_type=code')
    && authorizeUrl.includes('scope=openid%20profile%20email')
    && authorizeUrl.includes('state=')
    && authorizeUrl.includes(encodeURIComponent(`${base}/api/auth/sso/casdoor/callback`)))

  /* 4. authorize → 303 回调 → 未绑定出绑定页 */
  const authorizeRes = await fetch(authorizeUrl, { redirect: 'manual' })
  check('mock authorize 303 回调（code+state 原样回传）', authorizeRes.status === 303)
  const callbackUrl = authorizeRes.headers.get('location')
  check('回调携带 code 与 state', callbackUrl.includes('code=mock-casdoor-code-1') && /state=[^&]+/.test(callbackUrl))
  const callback = await getAbs(callbackUrl)
  const callbackText = await callback.text()
  check('未绑定 → 200 绑定页（Casdoor）', callback.status === 200 && callbackText.includes('绑定Casdoor账号') && callbackText.includes('bindToken'))
  const bindToken = /id="bt" value="([^"]+)"/.exec(callbackText)?.[1]
  check('绑定页含一次性 bindToken', typeof bindToken === 'string' && bindToken.length > 20)

  /* 5. token/userinfo 契约：Basic 头 + form body + Bearer */
  check('token 端点与 userinfo 端点各命中一次', casTokenHits === 1 && casUserinfoHits === 1)
  check('token 请求走 client_secret_basic', casTokenAuth === `Basic ${Buffer.from(`${CASDOOR_CLIENT_ID}:${CASDOOR_SECRET}`).toString('base64')}`)
  check('token 请求体为标准授权码参数', casTokenBody?.grant_type === 'authorization_code'
    && casTokenBody?.code === 'mock-casdoor-code-1'
    && casTokenBody?.redirect_uri === `${base}/api/auth/sso/casdoor/callback`)
  check('userinfo 请求携带 Bearer 访问令牌', casUserinfoAuth === 'Bearer mock-casdoor-access-token')

  /* 6. bind：错密码拒 / 对密码绑定并登录 */
  const badBind = await post('/api/auth/sso/bind', { bindToken, account: 'member@t', password: 'WrongPass1' })
  check('错密码 401', badBind.status === 401)
  check('sso_bind fail 留痕', await waitForAudit((e) => e.action === 'auth.sso_bind' && e.result === 'fail' && e.detail?.reason === 'bad_password' && e.detail?.provider === 'casdoor') !== undefined)
  // bindToken 一次性：失败后已消费，需重新走一遍拿新 token。
  const start2 = await get('/api/auth/sso/casdoor/start')
  const cb2 = (await fetch(start2.headers.get('location'), { redirect: 'manual' })).headers.get('location')
  const bindToken2 = /id="bt" value="([^"]+)"/.exec(await (await getAbs(cb2)).text())?.[1]
  const goodBind = await post('/api/auth/sso/bind', { bindToken: bindToken2, account: 'member@t', password: 'MemberPass1' })
  const goodBody = await goodBind.json()
  check('对密码绑定成功 200 + cookie', goodBind.status === 200 && goodBody.ok === true && goodBind.headers.getSetCookie()[0] !== undefined)
  const ssoEvent = await waitForAudit((e) => e.action === 'auth.sso_bind' && e.result === 'ok' && e.target === 'member@t' && e.detail?.provider === 'casdoor')
  check('sso_bind ok 留痕（ssoId=casdoor:sub）', ssoEvent !== undefined && ssoEvent.detail?.ssoId === `casdoor:${MOCK_SUB}`)
  const persisted = JSON.parse(readFileSync(join(DATA, 'accounts.json'), 'utf8')).accounts.find((a) => a.account === 'member@t')
  check('ssoIds 落盘 accounts.json（casdoor: 前缀）', Array.isArray(persisted.ssoIds) && persisted.ssoIds.includes(`casdoor:${MOCK_SUB}`))
  const meCookie = goodBind.headers.getSetCookie()[0]?.split(';')[0]
  check('绑定后 cookie 可达 /me', (await get('/me', meCookie)).status === 200)

  /* 7. 二次 SSO 登录直达（免绑定） */
  const start3 = await get('/api/auth/sso/casdoor/start')
  const cb3 = (await fetch(start3.headers.get('location'), { redirect: 'manual' })).headers.get('location')
  const direct = await getAbs(cb3)
  check('二次 SSO 直达登录（303 + cookie，无绑定页）', direct.status === 303 && direct.headers.getSetCookie()[0] !== undefined && !(await direct.text()).includes('绑定'))
  check('auth.sso_login 留痕（provider=casdoor）', await waitForAudit((e) => e.action === 'auth.sso_login' && e.result === 'ok' && e.actor?.account === 'member@t' && e.detail?.provider === 'casdoor') !== undefined)

  /* 8. state 伪造 / 缺失 → 400 */
  check('伪造 state 400', (await get('/api/auth/sso/casdoor/callback?code=x&state=forged-state')).status === 400)
  check('缺 state 400', (await get('/api/auth/sso/casdoor/callback?code=x')).status === 400)

  /* 9. 自动开通（JIT）：新身份首次登录直接建号，账号名不含身份原文 */
  mockSub = 'mock-casdoor-sub-auto-1'
  saveSsoConfig(DATA, { casdoor: {
    enabled: true, autoProvision: true, autoRole: 'employee', autoDepartment: '市场部', autoInstance: 'e02',
  } }, key)
  const startAuto = await get('/api/auth/sso/casdoor/start')
  const cbAuto = (await fetch(startAuto.headers.get('location'), { redirect: 'manual' })).headers.get('location')
  const autoRes = await getAbs(cbAuto)
  const accountsAfter = JSON.parse(readFileSync(join(DATA, 'accounts.json'), 'utf8')).accounts
  const provisioned = accountsAfter.find((a) => Array.isArray(a.ssoIds) && a.ssoIds.includes('casdoor:mock-casdoor-sub-auto-1'))
  check('自动开通成功（303 + cookie）', autoRes.status === 303 && autoRes.headers.getSetCookie()[0] !== undefined)
  check('自动开通账号名 = casdoor- + 12 位摘要（不含身份原文）',
    provisioned !== undefined && /^casdoor-[0-9a-f]{12}$/.test(provisioned.account) && !provisioned.account.includes('mock-casdoor-sub-auto-1'))
  check('自动开通沿用管理员配置的角色/部门/实例',
    provisioned?.role === 'employee' && provisioned?.department === '市场部' && provisioned?.instanceId === 'e02')
  const provisionEvent = await waitForAudit((e) => e.action === 'auth.sso_provision' && e.result === 'ok')
  check('auth.sso_provision ok 留痕（角色/实例，不含身份原文）', provisionEvent !== undefined
    && provisionEvent.detail?.provider === 'casdoor' && provisionEvent.detail?.instanceId === 'e02'
    && !JSON.stringify(provisionEvent.detail).includes('mock-casdoor-sub-auto-1'))

  // 二次扫码：同一身份不再重复建号
  const accountsCount = accountsAfter.length
  const startAuto2 = await get('/api/auth/sso/casdoor/start')
  const cbAuto2 = (await fetch(startAuto2.headers.get('location'), { redirect: 'manual' })).headers.get('location')
  const autoRes2 = await getAbs(cbAuto2)
  const accountsFinal = JSON.parse(readFileSync(join(DATA, 'accounts.json'), 'utf8')).accounts
  check('二次扫码不重复建号（幂等）', autoRes2.status === 303 && accountsFinal.length === accountsCount)

  // autoRole 白名单：管理员角色不可被自动开通
  check('autoRole 白名单拒绝 admin（管理员只能人工授予）',
    (() => { try { saveSsoConfig(DATA, { casdoor: { autoRole: 'admin' } }, key); return false } catch { return true } })())

  /* 10. 端点失败降级：token 500 / userinfo 缺 sub → 502 */
  mockTokenFail = true
  const startFail = await get('/api/auth/sso/casdoor/start')
  const cbFail = (await fetch(startFail.headers.get('location'), { redirect: 'manual' })).headers.get('location')
  const failRes = await getAbs(cbFail)
  const failText = await failRes.text()
  check('token 端点失败 → 502 且文案带原因', failRes.status === 502 && failText.includes('Casdoor token 接口失败'))
  mockTokenFail = false

  mockUserinfoNoSub = true
  const startFail2 = await get('/api/auth/sso/casdoor/start')
  const cbFail2 = (await fetch(startFail2.headers.get('location'), { redirect: 'manual' })).headers.get('location')
  const failRes2 = await getAbs(cbFail2)
  check('userinfo 缺 sub/id → 502', failRes2.status === 502 && (await failRes2.text()).includes('未返回 sub/id'))
  mockUserinfoNoSub = false

  /* 11. resolveSsoIdentity 直调 + AbortSignal 超时参数 */
  let capturedSignal = null
  const capturingFetch = (url, init) => {
    if (String(url).includes('/api/login/oauth/access_token')) capturedSignal = init?.signal ?? null
    return fetch(url, init)
  }
  mockSub = MOCK_SUB
  const identityOk = await resolveSsoIdentity('casdoor', 'probe-code', DATA, key, capturingFetch)
  check('resolveSsoIdentity 直调成功', identityOk.ssoId === `casdoor:${MOCK_SUB}`)
  check('身份解析返回展示名', identityOk.name === 'Mock Casdoor 用户')
  check('fetch 携带 AbortSignal 超时参数', capturedSignal instanceof AbortSignal)

  /* 12. 未知 provider 的 start 404（注册表之外） */
  check('未注册的 provider start 404', (await get('/api/auth/sso/nope/start')).status === 404)
} finally {
  gateway.close()
  gateway.closeAllConnections?.()
  mock.close()
  rmSync(DATA, { recursive: true, force: true })
}

console.log(`\n通过 ${passed}，失败 ${failed}`)
process.exit(failed > 0 ? 1 : 0)
