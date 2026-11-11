/**
 * 卡巴格企业平台 · 实例清单加载（清单 + 本地覆盖 + env 插值）。
 *
 * 背景：instances.json 是**被 git 跟踪**的清单文件，而实例 env 里要放
 * 服务令牌（`KABAGE_SERVICE_TOKEN`）这类管理凭据。直接写进清单等于把
 * 凭据提交进仓库（历史上确实发生过：`kbsvc-…` 出现在 instances.json 的
 * 提交里，且已在 git 历史中泄露）。本模块给出不改调用方的解法：
 *
 * 1. **本地覆盖文件** `data/instances.local.json`（data/ 已在 .gitignore
 *    内，不会进仓库）：按实例 id 覆盖 env 字段，用于存放真实令牌等秘密。
 *    加载时与清单合并，清单里的同名键作为缺省。
 * 2. **env 插值**：清单/覆盖里写 `"${MY_TOKEN}"` 会在加载时用进程环境变量
 *    取值（未设置则解析为空串并留下可定位的告警，避免把字面量 `${…}`
 *    当成真值下发到实例）。
 *
 * 设计约束：
 * - 合并是**按实例 id** 的，缺省实例不动；覆盖文件缺失时不报错。
 * - 覆盖文件本身也可能被误提交，故启动时若检测到它的内容出现在
 *   git 跟踪列表里也无法自动补救——靠 .gitignore + 约定来防。
 * - 零依赖，保持 supervisor 的「不引入第三方包」约定。
 */
import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'

/** 覆盖文件名（位于 data/ 下，随 .gitignore 排除）。 */
export const OVERLAY_FILENAME = 'instances.local.json'

/** 解析 `${VAR}` 占位：命中环境变量则替换，未设置则替换为空串并记录警告。 */
function interpolateEnv(value, warnings) {
  if (typeof value !== 'string') return value
  return value.replace(/\$\{([A-Za-z_][A-Za-z0-9_]*)\}/g, (_match, name) => {
    const resolved = process.env[name]
    if (resolved === undefined || resolved === '') {
      warnings.push(`清单中的 \${${name}} 未在环境变量中找到，已按空值处理`)
      return ''
    }
    return resolved
  })
}

/** 深合并 env 字段（覆盖文件优先）。 */
function mergeEnv(base = {}, override = {}) {
  const merged = { ...base }
  for (const [key, value] of Object.entries(override)) {
    merged[key] = value
  }
  return merged
}

/**
 * 加载清单。
 * @param {string} here supervisor 目录（清单所在目录）
 * @returns {{ manifest: object, warnings: string[], overlayPath: string }}
 */
export function loadManifest(here) {
  const manifestPath = join(here, 'instances.json')
  const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'))
  const overlayPath = join(here, 'data', OVERLAY_FILENAME)
  const warnings = []
  if (existsSync(overlayPath)) {
    let overlay = null
    try {
      overlay = JSON.parse(readFileSync(overlayPath, 'utf8'))
    } catch (error) {
      warnings.push(`本地覆盖文件解析失败（已忽略）：${overlayPath} — ${error?.message ?? error}`)
    }
    if (overlay !== null && Array.isArray(overlay.instances)) {
      for (const override of overlay.instances) {
        if (typeof override?.id !== 'string') continue
        const target = manifest.instances?.find((spec) => spec.id === override.id)
        if (target === undefined) {
          warnings.push(`本地覆盖里的实例 ${override.id} 不在清单中，已忽略`)
          continue
        }
        if (override.env !== undefined && override.env !== null) {
          target.env = mergeEnv(target.env ?? {}, override.env)
        }
        // 其余字段（port 等）允许覆盖，但必须显式给出，避免误改。
        for (const key of ['port', 'uid', 'account']) {
          if (override[key] !== undefined) target[key] = override[key]
        }
      }
    }
  }
  // env 插值（清单 + 覆盖合并后统一处理）。
  for (const spec of manifest.instances ?? []) {
    if (spec.env === undefined || spec.env === null) continue
    for (const [key, value] of Object.entries(spec.env)) {
      spec.env[key] = interpolateEnv(value, warnings)
    }
  }
  return { manifest, warnings, overlayPath }
}
