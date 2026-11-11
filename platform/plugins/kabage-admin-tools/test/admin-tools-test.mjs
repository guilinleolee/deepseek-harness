/**
 * kabage-admin-tools 单元测试（零测试框架，node 直接运行）。
 *
 * 起本地 mock 平台服务器（node:http，假 console API + 鉴权头校验），挂载
 * 插件并捕获注册的 9 个工具，断言：请求路径/方法/鉴权头、响应到工具结果
 * 的映射、错误分层与稳定原因码、列表过滤/排序/截断、audit 截断判定、5xx
 * 重试、超时/取消、非回环明文 HTTP 拦截、响应体闸门、vkey 回传与卡片脱敏。
 * 不触外网（mock 仅 127.0.0.1 随机端口；"非回环"用例用 0.0.0.0 走本机回环
 * 栈，不产生外网流量）、不依赖真平台。
 *
 * 运行：node platform/plugins/kabage-admin-tools/test/admin-tools-test.mjs
 */
import { createServer } from 'node:http'

import { apply, name as pluginName } from '../index.mjs'

let passed = 0
let failed = 0
const check = (label, cond) => {
  if (cond === true) { passed += 1; console.log(`  ok  ${label}`) } else { failed += 1; console.error(`FAIL  ${label}`) }
}

/* ── mock 平台服务器 ─────────────────────────────────────────────────────── */
const ADMIN_TOKEN = 'kbsvc-admin-token-test'
const READONLY_TOKEN = 'kbsvc-readonly-token-test'
const seen = [] // {method, path, authorization, body}
const members = Array.from({ length: 60 }, (_, i) => ({
  account: `u${String(i).padStart(2, '0')}@x`,
  displayName: `成员${i}`,
  department: i % 3 === 0 ? '设计部' : (i % 3 === 1 ? '研发部' : '市场部'),
  role: i % 5 === 0 ? 'auditor' : 'employee',
  instanceId: i % 2 === 0 ? 'e02' : 'e03',
  disabled: i % 7 === 0,
  monthlyPoints: 1000, pointsUsed: i * 10,
  tokensIn: 0, tokensOut: 0, requests: 0,
}))

const auditEvent = (i) => ({
  ts: '2026-09-25T10:00:00.000Z', actor: { account: 'svc:e01-admin', role: 'admin' },
  action: 'member.create', target: `u${String(i).padStart(2, '0')}@x`, result: 'ok', detail: null,
})

