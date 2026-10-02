import { mkdtemp, readFile, rm, writeFile, mkdir } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { afterAll, describe, expect, it } from 'vitest'
import type { CreateManifest } from '../src/types.ts'
import {
  CREATE_MAX_STORED_VERSIONS, assertOutputMetadata, assertTemplateBody, collectCreateReferencedFiles,
  deleteCreateTemplateFile, listAssetFiles, parseCreateManifest, publishFinalFile,
  putCreateTemplateFile, readCreateMetadataFile, readCreateStateFile, readCreateTemplatesFile,
  registerCreatePublishFile, resolveThemeFilePath, writeCreateStateFile, writeOutputMetadataFile,
} from '../src/create/store.ts'
import { GATHER_QUOTA_PER_SOURCE, applyRetentionQuota, writeAssetFile, writeGatherManifestFile } from '../src/gather/store.ts'

const dirs: string[] = []

async function makeRoot(): Promise<string> {
  const dir = await mkdtemp(join(tmpdir(), 'dsh-create-store-'))
  dirs.push(dir)
  return dir
}

afterAll(async () => {
  await Promise.all(dirs.map(dir => rm(dir, { recursive: true, force: true })))
})

function manifest(overrides: Partial<CreateManifest> = {}): CreateManifest {
  return {
    formatVersion: 0,
    contentId: 'cc-test0001',
    contentType: 'gzh-article',
    currentVersion: 1,
    context: { audience: null, points: '要点', references: null },
    topicRef: null,
    sources: [],
    versions: [{
      v: 1, ts: '2026-09-25T00:00:00.000Z', trigger: 'ai-generate', words: 2, content: '正文', pinned: false, profileRef: null,
    }],
    ...overrides,
  }
}

const METADATA = {
  formatVersion: 0, title: '标题', kind: 'article', platform: null, status: 'draft', tags: [], summary: null,
}

describe('parseCreateManifest', () => {
  it('round-trips a valid manifest', () => {
    const raw = JSON.stringify(manifest())
    expect(parseCreateManifest(raw)).toEqual({ manifest: manifest(), problems: [] })
  })

  it('rejects whole on broken JSON, wrong versions, or an invalid entry', () => {
    expect(parseCreateManifest('{broken').problems).toEqual(['create manifest is not valid JSON'])
    expect(parseCreateManifest(JSON.stringify({ ...manifest(), formatVersion: 1 })).problems[0]).toContain('formatVersion')
    expect(parseCreateManifest(JSON.stringify({ ...manifest(), versions: 'no' })).problems[0]).toContain('versions array')
    expect(parseCreateManifest(JSON.stringify({ ...manifest(), currentVersion: -1 })).problems[0]).toContain('currentVersion')
    expect(parseCreateManifest(JSON.stringify({ ...manifest(), context: null })).problems[0]).toContain('context')
    const badVersion: unknown = { ...manifest(), versions: [{ ...manifest().versions[0]!, pinned: 'yes' }] }
    expect(parseCreateManifest(JSON.stringify(badVersion)).problems[0]).toContain('invalid create version')
    expect(parseCreateManifest(JSON.stringify({ ...manifest(), contentType: 'poem' })).problems[0]).toContain('contentType')
  })

  it('tolerates a missing evaluation, accepts a valid one, and rejects a malformed one', () => {
    expect(parseCreateManifest(JSON.stringify(manifest())).problems).toEqual([])
    const evaluation = {
      model: 'm', promptVersion: 1, evaluatedAt: 't', grade: '良',
      attraction: { grade: '良', reason: '依据' }, readability: { grade: '良', reason: '依据' },
      differentiation: { grade: '良', reason: '依据' }, audienceFit: { grade: '良', reason: '依据' },
    }
    const evaluated: unknown = {
      ...manifest(), versions: [{ ...manifest().versions[0]!, evaluation }],
    }
    expect(parseCreateManifest(JSON.stringify(evaluated)).problems).toEqual([])
    const broken: unknown = {
      ...manifest(), versions: [{ ...manifest().versions[0]!, evaluation: { ...evaluation, grade: '神' } }],
    }
    expect(parseCreateManifest(JSON.stringify(broken)).problems[0]).toContain('invalid create version')
  })
})

