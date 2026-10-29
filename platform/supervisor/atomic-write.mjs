/**
 * 卡巴格企业平台 · 原子写 helper（Windows 稳健版）。
 *
 * 背景：平台所有状态文件（accounts.json / vkeys.json / usage.json / invites.json /
 * rate-limits.json / audit 段文件 / role-matrix.json / tool-policy 等）此前都写成
 * 「先写 <path>.tmp，再 renameSync 覆盖原文件」。在 Windows 上 rename 覆盖一个
 * **正被其它进程打开** 的目标文件会抛 EPERM（杀软实时扫描、索引器、编辑器、
 * 以及 CLI 与 daemon 两个进程并发写同一文件都会撞上）。实测症状：
 * 注册流程在写 vkeys.json 时报 `EPERM: rename ... vkeys.json.tmp -> vkeys.json`，
 * 整个建号/注册动作失败（500），而邀请码未被消费——用户看到的是「偶发注册失败」。
 *
 * 本模块提供两件事：
 * 1. **重试**：rename 遇到 Windows 常见的瞬时占用错误（EPERM/EBUSY/EACCES/
 *    ENOTEMPTY/EEXIST）时做指数退避重试，吞掉「目标文件刚好被占用」这类抖动。
 *    重试仍失败才抛错，并把底层 code 带进中文错误信息（便于运维定位）。
 * 2. **跨进程唯一 tmp 名**：tmp 文件名带 pid，避免 daemon 与 CLI 同时写同一状态
 *    文件时互相把对方的 tmp 抢走（固定 `<path>.tmp` 时会互相 rename 到对方的内容，
 *    表现为随机的 ENOENT 或数据串号）。同进程内两个写点并发写同一文件时，
 *    对方的 rename 可能带走本进程的 tmp（ENOENT）——写 tmp 置于重试循环内，
 *    ENOENT 时重写一次再 rename 即可自愈。
 *
 * 语义保持不变：仍然先写 tmp 再 rename（rename 在同目录同卷内是原子的），
 * 读者永远看不到写了一半的文件。失败路径会清理自己的 tmp，避免残留垃圾。
 */
import { renameSync, unlinkSync, writeFileSync } from 'node:fs'

/** Windows 上「目标文件瞬时被占用」的典型 errno —— 值得重试而不是立刻失败。 */
const RETRYABLE_CODES = new Set(['EPERM', 'EBUSY', 'EACCES', 'ENOTEMPTY', 'EEXIST'])

/** 同步退避等待（毫秒）。用 Atomics.wait 实现，不依赖定时器，保持同步函数语义。 */
const sleep = (ms) => {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms)
}

/**
 * 原子写文件。
 * @param {string} path 目标路径
 * @param {string|Buffer} contents 内容
 * @param {{retries?: number, baseDelayMs?: number}} [options]
 *   retries      rename 失败后的重试次数（默认 5）
 *   baseDelayMs  首次退避基数（默认 15ms），按 2 的幂递增
 */
export function writeFileAtomic(path, contents, options = {}) {
  const retries = Number.isInteger(options.retries) ? options.retries : 5
  const baseDelayMs = Number.isInteger(options.baseDelayMs) ? options.baseDelayMs : 15
  // 跨进程唯一 tmp 名：同 pid 同毫秒内连续写也不会撞（后写者覆盖前者的 tmp，
  // 但 rename 是最后一步，前者的内容此时要么已就位要么已被完整 rename 掉）。
  const tmp = `${path}.${process.pid}.tmp`
  let lastError = null
  for (let attempt = 0; attempt <= retries; attempt += 1) {
    try {
      // 写 tmp 放在重试循环内：同进程并发写同一文件时，对方的 rename 可能把
      // 我们的 tmp 带走（ENOENT），重写一次即可继续（内容一致，无副作用）。
      writeFileSync(tmp, contents)
      renameSync(tmp, path)
      return
    } catch (error) {
      lastError = error
      const retryable = RETRYABLE_CODES.has(error?.code)
      if (!retryable || attempt === retries) break
      sleep(baseDelayMs * 2 ** attempt)
    }
  }
  // 失败清理自己的 tmp（清理失败不掩盖主错误）。
  try { unlinkSync(tmp) } catch { /* 残留 tmp 由后续写覆盖或人工清理 */ }
  const code = lastError?.code ?? 'unknown'
  // 中文包装 + 保留底层 errno：调用方要能按 error.code 分支
  // （写阶段失败多为 ENOENT/EPERM，rename 阶段多为 EPERM/EACCES）。
  const wrapped = new Error(`原子写入失败（${code}）: ${path} — ${lastError?.message ?? lastError}`)
  if (code !== 'unknown') wrapped.code = code
  throw wrapped
}

/**
 * 原子写 JSON（与平台既有格式一致：2 空格缩进 + 末尾换行）。
 * @param {string} path 目标路径
 * @param {unknown} value 可 JSON 序列化的值
 * @param {{retries?: number, baseDelayMs?: number}} [options]
 */
export function writeJsonAtomic(path, value, options = {}) {
  writeFileAtomic(path, `${JSON.stringify(value, null, 2)}\n`, options)
}