const mock = createServer((req, res) => {
  let raw = ''
  req.on('data', (c) => { raw += c })
  req.on('end', () => {
    const auth = req.headers.authorization ?? ''
    seen.push({ method: req.method, path: req.url, authorization: auth, body: raw === '' ? undefined : JSON.parse(raw) })
    const json = (status, body) => { res.writeHead(status, { 'content-type': 'application/json' }); res.end(JSON.stringify(body)) }
    if (auth !== `Bearer ${ADMIN_TOKEN}` && auth !== `Bearer ${READONLY_TOKEN}`) return json(401, { error: 'invalid token' })
    if (req.method === 'POST' && auth === `Bearer ${READONLY_TOKEN}`) return json(403, { error: 'readonly' })
    const url = new URL(req.url, 'http://mock')
    if (req.method === 'GET' && url.pathname === '/console/api/member/list') {
      return json(200, { month: '2026-09', members })
    }
    if (req.method === 'GET' && url.pathname === '/console/api/member/usage') {
      const account = url.searchParams.get('account')
      if (account === 'ghost@x') return json(404, { error: `账号不存在: ${account}` })
      if (account === 'rate@x') return json(429, { error: 'too many requests' })
      if (account === 'boom@x') return json(500, { error: 'internal error' })
      if (account === 'echo@x') return json(400, { error: `invalid token ${ADMIN_TOKEN}` })
      if (account === 'huge@x') return json(200, { account, month: '2026-09', blob: 'x'.repeat(4096) })
      if (account !== 'u00@x') return json(404, { error: `账号不存在: ${account}` })
      return json(200, { account, month: '2026-09', points: 320, monthlyPoints: 1000, remainingPoints: 680, tokensIn: 50, tokensOut: 10, tokensUsed: 60, monthlyTokens: null, requests: 7, legacy: false, unlimited: false })
    }
    if (req.method === 'GET' && url.pathname === '/console/api/audit') {
      const action = url.searchParams.get('action')
      const limit = Number(url.searchParams.get('limit') ?? '20')
      // 平台只按 limit 截断、不返回总数：mock 同样按请求 limit 截断。
      if (action === 'bulk') return json(200, { events: Array.from({ length: 51 }, (_, i) => auditEvent(i)).slice(0, limit) })
      if (action === 'exact') return json(200, { events: Array.from({ length: 50 }, (_, i) => auditEvent(i)).slice(0, limit) })
      return json(200, { events: [auditEvent(99)] })
    }
    if (req.method === 'POST' && url.pathname === '/console/api/member/create') {
      const body = JSON.parse(raw)
      // 与平台一致：建号时签发虚拟钥匙，明文只在此响应出现一次。
      return json(200, { ok: true, account: body.account, instance: body.instance, password: 'Gen-Pass12', vkey: 'vk-test-abcdef' })
    }
    if (req.method === 'POST' && url.pathname === '/console/api/member/update') {
      const body = JSON.parse(raw)
      return json(200, { ok: true, role: body.role ?? 'employee', department: body.department ?? '未分配', displayName: body.displayName ?? null })
    }
    if (req.method === 'POST' && url.pathname === '/console/api/member/quota') {
      const body = JSON.parse(raw)
      return json(200, { ok: true, quota: body.points === null ? '不限' : body.points, unit: 'points' })
    }
    if (req.method === 'POST' && url.pathname === '/console/api/member/2fa/reset') {
      return json(200, { ok: true, account: JSON.parse(raw).account })
    }
    if (req.method === 'POST' && url.pathname === '/console/api/member/reset-password') {
      return json(200, { ok: true, password: 'Reset-Pw34' })
    }
    if (req.method === 'POST' && (url.pathname === '/console/api/member/disable' || url.pathname === '/console/api/member/enable')) {
      return json(200, { ok: true })
    }
    return json(404, { error: 'unknown' })
  })
})
await new Promise((r) => mock.listen(0, '127.0.0.1', r))
const baseUrl = `http://127.0.0.1:${mock.address().port}`

/* ── 挂载插件并捕获注册 ──────────────────────────────────────────────────── */
const registered = new Map()
const ctx = { tools: { register(definition) { registered.set(definition.name, definition); return () => {} } } }
apply(ctx, { baseUrl, token: ADMIN_TOKEN, defaultInstance: 'e02' })

const call = async (toolName, args) => {
  const tool = registered.get(toolName)
  if (tool === undefined) throw new Error(`工具未注册: ${toolName}`)
  return tool.execute(args, { signal: AbortSignal.timeout(5000) })
}
const callFail = async (toolName, args) => {
  try { await call(toolName, args); return null } catch (error) { return String(error?.message ?? error) }
}

/** 挂载一个独立插件实例（不同 config），返回它的工具表。 */
const mount = (prefix, cfg) => {
  const table = new Map()
  const instance = { tools: { register(definition) { table.set(definition.name, definition); return () => {} } } }
  apply(instance, cfg)
  return { table, prefix }
}
const runTool = async (table, toolName, args, exec) => {
  const tool = table.get(toolName)
  if (tool === undefined) throw new Error(`工具未注册: ${toolName}`)
  return tool.execute(args, exec ?? { signal: AbortSignal.timeout(5000) })
}
const runFail = async (table, toolName, args, exec) => {
  try { await runTool(table, toolName, args, exec); return null } catch (error) { return String(error?.message ?? error) }
}

/* ── 注册形态 ────────────────────────────────────────────────────────────── */
console.log('# 注册形态')
check('插件导出名', pluginName === 'kabage-admin-tools')
check('注册 9 个工具', registered.size === 9)
for (const toolName of ['user_list', 'user_quota_query', 'audit_query', 'user_create', 'user_update', 'user_reset_password', 'user_set_disabled', 'user_set_quota', 'user_reset_2fa']) {
  const tool = registered.get(toolName)
  check(`${toolName}: name/description/parameters 齐全`, tool?.name === toolName && typeof tool?.description === 'string' && tool?.parameters?.type === 'object')
  check(`${toolName}: output.schema + render`, tool?.output !== undefined && typeof tool?.output?.render === 'function' && typeof tool?.output?.schema === 'object')
  check(`${toolName}: presentCall 声明 generic 卡片`, tool?.presentCall !== undefined && JSON.stringify(tool.presentCall({})).includes('"card":"generic"'))
}

