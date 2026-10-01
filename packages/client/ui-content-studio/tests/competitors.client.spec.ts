import { describe, expect, it } from 'vitest'
import type { CompetitorManifest, CompetitorWork } from '@deepseek-ai/dsh-content-outputs/types'
import {
  aggregateAccountDigest, buildIdeaMarkdown, competitorWorkToTopicInput, exportAccounts, heatByWork, importAccounts,
  interactionScore, isAccountStale, newId, upsertWork,
} from '../src/client/competitors.ts'
import type { CompetitorAccount } from '../src/client/competitors.ts'

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
    metrics: [{ t: '2026-09-25T00:00:00.000Z', likes: 0, comments: 0, shares: 0 }],
    hot: false,
    favorite: false,
    via: 'manual',
    analysis: { status: 'none' },
    ...rest,
  }
}

function emptyManifest(): CompetitorManifest {
  return { formatVersion: 0, syncedAt: {}, works: [], reports: [] }
}

describe('interactionScore', () => {
  it('weights conversation over applause', () => {
    expect(interactionScore([{ t: 't', likes: 10, comments: 2, shares: 1 }])).toBe(17)
  })

  it('counts views as a reach tiebreaker on the newest snapshot', () => {
    expect(interactionScore([
      { t: 't1', likes: 100, comments: 0, shares: 0 },
      { t: 't2', likes: 10, comments: 2, shares: 1, views: 1000 },
    ])).toBe(27)
    expect(interactionScore([])).toBe(0)
  })
})

describe('heatByWork', () => {
  it("ranks against the account's own distribution once the sample is big enough", () => {
    const works = Array.from({ length: 10 }, (_, index) => work({
      id: `cw-${index}`,
      platformWorkId: `native-${index}`,
      metrics: [{ t: 't', likes: index + 1, comments: 0, shares: 0 }],
    }))
    const heat = heatByWork(works)
    expect(heat.get('cw-9')!.level).toBe('hot')
    expect(heat.get('cw-5')!.level).toBe('normal')
    expect(heat.get('cw-0')!.level).toBe('cold')
  })

  it('reads small samples as normal instead of ranking them', () => {
    const works = Array.from({ length: 3 }, (_, index) => work({ id: `cw-${index}`, platformWorkId: `n-${index}` }))
    const heat = heatByWork(works)
    expect([...heat.values()].every(entry => entry.level === 'normal')).toBe(true)
  })
})

describe('upsertWork', () => {
  it('creates a new work with an id and a fresh analysis', () => {
    const result = upsertWork(emptyManifest(), {
      accountId: 'acc-1', accountName: '竞品A', platform: 'xhs', platformWorkId: 'native-1', title: '作品',
      metrics: { t: 't', likes: 5, comments: 0, shares: 0 },
    })
    expect(result.updated).toBe(false)
    expect(result.manifest.works[0]!.id).toMatch(/^cw-/)
    expect(result.manifest.works[0]!.analysis).toEqual({ status: 'none' })
  })

  it('dedupes on platform + account + platform work id and appends a new snapshot', () => {
    const start = emptyManifest()
    const draft = {
      accountId: 'acc-1', accountName: '竞品A', platform: 'xhs' as const, platformWorkId: 'native-1', title: '作品',
      metrics: { t: 't1', likes: 5, comments: 0, shares: 0 },
    }
    const first = upsertWork(start, draft)
    const second = upsertWork(first.manifest, { ...draft, metrics: { t: 't2', likes: 9, comments: 0, shares: 0 } })
    expect(second.updated).toBe(true)
    expect(second.manifest.works).toHaveLength(1)
    expect(second.manifest.works[0]!.metrics).toHaveLength(2)
    expect(second.manifest.works[0]!.id).toBe(first.manifest.works[0]!.id)
  })

  it('skips a snapshot that repeats the newest values', () => {
    const draft = {
      accountId: 'acc-1', accountName: '竞品A', platform: 'xhs' as const, platformWorkId: 'native-1', title: '作品',
      metrics: { t: 't1', likes: 5, comments: 0, shares: 0 },
    }
    const first = upsertWork(emptyManifest(), draft)
    const second = upsertWork(first.manifest, { ...draft, metrics: { t: 't2', likes: 5, comments: 0, shares: 0 } })
    expect(second.manifest.works[0]!.metrics).toHaveLength(1)
  })

  it('falls back to the title as the dedup key and keeps markers and analysis', () => {
    const seeded = upsertWork(emptyManifest(), {
      accountId: 'acc-1', accountName: '竞品A', platform: 'douyin' as const, platformWorkId: '', title: '同题作品',
      metrics: { t: 't1', likes: 1, comments: 0, shares: 0 },
    })
    const marked: CompetitorManifest = {
      ...seeded.manifest,
      works: seeded.manifest.works.map(entry => ({ ...entry, hot: true, analysis: { status: 'done', result: {
        hookType: '痛点', structure: '清单', painPoints: [], topics: [], risks: [], reusable: [], migrationTopics: [], commentInsight: 'unavailable',
      } } })),
    }
    const again = upsertWork(marked, {
      accountId: 'acc-1', accountName: '竞品A', platform: 'douyin', platformWorkId: 'late-id', title: '同题作品',
      metrics: { t: 't2', likes: 2, comments: 0, shares: 0 },
    })
    expect(again.updated).toBe(true)
    expect(again.manifest.works[0]!.platformWorkId).toBe('title:同题作品')
    expect(again.manifest.works[0]!.hot).toBe(true)
    expect(again.manifest.works[0]!.analysis.status).toBe('done')
  })
})

