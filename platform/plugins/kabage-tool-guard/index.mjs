/**
 * 卡巴格企业平台 · 实例内工具 RBAC 守卫（栏目规划 v2 阶段 9，实例侧）。
 *
 * Cordis 插件：注册一个全局 `ctx.tools.guard()` 单调守卫。每次工具调用按
 * 「工具名 → 工具组 → 实例 home 的 tool-policy.json deny 列表」判定：
 * 命中 deny 返回拒绝理由（模型看到 `Error: <理由>`），否则放行。
 *
 * 策略文件语义（与平台 toolpolicy.mjs 约定一致）：
 * - 文件不存在 = 全放行（fail-open）——admin 角色的实例可能从未下发过文件，
 *   且隔离 precheck 启动的临时 home 里也没有；缺文件不是错误。
 * - 文件存在但 JSON 非法或结构不符 = fail-loud 抛错——加载时抛错让实例启动
 *   失败，运行中热更新出的坏文件让本次调用失败：坏配置必须可见，绝不静默放行。
 * - mtime 缓存：平台改策略文件后下一笔工具调用即生效，无需重启实例。
 *
 * 拒绝事件串行追加到实例 home 的 guard-events.jsonl（桥文件，格式对齐平台
 * 审计事件：ts/tool/group/decision），由平台 daemon 周期转写成 audit.jsonl
 * 后清空。桥文件写失败只降级到 stderr——它影响审计完整性，不影响拦截判定。
 *
 * 零 npm 依赖：仅 peer @deepseek-ai/cordis（经 profile 的修复兜底目录解析，
 * 插件本体不 import 任何包，ctx 由加载器注入）。
 */
import { closeSync, openSync, readFileSync, statSync, writeSync } from 'node:fs'

export const name = 'kabage-tool-guard'

/** 服务依赖声明：本插件全部能力挂在 ctx.tools 上（缺失即拒绝激活，fail-loud）。 */
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

/** 策略文件结构校验：{ deny: string[] }，deny 元素必须是已知组名。 */
export function validatePolicy(parsed) {
  if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) return null
  const deny = parsed.deny
  if (!Array.isArray(deny)) return null
  for (const group of deny) {
    // hasOwn 而非 in：'__proto__' 等危险键会命中原型链，in 会误判为合法组名。
    if (typeof group !== 'string' || !Object.hasOwn(TOOL_GROUPS, group)) return null
  }
  return { deny: [...new Set(deny)] }
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
      throw new Error(`kabage-tool-guard: 策略文件结构非法（${policyPath}）: 期望 {"role":"...","deny":["command"|"fs"|"network",...]}`)
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

  /** 串行追加一条拒绝事件；失败降级 stderr（不影响拦截判定）。 */
  function recordDenial(tool, group) {
    const line = `${JSON.stringify({ ts: new Date().toISOString(), tool, group, decision: 'deny' })}\n`
    try {
      writeSync(openEvents(), line)
    } catch (error) {
      console.error(`[kabage-tool-guard] 拒绝事件写入失败（仅影响审计，不影响拦截）: ${error?.message ?? error}`)
      try { closeSync(eventsFd) } catch { /* 句柄已无效 */ }
      eventsFd = null
    }
  }

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
    recordDenial(exec.name, group)
    return denialReason(exec.name, group, policy.role)
  })
}
