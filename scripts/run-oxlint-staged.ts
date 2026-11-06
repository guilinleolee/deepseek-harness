/**
 * Run Oxlint over the files staged for the pending commit, in bounded chunks.
 *
 * The lefthook job used to expand `{staged_files}` inline; a large staging set
 * overflows the Windows command-line limit, and the failure mode depends on the
 * caller: the spawn dies with `Argument list too long`, or Oxlint receives a
 * truncated list and reports success over fewer files than it was handed — a
 * false pass. Reading the list from the index and chunking keeps the gate real
 * at any staging size.
 *
 * `--fix` and the other Oxlint flags pass through; after a fixing run the
 * touched staged files are re-added so the commit carries the fixes.
 *
 * @module scripts/run-oxlint-staged
 */

import { spawnSync } from 'node:child_process'
import { resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { resolveOxlintInvocation } from './run-oxlint.ts'

const oxlintCli = fileURLToPath(new URL('../node_modules/oxlint/bin/oxlint', import.meta.url))

/** Files per Oxlint invocation; a chunk stays far below every argv limit. */
const CHUNK_SIZE = 150

/** Extensions the lint gate covers, mirroring the lefthook job's old glob. */
const LINTED_EXTENSIONS = new Set(['.ts', '.tsx', '.mts', '.cts', '.mjs'])

/** One line of `git diff --cached --name-only -z` output for a linted file. */
function stagedLintFiles(): string[] {
  const result = spawnSync('git', ['diff', '--cached', '--name-only', '-z', '--diff-filter=ACMR'], {
    encoding: 'utf8',
    maxBuffer: 64 * 1024 * 1024,
  })
  if (result.error !== undefined) throw result.error
  if (result.status !== 0) {
    throw new Error(`run-oxlint-staged: git diff --cached failed with status ${result.status}.`)
  }
  return (result.stdout ?? '')
    .split('\0')
    .filter((f) => f !== '' && LINTED_EXTENSIONS.has(f.slice(f.lastIndexOf('.'))))
    .filter((f) => !f.startsWith('vendor/') || !/^vendor\/[^/]+\/src\//.test(f))
}

/**
 * Run one Oxlint chunk.
 * @param files - the chunk's files, passed as one argument each.
 * @param passArgs - caller flags (`--config …`, `--fix`, …).
 * @returns whether Oxlint exited clean.
 */
function runChunk(files: readonly string[], passArgs: readonly string[]): boolean {
  const invocation = resolveOxlintInvocation([...passArgs, ...files], process.env)
  const result = spawnSync(process.execPath, [oxlintCli, ...invocation.args], {
    encoding: 'utf8',
    env: invocation.env,
    maxBuffer: 64 * 1024 * 1024,
    stdio: ['ignore', 'pipe', 'pipe'],
  })
  process.stdout.write(result.stdout ?? '')
  process.stderr.write(result.stderr ?? '')
  return result.status === 0
}

/** Re-stage the linted files so an applied `--fix` lands in the commit. */
function restage(files: readonly string[]): void {
  for (let i = 0; i < files.length; i += CHUNK_SIZE) {
    const result = spawnSync('git', ['add', '--', ...files.slice(i, i + CHUNK_SIZE)])
    if (result.status !== 0) throw new Error(`run-oxlint-staged: git add failed for chunk ${i}.`)
  }
}

function main(): void {
  const passArgs = process.argv.slice(2)
  const files = stagedLintFiles()
  let clean = true
  for (let i = 0; i < files.length; i += CHUNK_SIZE) {
    if (!runChunk(files.slice(i, i + CHUNK_SIZE), passArgs)) clean = false
  }
  if (clean) {
    console.log(`run-oxlint-staged: ${files.length} staged file(s) lint clean.`)
    return
  }
  if (passArgs.includes('--fix')) restage(files)
  process.exitCode = 1
}

const entrypoint = process.argv[1]
if (entrypoint !== undefined && resolve(entrypoint) === fileURLToPath(import.meta.url)) main()
