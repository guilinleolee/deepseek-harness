/**
 * 卡巴格企业平台 · 实例内工具 RBAC 守卫（栏目规划 v2 阶段 9 + 11b 审批组）。
 *
 * Cordis 插件：注册一个全局 `ctx.tools.guard()` 单调守卫。每次工具调用按
 * 「工具名 → 工具组 → 实例 home 的 tool-policy.json deny/approve 列表」判定：
 * 命中 deny 返回拒绝理由（模型看到 `Error: <理由>`）；命中 approve 交给
 * DSH 审批缝——`tools/pre-execute` 瀑布监听返回 `{kind:'ask'}`，由管道调
 * `ctx.approval.request`，员工在 web UI 现场批准/拒绝，`approval/asked` +
 * `approval/decided` 成对落实例会话日志；否则放行。
 *
 * 策略文件语义（与平台 toolpolicy.mjs 约定一致）：
 * - 文件不存在 = 全放行（fail-open）——admin 角色的实例可能从未下发过文件，
 *   且隔离 precheck 启动的临时 home 里也没有；缺文件不是错误。
 * - 文件存在但 JSON 非法或结构不符 = fail-loud 抛错——加载时抛错让实例启动
 *   失败，运行中热更新出的坏文件让本次调用失败：坏配置必须可见，绝不静默放行。
 * - mtime 缓存：平台改策略文件后下一笔工具调用即生效，无需重启实例。
 *
 * 桥事件串行追加到实例 home 的 guard-events.jsonl（格式对齐平台审计事件：
 * ts/tool/group/decision）：deny 一如既往；审批组产生的批准/拒绝以
 * decision=approval-allowed/approval-denied/cancelled/unavailable 记录
 * （监听 approval/asked→decided 配对；时间片内被取消的 ask 无 decided，
 * 由 Map 清理丢弃）。平台 daemon 周期转写成 audit.jsonl（guard.deny /
 * guard.approval）后清空。桥文件写失败只降级到 stderr——它影响审计完整性，
 * 不影响拦截判定。
 *
 * 零 npm 依赖：仅 peer @deepseek-ai/cordis（经 profile 的修复兜底目录解析，
 * 插件本体不 import 任何包，ctx 由加载器注入）。
 */
import { closeSync, openSync, readFileSync, statSync, writeSync } from 'node:fs'

export const name = 'kabage-tool-guard'

/** 服务依赖声明：守卫挂在 ctx.tools 上（缺失即拒绝激活，fail-loud）。 */
export const inject = ['tools']

/**
 * 工具名 → 工具组映射。名字是 DSH 内置工具的真实注册名
 * （docs/tool-catalog.md 权威清单逐个核对；命令行组含 terminal 六件套）。
 * 未出现在映射里的工具（todo_write、skill、subagent、session_*、job_* 等）
 * 不属于任何受管组，一律放行——策略只约束企业明确分组的危险面。
 */
const TOOL_GROUPS = {
  command: [
    'bash', 'pwsh',
    'terminal_open', 'terminal_read', 'terminal_send', 'terminal_signal',
    'terminal_list', 'terminal_close',
  ],
  fs: [
    'read', 'write', 'edit', 'read_image',
    'str_replace_editor',
    'glob', 'grep',
  ],
  network: [
    'web_search', 'web_fetch',
  ],
}

const GROUP_OF = new Map()
for (const [group, names] of Object.entries(TOOL_GROUPS)) {
  for (const tool of names) GROUP_OF.set(tool, group)
}

/** 工具名 → 所属组；未分组工具返回 null（放行）。 */
export function groupOfTool(toolName) {
  return GROUP_OF.get(toolName) ?? null
}

/**
 * 策略文件结构校验：{ role?, deny: string[], approve?: string[] }，元素必须
 * 是已知组名；同一组不得同时出现在 deny 与 approve（矛盾配置 fail-loud）。
 */
export function validatePolicy(parsed) {
  if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) return null
  const deny = parsed.deny
  if (!Array.isArray(deny)) return null
  const seenDeny = new Set()
  for (const group of deny) {
    // hasOwn 而非 in：'__proto__' 等危险键会命中原型链，in 会误判为合法组名。
    if (typeof group !== 'string' || !Object.hasOwn(TOOL_GROUPS, group)) return null
    seenDeny.add(group)
  }
  let approve = []
  if (parsed.approve !== undefined) {
    if (!Array.isArray(parsed.approve)) return null
    const seenApprove = new Set()
    for (const group of parsed.approve) {
      if (typeof group !== 'string' || !Object.hasOwn(TOOL_GROUPS, group)) return null
      if (seenDeny.has(group)) return null
      seenApprove.add(group)
    }
    approve = [...seenApprove]
  }
  return { deny: [...seenDeny], approve }
}

/** 拒绝理由（模型可见文案）：点明平台策略与所属组，模型可据此改道而非重试。 */
function denialReason(tool, group, role) {
  return `工具策略拒绝：当前实例角色（${role}）未被授权使用 ${group} 组工具，工具 "${tool}" 已被平台管理员禁用`
}

/**
 * 插件入口。config：{ policyPath?, eventsPath? }，缺省取
 * `$DSH_HOME/tool-policy.json` 与 `$DSH_HOME/guard-events.jsonl`（平台
 * supervisor 为每个实例注入 DSH_HOME；cordis.patch.yml 里以 `!!js` 表达式
 * 显式传入同一取值，供部署按需覆盖成绝对路径）。
 */
