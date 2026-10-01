import { describe, expect, it } from 'vitest'
import type { TopicItem } from '@deepseek-ai/dsh-content-topics/types'
import {
  DEFAULT_TOPIC_BANK_CONFIG,
  TOPIC_SOURCE_TYPES,
  TOPIC_STATUSES,
  collectTags,
  filterTopics,
  formatScore,
  groupByStatus,
  gatherMaterialToTopicInput,
  loadTopicBankConfig,
  manualTopicInput,
  parseTopicsMarkdown,
  planWindowRange,
  saveTopicBankConfig,
  topicInputOf,
  topicToMarkdown,
  topicsToMarkdown,
  weekStart,
  withAppendedTags,
} from '../src/client/topic-bank.ts'

/** One stored topic with every field overridable. */
function topic(overrides: Partial<TopicItem> = {}): TopicItem {
  return {
    id: 't-1' as TopicItem['id'],
    title: '选题一',
    oneLiner: null,
    status: 'idea',
    source: { type: 'manual', refId: null, url: null, snapshot: null },
    tags: [],
    description: null,
    score: null,
    planDate: null,
    scheduleItemId: null,
    topicDir: null,
    createdAt: '2026-09-24T00:00:00.000Z',
    updatedAt: '2026-09-25T00:00:00.000Z',
    ...overrides,
  }
}

describe('topic-bank config migration', () => {
  it('falls back whole to the defaults for null, garbage, wrong versions, and bad shapes', () => {
    expect(loadTopicBankConfig(null)).toEqual(DEFAULT_TOPIC_BANK_CONFIG)
    expect(loadTopicBankConfig('not json {')).toEqual(DEFAULT_TOPIC_BANK_CONFIG)
    expect(loadTopicBankConfig('[]')).toEqual(DEFAULT_TOPIC_BANK_CONFIG)
    expect(loadTopicBankConfig(JSON.stringify({ version: 2, view: 'table', filters: DEFAULT_TOPIC_BANK_CONFIG.filters }))).toEqual(DEFAULT_TOPIC_BANK_CONFIG)
    expect(loadTopicBankConfig(JSON.stringify({ version: 1, view: 'gallery', filters: DEFAULT_TOPIC_BANK_CONFIG.filters }))).toEqual(DEFAULT_TOPIC_BANK_CONFIG)
    expect(loadTopicBankConfig(JSON.stringify({ version: 1, view: 'table' }))).toEqual(DEFAULT_TOPIC_BANK_CONFIG)
    expect(loadTopicBankConfig(JSON.stringify({ version: 1, view: 'table', filters: { ...DEFAULT_TOPIC_BANK_CONFIG.filters, source: 'rss' } }))).toEqual(DEFAULT_TOPIC_BANK_CONFIG)
    expect(loadTopicBankConfig(JSON.stringify({ version: 1, view: 'table', filters: { ...DEFAULT_TOPIC_BANK_CONFIG.filters, status: 'published' } }))).toEqual(DEFAULT_TOPIC_BANK_CONFIG)
    expect(loadTopicBankConfig(JSON.stringify({ version: 1, view: 'table', filters: { ...DEFAULT_TOPIC_BANK_CONFIG.filters, scoreMin: 11 } }))).toEqual(DEFAULT_TOPIC_BANK_CONFIG)
    expect(loadTopicBankConfig(JSON.stringify({ version: 1, view: 'table', filters: { ...DEFAULT_TOPIC_BANK_CONFIG.filters, scoreMin: 8, scoreMax: 2 } }))).toEqual(DEFAULT_TOPIC_BANK_CONFIG)
    expect(loadTopicBankConfig(JSON.stringify({ version: 1, view: 'table', filters: { ...DEFAULT_TOPIC_BANK_CONFIG.filters, tag: 3 } }))).toEqual(DEFAULT_TOPIC_BANK_CONFIG)
    expect(loadTopicBankConfig(JSON.stringify({ version: 1, view: 'table', filters: { ...DEFAULT_TOPIC_BANK_CONFIG.filters, planWindow: 'year' } }))).toEqual(DEFAULT_TOPIC_BANK_CONFIG)
    expect(loadTopicBankConfig(JSON.stringify({ version: 1, view: 'table', filters: { ...DEFAULT_TOPIC_BANK_CONFIG.filters, search: 7 } }))).toEqual(DEFAULT_TOPIC_BANK_CONFIG)
  })

  it('round-trips a saved configuration and repairs out-of-order bounds as defaults', () => {
    const customized = {
      version: 1 as const,
      view: 'kanban' as const,
      filters: { ...DEFAULT_TOPIC_BANK_CONFIG.filters, source: 'gather' as const, tag: '职场', planWindow: 'week' as const, search: 'AI' },
    }
    expect(loadTopicBankConfig(saveTopicBankConfig(customized))).toEqual(customized)
  })

  it('keeps the canonical status and source sequences', () => {
    expect(TOPIC_STATUSES).toEqual(['idea', 'todo', 'creating', 'done', 'shelved'])
    expect(TOPIC_SOURCE_TYPES).toEqual(['manual', 'gather', 'benchmark', 'interaction'])
  })
})