describe('create state read/write', () => {
  it('reads an absent theme as empty without problems', async () => {
    const root = await makeRoot()
    expect(await readCreateStateFile(root, '主题')).toEqual({ manifest: null, draft: null, problems: [] })
  })

  it('round-trips the manifest and the draft body, rejecting malformed manifests whole', async () => {
    const root = await makeRoot()
    await writeCreateStateFile(root, '主题', manifest())
    await writeAssetFile(root, { theme: '主题', file: 'cc-test0001.md', content: '当前稿' })
    const state = await readCreateStateFile(root, '主题')
    expect(state.manifest).toEqual(manifest())
    expect(state.draft).toBe('当前稿')

    await writeFile(join(root, '主题', 'assets', '_create.json'), '{broken', 'utf8')
    const broken = await readCreateStateFile(root, '主题')
    expect(broken.manifest).toBeNull()
    expect(broken.problems).toHaveLength(1)
  })

  it('rejects writes beyond the stored version cap and guards theme names', async () => {
    const root = await makeRoot()
    const versions = Array.from({ length: CREATE_MAX_STORED_VERSIONS + 1 }, (_, index) => ({
      v: index + 1, ts: 't', trigger: 'manual-save', words: 1, content: 'x', pinned: false, profileRef: null,
    }))
    await expect(writeCreateStateFile(root, '主题', manifest({ versions }))).rejects.toThrow('exceeds')
    await expect(readCreateStateFile(root, '../escape')).rejects.toThrow('invalid gather theme name')
  })
})

describe('publishFinalFile', () => {
  it('copies the deliverable to the theme root and rejects collisions unless overwriting', async () => {
    const root = await makeRoot()
    expect(await publishFinalFile(root, '主题', { file: '标题-cc000001.md', content: '定稿', overwrite: false })).toBe('标题-cc000001.md')
    await expect(publishFinalFile(root, '主题', { file: '标题-cc000001.md', content: '定稿2', overwrite: false })).rejects.toThrow('already exists')
    await publishFinalFile(root, '主题', { file: '标题-cc000001.md', content: '定稿2', overwrite: true })
    expect(await readFile(join(root, '主题', '标题-cc000001.md'), 'utf8')).toBe('定稿2')
  })

  it('guards deliverable names, theme names, and the size cap', async () => {
    const root = await makeRoot()
    await expect(publishFinalFile(root, '主题', { file: '../escape.md', content: 'x', overwrite: false })).rejects.toThrow('deliverable file name')
    await expect(publishFinalFile(root, '_system', { file: 'a.md', content: 'x', overwrite: false })).rejects.toThrow('theme name')
    await expect(publishFinalFile(root, '主题', { file: '.meta.md', content: 'x', overwrite: false })).rejects.toThrow('deliverable file name')
    await expect(publishFinalFile(root, '主题', { file: 'big.md', content: 'x'.repeat(400_001), overwrite: false })).rejects.toThrow('cap')
  })
})

describe('output metadata face', () => {
  it('round-trips metadata and keeps unknown fields', async () => {
    const root = await makeRoot()
    await writeOutputMetadataFile(root, '主题', { ...METADATA, futureField: { a: 1 } })
    const read = await readCreateMetadataFile(root, '主题')
    expect(read.metadata).toEqual({ ...METADATA, futureField: { a: 1 } })
    expect(read.problem).toBeNull()
  })

  it('rejects violations and reads absent as null without a problem', async () => {
    const root = await makeRoot()
    expect(await readCreateMetadataFile(root, '主题')).toEqual({ metadata: null, problem: null })
    await expect(writeOutputMetadataFile(root, '主题', { ...METADATA, title: '' })).rejects.toThrow('format-0 rules')
    await expect(writeOutputMetadataFile(root, '主题', { ...METADATA, status: 'weird' })).rejects.toThrow('format-0 rules')
    await expect(writeOutputMetadataFile(root, '主题', { ...METADATA, create: { currentVersion: 'x' } })).rejects.toThrow('create state')
  })
})

