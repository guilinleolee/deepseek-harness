/**
 * 卡巴格企业平台 · 实例凭据落盘（Top10 #1「vkey 最后一公里」）。
 *
 * 背景：虚拟钥匙（vkey）明文此前只在签发响应/CLI 输出里出现一次，靠人工
 * 抄写进实例 home 的 .credentials.yaml——遗忘即钥匙作废。本模块在签发时刻
 * 自动把明文合并写入 data/homes/<实例id>/.credentials.yaml 的 refs 段：
 *
 *   version: 1
 *   refs:
 *     LYZ_VIRTUAL_KEY: vk-…
 *   records:            ← 原样保留（实例侧登录态等既有凭据）
 *     client-connection/browser-session:
 *       kind: grant
 *       payload: …
 *
 * 原则：零依赖（纯字符串行级合并，不引 YAML 库）；writeFileAtomic 原子写；
 * 任何失败都降级为 { ok:false, reason } 返回值——签发方（建号/启用/导入/
 * 签发页/注册/CLI）不因此中断，明文仍在响应里仅此一次可见。审计与 JSON
 * 存储绝不落明文（隐私红线），本模块只写实例 home 这一个位置。
 */
import { mkdirSync, readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { writeFileAtomic } from './atomic-write.mjs'

/** 实例 home 凭据文件路径（与 toolpolicy 的 homes/<id> 约定一致）。 */
export function instanceCredentialsPath(dataDir, instanceId) {
  return join(dataDir, 'homes', instanceId, '.credentials.yaml')
}

/** YAML 纯量落位：安全字符直接裸写，其余双引号转义（值永远单行）。 */
function yamlScalar(value) {
  const s = String(value)
  return /^[\w.\-/+=:]+$/.test(s) ? s : `"${s.replace(/\\/g, '\\\\').replace(/"/g, '\\"')}"`
}

/**
 * 把 refs.<refName> 合并进既有凭据文本（纯函数，便于测试）。
 * - 无既有内容 → 生成 version:1 + refs 骨架；
 * - 已有 refs 块 → 原位替换/插入该键，其余行（含 records）逐字节保留；
 * - 无 refs 块 → 在文件尾追加 refs 段。
 * refName 限 ^[A-Za-z_][A-Za-z0-9_]*$（键名来自代码常量，防御性校验）。
 */
export function mergeCredentialsYaml(existingText, refName, refValue) {
  if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(refName ?? '')) throw new Error(`非法的凭据引用名: ${refName}`)
  if (typeof refValue !== 'string' || refValue === '') throw new Error('凭据值不能为空')
  const valueLine = yamlScalar(refValue)
  if (typeof existingText !== 'string' || existingText.trim() === '') {
    return `version: 1\nrefs:\n  ${refName}: ${valueLine}\n`
  }
  const hadTrailingNewline = existingText.endsWith('\n')
  const lines = (hadTrailingNewline ? existingText.slice(0, -1) : existingText).split('\n')
  const refsIdx = lines.findIndex((l) => l === 'refs:')
  if (refsIdx === -1) {
    lines.push('refs:', `  ${refName}: ${valueLine}`)
    return `${lines.join('\n')}\n`
  }
  // refs 块范围：refs: 下一行起，直到下一个顶层（顶格）非空行。
  let end = refsIdx + 1
  while (end < lines.length && (lines[end] === '' || lines[end].startsWith(' '))) end += 1
  const keyRe = new RegExp(`^  ${refName}:`)
  for (let i = refsIdx + 1; i < end; i += 1) {
    if (keyRe.test(lines[i])) { lines[i] = `  ${refName}: ${valueLine}`; return `${lines.join('\n')}${hadTrailingNewline ? '\n' : ''}` }
  }
  lines.splice(end, 0, `  ${refName}: ${valueLine}`)
  return `${lines.join('\n')}${hadTrailingNewline ? '\n' : ''}`
}

/**
 * 把一份凭据引用写入实例 home（尽力而为，绝不抛错）。
 * 返回 { ok:true, path } 或 { ok:false, reason }。
 */
export function writeInstanceCredentials(dataDir, instanceId, refName, refValue) {
  try {
    if (typeof instanceId !== 'string' || !/^[A-Za-z0-9-]+$/.test(instanceId)) return { ok: false, reason: 'invalid_instance_id' }
    const path = instanceCredentialsPath(dataDir, instanceId)
    let existing
    try {
      existing = readFileSync(path, 'utf8')
    } catch (error) {
      if (error?.code !== 'ENOENT') return { ok: false, reason: 'read_failed' }
      existing = undefined
    }
    const merged = mergeCredentialsYaml(existing, refName, refValue)
    mkdirSync(dirname(path), { recursive: true })
    writeFileAtomic(path, merged)
    return { ok: true, path }
  } catch (error) {
    // Windows EPERM（文件被占用）等：降级为手动流程，签发响应仍含明文。
    return { ok: false, reason: String(error?.message ?? error) }
  }
}

/** 虚拟钥匙专用：把 vk-… 明文写进实例 home 的 LYZ_VIRTUAL_KEY。 */
export function writeVkeyToHome(dataDir, instanceId, token) {
  return writeInstanceCredentials(dataDir, instanceId, 'LYZ_VIRTUAL_KEY', token)
}
