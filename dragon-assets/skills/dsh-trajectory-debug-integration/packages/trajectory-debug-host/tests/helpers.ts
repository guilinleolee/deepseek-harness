import type { DebugEvent, EventSeq } from 'dsh-trajectory-debug'

/**
 * Test event factory with auto-incrementing seq and stable wall times.
 * The `type` key discriminates; extra fields are spread as-is.
 */
let nextSeq = 0

export function resetSeq(): void {
  nextSeq = 0
}

export function ev(partial: { type: string; time?: number } & Record<string, unknown>): DebugEvent {
  const time = typeof partial.time === 'number' ? partial.time : nextSeq * 1000
  const { time: _ignored, ...rest } = partial
  const seq = nextSeq
  nextSeq += 1
  return { ...rest, seq: seq as EventSeq, time } as unknown as DebugEvent
}

/** Convenience builders for a typical two-step session. */
export function sampleSession(): DebugEvent[] {
  resetSeq()
  return [
    ev({ type: 'turn/start', turn: 1 }),
    ev({ type: 'user/message', content: 'fix the failing test', source: 'direct' }),
    ev({ type: 'step/start', turn: 1, step: 1 }),
    ev({ type: 'assistant/chunk', step: 1, kind: 'text', text: 'Looking at the test…' }),
    ev({ type: 'assistant/chunk', step: 1, kind: 'reasoning', text: 'The test calls run() with an empty list.' }),
    ev({ type: 'assistant/message', turn: 1, step: 1, usage: { input: 120, output: 30 } }),
    ev({ type: 'tool/call', step: 1, callId: 'call-1', name: 'read', args: { path: 'src/a.test.ts' } }),
    ev({ type: 'tool/result', step: 1, callId: 'call-1', isError: false, contentPreview: 'import { run }…' }),
    ev({ type: 'step/end', turn: 1, step: 1 }),
    ev({ type: 'step/start', turn: 1, step: 2 }),
    ev({ type: 'assistant/chunk', step: 2, kind: 'text', text: 'The bug is an off-by-one.' }),
    ev({ type: 'assistant/message', turn: 1, step: 2, usage: { input: 160, output: 40 } }),
    ev({ type: 'tool/call', step: 2, callId: 'call-2', name: 'bash', args: { command: 'pnpm test' } }),
    ev({ type: 'tool/result', step: 2, callId: 'call-2', isError: true, code: 'EXIT_1', message: 'exit code 1', contentPreview: '1 test failed' }),
    ev({ type: 'step/end', turn: 1, step: 2 }),
    ev({ type: 'turn/end', turn: 1, reason: 'completed' }),
  ]
}
