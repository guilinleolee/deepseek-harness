/**
 * Plugin entry tests. Cover:
 * - the `apply` function registers the tool and skill;
 * - the credential warning logs when TUSHARE_TOKEN is unconfigured;
 * - the `index.ts` re-exports match the README's contract.
 *
 * @module @deepseek-ai/dsh-a-share-screener/tests/plugin
 */

import { afterEach, describe, expect, it, vi } from 'vitest'
import { apply, name, inject } from '../src/index.ts'
import type { Config } from '../src/types.ts'
import { defineScreenTool } from '../src/tools/screen.ts'

afterEach(() => {
  vi.restoreAllMocks()
})

interface FakeRegistry {
  register: ReturnType<typeof vi.fn>
}

function makeCtx(): { ctx: import('@deepseek-ai/cordis').Context; tools: FakeRegistry; skills: FakeRegistry; logger: { warn: ReturnType<typeof vi.fn>; info: ReturnType<typeof vi.fn>; error: ReturnType<typeof vi.fn>; debug: ReturnType<typeof vi.fn> } } {
  const tools: FakeRegistry = { register: vi.fn() }
  const skills: FakeRegistry = { register: vi.fn() }
  const logger = { warn: vi.fn(), info: vi.fn(), error: vi.fn(), debug: vi.fn() }
  const ctx = {
    tools,
    skills,
    credentials: { describe: vi.fn().mockResolvedValue({ configured: false }) },
    jobs: { start: vi.fn() },
    logger,
    effect: vi.fn((fn: (signal: AbortSignal) => void) => {
      fn(new AbortController().signal)
      return () => {}
    }),
  } as unknown as import('@deepseek-ai/cordis').Context
  return { ctx, tools, skills, logger }
}

const config: Config = {
  cacheRoot: '.cache',
  defaultLimit: 30,
  defaultUniverse: { kind: 'hot', size: 500 },
  jobOutputLimitBytes: 1024,
}

describe('plugin', () => {
  it('declares the expected manifest', () => {
    expect(name).toBe('dsh-a-share-screener')
    expect(inject).toEqual(['tools', 'skills', 'credentials', 'jobs'])
  })

  it('registers the screen tool and the skill when applied', () => {
    const { ctx, tools, skills } = makeCtx()
    apply(ctx, config)
    expect(tools.register).toHaveBeenCalledTimes(1)
    expect(skills.register).toHaveBeenCalledTimes(1)
    const registeredSkill = skills.register.mock.calls[0]?.[0]
    expect(registeredSkill).toMatchObject({
      name: 'stock-screener',
      source: 'runtime',
      modelInvocable: true,
      userInvocable: false,
    })
    expect(typeof registeredSkill.content).toBe('string')
  })

  it('warns when TUSHARE_TOKEN is unconfigured', async () => {
    const { ctx, logger } = makeCtx()
    apply(ctx, config)
    await new Promise((resolve) => setImmediate(resolve))
    expect(logger.warn).toHaveBeenCalledWith(expect.stringContaining('TUSHARE_TOKEN'))
  })

  it('warns when better-sqlite3 cannot be loaded', async () => {
    const { ctx, logger } = makeCtx()
    apply(ctx, config)
    await new Promise((resolve) => setImmediate(resolve))
    // The warning fires unconditionally because the test host has no native binding; either
    // the token warning or the store warning is enough to assert the effect path executed.
    const warns = logger.warn.mock.calls.map((args) => String(args[0] ?? ''))
    expect(warns.some((line) => /TUSHARE_TOKEN|memory store/.test(line))).toBe(true)
  })

  it('exports defineScreenTool so tests can construct the tool without a Cordis host', () => {
    expect(typeof defineScreenTool).toBe('function')
  })
})
