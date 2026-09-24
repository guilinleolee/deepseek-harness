#!/usr/bin/env node
/**
 * 落云宗企业平台 · 实例编排 supervisor MVP（任务书阶段 1）。
 *
 * 职责：按 instances.json 清单把每个员工实例拉起为一个独立 DSH web 进程
 * （独立 DSH_HOME + 独立端口 + 名义 uid），做健康检查、崩溃自动重启
 * （远低于任务书 30 秒上限）、空闲回收（手动），并向管理台暴露实例页
 * 数据（端口/pid/uid/目录/内存/磁盘/运行时长）与统一入口 portal 页。
 *
 * 形态：`up` 拉起一个驻留 daemon（持有全部子进程）；`status` / `stop` /
 * `restart` / `logs` 是短命命令，通过 data/ 下的状态与控制文件通信。
 * 零第三方依赖；Windows（开发机）与 Linux（生产服务器）均可运行。
 *
 * 隐私边界（任务书决定 5）：本组件只采集进程与资源元数据，
 * 不读会话日志、不读任何内容正文。
 */
import { get } from 'node:http'
import { spawn } from 'node:child_process'
import { createWriteStream } from 'node:fs'
import {
  existsSync, mkdirSync, readFileSync, readdirSync, renameSync, rmSync, statSync,
  writeFileSync, openSync, closeSync,
} from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { platform } from 'node:os'
import { randomBytes } from 'node:crypto'
import { addAccount, createGatewayServer, listAccounts, loadAccounts, revokeAccountTokens, setPassword, updateAccount } from './gateway.mjs'
import { createRelayServer, issueVkey, listUpstreams, listUsage, listVkeys, monthKey, revokeVkey, setQuota, setUpstream } from './relay.mjs'
import { fmtPoints } from './quotas.mjs'
import { compareSets, effectiveModels, effectivePlugins, grantedModels, loadDriftState, mergeDiffs, saveDriftState } from './introspect.mjs'
import { loadDesired, precheck, runPluginCommand, saveDesired } from './plugins-gov.mjs'

const HERE = dirname(fileURLToPath(import.meta.url))
const DATA = join(HERE, 'data')
const HOMES = join(DATA, 'homes')
const LOGS = join(DATA, 'logs')
const STATE_FILE = join(DATA, 'state.json')
const CONTROL_FILE = join(DATA, 'control.json')
const DAEMON_PID_FILE = join(DATA, 'daemon.pid')

const MANIFEST = JSON.parse(readFileSync(join(HERE, 'instances.json'), 'utf8'))
const IS_WIN = platform() === 'win32'
const RESTART_DELAY_MS = 2_000
const START_TIMEOUT_MS = 180_000
const HEALTH_INTERVAL_MS = 15_000
const CONTROL_POLL_MS = 2_000
const SAMPLE_INTERVAL_MS = 30_000
const DISK_INTERVAL_MS = 120_000
const RESTART_RESET_UPTIME_MS = 5 * 60_000
const MAX_RESTARTS_IN_WINDOW = 5
const DISK_WALK_ENTRY_CAP = 50_000

const instanceHome = (id) => join(HOMES, id)
const instanceLog = (id) => join(LOGS, `${id}.log`)

function readState() {
  try {
    return JSON.parse(readFileSync(STATE_FILE, 'utf8'))
  } catch {
    return { daemon: null, instances: {} }
  }
}

function writeState(state) {
  mkdirSync(DATA, { recursive: true })
  const tmp = `${STATE_FILE}.tmp`
  writeFileSync(tmp, `${JSON.stringify(state, null, 2)}\n`)
  renameSync(tmp, STATE_FILE)
}

function pidAlive(pid) {
  if (!Number.isInteger(pid) || pid <= 0) return false
  try {
    process.kill(pid, 0)
    return true
  } catch {
    return false
  }
}

function isDaemonAlive() {
  try {
    return pidAlive(JSON.parse(readFileSync(DAEMON_PID_FILE, 'utf8')).pid)
  } catch {
    return false
  }
}

function spawnDetachedDaemon() {
  mkdirSync(LOGS, { recursive: true })
  const out = openSync(join(LOGS, 'daemon.log'), 'a')
  const child = spawn(process.execPath, [join(HERE, 'supervisor.mjs'), 'daemon'], {
    cwd: HERE,
    detached: true,
    stdio: ['ignore', out, out],
    windowsHide: true,
  })
  child.unref()
  closeSync(out)
  return child.pid
}

function enqueueControl(action, id) {
  mkdirSync(DATA, { recursive: true })
  writeFileSync(CONTROL_FILE, `${JSON.stringify({ action, id, at: Date.now() })}\n`)
}

/* ── daemon 侧：实例生命周期 ─────────────────────────────────────────────── */

const children = new Map() // id -> { child, log }

function killTree(pid) {
  if (IS_WIN) {
    // child.kill() 只杀直接子进程；pnpm→node 的进程树要 taskkill /T。
    // 必须等 taskkill 跑完：fire-and-forget 的子进程会随调用方 process.exit
    // 一起被收割，一个都没杀成。
    return new Promise((resolve_) => {
      const p = spawn('taskkill', ['/PID', String(pid), '/T', '/F'], { windowsHide: true })
      p.on('close', () => resolve_())
      p.on('error', () => resolve_())
    })
  }
  try { process.kill(-pid, 'SIGTERM') } catch { try { process.kill(pid, 'SIGTERM') } catch {} }
  return Promise.resolve()
}

