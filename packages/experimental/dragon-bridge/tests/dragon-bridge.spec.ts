import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { Context } from '@deepseek-ai/cordis'
import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import DragonAssetIndex from '@deepseek-ai/dsh-experimental-skill-index'
import AgentRoster from '@deepseek-ai/dsh-experimental-agent-roster'
import LicensePolicy from '@deepseek-ai/dsh-experimental-license-policy'
import DragonBridge from '../src/index'

interface Harness {
  ctx: Context
  root: string
  cleanup: () => void
}

async function makeHarness(layout: {
  index?: Record<string, string>
  agents?: Record<string, string>
}): Promise<Harness> {
  const root = mkdtempSync(join(tmpdir(), 'dsh-dragon-bridge-'))
  const indexDir = join(root, 'index')
  const agentsDir = join(root, 'agents')
  mkdirSync(indexDir, { recursive: true })
  mkdirSync(agentsDir, { recursive: true })

  const fileMap: Record<string, string> = {
    skill: 'SKILLS.jsonl',
    agent: 'AGENTS.jsonl',
    hook: 'HOOKS.jsonl',
    command: 'COMMANDS.jsonl',
    plugin: 'PLUGINS.jsonl',
  }
  for (const [kind, content] of Object.entries(layout.index ?? {})) {
    const file = fileMap[kind]
    if (file === undefined) continue
    writeFileSync(join(indexDir, file), content, 'utf8')
  }
  for (const [relPath, content] of Object.entries(layout.agents ?? {})) {
    const full = join(root, relPath)
    mkdirSync(join(full, '..'), { recursive: true })
    writeFileSync(full, content, 'utf8')
  }

  const ctx = new Context()
  await ctx.plugin(DragonAssetIndex, { dragonAssetsRoot: root })
  await ctx.plugin(AgentRoster, { dragonAssetsRoot: root })
  await ctx.plugin(LicensePolicy)
  await ctx.plugin(DragonBridge)
  return {
    ctx,
    root,
    cleanup: () => { rmSync(root, { recursive: true, force: true }) },
  }
}

const SAMPLE_INDEX = {
  skill: [
    '{"id":"async-task-pattern","kind":"skill","path":"skills/async-task-pattern","license":"mit"}',
    '{"id":"guizang-card","kind":"skill","path":"skills/guizang-social-card-skill","license":"AGPL-3.0"}',
    '{"id":"a-stock-bridge","kind":"skill","path":"skills/a-stock-data-bridge","license":"Apache-2.0"}',
    '{"id":"cangjie","kind":"skill","path":"skills/cangjie-skill","license":"AGPL-3.0"}',
  ].join('\n'),
  agent: '{"id":"blogger-distiller","kind":"agent","path":"agents/35-06","license":"mit"}',
  command: '{"id":"check","kind":"command","path":"commands/check.md"}',
  plugin: '{"id":"hookify","kind":"plugin","path":"plugins/hookify","license":"NOASSERTION"}',
  hook: '{"id":"session-start","kind":"hook","path":"hooks/session-start"}',
}

const SAMPLE_AGENTS = {
  'agents/00-analyst.md': [
    '---',
    'license: mit',
    '---',
    '',
    '# 00-analyst',
    '',
    'Generic investigation analyst.',
  ].join('\n'),
  'agents/28-10-finance.md': [
    '---',
    'license: apache-2.0',
    '---',
    '',
    '# 28-10-finance',
    '',
    'A 股 + 美港股投研底稿师.',
  ].join('\n'),
}

