/**
 * Behavioral tests for the deliverable skill library gate.
 */

import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
import { inspectDeliverableSkills } from './verify-dragon-deliverable-skills.ts'

const REPO_ROOT = resolve(import.meta.dirname, '..')

/** Build a repository copy the gate can inspect. */
function makeRepo(manifest: unknown, registry: unknown = { skills: {} }): string {
  const root = mkdtempSync(join(tmpdir(), 'dragon-deliverable-'))
  mkdirSync(resolve(root, 'dragon-assets/index'), { recursive: true })
  writeFileSync(
    resolve(root, 'dragon-assets/index/DELIVERABLE_SKILLS.json'),
    typeof manifest === 'string' ? manifest : JSON.stringify(manifest),
    'utf8',
  )
  writeFileSync(
    resolve(root, 'dragon-assets/index/LICENSES.json'),
    typeof registry === 'string' ? registry : JSON.stringify(registry),
    'utf8',
  )
  return root
}

describe('inspectDeliverableSkills', () => {
  it('accepts the repository manifest', () => {
    const report = inspectDeliverableSkills(REPO_ROOT)
    expect(report.failures).toEqual([])
    expect(report.deliverableCount).toBeGreaterThan(0)
    expect(report.withheldCount).toBeGreaterThan(0)
  })

  it('fails when the manifest is missing', () => {
    const root = mkdtempSync(join(tmpdir(), 'dragon-deliverable-'))
    try {
      const report = inspectDeliverableSkills(root)
      expect(report.failures.join('\n')).toContain('does not exist')
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('rejects an AGPL asset in the deliverable set', () => {
    const root = makeRepo({
      deliverable: [{ id: 'guizang', tier: 'AGPL-3.0', decision: 'artifact-only', commercial_use: 'deliverable-only', obligations: [] }],
      withheld: [],
      violations: [],
    })
    try {
      const report = inspectDeliverableSkills(root)
      expect(report.failures.join('\n')).toContain('may not enter a client library')
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('rejects a NonCommercial asset in the deliverable set', () => {
    const root = makeRepo({
      deliverable: [{ id: 'opc-methodology', tier: 'CC-BY-NC-SA-4.0', decision: 'reject', commercial_use: 'no', obligations: [] }],
      withheld: [],
      violations: [],
    })
    try {
      const report = inspectDeliverableSkills(root)
      expect(report.failures.join('\n')).toContain('may not enter a client library')
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('rejects a proprietary asset in the deliverable set', () => {
    const root = makeRepo({
      deliverable: [{ id: 'docx', tier: 'proprietary', decision: 'reject', commercial_use: 'no', obligations: [] }],
      withheld: [],
      violations: [],
    })
    try {
      const report = inspectDeliverableSkills(root)
      expect(report.failures.join('\n')).toContain('may not enter a client library')
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('rejects an unverified tier in the deliverable set', () => {
    const root = makeRepo({
      deliverable: [{ id: 'mystery', tier: 'unknown', decision: 'attribute', commercial_use: 'unverified', obligations: [] }],
      withheld: [],
      violations: [],
    })
    try {
      const report = inspectDeliverableSkills(root)
      expect(report.failures.join('\n')).toContain('is not a deliverable tier')
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('rejects a deliverable entry whose commercial_use says no', () => {
    const root = makeRepo({
      deliverable: [{ id: 'odd', tier: 'MIT', decision: 'allow', commercial_use: 'no', obligations: [] }],
      withheld: [],
      violations: [],
    })
    try {
      const report = inspectDeliverableSkills(root)
      expect(report.failures.join('\n')).toContain("commercial_use says 'no'")
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('rejects a manifest that does not cover every registry entry', () => {
    const root = makeRepo(
      {
        deliverable: [{ id: 'kept', tier: 'MIT', decision: 'allow', commercial_use: 'yes', obligations: [] }],
        withheld: [],
        violations: [],
      },
      { skills: { kept: { license: 'MIT' }, dropped: { license: 'MIT' } } },
    )
    try {
      const report = inspectDeliverableSkills(root)
      expect(report.failures.join('\n')).toContain('does not cover')
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('surfaces a violation the generator reported', () => {
    const root = makeRepo({
      deliverable: [],
      withheld: [],
      violations: ['some-skill: license "Mystery" is not a known tier'],
    })
    try {
      const report = inspectDeliverableSkills(root)
      expect(report.failures.join('\n')).toContain('reports a violation')
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })
})