function launchInstance(spec, state) {
  const home = instanceHome(spec.id)
  mkdirSync(home, { recursive: true })
  mkdirSync(LOGS, { recursive: true })

  const rec = state.instances[spec.id]
  // 模板占位符：{port} {id} {gatewayAuthority}。trusted-host 让实例的信任
  // 围栏接受网关转发的 Host；--host 127.0.0.1 保证生产上员工绕不过网关。
  const gatewayAuthority = `${spec.id}.${MANIFEST.gatewayHost}:${MANIFEST.portalPort}`
  const substitutions = {
    '{port}': String(spec.port),
    '{id}': spec.id,
    '{gatewayAuthority}': gatewayAuthority,
  }
  const line = [MANIFEST.launch.command, ...MANIFEST.launch.args]
    .map((part) => {
      let out = part
      for (const [from, to] of Object.entries(substitutions)) out = out.replaceAll(from, to)
      return out
    })
    .join(' ')
  const child = spawn(line, {
    cwd: resolve(HERE, MANIFEST.repoRoot),
    env: {
      ...process.env,
      DSH_HOME: home,
      // 每实例 env 注入（任务书 6a）：如 CREATOR_WORKBENCH_SKILLS_PATH 指向
      // 服务器侧管理员维护的技能库，替代插件里的本机默认路径。值支持
      // {dataDir} 占位符。
      ...Object.fromEntries(Object.entries(spec.env ?? {}).map(([k, v]) => [k, v.replaceAll('{dataDir}', DATA)])),
    },
    stdio: ['ignore', 'pipe', 'pipe'],
    windowsHide: true,
    // 单字符串 + shell：pnpm 在 Windows 是 .cmd；清单内容是管理员维护的可信输入。
    shell: true,
  })
  const log = createWriteStream(instanceLog(spec.id), { flags: 'a' })
  log.write(`\n=== ${new Date().toISOString()} spawn pid=${child.pid} port=${spec.port} home=${home}\n`)
  child.stdout.pipe(log, { end: false })
  child.stderr.pipe(log, { end: false })
  children.set(spec.id, { child, log })

  rec.pid = child.pid
  rec.state = 'starting'
  rec.startedAt = Date.now()
  rec.health = { lastOkAt: null, latencyMs: null }
  rec.memoryKB = null
  rec.startTimeoutAt = Date.now() + START_TIMEOUT_MS
  writeState(state)

  child.on('exit', (code, signal) => {
    children.delete(spec.id)
    rec.pid = null
    rec.lastExit = { code, signal, at: Date.now() }
    if (rec.desired !== 'up') {
      rec.state = 'stopped'
      writeState(state)
      return
    }
    if (rec.controlledRestart) {
      // 受控重启（restart --id X）：不算崩溃、不计数，直接拉起。
      rec.controlledRestart = false
      rec.state = 'starting'
      writeState(state)
      setTimeout(() => {
        if (rec.desired === 'up' && rec.pid === null) launchInstance(spec, state)
      }, RESTART_DELAY_MS)
      return
    }
    // 崩溃自动重启：带防循环护栏。重启计数在稳定运行 5 分钟后清零。
    rec.state = 'crashed'
    writeState(state)
    const stableLongEnough = rec.startedAt !== null
      && rec.lastExit.at - rec.startedAt >= RESTART_RESET_UPTIME_MS
    if (stableLongEnough) rec.restarts = 0
    rec.restarts += 1
    if (rec.restarts > MAX_RESTARTS_IN_WINDOW) {
      rec.state = 'failed'
      writeState(state)
      console.error(`[supervisor] ${spec.id}: 连续重启 ${rec.restarts} 次仍退出，置为 failed，等人工介入`)
      return
    }
    rec.state = 'restarting'
    writeState(state)
    setTimeout(() => {
      if (rec.desired === 'up' && rec.pid === null) launchInstance(spec, state)
    }, RESTART_DELAY_MS)
  })
}

function healthOnce(port) {
  return new Promise((resolve_) => {
    const started = Date.now()
    const req = get({ host: '127.0.0.1', port, path: '/', timeout: 2_000 }, (res) => {
      res.resume()
      resolve_({ ok: res.statusCode !== undefined && res.statusCode < 500, latencyMs: Date.now() - started })
    })
    req.on('timeout', () => { req.destroy(); resolve_({ ok: false }) })
    req.on('error', () => resolve_({ ok: false }))
  })
}

/**
 * 采样进程树内存：rec.pid 是启动外壳（pnpm/cmd），真正的 DSH node 进程是
 * 它的后代，必须整树求和才是实例的真实占用。Windows 用一次 PowerShell
 * 全进程表（pid/ppid/工作集），Linux 读 /proc/<pid>/stat；解析在 node 侧
 * 统一建树。尽力而为：任一步失败返回 null，不阻塞其他采样。
 * @returns {Promise<Map<number, number>>} 根 pid → 树内工作集合计（KB）
 */
async function sampleTreeMemoryKB(rootPids) {
  const rows = await listProcesses()
  if (rows === null) return null
  const byPpid = new Map()
  const ws = new Map()
  for (const row of rows) {
    ws.set(row.pid, row.kb)
    if (!byPpid.has(row.ppid)) byPpid.set(row.ppid, [])
    byPpid.get(row.ppid).push(row.pid)
  }
  const result = new Map()
  for (const root of rootPids) {
    let total = 0
    const stack = [root]
    const seen = new Set()
    while (stack.length > 0) {
      const pid = stack.pop()
      if (seen.has(pid)) continue
      seen.add(pid)
      total += ws.get(pid) ?? 0
      for (const child of byPpid.get(pid) ?? []) stack.push(child)
    }
    result.set(root, total)
  }
  return result
}

