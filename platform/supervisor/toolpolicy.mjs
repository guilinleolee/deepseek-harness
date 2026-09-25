/**
 * 卡巴格企业平台 · 实例内工具 RBAC（栏目规划 v2 阶段 9）。
 *
 * 一人一实例 ⇒ 工具策略是实例级的：账号绑实例、角色定策略。平台把每个实例
 * 归属账号的角色对应的策略写进实例 home 的 tool-policy.json，实例侧
 * kabage-tool-guard 插件读该文件（mtime 缓存）热生效，拒绝越权工具调用。
 *
 * - 策略存 data/toolpolicy.json（缺省自动生成），按角色给 deny 工具组列表
 *   （组名：command 命令行 / fs 文件 / network 联网，映射表在插件 README）；
 * - 下发：实例归属账号的角色 → deny 列表 → 原子写 <home>/tool-policy.json，
 *   策略或账号角色变更后重写（管理台入口 + supervisor sync-toolpolicy）；
 * - 拒绝收集：guard 插件把每次拒绝追加到 <home>/guard-events.jsonl（桥文件），
 *   daemon 周期采样把它转写成平台 audit.jsonl（action=guard.deny，actor=实例
 *   归属账号，detail 只放工具名/分组/实例名等标量），转写成功后清空桥文件
 *   （清空前崩溃会重放少量事件——审计只追加，重复好过丢失）。
 *
 * 隐私红线：转写只取桥文件里的工具名/分组/决策标量，不含参数与任何正文。
 */
