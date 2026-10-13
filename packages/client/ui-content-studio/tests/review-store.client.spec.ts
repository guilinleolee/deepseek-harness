// @vitest-environment jsdom
import { describe, expect, it, vi } from 'vitest'
import type {
  ReviewGenerateReportRequest, ReviewImportPreview, ReviewManifest,
} from '@deepseek-ai/dsh-content-outputs/types'
import { createReviewController, type ReviewGateway } from '../src/client/review/review-store.ts'

/** In-memory storage backend so tests never touch real localStorage. */
function stubLocalStorage(): Map<string, string> {
  const map = new Map<string, string>()
  ;(globalThis as { window?: unknown }).window = {
    localStorage: {
      getItem: (key: string) => map.get(key) ?? null,
      setItem: (key: string, value: string) => { map.set(key, value) },
      removeItem: (key: string) => { map.delete(key) },
    },
  }
  return map
}

/** One valid stored manifest. */
function manifest(): ReviewManifest {
  return {
    formatVersion: 0,
    baselines: { engagementRate: 0.05, collectRate: 0.02, source: 'user', updatedAt: '2026-09-20T00:00:00.000Z' },
    snapshots: [{
      snapshotId: 's1',
      platformId: 'xhs',
      platformWorkId: 'work-1',
      title: '第一篇',
      publishedAt: '2026-09-01T00:00:00.000Z',
      capturedAt: '2026-09-20T00:00:00.000Z',
      contentId: null,
      matchMethod: null,
      contentType: 'image-text',
      metrics: {
        impressions: 1000, reads: 500, likes: 100, collects: 20,
        comments: 10, shares: 5, followersGained: null, coverCtr: null,
      },
    }],
    tasks: [],
  }
}

/** Wire a controller over in-memory doubles. */
function harness(stored: ReviewManifest | null = manifest()) {
  const map = stubLocalStorage()
  let current = stored
  const reports = new Map<string, string>()
  const topics: unknown[] = []
  const generateReport = vi.fn(async (_request: ReviewGenerateReportRequest) => ({
    markdown: '# 完整报告', model: 'test-model', promptVersion: 1,
  }))
  const gateway: ReviewGateway = {
    readReviewManifest: async () => ({ manifest: current, problems: [] }),
    writeReviewManifest: async (_theme, next) => { current = next },
    parseReviewImport: async () => ({
      fileName: 'notes.csv',
      platformId: 'xhs',
      rows: [{ platformWorkId: 'w9', title: '导入篇', publishedAt: null, contentType: null, metrics: {
        impressions: 1, reads: 1, likes: 1, collects: 1, comments: 1, shares: 1, followersGained: 1, coverCtr: 1,
      } }],
      rejected: [],
      unknownColumns: ['神秘列'],
      totalRows: 1,
    }) satisfies ReviewImportPreview,
    commitReviewImport: async () => ({ added: 1, overwritten: 0 }),
    deleteReviewTask: async (request) => {
      if (current !== null) {
        current = { ...current, tasks: current.tasks.filter(task => task.taskId !== request.taskId) }
      }
    },
    writeReviewReport: async (_theme, file, content) => {
      reports.set(file, content)
      return { file: `reports/${file}` }
    },
    readReviewReport: async (_theme, file) => {
      const direct = reports.get(file)
      if (direct !== undefined) return { content: direct }
      for (const [key, value] of reports) {
        if (key.endsWith(file.split('/').pop() ?? '')) return { content: value }
      }
      return {}
    },
    writeReviewTemplate: async () => ({ file: 'templates/t.md' }),
    listReviewTemplates: async () => ({ files: [] }),
    analyzeReviewWork: async () => ({ markdown: '# 诊断', model: 'test-model', promptVersion: 1 }),
    generateReviewReport: generateReport,
  }
  const controller = createReviewController(gateway, { put: async (input) => { topics.push(input) } })
  return { controller, map, reports, topics, generateReport, current: () => current }
}

