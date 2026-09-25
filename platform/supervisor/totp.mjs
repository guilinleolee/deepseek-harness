/**
 * 卡巴格企业平台 · TOTP 两步验证（栏目规划 v2 阶段 11A）。
 *
 * 纯密码学模块（零 npm 依赖，仅 node:crypto），不含任何 dataDir/账号逻辑：
 * - RFC 4648 base32 编解码（TOTP 密钥的标准文本形态）；
 * - RFC 6238 TOTP（HMAC-SHA1、30 秒步长、缺省 6 位、±1 窗口容错）——
 *   实现以 RFC 6238 附录 B 标准测试向量验收（见 test/twofa-http-verify.mjs）；
 * - AES-256-GCM 加解密：2FA 密钥与 SMTP 密码等敏感配置落盘的唯一形态
 *   （密钥由 auth-secret.key 经 SHA-256 派生，绝不落明文）。
 *
 * 时间安全：验证码比较走 timingSafeEqual；±1 窗口只放宽不收紧；防重放
 * （同一时间片第二次使用）不在本期（硬强制属阶段 11b 时一并收紧）。
 */
import { createHash, createHmac, createCipheriv, createDecipheriv, randomBytes, timingSafeEqual } from 'node:crypto'
import { mkdirSync, readFileSync, renameSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'

const BASE32_ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'

/** RFC 4648 base32 编码（无 padding，TOTP 惯例）。 */
export function base32Encode(bytes) {
  let bits = 0
  let value = 0
  let output = ''
  for (const byte of bytes) {
    value = (value << 8) | byte
    bits += 8
    while (bits >= 5) {
      output += BASE32_ALPHABET[(value >>> (bits - 5)) & 31]
      bits -= 5
    }
  }
  if (bits > 0) output += BASE32_ALPHABET[(value << (5 - bits)) & 31]
  return output
}

/**
 * RFC 4648 base32 解码：大小写不敏感，忽略空格与 `=` padding；遇到字母表
 * 外字符抛错（手抄密钥错字必须显式失败，不能静默得出错误密钥）。
 */
export function base32Decode(text) {
  const clean = String(text ?? '').toUpperCase().replace(/[=\s]/g, '')
  if (clean === '') throw new Error('base32 密钥为空')
  let bits = 0
  let value = 0
  const bytes = []
  for (const ch of clean) {
    const idx = BASE32_ALPHABET.indexOf(ch)
    if (idx === -1) throw new Error(`base32 密钥含非法字符: ${ch}`)
    value = (value << 5) | idx
    bits += 5
    if (bits >= 8) {
      bytes.push((value >>> (bits - 8)) & 0xff)
      bits -= 8
    }
  }
  return Buffer.from(bytes)
}

/**
 * 一个时间片的 TOTP 值。time 为毫秒时间戳；digits/step 可调（RFC 向量用
 * 8 位验收，线上用缺省 6 位）。
 */
export function totp(secretBytes, { time = Date.now(), digits = 6, stepSeconds = 30 } = {}) {
  const counter = Math.floor(time / 1000 / stepSeconds)
  const message = Buffer.alloc(8)
  message.writeBigUInt64BE(BigInt(counter))
  const hmac = createHmac('sha1', secretBytes).update(message).digest()
  const offset = hmac[hmac.length - 1] & 0xf
  const binary = ((hmac[offset] & 0x7f) << 24) | (hmac[offset + 1] << 16) | (hmac[offset + 2] << 8) | hmac[offset + 3]
  return String(binary % 10 ** digits).padStart(digits, '0')
}

/**
 * 校验验证码：±window 窗口内任一时间片命中即通过（常数时间逐片比较，
 * 长度不符直接拒绝）。code 必须是纯数字串。
 */
export function verifyTotp(secretBytes, code, { time = Date.now(), digits = 6, stepSeconds = 30, window = 1 } = {}) {
  if (typeof code !== 'string' || !/^\d+$/.test(code) || code.length !== digits) return false
  const expected = Buffer.from(code, 'utf8')
  for (let drift = -window; drift <= window; drift++) {
    const candidate = Buffer.from(
      totp(secretBytes, { time: time + drift * stepSeconds * 1000, digits, stepSeconds }),
      'utf8',
    )
    if (candidate.length === expected.length && timingSafeEqual(candidate, expected)) return true
  }
  return false
}

/** 生成新密钥：20 随机字节（160 bit，与主流认证器默认兼容）的 base32 文本。 */
export function generateTotpSecret() {
  return base32Encode(randomBytes(20))
}

/** otpauth:// 迁移链接（认证器扫码/手输用；本期页面展示文本与链接）。 */
export function otpauthUrl({ secret, account, issuer = 'Kabage' }) {
  return `otpauth://totp/${encodeURIComponent(issuer)}:${encodeURIComponent(account)}`
    + `?secret=${secret}&issuer=${encodeURIComponent(issuer)}&algorithm=SHA1&digits=6&period=30`
}

/* ── AES-256-GCM 落盘加密（2FA 密钥 / SMTP 密码等敏感配置唯一形态）───────── */

/** 由 auth-secret.key 内容派生 32 字节密钥（同进程内确定性，无需另存盐）。 */
export function deriveKey(authSecret) {
  return createHash('sha256').update(String(authSecret), 'utf8').digest()
}

const ENC_PREFIX = 'enc:v1:'

/** AES-256-GCM 加密 → `enc:v1:<iv b64>:<tag b64>:<data b64>`（自描述，含版本号）。 */
export function encryptText(key, plaintext) {
  const iv = randomBytes(12)
  const cipher = createCipheriv('aes-256-gcm', key, iv)
  const data = Buffer.concat([cipher.update(String(plaintext), 'utf8'), cipher.final()])
  return `${ENC_PREFIX}${iv.toString('base64')}:${cipher.getAuthTag().toString('base64')}:${data.toString('base64')}`
}

/** 解密 enc:v1: 密文；格式不符或认证失败抛错（坏数据必须显式失败）。 */
export function decryptText(key, blob) {
  if (typeof blob !== 'string' || !blob.startsWith(ENC_PREFIX)) {
    throw new Error('密文格式非法（期望 enc:v1: 前缀）')
  }
  const [ivB64, tagB64, dataB64] = blob.slice(ENC_PREFIX.length).split(':')
  if (ivB64 === undefined || tagB64 === undefined || dataB64 === undefined) {
    throw new Error('密文格式非法（期望 iv:tag:data 三段）')
  }
  const decipher = createDecipheriv('aes-256-gcm', key, Buffer.from(ivB64, 'base64'))
  decipher.setAuthTag(Buffer.from(tagB64, 'base64'))
  return Buffer.concat([decipher.update(Buffer.from(dataB64, 'base64')), decipher.final()]).toString('utf8')
}

/* ── data/twofa.json 存储（密钥 AES-GCM 落盘，绝不落明文）────────────────── */

const TWOFA_FILE = 'twofa.json'

function isUnsafeKey(key) {
  return key === '__proto__' || key === 'constructor' || key === 'prototype'
}

function loadTwofaRaw(dataDir) {
  try {
    const parsed = JSON.parse(readFileSync(join(dataDir, TWOFA_FILE), 'utf8'))
    return parsed !== null && typeof parsed === 'object' && !Array.isArray(parsed) ? parsed : {}
  } catch {
    return {}
  }
}

function saveTwofaRaw(dataDir, store) {
  mkdirSync(dataDir, { recursive: true })
  const path = join(dataDir, TWOFA_FILE)
  const tmp = `${path}.tmp`
  writeFileSync(tmp, `${JSON.stringify(store, null, 2)}\n`)
  renameSync(tmp, path)
}

/**
 * 某账号的 2FA 记录（三态，调用方必须区分）：
 * - { state: 'none' }：未绑定（缺文件/缺记录）——按未启用放行；
 * - { state: 'ok', enabled, pending, secret, confirmedAt }：记录可用；
 * - { state: 'broken' }：记录存在但密文解密失败（auth-secret 轮换/文件损坏）
 *   ——**登录路径必须 fail-closed**（不签发 cookie），由管理员救援重置。
 */
export function getTwofaRecord(dataDir, key, account) {
  if (isUnsafeKey(account)) return { state: 'none' }
  const record = loadTwofaRaw(dataDir)[account]
  if (record === undefined || typeof record.encSecret !== 'string') return { state: 'none' }
  let secret
  try {
    secret = decryptText(key, record.encSecret)
  } catch (error) {
    console.error(`[twofa] ${account} 的 2FA 密钥解密失败（记录损坏，需管理员重置）: ${error?.message ?? error}`)
    return { state: 'broken' }
  }
  return {
    state: 'ok',
    enabled: record.enabled === true,
    pending: record.enabled !== true,
    secret,
    confirmedAt: record.confirmedAt ?? null,
  }
}

/** 写入待确认密钥（绑定第一步：setup）。已启用时须先 disable，否则拒绝。 */
export function setPendingSecret(dataDir, key, account, base32Secret) {
  if (isUnsafeKey(account)) throw new Error('非法账号')
  const store = loadTwofaRaw(dataDir)
  const existing = store[account]
  if (existing?.enabled === true) throw new Error('该账号已启用两步验证，请先解绑')
  store[account] = { encSecret: encryptText(key, base32Secret), enabled: false }
  saveTwofaRaw(dataDir, store)
}

/** 确认绑定：验证码通过才 enabled（绑定第二步：confirm）。 */
export function confirmSecret(dataDir, key, account, code) {
  const record = getTwofaRecord(dataDir, key, account)
  if (record.state === 'broken') return { ok: false, reason: 'broken' }
  if (record.state === 'none') return { ok: false, reason: 'not_started' }
  if (!verifyTotp(base32Decode(record.secret), code)) return { ok: false, reason: 'bad_code' }
  const store = loadTwofaRaw(dataDir)
  store[account] = { encSecret: encryptText(key, record.secret), enabled: true, confirmedAt: new Date().toISOString() }
  saveTwofaRaw(dataDir, store)
  return { ok: true }
}

/** 解绑（本人验密码后或 admin 救援共用原语）：删除整条记录。 */
export function clearTwofa(dataDir, account) {
  if (isUnsafeKey(account)) return false
  const store = loadTwofaRaw(dataDir)
  if (store[account] === undefined) return false
  delete store[account]
  saveTwofaRaw(dataDir, store)
  return true
}

/** 登录时校验：仅 enabled 记录参与验证；未绑定/待确认/**损坏**一律 false（fail-closed）。 */
export function verifyTwofaForLogin(dataDir, key, account, code) {
  const record = getTwofaRecord(dataDir, key, account)
  if (record.state !== 'ok' || record.enabled !== true) return false
  return verifyTotp(base32Decode(record.secret), code)
}

/** 某账号是否已启用（损坏/未绑定均 false；登录分支须用 getTwofaRecord 区分三态）。 */
export function isTwofaEnabled(dataDir, key, account) {
  const record = getTwofaRecord(dataDir, key, account)
  return record.state === 'ok' && record.enabled === true
}
