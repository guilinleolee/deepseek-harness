/**
 * 安全与审计 + 配额点数 HTTP 集成验证（参照阶段 4 的受控环境验证方式：临时 data/ +
 * 随机端口起真实网关与 Relay + test/mock-upstream.mjs 受控上游）。
 *
 * 一期覆盖：
 * 1. 登录三路径（fail / success / rate_limited）在真实 HTTP 登录流落正确 JSONL；
 * 2. admin 变更端点审计（额度/安全设置/实例）与审计查询/导出 API；
 * 3. auditor 只读门禁（页面 200、变更 403「审计员为只读角色」且留 deny）；
 * 4. 密码策略落地（弱密码 400 留痕）与 employee 拒入。
 * 二期覆盖（配额点数模型，蓝图六节）：
 * 5. 200 实结正确（预扣与实结差值返还断言）；耗尽 429 点数口径文案 + 审计 detail；
 *    上游失败全额返还（usage.points 不变）；倍率改动下一请求生效；旧制账号仍按
 *    旧 tokens 判据硬停；model.ratio_change / quota.group_ratio_change 审计。
 *
 * 全程不占用 8460/9400；结束关闭全部服务并清理临时目录。
 * 运行：node test/auth-audit-http-verify.mjs
 */
import { spawn } from 'node:child_process'
import { createServer } from 'node:http'
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'

import { auditQuery, initAudit } from '../audit.mjs'
import { createGatewayServer, hashPassword } from '../gateway.mjs'
import { createRelayServer, issueVkey, monthKey } from '../relay.mjs'
import { saveSecurityConfig } from '../security.mjs'

const wait = (ms) => new Promise((r) => setTimeout(r, ms))
const JSON_HEAD = { 'content-type': 'application/json', connection: 'close' }

let passed = 0
let failed = 0
const check = (name, cond) => {
  if (cond === true) { passed += 1; console.log(`  ok  ${name}`) } else { failed += 1; console.error(`FAIL  ${name}`) }
}

const DATA = mkdtempSync(join(tmpdir(), 'lyz-audit-http-'))
const now = new Date().toISOString()
const account = (id, acc, role, pw, extra = {}) => ({
  id, account: acc, displayName: id, role, department: '验证组', instanceId: 'e01',
  tokenEpoch: 0, createdAt: now, passwordHash: hashPassword(pw), ...extra,
})

writeFileSync(join(DATA, 'accounts.json'), `${JSON.stringify({ accounts: [
  account('acc-admin', 'admin@t', 'admin', 'AdminPass1'),
  account('acc-auditor', 'auditor@t', 'auditor', 'AuditPass1'),
  account('acc-member', 'member@t', 'employee', 'MemberPass1', { monthlyPoints: 100000 }),
  account('acc-pts', 'pts@t', 'employee', 'PtsPass12', { monthlyPoints: 150 }),
  account('acc-legacy', 'legacy@t', 'employee', 'LegacyPw1', { monthlyTokens: 50 }),
  account('acc-tiny', 'tiny@t', 'employee', 'TinyPass1', { monthlyPoints: 5000 }),
  account('acc-abort', 'abort@t', 'employee', 'AbortPw12'),
] }, null, 2)}\n`)
initAudit(DATA)
saveSecurityConfig(DATA, { loginMaxFails: 3 }) // 缩小阈值加速锁定路径

const manifest = {
  gatewayHost: 'localhost', portalPort: 0, relayPort: 0, repoRoot: '.',
  instances: [{ id: 'e01', account: 'member@t', uid: 1, port: 1 }],
}
const gateway = createGatewayServer({ manifest, getState: () => ({ instances: {} }), dataDir: DATA })
await new Promise((r) => gateway.listen(0, '127.0.0.1', r))
const base = `http://127.0.0.1:${gateway.address().port}`

const post = async (path, body, cookie) =>
  fetch(`${base}${path}`, { method: 'POST', headers: cookie ? { ...JSON_HEAD, cookie } : JSON_HEAD, body: JSON.stringify(body ?? {}) })