async function listProcesses() {
  if (IS_WIN) {
    return new Promise((resolve_) => {
      const script = 'Get-CimInstance Win32_Process | '
        + 'Select-Object ProcessId,ParentProcessId,WorkingSetSize | '
        + 'ConvertTo-Json -Compress'
      const p = spawn('powershell.exe', ['-NoProfile', '-Command', script], { windowsHide: true })
      let out = ''
      p.stdout.on('data', (d) => { out += d })
      p.on('close', (code) => {
        if (code !== 0) { resolve_(null); return }
        try {
          const parsed = JSON.parse(out)
          const list = Array.isArray(parsed) ? parsed : [parsed]
          resolve_(list.map((r) => ({
            pid: Number(r.ProcessId),
            ppid: Number(r.ParentProcessId),
            kb: Math.round(Number(r.WorkingSetSize) / 1024),
          })))
        } catch { resolve_(null) }
      })
      p.on('error', () => resolve_(null))
    })
  }
  // Linux/BSD：一遍 /proc，stat 的第 4 字段是 ppid、第 24 字段是 rss（页）。
  const rows = []
  const pageSizeKb = 4
  for (const name of readdirSync('/proc')) {
    if (!/^\d+$/.test(name)) continue
    try {
      const stat = readFileSync(`/proc/${name}/stat`, 'utf8')
      const close = stat.lastIndexOf(')')
      const fields = stat.slice(close + 2).split(' ')
      rows.push({
        pid: Number(name),
        ppid: Number(fields[1]),
        kb: Number(fields[21]) * pageSizeKb,
      })
    } catch { /* 进程可能刚好退出，跳过 */ }
  }
  return rows
}

/**
 * home 磁盘占用：异步遍历（fs.promises 走线程池，事件循环不挨饿——home 里有
 * pnpm 装的上万文件的 node_modules，同步遍历曾把整个控制进程阻塞数十秒）。
 * 带条目数上限，超过即以当前累计值返回（尽力而为的近似值）。
 */
async function diskUsageBytes(dir) {
  const { readdir, stat } = await import('node:fs/promises')
  let total = 0
  let entries = 0
  const walk = async (path) => {
    if (entries > DISK_WALK_ENTRY_CAP) return
    let stats
    try { stats = await stat(path) } catch { return }
    if (!stats.isDirectory()) { total += stats.size; entries += 1; return }
    let names
    try { names = await readdir(path) } catch { return }
    for (const name of names) {
      if (entries > DISK_WALK_ENTRY_CAP) return
      entries += 1
      await walk(join(path, name))
    }
  }
  await walk(dir)
  return total
}

async function daemon() {
  if (isDaemonAlive()) {
    console.error('supervisor daemon 已在运行')
    process.exit(1)
  }
  mkdirSync(HOMES, { recursive: true })
  mkdirSync(LOGS, { recursive: true })
  writeFileSync(DAEMON_PID_FILE, `${JSON.stringify({ pid: process.pid, at: Date.now() })}\n`)

  const state = { daemon: { pid: process.pid, startedAt: Date.now() }, instances: {} }
  for (const spec of MANIFEST.instances) {
    state.instances[spec.id] = {
      ...spec,
      home: instanceHome(spec.id),
      desired: 'up',
      pid: null,
      state: 'stopped',
      startedAt: null,
      restarts: 0,
      lastExit: null,
      health: { lastOkAt: null, latencyMs: null },
      memoryKB: null,
      diskBytes: null,
    }
  }
  writeState(state)

  // 认证网关先绑定再拉实例：绑定失败（EADDRINUSE…）时一个孩子都不会留下。
  // 网关取代阶段 1 的裸 portal：登录 + JWT + Host 路由反代（见 gateway.mjs）。
  if (!existsSync(join(DATA, 'accounts.json'))) {
    console.error('[supervisor] 警告：data/accounts.json 不存在（还没有任何账号），所有人都将无法登录。'
      + `用 node supervisor.mjs add-account 创建账号后重试。`)
  }
  const gateway = createGatewayServer({ manifest: MANIFEST, getState: () => state, dataDir: DATA })
  await new Promise((resolveBind, rejectBind) => {
    gateway.once('error', rejectBind)
    gateway.listen(MANIFEST.portalPort, MANIFEST.gatewayBindHost ?? '127.0.0.1', resolveBind)
  })
  console.log(`[supervisor] gateway listening on ${MANIFEST.gatewayBindHost ?? '127.0.0.1'}:${MANIFEST.portalPort}`)

  // Relay 密钥代理：真实上游 Key 的唯一容身处（阶段 3）。
  const relay = createRelayServer({ dataDir: DATA })
  await new Promise((resolveBind, rejectBind) => {
    relay.once('error', rejectBind)
    relay.listen(MANIFEST.relayPort ?? 9400, '127.0.0.1', resolveBind)
  })
  console.log(`[supervisor] relay listening on 127.0.0.1:${MANIFEST.relayPort ?? 9400}`)

  for (const spec of MANIFEST.instances) launchInstance(spec, state)

  // 健康轮询：starting 期 2 秒一次直到通，之后 15 秒一次保活观测。
  setInterval(async () => {
    for (const spec of MANIFEST.instances) {
      const rec = state.instances[spec.id]
      if (rec.pid === null) continue
      const result = await healthOnce(spec.port)
      if (result.ok) {
        rec.state = 'running'
        rec.health = { lastOkAt: Date.now(), latencyMs: result.latencyMs }
        rec.startTimeoutAt = null
      } else if (rec.state === 'starting' && rec.startTimeoutAt !== null && Date.now() > rec.startTimeoutAt) {
        rec.state = 'unhealthy'
      } else if (rec.state === 'running') {
        rec.state = 'unhealthy'
      }
    }
    writeState(state)
  }, HEALTH_INTERVAL_MS)

  // 资源采样：实例进程树内存（一次全进程表，建树求和）与 home 磁盘占用。
  setInterval(async () => {
    const alive = MANIFEST.instances.filter((spec) => state.instances[spec.id].pid !== null)
    if (alive.length > 0) {
      const memory = await sampleTreeMemoryKB(alive.map((spec) => state.instances[spec.id].pid))
      if (memory !== null) {
        for (const spec of alive) {
          state.instances[spec.id].memoryKB = memory.get(state.instances[spec.id].pid) ?? null
        }
      }
    }
    writeState(state)
  }, SAMPLE_INTERVAL_MS)

  setInterval(async () => {
    for (const spec of MANIFEST.instances) {
      state.instances[spec.id].diskBytes = await diskUsageBytes(instanceHome(spec.id))
    }
    writeState(state)
  }, DISK_INTERVAL_MS)

  // 控制文件轮询：stop/start/restart <id>。
  setInterval(() => {
    let cmd
    try { cmd = JSON.parse(readFileSync(CONTROL_FILE, 'utf8')) } catch { return }
    try { rmSync(CONTROL_FILE) } catch {}
    const rec = state.instances[cmd.id]
    if (!rec) return
    if (cmd.action === 'stop' && rec.pid !== null) {
      rec.desired = 'down'
      killTree(rec.pid)
    } else if (cmd.action === 'start' && rec.pid === null) {
      rec.desired = 'up'
      rec.restarts = 0
      rec.state = 'starting'
      rec.startTimeoutAt = Date.now() + START_TIMEOUT_MS
      launchInstance(spec, state)
    } else if (cmd.action === 'restart') {
      rec.desired = 'up'
      rec.restarts = 0
      if (rec.pid !== null) {
        rec.controlledRestart = true
        rec.state = 'restarting'
        killTree(rec.pid)
        // 兜底：若 exit 事件丢失（进程树已被外部整体杀掉），也要拉起。
        setTimeout(() => {
          if (rec.desired === 'up' && rec.pid === null && !children.has(spec.id)) {
            rec.controlledRestart = false
            launchInstance(spec, state)
          }
        }, RESTART_DELAY_MS * 3)
      } else {
        launchInstance(spec, state)
      }
    }
    writeState(state)
  }, CONTROL_POLL_MS)

  const shutdown = async () => {
    for (const spec of MANIFEST.instances) {
      const rec = state.instances[spec.id]
      rec.desired = 'down'
      if (rec.pid !== null) await killTree(rec.pid)
    }
    writeState(state)
    process.exit(0)
  }
  process.on('SIGINT', () => { void shutdown() })
  process.on('SIGTERM', () => { void shutdown() })

  // 驻留：intervals 与 portal server 维持事件循环；main() 的完成回调
  // 会对短命命令 process.exit(0)，这里用永不 resolve 的 promise 挡住它。
  return new Promise(() => {})
}