describe('registerCreatePublishFile', () => {
  it('mirrors the publish into metadata and tolerates the register retry', async () => {
    const root = await makeRoot()
    await writeOutputMetadataFile(root, '主题', METADATA)
    await publishFinalFile(root, '主题', { file: '标题-cc000001.md', content: '定稿', overwrite: false })
    await registerCreatePublishFile(root, '主题', { file: '标题-cc000001.md', version: 3 })
    const registered = await readCreateMetadataFile(root, '主题')
    expect(registered.metadata?.status).toBe('published')
    expect(registered.metadata?.create).toEqual({
      currentVersion: 3, publishedVersion: 3, publishedPath: '标题-cc000001.md', publishedAt: expect.any(String) as string,
      topicId: null,
    })
    await registerCreatePublishFile(root, '主题', { file: '标题-cc000001.md', version: 4 })
    expect((await readCreateMetadataFile(root, '主题')).metadata?.create?.publishedVersion).toBe(4)
  })

  it('mirrors the creation topicRef topicId into the publish metadata', async () => {
    const root = await makeRoot()
    await writeOutputMetadataFile(root, '主题', METADATA)
    await writeCreateStateFile(root, '主题', {
      formatVersion: 0,
      contentId: 'cc000001-0000-0000-0000-000000000000',
      contentType: 'xhs-note',
      currentVersion: 1,
      context: { audience: null, points: null, references: null },
      topicRef: { topicId: 'topic-9', title: '选题九', syncState: 'linked' },
      sources: [],
      versions: [],
    })
    await publishFinalFile(root, '主题', { file: '标题-cc000001.md', content: '定稿', overwrite: false })
    await registerCreatePublishFile(root, '主题', { file: '标题-cc000001.md', version: 1 })
    const registered = await readCreateMetadataFile(root, '主题')
    expect(registered.metadata?.create?.topicId).toBe('topic-9')
  })

  it('rejects a missing deliverable, missing metadata, and malformed metadata', async () => {
    const root = await makeRoot()
    await expect(registerCreatePublishFile(root, '主题', { file: 'a.md', version: 1 })).rejects.toThrow('publish before registering')
    await mkdir(join(root, '主题'), { recursive: true })
    await writeFile(join(root, '主题', 'a.md'), 'x', 'utf8')
    await expect(registerCreatePublishFile(root, '主题', { file: 'a.md', version: 1 })).rejects.toThrow('no output metadata')
    await writeOutputMetadataFile(root, '主题', METADATA)
    await expect(registerCreatePublishFile(root, '主题', { file: 'a.md', version: 1 })).resolves.toBeUndefined()
    await writeFile(join(root, '主题', '.dsh-output.json'), '{broken', 'utf8')
    await expect(registerCreatePublishFile(root, '主题', { file: 'a.md', version: 2 })).rejects.toThrow('format-0 rules')
  })
})

describe('listAssetFiles', () => {
  it('lists sorted plain assets and hides system files', async () => {
    const root = await makeRoot()
    await writeAssetFile(root, { theme: '主题', file: 'b.png', content: 'x' })
    await writeAssetFile(root, { theme: '主题', file: 'a.md', content: 'x' })
    await writeAssetFile(root, { theme: '主题', file: '_gather.json', content: '{}' })
    expect(await listAssetFiles(root, '主题')).toEqual(['a.md', 'b.png'])
  })
})

describe('create references and the gather retention exemption', () => {
  function gatherMaterial(bodyFile: string): object {
    return {
      id: `g-${bodyFile}`, sourceId: 's1', sourceName: '源一', title: bodyFile, url: '',
      gatheredAt: '2026-09-25T00:00:00.000Z', status: 'unread', bodyFile,
    }
  }

  it('collects the referenced asset files of the create manifest', async () => {
    const root = await makeRoot()
    expect(await collectCreateReferencedFiles(root, '主题')).toEqual(new Set())
    const referenced: unknown = {
      ...manifest(), sources: [{ kind: 'gather', refId: 'g-1', file: 'a.html', title: '素材', url: null, addedAt: 't' }],
    }
    await writeCreateStateFile(root, '主题', referenced as never)
    expect(await collectCreateReferencedFiles(root, '主题')).toEqual(new Set(['a.html']))
    await writeFile(join(root, '主题', 'assets', '_create.json'), '{broken', 'utf8')
    expect(await collectCreateReferencedFiles(root, '主题')).toEqual(new Set())
  })

  it('exempts the referenced snapshots from the retention trim', async () => {
    const stale = Array.from({ length: GATHER_QUOTA_PER_SOURCE + 1 }, (_, index) => gatherMaterial(`stale-${index}.html`))
    const materials = [gatherMaterial('referenced.html'), gatherMaterial('pinned favorite.html'), ...stale]
    ;(materials[1] as { status: string }).status = 'favorite'
    const { kept, dropped } = applyRetentionQuota(materials as never[], new Set(['referenced.html']))
    const keptFiles = kept.map(entry => (entry as { bodyFile: string }).bodyFile)
    expect(keptFiles).toContain('referenced.html')
    expect(keptFiles).toContain('pinned favorite.html')
    expect(dropped).toHaveLength(1)
  })

  it('exempts through the write path when the gateway collects the references', async () => {
    const root = await makeRoot()
    const referenced: unknown = {
      ...manifest(), sources: [{ kind: 'gather', refId: null, file: 'referenced.html', title: '素材', url: null, addedAt: 't' }],
    }
    await writeCreateStateFile(root, '主题', referenced as never)
    await writeAssetFile(root, { theme: '主题', file: 'referenced.html', content: '<p>正文</p>' })
    await writeAssetFile(root, { theme: '主题', file: 'stale.html', content: '<p>旧</p>' })
    const stale = Array.from({ length: GATHER_QUOTA_PER_SOURCE + 1 }, (_, index) => gatherMaterial(`stale-${index}.html`))
    const gatherManifest = {
      formatVersion: 0 as const,
      materials: [gatherMaterial('referenced.html'), ...stale] as never[],
    }
    const stored = await writeGatherManifestFile(root, '主题', gatherManifest, await collectCreateReferencedFiles(root, '主题'))
    expect(stored.materials.map(entry => entry.bodyFile)).toContain('referenced.html')
    expect(stored.materials).toHaveLength(GATHER_QUOTA_PER_SOURCE + 1)
    await rm(join(root, '主题', 'assets', 'referenced.html'), { force: true })
  })
})

