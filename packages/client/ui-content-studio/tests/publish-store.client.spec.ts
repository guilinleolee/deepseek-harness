import { describe, expect, it } from 'vitest'
import type { OutputTopic, PublishManifest } from '@deepseek-ai/dsh-content-outputs/types'
import { PLATFORM_PROFILES } from '../src/client/publish/model.ts'
import { createPublishController, type PublishGateway } from '../src/client/publish/publish-store.ts'

/** In-memory doubles: a manifest per theme plus a derived-draft disk. */
function fakeGateway(): { gateway: PublishGateway; drafts: Map<string, string>; adaptFails: { adaptFails: boolean } } {
  const manifests = new Map<string, PublishManifest>()
  const drafts = new Map<string, string>()
  const state = { adaptFails: false }
  const gateway: PublishGateway = {
    async readPublishManifest(theme) {
      return { manifest: manifests.get(theme) ?? null, problems: [] }
    },
    async writePublishManifest(theme, manifest) {
      manifests.set(theme, manifest)
    },
    async listPublishIndex() {
      return { index: { formatVersion: 0, entries: [] }, problems: [] }
    },
    async readPublishProfiles() {
      return { profiles: [], problems: [] }
    },
    async writePublishProfiles() {},
    async writePublishDerived(theme, taskId, platformId, content) {
      drafts.set(`${theme}/${taskId}/${platformId}`, content)
      return { file: `publish/${taskId}/${platformId}.md` }
    },
    async readPublishDerived(theme, taskId, platformId) {
      const content = drafts.get(`${theme}/${taskId}/${platformId}`)
      return content === undefined ? {} : { content }
    },
    async readPublishSource(theme, file) {
      return { content: `# 定稿正文（${theme}/${file}）` }
    },
    async buildPublishPackage(theme, taskId) {
      const task = manifests.get(theme)?.tasks.find(candidate => candidate.taskId === taskId)
      for (const leg of task?.platforms ?? []) {
        if (!drafts.has(`${theme}/${taskId}/${leg.platformId}`)) {
          throw new Error(`publish task ${taskId} has no derived draft for ${leg.platformId} yet`)
        }
      }
      return {
        taskId: taskId, theme, title: task?.title ?? '', manuscriptFile: task?.manuscriptFile ?? '',
        topicId: null, personaDigest: null, mode: 'immediate', scheduledAt: null,
        platforms: (task?.platforms ?? []).map(leg => ({
          platformId: leg.platformId, accountAlias: leg.accountAlias, contentFile: leg.contentFile,
          tags: leg.tags, coverPrompt: null, scheduledAt: null,
        })),
        generatedAt: '2026-09-27T00:00:00.000Z',
      }
    },
    async adaptPublishContent() {
      if (state.adaptFails) throw new Error('429 rate limited')
      return { content: '适配稿', coverPrompt: '封面', tags: ['咖啡'], model: 'test-model', promptVersion: 1 }
    },
  }
  return { gateway, drafts, adaptFails: state }
}

/** A controller over fake faces with two enabled platforms preconfigured. */
function controllerWith() {
  const fake = fakeGateway()
  const applied: string[] = []
  const publish = createPublishController({
    gateway: fake.gateway,
    listOutputs: async () => ({
      root: '/tmp', projects: [{
        topic: 'theme-a' as OutputTopic, title: '杭州咖啡地图', kind: 'article' as const, platform: null,
        status: 'published' as const, tags: [], summary: null, updatedAt: '', deliverables: ['final.md'],
        assetCount: 0, hasMetadata: true,
      }], problems: [],
    }),
    schedule: {
      list: async () => ({ file: '_schedule.json', items: [], problems: [] }),
      put: async (input) => {
        applied.push(`schedule:${input.id ?? ''}`)
        return {
          file: '_schedule.json',
          items: input.id === undefined ? [] : [{ ...input, id: input.id }],
          problems: [],
        }
      },
      remove: async (id) => {
        applied.push(`unschedule:${id}`)
        return { file: '_schedule.json', items: [], problems: [] }
      },
    },
    topics: {
      list: async () => ({ file: '_topics.json', items: [], problems: [] }),
      put: async (input) => {
        applied.push(`topic:${input.status}`)
        return {}
      },
    },
  })
  return { publish, fake, applied }
}

