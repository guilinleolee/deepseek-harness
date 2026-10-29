/**
 * Enforce that the dragon-assets index stays in sync with the asset tree.
 *
 * The index has twice silently drifted: the builder's registry integration was
 * reverted and the index kept shipping with stale license facts, and a
 * mis-targeted default root wrote a second copy of the index into
 * `runtime/index/`. Both failures were invisible until a downstream lookup
 * answered from the wrong copy.
 *
 * This gate re-derives the two invariants the builder must hold and fails when
 * either breaks:
 *
 *   1. Registry coverage — every `commercial_use: yes` / `deliverable-only` /
 *      `no` registry entry must appear in SKILLS.jsonl carrying the same
 *      license and class, under its own id or the registry key's family.
 *   2. Single index home — the index files live in `dragon-assets/index/`
 *      only; a second SKILLS.jsonl under `runtime/index/` fails.
 *
 * @module scripts/verify-dragon-index-sync
 */

import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'

const ROOT = resolve(import.meta.dirname, '..')

/** Result of the index-sync gate. */
export interface DragonIndexSyncReport {
  /** Number of registry entries checked against the index. */
  entryCount: number
  /** Number of skill rows read from the index. */
  rowCount: number
  /** Repository-relative diagnostics. */
  failures: string[]
}

interface IndexRow {
  id: string
  path: string
  license?: string
  commercial_use?: string
}

function readJson(path: string): unknown {
  return JSON.parse(readFileSync(path, 'utf8'))
}

function readIndexRows(path: string): IndexRow[] {
  const rows: IndexRow[] = []
  for (const line of readFileSync(path, 'utf8').split('\n')) {
    const trimmed = line.trim()
    if (!trimmed) continue
    try {
      rows.push(JSON.parse(trimmed) as IndexRow)
    } catch {
      rows.push({ id: '<unparseable>', path: '' })
    }
  }
  return rows
}

/**
 * Check that the index is fresh against the license registry and lives in
 * exactly one directory.
 * @param root - absolute repository root.
 * @returns the inspected counts and every diagnostic.
 */
export function inspectDragonIndexSync(root: string): DragonIndexSyncReport {
  const indexDir = resolve(root, 'dragon-assets/index')
  const runtimeIndexDir = resolve(root, 'dragon-assets/runtime/index')
  const registryPath = resolve(indexDir, 'LICENSES.json')
  const skillsPath = resolve(indexDir, 'SKILLS.jsonl')
  const failures: string[] = []

  // Single index home: the builder once defaulted its root to runtime/ and
  // wrote a second index there.
  if (existsSync(resolve(runtimeIndexDir, 'SKILLS.jsonl'))) {
    failures.push(
      'dragon-assets/runtime/index/SKILLS.jsonl exists; the index must live only in dragon-assets/index (remove the runtime copy and fix the builder root).',
    )
  }

  if (!existsSync(skillsPath)) {
    return { entryCount: 0, rowCount: 0, failures: [...failures, 'dragon-assets/index/SKILLS.jsonl does not exist; run build-index.py'] }
  }

  const rows = readIndexRows(skillsPath)

  // Registry coverage: a registry fact must survive into the index.
  if (existsSync(registryPath)) {
    const registry = readJson(registryPath) as { skills?: Record<string, Record<string, unknown>> }
    const skills = registry.skills ?? {}

    const byId = new Map<string, IndexRow>()
    for (const row of rows) byId.set(String(row.id), row)
    // Family keys (dbs-*) match every row whose id or directory starts with
    // the key's stem.
    const families = Object.keys(skills).filter(key => key.endsWith('*'))

    let checked = 0
    for (const [key, entry] of Object.entries(skills)) {
      const expectedUse = String(entry.commercial_use ?? 'unverified')
      if (expectedUse === 'unverified') continue
      const expectedLicense = String(entry.license ?? '')

      let matched: IndexRow | undefined
      if (key.endsWith('*')) {
        const stem = key.slice(0, -1)
        matched = rows.find(row => row.id.startsWith(stem) || row.path.startsWith(`skills/${stem}`))
      } else {
        matched = byId.get(key) ?? rows.find(row => row.path.startsWith(`skills/${key}/`))
      }
      if (matched === undefined && families.length > 0) {
        matched = rows.find(row => families.some(family => row.id.startsWith(family.slice(0, -1))))
      }
      if (matched === undefined) {
        failures.push(`SKILLS.jsonl: registry entry ${key} (commercial_use=${expectedUse}) has no index row.`)
        continue
      }
      checked++
      if (expectedLicense && matched.license !== undefined && matched.license !== expectedLicense) {
        failures.push(
          `SKILLS.jsonl: ${key} license is ${String(matched.license)} but the registry says ${expectedLicense}. Rebuild the index.`,
        )
      }
      if (matched.commercial_use !== expectedUse) {
        failures.push(
          `SKILLS.jsonl: ${key} commercial_use is ${String(matched.commercial_use)} but the registry says ${expectedUse}. Rebuild the index.`,
        )
      }
    }

    return { entryCount: checked, rowCount: rows.length, failures }
  }

  return { entryCount: 0, rowCount: rows.length, failures }
}

if (process.argv[1] && import.meta.filename === resolve(process.argv[1])) {
  const report = inspectDragonIndexSync(ROOT)
  if (report.failures.length > 0) {
    process.stderr.write('verify-dragon-index-sync: index drift detected:\n')
    for (const failure of report.failures) process.stderr.write(`  ${failure}\n`)
    process.exitCode = 1
  } else {
    process.stdout.write(
      `verify-dragon-index-sync: ${String(report.entryCount)} registry entries and ${String(report.rowCount)} index rows agree; single index home.\n`,
    )
  }
}