/* ── 短命命令 ────────────────────────────────────────────────────────────── */

function humanBytes(n) {
  if (n === null || n === undefined) return '—'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  while (n >= 1024 && i < units.length - 1) { n /= 1024; i += 1 }
  return `${n.toFixed(i === 0 ? 0 : 1)} ${units[i]}`
}

function printStatus() {
  const state = readState()
  const daemonAlive = isDaemonAlive()
  console.log(`daemon: ${daemonAlive ? `运行中 (pid ${state.daemon?.pid})` : '未运行'}  portal: http://127.0.0.1:${MANIFEST.portalPort}/`)
  for (const spec of MANIFEST.instances) {
    const rec = state.instances[spec.id] ?? {}
    // daemon 不在时状态文件失真：按 pid 实际存活度诚实显示。
    let shown = rec.state ?? '—'
    if (!daemonAlive && rec.pid !== null) {
      shown = pidAlive(rec.pid) ? 'running（daemon 已停，进程残留）' : 'stopped'
    }
    const uptime = daemonAlive && rec.startedAt !== null && rec.pid !== null
      ? Math.round((Date.now() - rec.startedAt) / 1000) : null
    const mem = rec.memoryKB !== null && rec.memoryKB !== undefined ? humanBytes(rec.memoryKB * 1024) : '—'
    console.log(
      `${spec.id}  ${spec.account}  状态=${shown}  pid=${rec.pid ?? '—'}  `
      + `端口=${spec.port}  uid=${spec.uid}  内存=${mem}  磁盘=${humanBytes(rec.diskBytes)}  `
      + `重启=${rec.restarts ?? 0}  运行=${uptime !== null ? `${uptime}s` : '—'}  `
      + `home=${rec.home ?? instanceHome(spec.id)}`,
    )
  }
}

/** 从安装 spec 推导插件名：本地路径读其 package.json 的 name；npm spec 取最后一个 @ 前段。 */
function isLocalPathSpec(spec) {
  if (spec.startsWith('@')) return false
  if (spec.startsWith('.') || /^[a-zA-Z]:[\\/]/.test(spec) || spec.startsWith('/') || spec.startsWith('\\')) return true
  if ((spec.includes('/') || spec.includes('\\')) && existsSync(join(resolve(spec), 'package.json'))) return true
  return false
}

function pluginNameOf(spec) {
  if (isLocalPathSpec(spec)) {
    const manifest = JSON.parse(readFileSync(join(resolve(spec), 'package.json'), 'utf8'))
    return manifest.name
  }
  const at = spec.lastIndexOf('@')
  return at > 0 ? spec.slice(0, at) : spec
}

/** 本地路径 spec 转绝对路径（precheck/安装的 cwd 各不相同，边界上统一）。 */
function absolutizeSpec(spec) {
  return isLocalPathSpec(spec) ? resolve(spec) : spec
}