/* ── 只读三工具（路径/方法/鉴权头/映射/截断）────────────────────────────── */
console.log('# 只读工具')
const listed = await call('user_list', {})
check('user_list 请求携带 Bearer 鉴权头', seen.at(-1).authorization === `Bearer ${ADMIN_TOKEN}` && seen.at(-1).path === '/console/api/member/list')
check('user_list 截断到 50 条并标注', listed.total === 60 && listed.shown === 50 && listed.truncated === true)
const quota = await call('user_quota_query', { account: 'u00@x' })
check('user_quota_query 映射点数/余量', quota.points === 320 && quota.remainingPoints === 680)
const audited = await call('audit_query', { action: 'member', limit: 99 })
check('audit_query 探测上限 51（多取一条判定截断）', seen.at(-1).path.includes('limit=51'))
check('audit_query 映射事件', audited.count === 1 && audited.events[0].action === 'member.create')
check('audit_query 请求参数正确（action/limit=51，无 account）', seen.at(-1).path.includes('action=member') && seen.at(-1).path.includes('limit=51') && !seen.at(-1).path.includes('account='))

/* ── 变更六工具（映射与缺省值）──────────────────────────────────────────── */
console.log('# 变更工具')
const created = await call('user_create', { account: 'new@x' })
check('user_create 缺省实例/角色/平台生成密码', created.password === 'Gen-Pass12' && created.instance === 'e02' && typeof created.notice === 'string' && created.notice.includes('尽快修改'))
check('user_create 请求体（不含未提供字段）', seen.at(-1).body.account === 'new@x' && seen.at(-1).body.role === 'employee' && seen.at(-1).body.password === undefined)
const updated = await call('user_update', { account: 'u00@x', role: 'auditor' })
check('user_update 映射平台响应', updated.ok === true && updated.role === 'auditor')
const reset = await call('user_reset_password', { account: 'u00@x' })
check('user_reset_password 返回一次性密码 + 提示', reset.password === 'Reset-Pw34' && reset.notice.includes('会话记录'))
check('user_reset_password 请求路径', seen.at(-1).path === '/console/api/member/reset-password')
check('user_set_disabled(true) → disable 端点', (await call('user_set_disabled', { account: 'u00@x', disabled: true }))?.ok === true && seen.at(-1).path === '/console/api/member/disable')
check('user_set_disabled(false) → enable 端点', (await call('user_set_disabled', { account: 'u00@x', disabled: false }))?.ok === true && seen.at(-1).path === '/console/api/member/enable')

/* ── 错误转译 ────────────────────────────────────────────────────────────── */
console.log('# 错误转译')
check('缺参数：中文必填提示', String(await callFail('user_quota_query', {})).includes('参数 account 必填'))
const notFound = String(await callFail('user_quota_query', { account: 'ghost@x' }))
check('平台 404 → 账号不存在语义（not_found）', notFound.includes('账号不存在') && notFound.includes('not_found'))
const rateLimited = String(await callFail('user_quota_query', { account: 'rate@x' }))
check('平台 429 → 限流（rate_limited）', rateLimited.includes('限流') && rateLimited.includes('rate_limited'))
const serverError = String(await callFail('user_quota_query', { account: 'boom@x' }))
check('平台 5xx → 平台故障（platform_error，可重试语义）', serverError.includes('平台故障') && serverError.includes('platform_error'))
const rejected = String(await callFail('user_quota_query', { account: 'echo@x' }))
check('其他 4xx → rejected 且保留平台中文文案', rejected.includes('平台拒绝该操作') && rejected.includes('rejected'))
check('错误文案不泄露服务令牌', !rejected.includes(ADMIN_TOKEN))
// token 缺失的独立实例：config.token 与 env 均为空。
const previousTokenEnv = process.env.KABAGE_SERVICE_TOKEN
delete process.env.KABAGE_SERVICE_TOKEN
const noToken = mount('nt', { baseUrl })
const missing = await runFail(noToken.table, 'user_list', {})
if (previousTokenEnv !== undefined) process.env.KABAGE_SERVICE_TOKEN = previousTokenEnv
check('token 缺失：中文配置错误（token_missing）', missing !== null && missing.includes('未配置服务令牌') && missing.includes('token_missing'))

