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
import { mkdirSync, openSync, readFileSync, renameSync, rmSync, writeFileSync } from 'node:fs'
import { createServer } from 'node:http'
import { get } from 'node:http'
import { join, resolve } from 'node:path'

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
    if (!install.ok) return { pass: false, output: `安装失败:
${install.output}` }

    const port = await freePort()
    const commandLine = [launchTemplate.command, ...launchTemplate.args]
      .map((a) => a.replaceAll('{port}', String(port))
        .replaceAll('{id}', 'precheck')
        .replaceAll('{gatewayAuthority}', `precheck.local:${port}`))
      .join(' ')
    // detached + 日志落文件：本机沙箱会收割 daemon 晚生成的子进程并使管道
    // 随父进程失效；脱离进程组 + 文件输出让启动结果始终可查。
    const bootLog = join(tempHome, 'boot.log')
    const out = openSync(bootLog, 'a')
    const spawnedAt = Date.now()
    let crashed = false
    let crashDetail = ''
    const child = spawn(commandLine, {
      cwd: repoRoot,
      env: { ...process.env, DSH_HOME: tempHome },
      detached: true,
      windowsHide: true,
      shell: true,
      stdio: ['ignore', out, out],
    })
    child.unref()
    child.on('exit', (code, signal) => {
      crashed = true
      crashDetail = `exit code=${code} signal=${signal} at ${new Date().toISOString()} (spawned ${new Date(spawnedAt).toISOString()})`
    })

    const readBootLog = () => {
      try { return readFileSync(bootLog, 'utf8') } catch { return '' }
    }
    const deadline = Date.now() + bootTimeoutMs
    let healthy = false
    while (Date.now() < deadline) {
      if (crashed) break
      if (await healthOnce(port)) { healthy = true; break }
      await sleep(2_000)
    }
    await killTree(child.pid)
    const bootOutput = readBootLog()
    if (healthy) return { pass: true, output: `隔离启动健康（port ${port}，${Math.round((Date.now() - (deadline - bootTimeoutMs)) / 1000)}s）` }
    return { pass: false, output: `真启动未通过（${crashed ? `进程早退 ${crashDetail}` : '超时'}）:
${bootOutput.slice(-2_000)}` }
  } finally {
    try { rmSync(tempHome, { recursive: true, force: true }) } catch { /* 临时目录清理失败不阻塞 */ }
  }
}

/* ── 异步投放任务队列（控制台插件页）────────────────────────────────────────
 * 投放/预检是分钟级操作，HTTP 请求-响应装不下：任务落 data/jobs.json，
 * 串行执行（同一时刻至多一个 pnpm/预检启动），控制台轮询取状态。
 * 运行于 daemon 进程内；实例重启经 control.json 复用既有控制通道。 */


/** 从安装 spec 推导插件名：本地路径读其 package.json 的 name；npm spec 取最后一个 @ 前段。 */
function specName(spec) {
  if (spec.startsWith('.') || /^[a-zA-Z]:[\/]/.test(spec) || spec.startsWith('/')) {
    return JSON.parse(readFileSync(resolve(spec, 'package.json'), 'utf8')).name
  }
  if (spec.startsWith('@')) return spec.split('@').length > 2 ? spec.slice(0, spec.lastIndexOf('@')) : spec
  const at = spec.lastIndexOf('@')
  return at > 0 ? spec.slice(0, at) : spec
}

/** 可授权插件目录：push 登记的最新 spec（成员×插件矩阵的数据源）。 */
export function pluginCatalog(dataDir) {
  return loadDesired(dataDir).catalog ?? []
}

