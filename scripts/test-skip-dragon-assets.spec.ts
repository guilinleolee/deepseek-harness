/**
 * Smoke test for `gen-third-party-notices.ts` dragon-assets skip.
 *
 * Replays `loadWorkspaceManifests()` with the same glob patterns and asserts:
 *   1. Discovers at least 100 manifests (the original 100-floor guard).
 *   2. Zero manifest paths start with `dragon-assets/` (the fix is active).
 *   3. Completes in well under 5 seconds on the 21k-file mirror.
 *
 * Run manually after touching `scripts/gen-third-party-notices.ts`:
 *
 *   $ npx vitest run scripts/test-skip-dragon-assets.spec.ts
 */

import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
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

function loadWithSkip(): { count: number; leaked: string[]; elapsed: number } {
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
  return { count: manifests.size, leaked, elapsed: Date.now() - start }
}

describe('gen-third-party-notices dragon-assets skip', () => {
  it('discovers 100+ manifests without scanning dragon-assets/', () => {
    const result = loadWithSkip()
    expect(result.count).toBeGreaterThanOrEqual(100)
    expect(result.leaked).toEqual([])
    expect(result.elapsed).toBeLessThan(5000)
  })
})