// readonly 令牌：变更工具调用 → 平台 403 → forbidden 转译（不探测、始终注册）。
const readonly = mount('ro', { baseUrl, token: READONLY_TOKEN, defaultInstance: 'e02' })
const readonlyDenied = await runFail(readonly.table, 'user_create', { account: 'ro@x' })
check('readonly 令牌调变更工具 → 403 转译（forbidden）', readonlyDenied !== null && readonlyDenied.includes('权限不足') && readonlyDenied.includes('forbidden'))

// 401：坏 token。
const bad = mount('bad', { baseUrl, token: 'kbsvc-wrong', defaultInstance: 'e02' })
const badResult = await runFail(bad.table, 'user_list', {})
check('坏 token → 401 转译（auth_failed）', badResult !== null && badResult.includes('认证失败') && badResult.includes('auth_failed'))

// 网络错：错误端口。
const unreachable = mount('un', { baseUrl: 'http://127.0.0.1:1', token: ADMIN_TOKEN })
const unreachableMsg = await runFail(unreachable.table, 'user_list', {})
check('网络不可达 → unreachable 转译', unreachableMsg !== null && unreachableMsg.includes('无法连接平台管理接口') && unreachableMsg.includes('unreachable'))

/* ── vkey 回传 + 卡片脱敏 ─────────────────────────────────────────────────── */
console.log('# 一次性凭据与脱敏')
check('user_create 回传虚拟钥匙 vkey（不再丢失）', created.vkey === 'vk-test-abcdef')
check('user_create 结果标注敏感字段', Array.isArray(created.sensitiveFields) && created.sensitiveFields.includes('password') && created.sensitiveFields.includes('vkey'))
check('user_create 结果含一次性凭据警示语', created.notice.includes('vkey') && created.notice.includes('一次性') && created.notice.includes('无法找回'))
const card = registered.get('user_create').presentCall({ account: 'a@x', password: 'pw-secret', vkey: 'vk-secret', nested: { token: 'tk-secret' } })
const cardText = String(card.content)
check('UI 卡片对 password/vkey/token 脱敏', !cardText.includes('pw-secret') && !cardText.includes('vk-secret') && !cardText.includes('tk-secret') && cardText.includes('已脱敏'))
check('UI 卡片保留非敏感字段', cardText.includes('a@x') && card.card === 'generic')

/* ── 角色取值：非法显式报错，不静默降级 ─────────────────────────────────── */
console.log('# 角色与参数校验')
const badRoleUpdate = String(await callFail('user_update', { account: 'u00@x', role: 'admin' }))
check('user_update 非法 role 显式报错（invalid_role）', badRoleUpdate.includes('invalid_role') && badRoleUpdate.includes('role'))
const badRoleCreate = String(await callFail('user_create', { account: 'x@x', role: 'admin' }))
check('user_create 非法 role 显式报错（invalid_role）', badRoleCreate.includes('invalid_role'))
check('user_update 无字段时中文报错', String(await callFail('user_update', { account: 'u00@x' })).includes('至少提供'))