export function apply(ctx, config) {
  const envHome = process.env.DSH_HOME ?? '.'
  const policyPath = typeof config?.policyPath === 'string' && config.policyPath !== ''
    ? config.policyPath : `${envHome}/tool-policy.json`
  const eventsPath = typeof config?.eventsPath === 'string' && config.eventsPath !== ''
    ? config.eventsPath : `${envHome}/guard-events.jsonl`

  /** mtime+size 缓存的一条策略：{ mtime, size, role, deny } | null（缺文件）。 */
  let cache = null

  /**
   * 读取（带 mtime+size 缓存）并校验策略。文件不存在返回 null（全放行）；
   * 存在但非法抛错（fail-loud，见文件头语义说明）。size 补 mtime 的盲区：
   * 秒级精度文件系统上同秒内的二次改写 mtime 不变，size 变化即可感知。
   */
  function loadPolicy() {
    let stats
    try {
      stats = statSync(policyPath)
    } catch {
      cache = null
      return null
    }
    if (cache !== null && cache.mtime === stats.mtimeMs && cache.size === stats.size) return cache
    let parsed
    try {
      parsed = JSON.parse(readFileSync(policyPath, 'utf8'))
    } catch (error) {
      cache = null
      throw new Error(`kabage-tool-guard: 策略文件 JSON 非法（${policyPath}）: ${error.message}`)
    }
    const policy = validatePolicy(parsed)
    if (policy === null) {
      cache = null
      throw new Error(`kabage-tool-guard: 策略文件结构非法（${policyPath}）: 期望 {"role":"...","deny":["command"|"fs"|"network",...],"approve":[...]（deny∩approve 不得相交）}`)
    }
    cache = { mtime: stats.mtimeMs, size: stats.size, role: typeof parsed.role === 'string' ? parsed.role : 'unknown', ...policy }
    return cache
  }

  /** 桥文件追加句柄（惰性，'a' 模式 O_APPEND 每次写在末尾，单行原子）。 */
  let eventsFd = null
  function openEvents() {
    if (eventsFd === null) eventsFd = openSync(eventsPath, 'a')
    return eventsFd
  }

  /** 串行追加一条桥事件（deny 或审批决定）；失败降级 stderr（不影响拦截判定）。 */
  function recordEvent(tool, group, decision) {
    const line = `${JSON.stringify({ ts: new Date().toISOString(), tool, group, decision })}\n`
    try {
      writeSync(openEvents(), line)
    } catch (error) {
      console.error(`[kabage-tool-guard] 桥事件写入失败（仅影响审计，不影响拦截）: ${error?.message ?? error}`)
      try { closeSync(eventsFd) } catch { /* 句柄已无效 */ }
      eventsFd = null
    }
  }

  /**
   * 审批缝桥接：approval/asked→decided 按 id 配对（decided 不带 toolName），
   * 只回流受管组工具的审批决定——沙箱提权等其他来源的审批不经本桥。
   * cancelled 的 ask（用户中断请求）没有 decided，Map 残留由下一次同 id 或
   * 进程生命周期兜底（ask id 一次性，泄漏上界为会话内被中断的请求数）。
   */
  const pendingAsks = new Map()
  ctx.on('approval/asked', (event) => {
    const group = groupOfTool(event.toolName)
    if (group !== null) pendingAsks.set(event.id, { toolName: event.toolName, group })
  })
  ctx.on('approval/decided', (event) => {
    const ask = pendingAsks.get(event.id)
    pendingAsks.delete(event.id)
    if (ask === undefined) return
    const decision = event.outcome === 'allowed-once' ? 'approval-allowed'
      : event.outcome === 'rejected' ? 'approval-denied'
        : event.outcome === 'cancelled' ? 'approval-cancelled' : 'approval-unavailable'
    recordEvent(ask.toolName, ask.group, decision)
  })

  /**
   * 审批组（阶段 11b）：命中 approve 组的工具调用经 tools/pre-execute 返回
   * `{kind:'ask'}`，由工具管道调审批缝（员工 web UI 现场批准/拒绝，
   * approval/asked+decided 落实例会话日志，拒绝转模型可见错误）。
   * 瀑布语义：不受本策略约束的调用必须 next() 放行。
   */
  ctx.on('tools/pre-execute', async (exec, next) => {
    const group = groupOfTool(exec.name)
    if (group === null) return next()
    const policy = loadPolicy()
    if (policy === null || !policy.approve.includes(group)) return next()
    return { kind: 'ask', reason: `平台策略要求审批：${group} 组工具 "${exec.name}" 需本次使用审批` }
  })

  /**
   * 全局单调守卫：拒绝返回理由字符串，放行返回 undefined。
   * 映射外工具与「策略文件缺失」都不经任何 I/O 直接放行。
   */
  ctx.tools.guard((exec) => {
    const group = groupOfTool(exec.name)
    if (group === null) return undefined
    const policy = loadPolicy()
    if (policy === null) return undefined
    if (!policy.deny.includes(group)) return undefined
    recordEvent(exec.name, group, 'deny')
    return denialReason(exec.name, group, policy.role)
  })
}