describe('path guards', () => {
  it('resolveThemeFilePath rejects traversal and system names', () => {
    expect(() => resolveThemeFilePath('/r', '主题', '.dsh-output.json')).toThrow('deliverable file name')
    expect(() => resolveThemeFilePath('/r', '主题', 'a/b.md')).toThrow('deliverable file name')
    expect(() => resolveThemeFilePath('/r', '.', 'a.md')).toThrow('theme name')
    expect(resolveThemeFilePath('/r', '主题', 'a.md')).toContain(join('主题', 'a.md'))
  })
})

describe('assertOutputMetadata', () => {
  it('accepts a plain object record', () => {
    expect(() =>{  assertOutputMetadata(METADATA) }).not.toThrow()
  })
})

describe('custom template bank', () => {
  it('creates, bumps the revision on update, and deletes', async () => {
    const root = await makeRoot()
    const created = await putCreateTemplateFile(root, { title: '模板A', contentType: 'gzh-article', body: '写{{title}}' })
    expect(created).toHaveLength(1)
    expect(created[0]).toMatchObject({ title: '模板A', revision: 1 })
    const updated = await putCreateTemplateFile(root, { id: created[0]!.id, title: '模板A2', contentType: 'xhs-note', body: '写{{title}}和{{audience}}' })
    expect(updated[0]).toMatchObject({ title: '模板A2', revision: 2 })
    const afterDelete = await deleteCreateTemplateFile(root, created[0]!.id)
    expect(afterDelete).toHaveLength(0)
    expect(await deleteCreateTemplateFile(root, 'nope')).toHaveLength(0)
  })

  it('rejects empty titles, bad content types, and unknown placeholders', async () => {
    const root = await makeRoot()
    await expect(putCreateTemplateFile(root, { title: ' ', contentType: 'gzh-article', body: 'x' })).rejects.toThrow('non-empty title')
    await expect(putCreateTemplateFile(root, { title: 'T', contentType: 'poem' as never, body: 'x' })).rejects.toThrow('contentType')
    await expect(putCreateTemplateFile(root, { title: 'T', contentType: 'gzh-article', body: '写{{mystery}}' })).rejects.toThrow('unknown placeholder')
    await expect(putCreateTemplateFile(root, { title: 'T', contentType: 'gzh-article', body: '   ' })).rejects.toThrow('empty')
    expect(() => { assertTemplateBody('写{{title}} 和 {{ profile }}') }).not.toThrow()
  })

  it('reads an absent bank as empty and a malformed bank with problems', async () => {
    const root = await makeRoot()
    expect(await readCreateTemplatesFile(root)).toEqual({ templates: [], problems: [] })
    const { writeFile } = await import('node:fs/promises')
    await writeFile(join(root, '_templates.json'), '{broken', 'utf8')
    expect((await readCreateTemplatesFile(root)).problems[0]).toContain('not valid JSON')
    await writeFile(join(root, '_templates.json'), JSON.stringify({ formatVersion: 0, templates: [{ id: 'x' }] }), 'utf8')
    const { templates, problems } = await readCreateTemplatesFile(root)
    expect(templates).toHaveLength(0)
    expect(problems[0]).toContain('invalid create template')
  })
})
