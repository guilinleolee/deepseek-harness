/**
 * 落云宗企业平台 · 插件治理（任务书阶段 6）。
 *
 * 期望态存 data/plugins.json：{ instances: { <实例id>: [{ name, spec, state, since, history }] } }。
 * 命令语义（对齐任务书术语）：
 * - plugin-push：真启动预检通过后，把插件装进目标实例 profile——运行中的实例
 *   组卷只发生在启动时，装完即「暂存」，重启才「生效」；
 * - plugin-precheck：在隔离临时 DSH_HOME 里装同一插件并真启动（健康探测，
 *   超时 120 秒），失败即拦截；预检失败 push 拒绝安装，真实实例不受影响；
 * - plugin-activate：重启实例使暂存生效；
 * - plugin-remove：卸载 + 可选重启（回滚与「禁用」同一语义，禁用后员工
 *   工作台入口随重启消失）；
 * - plugin-rollback：按 history 回装上一个已知良好 spec 并重启。
 */
import { createHash } from 'node:crypto'
import { spawn } from 'node:child_process'
import { mkdirSync, readFileSync, rmSync, writeFileSync, renameSync } from 'node:fs'
import { createServer } from 'node:http'
import { get } from 'node:http'
import { join } from 'node:path'

const PLUGINS_FILE = 'plugins.json'
const INSTALL_TIMEOUT_MS = 10 * 60_000
const DEFAULT_PRECHECK_BOOT_TIMEOUT_MS = 120_000

export function loadDesired(dataDir) {
  try {
    return JSON.parse(readFileSync(join(dataDir, PLUGINS_FILE), 'utf8'))
  } catch {
    return { instances: {} }
  }
}

export function saveDesired(dataDir, store) {
  const path = join(dataDir, PLUGINS_FILE)
  const tmp = `${path}.tmp`
  writeFileSync(tmp, `${JSON.stringify(store, null, 2)}\n`)
  renameSync(tmp, path)
}

/** 在指定 DSH_HOME 的 web profile 里执行 dsh plugin add/remove（pnpm 转发）。 */
export function runPluginCommand({ repoRoot, home, action, spec, timeoutMs = INSTALL_TIMEOUT_MS }) {
  return new Promise((resolveCmd) => {
    const args = ['--import', 'tsx/esm', join(repoRoot, 'apps', 'cli', 'src', 'bin.ts'),
      'plugin', '--profile', 'web', action, spec]
    const child = spawn(process.execPath, args, {
      cwd: repoRoot,
      env: { ...process.env, DSH_HOME: home },
      windowsHide: true,
      timeout: timeoutMs,
    })
    let output = ''
    child.stdout.on('data', (d) => { output += d })
    child.stderr.on('data', (d) => { output += d })
    child.on('error', (error) => resolveCmd({ ok: false, output: `${output}\n${error.message}` }))
    child.on('close', (code) => resolveCmd({ ok: code === 0, output }))
  })
}

function killTree(pid) {
  if (process.platform === 'win32') {
    const p = spawn('taskkill', ['/PID', String(pid), '/T', '/F'], { windowsHide: true })
    return new Promise((r) => { p.on('close', r); p.on('error', r) })
  }
  try { process.kill(-pid, 'SIGTERM') } catch { try { process.kill(pid, 'SIGTERM') } catch {} }
  return Promise.resolve()
}

/** 找一个当前空闲的回环端口（预检启动用）。 */
function freePort() {
  return new Promise((resolvePort) => {
    const probe = createServer()
    probe.listen(0, '127.0.0.1', () => {
      const { port } = probe.address()
      probe.close(() => resolvePort(port))
    })
  })
}

function healthOnce(port) {
  return new Promise((resolvePing) => {
    const req = get({ host: '127.0.0.1', port, path: '/', timeout: 2_000 }, (res) => {
      res.resume()
      resolvePing(res.statusCode !== undefined && res.statusCode < 500)
    })
    req.on('timeout', () => { req.destroy(); resolvePing(false) })
    req.on('error', () => resolvePing(false))
  })
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

/**
 * 真启动预检：隔离临时 home 装插件 → 真启动（独立端口）→ 健康探测 ≤120 秒。
 * 返回 { pass, output }。启动失败/超时/进程早亡都算 FAIL。
 */
export async function precheck({ repoRoot, dataDir, spec, launchTemplate, timeoutMs }) {
  const bootTimeoutMs = timeoutMs ?? DEFAULT_PRECHECK_BOOT_TIMEOUT_MS
  const stamp = new Date().toISOString().replace(/[:.]/g, '-')
  const tempHome = join(dataDir, 'precheck', `${stamp}-${createHash('sha1').update(spec).digest('hex').slice(0, 8)}`)
  mkdirSync(tempHome, { recursive: true })
  try {
    const install = await runPluginCommand({ repoRoot, home: tempHome, action: 'add', spec })
    if (!install.ok) return { pass: false, output: `安装失败:\n${install.output}` }

    const port = await freePort()
    const commandLine = [launchTemplate.command, ...launchTemplate.args]
      .map((a) => a.replaceAll('{port}', String(port))
        .replaceAll('{id}', 'precheck')
        .replaceAll('{gatewayAuthority}', `precheck.local:${port}`))
      .join(' ')
    const child = spawn(commandLine, {
      cwd: repoRoot,
      env: { ...process.env, DSH_HOME: tempHome },
      windowsHide: true,
      shell: true,
      stdio: ['ignore', 'pipe', 'pipe'],
    })
    const spawnedAt = Date.now()
    let bootOutput = ''
    child.stdout.on('data', (d) => { bootOutput += d })
    child.stderr.on('data', (d) => { bootOutput += d })
    let crashed = false
    let crashDetail = ''
    child.on('exit', (code, signal) => { crashed = true; crashDetail = `exit code=${code} signal=${signal} at ${new Date().toISOString()} (spawned ${new Date(spawnedAt).toISOString()})`; bootOutput += `
[exit] ${crashDetail}
` })

    const deadline = Date.now() + bootTimeoutMs
    let healthy = false
    while (Date.now() < deadline) {
      if (crashed) break
      if (await healthOnce(port)) { healthy = true; break }
      await sleep(2_000)
    }
    await killTree(child.pid)
    if (healthy) return { pass: true, output: `隔离启动健康（port ${port}，${Math.round((Date.now() - (deadline - bootTimeoutMs)) / 1000)}s）` }
    return { pass: false, output: `真启动未通过（${crashed ? `进程早退 ${crashDetail}` : '超时'}）:\n${bootOutput.slice(-2_000)}` }
  } finally {
    try { rmSync(tempHome, { recursive: true, force: true }) } catch { /* 临时目录清理失败不阻塞 */ }
  }
}