describe('plan windows', () => {
  it('anchors the week on Monday and the month on day one', () => {
    // 2026-09-25 is a Friday; its week runs Monday 09-21 through Sunday 09-27.
    expect(weekStart('2026-09-25')).toBe('2026-09-21')
    expect(planWindowRange('week', '2026-09-25')).toEqual(['2026-09-21', '2026-09-27'])
    expect(planWindowRange('month', '2026-09-25')).toEqual(['2026-09-01', '2026-09-30'])
  })

  it('handles month boundaries and year ends', () => {
    expect(weekStart('2026-09-01')).toBe('2026-08-31')
    expect(planWindowRange('week', '2026-09-01')).toEqual(['2026-08-31', '2026-09-06'])
    expect(planWindowRange('month', '2026-12-15')).toEqual(['2026-12-01', '2026-12-31'])
    expect(planWindowRange('month', '2026-02-10')).toEqual(['2026-02-01', '2026-02-28'])
  })
})

describe('filterTopics', () => {
  const filters = (overrides: Partial<typeof DEFAULT_TOPIC_BANK_CONFIG.filters> = {}) => ({
    ...DEFAULT_TOPIC_BANK_CONFIG.filters,
    ...overrides,
  })

  const bank = [
    topic(),
    topic({ id: 't-2' as TopicItem['id'], title: 'AI 工具测评', source: { type: 'gather', refId: 'm-1', url: 'https://a.example', snapshot: null }, status: 'todo', tags: ['AI', '职场'], score: { total: 7.5, source: 'manual', factors: null, evaluatedAt: '2026-09-25T01:00:00.000Z' }, planDate: '2026-09-23' }),
    topic({ id: 't-3' as TopicItem['id'], title: 'Shelved draft', status: 'shelved', description: 'old idea about careers', planDate: '2026-10-01' }),
  ]

  it('passes everything through the default filters', () => {
    expect(filterTopics(bank, filters(), '2026-09-25')).toHaveLength(3)
  })

  it('filters by source family, status, and tag', () => {
    expect(filterTopics(bank, filters({ source: 'gather' }), '2026-09-25').map(item => item.id)).toEqual(['t-2'])
    expect(filterTopics(bank, filters({ status: 'shelved' }), '2026-09-25').map(item => item.id)).toEqual(['t-3'])
    expect(filterTopics(bank, filters({ tag: 'AI' }), '2026-09-25').map(item => item.id)).toEqual(['t-2'])
  })

  it('hides unscored topics once the score range tightens', () => {
    const minOne = filterTopics(bank, filters({ scoreMin: 1 }), '2026-09-25')
    expect(minOne.map(item => item.id)).toEqual(['t-2'])
    expect(filterTopics(bank, filters({ scoreMin: 8 }), '2026-09-25')).toEqual([])
    expect(filterTopics(bank, filters({ scoreMax: 7 }), '2026-09-25')).toEqual([])
    expect(filterTopics(bank, filters({ scoreMin: 7, scoreMax: 8 }), '2026-09-25').map(item => item.id)).toEqual(['t-2'])
  })

  it('scopes by the plan window around today', () => {
    const week = filterTopics(bank, filters({ planWindow: 'week' }), '2026-09-25')
    expect(week.map(item => item.id)).toEqual(['t-2'])
    const month = filterTopics(bank, filters({ planWindow: 'month' }), '2026-09-25')
    expect(month.map(item => item.id)).toEqual(['t-2'])
    expect(month.some(item => item.id === 't-3')).toBe(false)
  })

  it('unplanned topics only show under the all window', () => {
    expect(filterTopics([topic()], filters({ planWindow: 'week' }), '2026-09-25')).toEqual([])
  })

  it('matches the keyword case-insensitively across title, pitch, description, and tags', () => {
    expect(filterTopics(bank, filters({ search: 'ai 工具' }), '2026-09-25').map(item => item.id)).toEqual(['t-2'])
    expect(filterTopics(bank, filters({ search: 'CAREERS' }), '2026-09-25').map(item => item.id)).toEqual(['t-3'])
    expect(filterTopics(bank, filters({ search: '选题一' }), '2026-09-25').map(item => item.id)).toEqual(['t-1'])
    expect(filterTopics(bank, filters({ search: 'no such' }), '2026-09-25')).toEqual([])
  })
})