describe('review controller', () => {
  it('loads a theme and exposes the manifest', async () => {
    const { controller } = harness()
    await controller.load('主题A')
    expect(controller.getState().theme).toBe('主题A')
    expect(controller.getState().manifest?.snapshots).toHaveLength(1)
    expect(controller.getState().problems).toEqual([])
  })

  it('stages the import preview, exposes unknown columns, and commits', async () => {
    const { controller } = harness()
    await controller.load('主题A')
    await controller.stageImport('xhs', 'notes.csv', 'data')
    expect(controller.getState().preview?.rows).toHaveLength(1)
    expect(controller.getState().preview?.unknownColumns).toEqual(['神秘列'])
    controller.setIgnoredColumns(['神秘列'])
    await controller.commitImport()
    expect(controller.getState().preview).toBeNull()
    expect(controller.getState().notice).toBe('import-committed')
  })

  it('binds a snapshot manually and admits it into the pool', async () => {
    const { controller } = harness()
    await controller.load('主题A')
    await controller.bindWork('work-1', 'xhs', 'content-9')
    const bound = controller.getState().manifest?.snapshots[0]
    expect(bound?.contentId).toBe('content-9')
    expect(bound?.matchMethod).toBe('manual')
    controller.setFilters({ period: { from: '2026-09-01', to: '2026-09-27' } })
    expect(controller.pool()).toHaveLength(1)
    expect(controller.pool()[0]?.verdict).toBe('viral')
  })

  it('generates a report through the AI face and lands it ready', async () => {
    const { controller, generateReport, reports } = harness()
    await controller.load('主题A')
    await controller.bindWork('work-1', 'xhs', 'content-9')
    await controller.createTask('九月复盘')
    expect(generateReport).toHaveBeenCalledTimes(1)
    const tasks = controller.getState().manifest?.tasks
    expect(tasks?.[0]?.status).toBe('ready')
    expect(tasks?.[0]?.degraded).toBe(false)
    expect([...reports.keys()].length).toBe(1)
    expect(controller.getState().notice).toBe('report-ready')
  })

  it('falls back to the data-only report when the AI call fails', async () => {
    const harness1 = harness()
    harness1.generateReport.mockRejectedValueOnce(new Error('LLM down'))
    await harness1.controller.load('主题A')
    await harness1.controller.bindWork('work-1', 'xhs', 'content-9')
    await harness1.controller.createTask('九月复盘')
    const tasks = harness1.controller.getState().manifest?.tasks
    expect(tasks?.[0]?.status).toBe('ready')
    expect(tasks?.[0]?.degraded).toBe(true)
    expect(harness1.reports.get([...harness1.reports.keys()][0] as string)).toContain('AI 增强部分生成失败')
  })

  it('deletes a task through the gateway and reloads', async () => {
    const seeded = manifest()
    const { controller } = harness({
      ...seeded,
      tasks: [{
        taskId: 't1', name: '旧复盘', period: { from: '2026-09-01', to: '2026-09-15' },
        filters: { platforms: [], contentTypes: [], workFilter: 'all' },
        status: 'ready', reportFile: null, degraded: false, createdAt: '2026-09-20T00:00:00.000Z',
      }],
    })
    await controller.load('主题A')
    await controller.deleteTask('t1')
    expect(controller.getState().manifest?.tasks).toEqual([])
    expect(controller.getState().notice).toBe('task-deleted')
  })

  it('pushes the reflow topic with the review tag', async () => {
    const { controller, topics } = harness()
    await controller.load('主题A')
    await controller.pushToTopicBank('选题一', null, '说明')
    expect(topics).toHaveLength(1)
    const pushed = topics[0] as { title: string; tags: readonly string[]; source: { type: string } }
    expect(pushed.title).toBe('选题一')
    expect(pushed.tags).toContain('复盘')
    expect(pushed.source.type).toBe('manual')
  })
})