/* ── 新能力：displayName / 额度 / 2FA ─────────────────────────────────────── */
console.log('# 新能力')
await call('user_create', { account: 'dn@x', displayName: '张三' })
check('user_create 透传 displayName', seen.at(-1).path === '/console/api/member/create' && seen.at(-1).body.displayName === '张三')
await call('user_update', { account: 'u00@x', displayName: '李四' })
check('user_update 透传 displayName', seen.at(-1).path === '/console/api/member/update' && seen.at(-1).body.displayName === '李四')
await call('user_create', { account: 'dep@x', department: '研发部' })
check('user_create 建号后补写部门（平台建号端点忽略 department）', seen.at(-2).path === '/console/api/member/create' && seen.at(-2).body.department === '研发部' && seen.at(-1).path === '/console/api/member/update' && seen.at(-1).body.department === '研发部')
const quotaSet = await call('user_set_quota', { account: 'u00@x', points: 1000 })
check('user_set_quota 请求体与结果映射', seen.at(-1).path === '/console/api/member/quota' && seen.at(-1).body.points === 1000 && quotaSet.quota === 1000 && quotaSet.unlimited === false)
const quotaUnlimited = await call('user_set_quota', { account: 'u00@x' })
check('user_set_quota 留空 = 不限', seen.at(-1).body.points === null && quotaUnlimited.unlimited === true && quotaUnlimited.quota === '不限')
check('user_set_quota 非法点数中文报错', String(await callFail('user_set_quota', { account: 'u00@x', points: -5 })).includes('invalid_points'))
const twofa = await call('user_reset_2fa', { account: 'u00@x' })
check('user_reset_2fa 命中 2fa 重置端点', seen.at(-1).path === '/console/api/member/2fa/reset' && twofa.ok === true && twofa.notice.includes('两步验证'))
check('user_reset_2fa readonly 令牌 → forbidden', String(await runFail(readonly.table, 'user_reset_2fa', { account: 'u00@x' })).includes('forbidden'))
check('user_set_quota readonly 令牌 → forbidden', String(await runFail(readonly.table, 'user_set_quota', { account: 'u00@x', points: 10 })).includes('forbidden'))

/* ── user_list 过滤与排序 ────────────────────────────────────────────────── */
console.log('# 列表过滤与排序')
const byDepartment = await call('user_list', { department: '研发部' })
check('user_list 按部门过滤', byDepartment.matched === byDepartment.members.length && byDepartment.members.every((m) => m.department === '研发部') && byDepartment.matched < byDepartment.total)
const byRole = await call('user_list', { role: 'auditor' })
check('user_list 按角色过滤', byRole.members.every((m) => m.role === 'auditor') && byRole.matched === byRole.members.length)
const byDisabled = await call('user_list', { disabled: true })
check('user_list 按禁用状态过滤', byDisabled.members.every((m) => m.disabled === true) && byDisabled.matched === byDisabled.members.length)
const byInstance = await call('user_list', { instance: 'e03' })
check('user_list 按实例过滤', byInstance.members.every((m) => m.instanceId === 'e03') && byInstance.matched === byInstance.members.length)
const byKeyword = await call('user_list', { q: 'u05' })
check('user_list 关键词过滤（账号/显示名/部门）', byKeyword.matched === 1 && byKeyword.members[0].account === 'u05@x')
const sortedDesc = await call('user_list', { sort: 'pointsUsed', order: 'desc', limit: 5 })
check('user_list 排序 + limit', sortedDesc.shown === 5 && sortedDesc.members[0].pointsUsed === 590 && sortedDesc.truncated === true)
check('user_list 非法 sort 中文报错', String(await callFail('user_list', { sort: 'password' })).includes('invalid_parameter'))
check('user_list 非法 role 过滤中文报错', String(await callFail('user_list', { role: 'root' })).includes('invalid_role'))
const limitClamped = await call('user_list', { limit: 999 })
check('user_list limit 钳制到 50', limitClamped.shown === 50 && limitClamped.truncated === true)

/* ── audit 截断判定（修误报）────────────────────────────────────────────── */
console.log('# 审计截断判定')
const bulkAudit = await call('audit_query', { action: 'bulk', limit: 50 })
check('audit_query 超过上限时 truncated=true', bulkAudit.count === 50 && bulkAudit.truncated === true)
const exactAudit = await call('audit_query', { action: 'exact', limit: 50 })
check('audit_query 恰好等于上限不再误报截断', exactAudit.count === 50 && exactAudit.truncated === false)

/* ── 5xx 重试 / 超时 / 取消 ──────────────────────────────────────────────── */
console.log('# 健壮性')
let flakyCalls = 0
const flaky = createServer((req, res) => {
  flakyCalls += 1
  if (flakyCalls === 1) { res.writeHead(500, { 'content-type': 'application/json' }); res.end(JSON.stringify({ error: 'internal' })); return }
  res.writeHead(200, { 'content-type': 'application/json' }); res.end(JSON.stringify({ month: '2026-09', members: [] }))
})
await new Promise((r) => flaky.listen(0, '127.0.0.1', r))
const flakyTable = mount('flaky', { baseUrl: `http://127.0.0.1:${flaky.address().port}`, token: ADMIN_TOKEN })
const flakyResult = await runTool(flakyTable.table, 'user_list', {})
check('5xx 自动重试 1 次后成功', flakyCalls === 2 && flakyResult.shown === 0)

