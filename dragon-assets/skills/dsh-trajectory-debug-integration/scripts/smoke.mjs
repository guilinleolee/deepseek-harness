#!/usr/bin/env node
/**
 * Smoke test: load the trajectory-debug plugin family into a REAL dsh process.
 *
 * Creates/refreshes a scratch profile (`td-smoke`) under $DSH_HOME, installs
 * the four packages via pnpm `file:` links, verifies the composed tree with
 * `--dump-config`, then boots the profile and asserts the plugin tree loads
 * without errors (the profile has no app plugin, so a clean boot just idles).
 *
 * Usage: node scripts/smoke.mjs
 *
 * Lessons baked in (verified on rc.6):
 * - pnpm copies `file:` deps into the profile's virtual store, so REBUILD the
 *   workspace first and re-run `pnpm install` in the profile;
 * - the `Service` constructor already registers `ctx.trajectoryDebug` — do not
 *   `ctx.provide` it again;
 * - `ctx.logger` is a callable LoggerService (`ctx.logger(name).info`).
 */

import { spawn, spawnSync } from 'node:child_process'
import { cpSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { homedir } from 'node:os'
import { join, resolve } from 'node:path'

const ROOT = resolve(import.meta.dirname, '..')
const BIN = 'C:/Users/PC/AppData/Local/npm-cache/_npx/1e7f6d9597241db0/node_modules/@deepseek-ai/dsh/lib/bin.js'
const PROFILE = join(process.env.DSH_HOME ?? join(homedir(), '.dsh'), 'profiles', 'td-smoke')
const BOOT_WAIT_MS = 10_000

function run(cmd, args, opts = {}) {
  // Windows resolves corepack/pnpm through .cmd shims, which spawn() refuses
  // without a shell (CVE-2024-27980 hardening).
  const r = spawnSync(cmd, args, { encoding: 'utf8', shell: process.platform === 'win32', ...opts })
  if (r.status !== 0 && !opts.allowFail) {
    console.error(r.stdout ?? '')
    console.error(r.stderr ?? '')
    throw new Error(`${cmd} ${args.join(' ')} failed (${r.status})`)
  }
  return r
}

const STAGED = ['trajectory-debug', 'trajectory-debug-host', 'trajectory-debug-remotes', 'client-ui-trajectory-debug']
/** Package dir name → npm package name (the internal dep keys). */
const STAGED_NAMES = new Set(STAGED.map((dir) => (dir.startsWith('client-') ? `dsh-${dir}` : `dsh-${dir}`)))

/**
 * Stage the four packages as a self-contained vendor tree inside the profile:
 * copy { package.json, lib } and rewrite the internal `workspace:*` links to
 * relative `file:../<name>` so pnpm can resolve them without making the
 * profile a cross-drive workspace (the repo lives on D:, the profile on
 * $DSH_HOME). This keeps the smoke independent of the repo's dependency
 * protocol.
 */
function stagePackages() {
  const vendor = join(PROFILE, 'vendor')
  rmSync(vendor, { recursive: true, force: true })
  mkdirSync(vendor, { recursive: true })
  for (const name of STAGED) {
    const src = join(ROOT, 'packages', name)
    const dst = join(vendor, name)
    mkdirSync(dst, { recursive: true })
    cpSync(join(src, 'lib'), join(dst, 'lib'), { recursive: true })
    const manifest = JSON.parse(readFileSync(join(src, 'package.json'), 'utf8'))
    for (const section of ['dependencies', 'peerDependencies', 'devDependencies']) {
      const deps = manifest[section]
      if (!deps) continue
      for (const [dep, spec] of Object.entries(deps)) {
        if (spec === 'workspace:*' && STAGED_NAMES.has(dep)) {
          // Rewrite to the sibling's file: link (all four live in vendor/).
          deps[dep] = `file:../${dep.replace(/^dsh-/, '')}`
        }
      }
    }
    writeFileSync(join(dst, 'package.json'), JSON.stringify(manifest, null, 2))
  }
}

function profileFiles() {
  const pkg = {
    name: 'dsh-profile-td-smoke',
    private: true,
    // Dep keys are the npm PACKAGE names (dsh-*); the file: targets are the
    // staged directory names inside vendor/.
    dependencies: Object.fromEntries(STAGED.map((dir) => [`dsh-${dir}`, `file:./vendor/${dir}`])),
    dsh: { profile: { bundles: ['@deepseek-ai/dsh-base'] } },
  }
  const patch = `- insert:
    - id: trajectory-debug-host
      name: 'dsh-trajectory-debug-host'
      config:
        breakpointTimeoutMs: 600000
        rerunToolPolicy: record
    - id: trajectory-debug-remotes
      name: 'dsh-trajectory-debug-remotes'
    - id: ui-trajectory-debug
      name: 'dsh-client-ui-trajectory-debug'
`
  writeFileSync(join(PROFILE, 'package.json'), JSON.stringify(pkg, null, 2))
  writeFileSync(join(PROFILE, 'cordis.patch.yml'), patch)
  // pnpm 11 supply-chain policy rejects freshly-published packages; this is a
  // scratch test profile, so the release-age gate is disabled entirely. The
  // lockfile and node_modules are dropped for a fresh, self-consistent state
  // (a previous run's failed install must not leak links into this one).
  writeFileSync(join(PROFILE, 'pnpm-workspace.yaml'), 'packages:\nminimumReleaseAge: 0\n')
  const lockfile = join(PROFILE, 'pnpm-lock.yaml')
  if (existsSync(lockfile)) rmSync(lockfile)
  const modules = join(PROFILE, 'node_modules')
  if (existsSync(modules)) rmSync(modules, { recursive: true, force: true })
}

console.log('[smoke] building workspace…')
run('corepack', ['pnpm', '-r', 'build'], { cwd: ROOT })

if (!existsSync(BIN)) throw new Error(`dsh bin not found: ${BIN}`)
mkdirSync(PROFILE, { recursive: true })
stagePackages()
profileFiles()
console.log(`[smoke] installing profile deps (${PROFILE})…`)
run('corepack', ['pnpm', 'install'], { cwd: PROFILE, shell: true })

console.log('[smoke] verifying composed tree…')
const dump = run('node', [BIN, '--profile', 'td-smoke', '--dump-config'])
for (const id of ['trajectory-debug-host', 'trajectory-debug-remotes', 'ui-trajectory-debug']) {
  if (!dump.stdout.includes(id)) throw new Error(`row ${id} missing from composed tree`)
}
console.log('[smoke] rows present: trajectory-debug-host / -remotes / ui-trajectory-debug')

console.log('[smoke] booting profile (expecting clean idle for', BOOT_WAIT_MS / 1000, 's)…')
const child = spawn('node', [BIN, '--profile', 'td-smoke'], { stdio: ['ignore', 'pipe', 'pipe'] })
let output = ''
child.stdout.on('data', (d) => (output += d))
child.stderr.on('data', (d) => (output += d))
const settled = await new Promise((resolveSettle) => {
  child.on('exit', (code) => resolveSettle({ code }))
  setTimeout(() => {
    child.kill('SIGKILL')
    resolveSettle({ code: null })
  }, BOOT_WAIT_MS)
})
if (settled.code !== null) {
  console.error(output)
  throw new Error(`boot exited early with code ${settled.code} — plugin tree failed to load`)
}
if (/Error|TypeError|failed to load/i.test(output)) {
  console.error(output)
  throw new Error('boot produced errors')
}
console.log('[smoke] OK: plugin tree loaded and stayed alive; no boot errors')
console.log(output.trim() ? `[smoke] boot output:\n${output.trim()}` : '[smoke] (no output — clean idle)')