/** Seed one task through the real create path; returns [task, openTaskId]. */
async function seedTask(publish: ReturnType<typeof createPublishController>): Promise<string> {
  await publish.init()
  await publish.openTheme('theme-a')
  await publish.createTask({
    manuscript: { theme: 'theme-a', file: 'final.md', title: '杭州咖啡地图' },
    platformIds: [PLATFORM_PROFILES[0]!.platformId, PLATFORM_PROFILES[1]!.platformId],
    mode: 'immediate',
    scheduledAt: null,
    note: null,
    topicId: 't-1',
    personaDigest: null,
    manuscriptId: null,
  })
  return publish.getState().openTaskId!
}

describe('publish controller', () => {
  it('creates a pendingReview task with one pending leg per platform', async () => {
    const { publish } = controllerWith()
    const taskId = await seedTask(publish)
    const created = publish.getState().tasks.find(task => task.taskId === taskId)!
    expect(created.status).toBe('pendingReview')
    expect(created.platforms.map(leg => leg.status)).toEqual(['pending', 'pending'])
    expect(created.manuscriptFile).toBe('final.md')
    expect(created.topicId).toBe('t-1')
  })

  it('isolates a failed adaptation: only that leg logs the attempt', async () => {
    const { publish, fake } = controllerWith()
    const taskId = await seedTask(publish)
    fake.adaptFails.adaptFails = true
    await publish.adaptPlatform(taskId, 'xhs')
    const task = publish.getState().tasks.find(candidate => candidate.taskId === taskId)!
    const xhs = task.platforms.find(leg => leg.platformId === 'xhs')!
    const gzh = task.platforms.find(leg => leg.platformId === 'gzh')!
    expect(xhs.attempts).toHaveLength(1)
    expect(xhs.attempts[0]?.ok).toBe(false)
    expect(xhs.status).toBe('pending')
    expect(gzh.attempts).toHaveLength(0)
    expect(publish.getState().notice).toBe('adapt-failed')
  })

  it('appends retry attempts without rewriting history, then records', async () => {
    const { publish, fake } = controllerWith()
    const taskId = await seedTask(publish)
    fake.adaptFails.adaptFails = true
    await publish.adaptPlatform(taskId, 'xhs')
    fake.adaptFails.adaptFails = false
    await publish.adaptPlatform(taskId, 'xhs')
    let task = publish.getState().tasks.find(candidate => candidate.taskId === taskId)!
    const xhs = task.platforms.find(leg => leg.platformId === 'xhs')!
    expect(xhs.attempts.map(attempt => attempt.ok)).toEqual([false, true])
    expect(xhs.status).toBe('adapted')

    // Recording with the second leg unadapted fails loud and records nothing.
    await publish.recordTask(taskId)
    expect(publish.getState().notice).toBe('record-failed')

    await publish.adaptPlatform(taskId, 'gzh')
    await publish.recordTask(taskId)
    task = publish.getState().tasks.find(candidate => candidate.taskId === taskId)!
    expect(task.status).toBe('recorded')
    expect(task.platforms.every(leg => leg.status === 'recorded')).toBe(true)
  })

  it('editing a draft flips the leg to edited and logs the edit', async () => {
    const { publish } = controllerWith()
    const taskId = await seedTask(publish)
    await publish.adaptPlatform(taskId, 'xhs')
    await publish.saveDraftEdit(taskId, 'xhs', '手改后的稿')
    const xhs = publish.getState().tasks.find(candidate => candidate.taskId === taskId)!
      .platforms.find(leg => leg.platformId === 'xhs')!
    expect(xhs.status).toBe('edited')
    expect(xhs.attempts.at(-1)?.action).toBe('edit')
  })

  it('copying a task resets the legs to pending with an empty log', async () => {
    const { publish } = controllerWith()
    const taskId = await seedTask(publish)
    await publish.adaptPlatform(taskId, 'xhs')
    await publish.copyTask(taskId)
    const state = publish.getState()
    const copied = state.tasks.find(candidate => candidate.taskId !== taskId)!
    expect(copied.status).toBe('pendingReview')
    expect(copied.platforms.every(leg => leg.status === 'pending' && leg.attempts.length === 0)).toBe(true)
  })
})
