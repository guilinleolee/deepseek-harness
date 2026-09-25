/**
 * 卡巴格企业平台 · 服务令牌（栏目规划 v2 阶段 12）。
 *
 * 给可信实例内的管理类 DSH 工具提供机器凭据：data/service-tokens.json 存
 * [{id, tokenHash(SHA-256), role: "admin"|"readonly", createdAt}]；明文 token
 * （kbsvc-<base64url 256bit>）只在 createServiceToken 返回值出现一次。
 *
 * 安全语义：
 * - 比较走 timingSafeEqual（哈希恒 64 字节 hex，长度分支不泄露信息）；
 * - mtime 缓存读取：撤销后下一请求即生效；
 * - **服务令牌 = 管理凭据，仅注入可信实例**（能读到它即能以对应角色调用
 *   管理台 API）；readonly 角色仅放行只读白名单端点（白名单在 gateway.mjs）。
 */
import { createHash, randomBytes, timingSafeEqual } from 'node:crypto'
import { mkdirSync, readFileSync, renameSync, statSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'

const TOKENS_FILE = 'service-tokens.json'
const TOKEN_PREFIX = 'kbsvc-'

const ROLES = ['admin', 'readonly']

function isUnsafeKey(key) {
  return key === '__proto__' || key === 'constructor' || key === 'prototype'
}

const sha256Hex = (text) => createHash('sha256').update(text, 'utf8').digest('hex')

/** mtime 缓存读取（按 dataDir 键控——多目录并存时互不串扰，P2-7；文件损坏按空表处理）。 */
const caches = new Map() // dataDir -> { mtimeMs, tokens }
function loadTokens(dataDir) {
  let state = caches.get(dataDir)
  if (state === undefined) {
    state = { mtimeMs: -1, tokens: [] }
    caches.set(dataDir, state)
  }
  let mtimeMs
  try {
    mtimeMs = statSync(join(dataDir, TOKENS_FILE)).mtimeMs
  } catch {
    state.mtimeMs = -1
    state.tokens = []
    return []
  }
  if (state.mtimeMs === mtimeMs) return state.tokens
  let tokens = []
  try {
    const parsed = JSON.parse(readFileSync(join(dataDir, TOKENS_FILE), 'utf8'))
    if (Array.isArray(parsed?.tokens)) {
      tokens = parsed.tokens.filter((t) => t && typeof t.id === 'string' && typeof t.tokenHash === 'string' && !isUnsafeKey(t.id))
    }
  } catch { /* 损坏按空表 */ }
  state.mtimeMs = mtimeMs
  state.tokens = tokens
  return tokens
}

function saveTokens(dataDir, tokens) {
  mkdirSync(dataDir, { recursive: true })
  const path = join(dataDir, TOKENS_FILE)
  const tmp = `${path}.tmp`
  writeFileSync(tmp, `${JSON.stringify({ tokens }, null, 2)}\n`)
  renameSync(tmp, path)
  caches.set(dataDir, { mtimeMs: statSync(path).mtimeMs, tokens })
}

/**
 * 创建服务令牌：随机 256bit 明文只在本返回值出现一次，存储只落哈希。
 * id 校验（1–64 字母数字@._- 与中文）；重复 id 抛错。
 * @returns {{ id, role, token, createdAt }}
 */
export function createServiceToken(dataDir, id, role = 'admin') {
  if (typeof id !== 'string' || !/^[\w@.\-\u4e00-\u9fa5]{1,64}$/.test(id)) {
    throw new Error('令牌名称格式非法（允许字母数字、@._- 与中文，1–64 字符）')
  }
  if (!ROLES.includes(role)) throw new Error(`角色只支持 ${ROLES.join('/')}`)
  const tokens = loadTokens(dataDir)
  if (tokens.some((t) => t.id === id)) throw new Error(`令牌名称已存在: ${id}`)
  const token = `${TOKEN_PREFIX}${randomBytes(32).toString('base64url')}`
  const record = { id, tokenHash: sha256Hex(token), role, createdAt: new Date().toISOString() }
  tokens.push(record)
  saveTokens(dataDir, tokens)
  return { id, role, token, createdAt: record.createdAt }
}

/** 撤销（删除）；不存在返回 false。 */
export function revokeServiceToken(dataDir, id) {
  const tokens = loadTokens(dataDir)
  const next = tokens.filter((t) => t.id !== id)
  if (next.length === tokens.length) return false
  saveTokens(dataDir, next)
  return true
}

/** 列出令牌（不含哈希）。 */
export function listServiceTokens(dataDir) {
  return loadTokens(dataDir).map(({ tokenHash, ...rest }) => rest)
}

/**
 * 认证一个明文 token：全表逐条 timingSafeEqual 比较，命中返回 { id, role }。
 * 前缀不符直接 null（非 kbsvc- 串不做哈希）。
 */
export function authenticateServiceToken(dataDir, presented) {
  if (typeof presented !== 'string' || !presented.startsWith(TOKEN_PREFIX)) return null
  const digest = sha256Hex(presented)
  const expected = Buffer.from(digest, 'hex')
  for (const record of loadTokens(dataDir)) {
    if (typeof record.tokenHash !== 'string') continue
    const stored = Buffer.from(record.tokenHash, 'hex')
    if (stored.length === expected.length && timingSafeEqual(stored, expected)) {
      return { id: record.id, role: record.role === 'readonly' ? 'readonly' : 'admin' }
    }
  }
  return null
}
