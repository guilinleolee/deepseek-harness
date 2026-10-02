/**
 * kabage-admin-tools 单元测试（零测试框架，node 直接运行）。
 *
 * 起本地 mock 平台服务器（node:http，假 console API + 鉴权头校验），挂载
 * 插件并捕获注册的 7 个工具，断言：请求路径/方法/鉴权头、响应到工具结果
 * 的映射、401/403/4xx/网络错转译、列表截断（≤50）、token 缺失的中文配置
 * 错误、presentCall 的 generic render intent。不触网（mock 仅 127.0.0.1
 * 随机端口）、不依赖真平台。
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
  account: `u${String(i).padStart(2, '0')}@x`, displayName: `成员${i}`, department: '设计部',
  role: 'employee', instanceId: 'e02', disabled: false, monthlyPoints: 1000, pointsUsed: i * 10,
  tokensIn: 0, tokensOut: 0, requests: 0,
}))

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
      if (account !== 'u00@x') return json(404, { error: `账号不存在: ${account}` })
      return json(200, { account, month: '2026-09', points: 320, monthlyPoints: 1000, remainingPoints: 680, tokensIn: 50, tokensOut: 10, tokensUsed: 60, monthlyTokens: null, requests: 7, legacy: false, unlimited: false })
    }
    if (req.method === 'GET' && url.pathname === '/console/api/audit') {
      return json(200, { events: [{ ts: '2026-09-25T10:00:00.000Z', actor: { account: 'svc:e01-admin', role: 'admin' }, action: 'member.create', target: 'u99@x', result: 'ok', detail: null }] })
    }
    if (req.method === 'POST' && url.pathname === '/console/api/member/create') {
      const body = JSON.parse(raw)
      return json(200, { ok: true, account: body.account, instance: body.instance, password: 'Gen-Pass12' })
    }
    if (req.method === 'POST' && url.pathname === '/console/api/member/update') {
      return json(200, { ok: true, role: JSON.parse(raw).role ?? 'employee', department: JSON.parse(raw).department ?? '未分配' })
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

/* ── 注册形态 ────────────────────────────────────────────────────────────── */
console.log('# 注册形态')
check('插件导出名', pluginName === 'kabage-admin-tools')
check('注册 7 个工具', registered.size === 7)
for (const toolName of ['user_list', 'user_quota_query', 'audit_query', 'user_create', 'user_update', 'user_reset_password', 'user_set_disabled']) {
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
check('audit_query limit 钳制到 50（请求侧）', seen.at(-1).path.includes('limit=50'))
check('audit_query 映射事件', audited.count === 1 && audited.events[0].action === 'member.create')
check('audit_query 请求参数正确（action/limit=50，无 account）', seen.at(-1).path.includes('action=member') && seen.at(-1).path.includes('limit=50') && !seen.at(-1).path.includes('account='))

/* ── 变更四工具（映射与缺省值）──────────────────────────────────────────── */
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
check('平台 404 透传中文文案', String(await callFail('user_quota_query', { account: 'ghost@x' })).includes('平台拒绝该操作（404）') && String(await callFail('user_quota_query', { account: 'ghost@x' })).includes('账号不存在'))
// token 缺失的独立实例：config.token 与 env 均为空。
const previousTokenEnv = process.env.KABAGE_SERVICE_TOKEN
delete process.env.KABAGE_SERVICE_TOKEN
const noTokenCtx = { tools: { register(definition) { registered.set(`nt-${definition.name}`, definition); return () => {} } } }
apply(noTokenCtx, { baseUrl })
const missing = await (async () => {
  const tool = registered.get('nt-user_list')
  try { await tool.execute({}, { signal: AbortSignal.timeout(5000) }); return null } catch (error) { return String(error?.message ?? error) }
})()
if (previousTokenEnv !== undefined) process.env.KABAGE_SERVICE_TOKEN = previousTokenEnv
check('token 缺失：中文配置错误（token_missing）', missing !== null && missing.includes('未配置服务令牌') && missing.includes('token_missing'))

// readonly 令牌：变更工具调用 → 平台 403 → forbidden 转译（不探测、始终注册）。
const readonlyCtx = { tools: { register(definition) { registered.set(`ro-${definition.name}`, definition); return () => {} } } }
apply(readonlyCtx, { baseUrl, token: READONLY_TOKEN, defaultInstance: 'e02' })
const readonlyDenied = await callFail('user_create', { account: 'ro@x' }).then(async () => {
  const tool = registered.get('ro-user_create')
  try { await tool.execute({ account: 'ro@x' }, { signal: AbortSignal.timeout(5000) }); return null } catch (error) { return String(error?.message ?? error) }
})
check('readonly 令牌调变更工具 → 403 转译（forbidden）', readonlyDenied !== null && readonlyDenied.includes('权限不足') && readonlyDenied.includes('forbidden'))

// 401：坏 token。
const badCtx = { tools: { register(definition) { registered.set(`bad-${definition.name}`, definition); return () => {} } } }
apply(badCtx, { baseUrl, token: 'kbsvc-wrong', defaultInstance: 'e02' })
const badResult = await (async () => {
  const tool = registered.get('bad-user_list')
  try { await tool.execute({}, { signal: AbortSignal.timeout(5000) }); return null } catch (error) { return String(error?.message ?? error) }
})()
check('坏 token → 401 转译（auth_failed）', badResult !== null && badResult.includes('认证失败') && badResult.includes('auth_failed'))

// 网络错：错误端口。
const unreachableCtx = { tools: { register(definition) { registered.set(`un-${definition.name}`, definition); return () => {} } } }
apply(unreachableCtx, { baseUrl: 'http://127.0.0.1:1', token: ADMIN_TOKEN })
const unreachable = await (async () => {
  const tool = registered.get('un-user_list')
  try { await tool.execute({}, { signal: AbortSignal.timeout(5000) }); return null } catch (error) { return String(error?.message ?? error) }
})()
check('网络不可达 → unreachable 转译', unreachable !== null && unreachable.includes('无法连接平台管理接口') && unreachable.includes('unreachable'))

mock.close()
console.log(`\n通过 ${passed}，失败 ${failed}`)
process.exit(failed > 0 ? 1 : 0)
