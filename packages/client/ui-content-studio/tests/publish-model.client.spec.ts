import { describe, expect, it } from 'vitest'
import type { OutputTopic, PlatformTask, PublishTask } from '@deepseek-ai/dsh-content-outputs/types'
import {
  PLATFORM_IDS, PLATFORM_PROFILES, allPlatformsAt, dueScheduledTasks, exceedsCharLimit,
  formatTags, manuscriptCards, platformProfileOf, withAttempt, withPlatform, withStatus,
} from '../src/client/publish/model.ts'

/** One valid task, overridden per test. */
function task(overrides: Partial<PublishTask> = {}): PublishTask {
  return {
    taskId: '0f0a7b1e-5c2d-4e8f-9a3b-6d1c2e4f5a6b',
    title: '杭州咖啡地图',
    manuscriptFile: 'hangzhou-coffee-a1b2c3d4.md',
    manuscriptId: null,
    topicId: 't-1',
    personaDigest: null,
    mode: 'immediate',
    scheduledAt: null,
    scheduleItemId: null,
    status: 'pendingReview',
    note: null,
    platforms: [],
    createdAt: '2026-09-27T00:00:00.000Z',
    updatedAt: '2026-09-27T00:00:00.000Z',
    ...overrides,
  }
}

function leg(platformId: string, status: PlatformTask['status'] = 'pending'): PlatformTask {
  return { platformId, accountAlias: '别名', contentFile: `${platformId}.md`, coverPrompt: null, tags: [], status, attempts: [] }
}

describe('platform registry', () => {
  it('covers the seven launch platforms with unique ids', () => {
    expect(PLATFORM_IDS).toEqual(['xhs', 'gzh', 'zhihu', 'douyin', 'channels', 'bilibili', 'weibo'])
    expect(new Set(PLATFORM_IDS).size).toBe(PLATFORM_PROFILES.length)
  })

  it('declares long-form platforms unlimited and short-form ones capped', () => {
    expect(platformProfileOf('gzh')?.longForm).toBe(true)
    expect(platformProfileOf('gzh')?.charLimit).toBeNull()
    expect(platformProfileOf('xhs')?.charLimit).not.toBeNull()
    expect(platformProfileOf('douyin')?.charLimit).toBe(300)
  })

  it('formats tags per the platform tag style', () => {
    expect(formatTags(['咖啡', '探店'], 'space')).toBe('#咖啡 #探店')
    expect(formatTags(['咖啡', '探店'], 'closed')).toBe('#咖啡##探店#')
    expect(formatTags(['咖啡'], 'none')).toBe('')
    expect(formatTags([], 'space')).toBe('')
  })
})

describe('attempt log appends', () => {
  it('append-only retries keep every prior entry', () => {
    const first = withAttempt(leg('xhs'), 'adapt', false, '429 rate limited', '2026-09-27T01:00:00.000Z')
    const second = withAttempt(first, 'adapt', true, '适配完成', '2026-09-27T01:01:00.000Z')
    expect(second.attempts).toHaveLength(2)
    expect(second.attempts[0]?.ok).toBe(false)
    expect(second.attempts[1]?.ok).toBe(true)
    expect(first.attempts).toHaveLength(1)
  })

  it('withPlatform replaces one leg and bumps the task timestamp', () => {
    const base = task({ platforms: [leg('xhs'), leg('weibo')], updatedAt: '2026-09-27T00:00:00.000Z' })
    const next = withPlatform(base, 'weibo', leg('weibo', 'adapted'), '2026-09-27T09:00:00.000Z')
    expect(next.platforms.find(candidate => candidate.platformId === 'weibo')?.status).toBe('adapted')
    expect(next.platforms.find(candidate => candidate.platformId === 'xhs')?.status).toBe('pending')
    expect(next.updatedAt).toBe('2026-09-27T09:00:00.000Z')
  })

  it('withStatus maps task states without touching legs', () => {
    const next = withStatus(task({ platforms: [leg('xhs')] }), 'recorded', '2026-09-27T09:00:00.000Z')
    expect(next.status).toBe('recorded')
    expect(next.platforms[0]?.status).toBe('pending')
  })

  it('allPlatformsAt requires at least one leg', () => {
    expect(allPlatformsAt(task(), 'adapted')).toBe(false)
    expect(allPlatformsAt(task({ platforms: [leg('xhs', 'adapted')] }), 'adapted')).toBe(true)
    expect(allPlatformsAt(task({ platforms: [leg('xhs', 'adapted'), leg('weibo')] }), 'adapted')).toBe(false)
  })
})

describe('due scheduled scan', () => {
  const now = new Date('2026-09-27T12:00:00.000Z')
  const overdue = task({
    taskId: '1f0a7b1e-5c2d-4e8f-9a3b-6d1c2e4f5a6c',
    mode: 'scheduled', status: 'scheduled', scheduledAt: '2026-09-27T10:00:00.000Z',
  })
  const future = task({ mode: 'scheduled', status: 'scheduled', scheduledAt: '2026-09-28T10:00:00.000Z' })

  it('surfaces only overdue scheduled tasks not yet recorded', () => {
    expect(dueScheduledTasks([overdue, future], now)).toEqual([overdue])
    expect(dueScheduledTasks([overdue], now)).toHaveLength(1)
    expect(dueScheduledTasks([task({ ...overdue, status: 'recorded' })], now)).toEqual([])
    expect(dueScheduledTasks([task({ mode: 'immediate', status: 'scheduled', scheduledAt: '2026-09-27T01:00:00.000Z' })], now)).toEqual([])
  })
})

describe('char cap check', () => {
  it('compares the body length against the cap, unlimited passes', () => {
    expect(exceedsCharLimit('a'.repeat(301), 300)).toBe(true)
    expect(exceedsCharLimit('a'.repeat(300), 300)).toBe(false)
    expect(exceedsCharLimit('a'.repeat(5000), null)).toBe(false)
  })
})

describe('manuscript pool projection', () => {
  it('flattens every project deliverable, newest project first', () => {
    const cards = manuscriptCards([
      { topic: 'theme-a' as OutputTopic, title: '旧稿', kind: 'article', platform: null, status: 'published', tags: [], summary: null, updatedAt: '', deliverables: ['old.md'], assetCount: 0, hasMetadata: true },
      { topic: 'theme-b' as OutputTopic, title: '新稿', kind: 'article', platform: null, status: 'ready', tags: [], summary: null, updatedAt: '', deliverables: ['new.md'], assetCount: 0, hasMetadata: true },
    ])
    expect(cards).toEqual([
      { theme: 'theme-b', file: 'new.md', title: '新稿', status: 'ready' },
      { theme: 'theme-a', file: 'old.md', title: '旧稿', status: 'published' },
    ])
    expect(manuscriptCards([])).toEqual([])
  })
})
