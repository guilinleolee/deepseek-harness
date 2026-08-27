#!/usr/bin/env node
/**
 * Pre-publish manifest validation.
 *
 * Asserts every publishable package is ready for npm:
 * - no `file:` dependency specifiers (they cannot resolve on the registry);
 * - a valid semantic version;
 * - the bundle ships its runtime entry plus the patch file.
 *
 * `workspace:*` is the canonical monorepo form: pnpm rewrites it to the
 * package's version at publish time, so it is allowed here.
 *
 * Usage: node scripts/verify-publish.mjs
 */

import { readFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const PACKAGES = ['trajectory-debug', 'trajectory-debug-host', 'trajectory-debug-remotes', 'client-ui-trajectory-debug', 'trajectory-debug-bundle']

let failed = false
for (const name of PACKAGES) {
  const file = join(ROOT, 'packages', name, 'package.json')
  const manifest = JSON.parse(readFileSync(file, 'utf8'))
  const problems = []
  const deps = { ...manifest.dependencies, ...manifest.peerDependencies, ...manifest.devDependencies }
  for (const [dep, spec] of Object.entries(deps)) {
    if (typeof spec === 'string' && spec.startsWith('file:')) {
      problems.push(`file: dependency "${dep}" (publish requires version ranges or workspace:*)`)
    }
  }
  if (!/^\d+\.\d+\.\d+(-.+)?$/.test(manifest.version ?? '')) {
    problems.push(`invalid version "${manifest.version}"`)
  }
  if (name === 'trajectory-debug-bundle') {
    if (!(manifest.files ?? []).includes('cordis.patch.yml')) problems.push('bundle missing cordis.patch.yml in files')
    if (!(manifest.files ?? []).includes('index.js')) problems.push('bundle missing index.js in files')
    if (manifest.dsh?.bundle?.patch !== './cordis.patch.yml') problems.push('bundle missing dsh.bundle.patch')
  }
  if (problems.length > 0) {
    failed = true
    console.error(`[verify-publish] ${name}:`)
    for (const problem of problems) console.error(`  - ${problem}`)
  } else {
    console.log(`[verify-publish] ok: ${name}@${manifest.version}`)
  }
}
if (failed) {
  console.error('[verify-publish] FAILED')
  process.exit(1)
}
console.log('[verify-publish] all packages ready for publish')