describe('isAccountStale', () => {
  const account = {
    id: 'acc-1', name: '竞品A', platform: 'xhs' as const, homepageUrl: '', topics: [], priority: 'medium' as const,
    note: '', positioning: '', followerTier: '', monetization: '', intervalDays: 3 as const, enabled: true, createdAt: 't',
  }

  it('reads a never-synced enabled account as stale', () => {
    expect(isAccountStale(account, emptyManifest(), new Date('2026-09-25T00:00:00.000Z'))).toBe(true)
  })

  it('honors the interval and the enable switch', () => {
    const manifest: CompetitorManifest = { ...emptyManifest(), syncedAt: { 'acc-1': '2026-09-24T00:00:00.000Z' } }
    expect(isAccountStale(account, manifest, new Date('2026-09-25T00:00:00.000Z'))).toBe(false)
    expect(isAccountStale(account, manifest, new Date('2026-09-27T00:01:00.000Z'))).toBe(true)
    expect(isAccountStale({ ...account, enabled: false }, manifest, new Date('2026-09-27T00:01:00.000Z'))).toBe(false)
  })
})

describe('importAccounts', () => {
  const account: CompetitorAccount = {
    id: 'acc-1', name: '竞品A', platform: 'xhs', homepageUrl: '', topics: [], priority: 'medium',
    note: '', positioning: '', followerTier: '', monetization: '', intervalDays: 3, enabled: true, createdAt: 't',
  }

  it('skips name+platform duplicates inside and against the registry', () => {
    const first = importAccounts(JSON.stringify([account]), [])
    expect(first).toMatchObject({ added: 1, skipped: 0 })
    const second = importAccounts(JSON.stringify([account, { ...account, note: 'changed' }]), first.accounts)
    expect(second).toMatchObject({ added: 0, skipped: 2 })
  })

  it('keeps the registry unchanged on invalid JSON', () => {
    const existing = [account]
    const result = importAccounts('{broken', existing)
    expect(result.accounts).toBe(existing)
    expect(result.added).toBe(0)
  })

  it('round-trips the export payload', () => {
    const roundTrip = importAccounts(exportAccounts([account]), [])
    expect(roundTrip.added).toBe(1)
    expect(roundTrip.accounts[0]!.name).toBe('竞品A')
  })
})

describe('aggregateAccountDigest', () => {
  it('summarizes facts only and stays inside the token budget', () => {
    const analyzed = work({
      analysis: { status: 'done', result: {
        hookType: '痛点（时间焦虑）', structure: '清单', painPoints: [], topics: ['效率工具', '职场'], risks: [], reusable: [], migrationTopics: [], commentInsight: 'unavailable',
      } },
    })
    const digest = aggregateAccountDigest('竞品A', 'xhs', [analyzed, work({ id: 'cw-2', platformWorkId: 'n2' })])
    expect(digest).toContain('竞品A')
    expect(digest).toContain('选题分布')
    expect(digest.length).toBeLessThanOrEqual(1000)
  })
})

describe('buildIdeaMarkdown', () => {
  it('carries the structured header a later gather index can pick up', () => {
    const markdown = buildIdeaMarkdown(work(), '给小团队的工具组合选题')
    expect(markdown).toContain('kind: topic-idea')
    expect(markdown).toContain('sourceWorkId: cw-1')
    expect(markdown).toContain('给小团队的工具组合选题')
  })
})

describe('newId', () => {
  it('produces unique prefixed ids', () => {
    const ids = new Set(Array.from({ length: 50 }, () => newId('acc')))
    expect(ids.size).toBe(50)
    expect([...ids][0]!.startsWith('acc-')).toBe(true)
  })
})

describe('competitorWorkToTopicInput', () => {
  it('builds a benchmark-sourced idea anchored to the work id', () => {
    const input = competitorWorkToTopicInput(work({
      url: 'https://x.example/w1',
      analysis: { status: 'done', result: {
        hookType: '悬念', structure: '三段式', painPoints: ['没时间'], topics: ['效率'],
        risks: [], reusable: ['清单体'], migrationTopics: ['给小团队的工具组合选题'], commentInsight: 'unavailable',
      } },
    }), '2026-09-28T00:00:00.000Z')
    expect(input.status).toBe('idea')
    expect(input.source).toEqual({
      type: 'benchmark', refId: 'cw-1', url: 'https://x.example/w1',
      snapshot: { title: '一条对标作品', summary: '给小团队的工具组合选题', capturedAt: '2026-09-28T00:00:00.000Z' },
    })
    expect(input.title).toBe('给小团队的工具组合选题')
    expect(input.tags).toEqual(['对标'])
  })

  it('falls back to the work title when no teardown exists', () => {
    const input = competitorWorkToTopicInput(work(), '2026-09-28T00:00:00.000Z')
    expect(input.title).toBe('一条对标作品')
    expect(input.oneLiner).toBeNull()
    expect(input.source.url).toBeNull()
  })
})
