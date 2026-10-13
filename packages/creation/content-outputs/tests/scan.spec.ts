import { mkdtemp, mkdir, writeFile, utimes } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'
import { ASSETS_DIRNAME, METADATA_FILENAME, scanOutputs, scanProject } from '../src/scan.ts'
import type { OutputProject } from '../src/types.ts'

async function library(): Promise<string> {
  return mkdtemp(join(tmpdir(), 'dsh-content-outputs-'))
}

const VALID_METADATA = {
  formatVersion: 0,
  title: '秋天的第一篇图文',
  kind: 'xhs-note',
  platform: '小红书',
  status: 'ready',
  tags: ['秋日', '图文'],
  summary: '一篇应景的种草笔记',
}

describe('scanOutputs', () => {
  it('returns an empty snapshot for a missing root', async () => {
    const snapshot = await scanOutputs(join(await library(), 'absent'))
    expect(snapshot.projects).toEqual([])
    expect(snapshot.problems).toEqual([])
  })

  it('projects metadata, deliverables, and assets per project directory', async () => {
    const root = await library()
    await mkdir(join(root, 'autumn-note', ASSETS_DIRNAME), { recursive: true })
    await writeFile(join(root, 'autumn-note', METADATA_FILENAME), JSON.stringify(VALID_METADATA))
    await writeFile(join(root, 'autumn-note', 'cover.png'), 'png')
    await writeFile(join(root, 'autumn-note', 'final.md'), 'md')
    await writeFile(join(root, 'autumn-note', ASSETS_DIRNAME, 'draft.md'), 'md')

    const snapshot = await scanOutputs(root)
    expect(snapshot.problems).toEqual([])
    expect(snapshot.projects).toHaveLength(1)
    const project = snapshot.projects[0]!
    expect(project.topic).toBe('autumn-note')
    expect(project.title).toBe('秋天的第一篇图文')
    expect(project.kind).toBe('xhs-note')
    expect(project.platform).toBe('小红书')
    expect(project.status).toBe('ready')
    expect(project.tags).toEqual(['秋日', '图文'])
    expect([...project.deliverables].sort()).toEqual(['cover.png', 'final.md'])
    expect(project.assetCount).toBe(1)
    expect(project.hasMetadata).toBe(true)
    expect(Number.isNaN(Date.parse(project.updatedAt))).toBe(false)
  })

  it('skips dot and underscore entries as system names', async () => {
    const root = await library()
    await mkdir(join(root, '_ideas'), { recursive: true })
    await mkdir(join(root, '.hidden'), { recursive: true })
    await mkdir(join(root, 'real-project'), { recursive: true })

    const snapshot = await scanOutputs(root)
    expect(snapshot.projects.map(project => project.topic)).toEqual(['real-project'])
  })

  it('projects metadata-less directories with fallbacks and hasMetadata=false', async () => {
    const root = await library()
    await mkdir(join(root, 'bare'), { recursive: true })
    await writeFile(join(root, 'bare', 'out.md'), 'md')

    const snapshot = await scanOutputs(root)
    expect(snapshot.problems).toEqual([])
    const project = snapshot.projects[0]!
    expect(project.title).toBe('bare')
    expect(project.status).toBe('draft')
    expect(project.hasMetadata).toBe(false)
    expect(project.deliverables).toEqual(['out.md'])
  })

  it('surfaces malformed and future-format metadata instead of dropping the project', async () => {
    const root = await library()
    await mkdir(join(root, 'broken'), { recursive: true })
    await writeFile(join(root, 'broken', METADATA_FILENAME), '{not json')
    await mkdir(join(root, 'future'), { recursive: true })
    await writeFile(join(root, 'future', METADATA_FILENAME), JSON.stringify({ ...VALID_METADATA, formatVersion: 1 }))

    const snapshot = await scanOutputs(root)
    expect(snapshot.problems).toEqual([])
    const byTopic = new Map<string, OutputProject>(snapshot.projects.map(project => [project.topic, project]))
    expect(byTopic.get('broken')?.hasMetadata).toBe(true)
    expect(byTopic.get('broken')?.status).toBe('draft')
    expect(byTopic.get('future')?.hasMetadata).toBe(true)
    expect(byTopic.get('future')?.kind).toBe('other')
  })

  it('names an unreadable project directory as a problem instead of a project', async () => {
    const root = await library()
    const scanned = await scanProject(join(root, 'absent-root'), 'any')
    expect(scanned.problem).toBeDefined()
    expect(scanned.project).toBeUndefined()
  })

  it('orders projects by topic name', async () => {
    const root = await library()
    for (const topic of ['c-third', 'a-first', 'b-second']) {
      await mkdir(join(root, topic), { recursive: true })
    }
    const snapshot = await scanOutputs(root)
    expect(snapshot.projects.map(project => project.topic)).toEqual(['a-first', 'b-second', 'c-third'])
  })

  it('accepts metadata files whose mtime is older than the project mtime', async () => {
    const root = await library()
    await mkdir(join(root, 'stale'), { recursive: true })
    const metadataPath = join(root, 'stale', METADATA_FILENAME)
    await writeFile(metadataPath, JSON.stringify(VALID_METADATA))
    const old = new Date(Date.now() - 60_000)
    await utimes(metadataPath, old, old)
    const snapshot = await scanOutputs(root)
    expect(snapshot.projects[0]?.hasMetadata).toBe(true)
  })
})