async function main() {
  const [, , cmd, flag, value] = process.argv
  if (cmd === 'daemon') return daemon()
  if (cmd === 'up') {
    if (isDaemonAlive()) {
      console.log(`daemon 已在运行 (pid ${readState().daemon?.pid})`)
      return
    }
    const pid = spawnDetachedDaemon()
    console.log(`daemon 已拉起 (pid ${pid})，日志: ${join(LOGS, 'daemon.log')}`)
    return
  }
  if (cmd === 'status') {
    printStatus()
    return
  }
  if (cmd === 'stop') {
    if (flag === '--id') {
      if (!isDaemonAlive()) throw new Error('daemon 未在运行')
      enqueueControl('stop', value)
      console.log(`已请求停止实例 ${value}`)
      return
    }
    // 先逐个杀实例树，再杀 daemon：/T 的树遍历在中间壳进程已退出时会断链，
    // 显式遍历状态文件里的实例根 pid 是可靠的兜底。
    const state = readState()
    for (const rec of Object.values(state.instances)) {
      if (rec.pid !== null && pidAlive(rec.pid)) await killTree(rec.pid)
    }
    if (isDaemonAlive()) {
      const { pid } = JSON.parse(readFileSync(DAEMON_PID_FILE, 'utf8'))
      await killTree(pid)
      try { rmSync(DAEMON_PID_FILE) } catch {}
      console.log('已请求 daemon 退出（子进程一并停止）')
    } else {
      console.log('daemon 未在运行；已清理残留实例进程（如有）')
    }
    return
  }
  if (cmd === 'restart') {
    if (!isDaemonAlive()) throw new Error('daemon 未在运行')
    if (flag !== '--id' || !value) throw new Error('restart 需要 --id <实例id>')
    enqueueControl('restart', value)
    console.log(`已请求重启实例 ${value}`)
    return
  }
  if (cmd === 'start') {
    if (!isDaemonAlive()) throw new Error('daemon 未在运行')
    if (flag !== '--id' || !value) throw new Error('start 需要 --id <实例id>')
    enqueueControl('start', value)
    console.log(`已请求启动实例 ${value}`)
    return
  }
  if (cmd === 'logs') {
    const id = flag === '--id' ? value : cmd
    const log = instanceLog(id ?? '')
    if (!existsSync(log)) throw new Error(`没有实例日志: ${log}`)
    // 输出最后 200 行。
    const raw = readFileSync(log, 'utf8')
    process.stdout.write(raw.split('\n').slice(-200).join('\n'))
    return
  }
  if (cmd === 'add-account') {
    // add-account <email> --instance <id> --role <admin|auditor|employee> [--password <pw>] [--name <显示名>]
    const email = flag
    if (!email || !email.includes('@')) throw new Error('用法: add-account <email> --instance <id> --role <admin|auditor|employee> [--password <pw>] [--name <显示名>]')
    const opts = { account: email }
    for (let i = 4; i < process.argv.length; i += 2) {
      const flag = process.argv[i]
      const value = process.argv[i + 1]
      if (flag === '--instance') opts.instanceId = value
      else if (flag === '--role') opts.role = value
      else if (flag === '--password') opts.password = value
      else if (flag === '--name') opts.displayName = value
      else if (flag === '--department') opts.department = value
    }
    if (!opts.instanceId || !MANIFEST.instances.some((s) => s.id === opts.instanceId)) {
      throw new Error(`--instance 必须是清单中的实例 id: ${MANIFEST.instances.map((s) => s.id).join(', ')}`)
    }
    if (!['admin', 'auditor', 'employee'].includes(opts.role)) throw new Error('--role 必须是 admin | auditor | employee')
    if (opts.password === undefined) {
      opts.password = randomBytes(9).toString('base64url')
      console.log(`自动生成密码: ${opts.password}  （请立即转交本人）`)
    }
    const record = addAccount(DATA, opts)
    console.log(`已创建账号 ${record.account}（${record.role}）→ 实例 ${record.instanceId}`)
    return
  }
  if (cmd === 'list-accounts') {
    const accounts = listAccounts(DATA)
    if (accounts.length === 0) { console.log('（无账号）'); return }
    for (const a of accounts) {
      console.log(`${a.account}  ${a.role}  实例=${a.instanceId}  epoch=${a.tokenEpoch}  创建=${a.createdAt}`)
    }
    return
  }
  if (cmd === 'revoke') {
    // revoke --account <email>：epoch 递增，该账号所有已签发令牌立即失效。
    if (flag !== '--account' || !value) throw new Error('用法: revoke --account <email>')
    const epoch = revokeAccountTokens(DATA, value)
    console.log(`已撤销 ${value} 的全部令牌（tokenEpoch → ${epoch}）`)
    return
  }
  if (cmd === 'set-upstream') {
    // set-upstream <name> --baseURL <url> --models m1,m2 [--key <真实Key>]
    const name = flag
    if (!name) throw new Error('用法: set-upstream <name> --baseURL <url> --models m1,m2 [--key <真实Key>]（key 只写入不回显）')
    const opts = {}
    for (let i = 4; i < process.argv.length; i += 2) {
      if (process.argv[i] === '--baseURL') opts.baseURL = process.argv[i + 1]
      else if (process.argv[i] === '--models') opts.models = process.argv[i + 1].split(',').map((m) => m.trim()).filter(Boolean)
      else if (process.argv[i] === '--key') opts.apiKey = process.argv[i + 1]
    }
    if (!opts.baseURL || !opts.models?.length) throw new Error('--baseURL 与 --models 必填')
    setUpstream(DATA, { name, ...opts })
    console.log(`上游 ${name} 已保存（baseURL=${opts.baseURL}，模型 ${opts.models.join(', ')}）`)
    return
  }
  if (cmd === 'list-upstreams') {
    for (const u of listUpstreams(DATA)) {
      console.log(`${u.name}${u.revoked ? '（已停用）' : ''}  ${u.baseURL}  模型=${u.models.join(', ')}  key=${u.keyFingerprint}`)
    }
    return
  }
  if (cmd === 'issue-vkey') {
    // issue-vkey --account <email> [--models m1,m2 | --all]
    const opts = { models: '*' }
    for (let i = 3; i < process.argv.length; i += 2) {
      if (process.argv[i] === '--account') opts.account = process.argv[i + 1]
      else if (process.argv[i] === '--models') opts.models = process.argv[i + 1].split(',').map((m) => m.trim()).filter(Boolean)
      else if (process.argv[i] === '--all') { opts.models = '*'; i -= 1 }
    }
    if (!opts.account) throw new Error('用法: issue-vkey --account <email> [--models m1,m2 | --all]')
    const record = loadAccounts(DATA).accounts.find((a) => a.account === opts.account)
    if (record === undefined) throw new Error(`账号不存在: ${opts.account}`)
    const { token } = issueVkey(DATA, { account: opts.account, instanceId: record.instanceId, models: opts.models })
    console.log(`虚拟钥匙已签发（旧钥匙已自动吊销）。模型授权: ${opts.models === '*' ? '全部' : opts.models.join(', ')}`)
    console.log(`token（仅此一次显示，请立即写入实例 home 的 .credentials.yaml）:\n${token}`)
    return
  }
  if (cmd === 'list-vkeys') {
    for (const v of listVkeys(DATA)) {
      console.log(`${v.id}  ${v.account}  实例=${v.instanceId}  模型=${v.models === '*' ? '全部' : v.models.join(',')}  ${v.revoked ? '已吊销' : '有效'}  签发=${v.createdAt}`)
    }
    return
  }
  if (cmd === 'revoke-vkey') {
    if (flag !== '--account' || !value) throw new Error('用法: revoke-vkey --account <email>')
    const n = revokeVkey(DATA, { account: value })
    console.log(`已吊销 ${value} 的 ${n} 把虚拟钥匙`)
    return
  }
  if (cmd === 'set-password') {
    // set-password --account <email> [--password <pw>]：重哈希并 epoch+1 踢掉全部旧会话。
    const opts = {}
    for (let i = 3; i < process.argv.length; i += 2) {
      if (process.argv[i] === '--account') opts.account = process.argv[i + 1]
      else if (process.argv[i] === '--password') opts.password = process.argv[i + 1]
    }
    if (!opts.account) throw new Error('用法: set-password --account <email> [--password <pw>]（不给密码则自动生成）')
    if (opts.password === undefined) {
      opts.password = randomBytes(9).toString('base64url')
      console.log(`自动生成密码: ${opts.password}  （请立即转交本人）`)
    }
    const epoch = setPassword(DATA, opts.account, opts.password)
    console.log(`已重置 ${opts.account} 的密码（tokenEpoch → ${epoch}，全部旧会话已下线）`)
    return
  }
  if (cmd === 'set-role') {
    if (flag !== '--account' || !value) throw new Error('用法: set-role --account <email> --role <admin|auditor|employee>')
    const role = process.argv[6]
    if (!['admin', 'auditor', 'employee'].includes(role)) throw new Error('--role 必须是 admin | auditor | employee')
    updateAccount(DATA, value, { role })
    console.log(`已将 ${value} 的角色改为 ${role}`)
    return
  }
  if (cmd === 'set-quota') {
    // set-quota --account <email> --tokens <N> | --unlimited
    const opts = {}
    for (let i = 3; i < process.argv.length; i += 2) {
      if (process.argv[i] === '--account') opts.account = process.argv[i + 1]
      else if (process.argv[i] === '--tokens') opts.tokens = Number(process.argv[i + 1])
      else if (process.argv[i] === '--unlimited') { opts.unlimited = true; i -= 1 }
    }
    if (!opts.account) throw new Error('用法: set-quota --account <email> --tokens <N> | --unlimited')
    if (!opts.unlimited && !Number.isInteger(opts.tokens) || opts.tokens < 0) throw new Error('--tokens 必须是非负整数（0 = 立即硬停）；不限额度用 --unlimited')
    setQuota(DATA, { account: opts.account, monthlyTokens: opts.unlimited ? null : opts.tokens })
    console.log(`已设置 ${opts.account} 的月度额度: ${opts.unlimited ? '不限' : `${opts.tokens} tokens`}（硬停语义，服务器本地时区每月重置）`)
    return
  }
  if (cmd === 'list-usage') {
    let month = monthKey()
    for (let i = 3; i < process.argv.length; i += 2) {
      if (process.argv[i] === '--month') month = process.argv[i + 1]
    }
    console.log(`月份 ${month}（服务器本地时区）`)
    for (const u of listUsage(DATA, month)) {
      const quota = u.monthlyTokens === null ? '不限' : String(u.monthlyTokens)
      const points = `${fmtPoints(u.points)}${u.monthlyPoints !== null ? `/${u.monthlyPoints}` : ''}`
      const legacy = u.quotaMode === 'legacy-tokens' ? '  （旧制 tokens）' : ''
      console.log(`${u.account}  实例=${u.instanceId}  入=${u.tokensIn}  出=${u.tokensOut}  请求=${u.requests}  点数=${points}${legacy}  tokens已用=${u.used}/${quota}${u.remaining !== null ? `  剩余=${u.remaining}` : ''}`)
    }
    return
  }
  if (cmd === 'drift') {
    // 授权集（钥匙模型白名单 + 插件期望清单）vs 实际生效集（home 内省）。
    // 持续未消除的差异按时限（driftStaleHours，默认 24h）标红。
    const repoRoot = resolve(HERE, MANIFEST.repoRoot)
    const state = loadDriftState(DATA)
    const now = Date.now()
    const staleMs = (MANIFEST.driftStaleHours ?? 24) * 3_600_000
    const upstreams = listUpstreams(DATA)
    const vkeys = readFileSync(join(DATA, 'vkeys.json'), 'utf8')
    const vkeyStore = JSON.parse(vkeys)
    const desired = loadDesired(DATA)
    const report = []
    for (const spec of MANIFEST.instances) {
      const home = instanceHome(spec.id)
      const vkey = vkeyStore.vkeys.filter((v) => v.account === spec.account && !v.revoked).at(-1)
      const grantedM = vkey ? grantedModels(vkey.models, upstreams) : []
      const grantedP = (desired.instances[spec.id] ?? []).filter((p) => p.state !== 'removed')
      const effM = effectiveModels(home)
      const effPluginsRaw = effectivePlugins(home)
      const effP = effPluginsRaw.map((p) => p.name)
      const diffs = [
        ...compareSets(grantedM, effM, 'model'),
        ...compareSets(grantedP.map((p) => p.name), effP, 'plugin'),
      ]
      for (const g of grantedP) {
        // 期望 spec 是裸包名（无版本段）时只比存在性：pnpm 落盘的是解析后的版本号。
        if (g.spec !== g.name) {
          const installed = effPluginsRaw.find((p) => p.name === g.name)
          if (installed !== undefined && installed.spec !== g.spec) {
            diffs.push({ kind: 'plugin-version', detail: `${g.name}（期望 ${g.spec}，实际 ${installed.spec}）` })
          }
        }
      }
      const merged = mergeDiffs(state.checks[spec.id]?.diffs, diffs, now)
        .map((d) => ({ ...d, stale: now - Date.parse(d.detectedAt) > staleMs }))
      state.checks[spec.id] = {
        checkedAt: new Date(now).toISOString(),
        grantedSet: { models: grantedM, plugins: grantedP },
        effectiveSet: { models: effM, plugins: effPluginsRaw },
        diffs: merged,
      }
      report.push({ id: spec.id, account: spec.account, diffs: merged })
    }
    saveDriftState(DATA, state)
    if (flag === '--json') { console.log(JSON.stringify(report, null, 2)); return }
    for (const r of report) {
      if (r.diffs.length === 0) { console.log(`${r.id}  ${r.account}  ✓ 对齐`); continue }
      console.log(`${r.id}  ${r.account}  ✗ ${r.diffs.length} 处漂移`)
      for (const d of r.diffs) {
        const mark = d.stale ? '【红-超时未消除】' : '【黄-新发现】'
        console.log(`   ${mark} ${d.kind}: ${d.detail}（发现于 ${d.detectedAt}）`)
      }
    }
    return
  }
  if (cmd === 'plugin-precheck') {
    if (flag !== '--plugin' || !value) throw new Error('用法: plugin-precheck --plugin <spec|本地路径>')
    const spec = absolutizeSpec(value)
    console.log(`预检 ${spec}：隔离 home 安装 + 真启动（≤120 秒）…`)
    const result = await precheck({ repoRoot: resolve(HERE, MANIFEST.repoRoot), dataDir: DATA, spec, launchTemplate: MANIFEST.launch, timeoutMs: (MANIFEST.precheckTimeoutSeconds ?? 120) * 1000 })
    console.log(result.pass ? `PASS: ${result.output}` : `FAIL: ${result.output}`)
    if (!result.pass) process.exitCode = 1
    return
  }
  if (cmd === 'plugin-push') {
    // plugin-push --plugin <spec|本地路径> [--ids all|e01,e02] [--skip-precheck]
    const opts = { ids: 'all' }
    for (let i = 3; i < process.argv.length; i += 2) {
      if (process.argv[i] === '--plugin') opts.plugin = process.argv[i + 1]
      else if (process.argv[i] === '--ids') opts.ids = process.argv[i + 1]
      else if (process.argv[i] === '--skip-precheck') { opts.skip = true; i -= 1 }
    }
    if (!opts.plugin) throw new Error('用法: plugin-push --plugin <spec|本地路径> [--ids all|e01,e02] [--skip-precheck]')
    const targets = opts.ids === 'all' ? MANIFEST.instances.map((s) => s.id) : opts.ids.split(',')
    for (const id of targets) {
      if (!MANIFEST.instances.some((s) => s.id === id)) throw new Error(`未知实例: ${id}`)
    }
    if (opts.skip !== true) {
      console.log('真启动预检中…')
      const spec = absolutizeSpec(opts.plugin)
      const result = await precheck({ repoRoot: resolve(HERE, MANIFEST.repoRoot), dataDir: DATA, spec, launchTemplate: MANIFEST.launch, timeoutMs: (MANIFEST.precheckTimeoutSeconds ?? 120) * 1000 })
      if (!result.pass) {
        console.log(`预检 FAIL，已拦截，任何实例均未安装:\n${result.output}`)
        process.exitCode = 1
        return
      }
      console.log(`预检 PASS: ${result.output}`)
    }
    const repoRoot = resolve(HERE, MANIFEST.repoRoot)
    const spec = absolutizeSpec(opts.plugin)
    const name = pluginNameOf(spec)
    const installSpec = spec
    const store = loadDesired(DATA)
    for (const id of targets) {
      store.instances[id] ??= []
      const entry = store.instances[id].find((p) => p.name === name)
      const history = entry?.history ?? []
      if (entry?.spec !== undefined && entry.spec !== opts.plugin) history.unshift(entry.spec)
      const record = { name, spec: installSpec, state: 'staged', since: new Date().toISOString(), history }
      const idx = store.instances[id].findIndex((p) => p.name === name)
      if (idx >= 0) store.instances[id][idx] = record
      else store.instances[id].push(record)
      const install = await runPluginCommand({ repoRoot, home: instanceHome(id), action: 'add', spec: installSpec })
      if (!install.ok) {
        record.state = 'failed'
        saveDesired(DATA, store)
        console.log(`${id}: 安装失败（已标记 failed）:\n${install.output.slice(-1_000)}`)
        process.exitCode = 1
        continue
      }
      console.log(`${id}: 已暂存 ${name}（运行中实例不受影响；plugin-activate --id ${id} 重启生效）`)
    }
    saveDesired(DATA, store)
    return
  }
  if (cmd === 'plugin-activate') {
    if (flag !== '--id' || !value) throw new Error('用法: plugin-activate --id <实例id>（重启使暂存生效）')
    if (!isDaemonAlive()) throw new Error('daemon 未在运行')
    enqueueControl('restart', value)
    console.log(`已请求重启 ${value}；暂存插件将在启动时生效`)
    return
  }
  if (cmd === 'plugin-remove') {
    // plugin-remove --plugin <name> [--ids all|e01,e02] [--no-restart]
    // 卸载 + 重启 =「禁用」（员工工作台入口消失）；也是回滚的执行原语。
    const opts = { ids: 'all', restart: true }
    for (let i = 3; i < process.argv.length; i += 2) {
      if (process.argv[i] === '--plugin') opts.plugin = process.argv[i + 1]
      else if (process.argv[i] === '--ids') opts.ids = process.argv[i + 1]
      else if (process.argv[i] === '--no-restart') { opts.restart = false; i -= 1 }
    }
    if (!opts.plugin) throw new Error('用法: plugin-remove --plugin <name> [--ids all|e01,e02] [--no-restart]')
    const targets = opts.ids === 'all' ? MANIFEST.instances.map((s) => s.id) : opts.ids.split(',')
    const store = loadDesired(DATA)
    const repoRoot = resolve(HERE, MANIFEST.repoRoot)
    for (const id of targets) {
      const install = await runPluginCommand({ repoRoot, home: instanceHome(id), action: 'remove', spec: opts.plugin })
      const entries = store.instances[id] ?? []
      const entry = entries.find((p) => p.name === opts.plugin)
      if (entry !== undefined) entry.state = 'removed'
      if (!install.ok) {
        console.log(`${id}: 卸载失败:\n${install.output.slice(-1_000)}`)
        process.exitCode = 1
        continue
      }
      console.log(`${id}: 已卸载 ${opts.plugin}${opts.restart ? '（重启后生效/入口消失）' : ''}`)
      if (opts.restart && isDaemonAlive()) enqueueControl('restart', id)
    }
    saveDesired(DATA, store)
    return
  }
  if (cmd === 'plugin-rollback') {
    if (flag !== '--id' || !value) throw new Error('用法: plugin-rollback --id <实例id> --plugin <name>')
    const plugin = process.argv[6]
    if (!plugin) throw new Error('用法: plugin-rollback --id <实例id> --plugin <name>')
    const store = loadDesired(DATA)
    const entry = (store.instances[value] ?? []).find((p) => p.name === plugin)
    const previous = entry?.history?.[0]
    if (previous === undefined) throw new Error(`${plugin} 没有可回滚的历史版本`)
    const repoRoot = resolve(HERE, MANIFEST.repoRoot)
    const install = await runPluginCommand({ repoRoot, home: instanceHome(value), action: 'add', spec: previous })
    if (!install.ok) { console.log(`回滚安装失败:\n${install.output.slice(-1_000)}`); process.exitCode = 1; return }
    entry.spec = previous
    entry.state = 'staged'
    entry.history.shift()
    saveDesired(DATA, store)
    if (isDaemonAlive()) enqueueControl('restart', value)
    console.log(`${value}: 已回装 ${plugin}@${previous} 并请求重启生效`)
    return
  }
  console.log(`用法: supervisor.mjs <...|drift|plugin-precheck|plugin-push|plugin-activate|plugin-remove|plugin-rollback>
  drift [--json]    授权集 vs 实际生效集比对（差异按时限标红）
  plugin-precheck --plugin <spec|本地路径>      隔离真启动预检（≤120 秒）
  plugin-push --plugin <spec|本地路径> [--ids all|e01,e02] [--skip-precheck]
                    预检通过后装进实例 profile（暂存，重启才生效）
  plugin-activate --id <实例id>   重启实例使暂存生效
  plugin-remove --plugin <name> [--ids all|e01,e02] [--no-restart]
                    卸载并重启（=禁用，入口消失）；也是回滚原语
  plugin-rollback --id <实例id> --plugin <name>   回装上一个已知良好版本
  up                拉起驻留 daemon（后台），按清单启动全部实例
  status            打印实例页数据（端口/pid/uid/内存/磁盘/重启数）
  stop [--id X]     停 daemon（含全部实例）；带 --id 只停一个实例
  start --id X      启动单个实例
  restart --id X    重启单个实例
  logs --id X       查看实例日志（最后 200 行）
  daemon            前台运行 daemon（调试用）
  add-account <email> --instance <id> --role <admin|auditor|employee> [--password <pw>]
  list-accounts     列出账号
  revoke --account <email>   撤销该账号全部登录令牌（立即全端下线）
  set-upstream <name> --baseURL <url> --models m1,m2 [--key <真实Key>]
  list-upstreams    列出上游（key 只显示指纹）
  issue-vkey --account <email> [--models m1,m2 | --all]
  list-vkeys        列出虚拟钥匙（只有哈希，token 不可见）
  revoke-vkey --account <email>   吊销该账号全部虚拟钥匙
  set-quota --account <email> --tokens <N> | --unlimited   月度 Token 额度（硬停）
  set-role --account <email> --role <role>   修改账号角色
  set-password --account <email> [--password <pw>]   重置密码并踢掉全部旧会话
  list-usage [--month YYYY-MM]    当月用量对照额度`)
}

main().then(
  () => process.exit(process.exitCode ?? 0),
  (error) => { console.error(String(error?.message ?? error)); process.exit(1) },
)
