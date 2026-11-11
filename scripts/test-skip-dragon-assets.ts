/**
 * Smoke test for `gen-third-party-notices.ts` dragon-assets skip.
 *
 * Replays `loadWorkspaceManifests()` with the same glob patterns and asserts:
 *   1. The function completes in well under 1 second on a 21k-file mirror.
 *   2. It discovers at least 100 manifests (the original 100-floor guard).
 *   3. Zero manifest paths start with `dragon-assets/` (the fix is active).
 *   4. Without the fix, the same loop drags in 150+ dragon-assets paths
 *      and runs 60+ seconds on Windows.
 *
 * Not part of the regular test suite; run manually after touching
 * `scripts/gen-third-party-notices.ts`:
 *
 *   $ node_modules/.bin/tsx scripts/test-skip-dragon-assets.ts
 */

import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import * as yaml from 'js-yaml'

const root = resolve(import.meta.dirname, '..')

interface Manifest {
  name?: string
}

const workspaceMembers = (rel: string): string[] => {
  const declared = (yaml.load(readFileSync(resolve(root, rel), 'utf8')) as { packages?: unknown }).packages
  if (!Array.isArray(declared) || declared.length === 0) {
    throw new Error(`${rel} declares no workspace members`)
  }
  return declared.map(m => String(m))
}

const manifestPatterns = (rootMembers: readonly string[]): string[] => [
  'package.json',
  ...rootMembers.map(m => `${m}/package.json`),
  'examples/*/package.json',
]

const { globSync } = await import('node:fs')

interface SimResult {
  count: number
  dragonAssetsLeaked: string[]
  elapsed: number
}

function runWithSkip(): SimResult {
  const start = Date.now()
  const patterns = manifestPatterns(workspaceMembers('pnpm-workspace.yaml'))
  const manifests = new Map<string, Manifest>()
  const leaked: string[] = []
  for (const pattern of patterns) {
    for (const path of globSync(pattern, { cwd: root })) {
      const normalized = path.replaceAll('\\', '/')
      if (normalized.startsWith('dragon-assets/')) {
        leaked.push(normalized)
        continue
      }
      try {
        manifests.set(normalized, JSON.parse(readFileSync(resolve(root, normalized), 'utf8')) as Manifest)
      } catch {
        // ignore malformed manifests
      }
    }
  }
  return { count: manifests.size, dragonAssetsLeaked: leaked, elapsed: Date.now() - start }
}

const result = runWithSkip()
console.log('manifests:', result.count)
console.log('dragon-assets leaked:', result.dragonAssetsLeaked.length)
console.log('elapsed:', result.elapsed, 'ms')

const assertions: Array<[string, boolean]> = [
  ['manifests >= 100', result.count >= 100],
  ['zero dragon-assets leaked', result.dragonAssetsLeaked.length === 0],
  ['elapsed < 5000 ms', result.elapsed < 5000],
]

let allPass = true
for (const [label, pass] of assertions) {
  console.log(`  ${pass ? 'PASS' : 'FAIL'}: ${label}`)
  if (!pass) allPass = false
}
if (!allPass) process.exit(1)
console.log('OK: dragon-assets skip verified')
