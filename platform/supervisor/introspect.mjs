/**
 * 落云宗企业平台 · 漂移对齐（任务书阶段 5）。
 *
 * 授权集（GrantedSet，管理端应为）：模型 = 该实例账号虚拟钥匙的白名单
 * （'*' 展开为上游表全集）；插件 = data/plugins.json 的期望清单（阶段 6）。
 * 实际生效集（EffectiveSet，实例自报）：从实例 home 磁盘内省——
 * provider 路由声明的模型 + profile 已安装的第三方插件及版本。
 * （home 即实例启动时的组卷事实来源；运行时 boot 失败类漂移由阶段 6 的
 * 真启动预检拦截，见该篇说明。）
 *
 * 比对结果持久化在 data/drift.json：持续存在的差异保留首次发现时间，
 * 超过时限（manifest.driftStaleHours，默认 24 小时）即标记 STALE（红）——
 * 即任务书验收的「比对页按时限标红」。
 */
import { existsSync, readFileSync, writeFileSync, renameSync } from 'node:fs'
import { join } from 'node:path'

/** 粗读实例 settings.yaml 里各 provider 路由声明的模型 id（行级解析，格式由平台管理）。 */
export function effectiveModels(home) {
  const file = join(home, 'settings.yaml')
  if (!existsSync(file)) return []
  const models = new Set()
  let inProviders = false
  let providerDepth = -1
  for (const line of readFileSync(file, 'utf8').split('\n')) {
    const indent = line.match(/^(\s*)/)[1].length
    const trimmed = line.trim()
    if (trimmed === '' || trimmed.startsWith('#')) continue
    if (trimmed === 'providers:') { inProviders = true; providerDepth = indent; continue }
    if (inProviders && indent <= providerDepth && trimmed !== '') { inProviders = false; continue }
    if (!inProviders) continue
    const id = trimmed.match(/^-\s+id:\s*(.+)$/)
    if (id) models.add(id[1].trim())
  }
  return [...models]
}

/** 实例 profile 已安装的第三方插件（依赖即插件；键 = 名，值 = 安装 spec）。 */
export function effectivePlugins(home, profileName = 'web') {
  const file = join(home, 'profiles', profileName, 'package.json')
  if (!existsSync(file)) return []
  try {
    const manifest = JSON.parse(readFileSync(file, 'utf8'))
    return Object.entries(manifest.dependencies ?? {}).map(([name, spec]) => ({ name, spec }))
  } catch {
    return []
  }
}

export function grantedModels(vkeyModels, upstreams) {
  if (vkeyModels === '*') {
    const all = new Set()
    for (const u of upstreams.filter((x) => !x.revoked)) for (const m of u.models) all.add(m)
    return [...all]
  }
  return vkeyModels
}

/**
 * 比对并合并漂移状态：仍在的差异保留首次 detectedAt（时限从首次发现起算），
 * 已消失的差异移除。返回 { diffs, checkedAt }。
 */
export function mergeDiffs(previousDiffs, currentDiffs, now = Date.now()) {
  const kept = new Map(previousDiffs?.map((d) => [`${d.kind}:${d.detail}`, d.detectedAt] ?? []))
  return currentDiffs.map((d) => ({
    ...d,
    detectedAt: kept.get(`${d.kind}:${d.detail}`) ?? new Date(now).toISOString(),
  }))
}

export function compareSets(granted, effective, kindPrefix) {
  const diffs = []
  for (const item of granted) if (!effective.includes(item)) diffs.push({ kind: `${kindPrefix}-missing`, detail: item })
  for (const item of effective) if (!granted.includes(item)) diffs.push({ kind: `${kindPrefix}-extra`, detail: item })
  return diffs
}

export function loadDriftState(dataDir) {
  try {
    return JSON.parse(readFileSync(join(dataDir, 'drift.json'), 'utf8'))
  } catch {
    return { checks: {} }
  }
}

export function saveDriftState(dataDir, state) {
  const path = join(dataDir, 'drift.json')
  const tmp = `${path}.tmp`
  writeFileSync(tmp, `${JSON.stringify(state, null, 2)}\n`)
  renameSync(tmp, path)
}
