/**
 * 卡巴格企业平台 · 登录安全（栏目规划 v2 第五节）。
 *
 * data/security.json 保存可调参数，缺省自动生成；密码策略应用于控制台
 * 建号设密与重置密码（存量账号在下次变更时生效）；登录速率限制按「账号+IP」
 * 滑动窗口计数，达阈值锁定，成功登录清零。计数桶经 {dataDir, file} 持久化
 * 到 data/ 下的 JSON（fail/success/触发锁定时原子落盘），daemon 重启不清零；
 * 不传持久化参数则保持纯内存行为（测试用）。审计轮转按 auditRotateBytes
 * 大小切档、保留 auditKeepArchives 份归档（参数同样在本文件，audit.mjs
 * 每次追加现读）。全部参数可经 data/security.json 修改，改动即时生效。
 */
import { mkdirSync, readFileSync, renameSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'

/** 缺省安全参数（与 data/security.json 的自动生成内容一致）。 */
export const DEFAULT_SECURITY = {
  loginWindowMinutes: 15,
  loginMaxFails: 10,
  accountMaxFails: 50,
  lockoutMinutes: 15,
  passwordMinLength: 8,
  passwordMinClasses: 3,
  auditRotateBytes: 16_777_216,
  auditKeepArchives: 4,
  require2faRoles: [],
}

/** 各参数的合法整数区间（保存时校验，越界即拒）。 */
const RANGES = {
  loginWindowMinutes: [1, 1440],
  loginMaxFails: [1, 100],
  accountMaxFails: [5, 500],
  lockoutMinutes: [1, 1440],
  passwordMinLength: [6, 128],
  passwordMinClasses: [1, 3],
  auditRotateBytes: [1_024, 1_073_741_824],
  auditKeepArchives: [1, 100],
}

const SECURITY_ROLES = ['admin', 'auditor', 'employee']

const validValue = (key, value) =>
  Number.isInteger(value) && value >= RANGES[key][0] && value <= RANGES[key][1]

/** require2faRoles 归一化：只保留合法角色名并去重（保持传入顺序）。 */
const normalizeRoles = (value) => {
  if (!Array.isArray(value)) return null
  const seen = new Set()
  for (const role of value) {
    if (!SECURITY_ROLES.includes(role)) return null
    seen.add(role)
  }
  return SECURITY_ROLES.filter((role) => seen.has(role))
}

function writeConfig(dataDir, config) {
  const path = join(dataDir, 'security.json')
  const tmp = `${path}.tmp`
  writeFileSync(tmp, `${JSON.stringify(config, null, 2)}\n`)
  renameSync(tmp, path)
}

/** 读取安全参数；文件缺失时生成缺省配置，手改出的非法值回退缺省并重写。 */
export function loadSecurityConfig(dataDir) {
  mkdirSync(dataDir, { recursive: true })
  const file = join(dataDir, 'security.json')
  let stored = null
  try {
    stored = JSON.parse(readFileSync(file, 'utf8'))
  } catch {
    stored = null
  }
  if (stored === null || typeof stored !== 'object' || Array.isArray(stored)) {
    writeConfig(dataDir, { ...DEFAULT_SECURITY })
    return { ...DEFAULT_SECURITY }
  }
  let dirty = false
  const config = { ...DEFAULT_SECURITY, require2faRoles: [] }
  for (const key of Object.keys(RANGES)) {
    const value = stored[key]
    if (validValue(key, value)) config[key] = value
    else if (value !== undefined) dirty = true
  }
  if (stored.require2faRoles !== undefined) {
    const roles = normalizeRoles(stored.require2faRoles)
    if (roles !== null) config.require2faRoles = roles
    else dirty = true
  }
  if (dirty) {
    console.error('[security] security.json 存在非法参数值，已回退缺省并重写')
    writeConfig(dataDir, config)
  }
  return config
}

/**
 * 合并保存安全参数（patch 允许只传部分键）。未知键/非整数/越界抛错
 * （调用方转成 400 并留审计），校验通过才原子落盘。返回保存后的完整配置。
 */
export function saveSecurityConfig(dataDir, patch) {
  const current = loadSecurityConfig(dataDir)
  const next = { ...current }
  for (const [key, value] of Object.entries(patch ?? {})) {
    if (key === 'require2faRoles') {
      const roles = normalizeRoles(value)
      if (roles === null) throw new Error('require2faRoles 必须是由 admin/auditor/employee 组成的数组')
      next.require2faRoles = roles
      continue
    }
    if (!(key in DEFAULT_SECURITY)) throw new Error(`未知安全参数: ${key}`)
    if (!validValue(key, value)) {
      throw new Error(`${key} 必须是 ${RANGES[key][0]}–${RANGES[key][1]} 之间的整数`)
    }
    next[key] = value
  }
  writeConfig(dataDir, next)
  return next
}

/**
 * 密码策略：长度 ≥ passwordMinLength；大写/小写/数字至少含 passwordMinClasses
 * 类；不得与账号名相同（大小写不敏感）。config 缺省用 DEFAULT_SECURITY，
 * 调用方一般传 loadSecurityConfig 的结果。
 * @returns {{ok:true} | {ok:false, message:string}} message 为可直接展示的中文文案。
 */
export function checkPasswordPolicy(password, account, config = DEFAULT_SECURITY) {
  if (typeof password !== 'string' || password.length === 0) return { ok: false, message: '密码不能为空' }
  const minLength = config.passwordMinLength ?? DEFAULT_SECURITY.passwordMinLength
  if (password.length < minLength) return { ok: false, message: `密码长度至少 ${minLength} 位` }
  if (account && password.toLowerCase() === String(account).toLowerCase()) {
    return { ok: false, message: '密码不能与账号名相同' }
  }
  const minClasses = config.passwordMinClasses ?? DEFAULT_SECURITY.passwordMinClasses
  const classes = [/[a-z]/, /[A-Z]/, /[0-9]/].filter((re) => re.test(password)).length
  if (classes < minClasses) {
    return { ok: false, message: `密码需至少包含大写字母、小写字母、数字中的 ${minClasses} 类` }
  }
  return { ok: true }
}

/** 生成满足缺省策略的随机密码（延续 LyZ- 前缀格式，保证三类字符齐备）。 */
export function generatePassword() {
  const body = Math.random().toString(36).slice(2, 11)
  const digit = /[0-9]/.test(body) ? '' : String(Math.floor(Math.random() * 10))
  return `LyZ-${(body + digit).slice(0, 10)}`
}

/**
 * 登录速率限制（内存滑动窗口 + 可选文件持久化）。getLimits 在每次判定时取
 * 当前参数（管理台改动即时生效），返回 { windowMs, maxFails, accountMaxFails,
 * lockoutMs }。语义：windowMs 内第 maxFails 次失败即锁定 lockoutMs，锁定
 * 期满重新计数，锁定中不续期；成功登录清零该「账号+IP」。
 * 双层桶：除「账号+IP」桶外，同一账号跨全部 IP 的失败计入「账号|*」全局桶
 * （阈值 accountMaxFails，分布式撞库封口）；account 为空的桶（注册限流）
 * 不设全局桶。persistence = { dataDir, file } 时：创建时从 dataDir/file 载入
 * 计数桶（丢弃已过期条目），fail/success/触发锁定即原子落盘——daemon 崩溃
 * 重启后锁定与失败计数存活；落盘失败降级 stderr，不影响内存判定。
 */
export function createLoginRateGuard(getLimits, persistence = null) {
  const attempts = new Map() // "account|ip" / "account|*" -> { fails: number[], lockedUntil?: number }
  const keyOf = (account, ip) => `${account}|${ip ?? '-'}`
  const limits = () => {
    const raw = getLimits?.() ?? {}
    return {
      windowMs: Number.isFinite(raw.windowMs) && raw.windowMs > 0 ? raw.windowMs : 15 * 60_000,
      maxFails: Number.isInteger(raw.maxFails) && raw.maxFails > 0 ? raw.maxFails : 10,
      accountMaxFails: Number.isInteger(raw.accountMaxFails) && raw.accountMaxFails > 0 ? raw.accountMaxFails : 50,
      lockoutMs: Number.isFinite(raw.lockoutMs) && raw.lockoutMs > 0 ? raw.lockoutMs : 15 * 60_000,
    }
  }
  if (persistence !== null) {
    try {
      const parsed = JSON.parse(readFileSync(join(persistence.dataDir, persistence.file), 'utf8'))
      const now = Date.now()
      for (const [key, entry] of Object.entries(parsed?.buckets ?? {})) {
        if (entry === null || typeof entry !== 'object') continue
        const fails = Array.isArray(entry.fails) ? entry.fails.filter(Number.isFinite) : []
        const lockedUntil = Number.isFinite(entry.lockedUntil) ? entry.lockedUntil : undefined
        if (fails.length === 0 && !(lockedUntil > now)) continue
        attempts.set(key, lockedUntil === undefined ? { fails } : { fails, lockedUntil })
      }
    } catch { /* 文件缺失或损坏：从空计数开始（等价于清零语义的降级） */ }
  }
  const persist = () => {
    if (persistence === null) return
    const now = Date.now()
    const buckets = {}
    for (const [key, entry] of attempts) {
      const live = entry.fails.length > 0 || (Number.isFinite(entry.lockedUntil) && entry.lockedUntil > now)
      if (live) buckets[key] = entry
    }
    try {
      const path = join(persistence.dataDir, persistence.file)
      const tmp = `${path}.tmp`
      writeFileSync(tmp, `${JSON.stringify({ buckets }, null, 2)}\n`)
      renameSync(tmp, path)
    } catch (error) {
      console.error('[security] 限流计数持久化失败（内存判定不受影响）:', error?.message ?? error)
    }
  }
  const entryOf = (key) => {
    let entry = attempts.get(key)
    if (entry === undefined) {
      entry = { fails: [] }
      attempts.set(key, entry)
    }
    return entry
  }

  return {
    /** 判定是否允许本次登录尝试，返回 {allowed, retryAfterMinutes}。 */
    check(account, ip) {
      const { windowMs, maxFails, accountMaxFails, lockoutMs } = limits()
      const now = Date.now()
      const evaluate = (key, cap) => {
        const entry = attempts.get(key)
        if (entry === undefined) return { allowed: true, retryAfterMinutes: 0 }
        if (Number.isFinite(entry.lockedUntil) && entry.lockedUntil > now) {
          return { allowed: false, retryAfterMinutes: Math.max(1, Math.ceil((entry.lockedUntil - now) / 60_000)) }
        }
        entry.fails = entry.fails.filter((t) => now - t < windowMs)
        if (entry.fails.length >= cap) {
          // 窗口内失败已达阈值但尚未锁定（如阈值被调小）：立即锁定。
          entry.lockedUntil = now + lockoutMs
          entry.fails = []
          persist()
          return { allowed: false, retryAfterMinutes: Math.max(1, Math.ceil(lockoutMs / 60_000)) }
        }
        return { allowed: true, retryAfterMinutes: 0 }
      }
      const perBucket = evaluate(keyOf(account, ip), maxFails)
      if (!perBucket.allowed) return perBucket
      if (account === '') return perBucket
      // 账号级全局桶：跨 IP 分布式撞库在 accountMaxFails 处封口。
      return evaluate(`${account}|*`, accountMaxFails)
    },
    /** 记一次失败；达阈值即锁定并清空窗口计数（锁定期满后重新开始）。 */
    fail(account, ip) {
      const { windowMs, maxFails, accountMaxFails, lockoutMs } = limits()
      const now = Date.now()
      const record = (key, cap) => {
        const entry = entryOf(key)
        if (Number.isFinite(entry.lockedUntil) && entry.lockedUntil > now) return
        entry.fails = entry.fails.filter((t) => now - t < windowMs)
        entry.fails.push(now)
        if (entry.fails.length >= cap) {
          entry.lockedUntil = now + lockoutMs
          entry.fails = []
        }
      }
      record(keyOf(account, ip), maxFails)
      if (account !== '') record(`${account}|*`, accountMaxFails)
      persist()
    },
    /** 登录成功：清零该「账号+IP」的失败计数与锁定（含账号级全局桶）。 */
    success(account, ip) {
      const had = attempts.delete(keyOf(account, ip))
      const hadGlobal = account !== '' && attempts.delete(`${account}|*`)
      if (had || hadGlobal) persist()
    },
  }
}