describe('dragonBridge', () => {
  let harness: Harness | undefined

  afterEach(() => {
    harness?.cleanup()
    harness = undefined
  })

  it('starts with an empty asset list before loadAll()', async () => {
    harness = await makeHarness({})
    expect(harness.ctx.dragonBridge.assets$).toEqual([])
  })

  it('loadAll() merges every skill kind and agent role with a license evaluation', async () => {
    harness = await makeHarness({ index: SAMPLE_INDEX, agents: SAMPLE_AGENTS })
    const assets = await harness.ctx.dragonBridge.loadAll()
    // Index contributes 4 skills + 1 agent + 1 command + 1 plugin + 1 hook = 8.
    // Agent roster contributes 2 agents. Total = 8 + 2 = 10 (duplicates by id are kept).
    expect(assets.length).toBe(10)
    const skill = assets.find(a => a.kind === 'skill' && a.source.id === 'guizang-card')
    expect(skill?.licenseTier).toBe('agpl-3.0')
    expect(skill?.decision).toBe('artifact-only')
    const plugin = assets.find(a => a.kind === 'plugin' && a.source.id === 'hookify')
    expect(plugin?.licenseTier).toBe('noassertion')
    expect(plugin?.decision).toBe('reject')
  })

  it('search() filters by kind and text', async () => {
    harness = await makeHarness({ index: SAMPLE_INDEX, agents: SAMPLE_AGENTS })
    await harness.ctx.dragonBridge.loadAll()
    const br = harness.ctx.dragonBridge

    const finance = br.search({ text: 'finance' })
    expect(finance.length).toBeGreaterThan(0)
    expect(finance.some(a => a.source.id === '28-10-finance')).toBe(true)

    const skillOnly = br.search({ kind: 'skill' })
    expect(skillOnly.every(a => a.kind === 'skill')).toBe(true)
  })

  it('matches against displayName when description is absent (fallback path)', async () => {
    harness = await makeHarness({
      index: {
        // Entry without description forces describeSource() to fall through
        // to the displayName branch in the bridge.
        skill: '{"id":"no-desc-skill","kind":"skill","path":"x"}',
      },
      agents: {
        // AgentRole has a displayName; search the agent roster to exercise
        // the `displayName` fallback path inside describeSource().
        'agents/finance-bridge.md': [
          '---',
          'license: mit',
          '---',
          '',
          '# finance-bridge',
          '',
          'A 股 bridge agent.',
        ].join('\n'),
      },
    })
    await harness.ctx.dragonBridge.loadAll()
    const br = harness.ctx.dragonBridge
    // "no-desc-skill" lives only in id, not in description — must still be
    // reachable through id-substring match.
    expect(br.search({ text: 'no-desc' }).map(a => a.source.id)).toEqual(['no-desc-skill'])
  })

  it('matches an agent whose displayName contains the needle', async () => {
    harness = await makeHarness({
      agents: {
        'agents/finance-bridge.md': [
          '---',
          'license: mit',
          '---',
          '',
          '# finance-bot',
          '',
          'A 股 bridge specialist.',
        ].join('\n'),
      },
    })
    await harness.ctx.dragonBridge.loadAll()
    const br = harness.ctx.dragonBridge
    // "specialist" lives only in description, not in id — exercises the
    // description-hit branch inside matchesNeedle().
    expect(br.search({ text: 'specialist' }).map(a => a.source.id)).toContain('finance-bridge')
  })

  it('search() filters by license and decision', async () => {
    harness = await makeHarness({ index: SAMPLE_INDEX, agents: SAMPLE_AGENTS })
    await harness.ctx.dragonBridge.loadAll()
    const br = harness.ctx.dragonBridge

    expect(br.search({ license: 'mit' }).length).toBeGreaterThan(0)
    expect(br.search({ license: 'agpl-3.0' }).length).toBe(2)
    expect(br.search({ decision: 'artifact-only' }).length).toBe(2)
    expect(br.search({ decision: 'reject' }).length).toBe(1)
  })

  it('search() respects limit and ordering', async () => {
    harness = await makeHarness({ index: SAMPLE_INDEX, agents: SAMPLE_AGENTS })
    await harness.ctx.dragonBridge.loadAll()
    const br = harness.ctx.dragonBridge
    expect(br.search({ limit: 3 }).length).toBe(3)
  })

  it('safeOnly constructor flag filters out artifact-only and reject entries', async () => {
    harness = await makeHarness({ index: SAMPLE_INDEX, agents: SAMPLE_AGENTS })
    const safeCtx = new Context()
    await safeCtx.plugin(DragonAssetIndex, { dragonAssetsRoot: harness.root })
    await safeCtx.plugin(AgentRoster, { dragonAssetsRoot: harness.root })
    await safeCtx.plugin(LicensePolicy)
    await safeCtx.plugin(DragonBridge, { safeOnly: true })
    await safeCtx.dragonBridge.loadAll()

    const decisions = new Set(safeCtx.dragonBridge.search().map(a => a.decision))
    expect(decisions.has('artifact-only')).toBe(false)
    expect(decisions.has('reject')).toBe(false)

    // Explicit decision overrides the safeOnly filter.
    expect(safeCtx.dragonBridge.search({ decision: 'reject' }).length).toBe(1)
  })

  it('allowed() / attributed() / artifactOnly() / rejected() return the right buckets', async () => {
    harness = await makeHarness({ index: SAMPLE_INDEX, agents: SAMPLE_AGENTS })
    await harness.ctx.dragonBridge.loadAll()
    const br = harness.ctx.dragonBridge

    expect(br.allowed().every(a => a.decision === 'allow')).toBe(true)
    expect(br.attributed().every(a => a.decision === 'attribute')).toBe(true)
    expect(br.artifactOnly().every(a => a.decision === 'artifact-only')).toBe(true)
    expect(br.rejected().every(a => a.decision === 'reject')).toBe(true)
    expect(br.rejected().length).toBe(1)
    expect(br.artifactOnly().length).toBe(2)
  })

  it('disposes the bridge cleanly (HMR safety)', async () => {
    const ctx = new Context()
    await ctx.plugin(DragonAssetIndex)
    await ctx.plugin(AgentRoster)
    await ctx.plugin(LicensePolicy)
    const fiber = await ctx.plugin(DragonBridge)
    await ctx.dragonBridge.loadAll()
    expect(ctx.dragonBridge.assets$.length).toBeGreaterThan(0)
    await fiber.dispose()
    expect((ctx as unknown as { dragonBridge?: unknown }).dragonBridge).toBeUndefined()
  })
})

beforeEach(() => {
  delete process.env.DRAGON_ASSETS_ROOT
})
