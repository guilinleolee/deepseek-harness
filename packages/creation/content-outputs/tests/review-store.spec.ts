import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { afterEach, describe, expect, it } from 'vitest'
import type { MetricSnapshot, ReviewImportCommitRequest, ReviewManifest, ReviewParsedRow, ReviewTask } from '../src/review/types.ts'
import {
  REVIEW_INDEX_FILENAME, REVIEW_MANIFEST_FILENAME, assertReviewManifest, commitReviewImportFile,
  deleteReviewTaskFile, listReviewTemplatesFile, parseReviewManifest, readReviewIndexFile,
  readReviewManifestFile, readReviewReportFile, readReviewTemplateFile, writeReviewManifestFile,
  writeReviewReportFile, writeReviewTemplateFile,
} from '../src/review/store.ts'

let root: string | undefined

afterEach(async () => {
  if (root !== undefined) await rm(root, { recursive: true, force: true })
  root = undefined
})

async function library(): Promise<string> {
  root = await mkdtemp(join(tmpdir(), 'review-store-'))
  return root
}

/** One valid metrics record. */
function metrics(overrides: Partial<MetricSnapshot['metrics']> = {}): MetricSnapshot['metrics'] {
  return {
    impressions: 1000, reads: 500, likes: 50, collects: 20,
    comments: 10, shares: 5, followersGained: null, coverCtr: null,
    ...overrides,
  }
}

/** One valid stored snapshot, overridden per test. */
function snapshot(overrides: Partial<MetricSnapshot> = {}): MetricSnapshot {
  return {
    snapshotId: crypto.randomUUID(),
    platformId: 'xhs',
    platformWorkId: 'work-1',
    title: '第一篇',
    publishedAt: '2026-09-01T00:00:00.000Z',
    capturedAt: '2026-09-20T00:00:00.000Z',
    contentId: null,
    matchMethod: null,
    contentType: 'image-text',
    metrics: metrics(),
    ...overrides,
  }
}

/** One valid stored task, overridden per test. */
function task(overrides: Partial<ReviewTask> = {}): ReviewTask {
  return {
    taskId: 'task-1',
    name: '九月上旬复盘',
    period: { from: '2026-09-01', to: '2026-09-15' },
    filters: { platforms: ['xhs'], contentTypes: [], workFilter: 'all' },
    status: 'ready',
    reportFile: 'reports/report-task-1.md',
    degraded: false,
    createdAt: '2026-09-20T00:00:00.000Z',
    ...overrides,
  }
}

/** One valid manifest, overridden per test. */
function manifest(overrides: Partial<ReviewManifest> = {}): ReviewManifest {
  return {
    formatVersion: 0,
    baselines: { engagementRate: 0.05, collectRate: 0.02, source: 'user', updatedAt: '2026-09-20T00:00:00.000Z' },
    snapshots: [snapshot()],
    tasks: [task()],
    ...overrides,
  }
}

function commit(rows: ReviewParsedRow[], theme = 'theme-a'): ReviewImportCommitRequest {
  return { theme, platformId: 'xhs', rows }
}

describe('parseReviewManifest', () => {
  it('returns named problems for malformed JSON and unknown versions', () => {
    expect(parseReviewManifest('not json').problems).toEqual(['review manifest is not valid JSON'])
    expect(parseReviewManifest('{"formatVersion":1}').problems.length > 0).toBe(true)
  })

  it('drops malformed entries into problems and keeps valid ones', () => {
    const stored = manifest()
    const raw = JSON.stringify({ ...stored, snapshots: [stored.snapshots[0], { junk: true }], tasks: [stored.tasks[0], 42] })
    const { manifest: parsed, problems } = parseReviewManifest(raw)
    expect(parsed.snapshots).toHaveLength(1)
    expect(parsed.tasks).toHaveLength(1)
    expect(problems).toHaveLength(2)
  })

  it('falls back to default baselines when the stored record is malformed', () => {
    const raw = JSON.stringify({ formatVersion: 0, snapshots: [], tasks: [], baselines: { junk: true } })
    const { manifest: parsed } = parseReviewManifest(raw)
    expect(parsed.baselines.source).toBe('default')
  })
})

