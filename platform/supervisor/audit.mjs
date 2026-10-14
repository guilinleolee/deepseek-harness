/**
 * 卡巴格企业平台 · 审计日志（栏目规划 v2 第四节，本期最高优先）。
 *
 * 存储：data/audit.jsonl，只追加 JSONL，一行一事件；按大小轮转——达到
 * security.json 的 auditRotateBytes 即把当前文件改名为
 * audit-<时间戳>.jsonl 归档并另起新文件，只保留最新 auditKeepArchives 份
 * 归档（更早的删除，导出归档由 audit.export 承担）。查询跨 active+归档，
 * 从最新往旧扫，攒够 limit 即停。隐私红线：只记元数据（谁/何时/对谁/
 * 动作/结果/少量标量 detail），永不落会话正文、密码原文、密钥原文。
 *
 * 写入走模块级串行 promise 链 + fs.appendFile 保证并发调用的行序；追加失败
 * 只降级到 stderr，不拖垮业务请求。daemon 单进程同时承载网关/管理台/Relay，
 * 建服时以 initAudit 配置一次目录（重复传同一目录幂等）。
 */
import { appendFile } from 'node:fs/promises'
import { mkdirSync, readdirSync, readFileSync, renameSync, statSync, unlinkSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'

import { loadSecurityConfig } from './security.mjs'

const AUDIT_FILE = 'audit.jsonl'
const ARCHIVE_PATTERN = /^audit-\d{8}-\d{6}-\d{3}\.jsonl$/
const DEFAULT_QUERY_LIMIT = 500

let auditDir = null
let chain = Promise.resolve()
// 当前 active 文件的近似字节数（追加后累加；轮转后清零）。0 时惰性 statSync。
let activeSize = 0

/** 配置审计数据目录（gateway/relay 建服时调用；同目录重复调用为幂等）。 */
export function initAudit(dataDir) {
  if (auditDir === dataDir) return
  mkdirSync(dataDir, { recursive: true })
  auditDir = dataDir
  activeSize = 0
  chain = Promise.resolve()
}

/** 从请求取客户端 IP（去 IPv4-mapped 前缀，::1 规整为 127.0.0.1）。 */
export function clientIp(req) {
  const raw = req?.socket?.remoteAddress ?? ''
  if (raw === '::1') return '127.0.0.1'
  return raw.startsWith('::ffff:') ? raw.slice(7) : raw
}

/** 归档文件名（同秒内多次轮转靠毫秒段区分）。 */
const archiveName = () => {
  const d = new Date()
  const p = (n, w) => String(n).padStart(w, '0')
  return `audit-${d.getFullYear()}${p(d.getMonth() + 1, 2)}${p(d.getDate(), 2)}-${p(d.getHours(), 2)}${p(d.getMinutes(), 2)}${p(d.getSeconds(), 2)}-${p(d.getMilliseconds(), 3)}.jsonl`
}

/**
 * 追加前按 security.json 的 auditRotateBytes 轮转：active 达阈值即改名归档、
 * 超出 auditKeepArchives 的最旧归档删除，返回后 activeSize 归零重新计数。
 * 轮转在写入串行链内执行，无并发竞争；任一步失败只记 stderr（审计是
 * 降级不阻塞的存储），下次追加重试。
 */
function rotateIfNeeded() {
  if (auditDir === null) return
  const config = loadSecurityConfig(auditDir)
  if (activeSize === 0) {
    try { activeSize = statSync(join(auditDir, AUDIT_FILE)).size } catch { activeSize = 0 }
  }
  if (activeSize < config.auditRotateBytes) return
  try {
    renameSync(join(auditDir, AUDIT_FILE), join(auditDir, archiveName()))
  } catch (error) {
    console.error('[audit] 轮转改名失败（本事件仍追加到当前文件）:', error?.message ?? error)
    return
  }
  activeSize = 0
  try {
    const archives = readdirSync(auditDir).filter((name) => ARCHIVE_PATTERN.test(name)).sort().reverse()
    for (const stale of archives.slice(config.auditKeepArchives)) {
      try { unlinkSync(join(auditDir, stale)) } catch (error) {
        console.error('[audit] 归档清理失败:', stale, error?.message ?? error)
      }
    }
  } catch (error) {
    console.error('[audit] 归档清单读取失败:', error?.message ?? error)
  }
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
  const line = `${JSON.stringify(record)}\n`
  const write = chain.then(async () => {
    try {
      rotateIfNeeded()
      await appendFile(join(auditDir, AUDIT_FILE), line)
      activeSize += Buffer.byteLength(line)
    } catch (error) {
      console.error('[audit] 追加失败:', error?.message ?? error)
    }
  })
  chain = write
  return write
}

/**
 * 倒序查询审计事件（最新在前），跨 active + 全部归档：从 active 往归档
 * （文件名倒序 = 越来越旧）逐文件扫描，攒满 limit 即停——不设上限的导出
 * 自然覆盖归档全量。过滤：actionPrefix 前缀、actor 账号子串（大小写不敏感；
 * exact=true 时改为账号全等，供「只看本人」场景排除子串账号混入，如 a@x
 * 与 ba@x）、result 精确匹配；limit 默认 500。文件缺失或单行损坏只跳过，
 * 不抛错。
 */
export function auditQuery({ actionPrefix, actor, result, limit, exact } = {}) {
  if (auditDir === null) return []
  const max = Number.isInteger(limit) && limit > 0 ? limit : DEFAULT_QUERY_LIMIT
  const needle = actor ? String(actor).toLowerCase() : null
  const out = []
  let archiveNames = []
  try {
    archiveNames = readdirSync(auditDir).filter((name) => ARCHIVE_PATTERN.test(name)).sort().reverse()
  } catch { /* 目录缺失按无归档处理 */ }
  for (const name of [AUDIT_FILE, ...archiveNames]) {
    if (out.length >= max) break
    let raw = ''
    try {
      raw = readFileSync(join(auditDir, name), 'utf8')
    } catch {
      continue
    }
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
    // 每个文件只取最新的 remaining 条（文件内行序为旧→新），反转成新→旧
    // 追加；active 严格新于任何归档，跨文件次序成立。
    out.push(...matched.slice(-(max - out.length)).reverse())
  }
  return out
}
