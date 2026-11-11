/**
 * Enforce that the deliverable skill library contains only assets a client
 * inner network may legally hold.
 *
 * A client library holds the skill itself, not a produced artifact. That
 * distinction decides three tiers:
 *
 *   - AGPL-3.0 may be delivered as a produced PNG (the section 13 exemption),
 *     but the skill may not sit in a client library or run as a service for a
 *     client.
 *   - NonCommercial licences forbid commercial use, so the asset may not enter
 *     a paid delivery at all.
 *   - Proprietary licences forbid redistribution to any third party.
 *
 * This gate reads the generated manifest and the license registry, then fails
 * when a withheld asset appears in the deliverable set, when a withheld asset
 * carries a tier the manifest treats as deliverable, or when the manifest has
 * drifted from the registry.
 *
 * @module scripts/verify-dragon-deliverable-skills
 */

import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'

const ROOT = resolve(import.meta.dirname, '..')

/** Tiers a client inner-network library may hold. */
const DELIVERABLE_TIERS = new Set(['MIT', 'Apache-2.0', 'BSD-3-Clause', 'self'])

/** Tiers that must never reach a client library. */
const WITHHELD_TIERS = new Set([
  'AGPL-3.0',
  'CC-BY-NC-4.0',
  'CC-BY-NC-SA-4.0',
  'proprietary',
  'noassertion',
])

/** One deliverable-set record. */
interface ManifestRecord {
  id: string
  tier: string
  decision: string
  commercial_use: string
  obligations: string[]
}

/** One manifest entry, normalized. */
interface ManifestEntry {
  id: string
  tier: string
  decision: string
  commercialUse: string
  obligations: string[]
}

/** Result of the deliverable-skills gate. */
export interface DeliverableSkillsReport {
  /** Number of deliverable records inspected. */
  deliverableCount: number
  /** Number of withheld records inspected. */
  withheldCount: number
  /** Repository-relative diagnostics. */
  failures: string[]
}

function readJson(path: string): unknown {
  return JSON.parse(readFileSync(path, 'utf8'))
}

function toEntries(value: unknown): ManifestEntry[] {
  if (!Array.isArray(value)) return []
  const entries: ManifestEntry[] = []
  for (const record of value as ManifestRecord[]) {
    entries.push({
      id: String(record.id ?? ''),
      tier: String(record.tier ?? ''),
      decision: String(record.decision ?? ''),
      commercialUse: String(record.commercial_use ?? ''),
      obligations: Array.isArray(record.obligations) ? record.obligations.map((item) => String(item)) : [],
    })
  }
  return entries
}

/**
 * Check the deliverable skill library manifest against the license registry.
 * @param root - absolute repository root.
 * @returns the inspected counts and every diagnostic.
 */
export function inspectDeliverableSkills(root: string): DeliverableSkillsReport {
  const manifestPath = resolve(root, 'dragon-assets/index/DELIVERABLE_SKILLS.json')
  const registryPath = resolve(root, 'dragon-assets/index/LICENSES.json')
  const failures: string[] = []

  if (!existsSync(manifestPath)) {
    return {
      deliverableCount: 0,
      withheldCount: 0,
      failures: [
        'dragon-assets/index/DELIVERABLE_SKILLS.json does not exist; run dragon-assets/runtime/scripts/build-deliverable-skills.py',
      ],
    }
  }

  const manifest = readJson(manifestPath) as {
    deliverable?: unknown
    withheld?: unknown
    violations?: unknown
  }
  const deliverable = toEntries(manifest.deliverable)
  const withheld = toEntries(manifest.withheld)

  // A withheld tier must never appear in the deliverable set.
  for (const entry of deliverable) {
    if (WITHHELD_TIERS.has(entry.tier)) {
      failures.push(
        `DELIVERABLE_SKILLS.json: ${entry.id} has tier ${entry.tier}, which may not enter a client library.`,
      )
    }
    if (!DELIVERABLE_TIERS.has(entry.tier)) {
      failures.push(
        `DELIVERABLE_SKILLS.json: ${entry.id} has tier ${entry.tier}, which is not a deliverable tier.`,
      )
    }
    if (entry.commercialUse === 'no') {
      failures.push(
        `DELIVERABLE_SKILLS.json: ${entry.id} is listed as deliverable, but commercial_use says 'no'.`,
      )
    }
  }

  // A withheld record must carry a tier the policy refuses.
  for (const entry of withheld) {
    if (!WITHHELD_TIERS.has(entry.tier)) {
      failures.push(
        `DELIVERABLE_SKILLS.json: ${entry.id} is withheld but its tier ${entry.tier} is not a refusal tier.`,
      )
    }
  }

  // The manifest must not have drifted from the registry.
  const registry = readJson(registryPath) as { skills?: Record<string, unknown> }
  const registrySkills = registry.skills ?? {}
  const registryIds = Object.keys(registrySkills)
  const covered = new Set([...deliverable, ...withheld].map((entry) => entry.id))
  const missing = registryIds.filter((id) => !covered.has(id))
  if (missing.length > 0) {
    failures.push(
      `DELIVERABLE_SKILLS.json does not cover ${String(missing.length)} registry entries: ${missing.slice(0, 5).join(', ')}`,
    )
  }

  const violations = Array.isArray(manifest.violations) ? manifest.violations : []
  for (const violation of violations) {
    failures.push(`DELIVERABLE_SKILLS.json reports a violation: ${String(violation)}`)
  }

  return {
    deliverableCount: deliverable.length,
    withheldCount: withheld.length,
    failures,
  }
}

if (process.argv[1] && import.meta.filename === resolve(process.argv[1])) {
  const report = inspectDeliverableSkills(ROOT)
  if (report.failures.length > 0) {
    process.stderr.write('verify-dragon-deliverable-skills: deliverable library problems found:\n')
    for (const failure of report.failures) process.stderr.write(`  ${failure}\n`)
    process.exitCode = 1
  } else {
    process.stdout.write(
      `verify-dragon-deliverable-skills: ${String(report.deliverableCount)} deliverable, ${String(report.withheldCount)} withheld; the client library holds only redistributable assets.\n`,
    )
  }
}
