/**
 * 卡巴格企业平台 · 配额点数与倍率（栏目规划 v2 第六节）。
 *
 * 单位：点。消耗点 = (输入 tokens × 模型倍率 + 输出 tokens × 模型倍率 × 补全倍率) × 分组倍率。
 * 倍率存 data/ratios.json：未配置模型 ratio=1、completionRatio=defaultCompletionRatio（缺省 3，
 * 对齐主流对话模型输出/输入价格比）、未配置部门 groupRatio=1；非法值（≤0/非有限数）在写入时
 * 拒绝、在手改文件读取时剔除并重写。
 *
 * 读取走 mtime 缓存（relay 每请求调用，改动 ≤ 下一请求生效）；daemon 单进程承载
 * 网关/管理台/Relay，initQuotas 在建服时配置一次目录（写入口按 dataDir 幂等初始化）。
 */
import { mkdirSync, readFileSync, renameSync, statSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'

const RATIOS_FILE = 'ratios.json'

/** 缺省倍率配置（与 data/ratios.json 的自动生成内容一致）。 */
export const DEFAULT_RATIOS = { models: {}, defaultCompletionRatio: 3, groups: {} }

/** 缺省倍率下的计点参数（tokensToPoints 的 ratios 缺省值）。 */
export const DEFAULT_RATIO_SET = { ratio: 1, completionRatio: DEFAULT_RATIOS.defaultCompletionRatio, groupRatio: 1 }

let ratiosDir = null
const cache = { file: null, mtime: -1, value: null }

const validPositive = (value) => typeof value === 'number' && Number.isFinite(value) && value > 0

/** JSON 对象键白名单：拒绝可触发原型链污染的键（写入抛错、读取剔除）。 */
export function isUnsafeKey(key) {
  return key === '__proto__' || key === 'constructor' || key === 'prototype'
}

/** 配置倍率数据目录（relay 建服时调用；写入口也会以 dataDir 幂等初始化）。 */
export function initQuotas(dataDir) {
  if (ratiosDir === dataDir) return
  mkdirSync(dataDir, { recursive: true })
  ratiosDir = dataDir
  cache.file = null
  cache.value = null
}

function writeRatiosFile(file, ratios) {
  const tmp = `${file}.tmp`
  writeFileSync(tmp, `${JSON.stringify(ratios, null, 2)}\n`)
  renameSync(tmp, file)
  cache.file = file
  cache.mtime = statSync(file).mtimeMs
  cache.value = ratios
}

/** 归一化：只保留合法倍率；手改出的非法值剔除并标 dirty（重写回干净形态）。 */
function normalizeRatios(parsed, missing) {
  const ratios = { models: {}, defaultCompletionRatio: DEFAULT_RATIOS.defaultCompletionRatio, groups: {} }
  let dirty = false
  if (missing) return { ratios, dirty: false }
  if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) return { ratios, dirty: true }
  if (parsed.defaultCompletionRatio !== undefined) {
    if (validPositive(parsed.defaultCompletionRatio)) ratios.defaultCompletionRatio = parsed.defaultCompletionRatio
    else dirty = true
  }
  if (parsed.models !== undefined) {
    if (parsed.models !== null && typeof parsed.models === 'object' && !Array.isArray(parsed.models)) {
      for (const [model, conf] of Object.entries(parsed.models)) {
        if (!isUnsafeKey(model) && conf !== null && typeof conf === 'object' && validPositive(conf.ratio) && validPositive(conf.completionRatio)) {
          ratios.models[model] = { ratio: conf.ratio, completionRatio: conf.completionRatio }
        } else {
          dirty = true
        }
      }
    } else {
      dirty = true
    }
  }
  if (parsed.groups !== undefined) {
    if (parsed.groups !== null && typeof parsed.groups === 'object' && !Array.isArray(parsed.groups)) {
      for (const [department, ratio] of Object.entries(parsed.groups)) {
        if (!isUnsafeKey(department) && validPositive(ratio)) ratios.groups[department] = ratio
        else dirty = true
      }
    } else {
      dirty = true
    }
  }
  return { ratios, dirty }
}

/** mtime 缓存读取 ratios.json；缺省自动生成，非法配置剔除后重写。 */
export function loadRatios() {
  if (ratiosDir === null) throw new Error('quotas 未初始化数据目录（需先 initQuotas）')
  const file = join(ratiosDir, RATIOS_FILE)
  let mtime = null
  try {
    mtime = statSync(file).mtimeMs
  } catch {
    mtime = null
  }
  if (mtime !== null && cache.file === file && cache.mtime === mtime && cache.value !== null) return cache.value
  let parsed = null
  const missing = mtime === null
  if (!missing) {
    try {
      parsed = JSON.parse(readFileSync(file, 'utf8'))
    } catch {
      parsed = null
    }
  }
  const { ratios, dirty } = normalizeRatios(parsed, missing)
  if (missing || dirty) {
    if (dirty && !missing) console.error('[quotas] ratios.json 存在非法倍率配置，已剔除并重写')
    writeRatiosFile(file, ratios)
  }
  return ratios
}

