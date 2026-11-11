/**
 * @module @deepseek-ai/dsh-lead-generation/tests/state
 */
import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import {
  assertStage, computeDraftHash, computeTaskId, nextStage, TaskState,
} from '@deepseek-ai/dsh-lead-generation/state'

let home: string

beforeEach(() => {
  home = mkdtempSync(join(tmpdir(), 'dsh-lead-gen-state-'))
})

afterEach(() => {
  rmSync(home, { recursive: true, force: true })
})

describe('computeTaskId', () => {
  it('is deterministic across calls', () => {
    const a = computeTaskId('家居', '东南亚', 30)
    const b = computeTaskId('家居', '东南亚', 30)
    expect(a).toBe(b)
  })

  it('changes when any triple component changes', () => {
    const a = computeTaskId('home', 'SEA', 30)
    expect(computeTaskId('home', 'SEA', 31)).not.toBe(a)
    expect(computeTaskId('home', 'JP', 30)).not.toBe(a)
    expect(computeTaskId('kitchen', 'SEA', 30)).not.toBe(a)
  })

  it('returns a 16-character hex digest', () => {
    const id = computeTaskId('home', 'SEA', 30)
    expect(id).toMatch(/^[0-9a-f]{16}$/)
  })
})

describe('assertStage', () => {
  it('accepts the expected stage', () => {
    expect(() => assertStage(
      { taskId: 't', industry: 'x', region: 'y', count: 1, stage: 'parsing', prospects: [], dossiers: {}, scores: {}, drafts: {}, createdAt: '', updatedAt: '' },
      'parsing',
    )).not.toThrow()
  })

  it('rejects a different stage with a clear message', () => {
    expect(() => assertStage(
      { taskId: 't', industry: 'x', region: 'y', count: 1, stage: 'parsing', prospects: [], dossiers: {}, scores: {}, drafts: {}, createdAt: '', updatedAt: '' },
      'prospecting',
    )).toThrow(/expected stage prospecting, currently parsing/)
  })
})

describe('nextStage', () => {
  it('advances through every transition', () => {
    expect(nextStage('parsing')).toBe('prospecting')
    expect(nextStage('prospecting')).toBe('research')
    expect(nextStage('research')).toBe('scoring')
    expect(nextStage('scoring')).toBe('drafting')
    expect(nextStage('drafting')).toBe('closed')
  })

  it('refuses to advance past closed', () => {
    expect(() => nextStage('closed')).toThrow(/terminal stage/)
  })
})

describe('computeDraftHash', () => {
  it('is deterministic', () => {
    expect(computeDraftHash('hello')).toBe(computeDraftHash('hello'))
  })

  it('changes when the body changes', () => {
    expect(computeDraftHash('hello')).not.toBe(computeDraftHash('Hello'))
  })

  it('uses the sha256: prefix', () => {
    expect(computeDraftHash('x')).toMatch(/^sha256:[0-9a-f]{64}$/)
  })
})

describe('TaskState persistence', () => {
  it('createOrLoad returns the same record on repeated calls', async () => {
    const state = new TaskState(join(home, 'state'))
    const args = { industry: 'home', region: 'SEA', count: 30 }
    const first = await state.createOrLoad(args)
    const second = await state.createOrLoad(args)
    expect(second.taskId).toBe(first.taskId)
    expect(second.createdAt).toBe(first.createdAt)
    expect(second.stage).toBe('parsing')
  })

  it('createOrLoad returns distinct records for different inputs', async () => {
    const state = new TaskState(join(home, 'state'))
    const a = await state.createOrLoad({ industry: 'home', region: 'SEA', count: 30 })
    const b = await state.createOrLoad({ industry: 'home', region: 'SEA', count: 31 })
    expect(a.taskId).not.toBe(b.taskId)
  })

  it('save / load roundtrip preserves the full record', async () => {
    const state = new TaskState(join(home, 'state'))
    const created = await state.createOrLoad({ industry: 'home', region: 'SEA', count: 30 })
    const loaded = await state.load(created.taskId)
    expect(loaded).toBeDefined()
    expect(loaded!.taskId).toBe(created.taskId)
  })

  it('load returns undefined when no record exists', async () => {
    const state = new TaskState(join(home, 'state'))
    const loaded = await state.load(computeTaskId('nope', 'nowhere', 99))
    expect(loaded).toBeUndefined()
  })
})
