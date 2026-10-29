/**
 * Behavioral tests for the dragon-assets index-sync gate.
 */

import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
import { inspectDragonIndexSync } from './verify-dragon-index-sync.ts'

const REPO_ROOT = resolve(import.meta.dirname, '..')

function skillRow(id: string, license: string, commercialUse: string, path: string): string {
  return JSON.stringify({ schema: 'dragon-index/1.0', id, kind: 'skill', license, commercial_use: commercialUse, path })
}

/** Build a repository copy the gate can inspect. */
function makeRepo(files: Record<string, string>): string {
  const root = mkdtempSync(join(tmpdir(), 'dragon-index-sync-'))
  for (const [relative, content] of Object.entries(files)) {
    const target = resolve(root, relative)
    mkdirSync(resolve(target, '..'), { recursive: true })
    writeFileSync(target, content, 'utf8')
  }
  return root
}

describe('inspectDragonIndexSync', () => {
  it('accepts the repository index', () => {
    const report = inspectDragonIndexSync(REPO_ROOT)
    expect(report.failures).toEqual([])
    expect(report.entryCount).toBeGreaterThan(0)
    expect(report.rowCount).toBeGreaterThan(0)
  })

  it('rejects a second index under runtime/', () => {
    const root = makeRepo({
      'dragon-assets/index/SKILLS.jsonl': `${skillRow('a', 'MIT', 'yes', 'skills/a/SKILL.md')}\n`,
      'dragon-assets/index/LICENSES.json': JSON.stringify({ skills: { a: { license: 'MIT', commercial_use: 'yes' } } }),
      'dragon-assets/runtime/index/SKILLS.jsonl': `${skillRow('a', 'unknown', 'unverified', 'skills/a/SKILL.md')}\n`,
    })
    try {
      const report = inspectDragonIndexSync(root)
      expect(report.failures.join('\n')).toContain('runtime/index/SKILLS.jsonl exists')
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('rejects a registry entry with no index row', () => {
    const root = makeRepo({
      'dragon-assets/index/SKILLS.jsonl': `${skillRow('a', 'MIT', 'yes', 'skills/a/SKILL.md')}\n`,
      'dragon-assets/index/LICENSES.json': JSON.stringify({
        skills: { a: { license: 'MIT', commercial_use: 'yes' }, gone: { license: 'MIT', commercial_use: 'yes' } },
      }),
    })
    try {
      const report = inspectDragonIndexSync(root)
      expect(report.failures.join('\n')).toContain('registry entry gone')
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('rejects a stale license in the index', () => {
    const root = makeRepo({
      'dragon-assets/index/SKILLS.jsonl': `${skillRow('a', 'unknown', 'yes', 'skills/a/SKILL.md')}\n`,
      'dragon-assets/index/LICENSES.json': JSON.stringify({ skills: { a: { license: 'MIT', commercial_use: 'yes' } } }),
    })
    try {
      const report = inspectDragonIndexSync(root)
      expect(report.failures.join('\n')).toContain('Rebuild the index')
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('rejects a stale commercial_use in the index', () => {
    const root = makeRepo({
      'dragon-assets/index/SKILLS.jsonl': `${skillRow('a', 'MIT', 'unverified', 'skills/a/SKILL.md')}\n`,
      'dragon-assets/index/LICENSES.json': JSON.stringify({ skills: { a: { license: 'MIT', commercial_use: 'yes' } } }),
    })
    try {
      const report = inspectDragonIndexSync(root)
      expect(report.failures.join('\n')).toContain('commercial_use')
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('matches a family key against a prefixed row', () => {
    const root = makeRepo({
      'dragon-assets/index/SKILLS.jsonl': `${skillRow('dbs-action', 'CC-BY-NC-4.0', 'no', 'skills/dbs-action/SKILL.md')}\n`,
      'dragon-assets/index/LICENSES.json': JSON.stringify({ skills: { 'dbs-*': { license: 'CC-BY-NC-4.0', commercial_use: 'no' } } }),
    })
    try {
      const report = inspectDragonIndexSync(root)
      expect(report.failures).toEqual([])
      expect(report.entryCount).toBe(1)
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('ignores registry entries that are unverified', () => {
    const root = makeRepo({
      'dragon-assets/index/SKILLS.jsonl': `${skillRow('a', 'MIT', 'yes', 'skills/a/SKILL.md')}\n`,
      'dragon-assets/index/LICENSES.json': JSON.stringify({
        skills: { a: { license: 'MIT', commercial_use: 'yes' }, mystery: { license: 'unknown', commercial_use: 'unverified' } },
      }),
    })
    try {
      const report = inspectDragonIndexSync(root)
      expect(report.failures).toEqual([])
      expect(report.entryCount).toBe(1)
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('fails when the index file is missing', () => {
    const root = makeRepo({
      'dragon-assets/index/LICENSES.json': JSON.stringify({ skills: {} }),
    })
    try {
      const report = inspectDragonIndexSync(root)
      expect(report.failures.join('\n')).toContain('does not exist')
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })
})