/**
 * 解析某模型+部门的生效倍率。未配置模型 ratio=1、completionRatio=defaultCompletionRatio；
 * 未配置（或未传）部门 groupRatio=1。读取键同样过原型链污染白名单：
 * 危险键一律视为未配置（否则 groups['__proto__'] 会命中原型 getter 返回非数值倍率）。
 */
export function resolveRatios(modelId, department) {
  const ratios = loadRatios()
  const safeModel = modelId !== null && modelId !== undefined && !isUnsafeKey(modelId) ? modelId : undefined
  const safeDepartment = department !== null && department !== undefined && !isUnsafeKey(department) ? department : undefined
  const modelConf = safeModel !== undefined ? ratios.models[safeModel] : undefined
  return {
    ratio: modelConf?.ratio ?? 1,
    completionRatio: modelConf?.completionRatio ?? ratios.defaultCompletionRatio,
    groupRatio: safeDepartment !== undefined ? (ratios.groups[safeDepartment] ?? 1) : 1,
  }
}

/**
 * tokens → 点数：(输入 × 模型倍率 + 输出 × 模型倍率 × 补全倍率) × 分组倍率。
 * 非有限输入按 0 计。
 */
export function tokensToPoints(inTokens, outTokens, ratios = DEFAULT_RATIO_SET) {
  const modelRatio = ratios?.ratio ?? 1
  const completionRatio = ratios?.completionRatio ?? DEFAULT_RATIO_SET.completionRatio
  const groupRatio = ratios?.groupRatio ?? 1
  const inPoints = (Number.isFinite(inTokens) ? inTokens : 0) * modelRatio
  const outPoints = (Number.isFinite(outTokens) ? outTokens : 0) * modelRatio * completionRatio
  return (inPoints + outPoints) * groupRatio
}

/** 预扣估点：与实结同一公式，只是输入为估算 tokens（估输入=ceil(字符数/4)、估输出=max_tokens）。 */
export function estimatePoints(estInTokens, estOutTokens, ratios = DEFAULT_RATIO_SET) {
  return tokensToPoints(estInTokens, estOutTokens, ratios)
}

/** 点数展示：整数不带小数点，其余最多 6 位小数。 */
export function fmtPoints(value) {
  const x = Number(value)
  const safe = Number.isFinite(x) ? x : 0
  return Number.isInteger(safe) ? String(safe) : String(Math.round(safe * 1e6) / 1e6)
}

function round6(x) {
  return Math.round(x * 1e6) / 1e6
}

/**
 * 设置模型倍率（模型页行内编辑）。ratio/completionRatio 必须 >0 且有限，否则抛错
 * （调用方转 400）；不落脏数据。返回写入后的该模型配置。
 */
export function setModelRatio(dataDir, model, { ratio, completionRatio }) {
  initQuotas(dataDir)
  const trimmed = typeof model === 'string' ? model.trim() : ''
  if (trimmed === '' || isUnsafeKey(trimmed)) throw new Error('非法模型 ID')
  if (!validPositive(ratio)) throw new Error('倍率必须是大于 0 的数字')
  if (!validPositive(completionRatio)) throw new Error('补全倍率必须是大于 0 的数字')
  const file = join(ratiosDir, RATIOS_FILE)
  const ratios = loadRatios()
  const next = { ratio: round6(ratio), completionRatio: round6(completionRatio) }
  ratios.models[trimmed] = next
  writeRatiosFile(file, ratios)
  return next
}

/** 设置部门分组倍率（部门与角色页行内编辑）。校验与落盘语义同 setModelRatio。 */
export function setGroupRatio(dataDir, department, ratio) {
  initQuotas(dataDir)
  const trimmed = typeof department === 'string' ? department.trim() : ''
  if (trimmed === '' || isUnsafeKey(trimmed)) throw new Error('非法部门名')
  if (!validPositive(ratio)) throw new Error('分组倍率必须是大于 0 的数字')
  const file = join(ratiosDir, RATIOS_FILE)
  const ratios = loadRatios()
  ratios.groups[trimmed] = round6(ratio)
  writeRatiosFile(file, ratios)
  return round6(ratio)
}
