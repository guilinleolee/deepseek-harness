/**
 * kabage-tool-guard 单元测试（零测试框架，node 直接运行）。
 *
 * 覆盖：工具分类映射（真实注册名逐个断言）、策略结构校验（危险/非法结构）、
 * guard 行为（缺文件放行 / deny 拦截 / 未分组放行 / mtime 热生效 / 非法文件
 * fail-loud）、拒绝事件串行追加、DSH_HOME env 缺省 config。不触网、不占
 * 平台端口，全程系统临时目录。
 *
 * 运行：node platform/plugins/kabage-tool-guard/test/guard-test.mjs
 */
import { existsSync, mkdtempSync, readFileSync, rmSync, utimesSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { apply, groupOfTool, name as pluginName, validatePolicy } from '../index.mjs'

const HOME = mkdtempSync(join(tmpdir(), 'kabage-guard-'))
const POLICY = join(HOME, 'tool-policy.json')
const EVENTS = join(HOME, 'guard-events.jsonl')

let passed = 0
let failed = 0
const check = (cond, label) => {
  if (cond === true) { passed += 1; console.log(`  ok  ${label}`) } else { failed += 1; console.error(`FAIL  ${label}`) }
}
const throws = (fn) => {
  try { fn(); return false } catch { return true }
}
const writePolicy = (object) => {
  writeFileSync(POLICY, `${JSON.stringify(object)}\n`)
  // Windows mtime 毫秒分辨率可能同刻：显式推 2 秒确保 mtime 缓存失效。
  utimesSync(POLICY, new Date(Date.now() + 2_000), new Date(Date.now() + 2_000))
}

/**
 * 挂载一个插件实例：捕获 guard 函数与 ctx.on 注册的事件监听器。
 * runListeners(event, payload) 依次触发该事件的监听器（审批桥测试用）。
 */
function mount(config) {
  let guard = null
  const listeners = new Map()
  const ctx = {
    tools: { guard(fn) { guard = fn; return () => {} } },
    on(event, fn) {
      const list = listeners.get(event) ?? []
      list.push(fn)
      listeners.set(event, list)
    },
  }
  apply(ctx, config)
  const runListeners = (event, payload) => Promise.all((listeners.get(event) ?? []).map((fn) => fn(payload)))
  const call = (toolName) => guard({ name: toolName, arguments: {}, callId: 't' })
  call.preExecute = async (toolName, next = async () => 'ALLOWED-BY-NEXT') => {
    const list = listeners.get('tools/pre-execute') ?? []
    let decision
    for (const fn of list) decision = await fn({ name: toolName, arguments: {}, callId: 't' }, next)
    return decision
  }
  call.runListeners = runListeners
  return call
}

/* ── 1. 工具分类映射（真实注册名逐个断言）────────────────────────────────── */
console.log('# 工具分类映射')
for (const tool of ['bash', 'pwsh', 'terminal_open', 'terminal_read', 'terminal_send', 'terminal_signal', 'terminal_list', 'terminal_close']) {
  check(groupOfTool(tool) === 'command', `command 组: ${tool}`)
}
for (const tool of ['read', 'write', 'edit', 'read_image', 'str_replace_editor', 'glob', 'grep']) {
  check(groupOfTool(tool) === 'fs', `fs 组: ${tool}`)
}
for (const tool of ['web_search', 'web_fetch']) {
  check(groupOfTool(tool) === 'network', `network 组: ${tool}`)
}
for (const tool of ['todo_write', 'skill', 'subagent', 'session_search', 'job_output', 'ask_user_question', 'run_code', '完全不存在的工具']) {
  check(groupOfTool(tool) === null, `未分组放行: ${tool}`)
}

/* ── 2. 策略结构校验 ─────────────────────────────────────────────────────── */
console.log('# 策略结构校验')
check(pluginName === 'kabage-tool-guard', '插件导出名')
check(validatePolicy({ role: 'employee', deny: ['command', 'network'] }).deny.length === 2, '合法策略通过')
check(validatePolicy({ deny: ['command', 'command'] }).deny.length === 1, '重复组去重')
check(validatePolicy({ deny: [] }).deny.length === 0, '空 deny 合法')
check(validatePolicy(null) === null, 'null 拒绝')
check(validatePolicy('x') === null, '字符串拒绝')
check(validatePolicy([]) === null, '数组拒绝')
check(validatePolicy({ role: 'x' }) === null, '缺 deny 拒绝')
check(validatePolicy({ deny: 'command' }) === null, 'deny 非数组拒绝')
check(validatePolicy({ deny: ['command', 'shell'] }) === null, '未知组名拒绝')
check(validatePolicy({ deny: [1] }) === null, '非字符串组名拒绝')
check(validatePolicy({ deny: ['__proto__'] }) === null, '危险组名拒绝')
check(validatePolicy({ deny: ['command'], approve: ['fs'] }).approve.length === 1, 'approve 合法通过')
check(validatePolicy({ deny: ['command'] }).approve.length === 0, 'approve 缺省空数组')
check(validatePolicy({ deny: ['command'], approve: 'fs' }) === null, 'approve 非数组拒绝')
check(validatePolicy({ deny: ['command'], approve: ['shell'] }) === null, 'approve 未知组名拒绝')
check(validatePolicy({ deny: ['command'], approve: ['command'] }) === null, 'deny∩approve 相交拒绝')

/* ── 3. guard 行为：缺文件全放行（fail-open）────────────────────────────── */
console.log('# 缺文件全放行')
const envHome = process.env.DSH_HOME
process.env.DSH_HOME = HOME // 同时验证 config 缺省取 $DSH_HOME
const fresh = mount({})
check(fresh('bash') === undefined, '无策略文件：bash 放行')
check(fresh('web_search') === undefined, '无策略文件：web_search 放行')
check(existsSync(POLICY) === false, '守卫不创建策略文件')

/* ── 4. deny 拦截 + 未分组放行 + 桥文件串行追加 ──────────────────────────── */
console.log('# deny 拦截与事件追加')
writePolicy({ role: 'employee', deny: ['command', 'network'] })
const denyCmd = mount({ policyPath: POLICY, eventsPath: EVENTS })
const reason = String(denyCmd('bash'))
check(reason.includes('工具策略拒绝') && reason.includes('command') && reason.includes('employee'), 'bash 被拒且文案点名组与角色')
check(denyCmd('pwsh') !== undefined, 'pwsh 同组被拒')
check(denyCmd('web_fetch') !== undefined, 'web_fetch 被拒（network）')
check(denyCmd('read') === undefined, 'read 放行（fs 未禁）')
check(denyCmd('todo_write') === undefined, '未分组工具不受策略影响')
const denySingle = mount({ policyPath: POLICY, eventsPath: EVENTS })
denySingle('terminal_send')
const lines = readFileSync(EVENTS, 'utf8').trimEnd().split('\n')
check(lines.length === 4, `拒绝事件串行追加（4 笔）`)
const events = lines.map((l) => JSON.parse(l))
check(events.every((e) => e.decision === 'deny' && typeof e.ts === 'string' && e.tool && e.group), '事件字段齐全（ts/tool/group/decision）')
check(events[0].tool === 'bash' && events[0].group === 'command', '首条事件 bash/command')

/* ── 5. mtime 热生效：平台改策略下一笔调用即变 ───────────────────────────── */
console.log('# mtime 热生效')
check(denySingle('web_search') !== undefined, '改前 web_search 被拒')
writePolicy({ role: 'employee', deny: [] })
check(denySingle('web_search') === undefined, '清空 deny 后 web_search 立即放行（无需重启）')
writePolicy({ role: 'employee', deny: ['fs'] })
check(denySingle('read') !== undefined, '补禁 fs 后 read 立即被拒')
check(denySingle('bash') === undefined, 'command 已解禁放行')

/* ── 6. 非法策略文件 fail-loud ──────────────────────────────────────────── */
console.log('# 非法文件 fail-loud')
writeFileSync(POLICY, '{broken json')
check(throws(() => denySingle('read')), 'JSON 非法：调用抛错而非放行')
writePolicy({ deny: 'command' })
check(throws(() => denySingle('read')), '结构非法：调用抛错而非放行')
// 修复后恢复判定（抛错不清空合法缓存之外的状态）。
writePolicy({ role: 'employee', deny: ['fs'] })
check(denySingle('read') !== undefined, '文件修复后恢复拦截')

/* ── 7. 同秒二次改写感知（size 补 mtime 盲区，P2-6）──────────────────────── */
console.log('# 同秒改写感知')
// 刻意不用 utimes 推移：同秒内连续改写 mtime 不变，size 变化必须被感知。
const fast = mount({ policyPath: POLICY, eventsPath: EVENTS })
writeFileSync(POLICY, `${JSON.stringify({ role: 'employee', deny: ['fs'] })}\n`)
check(fast('read') !== undefined, '改写 A：read 被拒')
writeFileSync(POLICY, `${JSON.stringify({ role: 'employee', deny: [] })}\n`)
check(fast('read') === undefined, '同秒清空 deny（size 变化）→ read 立即放行')
writeFileSync(POLICY, `${JSON.stringify({ role: 'employee', deny: ['network'] })}\n`)
check(fast('web_search') !== undefined, '同秒补禁 network（size 变化）→ web_search 立即被拒')

/* ── 8. 审批组（阶段 11b）：approve → pre-execute 返回 ask；桥接审批决定 ── */
console.log('# 审批组与审批桥接')
writePolicy({ role: 'employee', deny: ['command'], approve: ['network'] })
const approver = mount({ policyPath: POLICY, eventsPath: EVENTS })
check(await approver.preExecute('web_search').then((d) => d?.kind === 'ask' && String(d.reason).includes('审批')), 'approve 组命中 → pre-execute 返回 ask 决策')
check(await approver.preExecute('bash') === 'ALLOWED-BY-NEXT', 'deny 组命中 → pre-execute 仍 next() 放行（deny 由 guard 负责）')
check(await approver.preExecute('todo_write') === 'ALLOWED-BY-NEXT', '未分组工具 → pre-execute next() 放行')
writePolicy({ role: 'employee', deny: ['command'] })
check(await approver.preExecute('web_search') === 'ALLOWED-BY-NEXT', 'approve 清空（mtime 热生效）→ next() 放行')
// 审批桥：asked→decided 按 id 配对写桥文件（独立桥文件，不与 deny 段混行）；
// 非受管工具与未配对 decided 不写。
const BRIDGE_EVENTS = join(HOME, 'guard-events-bridge.jsonl')
writePolicy({ role: 'employee', deny: [], approve: ['network'] })
const bridge = mount({ policyPath: POLICY, eventsPath: BRIDGE_EVENTS })
await bridge.runListeners('approval/asked', { id: 'a1', toolName: 'web_search' })
await bridge.runListeners('approval/decided', { id: 'a1', outcome: 'allowed-once' })
await bridge.runListeners('approval/asked', { id: 'a2', toolName: 'web_fetch' })
await bridge.runListeners('approval/decided', { id: 'a2', outcome: 'rejected' })
await bridge.runListeners('approval/asked', { id: 'a3', toolName: 'todo_write' })
await bridge.runListeners('approval/decided', { id: 'a3', outcome: 'allowed-once' })
await bridge.runListeners('approval/decided', { id: 'unknown', outcome: 'rejected' })
const bridgeLines = readFileSync(BRIDGE_EVENTS, 'utf8').trim().split('\n').map((l) => JSON.parse(l))
check(bridgeLines.some((e) => e.tool === 'web_search' && e.decision === 'approval-allowed'), '批准事件落桥（approval-allowed）')
check(bridgeLines.some((e) => e.tool === 'web_fetch' && e.decision === 'approval-denied'), '拒绝事件落桥（approval-denied）')
check(bridgeLines.every((e) => e.tool !== 'todo_write'), '非受管工具的审批不落桥')
check(bridgeLines.length === 2, '未配对 decided 不落桥')
check(bridgeLines.every((e) => typeof e.ts === 'string' && e.group === 'network'), '桥事件含 ts/group 标量')

process.env.DSH_HOME = envHome
rmSync(HOME, { recursive: true, force: true })
console.log(`\n通过 ${passed}，失败 ${failed}`)
process.exit(failed > 0 ? 1 : 0)
