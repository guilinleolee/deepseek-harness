import { describe, expect, it } from 'vitest'
import { compareTrajectories, jsonDiff } from '../src/diff-engine.ts'
import { ev } from './helpers.ts'

describe('jsonDiff', () => {
  it('reports scalar changes with paths', () => {
    expect(jsonDiff({ a: 1, b: 2 }, { a: 2, b: 2 })).toEqual(['$.a: changed 1 → 2'])
  })

  it('reports additions and removals', () => {
    expect(jsonDiff({ a: 1 }, { a: 1, b: 3 })).toEqual(['$.b: added 3'])
    expect(jsonDiff({ a: 1, b: 3 }, { a: 1 })).toEqual(['$.b: removed 3'])
  })

  it('diffs arrays by index', () => {
    expect(jsonDiff([1, 2], [1, 3])).toEqual(['$[1]: changed 2 → 3'])
  })

  it('returns empty for deep-equal values', () => {
    expect(jsonDiff({ a: { b: [1, 2] } }, { a: { b: [1, 2] } })).toEqual([])
  })
})

function sessionWithArgs(args: unknown): ReturnType<typeof ev>[] {
  return [
    ev({ type: 'turn/start', turn: 1 }),
    ev({ type: 'user/message', content: 'go' }),
    ev({ type: 'step/start', turn: 1, step: 1 }),
    ev({ type: 'assistant/message', turn: 1, step: 1 }),
    ev({ type: 'tool/call', step: 1, callId: 'c1', name: 'web_fetch', args }),
    ev({ type: 'tool/result', step: 1, callId: 'c1', isError: false, contentPreview: 'ok', time: 1000 }),
    ev({ type: 'step/end', turn: 1, step: 1 }),
    ev({ type: 'turn/end', turn: 1, reason: 'completed', time: 1000 }),
  ]
}

describe('compareTrajectories', () => {
  it('detects changed tool args and result diffs', () => {
    const base = sessionWithArgs({ url: 'https://a.example/1', page: 1 })
    const head = sessionWithArgs({ url: 'https://a.example/2', page: 2 })
    const result = compareTrajectories(base, head, { base: 'base' as never, head: 'head' as never })

    expect(result.stepsChanged).toEqual([0])
    expect(result.toolsChanged).toEqual([
      expect.objectContaining({ step: 0, name: 'web_fetch', kind: 'args-changed' }),
    ])
    expect(result.toolsChanged[0]!.diff.join('\n')).toContain('$.url: changed')
    expect(result.toolsChanged[0]!.diff.join('\n')).toContain('$.page: changed')
    expect(result.resultDiffs).toHaveLength(0) // same previews
    expect(result.summary).toContain('工具变更 1 处')
  })

  it('detects added/removed tools', () => {
    const base = sessionWithArgs({ url: 'https://a.example/1' })
    const head = [
      ...sessionWithArgs({ url: 'https://a.example/1' }),
      ev({ type: 'tool/call', step: 1, callId: 'c2', name: 'read', args: { path: 'x' } }),
      ev({ type: 'tool/result', step: 1, callId: 'c2', isError: false, contentPreview: 'x', time: 2000 }),
    ]
    const result = compareTrajectories(base, head, { base: 'base' as never, head: 'head' as never })
    // step 1 in head has 2 calls; alignment by position marks call 2 as added
    expect(result.toolsChanged.some((t) => t.kind === 'added')).toBe(true)
  })

  it('computes token and timing deltas in the summary', () => {
    const base = sessionWithArgs({ url: 'u' })
    const head = sessionWithArgs({ url: 'u' })
    const result = compareTrajectories(base, head, { base: 'base' as never, head: 'head' as never })
    expect(result.summary).toContain('工具调用无变化')
    expect(result.tokens.base).toEqual({ input: 0, output: 0 })
  })

  it('handles an empty base (one-sided comparison)', () => {
    const head = sessionWithArgs({ url: 'u' })
    const result = compareTrajectories([], head, { base: 'base' as never, head: 'head' as never })
    expect(result.baseStepCount).toBe(0)
    expect(result.headStepCount).toBe(1)
    expect(result.stepsChanged).toEqual([0])
  })

  it('detects a result flipping to error', () => {
    const base = [
      ev({ type: 'turn/start', turn: 1 }),
      ev({ type: 'step/start', turn: 1, step: 1 }),
      ev({ type: 'assistant/message', turn: 1, step: 1 }),
      ev({ type: 'tool/call', step: 1, callId: 'c1', name: 'bash', args: {} }),
      ev({ type: 'tool/result', step: 1, callId: 'c1', isError: false, contentPreview: 'ok' }),
      ev({ type: 'step/end', turn: 1, step: 1 }),
      ev({ type: 'turn/end', turn: 1, reason: 'completed' }),
    ]
    const head = [
      ...base.slice(0, 4),
      ev({ type: 'tool/result', step: 1, callId: 'c1', isError: true, code: 'EXIT_1', message: 'boom' }),
      ev({ type: 'step/end', turn: 1, step: 1 }),
      ev({ type: 'turn/end', turn: 1, reason: 'completed' }),
    ]
    const result = compareTrajectories(base, head, { base: 'base' as never, head: 'head' as never })
    expect(result.resultDiffs).toHaveLength(1)
    expect(result.resultDiffs[0]).toMatchObject({ step: 0, changed: true })
  })

  it('compares across multiple turns', () => {
    const twoTurn = (failSecond: boolean) => [
      ev({ type: 'turn/start', turn: 1 }),
      ev({ type: 'step/start', turn: 1, step: 1 }),
      ev({ type: 'assistant/message', turn: 1, step: 1 }),
      ev({ type: 'tool/call', step: 1, callId: 'c1', name: 'read', args: { path: 'a' } }),
      ev({ type: 'tool/result', step: 1, callId: 'c1', isError: false, contentPreview: 'a' }),
      ev({ type: 'step/end', turn: 1, step: 1 }),
      ev({ type: 'turn/end', turn: 1, reason: 'completed' }),
      ev({ type: 'turn/start', turn: 2 }),
      ev({ type: 'step/start', turn: 2, step: 2 }),
      ev({ type: 'assistant/message', turn: 2, step: 2 }),
      ev({ type: 'tool/call', step: 2, callId: 'c2', name: 'bash', args: { command: 'x' } }),
      ev({ type: 'tool/result', step: 2, callId: 'c2', isError: failSecond, contentPreview: failSecond ? '' : 'ok' }),
      ev({ type: 'step/end', turn: 2, step: 2 }),
      ev({ type: 'turn/end', turn: 2, reason: failSecond ? 'error' : 'completed' }),
    ]
    const result = compareTrajectories(twoTurn(false), twoTurn(true), { base: 'b' as never, head: 'h' as never })
    expect(result.stepsChanged).toContain(1)
    expect(result.summary).toContain('步数相同')
  })
})
