/**
 * Behavioral tests for the dragon-assets commercial-use license gate.
 */

import { mkdtempSync, mkdirSync, writeFileSync, cpSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
import { inspectDragonAssetsLicenses } from './verify-dragon-assets-licenses.ts'

const REPO_ROOT = resolve(import.meta.dirname, '..')

/** Build a repository copy that the gate can inspect. */
function makeRepo(registry: unknown, files: Record<string, string> = {}): string {
  const root = mkdtempSync(join(tmpdir(), 'dragon-licenses-'))
  mkdirSync(resolve(root, 'dragon-assets/index'), { recursive: true })
  writeFileSync(
    resolve(root, 'dragon-assets/index/LICENSES.json'),
    typeof registry === 'string' ? registry : JSON.stringify(registry),
    'utf8',
  )
  for (const [relative, content] of Object.entries(files)) {
    const target = resolve(root, relative)
    mkdirSync(resolve(target, '..'), { recursive: true })
    writeFileSync(target, content, 'utf8')
  }
  return root
}

describe('inspectDragonAssetsLicenses', () => {
  it('accepts the repository registry', () => {
    const report = inspectDragonAssetsLicenses(REPO_ROOT)
    expect(report.failures).toEqual([])
    expect(report.entryCount).toBeGreaterThan(0)
  })

  it('rejects a NonCommercial licence marked commercially usable', () => {
    const root = makeRepo({
      skills: { 'nc-skill': { license: 'CC-BY-NC-4.0', commercial_use: 'yes', obligations: [] } },
    })
    try {
      const report = inspectDragonAssetsLicenses(root)
      expect(report.failures.join('\n')).toContain('forbids commercial use')
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('rejects a proprietary licence marked commercially usable', () => {
    const root = makeRepo({
      skills: { 'prop-skill': { license: 'proprietary', commercial_use: 'yes', obligations: [] } },
    })
    try {
      const report = inspectDragonAssetsLicenses(root)
      expect(report.failures.join('\n')).toContain('forbids redistribution')
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('rejects an AGPL licence marked unrestricted', () => {
    const root = makeRepo({
      skills: { 'agpl-skill': { license: 'AGPL-3.0', commercial_use: 'yes', obligations: ['retain-license-text'] } },
    })
    try {
      const report = inspectDragonAssetsLicenses(root)
      expect(report.failures.join('\n')).toContain('deliverable-only')
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('rejects an unrecognized license value', () => {
    const root = makeRepo({
      skills: { 'weird-skill': { license: 'Mystery-1.0', commercial_use: 'yes', obligations: [] } },
    })
    try {
      const report = inspectDragonAssetsLicenses(root)
      expect(report.failures.join('\n')).toContain('unrecognized license')
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('rejects a delivery surface that names a non-commercial skill', () => {
    const root = makeRepo(
      {
        skills: { 'blocked-skill': { license: 'CC-BY-NC-4.0', commercial_use: 'no', obligations: ['retain-license-text'] } },
      },
      {
        'packages/client/ui-content-studio/src/client/capabilities.ts':
          "export const id = 'blocked-skill'\n",
      },
    )
    try {
      const report = inspectDragonAssetsLicenses(root)
      expect(report.failures.join('\n')).toContain('references blocked-skill')
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('accepts a delivery surface that names a commercially usable skill', () => {
    const root = makeRepo(
      {
        skills: { 'allowed-skill': { license: 'MIT', commercial_use: 'yes', obligations: ['retain-license-text'] } },
      },
      {
        'packages/client/ui-content-studio/src/client/capabilities.ts':
          "export const id = 'allowed-skill'\n",
      },
    )
    try {
      const report = inspectDragonAssetsLicenses(root)
      expect(report.failures).toEqual([])
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })
})
