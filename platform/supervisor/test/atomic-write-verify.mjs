/**
 * 原子写 helper 验证（platform/supervisor/atomic-write.mjs）。
 *
 * 覆盖平台 supervisor 全部状态文件共用的「先写 tmp 再 rename」写入路径：
 * 1. 正常写入：内容与目标文件逐字节一致，且不残留 `${path}.${pid}.tmp`；
 * 2. JSON 写入格式：2 空格缩进 + 末尾换行（与平台既有写法一致）；
 * 3. 覆盖写入已存在文件成功（Windows 上 rename 覆盖已存在目标）；
 * 4. **重试可验证**：用真实 Windows 独占句柄（FileShare.Read，不含 Delete
 *    共享）占住目标文件 → rename 必得 EPERM；helper 退避重试、锁释放后成功，
 *    证明「rename 遇 EPERM 会重试而不是立刻失败」。另用子进程轮询器在重试
 *    窗口内观测到 `${path}.${pid}.tmp` 实体文件，同时证明 tmp 名带 pid
 *    （跨进程唯一）与「重试期间 tmp 确实存在」；
 * 5. 非重试类错误（ENOENT）立即抛出、不被吞掉、错误信息含 errno code，
 *    且不进入退避重试（耗时远小于重试预算）；
 * 6. rename 阶段最终失败（目标为已存在目录 → Windows 返回 EPERM）时，重试
 *    耗尽后抛**中文**错误（`原子写入失败（EPERM）…`，含 errno code），
 *    且失败路径清理自己的 tmp（不残留）。
 *
 * 运行：node platform/supervisor/test/atomic-write-verify.mjs
 * 退出码：全过 0；有失败 1。
 */
