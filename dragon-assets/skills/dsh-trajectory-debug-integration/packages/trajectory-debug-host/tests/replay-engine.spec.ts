import { describe, expect, it } from 'vitest'
import {
  buildTrajectoryPage,
  deriveModelView,
  resolveStepBoundary,
  stepBoundaries,
  stepContextAt,
} from '../src/replay-engine.ts'
import { ev, sampleSession } from './helpers.ts'

describe('stepBoundaries', () => {
  it('indexes every step with inclusive seq ranges', () => {
    const boundaries = stepBoundaries(sampleSession())
    expect(boundaries).toHaveLength(2)
    expect(boundaries[0]).toMatchObject({ step: 1, turn: 1, startSeq: 2 })
    expect(boundaries[0]!.endSeq).toBeGreaterThanOrEqual(boundaries[0]!.startSeq)
    expect(boundaries[1]).toMatchObject({ step: 2, startSeq: 9 })
  })

  it('returns empty for an empty log', () => {
    expect(stepBoundaries([])).toEqual([])
  })
})

describe('resolveStepBoundary', () => {
  it('resolves a seq inside a step to that step', () => {
    const events = sampleSession()
    expect(resolveStepBoundary(events, 5)?.step).toBe(1)
    expect(resolveStepBoundary(events, 11)?.step).toBe(2)
  })
})

describe('buildTrajectoryPage', () => {
  it('folds rows with statuses, durations, tokens and error codes', () => {
    const page = buildTrajectoryPage(sampleSession(), { window: { offset: 0, limit: 100 } })
    expect(page.turnCount).toBe(1)
    expect(page.stepCount).toBe(2)
    const tools = page.rows.filter((r) => r.kind === 'tool')
    expect(tools).toHaveLength(2)
    const failed = tools.find((r) => r.kind === 'tool' && r.name === 'bash')
    expect(failed).toMatchObject({ kind: 'tool', status: 'error' })
    if (failed?.kind === 'tool') {
      expect(failed.result?.code).toBe('EXIT_1')
      expect(failed.durationMs).toBe(1000)
    }
    const step = page.rows.find((r) => r.kind === 'step' && r.step === 1)
    if (step?.kind === 'step') {
      expect(step.inputTokens).toBe(120)
      expect(step.outputTokens).toBe(30)
      expect(step.reasoningSnippet).toContain('empty list')
    }
  })

  it('filters by tool name and error code', () => {
    const events = sampleSession()
    const page = buildTrajectoryPage(events, {
      window: { offset: 0, limit: 100 },
      filter: { toolName: 'read' },
    })
    expect(page.rows).toHaveLength(1)
    expect(page.rows[0]).toMatchObject({ kind: 'tool', name: 'read' })

    const err = buildTrajectoryPage(events, {
      window: { offset: 0, limit: 100 },
      filter: { errorCode: 'EXIT_1' },
    })
    expect(err.rows).toHaveLength(1)
    expect(err.rows[0]).toMatchObject({ kind: 'tool', name: 'bash' })
  })

  it('windows rows', () => {
    const page = buildTrajectoryPage(sampleSession(), { window: { offset: 0, limit: 3 } })
    expect(page.rows.length).toBeLessThanOrEqual(3)
  })
})

describe('deriveModelView', () => {
  it('shows everything the model saw before the boundary', () => {
    const events = sampleSession()
    const view = deriveModelView(events, 9) // before step 2
    const roles = view.map((m) => m.role)
    expect(roles).toContain('user')
    expect(roles).toContain('assistant')
    expect(roles).toContain('tool')
    expect(view.find((m) => m.role === 'tool' && m.toolCall?.name === 'read')).toBeDefined()
  })
})

describe('stepContextAt', () => {
  it('assembles model view + action for a step', () => {
    const events = sampleSession()
    const ctx = stepContextAt(events, 'session-1' as never, 0)
    expect(ctx.seq).toBe(2)
    expect(ctx.modelView.find((m) => m.role === 'user')?.content).toBe('fix the failing test')
    expect(ctx.action.tools).toHaveLength(1)
    expect(ctx.action.tools[0]).toMatchObject({ name: 'read', status: 'ok' })
    expect(ctx.nextCursor.stepIndex).toBe(1)
  })

  it('throws on out-of-range step index', () => {
    expect(() => stepContextAt(sampleSession(), 'session-1' as never, 99)).toThrow(RangeError)
  })
})

describe('edge cases', () => {
  it('handles an interrupted log (no turn/end)', () => {
    const events = [
      ev({ type: 'turn/start', turn: 1 }),
      ev({ type: 'step/start', turn: 1, step: 1 }),
      ev({ type: 'tool/call', step: 1, callId: 'c1', name: 'bash', args: {} }),
    ]
    const page = buildTrajectoryPage(events, { window: { offset: 0, limit: 100 } })
    expect(page.stepCount).toBe(1)
    const tool = page.rows.find((r) => r.kind === 'tool')
    expect(tool).toMatchObject({ kind: 'tool', status: 'pending' })
  })
})
