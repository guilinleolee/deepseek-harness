/**
 * 卡巴格企业平台 · 邀请注册（栏目规划 v2 阶段 10）。
 *
 * 邀请存 data/invites.json：{ invites: [{ id, codeHash, department, role,
 * instanceId, expiresAt, used, usedBy?, consumedAt?, revoked?, createdAt }] }。
 * 明文 code（inv-<base64url 192bit>）只在 createInvite 返回值与邀请链接里出现
 * 一次，存储与审计只落 SHA-256；校验用 timingSafeEqual 常数时间比较防时序
 * 侧信道（全表逐条比较，长度恒等 64 字节 hex，长度分支不泄露信息）。
 *
 * 语义：
 * - validateInvite 只读校验（注册页 GET 预设展示用），不产生副作用；
 * - consumeInvite 校验通过即原子标记 used（注册建号成功后调用；调用方用
 *   串行队列保证同一 code 的并发注册串行化，标记失败不可能与建号交错）；
 * - 撤销只对未用邀请生效（已用的撤销无语义）。
 */
import { createHash, randomBytes, timingSafeEqual } from 'node:crypto'
import { mkdirSync, readFileSync, renameSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'

const INVITES_FILE = 'invites.json'
/** 邀请角色白名单：邀请不发放 admin（管理员只能由既有管理员在成员页创建）。 */
const INVITE_ROLES = ['employee', 'auditor']
/** 有效期上限（小时）：720 = 30 天。 */
const MAX_EXPIRES_IN_HOURS = 720

/** JSON 对象键白名单：拒绝可触发原型链污染的键（与 quotas.mjs 同一规则）。 */
function isUnsafeKey(key) {
  return key === '__proto__' || key === 'constructor' || key === 'prototype'
}

function loadInvites(dataDir) {
  try {
    const parsed = JSON.parse(readFileSync(join(dataDir, INVITES_FILE), 'utf8'))
    return parsed !== null && typeof parsed === 'object' && Array.isArray(parsed.invites)
      ? { invites: parsed.invites.filter((i) => i && !isUnsafeKey(Object.keys(i)[0] ?? '')) }
      : { invites: [] }
  } catch {
    return { invites: [] }
  }
}

function saveInvites(dataDir, store) {
  mkdirSync(dataDir, { recursive: true })
  const path = join(dataDir, INVITES_FILE)
  const tmp = `${path}.tmp`
  writeFileSync(tmp, `${JSON.stringify(store, null, 2)}\n`)
  renameSync(tmp, path)
}

const sha256Hex = (text) => createHash('sha256').update(text, 'utf8').digest('hex')

/** 常数时间比较两条等长 hex（不等长先比长度——长度恒定不构成侧信道）。 */
function safeHexEqual(a, b) {
  const bufA = Buffer.from(a, 'hex')
  const bufB = Buffer.from(b, 'hex')
  return bufA.length === bufB.length && timingSafeEqual(bufA, bufB)
}

function expired(invite, now = Date.now()) {
  return Date.parse(invite.expiresAt) < now
}

/**
 * 只读校验一个明文 code：全表逐条常数时间比较 SHA-256，命中后再查
 * 撤销/已用/过期。返回 { ok:true, invite } 或 { ok:false, reason }（reason
 * 为稳定原因码：invalid_code / code_revoked / code_used / code_expired）。
 */
export function validateInvite(dataDir, code, now = Date.now()) {
  if (typeof code !== 'string' || code === '') return { ok: false, reason: 'invalid_code' }
  const digest = sha256Hex(code)
  for (const invite of loadInvites(dataDir).invites) {
    if (typeof invite?.codeHash !== 'string') continue
    if (!safeHexEqual(digest, invite.codeHash)) continue
    // 纵深防御：手改存储造出的 admin 邀请一律按无效处理（createInvite 是
    // 唯一合法入口，角色白名单在那里同样收口）。
    if (!INVITE_ROLES.includes(invite.role)) return { ok: false, reason: 'invalid_code' }
    if (invite.revoked === true) return { ok: false, reason: 'code_revoked' }
    if (invite.used === true) return { ok: false, reason: 'code_used' }
    if (expired(invite, now)) return { ok: false, reason: 'code_expired' }
    return { ok: true, invite }
  }
  return { ok: false, reason: 'invalid_code' }
}

/**
 * 创建邀请：随机明文 code 只在本返回值出现一次，存储只落哈希。
 * role 只允许 employee/auditor；expiresInHours 1–720（缺省 72）。
 * @returns {{ id, code, expiresAt, record }}
 */
export function createInvite(dataDir, { department, role, instanceId, expiresInHours }) {
  if (!INVITE_ROLES.includes(role)) throw new Error(`邀请角色只支持 ${INVITE_ROLES.join('/')}`)
  const hours = expiresInHours === undefined ? 72 : Number(expiresInHours)
  if (!Number.isInteger(hours) || hours < 1 || hours > MAX_EXPIRES_IN_HOURS) {
    throw new Error(`有效期必须是 1–${MAX_EXPIRES_IN_HOURS} 的整数小时`)
  }
  const code = `inv-${randomBytes(24).toString('base64url')}`
  const record = {
    id: `inv-${randomBytes(6).toString('hex')}`,
    codeHash: sha256Hex(code),
    department: department ?? '未分配',
    role,
    instanceId,
    expiresAt: new Date(Date.now() + hours * 3_600_000).toISOString(),
    used: false,
    createdAt: new Date().toISOString(),
  }
  const store = loadInvites(dataDir)
  store.invites.push(record)
  saveInvites(dataDir, store)
  return { id: record.id, code, expiresAt: record.expiresAt, record }
}

/** 撤销未用邀请；不存在/已用/已撤销返回 false（调用方转 400）。 */
export function revokeInvite(dataDir, id) {
  const store = loadInvites(dataDir)
  const invite = store.invites.find((i) => i.id === id)
  if (invite === undefined || invite.used === true || invite.revoked === true) return false
  invite.revoked = true
  invite.revokedAt = new Date().toISOString()
  saveInvites(dataDir, store)
  return true
}

/**
 * 消费一个邀请（注册建号成功后调用）：校验语义同 validateInvite，通过即
 * 原子标记 used/usedBy/consumedAt。调用方必须把「校验→建号→消费」放进同一
 * 串行队列，保证同一 code 的并发注册只有一个能走到这里。
 */
export function consumeInvite(dataDir, code, account) {
  const verdict = validateInvite(dataDir, code)
  if (!verdict.ok) return verdict
  const store = loadInvites(dataDir)
  const invite = store.invites.find((i) => i.id === verdict.invite.id)
  if (invite === undefined || invite.used === true || invite.revoked === true || expired(invite)) {
    return { ok: false, reason: 'code_used' }
  }
  invite.used = true
  invite.usedBy = account
  invite.consumedAt = new Date().toISOString()
  saveInvites(dataDir, store)
  return { ok: true, invite }
}

/** 未撤销未用未过期的邀请展示列表（不含哈希），过期时间升序。 */
export function listOpenInvites(dataDir, now = Date.now()) {
  return loadInvites(dataDir).invites
    .filter((i) => i.revoked !== true && i.used !== true && !expired(i, now))
    .map(({ codeHash, ...open }) => open)
    .sort((a, b) => Date.parse(a.expiresAt) - Date.parse(b.expiresAt))
}

/** 稳定原因码 → 中文文案（注册页与 API 共用）。 */
export function inviteRejectMessage(reason) {
  switch (reason) {
    case 'code_revoked': return '邀请链接已被撤销'
    case 'code_used': return '邀请链接已被使用（每个邀请只能注册一次）'
    case 'code_expired': return '邀请链接已过期，请联系管理员重新生成'
    default: return '邀请链接无效，请核对链接是否完整'
  }
}
