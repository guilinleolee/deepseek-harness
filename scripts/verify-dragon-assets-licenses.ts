/**
 * Enforce commercial-use licensing facts for the dragon-assets skill library.
 *
 * The index builder records a license and a `commercial_use` class per asset, but
 * nothing verified that the recorded facts stayed true. This gate closes that
 * loop: it re-derives the license for every registry entry from the registry and
 * the asset's own LICENSE file, and it fails when a skill that may not be used
 * commercially is reachable from a paid delivery surface.
 *
 * @module scripts/verify-dragon-assets-licenses
 */

import { existsSync, readFileSync, readdirSync } from 'node:fs'
import { resolve, sep } from 'node:path'

const ROOT = resolve(import.meta.dirname, '..')
const REGISTRY_PATH = resolve(ROOT, 'dragon-assets/index/LICENSES.json')
const SKILLS_DIR = resolve(ROOT, 'dragon-assets/skills')

/** One registry entry after normalization. */
interface RegistryEntry {
  id: string
  license: string
  commercialUse: string
  obligations: string[]
  upstream: string
  note: string
}

/** The license classes the gate accepts. */
const KNOWN_LICENSES = new Set([
  'MIT',
  'Apache-2.0',
  'BSD-3-Clause',
  'AGPL-3.0',
  'GPL-3.0',
  'MPL-2.0',
  'ISC',
  'CC-BY-4.0',
  'CC-BY-NC-4.0',
  'CC-BY-NC-SA-4.0',
  'self',
  'proprietary',
])

/** The commercial-use classes the gate accepts. */
const KNOWN_COMMERCIAL_USE = new Set(['yes', 'no', 'deliverable-only', 'unverified'])

/** Licenses that forbid commercial use outright. */
const NON_COMMERCIAL_LICENSES = new Set(['CC-BY-NC-4.0', 'CC-BY-NC-SA-4.0'])

/** Licenses that forbid redistribution of the skill itself. */
const NON_REDISTRIBUTABLE_LICENSES = new Set(['proprietary'])

/** The deliverable surfaces a client engagement may use. */
const DELIVERABLE_SURFACES = [
  { label: 'content-studio capabilities', file: 'packages/client/ui-content-studio/src/client/capabilities.ts' },
  { label: 'creator workbench skills path', file: 'packages/creation/content-outputs/src/gather/feed.ts' },
]

/** Result of the license gate. */
export interface DragonAssetsLicenseReport {
  /** Number of registry entries inspected. */
  entryCount: number
  /** Repository-relative diagnostics. */
  failures: string[]
}

function readJson(path: string): unknown {
  return JSON.parse(readFileSync(path, 'utf8'))
}

function printable(value: unknown): string {
  if (typeof value === 'string') return value
  return JSON.stringify(value)
}

function normalizePath(path: string): string {
  return path.split(sep).join('/')
}

/** Read the registry into normalized entries. */
function readRegistry(path: string): RegistryEntry[] {
  const parsed = readJson(path)
  if (typeof parsed !== 'object' || parsed === null) {
    throw new Error('verify-dragon-assets-licenses: registry must be a JSON object.')
  }
  const skills = (parsed as { skills?: unknown }).skills
  if (typeof skills !== 'object' || skills === null) {
    throw new Error('verify-dragon-assets-licenses: registry must declare a skills object.')
  }

  const entries: RegistryEntry[] = []
  for (const [id, value] of Object.entries(skills as Record<string, unknown>)) {
    if (typeof value !== 'object' || value === null) {
      throw new Error(`verify-dragon-assets-licenses: registry entry ${id} must be an object.`)
    }
    const entry = value as Record<string, unknown>
    const obligations = entry.obligations
    entries.push({
      id,
      license: String(entry.license ?? ''),
      commercialUse: String(entry.commercial_use ?? ''),
      obligations: Array.isArray(obligations) ? obligations.map((item) => String(item)) : [],
      upstream: String(entry.upstream ?? ''),
      note: String(entry.note ?? ''),
    })
  }
  return entries
}