describe('kanban helpers', () => {
  it('groups into the five canonical columns in order', () => {
    const bank = [topic({ status: 'done' }), topic({ id: 't-2' as TopicItem['id'], status: 'idea' })]
    const columns = groupByStatus(bank)
    expect(columns.map(column => column.status)).toEqual(['idea', 'todo', 'creating', 'done', 'shelved'])
    expect(columns.find(column => column.status === 'idea')?.items.map(item => item.id)).toEqual(['t-2'])
    expect(columns.find(column => column.status === 'done')?.items.map(item => item.id)).toEqual(['t-1'])
    expect(columns.find(column => column.status === 'todo')?.items).toEqual([])
  })

  it('collects the distinct tag set alphabetically', () => {
    const bank = [
      topic({ tags: ['b', 'a'] }),
      topic({ id: 't-2' as TopicItem['id'], tags: ['b', 'c'] }),
      topic({ id: 't-3' as TopicItem['id'], tags: [] }),
    ]
    expect(collectTags(bank)).toEqual(['a', 'b', 'c'])
  })

  it('formats integral and fractional scores', () => {
    expect(formatScore(7)).toBe('7')
    expect(formatScore(7.5)).toBe('7.5')
    expect(formatScore(7.25)).toBe('7.3')
  })
})

describe('markdown export schema', () => {
  it('round-trips one topic losslessly, including quoting specials', () => {
    const item = topic({
      title: 'He said "run" \\ fast: AI 工具',
      oneLiner: 'one: liner',
      status: 'todo',
      source: { type: 'gather', refId: 'm-1', url: 'https://a.example/x', snapshot: null },
      tags: ['a, b', 'quote"tag', 'plain'],
      score: { total: 7.5, source: 'manual', factors: null, evaluatedAt: '2026-09-25T01:00:00.000Z' },
      planDate: '2026-09-30',
      description: 'Body line one\n\nBody line two',
    })
    const parsed = parseTopicsMarkdown(topicToMarkdown(item))
    expect(parsed).toEqual({
      title: 'He said "run" \\ fast: AI 工具',
      oneLiner: 'one: liner',
      status: 'todo',
      sourceType: 'gather',
      sourceUrl: 'https://a.example/x',
      tags: ['a, b', 'quote"tag', 'plain'],
      score: 7.5,
      planDate: '2026-09-30',
      updatedAt: '2026-09-25T00:00:00.000Z',
      description: 'Body line one\n\nBody line two',
    })
  })

  it('round-trips the empty shapes: nulls, no tags, no score, no body', () => {
    const item = topic()
    expect(parseTopicsMarkdown(topicToMarkdown(item))).toEqual({
      title: '选题一',
      oneLiner: null,
      status: 'idea',
      sourceType: 'manual',
      sourceUrl: null,
      tags: [],
      score: null,
      planDate: null,
      updatedAt: '2026-09-25T00:00:00.000Z',
      description: null,
    })
  })

  it('keeps bare dates and numbers in the emitted frontmatter', () => {
    const text = topicToMarkdown(topic({ planDate: '2026-09-30', score: { total: 8, source: 'manual', factors: null, evaluatedAt: '2026-09-25T01:00:00.000Z' } }))
    expect(text).toContain('planDate: 2026-09-30\n')
    expect(text).toContain('score: 8\n')
    expect(text).toContain('planDate: 2026-09-30\n')
  })

  it('joins the batch export as one document', () => {
    const text = topicsToMarkdown([topic(), topic({ id: 't-2' as TopicItem['id'], title: 'second' })])
    expect(text).toContain('title: "选题一"')
    expect(text).toContain('title: "second"')
  })

  it('rejects anything that is not this schema output', () => {
    expect(parseTopicsMarkdown('no frontmatter')).toBeNull()
    expect(parseTopicsMarkdown('---\nonly: open\n')).toBeNull()
    expect(parseTopicsMarkdown('---\ntitle: "x"\nstatus: nope\n---\n')).toBeNull()
    expect(parseTopicsMarkdown('---\ntitle: "x"\nstatus: idea\nsourceType: rss\n---\n')).toBeNull()
    expect(parseTopicsMarkdown('---\ntitle: "x"\nstatus: idea\nsourceType: manual\ntags: a, b\n---\n')).toBeNull()
    expect(parseTopicsMarkdown('---\ntitle: "x"\nstatus: idea\nsourceType: manual\ntags: []\nscore: 42\n---\n')).toBeNull()
    expect(parseTopicsMarkdown('---\ntitle: "x"\nstatus: idea\nsourceType: manual\ntags: []\nplanDate: 2026/09/30\n---\n')).toBeNull()
    expect(parseTopicsMarkdown('---\nstatus: idea\nsourceType: manual\ntags: []\n---\n')).toBeNull()
    expect(parseTopicsMarkdown('---\ntitle: ""\nstatus: idea\nsourceType: manual\ntags: []\n---\n')).toBeNull()
  })
})

