/**
 * Behavioral tests for the dragon-assets capability-honesty gate.
 */

import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
import { expandComponent, inspectCapabilityHonesty } from './verify-dragon-capability-honesty.ts'

const REPO_ROOT = resolve(import.meta.dirname, '..')

/** Build a repository copy the gate can inspect. */
function makeRepo(registry: unknown, files: Record<string, string> = {}): string {
  const root = mkdtempSync(join(tmpdir(), 'dragon-capability-'))
  mkdirSync(resolve(root, 'dragon-assets/index'), { recursive: true })
  writeFileSync(
    resolve(root, 'dragon-assets/index/CAPABILITY_STATUS.json'),
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

describe('expandComponent', () => {
  it('resolves a plain file', () => {
    const root = makeRepo({}, { 'a/b.txt': 'x' })
    try {
      expect(expandComponent(root, 'a/b.txt')).toEqual(['a/b.txt'])
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('expands a brace pattern', () => {
    const root = makeRepo({}, { 'a/one/x.ts': 'x', 'a/two/x.ts': 'x' })
    try {
      const files = expandComponent(root, 'a/{one,two}/x.ts')
      expect(files).toContain('a/one/x.ts')
      expect(files).toContain('a/two/x.ts')
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('returns nothing for a missing path', () => {
    const root = makeRepo({})
    try {
      expect(expandComponent(root, 'nope/missing.ts')).toEqual([])
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })
})

describe('inspectCapabilityHonesty', () => {
  it('accepts the repository registry', () => {
    const report = inspectCapabilityHonesty(REPO_ROOT)
    expect(report.failures).toEqual([])
    expect(report.entryCount).toBeGreaterThan(0)
  })

  it('rejects an unrecognized status', () => {
    const root = makeRepo({
      paths: { 'a-path': { status: 'magic', component: 'x.ts', reason: '' } },
    })
    try {
      const report = inspectCapabilityHonesty(root)
      expect(report.failures.join('\n')).toContain('unrecognized status')
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('rejects a component that does not exist', () => {
    const root = makeRepo({
      paths: { 'a-path': { status: 'live', component: 'missing/file.ts', reason: '' } },
    })
    try {
      const report = inspectCapabilityHonesty(root)
      expect(report.failures.join('\n')).toContain('does not exist')
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('rejects a component that writes placeholder output', () => {
    const root = makeRepo(
      {
        paths: { 'a-path': { status: 'stub', component: 'scripts/thing.sh', reason: '' } },
      },
      { 'scripts/thing.sh': '#!/bin/sh\necho "# thing placeholder for $TASK_ID" > "$OUTPUT"\n' },
    )
    try {
      const report = inspectCapabilityHonesty(root)
      expect(report.failures.join('\n')).toContain('writes placeholder output')
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('rejects a fabricated publish result without an opt-in', () => {
    const root = makeRepo(
      {
        paths: { 'a-path': { status: 'stub', component: 'scripts/pub.py', reason: '' } },
      },
      { 'scripts/pub.py': 'post_id = f"{platform}_{uuid.uuid4().hex[:12]}"\n' },
    )
    try {
      const report = inspectCapabilityHonesty(root)
      expect(report.failures.join('\n')).toContain('fabricates a publish result')
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('accepts a fabricated publish result behind an opt-in', () => {
    const root = makeRepo(
      {
        paths: { 'a-path': { status: 'stub', component: 'scripts/pub.py', reason: '' } },
      },
      {
        'scripts/pub.py':
          'if os.environ.get("DSH_PUBLISHER_ALLOW_MOCK"):\n    post_id = f"{platform}_{uuid.uuid4().hex[:12]}"\n',
      },
    )
    try {
      const report = inspectCapabilityHonesty(root)
      expect(report.failures).toEqual([])
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('rejects a deliverable table that lists a stub as deliverable', () => {
    const root = makeRepo(
      {
        paths: { 'fake-publisher': { status: 'stub', component: 'scripts/pub.py', reason: '' } },
      },
      {
        'scripts/pub.py': '# real\n',
        'dragon-assets/index/DELIVERABLE_CAPABILITIES.md':
          '# 表\n\n## 1. 可交付能力\n\n| fake-publisher | 能交付 |\n',
      },
    )
    try {
      const report = inspectCapabilityHonesty(root)
      expect(report.failures.join('\n')).toContain('lists fake-publisher as deliverable')
    } finally {
      rmSync(root, { recursive: true, force: true })
    }
  })
})