export function createJobRunner({ dataDir, manifest, repoRoot }) {
  const jobsFile = join(dataDir, 'jobs.json')
  const JOBS_TIMEOUT_MS = 20 * 60_000
  let queue = Promise.resolve()
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

  const loadJobs = () => {
    try { return JSON.parse(readFileSync(jobsFile, 'utf8')) } catch { return { jobs: [] } }
  }
  const saveJobs = (store) => {
    const tmp = `${jobsFile}.tmp`
    writeFileSync(tmp, `${JSON.stringify(store, null, 2)}\n`)
    renameSync(tmp, jobsFile)
  }
  const patchJob = (id, patch) => {
    const store = loadJobs()
    const job = store.jobs.find((j) => j.id === id)
    if (job === undefined) return
    Object.assign(job, patch)
    job.updatedAt = new Date().toISOString()
    saveJobs(store)
  }
  const appendOutput = (id, text) => {
    const store = loadJobs()
    const job = store.jobs.find((j) => j.id === id)
    if (job === undefined) return
    job.output = `${job.output ?? ''}${text}`.slice(-4_000)
    saveJobs(store)
  }

  async function execute(job) {
    const homeOf = (id) => join(dataDir, 'homes', id)
    const targets = job.ids === 'all' ? manifest.instances.map((s) => s.id) : job.ids
    for (const id of targets) {
      if (!manifest.instances.some((s) => s.id === id)) throw new Error(`未知实例: ${id}`)
    }
    switch (job.type) {
      case 'precheck': {
        const result = await precheck({ repoRoot, dataDir, spec: job.spec, launchTemplate: manifest.launch })
        appendOutput(job.id, `\n${result.pass ? 'PASS' : 'FAIL'}: ${result.output}`)
        if (!result.pass) throw new Error('预检未通过')
        return
      }
      case 'push': {
        if (job.skipPrecheck !== true) {
          appendOutput(job.id, '\n[precheck] 隔离真启动预检中…')
          const result = await precheck({ repoRoot, dataDir, spec: job.spec, launchTemplate: manifest.launch })
          appendOutput(job.id, `\n[precheck] ${result.pass ? 'PASS' : 'FAIL'}: ${result.output}`)
          if (!result.pass) throw new Error('预检未通过，已拦截（任何实例均未安装）')
        }
        const name = job.name
        for (const id of targets) {
          appendOutput(job.id, `\n[install] ${id}: 安装到 profile（暂存）…`)
          const install = await runPluginCommand({ repoRoot, home: homeOf(id), action: 'add', spec: job.spec })
          if (!install.ok) {
            appendOutput(job.id, `\n[install] ${id} 失败:\n${install.output.slice(-1_000)}`)
            const store = loadDesired(dataDir)
            const entry = (store.instances[id] ??= []).find((p) => p.name === name)
            if (entry !== undefined) entry.state = 'failed'
            saveDesired(dataDir, store)
            throw new Error(`实例 ${id} 安装失败`)
          }
          const store = loadDesired(dataDir)
          const list = (store.instances[id] ??= [])
          const prev = list.find((p) => p.name === name)
          const history = prev?.history ?? []
          if (prev?.spec !== undefined && prev.spec !== job.spec) history.unshift(prev.spec)
          const record = { name, spec: job.spec, state: 'staged', since: new Date().toISOString(), history }
          const idx = list.findIndex((p) => p.name === name)
          if (idx >= 0) list[idx] = record
          else list.push(record)
          saveDesired(dataDir, store)
          appendOutput(job.id, `\n[install] ${id}: 已暂存（plugin-activate 或实例管理页重启生效）`)
        }
        return
      }
      case 'remove': {
        for (const id of targets) {
          appendOutput(job.id, `\n[remove] ${id}: 卸载…`)
          const install = await runPluginCommand({ repoRoot, home: homeOf(id), action: 'remove', spec: job.name })
          if (!install.ok) throw new Error(`实例 ${id} 卸载失败:\n${install.output.slice(-500)}`)
          const store = loadDesired(dataDir)
          const entry = (store.instances[id] ?? []).find((p) => p.name === job.name)
          if (entry !== undefined) entry.state = 'removed'
          saveDesired(dataDir, store)
          appendOutput(job.id, `\n[remove] ${id}: 已卸载，写入重启控制`)
          writeFileSync(join(dataDir, 'control.json'), `${JSON.stringify({ action: 'restart', id, at: Date.now() })}\n`)
        }
        return
      }
      case 'activate': {
        for (const id of targets) {
          writeFileSync(join(dataDir, 'control.json'), `${JSON.stringify({ action: 'restart', id, at: Date.now() })}\n`)
          appendOutput(job.id, `\n[activate] ${id}: 已请求重启`)
          await sleep(3_000)
        }
        return
      }
      default:
        throw new Error(`未知任务类型: ${job.type}`)
    }
  }

  // 启动清理：daemon 重启会打断执行中的任务，僵尸 queued/running 记录转为失败
  {
    const store = loadJobs()
    let dirty = false
    for (const j of store.jobs) {
      if (j.state === 'queued' || j.state === 'running') {
        j.state = 'failed'
        j.error = 'daemon 重启导致任务中断'
        dirty = true
      }
    }
    if (dirty) saveJobs(store)
  }

  return {
    /** 入队一个投放任务；串行执行，立即返回任务记录。 */
    enqueue({ type, spec, ids, skipPrecheck }) {
      const store = loadJobs()
      const pending = store.jobs.filter((j) => j.state === 'queued' || j.state === 'running').length
      if (pending >= 10) {
        throw new Error('队列中待处理任务过多（10），请等当前任务完成后再试')
      }
      const name = specName(spec)
      const job = {
        id: `job-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 6)}`,
        type, spec, name,
        ids: ids ?? 'all',
        skipPrecheck: skipPrecheck === true,
        state: 'queued',
        output: '',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      }
      store.jobs.push(job)
      if (store.jobs.length > 50) store.jobs = store.jobs.slice(-50)
      saveJobs(store)
      this._kick()
      return job
    },
    list() {
      return loadJobs().jobs.slice(-20).reverse()
    },
    _kick() {
      const store = loadJobs()
      const next = [...store.jobs].reverse().find((j) => j.state === 'queued')
      if (next === undefined) return
      queue = queue.then(async () => {
        const current = loadJobs().jobs.find((j) => j.id === next.id)
        if (current === undefined || current.state !== 'queued') return
        patchJob(next.id, { state: 'running', startedAt: new Date().toISOString() })
        try {
          await execute({ ...next })
          patchJob(next.id, { state: 'done', finishedAt: new Date().toISOString() })
        } catch (error) {
          patchJob(next.id, { state: 'failed', error: String(error?.message ?? error), finishedAt: new Date().toISOString() })
        }
      })
      return queue
    },
  }
}