let postCalls = 0
const flakyPost = createServer((req, res) => {
  postCalls += 1
  res.writeHead(500, { 'content-type': 'application/json' }); res.end(JSON.stringify({ error: 'internal' }))
})
await new Promise((r) => flakyPost.listen(0, '127.0.0.1', r))
const flakyPostTable = mount('flakyPost', { baseUrl: `http://127.0.0.1:${flakyPost.address().port}`, token: ADMIN_TOKEN })
const postFail = await runFail(flakyPostTable.table, 'user_create', { account: 'p@x' })
check('写操作不自动重试（避免重复建号）并报 platform_error', postCalls === 1 && postFail.includes('platform_error'))

const slow = createServer(() => { /* 故意不响应 */ })
await new Promise((r) => slow.listen(0, '127.0.0.1', r))
const slowTable = mount('slow', { baseUrl: `http://127.0.0.1:${slow.address().port}`, token: ADMIN_TOKEN, timeoutMs: 150 })
const timeoutMsg = await runFail(slowTable.table, 'user_list', {})
check('超时兜底（exec.signal 之外自建 AbortSignal）→ timeout', timeoutMsg.includes('timeout') && timeoutMsg.includes('超时'))

const abortTable = mount('abort', { baseUrl, token: ADMIN_TOKEN })
const abortMsg = await runFail(abortTable.table, 'user_list', {}, { signal: AbortSignal.abort() })
check('外部取消 → aborted', abortMsg.includes('aborted'))

const hugeTable = mount('huge', { baseUrl, token: ADMIN_TOKEN, maxResponseBytes: 512 })
const hugeMsg = await runFail(hugeTable.table, 'user_quota_query', { account: 'huge@x' })
check('响应体过大 → response_too_large', hugeMsg.includes('response_too_large'))

// 超时也可经实例 env 配置（部署侧不用改插件包）。
const previousTimeoutEnv = process.env.KABAGE_ADMIN_TIMEOUT_MS
process.env.KABAGE_ADMIN_TIMEOUT_MS = '150'
const slowEnvTable = mount('slowEnv', { baseUrl: `http://127.0.0.1:${slow.address().port}`, token: ADMIN_TOKEN })
const slowEnvMsg = await runFail(slowEnvTable.table, 'user_list', {})
if (previousTimeoutEnv === undefined) delete process.env.KABAGE_ADMIN_TIMEOUT_MS
else process.env.KABAGE_ADMIN_TIMEOUT_MS = previousTimeoutEnv
check('超时阈值可经 env 配置（KABAGE_ADMIN_TIMEOUT_MS）', slowEnvMsg.includes('timeout'))

/* ── baseUrl 安全：明文 HTTP + 非回环 ───────────────────────────────────── */
console.log('# 传输安全')
const insecureUrl = `http://0.0.0.0:${mock.address().port}`
const seenBefore = seen.length
const insecureTable = mount('insecure', { baseUrl: insecureUrl, token: ADMIN_TOKEN })
const insecureMsg = await runFail(insecureTable.table, 'user_list', {})
check('非回环明文 HTTP 被显式拒绝（insecure_transport）', insecureMsg.includes('insecure_transport') && insecureMsg.includes('HTTP'))
check('被拒绝时未向该地址发出请求', seen.length === seenBefore)
const insecureAllowed = mount('insecureOk', { baseUrl: insecureUrl, token: ADMIN_TOKEN, allowInsecureHttp: true })
const insecureResult = await runTool(insecureAllowed.table, 'user_list', {})
check('显式 opt-in 后可调用但结果带高危告警', typeof insecureResult.securityWarning === 'string' && insecureResult.securityWarning.includes('明文 HTTP'))

mock.close()
flaky.close()
flakyPost.close()
slow.close()
console.log(`\n通过 ${passed}，失败 ${failed}`)
process.exit(failed > 0 ? 1 : 0)