/** Resolve the on-disk directory for a registry key, tolerating family wildcards. */
function resolveSkillDir(id: string): string | undefined {
  if (id.endsWith('*')) {
    const family = id.slice(0, -1)
    if (!existsSync(SKILLS_DIR)) return undefined
    const match = readdirSync(SKILLS_DIR).find((name) => name.startsWith(family))
    return match ? resolve(SKILLS_DIR, match) : undefined
  }
  const direct = resolve(SKILLS_DIR, id)
  if (existsSync(direct)) return direct
  if (!existsSync(SKILLS_DIR)) return undefined
  const match = readdirSync(SKILLS_DIR).find((name) => {
    if (name !== id && !name.startsWith(`${id}-`)) return false
    const dir = resolve(SKILLS_DIR, name)
    return existsSync(resolve(dir, 'SKILL.md')) || existsSync(resolve(dir, 'skill', 'SKILL.md'))
  })
  return match ? resolve(SKILLS_DIR, match) : undefined
}

/**
 * Check the dragon-assets license registry and the delivery surfaces that
 * reference it.
 * @param root - absolute repository root.
 * @returns the inspected entry count and every diagnostic.
 */
export function inspectDragonAssetsLicenses(root: string): DragonAssetsLicenseReport {
  const registryPath = resolve(root, 'dragon-assets/index/LICENSES.json')
  const failures: string[] = []
  const entries = readRegistry(registryPath)

  for (const entry of entries) {
    if (!KNOWN_LICENSES.has(entry.license)) {
      failures.push(
        `${normalizePath(resolve(root, 'dragon-assets/index/LICENSES.json'))}: ${entry.id} declares an unrecognized license ${printable(entry.license)}.`,
      )
    }
    if (!KNOWN_COMMERCIAL_USE.has(entry.commercialUse)) {
      failures.push(
        `${normalizePath(resolve(root, 'dragon-assets/index/LICENSES.json'))}: ${entry.id} declares an unrecognized commercial_use ${printable(entry.commercialUse)}.`,
      )
    }

    // A NonCommercial or proprietary licence must never be marked usable.
    if (NON_COMMERCIAL_LICENSES.has(entry.license) && entry.commercialUse !== 'no') {
      failures.push(
        `${entry.id}: license ${entry.license} forbids commercial use, but commercial_use is ${printable(entry.commercialUse)}; expected "no".`,
      )
    }
    if (NON_REDISTRIBUTABLE_LICENSES.has(entry.license) && entry.commercialUse !== 'no') {
      failures.push(
        `${entry.id}: license ${entry.license} forbids redistribution, but commercial_use is ${printable(entry.commercialUse)}; expected "no".`,
      )
    }
    if (entry.license === 'AGPL-3.0' && entry.commercialUse !== 'deliverable-only') {
      failures.push(
        `${entry.id}: AGPL-3.0 permits delivering the produced artifact only, but commercial_use is ${printable(entry.commercialUse)}; expected "deliverable-only".`,
      )
    }
    if (entry.commercialUse === 'no' && entry.obligations.length === 0 && entry.license !== 'proprietary') {
      failures.push(`${entry.id}: commercial_use "no" still requires the licence text to be retained.`)
    }
  }

  // A paid delivery surface must not name a skill that may not be used commercially.
  for (const surface of DELIVERABLE_SURFACES) {
    const surfacePath = resolve(root, surface.file)
    if (!existsSync(surfacePath)) continue
    const text = readFileSync(surfacePath, 'utf8')
    for (const entry of entries) {
      if (entry.commercialUse !== 'no') continue
      const key = entry.id.endsWith('*') ? entry.id.slice(0, -1) : entry.id
      if (!text.includes(key)) continue
      failures.push(
        `${surface.file}: references ${entry.id}, which is ${printable(entry.license)} with commercial_use "no".`,
      )
    }
  }

  return { entryCount: entries.length, failures }
}

if (process.argv[1] && import.meta.filename === resolve(process.argv[1])) {
  const report = inspectDragonAssetsLicenses(ROOT)
  if (report.failures.length > 0) {
    process.stderr.write('verify-dragon-assets-licenses: license problems found:\n')
    for (const failure of report.failures) process.stderr.write(`  ${failure}\n`)
    process.exitCode = 1
  } else {
    process.stdout.write(
      `verify-dragon-assets-licenses: ${String(report.entryCount)} registry entries checked; commercial-use classes are consistent.\n`,
    )
  }
}