const get = async (path, cookie) =>
  fetch(`${base}${path}`, { headers: cookie ? { cookie, connection: 'close' } : { connection: 'close' } })
const login = async (acc, pw) => {
  const res = await post('/api/auth/login', { account: acc, password: pw })
  return { status: res.status, cookie: res.headers.getSetCookie()[0]?.split(';')[0], body: await res.json().catch(() => ({})) }
}
const waitForAudit = async (actionPrefix, min = 1, extra = {}, timeoutMs = 4000) => {
  const deadline = Date.now() + timeoutMs
  let n = 0
  while (Date.now() < deadline) {
    n = auditQuery({ actionPrefix, limit: 10000, ...extra }).length
    if (n >= min) return n
    await wait(40)
  }
  return n
}
const readUsageEntry = (account) => {
  try {
    return JSON.parse(readFileSync(join(DATA, 'usage.json'), 'utf8')).months[monthKey()]?.[account] ?? {}
  } catch {
    return {}
  }
}
const readUsagePoints = (account) => readUsageEntry(account).points ?? 0
const waitForPoints = async (account, expect, timeoutMs = 5000) => {
  const deadline = Date.now() + timeoutMs
  let p = readUsagePoints(account)
  while (Date.now() < deadline) {
    p = readUsagePoints(account)
    if (Math.abs(p - expect) < 1e-6) return p
    await wait(40)
  }
  return p
}
const waitForTokens = async (account, minTokensIn, timeoutMs = 5000) => {
  const deadline = Date.now() + timeoutMs
  let e = readUsageEntry(account)
  while (Date.now() < deadline) {
    e = readUsageEntry(account)
    if ((e.tokensIn ?? 0) >= minTokensIn) return e
    await wait(40)
  }
  return e
}
/** 轮询等待第一条满足条件的审计事件（多账号同名事件间有落盘竞态，不能只等条数）。 */
const waitForAuditEvent = async (actionPrefix, pred, timeoutMs = 4000) => {
  const deadline = Date.now() + timeoutMs
  while (Date.now() < deadline) {
    const e = auditQuery({ actionPrefix, limit: 100 }).find(pred)
    if (e !== undefined) return e
    await wait(40)
  }
  return undefined
}

