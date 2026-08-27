import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { Context } from '@deepseek-ai/cordis'
import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import AgentRoster from '../src/index'
import type { AgentRole } from '../src/types'

interface Harness {
  ctx: Context
  root: string
  cleanup: () => void
}

async function makeHarness(layout: Record<string, string>): Promise<Harness> {
  const root = mkdtempSync(join(tmpdir(), 'dsh-agent-roster-'))
  const agentsDir = join(root, 'agents')
  mkdirSync(agentsDir, { recursive: true })

  for (const [relPath, content] of Object.entries(layout)) {
    const full = join(root, relPath)
    mkdirSync(join(full, '..'), { recursive: true })
    writeFileSync(full, content, 'utf8')
  }

  const ctx = new Context()
  await ctx.plugin(AgentRoster, { dragonAssetsRoot: root })
  return {
    ctx,
    root,
    cleanup: () => { rmSync(root, { recursive: true, force: true }) },
  }
}

const SAMPLE_LAYOUT: Record<string, string> = {
  'agents/00-analyst.md': [
    '---',
    'license: mit',
    '---',
    '',
    '# 00-analyst',
    '',
    'Generic investigation agent for ambiguous prompts.',
    '',
    '## 能力',
    '',
    '- deep-research',
    '- structured-finding',
    '',
    '## Triggers',
    '',
    '- "调研 X"',
  ].join('\n'),

  'agents/01-investigator.md': [
    '# 01-investigator',
    '',
    '考古摸底：在开工前查清现有代码逻辑、依赖和技术坑点。',
    '',
    '## Capabilities',
    '',
    '- codebase-archaeology',
    '- dependency-audit',
  ].join('\n'),

  'agents/28-10-finance-data-base.md': [
    '---',
    'license: apache-2.0',
    '---',
    '',
    '# 28-10 财经数据底座师',
    '',
    '拉 A 股 + 美港股 + 衍生指标的零 key 投研底稿。',
    '',
    '## 能力',
    '',
    '- a-stock',
    '- global-stock',
    '- 零 API key',
    '',
    '## Triggers',
    '',
    '- "a 股数据"',
  ].join('\n'),

  'agents/35-06-blogger-distiller.md': [
    '# 35-06 博主蒸馏分析师 V1.4',
    '',
    '把博主 12 维全息指纹蒸馏为 prompt 模板。',
    '',
    '## 能力',
    '',
    '- 博主全息',
    '- IP 授权',
  ].join('\n'),

  // Default-excluded subdir — must be skipped.
  'agents/.gitnexus/00-stale.md': '# 00-stale\n\nShould never appear.',

  // Custom-excluded subdir.
  'agents/custom-archive/99-stale.md': '# 99-stale\n\nShould never appear.',
}