describe('assertReviewManifest', () => {
  it('rejects a wrong envelope version and malformed entries wholesale', () => {
    expect(() =>{  assertReviewManifest({ ...manifest(), formatVersion: 1 } as unknown as ReviewManifest) }).toThrow(/formatVersion/)
    const broken = { ...manifest(), snapshots: [{ junk: true } as unknown as MetricSnapshot] }
    expect(() => { assertReviewManifest(broken) }).toThrow(/invalid review snapshot/)
  })
})

describe('readReviewManifestFile / writeReviewManifestFile', () => {
  it('reads an absent manifest as null with no problems', async () => {
    const read = await readReviewManifestFile(await library(), 'theme-a')
    expect(read.manifest).toBeNull()
    expect(read.problems).toEqual([])
  })

  it('round-trips a manifest and refreshes the global index rows', async () => {
    const dir = await library()
    await writeReviewManifestFile(dir, 'theme-a', manifest())
    const read = await readReviewManifestFile(dir, 'theme-a')
    expect(read.manifest?.tasks[0]?.name).toBe('九月上旬复盘')
    const index = await readReviewIndexFile(dir)
    expect(index.doc?.rows).toHaveLength(1)
    expect(index.doc?.rows[0]?.theme).toBe('theme-a')
  })

  it('keeps index rows of other themes and replaces the written theme rows', async () => {
    const dir = await library()
    await writeReviewManifestFile(dir, 'theme-a', manifest())
    await writeReviewManifestFile(dir, 'theme-b', manifest({ tasks: [task({ taskId: 'task-2', name: '第二主题' })] }))
    await writeReviewManifestFile(dir, 'theme-a', manifest({ tasks: [] }))
    const index = await readReviewIndexFile(dir)
    expect(index.doc?.rows.map(row => row.theme).sort()).toEqual(['theme-b'])
  })

  it('rejects an oversized snapshot list wholesale', async () => {
    const dir = await library()
    const flood = manifest({ snapshots: Array.from({ length: 20_001 }, () => snapshot()) })
    await expect(writeReviewManifestFile(dir, 'theme-a', flood)).rejects.toThrow(/snapshot cap/)
  })
})

describe('commitReviewImportFile', () => {
  it('appends rows as unbound snapshots and creates the manifest on first commit', async () => {
    const dir = await library()
    const result = await commitReviewImportFile(dir, commit([
      { platformWorkId: 'w1', title: '第一篇', publishedAt: null, contentType: null, metrics: metrics() },
    ]))
    expect(result).toEqual({ added: 1, overwritten: 0 })
    const read = await readReviewManifestFile(dir, 'theme-a')
    const added = read.manifest?.snapshots[0]
    expect(added?.contentId).toBeNull()
    expect(added?.matchMethod).toBeNull()
    expect(read.manifest?.baselines.source).toBe('default')
  })

  it('overwrites the same UTC day snapshot of a known work and keeps older days', async () => {
    const dir = await library()
    // First commit lands today's snapshot; re-importing the same work on the
    // same UTC day overwrites it, and a seeded older day survives.
    await writeReviewManifestFile(dir, 'theme-a', manifest({
      snapshots: [snapshot({ capturedAt: '2026-09-19T08:00:00.000Z' })],
      tasks: [],
    }))
    const first = await commitReviewImportFile(dir, commit([
      { platformWorkId: 'work-1', title: '第一篇', publishedAt: null, contentType: null, metrics: metrics() },
    ]))
    expect(first).toEqual({ added: 1, overwritten: 0 })
    const second = await commitReviewImportFile(dir, commit([
      { platformWorkId: 'work-1', title: '第一篇', publishedAt: null, contentType: null, metrics: metrics({ reads: 999 }) },
    ]))
    expect(second).toEqual({ added: 0, overwritten: 1 })
    const read = await readReviewManifestFile(dir, 'theme-a')
    expect(read.manifest?.snapshots).toHaveLength(2)
    const today = read.manifest?.snapshots.find(candidate => candidate.capturedAt.slice(0, 10) === new Date().toISOString().slice(0, 10))
    expect(today?.metrics.reads).toBe(999)
  })

  it('treats the same work on a different platform as a distinct work', async () => {
    const dir = await library()
    await writeReviewManifestFile(dir, 'theme-a', manifest({ tasks: [] }))
    const result = await commitReviewImportFile(dir, { theme: 'theme-a', platformId: 'douyin', rows: [
      { platformWorkId: 'work-1', title: '同名', publishedAt: null, contentType: null, metrics: metrics() },
    ] })
    expect(result.added).toBe(1)
  })

  it('rejects the commit when the stored manifest is malformed', async () => {
    const dir = await library()
    await mkdir(join(dir, 'theme-a', 'assets'), { recursive: true })
    await writeFile(join(dir, 'theme-a', 'assets', REVIEW_MANIFEST_FILENAME), 'not json', 'utf8')
    await expect(commitReviewImportFile(dir, commit([]))).rejects.toThrow(/unreadable/)
  })
})

