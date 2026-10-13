import { mkdtemp, readFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'
import {
  assertCompetitorManifest, COMPETITOR_MANIFEST_FILENAME, emptyManifest, parseCompetitorManifest,
  readCompetitorManifestFile, writeCompetitorManifestFile,
} from '../src/competitor/store.ts'
import type { CompetitorManifest, CompetitorWork } from '../src/types.ts'

/** One valid work entry over the required fields, overridden per test. The id stays a plain string for convenience. */
function work(overrides: Partial<Omit<CompetitorWork, 'id'>> & { id?: string } = {}): CompetitorWork {
  const { id, ...rest } = overrides
  return {
    id: (id ?? 'cw-1') as CompetitorWork['id'],
    accountId: 'acc-1',
    accountName: '竞品A',
    platform: 'xhs',
    platformWorkId: 'native-1',
    title: '一条对标作品',
    importedAt: '2026-09-25T00:00:00.000Z',
    metrics: [{ t: '2026-09-25T00:00:00.000Z', likes: 10, comments: 2, shares: 1 }],
    hot: false,
    favorite: false,
    via: 'manual',
    analysis: { status: 'none' },
    ...rest,
  }
}

function manifest(overrides: Partial<CompetitorManifest> = {}): CompetitorManifest {
  return { formatVersion: 0, syncedAt: { 'acc-1': '2026-09-25T00:00:00.000Z' }, works: [work()], reports: [], ...overrides }
}

describe('parseCompetitorManifest', () => {
  it('round-trips a valid manifest', () => {
    const parsed = parseCompetitorManifest(JSON.stringify(manifest()))
    expect(parsed.problems).toEqual([])
    expect(parsed.manifest.works).toHaveLength(1)
    expect(parsed.manifest.syncedAt['acc-1']).toBe('2026-09-25T00:00:00.000Z')
  })

  it('names invalid JSON and unsupported versions instead of throwing', () => {
    expect(parseCompetitorManifest('{nope').problems).toHaveLength(1)
    const wrongVersion = parseCompetitorManifest(JSON.stringify({ ...manifest(), formatVersion: 1 }))
    expect(wrongVersion.manifest.works).toEqual([])
    expect(wrongVersion.problems[0]).toContain('formatVersion')
  })

  it('drops invalid entries and names them', () => {
    // Invalid shapes are simulated persisted data; the loose casts keep the
    // fixture construction honest about what the parser must reject.
    const invalid = [
      { ...work(), platform: 'twitter' },
      { ...work(), id: 'cw-2', metrics: [{ t: 'x', likes: -1, comments: 0, shares: 0 }] },
      { ...work(), id: 'cw-3', analysis: { status: 'running' } },
      { ...work(), id: 'cw-4', analysis: { status: 'done' } },
    ] as unknown as CompetitorWork[]
    const parsed = parseCompetitorManifest(JSON.stringify(manifest({ works: [work(), ...invalid] })))
    expect(parsed.manifest.works.map(entry => entry.id)).toEqual(['cw-1'])
    expect(parsed.problems).toHaveLength(4)
  })

  it('accepts a done analysis only with a complete result', () => {
    const done = work({
      id: 'cw-5',
      analysis: {
        status: 'done',
        ref: 'ca-5.md',
        result: { hookType: '痛点', structure: '总分总', painPoints: [], topics: [], risks: [], reusable: [], migrationTopics: [], commentInsight: 'unavailable' },
      },
    })
    const parsed = parseCompetitorManifest(JSON.stringify(manifest({ works: [done] })))
    expect(parsed.problems).toEqual([])
    expect(parsed.manifest.works[0]!.analysis.result!.hookType).toBe('痛点')
  })

  it('tolerates absent sections', () => {
    const parsed = parseCompetitorManifest(JSON.stringify({ formatVersion: 0 }))
    expect(parsed.problems).toEqual([])
    expect(parsed.manifest).toEqual(emptyManifest())
  })
})

describe('writeCompetitorManifestFile', () => {
  it('round-trips through disk and creates the theme directory', async () => {
    const root = await mkdtemp(join(tmpdir(), 'dsh-competitor-'))
    const next = manifest({ works: [work({ id: 'cw-2', platformWorkId: 'native-2' }), work({ id: 'cw-3', platformWorkId: 'native-3' })] })
    await writeCompetitorManifestFile(root, '竞品主题', next)
    const stored = JSON.parse(await readFile(join(root, '竞品主题', 'assets', COMPETITOR_MANIFEST_FILENAME), 'utf8')) as CompetitorManifest
    expect(stored.works).toHaveLength(2)
    const read = await readCompetitorManifestFile(root, '竞品主题')
    expect(read.manifest.works).toHaveLength(2)
    expect(read.problems).toEqual([])
  })

  it('rejects malformed manifests loudly', async () => {
    const root = await mkdtemp(join(tmpdir(), 'dsh-competitor-'))
    const mcpWork = { ...work(), via: 'mcp' } as unknown as CompetitorWork
    expect(() =>{  assertCompetitorManifest(manifest({ works: [mcpWork] })) }).toThrow(/invalid competitor work/)
    await expect(writeCompetitorManifestFile(root, '主题', manifest({ formatVersion: 9 } as unknown as CompetitorManifest))).rejects.toThrow(/formatVersion/)
  })

  it('reads an absent theme as an empty manifest without problems', async () => {
    const root = await mkdtemp(join(tmpdir(), 'dsh-competitor-'))
    const read = await readCompetitorManifestFile(root, 'absent')
    expect(read.manifest).toEqual(emptyManifest())
    expect(read.problems).toEqual([])
  })

  it('replaces an existing manifest atomically', async () => {
    const root = await mkdtemp(join(tmpdir(), 'dsh-competitor-'))
    await writeCompetitorManifestFile(root, '主题', manifest())
    await writeCompetitorManifestFile(root, '主题', emptyManifest())
    const read = await readCompetitorManifestFile(root, '主题')
    expect(read.manifest.works).toEqual([])
    expect(read.manifest.reports).toEqual([])
  })
})

describe('readCompetitorManifestFile guards', () => {
  it('propagates invalid theme names', async () => {
    const root = await mkdtemp(join(tmpdir(), 'dsh-competitor-'))
    await expect(readCompetitorManifestFile(root, '../escape')).rejects.toThrow(/invalid gather theme name/)
  })
})