try {
  /* ── 1. 登录审计三路径 ────────────────────────────────────────────────── */
  console.log('# 登录审计三路径')
  const badAdmin = await login('admin@t', 'WrongPass9')
  check('错误密码 401', badAdmin.status === 401)
  const admin = await login('admin@t', 'AdminPass1')
  check('admin 正确密码 200 + Cookie', admin.status === 200 && admin.cookie !== undefined)
  const auditor = await login('auditor@t', 'AuditPass1')
  check('auditor 登录 200（新增放行）', auditor.status === 200 && auditor.cookie !== undefined)
  check('auth.login_fail 落盘', await waitForAudit('auth.login_fail') >= 1)
  check('auth.login_success 落盘 ×2', await waitForAudit('auth.login_success', 2) >= 2)
  const failEvent = auditQuery({ actionPrefix: 'auth.login_fail' })[0]
  check('login_fail 事件含 ip 与 reason', typeof failEvent?.actor?.ip === 'string' && failEvent.actor.ip !== '' && failEvent.detail?.reason === 'bad_credentials')

  // 锁定路径：loginMaxFails=3，member@t 连错 3 次后，正确密码也被限流
  for (let i = 0; i < 3; i++) await login('member@t', 'BadPass1')
  const limited = await login('member@t', 'MemberPass1')
  check('达阈值后正确密码也 429', limited.status === 429)
  check('429 中文文案', String(limited.body?.error ?? '').includes('锁定'))
  check('auth.login_rate_limited 落盘', await waitForAudit('auth.login_rate_limited') >= 1)

  /* ── 2. Relay 计费链（点数口径：实结/倍率生效/耗尽/返还/旧制/严格判定/断连）── */
  console.log('# Relay 计费链（点数配额模型）')
  const mock = spawn(process.execPath, [fileURLToPath(new URL('./mock-upstream.mjs', import.meta.url))], { stdio: 'ignore' })
  let relay = null
  // 慢上游：500ms 后返回固定 usage（严格判定与断连验证的时序锚点）。
  const slowServer = createServer((req, res) => {
    req.resume()
    req.on('end', () => {
      setTimeout(() => {
        res.writeHead(200, { 'content-type': 'application/json' })
        res.end(JSON.stringify({ choices: [{ message: { role: 'assistant', content: 'ok' } }], usage: { prompt_tokens: 100, completion_tokens: 20 } }))
      }, 500)
    })
  })
  await new Promise((r) => slowServer.listen(0, '127.0.0.1', r))
  try {
    // 等 mock 上游就绪（9410 可连通）再发首笔请求。
    let mockUp = false
    for (let i = 0; i < 50 && !mockUp; i++) {
      mockUp = await new Promise((resolveProbe) => {
        fetch('http://127.0.0.1:9410/v1/chat/completions', { method: 'POST', headers: JSON_HEAD, body: '{}' })
          .then((res) => { res.arrayBuffer().catch(() => {}); resolveProbe(res.status === 200) })
          .catch(() => resolveProbe(false))
      })
      if (!mockUp) await wait(100)
    }
    check('mock 上游就绪', mockUp)
    // 正常上游 + 坏上游（端口不监听，验证失败返还）+ 慢上游（时序锚点）
    writeFileSync(join(DATA, 'upstreams.json'), `${JSON.stringify({ upstreams: [
      { name: 'mock', baseURL: 'http://127.0.0.1:9410', models: ['test-model'], apiKey: 'sk-verify', revoked: false, apiFormat: 'openai', createdAt: now },
      { name: 'broken', baseURL: 'http://127.0.0.1:9422', models: ['fail-model'], apiKey: 'sk-verify', revoked: false, apiFormat: 'openai', createdAt: now },
      { name: 'slow', baseURL: `http://127.0.0.1:${slowServer.address().port}`, models: ['slow-model'], apiKey: 'sk-verify', revoked: false, apiFormat: 'openai', createdAt: now },
    ] }, null, 2)}\n`)
    const memberToken = issueVkey(DATA, { account: 'member@t', instanceId: 'e01', models: ['test-model'] }).token
    const adminRelayToken = issueVkey(DATA, { account: 'admin@t', instanceId: 'e01', models: ['fail-model'] }).token
    const ptsToken = issueVkey(DATA, { account: 'pts@t', instanceId: 'e01', models: ['test-model'] }).token
    const legacyToken = issueVkey(DATA, { account: 'legacy@t', instanceId: 'e01', models: ['test-model'] }).token
    relay = createRelayServer({ dataDir: DATA })
    await new Promise((r) => relay.listen(0, '127.0.0.1', r))
    const relayPort = relay.address().port
    const relayPost = (token, body, signal) => fetch(`http://127.0.0.1:${relayPort}/v1/chat/completions`, {
      method: 'POST', headers: { ...JSON_HEAD, authorization: `Bearer ${token}` }, body: JSON.stringify(body), signal,
    })
    const chat = (model, maxTokens) => ({ model, messages: [{ role: 'user', content: 'hi' }], max_tokens: maxTokens })

    // 2a. 200 实结：预扣（估输入 1 + 估输出 500×3 = 1501 点）入账后，按实际 usage 多退少补
    const p0 = readUsagePoints('member@t')
    const ok1 = await relayPost(memberToken, chat('test-model', 500))
    check('relay 请求 200', ok1.status === 200)
    await ok1.arrayBuffer()
    const p1 = await waitForPoints('member@t', p0 + 160)
    check('实结点数 = 实际 usage（100 + 20×3 = 160，预扣 1501 已按差值返还）', Math.abs(p1 - (p0 + 160)) < 1e-6)
    const mEntry = await waitForTokens('member@t', 100)
    check('tokens 进/出照旧累计（100/20，requests=1）', mEntry.tokensIn === 100 && mEntry.tokensOut === 20 && mEntry.requests === 1)

    // 2b. 倍率改动下一请求生效（1→2）：实结 = 100×2 + 20×2×3 = 400 点
    const ratioRes = await post('/console/api/model/ratio', { model: 'test-model', ratio: 2, completionRatio: 3 }, admin.cookie)
    check('模型倍率改动 200', ratioRes.status === 200)
    check('model.ratio_change 落盘含旧值→新值', await waitForAudit('model.ratio_change') >= 1
      && (() => { const e = auditQuery({ actionPrefix: 'model.ratio_change' })[0]; return e?.detail?.old?.ratio === 1 && e?.detail?.new?.ratio === 2 })())
    const p2 = readUsagePoints('member@t')
    const ok2 = await relayPost(memberToken, chat('test-model', 500))
    check('倍率改动后请求 200', ok2.status === 200)
    await ok2.arrayBuffer()
    const p3 = await waitForPoints('member@t', p2 + 320)
    check('倍率改动下一请求生效（实结 = 100×2 + 20×2×3 = 320 点）', Math.abs(p3 - (p2 + 320)) < 1e-6)

    // 2c. pts@t（monthlyPoints=150）耗尽 → 429 点数口径
    const pts1 = await relayPost(ptsToken, chat('test-model', 10))
    check('点数账号首请求 200（账面未到线）', pts1.status === 200)
    await pts1.arrayBuffer()
    await waitForPoints('pts@t', 320) // 等 2 倍率实结（320 点）入账
    const pts2 = await relayPost(ptsToken, chat('test-model', 10))
    check('点数额度耗尽 429', pts2.status === 429)
    const ptsBody = await pts2.json().catch(() => ({}))
    check('429 点数口径中文文案', String(ptsBody?.error?.message ?? '').includes('点数'))
    const qe = await waitForAuditEvent('quota.exceeded', (e) => e.target === 'pts@t')
    check('quota.exceeded detail 点数口径（usedPoints/quotaPoints）', qe?.detail?.usedPoints === 320 && qe?.detail?.quotaPoints === 150)

    // 2d. 上游失败全额返还预扣（broken 上游；admin 无额度）
    const pa0 = readUsagePoints('admin@t')
    const bad = await relayPost(adminRelayToken, chat('fail-model', 100))
    check('坏上游 502', bad.status === 502)
    await bad.arrayBuffer().catch(() => {})
    const pa1 = await waitForPoints('admin@t', pa0)
    check('上游失败后 usage.points 不变（预扣全额返还）', Math.abs(pa1 - pa0) < 1e-6)

    // 2e. legacy@t（只有 monthlyTokens=50）仍按旧 tokens 判据硬停
    const lg1 = await relayPost(legacyToken, chat('test-model', 10))
    check('旧制账号首请求 200', lg1.status === 200)
    await lg1.arrayBuffer()
    const lgEntry = await waitForTokens('legacy@t', 100)
    check('旧制账号 tokens 实结 120', (lgEntry.tokensIn ?? 0) + (lgEntry.tokensOut ?? 0) === 120)
    const lg2 = await relayPost(legacyToken, chat('test-model', 10))
    check('旧制 429 硬停', lg2.status === 429)
    const lgBody = await lg2.json().catch(() => ({}))
    check('旧制 429 保持 tokens 文案', String(lgBody?.error?.message ?? '').includes('Token 额度已用完'))
    const lqe = await waitForAuditEvent('quota.exceeded', (e) => e.target === 'legacy@t')
    check('旧制 quota.exceeded detail 保持 tokens 口径 + 旧制标记', lqe?.detail?.used === 120 && lqe?.detail?.quota === 50 && lqe?.detail?.legacyTokens === true)

    // 2f. 预扣计入判定：A（慢上游，未实结）的预扣占账（9001 点）后，B 立即被拒
    const tinyToken = issueVkey(DATA, { account: 'tiny@t', instanceId: 'e01', models: ['slow-model'] }).token
    const slowChat = { model: 'slow-model', messages: [{ role: 'user', content: 'hi' }], max_tokens: 3000 }
    const aSlow = relayPost(tinyToken, slowChat) // 不 await：保持 in-flight（预扣未实结）
    await wait(150) // 确保 A 已被 relay 预扣（慢上游 500ms 未返回）
    const bDenied = await relayPost(tinyToken, slowChat)
    check('预扣占账期间并发请求被拒（usedPoints+未实结预扣 ≥ 额度）', bDenied.status === 429)
    const bBody = await bDenied.json().catch(() => ({}))
    check('严格判定 429 点数文案', String(bBody?.error?.message ?? '').includes('点数'))
    const bqe = await waitForAuditEvent('quota.exceeded', (e) => e.target === 'tiny@t')
    check('严格判定 detail 含未实结预扣（9001/5000）', bqe?.detail?.usedPoints === 9001 && bqe?.detail?.quotaPoints === 5000)
    const aRes = await aSlow
    check('占账的 A 请求本身不受影响 200', aRes.status === 200)
    await aRes.arrayBuffer()
    const tinySettled = await waitForPoints('tiny@t', 160)
    check('A 实结 160 点入账（预扣 9001 只占判定额度，不落账面）', Math.abs(tinySettled - 160) < 1e-6)

    // 2g. 客户端断连：全额返还预扣、requests 计 1、tokens 不计、relay.log 记 aborted
    const abortToken = issueVkey(DATA, { account: 'abort@t', instanceId: 'e01', models: ['slow-model'] }).token
    const ac = new AbortController()
    const abortedReq = relayPost(abortToken, slowChat, ac.signal)
    await wait(120) // relay 已预扣、尚在等慢上游
    ac.abort()
    await abortedReq.catch(() => { /* 客户端主动断开 */ })
    await wait(700) // 慢上游响应到达时连接已毁，不应产生任何账目
    const abEntry = readUsageEntry('abort@t')
    check('断连后 points 不变（预扣全额返还）', (abEntry.points ?? 0) === 0)
    check('断连后 requests 计 1、tokens 不计（保持 0）', abEntry.requests === 1 && (abEntry.tokensIn ?? 0) === 0 && (abEntry.tokensOut ?? 0) === 0)
    let abortedLog = false
    try {
      abortedLog = readFileSync(join(DATA, 'logs', 'relay.log'), 'utf8').includes('"aborted":true')
    } catch { /* 尚无日志 */ }
    check('relay.log 记 aborted 元数据', abortedLog)

    relay.close()
    relay.closeAllConnections?.()
    slowServer.close()
    slowServer.closeAllConnections?.()
  } finally {
    mock.kill()
  }

  /* ── 3. admin 页面、变更端点审计与查询/导出 ───────────────────────────── */
  console.log('# admin 页面与变更审计')
  const overview = await get('/console', admin.cookie)
  const overviewText = await overview.text()
  check('admin 总览 200', overview.status === 200)
  check('总览含告警卡（额度将尽成员/失败登录/审计摘要）', overviewText.includes('额度将尽成员') && overviewText.includes('24 小时失败登录') && overviewText.includes('最近审计事件'))
  const auditPageRes = await get('/console/audit', admin.cookie)
  check('admin 安全与审计页 200', auditPageRes.status === 200)

  const quotaRes = await post('/console/api/member/quota', { account: 'member@t', points: 5000 }, admin.cookie)
  check('admin 改点数额度 200', quotaRes.status === 200)
  check('member.quota_change 落盘', await waitForAudit('member.quota_change', 1, { result: 'ok' }) >= 1)
  const qEvent = auditQuery({ actionPrefix: 'member.quota_change', result: 'ok' })[0]
  check('quota_change detail 含旧值→新值（点数口径）', qEvent?.detail?.from === 100000 && qEvent?.detail?.to === 5000)

  const grpRes = await post('/console/api/department/group-ratio', { department: '验证组', ratio: 1.2 }, admin.cookie)
  check('admin 改分组倍率 200', grpRes.status === 200)
  check('quota.group_ratio_change 落盘含旧值→新值', await waitForAudit('quota.group_ratio_change') >= 1
    && (() => { const e = auditQuery({ actionPrefix: 'quota.group_ratio_change' })[0]; return e?.detail?.old?.groupRatio === 1 && e?.detail?.new?.groupRatio === 1.2 })())
  const rolesPageRes = await get('/console/roles', admin.cookie)
  check('admin 部门与角色页 200', rolesPageRes.status === 200)

  // 原型链污染键：写入侧拒绝 + 审计 fail 留痕 + 配置文件零污染
  const protoRatio = await post('/console/api/model/ratio', { model: '__proto__', ratio: 2, completionRatio: 3 }, admin.cookie)
  check('__proto__ 模型键改倍率 400', protoRatio.status === 400)
  check('model.ratio_change 危险键留痕 fail', await waitForAudit('model.ratio_change', 1, { result: 'fail' }) >= 1)
  check('__proto__ 部门键改分组倍率 400', (await post('/console/api/department/group-ratio', { department: '__proto__', ratio: 2 }, admin.cookie)).status === 400)
  const protoModel = await post('/console/api/model/add', { upstream: 'mock', model: '__proto__' }, admin.cookie)
  check('__proto__ 模型 add 400', protoModel.status === 400)
  const ratiosOnDisk = JSON.parse(readFileSync(join(DATA, 'ratios.json'), 'utf8'))
  check('ratios.json 无危险键且合法配置完好', !Object.hasOwn(ratiosOnDisk.models, '__proto__') && !Object.hasOwn(ratiosOnDisk.groups, '__proto__') && ratiosOnDisk.models['test-model']?.ratio === 2)

  // esc 引号/尖括号转义：审计页查询参数反射不构成 XSS
  const xssPayload = '"><script>alert(1)</script>'
  const xssRes = await get(`/console/audit?actor=${encodeURIComponent(xssPayload)}`, admin.cookie)
  const xssText = await xssRes.text()
  check('审计页反射参数被转义（&quot;/&lt;script&gt;）', xssRes.status === 200 && xssText.includes('&quot;&gt;&lt;script&gt;') && !xssText.includes('<script>alert'))

  const secRes = await post('/console/api/security/config', { lockoutMinutes: 16 }, admin.cookie)
  check('admin 改安全设置 200', secRes.status === 200)
  check('security.config_change 落盘', await waitForAudit('security.config_change') >= 1)
  const sEvent = auditQuery({ actionPrefix: 'security.config_change' })[0]
  check('config_change 旧值→新值', sEvent?.detail?.old?.lockoutMinutes === 15 && sEvent?.detail?.new?.lockoutMinutes === 16)

  const instRes = await post('/console/api/instance/start', { id: 'e01' }, admin.cookie)
  check('admin 实例启动指令 200', instRes.status === 200)
  check('instance.start 落盘', await waitForAudit('instance.start') >= 1)

  const auditApi = await get('/console/api/audit?action=auth&result=fail', admin.cookie)
  const auditApiBody = await auditApi.json()
  check('审计查询 API 200 且过滤生效', auditApi.status === 200 && auditApiBody.events.length >= 1 && auditApiBody.events.every((e) => e.action.startsWith('auth') && e.result === 'fail'))
  const exportRes = await get('/console/api/audit/export?action=auth', admin.cookie)
  const exportText = await exportRes.text()
  check('审计导出 200 ndjson + 附件头', exportRes.status === 200 && String(exportRes.headers.get('content-type')).includes('x-ndjson') && String(exportRes.headers.get('content-disposition')).includes('attachment'))
  check('导出内容逐行 JSON 且只含 auth 前缀', exportText.trim().length > 0 && exportText.trimEnd().split('\n').every((l) => JSON.parse(l).action.startsWith('auth')))
  check('audit.export 落盘', await waitForAudit('audit.export') >= 1)

  /* ── 4. auditor 只读门禁 ─────────────────────────────────────────────── */
  console.log('# auditor 只读门禁')
  for (const page of ['/console', '/console/members', '/console/roles', '/console/models', '/console/instances', '/console/plugins', '/console/audit']) {
    const res = await get(page, auditor.cookie)
    check(`auditor GET ${page} 200`, res.status === 200)
  }
  check('auditor 投放任务查询 200', (await get('/console/api/plugin/jobs', auditor.cookie)).status === 200)
  check('auditor 审计查询 200', (await get('/console/api/audit', auditor.cookie)).status === 200)
  check('auditor 审计导出 200', (await get('/console/api/audit/export', auditor.cookie)).status === 200)
  const aQuota = await post('/console/api/member/quota', { account: 'member@t', tokens: 1 }, auditor.cookie)
  check('auditor 改额度 403 + 只读文案', aQuota.status === 403 && (await aQuota.json()).error === '审计员为只读角色')
  check('auditor 403 留痕 deny', await waitForAudit('member.quota_change', 1, { result: 'deny' }) >= 1)
  check('auditor 改安全设置 403', (await post('/console/api/security/config', { lockoutMinutes: 20 }, auditor.cookie)).status === 403)
  check('auditor 建号 403', (await post('/console/api/member/create', { account: 'x@t', instance: 'e01' }, auditor.cookie)).status === 403)
  check('auditor 投放插件 403', (await post('/console/api/plugin/job', { type: 'push', spec: 'x', ids: ['e01'] }, auditor.cookie)).status === 403)
  check('auditor 改模型倍率 403', (await post('/console/api/model/ratio', { model: 'test-model', ratio: 9 }, auditor.cookie)).status === 403)
  check('auditor 改分组倍率 403', (await post('/console/api/department/group-ratio', { department: '验证组', ratio: 9 }, auditor.cookie)).status === 403)

  /* ── 5. 密码策略落地与 employee 拒入 ─────────────────────────────────── */
  console.log('# 密码策略与 employee 拒入')
  const weak = await post('/console/api/member/create', { account: 'weak@t', instance: 'e01', password: 'weak' }, admin.cookie)
  check('弱密码建号 400 + 中文文案', weak.status === 400 && String((await weak.json()).error ?? '').includes('密码'))
  check('弱密码拒绝留痕 fail', await waitForAudit('member.create', 1, { result: 'fail' }) >= 1)
  const badAcc = await post('/console/api/member/create', { account: 'bad name!', instance: 'e01', password: 'GoodPass1' }, admin.cookie)
  check('非法账号名建号 400 + 中文文案', badAcc.status === 400 && String((await badAcc.json()).error ?? '').includes('账号格式非法'))
  const badAccEvent = await waitForAuditEvent('member.create', (e) => e.result === 'fail' && String(e.detail?.error ?? '').includes('账号格式非法'))
  check('非法账号名留痕 fail（白名单校验路径）', badAccEvent !== undefined)
  const empCreate = await post('/console/api/member/create', { account: 'emp@t', instance: 'e01', role: 'employee', password: 'EmpPass123', displayName: '员工' }, admin.cookie)
  check('合规密码建号 200', empCreate.status === 200)
  check('member.create 落盘 ok', await waitForAudit('member.create', 1, { result: 'ok' }) >= 1)
  const emp = await login('emp@t', 'EmpPass123')
  check('新建员工登录 200', emp.status === 200)
  check('employee 管理台拒入 403', (await get('/console', emp.cookie)).status === 403)
} finally {
  gateway.close()
  gateway.closeAllConnections?.()
  rmSync(DATA, { recursive: true, force: true })
}

console.log(`\n通过 ${passed}，失败 ${failed}`)
process.exit(failed > 0 ? 1 : 0)