describe('upsert inputs', () => {
  it('builds a gather join carrying the material identity and snapshot', () => {
    expect(gatherMaterialToTopicInput({ id: 'm-1', title: '素材', url: 'https://a.example', summary: '摘要' }, '2026-09-25T02:00:00.000Z')).toEqual({
      title: '素材',
      oneLiner: '摘要',
      status: 'idea',
      source: { type: 'gather', refId: 'm-1', url: 'https://a.example', snapshot: { title: '素材', summary: '摘要', capturedAt: '2026-09-25T02:00:00.000Z' } },
      tags: [],
      description: null,
      score: null,
      planDate: null,
      scheduleItemId: null,
      topicDir: null,
    })
    const withoutSummary = gatherMaterialToTopicInput({ id: 'm-2', title: '素材', url: 'https://a.example' }, '2026-09-25T02:00:00.000Z')
    expect(withoutSummary.oneLiner).toBeNull()
    expect(withoutSummary.source.snapshot?.summary).toBeNull()
  })

  it('builds a manual topic with only the title and the idea start', () => {
    expect(manualTopicInput('新选题')).toEqual({
      title: '新选题',
      oneLiner: null,
      status: 'idea',
      source: { type: 'manual', refId: null, url: null, snapshot: null },
      tags: [],
      description: null,
      score: null,
      planDate: null,
      scheduleItemId: null,
      topicDir: null,
    })
  })

  it('projects a stored topic back to an input with patches and copied tags', () => {
    const item = topic({ tags: ['a'] })
    const input = topicInputOf(item, { status: 'done' })
    expect(input.id).toBe(item.id)
    expect(input.status).toBe('done')
    expect(input.tags).toEqual(['a'])
    const mutableTags = input.tags as string[]
    mutableTags.push('mutated')
    expect(item.tags).toEqual(['a'])
  })

  it('appends batch tags deduplicated and skips blanks', () => {
    const item = topic({ tags: ['a', 'b'] })
    expect(withAppendedTags(item, ['b', 'c', '']).tags).toEqual(['a', 'b', 'c'])
  })
})
