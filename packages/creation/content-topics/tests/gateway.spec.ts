import { mkdtemp, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { Context } from '@deepseek-ai/cordis'
import { describe, expect, it } from 'vitest'
import ContentTopicsGateway, { ContentTopicsGateway as Named, TOPICS_FILENAME, readTopics } from '../src/index.ts'
import type { TopicItemInput } from '../src/types.ts'

/** One minimal valid upsert input with every optional field overridable. */
function input(overrides: Partial<TopicItemInput> = {}): TopicItemInput {
  return {
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
    ...overrides,
  }
}

/** One gateway over a fresh temporary outputs root, with its bank path. */
async function makeGateway() {
  const ctx = new Context()
  const root = await mkdtemp(join(tmpdir(), 'dsh-topics-'))
  return { gateway: new ContentTopicsGateway(ctx, { root }), file: join(root, 'outputs', TOPICS_FILENAME) }
}

describe('ContentTopicsGateway', () => {
  it('is the default export and registers under the contentTopics key', async () => {
    expect(Named).toBe(ContentTopicsGateway)
    const { gateway } = await makeGateway()
    expect(gateway.name).toBe('contentTopics')
  })

  it('lists an absent bank as empty and creates through put', async () => {
    const { gateway } = await makeGateway()
    const before = await gateway.list()
    expect(before.items).toEqual([])
    expect(before.problems).toEqual([])

    const after = await gateway.put(input({ tags: [' a ', ''] }))
    expect(after.items).toHaveLength(1)
    expect(after.items[0]?.title).toBe('选题一')
    expect(after.items[0]?.tags).toEqual(['a'])
    expect(after.items[0]?.createdAt).toBe(after.items[0]?.updatedAt)
  })

  it('upserts by id: a known id keeps createdAt and restamps updatedAt', async () => {
    const { gateway } = await makeGateway()
    const created = await gateway.put(input())
    const id = created.items[0]!.id
    // A second topic makes the upsert map walk past a non-matching candidate.
    await gateway.put(input({ title: '选题二' }))
    const updated = await gateway.put(input({ id, title: '改题' }))
    expect(updated.items).toHaveLength(2)
    expect(updated.items.find(item => item.id === id)?.title).toBe('改题')
    expect(updated.items.find(item => item.id === id)?.createdAt).toBe(created.items[0]?.createdAt)
    expect(updated.items.find(item => item.id === id)?.updatedAt).not.toBe(created.items[0]?.updatedAt)
  })

  it('rejects an invalid put with the normalizer reason', async () => {
    const { gateway } = await makeGateway()
    await expect(gateway.put(input({ title: '   ' }))).rejects.toThrow(/invalid topic item/)
    await expect(gateway.put(input({ status: 'published' as never }))).rejects.toThrow(/invalid topic item/)
  })

  it('deletes by id and treats an unknown id as a no-op', async () => {
    const { gateway } = await makeGateway()
    const created = await gateway.put(input())
    const id = created.items[0]!.id
    const after = await gateway.delete(id)
    expect(after.items).toEqual([])
    const again = await gateway.delete(id)
    expect(again.items).toEqual([])
  })

  it('refuses future formats and names bad records instead of dropping them silently', async () => {
    const { gateway, file } = await makeGateway()
    const created = await gateway.put(input())
    // Future format: the whole file refuses to load as current records.
    await writeFile(file, JSON.stringify({ formatVersion: 1, items: [] }), 'utf8')
    const future = await gateway.list()
    expect(future.items).toEqual([])
    expect(future.problems[0]).toContain('unsupported topic bank formatVersion')
    // One bad record among good ones: the good one survives, the bad is named.
    await writeFile(file, JSON.stringify({ formatVersion: 0, items: [created.items[0], { title: 7 }] }), 'utf8')
    const mixed = await gateway.list()
    expect(mixed.items).toHaveLength(1)
    expect(mixed.problems[0]).toContain('dropped one invalid topic record')
    // Truncated JSON refuses to load as a silent empty bank.
    await writeFile(file, '{truncated', 'utf8')
    const broken = await gateway.list()
    expect(broken.items).toEqual([])
    expect(broken.problems[0]).toContain('not valid JSON')
  })

  it('keeps the exported store helpers consistent with the Remote reads', async () => {
    const { gateway, file } = await makeGateway()
    await gateway.put(input())
    const direct = await readTopics(file)
    expect(direct.items).toHaveLength(1)
  })
})
