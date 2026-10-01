import { mkdtemp, readFile, readdir, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { afterEach, describe, expect, it } from 'vitest'
import type { TemplateId, TemplateTag, TemplateTagId } from '../src/types.ts'
import {
  HISTORY_DIRNAME, TEMPLATES_FILENAME, TEMPLATE_HISTORY_LIMIT, TAXONOMY_FILENAME,
  deleteTemplateFile, exportTemplatePack, importTemplatePack, parseTemplateTaxonomy,
  parseTemplatesManifest, putTemplateFile, putTemplateTagsFile, readTemplateHistory,
  readTemplateLibrary, setTemplateStatusFile,
} from '../src/template/store.ts'
import type { TemplateInput, TemplatePack, TemplateRecord } from '../src/types.ts'

/** Brand the wire constants at the spec's single boundary. */
const tid = (value: string): TemplateId => value as TemplateId
const tagId = (value: string): TemplateTagId => value as TemplateTagId
const tag = (id: string, name: string): TemplateTag => ({ id: tagId(id), name })

let dir: string | undefined

afterEach(async () => {
  if (dir !== undefined) await rm(dir, { recursive: true, force: true })
  dir = undefined
})

async function storeRoot(): Promise<string> {
  dir = await mkdtemp(join(tmpdir(), 'template-store-'))
  return dir
}

/** One full valid input, overridden per test. */
function input(overrides: Partial<TemplateInput> = {}): TemplateInput {
  return {
    name: '小红书爆款图文骨架',
    category: 'creation',
    description: '三段式图文创作提示词',
    tagIds: [],
    body: '# {{title}}\n\n{{hook}}\n\n{{body}}',
    variables: [
      { name: 'title', label: '标题', description: '笔记标题', defaultValue: '', required: true },
      { name: 'hook', label: '开头钩子', description: '首句', defaultValue: '刷到这条的你', required: false },
      { name: 'body', label: '正文', description: '主体内容', defaultValue: '', required: true },
    ],
    ...overrides,
  }
}

/** A full valid stored record for pack fixtures, overridden per test. */
function packRecord(overrides: Partial<TemplateRecord> = {}): TemplateRecord {
  return {
    id: tid('01890a5d-ac96-774b-bcce-b302099a8057'),
    name: '导入模板',
    category: 'topic',
    description: '',
    tagIds: [],
    body: '选题：{{topic}}',
    variables: [{ name: 'topic', label: '选题', description: '', defaultValue: '', required: true }],
    status: 'active',
    version: 3,
    createdAt: '2026-09-01T00:00:00.000Z',
    updatedAt: '2026-09-01T00:00:00.000Z',
    ...overrides,
  }
}

function pack(overrides: Partial<TemplatePack> = {}): TemplatePack {
  return {
    format: 'dsh-template-pack',
    formatVersion: 1,
    exportedAt: '2026-09-27T00:00:00.000Z',
    templates: [],
    tags: [],
    ...overrides,
  }
}

describe('parseTemplatesManifest', () => {
  it('reads an absent file as empty', () => {
    expect(parseTemplatesManifest('')).toEqual({ kind: 'empty' })
  })

  it('names invalid JSON as a refuse-write state', () => {
    const parsed = parseTemplatesManifest('{broken')
    expect(parsed.kind).toBe('invalid')
  })

  it('rejects a future format version', () => {
    const parsed = parseTemplatesManifest(JSON.stringify({ formatVersion: 1, templates: [] }))
    expect(parsed.kind).toBe('invalid')
    if (parsed.kind === 'invalid') expect(parsed.problem).toContain('formatVersion 1')
  })

  it('drops malformed records into problems and keeps valid ones', () => {
    const good = packRecord()
    const raw = JSON.stringify({ formatVersion: 0, templates: [good, { id: 'x' }] })
    const parsed = parseTemplatesManifest(raw)
    expect(parsed.kind).toBe('ok')
    if (parsed.kind === 'ok') {
      expect(parsed.manifest.templates).toHaveLength(1)
      expect(parsed.problems).toHaveLength(1)
    }
  })
})

describe('putTemplateFile', () => {
  it('creates at version 1 and writes the first snapshot', async () => {
    const root = await storeRoot()
    const record = await putTemplateFile(root, input(), '2026-09-27T00:00:00.000Z')
    expect(record.version).toBe(1)
    expect(record.status).toBe('active')
    const history = await readTemplateHistory(root, record.id)
    expect(history).toHaveLength(1)
    expect(history[0]?.version).toBe(1)
    expect(history[0]?.record.body).toBe(record.body)
  })

  it('bumps the version and snapshots every save', async () => {
    const root = await storeRoot()
    const created = await putTemplateFile(root, input(), '2026-09-27T00:00:00.000Z')
    const updated = await putTemplateFile(root, input({ id: created.id, body: '# {{title}} v2' }), '2026-09-27T01:00:00.000Z')
    expect(updated.version).toBe(2)
    const history = await readTemplateHistory(root, created.id)
    expect(history.map(entry => entry.version)).toEqual([2, 1])
  })

  it('rejects a duplicate display name from another record', async () => {
    const root = await storeRoot()
    await putTemplateFile(root, input(), '2026-09-27T00:00:00.000Z')
    await expect(putTemplateFile(root, input({ name: ' 小红书爆款图文骨架 ' }))).rejects.toThrow(/duplicate template name/)
  })

  it('rejects unknown ids instead of resurrecting deleted templates', async () => {
    const root = await storeRoot()
    await expect(putTemplateFile(root, input({ id: tid('missing') }))).rejects.toThrow(/unknown template/)
  })

  it('validates variable names and rejects duplicates', async () => {
    const root = await storeRoot()
    await expect(putTemplateFile(root, input({ variables: [{ name: '9bad', label: '', description: '', defaultValue: '', required: true }] }))).rejects.toThrow(/variable name/)
    await expect(putTemplateFile(root, input({
      variables: [
        { name: 'title', label: '', description: '', defaultValue: '', required: true },
        { name: 'title', label: '', description: '', defaultValue: '', required: false },
      ],
    }))).rejects.toThrow(/must not repeat/)
  })

  it('refuses to write over a store whose parse dropped records', async () => {
    const root = await storeRoot()
    await putTemplateFile(root, input(), '2026-09-27T00:00:00.000Z')
    const file = join(root, TEMPLATES_FILENAME)
    const stored = JSON.parse(await readFile(file, 'utf8')) as { templates: unknown[] }
    stored.templates.push({ broken: true })
    await writeFile(file, `${JSON.stringify(stored)}\n`)
    await expect(putTemplateFile(root, input({ name: '另一个模板' }))).rejects.toThrow(/refusing to write/)
  })
})

describe('setTemplateStatusFile', () => {
  it('flips status without writing a snapshot', async () => {
    const root = await storeRoot()
    const created = await putTemplateFile(root, input(), '2026-09-27T00:00:00.000Z')
    const archived = await setTemplateStatusFile(root, created.id, 'archived', '2026-09-27T02:00:00.000Z')
    expect(archived.status).toBe('archived')
    expect(archived.version).toBe(1)
    expect(await readTemplateHistory(root, created.id)).toHaveLength(1)
    const restored = await setTemplateStatusFile(root, created.id, 'active')
    expect(restored.status).toBe('active')
  })

  it('rejects unknown ids', async () => {
    const root = await storeRoot()
    await expect(setTemplateStatusFile(root, 'missing', 'archived')).rejects.toThrow(/unknown template/)
  })
})

describe('deleteTemplateFile', () => {
  it('cascades the history directory away', async () => {
    const root = await storeRoot()
    const created = await putTemplateFile(root, input(), '2026-09-27T00:00:00.000Z')
    await deleteTemplateFile(root, created.id)
    const library = await readTemplateLibrary(root)
    expect(library.templates).toHaveLength(0)
    await expect(readdir(join(root, HISTORY_DIRNAME, created.id))).rejects.toThrow()
  })

  it('ignores unknown ids', async () => {
    const root = await storeRoot()
    await deleteTemplateFile(root, 'missing')
    expect((await readTemplateLibrary(root)).templates).toHaveLength(0)
  })
})

describe('history', () => {
  it('trims to the newest snapshots at the cap', async () => {
    const root = await storeRoot()
    let record = await putTemplateFile(root, input(), '2026-09-27T00:00:00.000Z')
    for (let index = 2; index <= TEMPLATE_HISTORY_LIMIT + 3; index += 1) {
      record = await putTemplateFile(root, { ...input({ id: record.id, body: `v${String(index)}` }), changeNote: `第 ${String(index)} 版` })
    }
    const history = await readTemplateHistory(root, record.id)
    expect(history).toHaveLength(TEMPLATE_HISTORY_LIMIT)
    expect(history[0]?.version).toBe(TEMPLATE_HISTORY_LIMIT + 3)
    expect(history[0]?.changeNote).toContain('版')
  })

  it('skips malformed snapshot files on read', async () => {
    const root = await storeRoot()
    const created = await putTemplateFile(root, input())
    const historyDir = join(root, HISTORY_DIRNAME, created.id)
    await writeFile(join(historyDir, '999.json'), '{broken')
    const history = await readTemplateHistory(root, created.id)
    expect(history).toHaveLength(1)
  })
})

describe('putTemplateTagsFile', () => {
  it('stores tags and strips references to removed ones', async () => {
    const root = await storeRoot()
    const tags: TemplateTag[] = [
      tag('tag-1', '爆款'),
      tag('tag-2', '短视频'),
    ]
    const created = await putTemplateFile(root, input({ tagIds: [tagId('tag-1'), tagId('tag-2')] }))
    await putTemplateTagsFile(root, [tags[0] as TemplateTag])
    const library = await readTemplateLibrary(root)
    expect(library.tags).toEqual([{ id: tid('tag-1'), name: '爆款' }])
    expect(library.templates.find(record => record.id === created.id)?.tagIds).toEqual(['tag-1'])
  })

  it('rejects duplicate tag names', async () => {
    const root = await storeRoot()
    await expect(putTemplateTagsFile(root, [tag('a', '爆款'), tag('b', '爆款')])).rejects.toThrow(/duplicate tag name/)
  })

  it('round-trips through the taxonomy parser', async () => {
    const root = await storeRoot()
    await putTemplateTagsFile(root, [tag('tag-1', '爆款')])
    const parsed = parseTemplateTaxonomy(await readFile(join(root, TAXONOMY_FILENAME), 'utf8'))
    expect(parsed.kind).toBe('ok')
    if (parsed.kind === 'ok') expect(parsed.taxonomy.tags).toEqual([tag('tag-1', '爆款')])
  })
})

describe('exportTemplatePack', () => {
  it('exports the whole library when no ids are given', async () => {
    const root = await storeRoot()
    await putTemplateFile(root, input())
    await putTemplateFile(root, input({ name: '第二个模板' }))
    await putTemplateTagsFile(root, [tag('tag-1', '爆款')])
    const packDoc = await exportTemplatePack(root, [], '2026-09-27T00:00:00.000Z')
    expect(packDoc.format).toBe('dsh-template-pack')
    expect(packDoc.formatVersion).toBe(1)
    expect(packDoc.templates).toHaveLength(2)
    expect(packDoc.tags).toHaveLength(1)
  })

  it('exports only the selected ids', async () => {
    const root = await storeRoot()
    const first = await putTemplateFile(root, input())
    await putTemplateFile(root, input({ name: '第二个模板' }))
    const packDoc = await exportTemplatePack(root, [first.id], '2026-09-27T00:00:00.000Z')
    expect(packDoc.templates).toEqual([first])
  })
})

describe('importTemplatePack', () => {
  it('rejects an unknown pack envelope', async () => {
    const root = await storeRoot()
    await expect(importTemplatePack(root, pack({ format: 'other' as TemplatePack['format'] }), 'skip')).rejects.toThrow(/pack format/)
    await expect(importTemplatePack(root, pack({ formatVersion: 2 } as unknown as Partial<TemplatePack>), 'skip')).rejects.toThrow(/formatVersion/)
  })

  it('adds new entries, keeps their versions, and writes a snapshot', async () => {
    const root = await storeRoot()
    const summary = await importTemplatePack(root, pack({ templates: [packRecord()] }), 'skip')
    expect(summary).toEqual({ added: 1, skipped: 0, overwritten: 0, renamed: 0, failed: [] })
    const library = await readTemplateLibrary(root)
    expect(library.templates[0]?.version).toBe(3)
    expect(await readTemplateHistory(root, packRecord().id)).toHaveLength(1)
  })

  it('skips conflicting ids verbatim when the strategy is skip', async () => {
    const root = await storeRoot()
    const local = await putTemplateFile(root, input())
    const summary = await importTemplatePack(root, pack({ templates: [packRecord({ id: local.id, body: 'changed' })] }), 'skip')
    expect(summary.skipped).toBe(1)
    expect((await readTemplateLibrary(root)).templates[0]?.body).toBe(local.body)
  })

  it('overwrites conflicting ids with a new version and snapshot', async () => {
    const root = await storeRoot()
    const local = await putTemplateFile(root, input())
    const summary = await importTemplatePack(root, pack({ templates: [packRecord({ id: local.id, version: 3, body: '覆盖后的正文' })] }), 'overwrite')
    expect(summary.overwritten).toBe(1)
    const library = await readTemplateLibrary(root)
    expect(library.templates[0]?.version).toBe(4)
    expect(library.templates[0]?.body).toBe('覆盖后的正文')
    expect(await readTemplateHistory(root, local.id)).toHaveLength(2)
  })

  it('renames conflicting ids under a fresh id and suffixed name', async () => {
    const root = await storeRoot()
    const local = await putTemplateFile(root, input({ name: '导入模板' }))
    const summary = await importTemplatePack(root, pack({ templates: [packRecord({ id: local.id })] }), 'rename')
    expect(summary.renamed).toBe(1)
    const library = await readTemplateLibrary(root)
    expect(library.templates).toHaveLength(2)
    const names = library.templates.map(record => record.name).sort()
    expect(names).toEqual(['导入模板', '导入模板-2'])
    expect(library.templates.filter(record => record.id === local.id)).toHaveLength(1)
  })

  it('suffixes same-name entries that land under a different id', async () => {
    const root = await storeRoot()
    await putTemplateFile(root, input({ name: '重名模板' }))
    await importTemplatePack(root, pack({ templates: [packRecord({ name: '重名模板' })] }), 'skip')
    const names = (await readTemplateLibrary(root)).templates.map(record => record.name).sort()
    expect(names).toEqual(['重名模板', '重名模板-2'])
  })

  it('imports into a library whose directory does not exist yet (first-ever write)', async () => {
    const root = await storeRoot()
    const fresh = join(root, 'templates')
    const summary = await importTemplatePack(fresh, pack({ templates: [packRecord()] }), 'skip')
    expect(summary.added).toBe(1)
    expect((await readTemplateLibrary(fresh)).templates).toHaveLength(1)
  })

  it('names invalid entries in failed while the rest land', async () => {
    const root = await storeRoot()
    const summary = await importTemplatePack(root, pack({
      templates: [packRecord(), { id: 'broken' } as unknown as TemplateRecord],
      tags: [tag('tag-1', '爆款'), { id: tid('tag-2'), name: '' } as unknown as TemplateTag],
    }), 'skip')
    expect(summary.added).toBe(1)
    expect(summary.failed).toHaveLength(2)
    expect((await readTemplateLibrary(root)).tags).toEqual([tag('tag-1', '爆款')])
  })

  it('keeps local tag names when a pack tag id already exists', async () => {
    const root = await storeRoot()
    await putTemplateTagsFile(root, [tag('tag-1', '本地名')])
    await importTemplatePack(root, pack({ tags: [tag('tag-1', '包内名')] }), 'skip')
    expect((await readTemplateLibrary(root)).tags).toEqual([tag('tag-1', '本地名')])
  })
})