describe('deleteReviewTaskFile', () => {
  it('removes the task, deletes the report file, and keeps snapshots', async () => {
    const dir = await library()
    await writeReviewManifestFile(dir, 'theme-a', manifest())
    await writeReviewReportFile(dir, 'theme-a', 'report-task-1.md', '# 报告')
    await deleteReviewTaskFile(dir, 'theme-a', 'task-1')
    const read = await readReviewManifestFile(dir, 'theme-a')
    expect(read.manifest?.tasks).toEqual([])
    expect(read.manifest?.snapshots).toHaveLength(1)
    await expect(readReviewReportFile(dir, 'theme-a', 'reports/report-task-1.md')).resolves.toEqual({})
  })

  it('rejects an unknown task id', async () => {
    const dir = await library()
    await writeReviewManifestFile(dir, 'theme-a', manifest())
    await expect(deleteReviewTaskFile(dir, 'theme-a', 'missing')).rejects.toThrow(/unknown review task/)
  })
})

describe('report and template files', () => {
  it('writes and reads back a report; absent files read as empty', async () => {
    const dir = await library()
    const stored = await writeReviewReportFile(dir, 'theme-a', 'report-task-1.md', '# 报告')
    expect(stored.file).toBe('reports/report-task-1.md')
    await expect(readReviewReportFile(dir, 'theme-a', 'reports/report-task-1.md')).resolves.toEqual({ content: '# 报告' })
    await expect(readReviewReportFile(dir, 'theme-a', 'reports/missing.md')).resolves.toEqual({})
  })

  it('rejects path escapes and non-report references', async () => {
    const dir = await library()
    await expect(writeReviewReportFile(dir, 'theme-a', '../escape.md', 'x')).rejects.toThrow(/invalid review file name/)
    await expect(readReviewReportFile(dir, 'theme-a', 'templates/not-a-report.md')).rejects.toThrow(/invalid review report reference/)
  })

  it('lists and reads saved templates; an absent directory reads as empty', async () => {
    const dir = await library()
    expect(await listReviewTemplatesFile(dir, 'theme-a')).toEqual([])
    await writeReviewTemplateFile(dir, 'theme-a', '爆款-标题.md', '# 模板')
    expect(await listReviewTemplatesFile(dir, 'theme-a')).toEqual(['爆款-标题.md'])
    await expect(readReviewTemplateFile(dir, 'theme-a', '爆款-标题.md')).resolves.toEqual({ content: '# 模板' })
    await expect(writeReviewTemplateFile(dir, 'theme-a', '.hidden.md', 'x')).rejects.toThrow(/invalid review file name/)
  })
})

describe('readReviewIndexFile', () => {
  it('reads an absent index as empty and a malformed one with problems', async () => {
    const dir = await library()
    expect(await readReviewIndexFile(dir)).toEqual({ doc: null, problems: [] })
    await writeFile(join(dir, REVIEW_INDEX_FILENAME), 'not json', 'utf8')
    const read = await readReviewIndexFile(dir)
    expect(read.doc).toBeNull()
    expect(read.problems[0]).toContain('not valid JSON')
  })
})
