/**
 * 卡巴格企业平台 · 审计日志（栏目规划 v2 第四节，本期最高优先）。
 *
 * 存储：data/audit.jsonl，只追加 JSONL，一行一事件；MVP 无轮转，提供导出归档。
 * 隐私红线：只记元数据（谁/何时/对谁/动作/结果/少量标量 detail），永不落
 * 会话正文、密码原文、密钥原文。
 *
 * 写入走模块级串行 promise 链 + fs.appendFile 保证并发调用的行序；追加失败
 * 只降级到 stderr，不拖垮业务请求。daemon 单进程同时承载网关/管理台/Relay，
 * 建服时以 initAudit 配置一次目录（重复传同一目录幂等）。
 */
import { appendFile } from 'node:fs/promises'
import { mkdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'

const AUDIT_FILE = 'audit.jsonl'
const DEFAULT_QUERY_LIMIT = 500

let auditDir = null
let chain = Promise.resolve()

/** 配置审计数据目录（gateway/relay 建服时调用；同目录重复调用为幂等）。 */
export function initAudit(dataDir) {
  if (auditDir === dataDir) return
  mkdirSync(dataDir, { recursive: true })
  auditDir = dataDir
  chain = Promise.resolve()
}

/** 从请求取客户端 IP（去 IPv4-mapped 前缀，::1 规整为 127.0.0.1）。 */
export function clientIp(req) {
  const raw = req?.socket?.remoteAddress ?? ''
  if (raw === '::1') return '127.0.0.1'
  return raw.startsWith('::ffff:') ? raw.slice(7) : raw
}

/**
 * 追加一条审计事件。entry：{ actor:{account,role,ip}, action, target?,
 * result?, detail?, ts? }；ts/result 缺省补当前时间/ok。返回 promise，
 * 落盘（或失败降级为 stderr 日志）后 resolve，需要顺序保证的调用方可 await。
 */
export function auditAppend(entry) {
  if (auditDir === null) {
    console.error('[audit] 数据目录未初始化，事件被丢弃:', entry?.action)
    return Promise.resolve()
  }
  if (typeof entry?.action !== 'string' || entry.action === '') {
    console.error('[audit] 事件缺少 action，被丢弃:', String(JSON.stringify(entry)).slice(0, 200))
    return Promise.resolve()
  }
  const record = {
    ts: entry.ts ?? new Date().toISOString(),
    actor: entry.actor ?? null,
    action: entry.action,
    target: entry.target ?? null,
    result: entry.result ?? 'ok',
    detail: entry.detail ?? null,
  }
  const write = chain.then(async () => {
    try {
      await appendFile(join(auditDir, AUDIT_FILE), `${JSON.stringify(record)}\n`)
    } catch (error) {
      console.error('[audit] 追加失败:', error?.message ?? error)
    }
  })
  chain = write
  return write
}

/**
 * 倒序查询审计事件（最新在前）。过滤：actionPrefix 前缀、actor 账号子串
 * （大小写不敏感；exact=true 时改为账号全等，供「只看本人」场景排除子串
 * 账号混入，如 a@x 与 ba@x）、result 精确匹配；limit 默认 500。文件缺失
 * 或单行损坏只跳过，不抛错。
 */
export function auditQuery({ actionPrefix, actor, result, limit, exact } = {}) {
  if (auditDir === null) return []
  let raw = ''
  try {
    raw = readFileSync(join(auditDir, AUDIT_FILE), 'utf8')
  } catch {
    return []
  }
  const max = Number.isInteger(limit) && limit > 0 ? limit : DEFAULT_QUERY_LIMIT
  const needle = actor ? String(actor).toLowerCase() : null
  const matched = []
  for (const line of raw.split('\n')) {
    if (line.trim() === '') continue
    let entry
    try {
      entry = JSON.parse(line)
    } catch {
      continue
    }
    if (actionPrefix && !String(entry.action ?? '').startsWith(actionPrefix)) continue
    if (needle !== null) {
      const account = String(entry.actor?.account ?? '').toLowerCase()
      if (exact === true ? account !== needle : !account.includes(needle)) continue
    }
    if (result && entry.result !== result) continue
    matched.push(entry)
  }
  return matched.slice(-max).reverse()
}
