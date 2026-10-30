import { mkdir, mkdtemp, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { dirname, join } from 'node:path'
import { Context } from '@deepseek-ai/cordis'
import { describe, expect, it } from 'vitest'
import ContentTopicsGateway, {
  TOPIC_CATEGORIES_FILENAME, normalizeCategoryInput, readTopicCategories,
} from '../src/index.ts'
import type { TopicCategoryInput } from '../src/types.ts'

/** One minimal valid category input with every field overridable. */
function input(overrides: Partial<TopicCategoryInput> = {}): TopicCategoryInput {
  return { name: 'AI 编程', keywords: ['AI 编程', 'Copilot'], ...overrides }
}

/** One gateway over a fresh temporary outputs root, with its categories path. */
async function makeGateway() {
  const ctx = new Context()
  const root = await mkdtemp(join(tmpdir(), 'dsh-topics-cats-'))
  return {
    gateway: new ContentTopicsGateway(ctx, { root }),
    file: join(root, 'outputs', TOPIC_CATEGORIES_FILENAME),
  }
}

describe('normalizeCategoryInput', () => {
  it('trims the name and keywords, drops blanks and duplicate terms', () => {
    const { item, detail } = normalizeCategoryInput(input({ name: '  科技  ', keywords: [' A ', '', 'A', 'B'] }))
    expect(detail).toBeUndefined()
    expect(item?.name).toBe('科技')
    expect(item?.keywords).toEqual(['A', 'B'])
    expect(item?.createdAt).toBe(item?.updatedAt)
  })

  it('rejects an empty name, an over-cap name, no keywords, and an over-cap term', () => {
    expect(normalizeCategoryInput(input({ name: '  ' })).detail).toContain('name must be')
    expect(normalizeCategoryInput(input({ name: 'x'.repeat(41) })).detail).toContain('name must be')
    expect(normalizeCategoryInput(input({ keywords: [] })).detail).toContain('keywords must be')
    expect(normalizeCategoryInput(input({ keywords: ['x'.repeat(41)] })).detail).toContain('at most 40')
  })
})

describe('topic categories store + gateway', () => {
  it('lists an absent file as empty and creates through putCategory', async () => {
    const { gateway, file } = await makeGateway()
    const before = await gateway.listCategories()
    expect(before.items).toEqual([])
    const after = await gateway.putCategory(input())
    expect(await readTopicCategories(file)).toEqual(after)
    expect(after.items).toHaveLength(1)
    expect(after.items[0]?.name).toBe('AI 编程')
  })

  it('upserts by id: a known id keeps createdAt and restamps updatedAt', async () => {
    const { gateway } = await makeGateway()
    const created = await gateway.putCategory(input())
    const id = created.items[0]!.id
    const updated = await gateway.putCategory(input({ id, name: '改分类', keywords: ['新词'] }))
    expect(updated.items).toHaveLength(1)
    expect(updated.items[0]?.createdAt).toBe(created.items[0]?.createdAt)
    expect(updated.items[0]?.updatedAt).not.toBe(created.items[0]?.createdAt)
    expect(updated.items[0]?.keywords).toEqual(['新词'])
  })

  it('rejects invalid inputs with the normalizer reason and caps the store size', async () => {
    const { gateway, file } = await makeGateway()
    await expect(gateway.putCategory(input({ keywords: [] }))).rejects.toThrow(/invalid topic category/)
    // Seed the cap directly on disk: one write instead of 30 locked upserts.
    const now = '2026-10-01T00:00:00.000Z'
    const full = Array.from({ length: 30 }, (_, index) => ({
      id: `cat-${index}`, name: `分类 ${index}`, keywords: ['词'], createdAt: now, updatedAt: now,
    }))
    await mkdir(dirname(file), { recursive: true })
    await writeFile(file, JSON.stringify({ formatVersion: 0, items: full }), 'utf8')
    await expect(gateway.putCategory(input())).rejects.toThrow(/at most 30 categories/)
  })

  it('deletes by id and treats an unknown id as a no-op; topics stay untouched', async () => {
    const { gateway } = await makeGateway()
    const created = await gateway.putCategory(input())
    const id = created.items[0]!.id
    await expect(gateway.deleteCategory(id)).resolves.toMatchObject({ items: [] })
    await expect(gateway.deleteCategory(id)).resolves.toMatchObject({ items: [] })
  })

  it('normalizes feedUrls: blanks and duplicates drop, cap enforced, absent reads as undefined', async () => {
    const { item, detail } = normalizeCategoryInput(input({ feedUrls: [' https://a.example/rss ', '', 'https://a.example/rss', 'https://b.example/rss'] }))
    expect(detail).toBeUndefined()
    expect(item?.feedUrls).toEqual(['https://a.example/rss', 'https://b.example/rss'])
    expect(normalizeCategoryInput(input({ keywords: ['词'], feedUrls: Array.from({ length: 11 }, (_, index) => `https://f${String(index)}.example/rss`) })).detail).toContain('at most 10')
    // A stored record from before the field reads back as-is (optional wire).
    const { gateway, file } = await makeGateway()
    await gateway.putCategory(input())
    await writeFile(file, JSON.stringify({ formatVersion: 0, items: [{ id: 'cat-0', name: '旧记录', keywords: ['词'], createdAt: '2026-10-01T00:00:00.000Z', updatedAt: '2026-10-01T00:00:00.000Z' }] }), 'utf8')
    const read = await gateway.listCategories()
    expect(read.items[0]?.feedUrls).toBeUndefined()
  })

  it('stores a keyword-source topic alongside the categories', async () => {
    const { gateway } = await makeGateway()
    await gateway.putCategory(input())
    const after = await gateway.put({
      title: '收集到的选题',
      oneLiner: null,
      status: 'idea',
      source: { type: 'keyword', refId: null, url: 'https://weibo.example/1', snapshot: { title: '收集到的选题', summary: null, capturedAt: '2026-10-30T00:00:00.000Z' } },
      tags: [],
      description: null,
      score: null,
      planDate: null,
      scheduleItemId: null,
      topicDir: null,
    })
    expect(after.items[0]?.source.type).toBe('keyword')
  })

  it('refuses future formats and names bad records instead of dropping them silently', async () => {
    const { gateway, file } = await makeGateway()
    const created = await gateway.putCategory(input())
    await writeFile(file, JSON.stringify({ formatVersion: 1, items: [] }), 'utf8')
    const future = await gateway.listCategories()
    expect(future.items).toEqual([])
    expect(future.problems[0]).toContain('unsupported topic categories formatVersion')
    await writeFile(file, JSON.stringify({ formatVersion: 0, items: [created.items[0], { name: 7 }] }), 'utf8')
    const mixed = await gateway.listCategories()
    expect(mixed.items).toHaveLength(1)
    expect(mixed.problems[0]).toContain('dropped one invalid category record')
    await writeFile(file, '{truncated', 'utf8')
    const broken = await gateway.listCategories()
    expect(broken.items).toEqual([])
    expect(broken.problems[0]).toContain('not valid JSON')
  })
})