import assert from 'node:assert/strict'
import { spawn } from 'node:child_process'
import { existsSync, mkdirSync, readFileSync, readdirSync, renameSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

import { writeFileAtomic, writeJsonAtomic } from '../atomic-write.mjs'

const ROOT = join(tmpdir(), `dsh-atomic-verify-${process.pid}`)
mkdirSync(ROOT, { recursive: true })

let passed = 0
let failed = 0

const check = async (name, fn) => {
  try {
    await fn()
    passed += 1
    console.log(`[PASS] ${name}`)
  } catch (error) {
    failed += 1
    console.log(`[FAIL] ${name}`)
    console.log(`       ${error?.message ?? error}`)
  }
}

const wait = (ms) => new Promise((r) => setTimeout(r, ms))

/** PowerShell 单引号串里的单引号要写成两个。 */
const psQuote = (s) => `'${String(s).replace(/'/g, "''")}'`

/**
 * 起一个子进程用独占句柄占住 target（FileShare.Read —— 不含 Delete 共享），
 * 打开成功后写 ready 标记，持有 holdMs 毫秒后释放。持有期间任何针对该文件
 * 的 rename 都会得到 Windows 的 ERROR_SHARING_VIOLATION → Node 映射为 EPERM。
 */
const lockTarget = (target, readyFlag, holdMs) => {
  const script = [
    `$f=[System.IO.File]::Open(${psQuote(target)},'Open','Read','Read');`,
    `[System.IO.File]::WriteAllText(${psQuote(readyFlag)},'1');`,
    `Start-Sleep -Milliseconds ${holdMs};`,
    `$f.Close()`,
  ].join('')
  return spawn('powershell', ['-NoProfile', '-Command', script], { stdio: 'ignore' })
}

/** 轮询器子进程：在窗口期内观测 tmp 文件是否出现，出现即写标记后退出。
 *  同时盯住「带 pid」与「固定名」两个候选，标记 seen=pid / seen=fixed，
 *  以证明 helper 用的是带 pid 的跨进程唯一 tmp 名。 */
const POLLER_SRC = `
import { existsSync, writeFileSync } from 'node:fs'
const [pidTmpPath, fixedTmpPath, flagPath] = process.argv.slice(2)
const deadline = Date.now() + 8000
while (Date.now() < deadline) {
  if (existsSync(pidTmpPath)) { writeFileSync(flagPath, 'pid'); break }
  if (existsSync(fixedTmpPath)) { writeFileSync(flagPath, 'fixed'); break }
  await new Promise((r) => setTimeout(r, 10))
}
`

/* ── 1. 正常写入 ─────────────────────────────────────────────────────────── */
console.log('# 正常写入')
await check('内容与目标文件一致', () => {
  const dir = join(ROOT, 't1')
  mkdirSync(dir, { recursive: true })
  const path = join(dir, 'note.txt')
  writeFileAtomic(path, 'hello 原子写\n')
  assert.equal(readFileSync(path, 'utf8'), 'hello 原子写\n')
})

await check('无残留 tmp 文件（${path}.${pid}.tmp 不存在，目录内只有目标文件）', () => {
  const dir = join(ROOT, 't1')
  const path = join(dir, 'note.txt')
  assert.equal(existsSync(`${path}.${process.pid}.tmp`), false, '不应残留 pid 版 tmp')
  assert.deepEqual(readdirSync(dir), ['note.txt'], '目录内不应有其它 tmp 文件')
})

/* ── 2. JSON 写入格式 ────────────────────────────────────────────────────── */
console.log('# JSON 写入格式')
await check('2 空格缩进 + 末尾换行（与 JSON.stringify(v, null, 2) + "\\n" 逐字节一致）', () => {
  const dir = join(ROOT, 't2')
  mkdirSync(dir, { recursive: true })
  const path = join(dir, 'a.json')
  const value = { b: 1, a: [1, 2, { c: true }], '中文键': '值' }
  writeJsonAtomic(path, value)
  const raw = readFileSync(path, 'utf8')
  assert.equal(raw, `${JSON.stringify(value, null, 2)}\n`, '应与既有格式逐字节一致')
  assert.ok(raw.includes('\n  "b": 1'), '应为 2 空格缩进')
  assert.ok(raw.endsWith('\n'), '应以换行结尾')
  assert.equal(existsSync(`${path}.${process.pid}.tmp`), false)
})

/* ── 3. 覆盖已存在文件 ───────────────────────────────────────────────────── */
console.log('# 覆盖已存在文件')
await check('覆盖写入已存在文件成功（Windows rename 覆盖目标）', () => {
  const dir = join(ROOT, 't3')
  mkdirSync(dir, { recursive: true })
  const path = join(dir, 'a.json')
  writeFileSync(path, 'OLD CONTENT')
  writeJsonAtomic(path, { fresh: true })
  assert.equal(readFileSync(path, 'utf8'), `${JSON.stringify({ fresh: true }, null, 2)}\n`)
  assert.equal(existsSync(`${path}.${process.pid}.tmp`), false)
  assert.deepEqual(readdirSync(dir), ['a.json'])
})

/* ── 4. 重试可验证（真实 Windows EPERM）─────────────────────────────────── */
console.log('# 重试可验证（Windows 独占句柄 → rename EPERM）')
await check('rename 遇 EPERM 会退避重试而非立刻失败（锁释放后写入成功）', async () => {
  const dir = join(ROOT, 't4')
  mkdirSync(dir, { recursive: true })
  const target = join(dir, 'locked.json')
  const readyFlag = join(dir, 'ready.flag')
  const holdMs = 600
  writeFileSync(target, 'ORIGINAL')

  const locker = lockTarget(target, readyFlag, holdMs)
  const deadline = Date.now() + 30_000
  while (!existsSync(readyFlag) && Date.now() < deadline) await wait(25)
  assert.ok(existsSync(readyFlag), '独占句柄未能在 30s 内建立')

  // 控制实验：此刻裸 rename 必须失败，证明锁真实生效（否则下面的重试无从谈起）。
  const controlSrc = join(dir, 'control.tmp')
  writeFileSync(controlSrc, 'x')
  let controlCode = null
  try { renameSync(controlSrc, target) } catch (error) { controlCode = error?.code }
  assert.equal(controlCode, 'EPERM', `控制实验期望 EPERM，实际 ${controlCode}`)

  // 轮询器在重试窗口内观测 tmp 实体文件。
  const pollerFile = join(dir, 'poller.mjs')
  writeFileSync(pollerFile, POLLER_SRC)
  const tmpPath = `${target}.${process.pid}.tmp`
  const fixedTmpPath = `${target}.tmp`
  const sawFlag = join(dir, 'saw-tmp.flag')
  const poller = spawn(process.execPath, [pollerFile, tmpPath, fixedTmpPath, sawFlag], { stdio: 'ignore' })

  const started = Date.now()
  writeFileAtomic(target, 'NEW CONTENT', { retries: 8, baseDelayMs: 15 })
  const elapsed = Date.now() - started

  await Promise.all([
    new Promise((r) => locker.on('exit', r)),
    new Promise((r) => poller.on('exit', r)),
  ])

  assert.equal(readFileSync(target, 'utf8'), 'NEW CONTENT', '重试成功后应写入新内容')
  assert.ok(elapsed >= holdMs, `写入耗时 ${elapsed}ms 应 >= 锁持有 ${holdMs}ms（证明首轮 rename 失败并经过重试）`)
  assert.ok(existsSync(sawFlag), '重试窗口内应能观测到 tmp 实体文件')
  assert.equal(existsSync(tmpPath), false, '成功后不应残留 tmp')
})

await check('tmp 名带 pid（跨进程唯一：轮询器只命中 ${path}.${pid}.tmp，未命中固定名 path.tmp）', () => {
  const dir = join(ROOT, 't4')
  assert.ok(existsSync(join(dir, 'saw-tmp.flag')), '上一用例已观测到 tmp 实体文件')
  assert.equal(readFileSync(join(dir, 'saw-tmp.flag'), 'utf8'), 'pid', 'tmp 名应为 pid 版而非固定名')
  assert.equal(existsSync(join(dir, 'locked.json.tmp')), false, '不应出现固定名 path.tmp')
  const siblings = readdirSync(dir).filter((n) => n.endsWith('.tmp'))
  assert.deepEqual(siblings, ['control.tmp'], '不应有除对照文件外的残留 tmp')
})

await check('对照：retries=0 时同一独占锁直接抛 EPERM（证明是「重试」救了这次写入）', async () => {
  const dir = join(ROOT, 't4b')
  mkdirSync(dir, { recursive: true })
  const target = join(dir, 'locked2.json')
  const readyFlag = join(dir, 'ready.flag')
  writeFileSync(target, 'ORIGINAL')
  const locker = lockTarget(target, readyFlag, 1500)
  const deadline = Date.now() + 30_000
  while (!existsSync(readyFlag) && Date.now() < deadline) await wait(25)
  assert.ok(existsSync(readyFlag), '独占句柄未能在 30s 内建立')

  let error = null
  try { writeFileAtomic(target, 'NEW', { retries: 0 }) } catch (caught) { error = caught }
  await new Promise((r) => locker.on('exit', r))
  assert.ok(error, 'retries=0 时应直接失败')
  assert.ok(String(error.message).includes('EPERM'), `错误信息应含 errno code：${error.message}`)
  assert.equal(readFileSync(target, 'utf8'), 'ORIGINAL', '失败时不应改动目标文件')
  assert.equal(existsSync(`${target}.${process.pid}.tmp`), false, '失败后不应残留 tmp')
})

/* ── 5. 非重试类错误立即抛出 ────────────────────────────────────────────── */
console.log('# 非重试类错误')
await check('ENOENT 立即抛出（不进入退避重试），错误含 errno code，异常未被吞掉', () => {
  const dir = join(ROOT, 't5')
  mkdirSync(dir, { recursive: true })
  const path = join(dir, 'no-such-dir', 'x.json')
  const started = Date.now()
  let error = null
  try { writeFileAtomic(path, 'x') } catch (caught) { error = caught }
  const elapsed = Date.now() - started
  assert.ok(error, '必须抛出异常（不得吞掉）')
  assert.equal(error.code, 'ENOENT', 'errno code 应为 ENOENT')
  assert.ok(String(error.message).includes('ENOENT'), `错误信息应含 errno code：${error.message}`)
  // 默认重试预算 = 15+30+60+120+240 = 465ms；若误入重试，耗时必然远超此值。
  assert.ok(elapsed < 200, `非重试类错误应立即抛出（耗时 ${elapsed}ms 应 < 200ms）`)
  assert.equal(existsSync(`${path}.${process.pid}.tmp`), false, '失败后不应残留 tmp')
})

/* ── 6. rename 阶段最终失败：中文错误 + errno code + 无残留 tmp ─────────── */
console.log('# rename 阶段最终失败')
await check('重试耗尽后抛中文错误（含 errno code），且失败后不残留 tmp', () => {
  const dir = join(ROOT, 't6')
  mkdirSync(dir, { recursive: true })
  // 目标是一个已存在目录 → Windows 上 rename 文件到目录必得 EPERM。
  const target = join(dir, 'target-dir')
  mkdirSync(target, { recursive: true })
  let error = null
  try { writeFileAtomic(target, 'x', { retries: 1, baseDelayMs: 5 }) } catch (caught) { error = caught }
  assert.ok(error, '必须抛出异常')
  assert.ok(/[\u4e00-\u9fff]/.test(String(error.message)), `错误信息应含中文：${error.message}`)
  assert.ok(String(error.message).includes('EPERM'), `错误信息应含 errno code：${error.message}`)
  assert.ok(String(error.message).includes('原子写入失败'), `错误信息应为中文包装：${error.message}`)
  assert.equal(existsSync(`${target}.${process.pid}.tmp`), false, '失败后不应残留 tmp')
  assert.deepEqual(readdirSync(dir), ['target-dir'], '目录内不应残留 tmp 文件')
})

rmSync(ROOT, { recursive: true, force: true })

console.log(`\n通过 ${passed}，失败 ${failed}`)
process.exit(failed > 0 ? 1 : 0)
