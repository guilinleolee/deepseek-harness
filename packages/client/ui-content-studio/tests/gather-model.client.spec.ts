import { describe, expect, it } from 'vitest'
import type { GatherMaterialId } from '@deepseek-ai/dsh-content-outputs/types'
import type { GatherItemDraft, GatherMaterial } from '../src/client/gather/types.ts'
import { applyQuota, failureBackoffMs, filterDrafts, isSourceDue, mergeDrafts } from '../src/client/gather/model.ts'

function draft(overrides: Omit<Partial<GatherItemDraft>, 'id'> & { id: string }): GatherItemDraft {
  return {
    id: overrides.id,
    rawGuid: overrides.rawGuid ?? null,
    url: overrides.url ?? `https://example.com/${overrides.id}`,
    title: overrides.title ?? overrides.id,
    publishedAt: overrides.publishedAt ?? '2026-09-20T10:00:00.000Z',
    summary: overrides.summary ?? null,
    content: overrides.content ?? null,
  }
}

function material(overrides: Omit<Partial<GatherMaterial>, 'id'> & { id: string }): GatherMaterial {
  return {
    id: overrides.id as GatherMaterialId,
    sourceId: overrides.sourceId ?? 's1',
    sourceName: overrides.sourceName ?? '源一',
    title: overrides.title ?? overrides.id,
    url: overrides.url ?? `https://example.com/${overrides.id}`,
    gatheredAt: overrides.gatheredAt ?? '2026-09-20T10:00:00.000Z',
    status: overrides.status ?? 'unread',
  }
}

describe('gather keyword filters', () => {
  it('drops drafts matching an excluded word from either layer', () => {
    const drafts = [draft({ id: 'a', title: 'AI 工具评测' }), draft({ id: 'b', title: '融资新闻' })]
    const filters = { sourceExcludeKeywords: ['融资'], includeKeywords: [], excludeKeywords: [] }
    expect(filterDrafts(drafts, filters, null, 10).map(item => item.id)).toEqual(['a'])
  })

  it('keeps only include-keyword matches when the task declares any', () => {
    const drafts = [draft({ id: 'a', title: 'AI 工具评测' }), draft({ id: 'b', title: '融资新闻' })]
    const filters = { sourceExcludeKeywords: [], includeKeywords: ['AI'], excludeKeywords: [] }
    expect(filterDrafts(drafts, filters, null, 10).map(item => item.id)).toEqual(['a'])
  })

  it('applies the since cursor on the publication instant and caps the run newest first', () => {
    const drafts = [
      draft({ id: 'old', publishedAt: '2026-09-01T10:00:00.000Z' }),
      draft({ id: 'new1', publishedAt: '2026-09-21T10:00:00.000Z' }),
      draft({ id: 'new2', publishedAt: '2026-09-22T10:00:00.000Z' }),
    ]
    const kept = filterDrafts(drafts, { sourceExcludeKeywords: [], includeKeywords: [], excludeKeywords: [] }, '2026-09-15T00:00:00.000Z', 1)
    expect(kept.map(item => item.id)).toEqual(['new2'])
  })
})

describe('gather manifest merge', () => {
  it('adds new drafts and never touches existing entries', () => {
    const existing = material({ id: 'a', status: 'favorite', title: '用户改过的标题' })
    const drafts = [draft({ id: 'a' }), draft({ id: 'b' })]
    const { merged, added } = mergeDrafts([existing], 's1', '源一', drafts, { now: '2026-09-25T00:00:00.000Z' })
    expect(merged).toHaveLength(2)
    expect(merged[0]).toBe(existing)
    expect(merged[0]!.status).toBe('favorite')
    expect(added.map(item => item.id)).toEqual(['b'])
    expect(added[0]!.status).toBe('unread')
    expect(added[0]!.gatheredAt).toBe('2026-09-25T00:00:00.000Z')
  })

  it('keys duplicates by the composite of source and draft id', () => {
    const existing = material({ id: 'a', sourceId: 's2' })
    const { added } = mergeDrafts([existing], 's1', '源一', [draft({ id: 'a' })], { now: '2026-09-25T00:00:00.000Z' })
    expect(added).toHaveLength(1)
  })
})

describe('gather retention quota', () => {
  it('keeps the newest 50 per source and always keeps favorite and picked', () => {
    const flood: GatherMaterial[] = Array.from({ length: 55 }, (_, index) => material({ id: `m${index}`, gatheredAt: `2026-09-01T00:00:${String(index).padStart(2, '0')}.000Z` }))
    const favorite = material({ id: 'fav', sourceId: 's1', status: 'favorite', gatheredAt: '2026-08-01T00:00:00.000Z' })
    const picked = material({ id: 'picked', sourceId: 's1', status: 'picked', gatheredAt: '2026-08-02T00:00:00.000Z' })
    const { kept, dropped } = applyQuota([...flood, favorite, picked])
    expect(kept.filter(item => item.status === 'unread')).toHaveLength(50)
    expect(kept.filter(item => item.status === 'favorite' || item.status === 'picked')).toHaveLength(2)
    // Every dropped entry is one of the five oldest unread items.
    expect(dropped.every(item => item.status === 'unread')).toBe(true)
    expect(dropped).toHaveLength(5)
  })

  it('tracks the quota per source, not per manifest', () => {
    const a = Array.from({ length: 50 }, (_, index) => material({ id: `a${index}`, sourceId: 'sA' }))
    const b = material({ id: 'b0', sourceId: 'sB' })
    const { kept, dropped } = applyQuota([...a, b])
    expect(dropped).toHaveLength(0)
    expect(kept).toHaveLength(51)
  })
})

describe('gather failure backoff', () => {
  it('doubles hourly and caps at 24h', () => {
    expect(failureBackoffMs(0)).toBe(0)
    expect(failureBackoffMs(1)).toBe(60 * 60 * 1000)
    expect(failureBackoffMs(2)).toBe(2 * 60 * 60 * 1000)
    expect(failureBackoffMs(3)).toBe(4 * 60 * 60 * 1000)
    expect(failureBackoffMs(6)).toBe(24 * 60 * 60 * 1000)
    expect(failureBackoffMs(50)).toBe(24 * 60 * 60 * 1000)
  })

  it('holds a failed source back past its own interval', () => {
    const now = '2026-09-25T12:00:00.000Z'
    const fresh = { intervalMinutes: 60, lastFetchedAt: '2026-09-25T11:30:00.000Z', consecutiveFailures: 0 }
    expect(isSourceDue(fresh, now)).toBe(false)
    const failed = { intervalMinutes: 30, lastFetchedAt: '2026-09-25T11:30:00.000Z', consecutiveFailures: 1 }
    expect(isSourceDue(failed, now)).toBe(false)
    const recovered = { intervalMinutes: 30, lastFetchedAt: '2026-09-25T10:00:00.000Z', consecutiveFailures: 1 }
    expect(isSourceDue(recovered, now)).toBe(true)
  })
})