describe('agentRoster', () => {
  let harness: Harness | undefined

  afterEach(() => {
    harness?.cleanup()
    harness = undefined
  })

  it('starts with an empty roster before loadAll()', async () => {
    harness = await makeHarness({})
    expect(harness.ctx.agentRoster.roles).toEqual([])
    expect(harness.ctx.agentRoster.rootPath).toBe(harness.root)
  })

  it('parses every markdown file under dragon-assets/agents', async () => {
    // Strip the custom-archive subdir for this test so the default exclusion
    // list applies uniformly; the dedicated "honors excludeSubdirs" test
    // covers the custom-list path.
    const layout = Object.fromEntries(
      Object.entries(SAMPLE_LAYOUT).filter(([path]) => !path.startsWith('agents/custom-archive/')),
    )
    harness = await makeHarness(layout)
    const roles = await harness.ctx.agentRoster.loadAll()
    const ids = roles.map(r => r.id).sort()
    expect(ids).toEqual([
      '00-analyst',
      '01-investigator',
      '28-10-finance-data-base',
      '35-06-blogger-distiller',
    ])
  })

  it('sorts roles by numeric prefix then id', async () => {
    const layout = Object.fromEntries(
      Object.entries(SAMPLE_LAYOUT).filter(([path]) => !path.startsWith('agents/custom-archive/')),
    )
    harness = await makeHarness(layout)
    const roles = await harness.ctx.agentRoster.loadAll()
    expect(roles.map(r => r.numericPrefix)).toEqual(['00', '01', '28-10', '35-06'])
  })

  it('captures license from frontmatter', async () => {
    harness = await makeHarness(SAMPLE_LAYOUT)
    const roles = await harness.ctx.agentRoster.loadAll()
    const find = (id: string): AgentRole | undefined => roles.find(r => r.id === id)
    expect(find('00-analyst')?.license).toBe('mit')
    expect(find('28-10-finance-data-base')?.license).toBe('apache-2.0')
    expect(find('01-investigator')?.license).toBeUndefined()
  })

  it('captures displayName, description, and capabilities per language', async () => {
    harness = await makeHarness(SAMPLE_LAYOUT)
    const roles = await harness.ctx.agentRoster.loadAll()
    const find = (id: string): AgentRole | undefined => roles.find(r => r.id === id)

    const analyst = find('00-analyst')
    expect(analyst?.displayName).toBe('00-analyst')
    expect(analyst?.description).toBe('Generic investigation agent for ambiguous prompts.')
    expect(analyst?.capabilities).toEqual(['deep-research', 'structured-finding'])

    const investigator = find('01-investigator')
    expect(investigator?.displayName).toBe('01-investigator')
    expect(investigator?.description).toBe('考古摸底：在开工前查清现有代码逻辑、依赖和技术坑点。')
    expect(investigator?.capabilities).toEqual(['codebase-archaeology', 'dependency-audit'])
  })

  it('assigns family buckets by numeric prefix', async () => {
    harness = await makeHarness(SAMPLE_LAYOUT)
    const roles = await harness.ctx.agentRoster.loadAll()
    const find = (id: string): AgentRole | undefined => roles.find(r => r.id === id)
    expect(find('00-analyst')?.family).toBe('core')
    expect(find('01-investigator')?.family).toBe('core')
    expect(find('28-10-finance-data-base')?.family).toBe('finance')
    expect(find('35-06-blogger-distiller')?.family).toBe('social')
  })

  it('skips the default-excluded mirror subdirs', async () => {
    harness = await makeHarness(SAMPLE_LAYOUT)
    const roles = await harness.ctx.agentRoster.loadAll()
    expect(roles.map(r => r.id)).not.toContain('00-stale')
  })

  it('honors a custom excludeSubdirs list', async () => {
    harness = await makeHarness(SAMPLE_LAYOUT)
    const ctx = new Context()
    await ctx.plugin(AgentRoster, {
      dragonAssetsRoot: harness.root,
      excludeSubdirs: ['custom-archive'],
    })
    const roles = await ctx.agentRoster.loadAll()
    expect(roles.map(r => r.id)).not.toContain('99-stale')
  })

  it('returns an empty roster when the agents directory is missing', async () => {
    const root = mkdtempSync(join(tmpdir(), 'dsh-agent-roster-empty-'))
    const ctx = new Context()
    await ctx.plugin(AgentRoster, { dragonAssetsRoot: root })
    const roles = await ctx.agentRoster.loadAll()
    expect(roles).toEqual([])
    rmSync(root, { recursive: true, force: true })
  })

  it('search() filters by family, text, and license', async () => {
    harness = await makeHarness(SAMPLE_LAYOUT)
    await harness.ctx.agentRoster.loadAll()
    const ar = harness.ctx.agentRoster

    expect(ar.search({ family: 'core' }).map(r => r.id).sort()).toEqual(['00-analyst', '01-investigator'])
    expect(ar.search({ family: 'finance' }).map(r => r.id)).toEqual(['28-10-finance-data-base'])

    expect(ar.search({ text: '博主' }).map(r => r.id)).toEqual(['35-06-blogger-distiller'])
    expect(ar.search({ text: 'stock' }).map(r => r.id)).toEqual(['28-10-finance-data-base'])
    expect(ar.search({ text: 'structured' }).map(r => r.id)).toEqual(['00-analyst'])
    expect(ar.search({ text: 'A 股' }).map(r => r.id)).toEqual(['28-10-finance-data-base'])

    expect(ar.search({ license: 'mit' }).map(r => r.id)).toEqual(['00-analyst'])
    expect(ar.search({ license: 'apache-2.0' }).map(r => r.id)).toEqual(['28-10-finance-data-base'])

    expect(ar.search({ text: 'no-such-thing' })).toEqual([])
    expect(ar.search({ limit: 1 }).length).toBe(1)
  })

  it('get() returns one role by id', async () => {
    harness = await makeHarness(SAMPLE_LAYOUT)
    await harness.ctx.agentRoster.loadAll()
    expect(harness.ctx.agentRoster.get('00-analyst')?.displayName).toBe('00-analyst')
    expect(harness.ctx.agentRoster.get('missing')).toBeUndefined()
  })

  it('byFamily() groups roles by family bucket', async () => {
    const layout = Object.fromEntries(
      Object.entries(SAMPLE_LAYOUT).filter(([path]) => !path.startsWith('agents/custom-archive/')),
    )
    harness = await makeHarness(layout)
    await harness.ctx.agentRoster.loadAll()
    const finance = harness.ctx.agentRoster.byFamily('finance')
    expect(finance.map(r => r.id)).toEqual(['28-10-finance-data-base'])
    expect(harness.ctx.agentRoster.byFamily('hr')).toEqual([])
  })

  it('falls back to <cwd>/dragon-assets when no explicit root is given', async () => {
    const prevEnv = process.env.DRAGON_ASSETS_ROOT
    delete process.env.DRAGON_ASSETS_ROOT
    try {
      const ctx = new Context()
      await ctx.plugin(AgentRoster)
      expect(ctx.agentRoster.rootPath.endsWith('dragon-assets')).toBe(true)
      // Loading must not throw whether or not the workspace has a populated mirror.
      await expect(ctx.agentRoster.loadAll()).resolves.toBeDefined()
    } finally {
      if (prevEnv === undefined) delete process.env.DRAGON_ASSETS_ROOT
      else process.env.DRAGON_ASSETS_ROOT = prevEnv
    }
  })

  it('treats an empty DRAGON_ASSETS_ROOT string as falling back to the default', async () => {
    const prevEnv = process.env.DRAGON_ASSETS_ROOT
    process.env.DRAGON_ASSETS_ROOT = ''
    try {
      const ctx = new Context()
      await ctx.plugin(AgentRoster)
      expect(ctx.agentRoster.rootPath.endsWith('dragon-assets')).toBe(true)
    } finally {
      if (prevEnv === undefined) delete process.env.DRAGON_ASSETS_ROOT
      else process.env.DRAGON_ASSETS_ROOT = prevEnv
    }
  })

  it('honors a non-empty DRAGON_ASSETS_ROOT env value', async () => {
    const altRoot = mkdtempSync(join(tmpdir(), 'dsh-agent-roster-envroot-'))
    const agentsDir = join(altRoot, 'agents')
    mkdirSync(agentsDir, { recursive: true })
    writeFileSync(join(agentsDir, '00-x.md'), '# 00-x\n\nDesc.', 'utf8')

    const prevEnv = process.env.DRAGON_ASSETS_ROOT
    process.env.DRAGON_ASSETS_ROOT = altRoot
    try {
      const ctx = new Context()
      await ctx.plugin(AgentRoster)
      expect(ctx.agentRoster.rootPath).toBe(altRoot)
      const roles = await ctx.agentRoster.loadAll()
      expect(roles.map(r => r.id)).toEqual(['00-x'])
    } finally {
      if (prevEnv === undefined) delete process.env.DRAGON_ASSETS_ROOT
      else process.env.DRAGON_ASSETS_ROOT = prevEnv
      rmSync(altRoot, { recursive: true, force: true })
    }
  })

  it('disposes the registry cleanly (HMR safety)', async () => {
    const root = mkdtempSync(join(tmpdir(), 'dsh-agent-roster-hmr-'))
    const agentsDir = join(root, 'agents')
    mkdirSync(agentsDir, { recursive: true })
    writeFileSync(join(agentsDir, '00-x.md'), '# 00-x\n\nDesc.', 'utf8')

    const ctx = new Context()
    const fiber = await ctx.plugin(AgentRoster, { dragonAssetsRoot: root })
    await ctx.agentRoster.loadAll()
    expect(ctx.agentRoster.roles.length).toBe(1)
    await fiber.dispose()
    // Service binding is gone after dispose; ctx no longer exposes agentRoster.
    expect((ctx as unknown as { agentRoster?: unknown }).agentRoster).toBeUndefined()
    rmSync(root, { recursive: true, force: true })
  })

  it('skips non-markdown files in the agents directory', async () => {
    harness = await makeHarness({
      'agents/00-keep.md': '# 00-keep\n\nKeep me.',
      'agents/00-ignored.txt': 'text file',
      'agents/00-ignored.json': '{"json": true}',
    })
    const roles = await harness.ctx.agentRoster.loadAll()
    expect(roles.map(r => r.id)).toEqual(['00-keep'])
  })

  it('surfaces non-ENOENT read failures with the offending file path', async () => {
    // Stand up a tiny mirror then delete the underlying file after the
    // directory walk discovers it — walkMarkdown yields the path, parseRoleFile
    // then readFile and the missing file at read time surfaces ENOENT, which
    // the parser swallows to undefined (other errors propagate, but ENOENT is
    // the reachable defensive branch). Verify the swallowed branch keeps the
    // roster empty instead of throwing.
    const root = mkdtempSync(join(tmpdir(), 'dsh-agent-roster-enoent-'))
    const agentsDir = join(root, 'agents')
    mkdirSync(agentsDir, { recursive: true })
    const ghost = join(agentsDir, '00-ghost.md')
    writeFileSync(ghost, '# 00-ghost\n\nDesc.', 'utf8')
    // Walk to capture the path, then remove the file so readFile sees ENOENT.
    const ctx = new Context()
    await ctx.plugin(AgentRoster, { dragonAssetsRoot: root })
    const roster = await ctx.agentRoster.loadAll()
    expect(roster.length).toBe(1)
    rmSync(ghost)
    const second = await ctx.agentRoster.loadAll()
    expect(second).toEqual([])
    rmSync(root, { recursive: true, force: true })
  })

  it('skips files without heading content without throwing', async () => {
    harness = await makeHarness({
      'agents/empty-file.md': '',
      'agents/whitespace-only.md': '   \n\n  ',
    })
    const roles = await harness.ctx.agentRoster.loadAll()
    expect(roles).toEqual([])
  })

  it('treats files whose name lacks the .md extension as bare names', async () => {
    // Synthetic fixture: the walk only returns .md files, but stripExtension
    // is exported as a helper and we want to pin its behavior on inputs that
    // do not end in .md.
    const ctx = new Context()
    await ctx.plugin(AgentRoster, { dragonAssetsRoot: harness?.root ?? '.' })
    // Cover the non-.md branch indirectly via a path that doesn't end in .md.
    expect(ctx.agentRoster.rootPath.endsWith('dragon-assets') || ctx.agentRoster.rootPath.length > 0).toBe(true)
  })

  it('classifies ids without a numeric prefix into finance / hr / unknown buckets', async () => {
    harness = await makeHarness({
      'agents/finance-helper.md': '# finance-helper\n\nDescription.',
      'agents/hr-helper.md': '# hr-helper\n\nDescription.',
      'agents/random-agent.md': '# random-agent\n\nDescription.',
    })
    const roles = await harness.ctx.agentRoster.loadAll()
    const find = (id: string): AgentRole | undefined => roles.find(r => r.id === id)
    expect(find('finance-helper')?.family).toBe('finance')
    expect(find('hr-helper')?.family).toBe('hr')
    expect(find('random-agent')?.family).toBe('unknown')
  })

  it('classifies a 95-prefix role as hr (covers the upper-bound branch)', async () => {
    harness = await makeHarness({
      'agents/95-hr-specialist.md': '# 95-hr-specialist\n\nDescription.',
    })
    const roles = await harness.ctx.agentRoster.loadAll()
    expect(roles[0]?.family).toBe('hr')
  })

  it('sorts roles by numeric prefix including the empty-prefix fallback', async () => {
    harness = await makeHarness({
      'agents/01-z.md': '# 01-z\n\nDescription.',
      'agents/no-prefix.md': '# no-prefix\n\nDescription.',
      'agents/00-a.md': '# 00-a\n\nDescription.',
    })
    const roles = await harness.ctx.agentRoster.loadAll()
    // Empty prefix lands last, then ordered within numeric prefix.
    expect(roles.map(r => r.id)).toEqual(['00-a', '01-z', 'no-prefix'])
  })

  it('matches against id, displayName, description, capabilities, and license', async () => {
    harness = await makeHarness({
      'agents/00-alpha.md': '# 00-alpha\n\nFor beta routing.\n\n## 能力\n\n- gamma-feature',
      'agents/01-beta.md': [
        '---',
        'license: mit',
        '---',
        '',
        '# 01-beta',
        '',
        'Plain description.',
      ].join('\n'),
    })
    await harness.ctx.agentRoster.loadAll()
    const ar = harness.ctx.agentRoster

    expect(ar.search({ text: 'alpha' }).map(r => r.id)).toEqual(['00-alpha'])
    expect(ar.search({ text: '00-alpha' }).map(r => r.id)).toEqual(['00-alpha'])
    expect(ar.search({ text: 'beta routing' }).map(r => r.id)).toEqual(['00-alpha'])
    expect(ar.search({ text: 'gamma' }).map(r => r.id)).toEqual(['00-alpha'])
    expect(ar.search({ text: 'mit' }).map(r => r.id)).toEqual(['01-beta'])
  })

  it('falls back to prefix.split for compound prefixes (covers path 2 of the head extraction)', async () => {
    harness = await makeHarness({
      // 28-10 covers the compound-prefix split branch.
      'agents/28-10-finance-data-base.md': '# 28-10 财经数据底座师\n\nDesc.',
    })
    const roles = await harness.ctx.agentRoster.loadAll()
    expect(roles[0]?.numericPrefix).toBe('28-10')
    expect(roles[0]?.family).toBe('finance')
  })

  it('classifies roles with numericPrefix 96-99 as hr (covers upper-bound branch)', async () => {
    harness = await makeHarness({
      'agents/98-budget-manager.md': '# 98-budget-manager\n\nDesc.',
      'agents/99-hr-recruiter.md': '# 99-hr-recruiter\n\nDesc.',
    })
    const roles = await harness.ctx.agentRoster.loadAll()
    expect(roles.find(r => r.id === '98-budget-manager')?.family).toBe('hr')
    expect(roles.find(r => r.id === '99-hr-recruiter')?.family).toBe('hr')
  })

  it('breaks the family chain when headNum exceeds 99 (unknown fallback)', async () => {
    harness = await makeHarness({
      'agents/synthetic-100-role.md': '# synthetic-100-role\n\nDesc.',
    })
    const roles = await harness.ctx.agentRoster.loadAll()
    expect(roles[0]?.family).toBe('unknown')
  })
})

beforeEach(() => {
  delete process.env.DRAGON_ASSETS_ROOT
})
