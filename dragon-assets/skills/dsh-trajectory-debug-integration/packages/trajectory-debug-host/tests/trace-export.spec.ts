import { describe, expect, it } from 'vitest'
import { buildTrace } from '../src/trace-export.ts'
import { ev, sampleSession } from './helpers.ts'

describe('buildTrace (OTel GenAI spans)', () => {
  it('emits turn, model and tool spans with gen_ai attributes', () => {
    const doc = buildTrace(sampleSession(), 'session-1')
    expect(doc.sessionId).toBe('session-1')
    const spans = doc.resourceSpans[0]!.scopeSpans[0]!.spans
    const turnSpans = spans.filter((s) => s.name === 'turn.1')
    expect(turnSpans.length).toBeGreaterThanOrEqual(1)

    const modelSpan = spans.find((s) => s.name.startsWith('llm.'))
    expect(modelSpan).toBeDefined()
    expect(modelSpan!.attributes['gen_ai.operation.name']).toBe('chat')
    expect(modelSpan!.attributes['gen_ai.usage.input_tokens']).toBe(120)
    expect(modelSpan!.parentSpanId).toBe('turn.1')

    const toolSpan = spans.find((s) => s.name.startsWith('tool.'))
    expect(toolSpan).toBeDefined()
    expect(toolSpan!.attributes['dsh.tool.name']).toBe('read')
    expect(toolSpan!.attributes['dsh.tool.ok']).toBe(true)
  })

  it('marks failed tool spans with the error code', () => {
    const doc = buildTrace(sampleSession(), 'session-1')
    const spans = doc.resourceSpans[0]!.scopeSpans[0]!.spans
    const failed = spans.find((s) => s.name.startsWith('tool.') && s.attributes['dsh.tool.ok'] === false)
    expect(failed).toBeDefined()
    expect(failed!.attributes['dsh.tool.error.code']).toBe('EXIT_1')
  })

  it('carries a perf summary and handles empty logs', () => {
    const doc = buildTrace([], 'session-0')
    expect(doc.summary.turns.steps).toBe(0)
    expect(doc.resourceSpans[0]!.scopeSpans[0]!.spans).toEqual([])
  })
})
