import { mkdtemp, mkdir, readFile, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { afterEach, describe, expect, it } from 'vitest'
import type { PublishManifest, PublishTask } from '../src/publish/types.ts'
import {
  PUBLISH_DIRNAME, PUBLISH_MANIFEST_FILENAME, PUBLISH_PROFILES_FILENAME,
  assertPublishManifest, buildPublishPackageFile, isPlatformId, isTaskId,
  readPublishDerivedFile, readPublishIndexFile, readPublishManifestFile, readPublishProfilesFile,
  readPublishSourceFile, writePublishDerivedFile, writePublishManifestFile, writePublishProfilesFile,
} from '../src/publish/store.ts'
import { adaptFramedPrompt, adaptSystemPrompt, parsePublishAdaptOutput } from '../src/publish/ai.ts'

let root: string | undefined

afterEach(async () => {
  if (root !== undefined) await rm(root, { recursive: true, force: true })
  root = undefined
})

async function library(): Promise<string> {
  root = await mkdtemp(join(tmpdir(), 'publish-store-'))
  return root
}

const UUID = '0f0a7b1e-5c2d-4e8f-9a3b-6d1c2e4f5a6b'
const OTHER_UUID = '1f0a7b1e-5c2d-4e8f-9a3b-6d1c2e4f5a6c'

/** One valid stored task, overridden per test. */
function task(overrides: Partial<PublishTask> = {}): PublishTask {
  return {
    taskId: UUID,
    title: '杭州咖啡地图',
    manuscriptFile: 'hangzhou-coffee-a1b2c3d4.md',
    manuscriptId: 'a1b2c3d4-0000-0000-0000-000000000000',
    topicId: null,
    personaDigest: null,
    mode: 'immediate',
    scheduledAt: null,
    scheduleItemId: null,
    status: 'pendingReview',
    note: null,
    platforms: [{
      platformId: 'xhs',
      accountAlias: '老李探店',
      contentFile: 'xhs.md',
      coverPrompt: null,
      tags: ['咖啡'],
      status: 'pending',
      attempts: [],
    }],
    createdAt: '2026-09-27T00:00:00.000Z',
    updatedAt: '2026-09-27T00:00:00.000Z',
    ...overrides,
  }
}

/** Persist a manifest directly, bypassing the write face when needed. */
async function seedManifest(theme: string, tasks: PublishTask[]): Promise<void> {
  const assets = join(root!, theme, 'assets')
  await mkdir(assets, { recursive: true })
  await writeFile(join(assets, PUBLISH_MANIFEST_FILENAME), `${JSON.stringify({ formatVersion: 0, tasks }, null, 2)}\n`)
}

describe('publish task and platform id guards', () => {
  it('accepts UUID task ids and lowercase platform ids, rejects path escape', () => {
    expect(isTaskId(UUID)).toBe(true)
    expect(isTaskId('../escape')).toBe(false)
    expect(isPlatformId('xhs')).toBe(true)
    expect(isPlatformId('XHS')).toBe(false)
    expect(isPlatformId('../x')).toBe(false)
  })
})

describe('publish manifest store', () => {
  it('reads an absent manifest as null with no problems', async () => {
    await library()
    const read = await readPublishManifestFile(root!, 'theme-a')
    expect(read.manifest).toBeNull()
    expect(read.problems).toEqual([])
  })

  it('drops malformed tasks into problems instead of hiding them', async () => {
    await library()
    await seedManifest('theme-a', [task()])
    const file = join(root!, 'theme-a', 'assets', PUBLISH_MANIFEST_FILENAME)
    const stored = JSON.parse(await readFile(file, 'utf8')) as { tasks: unknown[] }
    stored.tasks.push({ taskId: 'garbage' })
    await writeFile(file, JSON.stringify(stored))
    const read = await readPublishManifestFile(root!, 'theme-a')
    expect(read.manifest?.tasks).toHaveLength(1)
    expect(read.problems).toHaveLength(1)
  })

  it('rejects an unknown formatVersion on read and on write', async () => {
    await library()
    const assets = join(root!, 'theme-a', 'assets')
    await mkdir(assets, { recursive: true })
    await writeFile(join(assets, PUBLISH_MANIFEST_FILENAME), JSON.stringify({ formatVersion: 1, tasks: [] }))
    const read = await readPublishManifestFile(root!, 'theme-a')
    expect(read.manifest?.tasks).toEqual([])
    expect(read.problems[0]).toContain('formatVersion')
    expect(() =>{  assertPublishManifest({ formatVersion: 1, tasks: [] } as unknown as PublishManifest) }).toThrow(/formatVersion/)
  })

  it('write rejects a malformed task loud instead of storing it', async () => {
    await library()
    await seedManifest('theme-a', [])
    await expect(writePublishManifestFile(root!, 'theme-a', { formatVersion: 0, tasks: [task({ title: '' })] }))
      .rejects.toThrow(/malformed/)
  })

  it('writePublishManifest refreshes the theme rows of the global index', async () => {
    await library()
    await seedManifest('theme-a', [])
    await writePublishManifestFile(root!, 'theme-a', { formatVersion: 0, tasks: [task()] })
    await writePublishManifestFile(root!, 'theme-b', { formatVersion: 0, tasks: [task({ taskId: OTHER_UUID, title: '另一主题' })] })
    const { index } = await readPublishIndexFile(root!)
    expect(index.entries.map(entry => entry.taskId).sort()).toEqual([OTHER_UUID, UUID].sort())
    // Rewriting theme-a drops none of theme-b's rows.
    await writePublishManifestFile(root!, 'theme-a', { formatVersion: 0, tasks: [] })
    const { index: after } = await readPublishIndexFile(root!)
    expect(after.entries.map(entry => entry.theme)).toEqual(['theme-b'])
  })
})

describe('derived drafts', () => {
  it('writes and reads back inside assets/publish/<taskId>/', async () => {
    await library()
    const { file } = await writePublishDerivedFile(root!, 'theme-a', UUID, 'xhs', '# 标题\n正文')
    expect(file).toBe(join(PUBLISH_DIRNAME, UUID, 'xhs.md'))
    expect(await readPublishDerivedFile(root!, 'theme-a', UUID, 'xhs')).toBe('# 标题\n正文')
    expect(await readPublishDerivedFile(root!, 'theme-a', UUID, 'weibo')).toBeUndefined()
  })

  it('rejects task and platform ids that would escape the directory', async () => {
    await library()
    await expect(writePublishDerivedFile(root!, 'theme-a', '../escape', 'xhs', 'x')).rejects.toThrow(/task id/)
    await expect(writePublishDerivedFile(root!, 'theme-a', UUID, '../escape', 'x')).rejects.toThrow(/platform id/)
  })
})

describe('publish source reads', () => {
  it('reads a theme-root deliverable and refuses metadata and paths', async () => {
    await library()
    await mkdir(join(root!, 'theme-a'), { recursive: true })
    await writeFile(join(root!, 'theme-a', 'final.md'), '定稿正文')
    expect(await readPublishSourceFile(root!, 'theme-a', 'final.md')).toBe('定稿正文')
    await expect(readPublishSourceFile(root!, 'theme-a', '.dsh-output.json')).rejects.toThrow(/manuscript file/)
    await expect(readPublishSourceFile(root!, 'theme-a', '../other.md')).rejects.toThrow(/manuscript file/)
    await expect(readPublishSourceFile(root!, 'theme-a', '_schedule.json')).rejects.toThrow(/manuscript file/)
  })
})

describe('publish profiles store', () => {
  it('round-trips the account cards and drops malformed rows by name', async () => {
    await library()
    await writePublishProfilesFile(root!, [{ platformId: 'xhs', alias: '老李探店', enabled: true, adaptationOverrides: null }])
    const read = await readPublishProfilesFile(root!)
    expect(read.profiles).toHaveLength(1)
    expect(read.problems).toEqual([])
    const file = join(root!, PUBLISH_PROFILES_FILENAME)
    const stored = JSON.parse(await readFile(file, 'utf8')) as { profiles: unknown[] }
    stored.profiles.push({ platformId: 'BAD', alias: '', enabled: true })
    await writeFile(file, JSON.stringify(stored))
    const broken = await readPublishProfilesFile(root!)
    expect(broken.profiles).toHaveLength(1)
    expect(broken.problems).toHaveLength(1)
  })

  it('rejects writes with an empty alias', async () => {
    await library()
    await expect(writePublishProfilesFile(root!, [{ platformId: 'xhs', alias: ' ', enabled: true, adaptationOverrides: null }]))
      .rejects.toThrow(/alias/)
  })
})

describe('buildPublishPackageFile', () => {
  it('assembles every leg from disk and refuses an incomplete task', async () => {
    await library()
    await seedManifest('theme-a', [task({
      status: 'recorded',
      platforms: [
        task().platforms[0]!,
        { platformId: 'weibo', accountAlias: '微博号', contentFile: 'weibo.md', coverPrompt: null, tags: [], status: 'adapted', attempts: [] },
      ],
    })])
    await writePublishDerivedFile(root!, 'theme-a', UUID, 'xhs', '小红书版')
    await expect(buildPublishPackageFile(root!, 'theme-a', UUID)).rejects.toThrow(/no derived draft/)
    await writePublishDerivedFile(root!, 'theme-a', UUID, 'weibo', '微博版')
    const pkg = await buildPublishPackageFile(root!, 'theme-a', UUID)
    expect(pkg.theme).toBe('theme-a')
    expect(pkg.platforms).toHaveLength(2)
    expect(pkg.platforms.map(platform => platform.platformId).sort()).toEqual(['weibo', 'xhs'])
    expect(pkg.generatedAt.length).toBeGreaterThan(0)
  })

  it('rejects an unknown task', async () => {
    await library()
    await seedManifest('theme-a', [])
    await expect(buildPublishPackageFile(root!, 'theme-a', UUID)).rejects.toThrow(/does not exist/)
  })
})

describe('publish AI prompt and parser', () => {
  const request = {
    platformId: 'xhs',
    platformName: '小红书',
    styleHints: '短句为主',
    charLimit: 1000,
    title: '杭州咖啡地图',
    sourceText: '正文',
    personaDigest: null,
  }

  it('frames the platform rules, the char cap, and the JSON contract', () => {
    const system = adaptSystemPrompt(request)
    expect(system).toContain('小红书')
    expect(system).toContain('1000')
    expect(system).toContain('"content"')
    const framed = adaptFramedPrompt(request, 10_000)
    expect(framed).toContain('杭州咖啡地图')
    expect(framed).toContain('正文')
  })

  it('states no cap when the platform is unlimited and folds the persona', () => {
    const system = adaptSystemPrompt({ ...request, charLimit: null, personaDigest: '老李人设' })
    expect(system).toContain('没有硬性字数上限')
    expect(system).toContain('老李人设')
  })

  it('parses a fenced JSON answer, trims tags, caps them at 8', () => {
    const tags = Array.from({ length: 12 }, (_, index) => `tag${index}`)
    const result = parsePublishAdaptOutput('```json\n{"content":"改写","coverPrompt":"  ","tags":' + JSON.stringify(tags) + '}\n```', 'deepseek-chat')
    expect(result.content).toBe('改写')
    expect(result.coverPrompt).toBeNull()
    expect(result.tags).toHaveLength(8)
    expect(result.model).toBe('deepseek-chat')
    expect(result.promptVersion).toBeGreaterThan(0)
  })

  it('rejects answers without content or without JSON', () => {
    expect(() => parsePublishAdaptOutput('{"tags":[]}', 'm')).toThrow(/no content/)
    expect(() => parsePublishAdaptOutput('没有 JSON', 'm')).toThrow(/no JSON object/)
    expect(() => parsePublishAdaptOutput('{"content":42}', 'm')).toThrow(/no content/)
  })
})
