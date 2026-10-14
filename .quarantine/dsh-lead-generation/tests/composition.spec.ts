/**
 * @module @deepseek-ai/dsh-lead-generation/tests/composition
 */
import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { Context } from '@deepseek-ai/cordis'
import SystemPrompt from '@deepseek-ai/dsh-system-prompt'
import { CallId } from '@deepseek-ai/dsh-llm'
import ToolRuntime from '@deepseek-ai/dsh-tools'
import * as leadGen from '@deepseek-ai/dsh-lead-generation'
import { computeTaskId, type TaskState } from '@deepseek-ai/dsh-lead-generation/state'

const testSignal = new AbortController().signal

let home: string
let ctx: Context
let state: TaskState

beforeEach(async () => {
  home = mkdtempSync(join(tmpdir(), 'dsh-lead-gen-'))
  ctx = new Context()
  await ctx.plugin(SystemPrompt)
  await ctx.plugin(ToolRuntime)
  await ctx.plugin(leadGen, {
    storagePath: join(home, 'state'),
    approvalsPath: join(home, 'approvals.json'),
    dryRun: true,
    agentKnowledge: false,
    agentConfig: false,
    synthSeedCount: 30,
  } satisfies leadGen.Config)
  state = new TaskState(join(home, 'state'))
})

afterEach(() => {
  rmSync(home, { recursive: true, force: true })
})

describe('lead-gen plugin: composition', () => {
  it('mounts alongside SystemPrompt and ToolRuntime without conflict', () => {
    expect(ctx).toBeDefined()
    expect(typeof ctx.tools.register).toBe('function')
  })

  it('registers the `lg_create_task` model-facing tool', () => {
    const found = ctx.tools.get('lg_create_task')
    expect(found, 'lg_create_task should be registered after apply()').toBeDefined()
    expect(found!.parameters).toMatchObject({
      type: 'object',
      properties: {
        industry: { type: 'string' },
        region: { type: 'string' },
        count: { type: 'number' },
      },
      required: ['industry', 'region', 'count'],
    })
  })

  it('registers the `lg_prospect` model-facing tool', () => {
    const found = ctx.tools.get('lg_prospect')
    expect(found, 'lg_prospect should be registered after apply()').toBeDefined()
    expect(found!.parameters).toMatchObject({
      type: 'object',
      properties: {
        taskId: { type: 'string' },
      },
      required: ['taskId'],
    })
  })
})

describe('lg_create_task through ToolRuntime', () => {
  it('creates a task and returns its id', async () => {
    const result = await ctx.tools.execute({
      signal: testSignal,
      callId: CallId('c1'),
      name: 'lg_create_task',
      arguments: { industry: 'home', region: 'SEA', count: 30 },
    })
    expect(result.isError).toBe(false)
    if (result.isError) throw new Error('unreachable')
    const expectedId = computeTaskId('home', 'SEA', 30)
    expect(result.value).toMatchObject({ taskId: expectedId, stage: 'parsing', created: true })
  })

  it('is idempotent on identical inputs', async () => {
    const args = { industry: 'home', region: 'SEA', count: 30 }
    const first = await ctx.tools.execute({
      signal: testSignal,
      callId: CallId('c1'),
      name: 'lg_create_task',
      arguments: args,
    })
    const second = await ctx.tools.execute({
      signal: testSignal,
      callId: CallId('c2'),
      name: 'lg_create_task',
      arguments: args,
    })
    if (first.isError || second.isError) throw new Error('unreachable')
    expect(first.value).toMatchObject({ created: true })
    expect(second.value).toMatchObject({ created: false })
    expect(second.value).toMatchObject({ taskId: (first.value as { taskId: string }).taskId })
  })
})

describe('lg_prospect end-to-end through TaskState', () => {
  it('materializes 30 prospects and advances the task from parsing to prospecting', async () => {
    const created = await state.createOrLoad({ industry: 'home', region: 'SEA', count: 30 })
    expect(created.stage).toBe('parsing')
    expect(created.prospects).toEqual([])

    const result = await ctx.tools.execute({
      signal: testSignal,
      callId: CallId('p1'),
      name: 'lg_prospect',
      arguments: { taskId: created.taskId },
    })
    expect(result.isError).toBe(false)
    if (result.isError) throw new Error(result.content.map(c => c.text).join('\n'))

    const value = result.value as { stage: string; prospects: Array<{ id: string; name: string }> }
    expect(value.stage).toBe('prospecting')
    expect(value.prospects).toHaveLength(30)
    expect(value.prospects[0]).toMatchObject({
      id: 'p001',
      name: 'PT Rumah Nyaman Indonesia',
    })

    const reloaded = await state.load(created.taskId)
    expect(reloaded!.stage).toBe('prospecting')
    expect(reloaded!.prospects).toHaveLength(30)
  })

  it('is idempotent: a second call returns the same prospects without rewinding', async () => {
    const created = await state.createOrLoad({ industry: 'home', region: 'SEA', count: 30 })
    const first = await ctx.tools.execute({
      signal: testSignal,
      callId: CallId('p1'),
      name: 'lg_prospect',
      arguments: { taskId: created.taskId },
    })
    const second = await ctx.tools.execute({
      signal: testSignal,
      callId: CallId('p2'),
      name: 'lg_prospect',
      arguments: { taskId: created.taskId },
    })
    expect(first.isError).toBe(false)
    expect(second.isError).toBe(false)
    if (first.isError || second.isError) throw new Error('unreachable')
    const a = first.value as { prospects: unknown[] }
    const b = second.value as { prospects: unknown[] }
    expect(b.prospects).toEqual(a.prospects)
  })

  it('refuses to advance from a downstream stage', async () => {
    const created = await state.createOrLoad({ industry: 'home', region: 'SEA', count: 30 })
    await state.save({ ...created, stage: 'drafting', updatedAt: new Date().toISOString() })

    const result = await ctx.tools.execute({
      signal: testSignal,
      callId: CallId('p1'),
      name: 'lg_prospect',
      arguments: { taskId: created.taskId },
    })
    expect(result.isError).toBe(true)
    expect(result.content.map(c => c.text).join('\n')).toMatch(/expected stage parsing, currently drafting/)
  })

  it('throws a clear error when the task does not exist', async () => {
    const result = await ctx.tools.execute({
      signal: testSignal,
      callId: CallId('p1'),
      name: 'lg_prospect',
      arguments: { taskId: 'no-such-task' },
    })
    expect(result.isError).toBe(true)
    expect(result.content.map(c => c.text).join('\n')).toMatch(/task no-such-task not found/)
  })
})