import { mkdirSync, readFileSync, renameSync, statSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'

import { isUnsafeKey } from './quotas.mjs'

const POLICY_FILE = 'toolpolicy.json'
const HOME_POLICY_FILE = 'tool-policy.json'
const BRIDGE_FILE = 'guard-events.jsonl'

/** 工具组全集（与 kabage-tool-guard 的 classifyTool 映射一一对应）。 */
export const TOOL_GROUPS = ['command', 'fs', 'network']

/** 合法角色名（与 gateway.mjs 的 VALID_ROLES 一致，复制以避免反向依赖）。 */
const ROLES = ['admin', 'auditor', 'employee']

/** 缺省策略（与 data/toolpolicy.json 的自动生成内容一致；admin 全开）。 */
export const DEFAULT_TOOL_POLICY = {
  roles: {
    admin: { deny: [] },
    auditor: { deny: ['command', 'network'] },
    employee: { deny: ['command', 'network'] },
  },
}

/** 归一化一个角色的 deny 列表：只保留合法组名并去重；非法输入返回 null。 */
function normalizeDeny(value) {
  if (!Array.isArray(value)) return null
  const seen = new Set()
  for (const group of value) {
    if (typeof group !== 'string' || !TOOL_GROUPS.includes(group)) return null
    seen.add(group)
  }
  return TOOL_GROUPS.filter((group) => seen.has(group))
}

/** 归一化整个策略对象：只保留三角色的合法条目；dirty 表示需要重写回干净形态。 */
function normalizePolicy(parsed) {
  const roles = {}
  let dirty = false
  for (const role of ROLES) {
    const entry = parsed?.roles?.[role]
    const deny = normalizeDeny(entry?.deny)
    if (deny !== null) roles[role] = { deny }
    else dirty = true
  }
  if (parsed?.roles !== undefined) {
    for (const key of Object.keys(parsed.roles)) {
      if (isUnsafeKey(key) || !ROLES.includes(key)) dirty = true
    }
  }
  return { policy: { roles }, dirty }
}

function writePolicyFile(dataDir, policy) {
  const path = join(dataDir, POLICY_FILE)
  const tmp = `${path}.tmp`
  writeFileSync(tmp, `${JSON.stringify(policy, null, 2)}\n`)
  renameSync(tmp, path)
}

/**
 * 读取工具策略；缺省自动生成，手改出的非法配置回退该角色缺省并重写
 * （语义同 security.mjs：坏值不静默保留）。
 */
export function loadToolPolicy(dataDir) {
  mkdirSync(dataDir, { recursive: true })
  let stored = null
  try {
    stored = JSON.parse(readFileSync(join(dataDir, POLICY_FILE), 'utf8'))
  } catch {
    stored = null
  }
  if (stored === null || typeof stored !== 'object' || Array.isArray(stored)) {
    writePolicyFile(dataDir, DEFAULT_TOOL_POLICY)
    return structuredClone(DEFAULT_TOOL_POLICY)
  }
  const { policy, dirty } = normalizePolicy(stored)
  if (dirty) {
    console.error('[toolpolicy] toolpolicy.json 存在非法配置，已回退合法角色条目并重写')
    writePolicyFile(dataDir, policy)
  }
  return policy
}

/**
 * 合并保存工具策略（roles 允许只传部分角色）。未知角色/危险键/非法 deny 抛错
 * （调用方转 400 并留审计），校验通过才原子落盘。返回保存后的完整策略。
 */
export function saveToolPolicy(dataDir, roles) {
  if (roles === null || typeof roles !== 'object' || Array.isArray(roles)) {
    throw new Error('roles 必须是对象')
  }
  const policy = loadToolPolicy(dataDir)
  for (const [role, entry] of Object.entries(roles)) {
    if (isUnsafeKey(role)) throw new Error(`非法角色键: ${role}`)
    if (!ROLES.includes(role)) throw new Error(`未知角色: ${role}（仅支持 ${ROLES.join('/')}）`)
    const deny = normalizeDeny(entry?.deny)
    if (deny === null) {
      throw new Error(`${role}.deny 必须是由 ${TOOL_GROUPS.join('/')} 组成的数组`)
    }
    policy.roles[role] = { deny }
  }
  writePolicyFile(dataDir, policy)
  return policy
}

/** 某角色的 deny 列表（未知角色按最严的 employee 缺省处理）。 */
export function denyForRole(policy, role) {
  return policy.roles[role]?.deny ?? DEFAULT_TOOL_POLICY.roles.employee.deny
}

/** 实例 home 的策略文件路径。 */
export function homePolicyPath(home) {
  return join(home, HOME_POLICY_FILE)
}

function loadAccountsRaw(dataDir) {
  try {
    return JSON.parse(readFileSync(join(dataDir, 'accounts.json'), 'utf8')).accounts ?? []
  } catch {
    return []
  }
}

/**
 * 把一个实例的策略下发到它的 home：归属账号的角色 → deny 列表 → 原子写
 * tool-policy.json（实例侧 guard 读 mtime 热生效，无需重启）。
 * 归属账号在 accounts.json 无记录时跳过并告警（等待账号侧操作补齐）。
 * @returns {{ skipped?: true, role?: string, deny?: string[] }}
 */
export function syncInstanceHome(dataDir, spec) {
  const role = loadAccountsRaw(dataDir).find((a) => a.account === spec.account)?.role
  if (role === undefined) {
    console.error(`[toolpolicy] 实例 ${spec.id} 的归属账号 ${spec.account} 不存在，跳过策略下发`)
    return { skipped: true }
  }
  const deny = denyForRole(loadToolPolicy(dataDir), role)
  const home = join(dataDir, 'homes', spec.id)
  mkdirSync(home, { recursive: true })
  const payload = { role, deny }
  const path = homePolicyPath(home)
  const tmp = `${path}.tmp`
  writeFileSync(tmp, `${JSON.stringify(payload, null, 2)}\n`)
  renameSync(tmp, path)
  return { role, deny }
}

/** 全量重写：所有实例 home 的策略文件（策略变更后调用）。 */
export function syncAllHomes(dataDir, manifest) {
  loadToolPolicy(dataDir) // 缺省自动生成 data/toolpolicy.json（全新部署即有缺省策略）
  return manifest.instances.map((spec) => ({ id: spec.id, ...syncInstanceHome(dataDir, spec) }))
}

/** 读出桥文件快照（合法事件行 + mtime/size 指纹）；缺文件返回 null。 */
function readBridgeSnapshot(path) {
  let raw
  let stat
  try {
    stat = statSync(path)
    raw = readFileSync(path, 'utf8')
  } catch {
    return null
  }
  const events = []
  for (const line of raw.split('\n')) {
    if (line.trim() === '') continue
    try {
      const event = JSON.parse(line)
      if (typeof event?.tool === 'string' && typeof event?.group === 'string' && event.decision === 'deny') {
        events.push(event)
      }
    } catch { /* 半行损坏只跳过 */ }
  }
  return { events, mtimeMs: stat.mtimeMs, size: stat.size }
}

/**
 * 截断前重读比对：文件指纹（mtime 与 size）与转写用的快照一致才清空。
 * 并发追加（实例侧 guard 在读取与截断之间又写了事件）时不清空——本轮只
 * 转写快照内容，新追加的事件留待下一轮，消除「转写期间追加被截断销毁」
 * 的窗口。文件已消失按变化处理（不清空、不抛错）。
 * @returns true 表示已截断；false 表示检测到并发变化，保留文件。
 */
export function truncateIfUnchanged(path, snapshot) {
  let stat
  try {
    stat = statSync(path)
  } catch {
    return false
  }
  if (stat.mtimeMs !== snapshot.mtimeMs || stat.size !== snapshot.size) return false
  writeFileSync(path, '')
  return true
}

/**
 * 把各实例 home 的 guard-events.jsonl 转写成平台审计并清空桥文件。
 * 由 daemon 周期调用（也供 sync-toolpolicy 手动触发）；转写走 audit.mjs 的
 * 串行链，await 全部落盘后经 truncateIfUnchanged 清空（并发追加不截断，
 * 留待下轮）。桥文件缺文件/无事件直接返回，不碰磁盘。
 * @returns {Promise<{ transcribed: number, instances: string[], pending: string[] }>}
 *   pending = 检测到并发追加而未截断的实例（本轮已转写快照部分）。
 */
export async function transcribeGuardEvents(dataDir, manifest, auditAppend) {
  const accounts = loadAccountsRaw(dataDir)
  let transcribed = 0
  const touched = []
  const pending = []
  for (const spec of manifest.instances) {
    const path = join(dataDir, 'homes', spec.id, BRIDGE_FILE)
    const snapshot = readBridgeSnapshot(path)
    if (snapshot === null || snapshot.events.length === 0) continue
    const role = accounts.find((a) => a.account === spec.account)?.role ?? null
    for (const event of snapshot.events) {
      await auditAppend({
        actor: { account: spec.account, role, ip: null },
        action: 'guard.deny',
        target: event.tool,
        result: 'deny',
        detail: { tool: event.tool, group: event.group, instance: spec.id },
      })
    }
    // 清空而非删除：实例侧 guard 持有追加句柄，Windows 上删除打开中的文件
    // 会失败；截断后 O_APPEND 句柄继续在末尾追加，无丢失窗口。
    if (truncateIfUnchanged(path, snapshot)) {
      transcribed += snapshot.events.length
      touched.push(spec.id)
    } else {
      transcribed += snapshot.events.length
      pending.push(spec.id)
    }
  }
  return { transcribed, instances: touched, pending }
}

/** 桥文件路径（测试与 CLI 用）。 */
export function bridgePathFor(home) {
  return join(home, BRIDGE_FILE)
}

/** 平台策略文件路径（测试用）。 */
export function policyFilePath(dataDir) {
  return join(dataDir, POLICY_FILE)
}

/** 桥文件事件行的 mtime 读取辅助（daemon 采样前快速跳过未变化实例）。 */
export function bridgeChanged(home, sinceMs) {
  try {
    return statSync(bridgePathFor(home)).mtimeMs > sinceMs
  } catch {
    return false
  }
}
