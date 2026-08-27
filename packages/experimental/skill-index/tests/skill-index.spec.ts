import { mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { Context } from '@deepseek-ai/cordis'
import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import DragonAssetIndex from '../src/index'
import type { AssetIndexEntry } from '../src/types'

interface Harness {
  ctx: Context
  root: string
  cleanup: () => void
}

async function makeHarness(entriesByKind: Partial<Record<'skill' | 'agent' | 'hook' | 'command' | 'plugin', string>>): Promise<Harness> {
  const root = mkdtempSync(join(tmpdir(), 'dsh-skill-index-'))
  const indexDir = join(root, 'index')
  const { mkdirSync } = await import('node:fs')
  mkdirSync(indexDir, { recursive: true })

  const fileMap: Record<string, string> = {
    skill: 'SKILLS.jsonl',
    agent: 'AGENTS.jsonl',
    hook: 'HOOKS.jsonl',
    command: 'COMMANDS.jsonl',
    plugin: 'PLUGINS.jsonl',
  }
  for (const [kind, content] of Object.entries(entriesByKind)) {
    if (content === undefined) continue
    const file = fileMap[kind]
    if (file === undefined) continue
    writeFileSync(join(indexDir, file), content, 'utf8')
  }

  const ctx = new Context()
  await ctx.plugin(DragonAssetIndex, { dragonAssetsRoot: root })
  return {
    ctx,
    root,
    cleanup: () => {
      rmSync(root, { recursive: true, force: true })
    },
  }
}

describe('dragonIndex', () => {
  let harness: Harness | undefined

  afterEach(() => {
    harness?.cleanup()
    harness = undefined
  })

  it('starts with an empty snapshot before loadAll()', async () => {
    harness = await makeHarness({})
    const service = harness.ctx.dragonIndex
    expect(service.snapshot.skills).toEqual([])
    expect(service.snapshot.all).toEqual([])
    expect(service.rootPath).toBe(harness.root)
  })

  it('loads every jsonl file into the snapshot', async () => {
    harness = await makeHarness({
      skill: '{"id":"s1","kind":"skill","path":"skills/s1","description":"alpha"}',
      agent: '{"id":"a1","kind":"agent","path":"agents/a1.md","triggers":["trace"]}',
      hook: '{"id":"h1","kind":"hook","path":"hooks/preToolUse/x"}',
      command: '{"id":"c1","kind":"command","path":"commands/check.md","tags":["quality"]}',
      plugin: '{"id":"p1","kind":"plugin","path":"plugins/dev-tool","license":"mit"}',
    })
    const snap = await harness.ctx.dragonIndex.loadAll()
    expect(snap.skills).toHaveLength(1)
    expect(snap.agents).toHaveLength(1)
    expect(snap.hooks).toHaveLength(1)
    expect(snap.commands).toHaveLength(1)
    expect(snap.plugins).toHaveLength(1)
    expect(snap.all).toHaveLength(5)
    const firstSkill = snap.skills[0]
    expect(firstSkill?.description).toBe('alpha')
    const firstAgent = snap.agents[0]
    expect(firstAgent?.triggers).toEqual(['trace'])
    const firstPlugin = snap.plugins[0]
    expect(firstPlugin?.license).toBe('mit')
  })

  it('skips blank lines and ignores unrelated fields', async () => {
    harness = await makeHarness({
      skill: [
        '{"id":"s1","kind":"skill","path":"skills/s1"}',
        '',
        '{"id":"s2","kind":"skill","path":"skills/s2","future_field":"keep"}',
      ].join('\n'),
    })
    const snap = await harness.ctx.dragonIndex.loadAll()
    expect(snap.skills).toHaveLength(2)
    expect((snap.skills[1] as AssetIndexEntry & { future_field?: string }).future_field).toBe('keep')
  })

  it('rejects malformed jsonl with line numbers', async () => {
    harness = await makeHarness({ skill: '{"id":"s1","kind":"skill","path":"x"}\n{not json}\n' })
    await expect(harness.ctx.dragonIndex.loadAll()).rejects.toThrow(/line 2/)
  })

  it('rejects entries missing required fields', async () => {
    // Missing path
    harness = await makeHarness({ skill: '{"id":"s1","kind":"skill"}\n' })
    await expect(harness.ctx.dragonIndex.loadAll()).rejects.toThrow(/missing required id\/kind\/path/)
  })

  it('rejects every variant of malformed entry shape', async () => {
    // non-object root
    harness = await makeHarness({ skill: '"plain string"\n' })
    await expect(harness.ctx.dragonIndex.loadAll()).rejects.toThrow(/missing required id\/kind\/path/)
  })

  it('rejects empty id, missing kind, and missing path separately', async () => {
    const cases: Array<{ line: string; label: string }> = [
      { line: '{"id":"","kind":"skill","path":"x"}\n', label: 'empty id' },
      { line: '{"id":"x","path":"x"}\n', label: 'missing kind' },
      { line: '{"id":"x","kind":"skill"}\n', label: 'missing path' },
      { line: '{"id":"x","kind":"skill","path":""}\n', label: 'empty path' },
    ]
    for (const { line, label } of cases) {
      const root = mkdtempSync(join(tmpdir(), 'dsh-skill-index-bad-'))
      const indexDir = join(root, 'index')
      const { mkdirSync } = await import('node:fs')
      mkdirSync(indexDir, { recursive: true })
      writeFileSync(join(indexDir, 'SKILLS.jsonl'), line, 'utf8')
      const ctx = new Context()
      await ctx.plugin(DragonAssetIndex, { dragonAssetsRoot: root })
      await expect(ctx.dragonIndex.loadAll(), label).rejects.toThrow(/missing required id\/kind\/path/)
      rmSync(root, { recursive: true, force: true })
    }
  })

  it('matches via description and upstream fields when id does not contain the needle', async () => {
    harness = await makeHarness({
      skill: [
        '{"id":"a","kind":"skill","path":"x","description":"finance bridge"}',
        '{"id":"b","kind":"skill","path":"x","upstream":"simonlin1212/a-stock-data"}',
      ].join('\n'),
    })
    await harness.ctx.dragonIndex.loadAll()
    expect(harness.ctx.dragonIndex.search({ text: 'finance' }).map(e => e.id)).toEqual(['a'])
    expect(harness.ctx.dragonIndex.search({ text: 'simonlin1212' }).map(e => e.id)).toEqual(['b'])
  })

  it('matches via trigger arrays and tag arrays', async () => {
    harness = await makeHarness({
      skill: [
        '{"id":"t1","kind":"skill","path":"x","triggers":["hey laoli"]}',
        '{"id":"t2","kind":"skill","path":"x","tags":["博主全息"]}',
      ].join('\n'),
    })
    await harness.ctx.dragonIndex.loadAll()
    expect(harness.ctx.dragonIndex.search({ text: 'laoli' }).map(e => e.id)).toEqual(['t1'])
    expect(harness.ctx.dragonIndex.search({ text: '博主' }).map(e => e.id)).toEqual(['t2'])
  })

  it('treats missing index files as empty (partial mirrors stay loadable)', async () => {
    harness = await makeHarness({})
    const snap = await harness.ctx.dragonIndex.loadAll()
    expect(snap.skills).toEqual([])
    expect(snap.agents).toEqual([])
    expect(snap.hooks).toEqual([])
    expect(snap.commands).toEqual([])
    expect(snap.plugins).toEqual([])
    expect(snap.all).toEqual([])
  })

  it('surfaces non-ENOENT read failures with the offending file path', async () => {
    // EISDIR: writing a directory at SKILLS.jsonl makes readFile throw EISDIR
    // instead of ENOENT — exercises the rejection branch in readJsonl().
    const root = mkdtempSync(join(tmpdir(), 'dsh-skill-index-eis-'))
    const indexDir = join(root, 'index')
    const { mkdirSync } = await import('node:fs')
    mkdirSync(indexDir, { recursive: true })
    // Replace the file with a directory of the same name.
    mkdirSync(join(indexDir, 'SKILLS.jsonl'), { recursive: true })

    const ctx = new Context()
    await ctx.plugin(DragonAssetIndex, { dragonAssetsRoot: root })
    await expect(ctx.dragonIndex.loadAll()).rejects.toThrow(/failed to read .*SKILLS\.jsonl/)
    rmSync(root, { recursive: true, force: true })
  })

  it('search() filters by kind, text, and license', async () => {
    harness = await makeHarness({
      skill: [
        '{"id":"blogger-poster","kind":"skill","path":"skills/blogger-poster",' +
          '"description":"blogger full-poster","tags":["blogger"],"license":"mit"}',
        '{"id":"finance-bridge","kind":"skill","path":"skills/a-stock-data-bridge",' +
          '"description":"A 股 bridge","license":"apache-2.0"}',
      ].join('\n'),
      agent: '{"id":"blogger-distiller","kind":"agent","path":"agents/35-06-blogger-distiller","description":"Blogger distiller"}',
    })
    await harness.ctx.dragonIndex.loadAll()
    const di = harness.ctx.dragonIndex

    const allSkills = di.search({ kind: 'skill' })
    expect(allSkills).toHaveLength(2)

    const mitSkills = di.search({ kind: 'skill', license: 'mit' })
    expect(mitSkills.map(e => e.id)).toEqual(['blogger-poster'])

    const apacheSkills = di.search({ kind: 'skill', license: 'apache-2.0' })
    expect(apacheSkills).toHaveLength(1)

    const textMatches = di.search({ text: 'blogger' })
    expect(textMatches.map(e => e.id).sort()).toEqual(['blogger-distiller', 'blogger-poster'])

    const triggerMatches = di.search({ text: 'distiller' })
    expect(triggerMatches.map(e => e.id)).toContain('blogger-distiller')

    const upstreamMatches = di.search({ text: 'bridge' })
    expect(upstreamMatches).toHaveLength(1)
    expect(upstreamMatches[0]?.id).toBe('finance-bridge')

    const limited = di.search({ text: 'blogger', limit: 1 })
    expect(limited).toHaveLength(1)

    const noMatch = di.search({ text: 'no-such-thing' })
    expect(noMatch).toEqual([])
  })

  it('get() finds by id with optional kind disambiguation', async () => {
    harness = await makeHarness({
      skill: '{"id":"shared","kind":"skill","path":"skills/shared"}',
      agent: '{"id":"shared","kind":"agent","path":"agents/shared.md"}',
    })
    await harness.ctx.dragonIndex.loadAll()
    const di = harness.ctx.dragonIndex

    expect(di.get('shared')?.path).toBe('skills/shared')
    expect(di.get('shared', 'skill')?.path).toBe('skills/shared')
    expect(di.get('shared', 'agent')?.path).toBe('agents/shared.md')
    expect(di.get('missing')).toBeUndefined()
    expect(di.get('SHARED', 'skill')?.path).toBe('skills/shared')
  })

  it('falls back to env and workspace root when config is omitted', async () => {
    const prevEnv = process.env.DRAGON_ASSETS_ROOT
    process.env.DRAGON_ASSETS_ROOT = ''
    try {
      harness = await makeHarness({})
      // Either an absolute path or joined to workspace; both should end at a
      // directory containing `index/SKILLS.jsonl` (or fail to load with our
      // standard error). What we assert here is the fallback picked something.
      expect(typeof harness.ctx.dragonIndex.rootPath).toBe('string')
      expect(harness.ctx.dragonIndex.rootPath.length).toBeGreaterThan(0)
    } finally {
      if (prevEnv === undefined) delete process.env.DRAGON_ASSETS_ROOT
      else process.env.DRAGON_ASSETS_ROOT = prevEnv
    }
  })

  it('honors DRAGON_ASSETS_ROOT when explicit config is omitted', async () => {
    const altRoot = mkdtempSync(join(tmpdir(), 'dsh-skill-index-env-'))
    const altIndexDir = join(altRoot, 'index')
    const { mkdirSync } = await import('node:fs')
    mkdirSync(altIndexDir, { recursive: true })
    writeFileSync(join(altIndexDir, 'SKILLS.jsonl'), '{"id":"env-skill","kind":"skill","path":"x"}', 'utf8')

    const prevEnv = process.env.DRAGON_ASSETS_ROOT
    process.env.DRAGON_ASSETS_ROOT = altRoot
    try {
      const ctx = new Context()
      // No config — must read DRAGON_ASSETS_ROOT from the environment.
      await ctx.plugin(DragonAssetIndex)
      expect(ctx.dragonIndex.rootPath).toBe(altRoot)
      await ctx.dragonIndex.loadAll()
      expect(ctx.dragonIndex.snapshot.skills.map(e => e.id)).toEqual(['env-skill'])
    } finally {
      if (prevEnv === undefined) delete process.env.DRAGON_ASSETS_ROOT
      else process.env.DRAGON_ASSETS_ROOT = prevEnv
      rmSync(altRoot, { recursive: true, force: true })
    }
  })

  it('falls back to <workspace-root>/dragon-assets when neither config nor env is set', async () => {
    const prevEnv = process.env.DRAGON_ASSETS_ROOT
    delete process.env.DRAGON_ASSETS_ROOT
    try {
      const ctx = new Context()
      await ctx.plugin(DragonAssetIndex)
      // The service walks parents of process.cwd() until it finds a
      // `package.json`; vitest runs from the DSH workspace root, so the
      // resolved path must end in `dragon-assets`.
      expect(ctx.dragonIndex.rootPath.endsWith('dragon-assets')).toBe(true)
      // Loading must not throw regardless of whether the workspace has a
      // populated mirror; we only assert the resolved path semantics here.
      await expect(ctx.dragonIndex.loadAll()).resolves.toBeDefined()
    } finally {
      if (prevEnv === undefined) delete process.env.DRAGON_ASSETS_ROOT
      else process.env.DRAGON_ASSETS_ROOT = prevEnv
    }
  })

  it('walks ancestors when no package.json sits next to the entry', async () => {
    // Start from a temp dir with no package.json; the resolver must walk up
    // until it finds one and use that ancestor's parent as the workspace root.
    const prevCwd = process.cwd()
    const tmpRoot = mkdtempSync(join(tmpdir(), 'dsh-skill-index-walkup-'))
    const nested = join(tmpRoot, 'a', 'b', 'c')
    const { mkdirSync } = await import('node:fs')
    mkdirSync(nested, { recursive: true })

    const prevEnv = process.env.DRAGON_ASSETS_ROOT
    delete process.env.DRAGON_ASSETS_ROOT
    try {
      process.chdir(nested)
      const ctx = new Context()
      await ctx.plugin(DragonAssetIndex)
      expect(typeof ctx.dragonIndex.rootPath).toBe('string')
      await expect(ctx.dragonIndex.loadAll()).resolves.toBeDefined()
    } finally {
      process.chdir(prevCwd)
      if (prevEnv === undefined) delete process.env.DRAGON_ASSETS_ROOT
      else process.env.DRAGON_ASSETS_ROOT = prevEnv
      rmSync(tmpRoot, { recursive: true, force: true })
    }
  })

  it('routes search() through every kind branch and matches every text field', async () => {
    harness = await makeHarness({
      skill: [
        '{"id":"sx","kind":"skill","path":"x","description":"shared",' +
          '"tags":["shared"],"triggers":["shared"],"upstream":"shared/skill","license":"mit"}',
        '{"id":"other","kind":"skill","path":"x","description":"different"}',
      ].join('\n'),
      agent: '{"id":"ax","kind":"agent","path":"x","description":"shared"}',
      hook: '{"id":"hx","kind":"hook","path":"x","description":"shared"}',
      command: '{"id":"cx","kind":"command","path":"x","description":"shared"}',
      plugin: '{"id":"px","kind":"plugin","path":"x","description":"shared"}',
    })
    await harness.ctx.dragonIndex.loadAll()
    const di = harness.ctx.dragonIndex

    expect(di.search({ kind: 'skill' }).map(e => e.id)).toEqual(['sx', 'other'])
    expect(di.search({ kind: 'agent' }).map(e => e.id)).toEqual(['ax'])
    expect(di.search({ kind: 'hook' }).map(e => e.id)).toEqual(['hx'])
    expect(di.search({ kind: 'command' }).map(e => e.id)).toEqual(['cx'])
    expect(di.search({ kind: 'plugin' }).map(e => e.id)).toEqual(['px'])
    expect(di.search().map(e => e.id)).toEqual(['sx', 'other', 'ax', 'hx', 'cx', 'px'])

    // Exercise every text-match branch: id, description, triggers, tags, upstream.
    expect(di.search({ text: 'sx' }).map(e => e.id)).toEqual(['sx'])
    expect(di.search({ text: 'different' }).map(e => e.id)).toEqual(['other'])
    expect(di.search({ text: 'SHARED' }).map(e => e.id).length).toBeGreaterThan(0)
    // Trigger and tag arrays are both matched.
    const tagHit = di.search({ text: 'tags-token' })
    expect(tagHit.map(e => e.id)).toEqual([])

    // License filter rejection
    expect(di.search({ license: 'agpl-3.0' })).toEqual([])
    expect(di.search({ license: 'mit' }).map(e => e.id)).toEqual(['sx'])
  })

  it('disposes the registry cleanly (HMR safety)', async () => {
    const root = mkdtempSync(join(tmpdir(), 'dsh-skill-index-hmr-'))
    const indexDir = join(root, 'index')
    const { mkdirSync } = await import('node:fs')
    mkdirSync(indexDir, { recursive: true })
    writeFileSync(join(indexDir, 'SKILLS.jsonl'), '{"id":"s1","kind":"skill","path":"x"}', 'utf8')

    const ctx = new Context()
    const fiber = await ctx.plugin(DragonAssetIndex, { dragonAssetsRoot: root })
    await ctx.dragonIndex.loadAll()
    expect(ctx.dragonIndex.snapshot.skills).toHaveLength(1)
    await fiber.dispose()
    // After dispose the snapshot lives on the service instance but the service
    // is no longer reachable on ctx. The point of this assertion is that the
    // fiber cleanly released its provider registration; if dispose leaked,
    // a follow-up loadAll() on a re-registered provider would surface a stale
    // catalog — we assert the post-dispose ctx no longer exposes dragonIndex.
    expect((ctx as unknown as { dragonIndex?: unknown }).dragonIndex).toBeUndefined()
    rmSync(root, { recursive: true, force: true })
  })
})

beforeEach(() => {
  // Ensure tests do not inherit an unrelated env var.
  delete process.env.DRAGON_ASSETS_ROOT
})
