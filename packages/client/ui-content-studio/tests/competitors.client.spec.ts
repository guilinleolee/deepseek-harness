import { describe, expect, it } from 'vitest'
import type { CompetitorManifest, CompetitorWork } from '@deepseek-ai/dsh-content-outputs/types'
import {
  aggregateAccountDigest, buildIdeaMarkdown, competitorWorkToTopicInput, exportAccounts, heatByWork, importAccounts,
  aggregateAuditDigest, buildSyncAssetMarkdown, importSyncPayload, interactionScore, isAccountStale, newId, sortWorks, upsertWork,
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

describe('volume compare word collection', () => {
  it('derives the niche-word rows from account topics, deduped and non-empty', () => {
    const accounts: readonly CompetitorAccount[] = [
      { id: 'acc-1', name: 'A', platform: 'xhs', homepageUrl: '', topics: ['效率工具', 'AI'], priority: 'medium', note: '', positioning: '', followerTier: '', monetization: '', intervalDays: 7, enabled: true, createdAt: 't' },
      { id: 'acc-2', name: 'B', platform: 'xhs', homepageUrl: '', topics: ['效率工具', ' '], priority: 'medium', note: '', positioning: '', followerTier: '', monetization: '', intervalDays: 7, enabled: true, createdAt: 't' },
    ]
    const words = [...new Set(accounts.flatMap(account => [...account.topics]))]
      .filter(word => word.trim().length > 0)
    expect(words).toHaveLength(2)
    expect(words).toContain('效率工具')
    expect(words).toContain('AI')
  })
})

describe('sortWorks', () => {
  const sortable = [
    work({ id: 'cw-a', platformWorkId: 'n-a', publishedAt: '2026-09-01T00:00:00.000Z', metrics: [{ t: 't', likes: 10, comments: 0, shares: 5 }] }),
    work({ id: 'cw-b', platformWorkId: 'n-b', publishedAt: '2026-09-10T00:00:00.000Z', metrics: [{ t: 't', likes: 2, comments: 0, shares: 40 }] }),
    work({ id: 'cw-c', platformWorkId: 'n-c', publishedAt: '2026-09-05T00:00:00.000Z', metrics: [{ t: 't', likes: 4, comments: 0, shares: 0 }] }),
  ]

  it('sorts newest first by publication instant', () => {
    expect(sortWorks(sortable, 'newest').map(item => item.id)).toEqual(['cw-b', 'cw-c', 'cw-a'])
  })

  it('sorts by interaction score', () => {
    // scores: cw-b = 2 + 3×40 = 122, cw-a = 10 + 3×5 = 25, cw-c = 4
    expect(sortWorks(sortable, 'score').map(item => item.id)).toEqual(['cw-b', 'cw-a', 'cw-c'])
  })

  it('sorts by the newest saves count so collect-heavy tutorials rank first', () => {
    expect(sortWorks(sortable, 'collects').map(item => item.id)).toEqual(['cw-b', 'cw-a', 'cw-c'])
  })
})

describe('importSyncPayload', () => {
  const accounts: readonly CompetitorAccount[] = [
    { id: 'acc-1', name: '竞品A', platform: 'xhs', homepageUrl: '', topics: [], priority: 'medium', note: '', positioning: '', followerTier: '', monetization: '', intervalDays: 3, enabled: true, createdAt: 't' },
  ]
  const payload = JSON.stringify({
    version: 1,
    platform: 'xhs',
    account: { name: '竞品A', followers: '9万', bio: '30年企业实战派' },
    works: [
      { platformWorkId: 'native-sync-1', title: '同步爆款', likes: 1514, comments: 17, shares: 900, url: 'https://x.example/s1', publishedAt: '2026-10-01T00:00:00.000Z' },
      { title: '无ID作品', likes: 3 },
      { title: '   ' },
    ],
  })

  it('upserts every valid entry through the manual-import dedup path', () => {
    const result = importSyncPayload(payload, emptyManifest(), accounts)
    expect(result.added).toBe(2)
    expect(result.updated).toBe(0)
    expect(result.manifest.works).toHaveLength(2)
    const synced = result.manifest.works.find(item => item.platformWorkId === 'native-sync-1')
    expect(synced?.metrics[0]).toMatchObject({ likes: 1514, comments: 17, shares: 900 })
  })

  it('refreshes the matched account follower tier and stamps syncedAt in the view', () => {
    const result = importSyncPayload(payload, emptyManifest(), accounts)
    expect(result.accountPatch).toEqual({ accountId: 'acc-1', followerTier: '9万', positioning: '30年企业实战派' })
  })

  it('keeps a stored positioning instead of overwriting it with the bio', () => {
    const positioned = [{ ...accounts[0]!, positioning: '已有定位' }]
    const result = importSyncPayload(payload, emptyManifest(), positioned)
    expect(result.accountPatch).toEqual({ accountId: 'acc-1', followerTier: '9万' })
  })

  it('updates an existing work instead of duplicating it', () => {
    const seeded = importSyncPayload(payload, emptyManifest(), accounts).manifest
    const again = importSyncPayload(payload, seeded, accounts)
    expect(again.added).toBe(0)
    expect(again.updated).toBe(2)
    expect(again.manifest.works).toHaveLength(2)
  })

  it('rejects wrong versions, unknown platforms, and unparseable JSON without throwing', () => {
    const bad = [
      'not json',
      JSON.stringify({ version: 2, platform: 'xhs', account: { name: 'A' }, works: [] }),
      JSON.stringify({ version: 1, platform: 'pinterest', account: { name: 'A' }, works: [] }),
      JSON.stringify({ version: 1, platform: 'xhs', account: {}, works: [] }),
    ]
    for (const json of bad) {
      const result = importSyncPayload(json, emptyManifest(), accounts)
      expect(result).toMatchObject({ added: 0, updated: 0 })
    }
  })

  it('imports under an unassigned account id when no registry account matches', () => {
    const orphan = JSON.stringify({ version: 1, platform: 'xhs', account: { name: '陌生号' }, works: [{ title: '外部作品', likes: 1 }] })
    const result = importSyncPayload(orphan, emptyManifest(), accounts)
    expect(result.added).toBe(1)
    expect(result.manifest.works[0]?.accountId).toBe('unassigned')
    expect(result.accountPatch).toBeUndefined()
  })
})

describe('aggregateAuditDigest', () => {
  it('feeds registry facts and median-based distribution facts, capped', () => {
    const account: CompetitorAccount = {
      id: 'acc-1', name: '竞品A', platform: 'xhs', homepageUrl: '', topics: [], priority: 'medium',
      note: '', positioning: '中小企业的AI落地', followerTier: '9万', monetization: '扣字引流私域',
      intervalDays: 3, enabled: true, createdAt: 't',
    }
    const works = [
      work({ id: 'cw-1', platformWorkId: 'n-1', metrics: [{ t: 't', likes: 10, comments: 2, shares: 40 }] }),
      work({ id: 'cw-2', platformWorkId: 'n-2', metrics: [{ t: 't', likes: 4, comments: 1, shares: 5 }] }),
    ]
    const digest = aggregateAuditDigest(account, works)
    expect(digest).toContain('9万')
    expect(digest).toContain('中小企业的AI落地')
    expect(digest).toContain('中位数')
    expect(digest).toContain('7') // 收藏中位数 (40+5)/2
    expect(digest.length).toBeLessThanOrEqual(1000)
  })

  it('states unknown recency instead of inventing a number', () => {
    const account: CompetitorAccount = {
      id: 'acc-1', name: 'A', platform: 'xhs', homepageUrl: '', topics: [], priority: 'medium',
      note: '', positioning: '', followerTier: '', monetization: '', intervalDays: 3, enabled: true, createdAt: 't',
    }
    expect(aggregateAuditDigest(account, [])).toContain('未知')
  })
})

describe('sync body assets', () => {
  const payloadWithContent = JSON.stringify({
    version: 1,
    platform: 'xhs',
    account: { name: '竞品A' },
    works: [
      { platformWorkId: 'n-1', title: '带正文', body: '正文内容', hotComments: ['包不出来', '  ', '多练几次'], likes: 5 },
      { platformWorkId: 'n-2', title: '只有评论', hotComments: ['求教程'] },
      { platformWorkId: 'n-3', title: '无内容', likes: 1 },
      { title: '无ID带正文', body: '无法落文件' },
    ],
  })

  it('lands a stable body asset per platform id and skips id-less entries', () => {
    const result = importSyncPayload(payloadWithContent, emptyManifest(), [])
    expect(result.assets).toHaveLength(2)
    expect(result.assets.map(asset => asset.file)).toEqual(['sync-n-1.md', 'sync-n-2.md'])
    expect(result.assets[0]!.content).toContain('正文内容')
    expect(result.assets[0]!.content).toContain('- 包不出来')
    expect(result.assets[0]!.content).not.toContain('  ')
    expect(result.manifest.works.find(item => item.platformWorkId === 'n-1')?.textFile).toBe('sync-n-1.md')
    expect(result.manifest.works.find(item => item.platformWorkId === 'n-3')?.textFile).toBeUndefined()
    expect(result.manifest.works.find(item => item.title === '无ID带正文')?.textFile).toBeUndefined()
  })

  it('buildSyncAssetMarkdown renders title, body, and trimmed comments', () => {
    const markdown = buildSyncAssetMarkdown({ title: '标题', body: '正文', hotComments: [' 评A ', '评B'] })
    expect(markdown.startsWith('# 标题\n\n正文')).toBe(true)
    expect(markdown).toContain('## 热门评论')
    expect(markdown).toContain('- 评A')
    expect(buildSyncAssetMarkdown({ title: '只有标题' })).toBe('# 只有标题\n\n')
  })
})
