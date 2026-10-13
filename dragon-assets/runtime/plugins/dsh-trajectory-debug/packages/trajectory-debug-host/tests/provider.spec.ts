import { Context } from '@deepseek-ai/cordis'
import { describe, expect, it } from 'vitest'
import type { DebugSession, ExperimentRecord, SessionId, Variant } from 'dsh-trajectory-debug'
import { TrajectoryDebugProvider } from '../src/index.ts'
import { MemorySidecar } from '../src/sidecar.ts'
import { ev, resetSeq } from './helpers.ts'

/** A minimal DebugSession with one tool call to re-run (tool call at seq 3). */
function sessionWithCall(): DebugSession {
  resetSeq()
  return {
    id: 'session-1' as SessionId,
    events: [
      ev({ type: 'turn/start', turn: 1 }),
      ev({ type: 'step/start', turn: 1, step: 1 }),
      ev({ type: 'assistant/message', turn: 1, step: 1 }),
      ev({ type: 'tool/call', step: 1, callId: 'c1', name: 'web_fetch', args: { url: 'https://a.example/1' } }),
      ev({ type: 'tool/result', step: 1, callId: 'c1', isError: false, contentPreview: 'old' }),
      ev({ type: 'step/end', turn: 1, step: 1 }),
      ev({ type: 'turn/end', turn: 1, reason: 'completed' }),
    ],
  }
}

interface FakeTools {
  calls: Array<{ name: string; arguments: unknown; agent?: unknown; signal: unknown }>
  result?: unknown
  error?: unknown
}

function fakeTools(overrides: Partial<FakeTools> = {}): FakeTools & { execute: (input: never) => Promise<unknown> } {
  const fake: FakeTools = { calls: [], result: undefined, error: undefined, ...overrides }
  return {
    ...fake,
    execute: (input: never) => {
      fake.calls.push(input as FakeTools['calls'][number])
      if (fake.error !== undefined) return Promise.reject(fake.error)
      return Promise.resolve(fake.result)
    },
  } as unknown as FakeTools & { execute: (input: never) => Promise<unknown> }
}

function makeProvider(
  options: { policy?: 'record' | 'sandbox' | 'ask' } = {},
  fakes: { tools?: ReturnType<typeof fakeTools>; resumeResult?: 'ok' | 'error'; liveAgent?: boolean } = {},
): TrajectoryDebugProvider {
  const ctx = new Context()
  const sidecar = new MemorySidecar()
  const sessions = {
    fork: (source: unknown, boundary?: number) => ({ id: `child-${boundary ?? 0}` }),
    get: () => undefined,
  }
  const agents = {
    get: () => (fakes.liveAgent === true ? { session: { id: 'session-1' } } : undefined),
    resume: () =>
      fakes.resumeResult === 'error'
        ? Promise.reject(new Error('resume boom'))
        : Promise.resolve({ agent: { followup: (msg: never) => void msg }, dispose: () => Promise.resolve() }),
  }
  const deps: { sessions: unknown; agents: unknown; sidecar: MemorySidecar; tools?: unknown } = {
    sessions,
    agents,
    sidecar,
  }
  if (fakes.tools !== undefined) deps.tools = fakes.tools
  return new TrajectoryDebugProvider(ctx, { rerunToolPolicy: options.policy ?? 'record' }, deps as never)
}

describe('rerunTool (M2 execution)', () => {
  it('policy=record never executes', async () => {
    const tools = fakeTools({ result: { isError: false, value: 'x', content: [] } })
    const provider = makeProvider({ policy: 'record' }, { tools })
    const record = await provider.rerunTool(sessionWithCall(), { seq: 3, editedArgs: { url: 'https://b.example/2' } })
    expect(tools.calls).toHaveLength(0)
    expect(record.newResult).toBeUndefined()
    expect(record.diff.join('\n')).toContain('$.url: changed')
  })

  it('policy=sandbox executes through the tools pipeline and maps success', async () => {
    const tools = fakeTools({ result: { isError: false, value: { ok: true }, content: [{ type: 'text', text: 'fetched' }] } })
    const provider = makeProvider({ policy: 'sandbox' }, { tools })
    const record = await provider.rerunTool(sessionWithCall(), { seq: 3, editedArgs: { url: 'https://b.example/2' } })
    expect(tools.calls).toHaveLength(1)
    expect(tools.calls[0]).toMatchObject({ name: 'web_fetch', arguments: { url: 'https://b.example/2' } })
    expect(record.newResult).toMatchObject({ isError: false, contentPreview: 'fetched' })
  })

  it('maps tool failures to classified error records', async () => {
    const tools = fakeTools({
      result: { isError: true, error: { message: 'boom', info: { code: 'NETWORK_ERR' } }, content: [] },
    })
    const provider = makeProvider({ policy: 'sandbox' }, { tools })
    const record = await provider.rerunTool(sessionWithCall(), { seq: 3, editedArgs: { url: 'https://b.example/2' } })
    expect(record.newResult).toMatchObject({ isError: true, code: 'NETWORK_ERR', message: 'boom' })
  })

  it('fail-closed when the tools service is absent', async () => {
    const provider = makeProvider({ policy: 'sandbox' }) // no tools fake
    const record = await provider.rerunTool(sessionWithCall(), { seq: 3, editedArgs: { url: 'u' } })
    expect(record.newResult).toMatchObject({ isError: true, code: 'TOOLS_UNAVAILABLE' })
  })

  it('policy=ask fails closed without a live agent', async () => {
    const tools = fakeTools({ result: { isError: false, value: 1, content: [] } })
    const provider = makeProvider({ policy: 'ask' }, { tools }) // liveAgent not set
    const record = await provider.rerunTool(sessionWithCall(), { seq: 3, editedArgs: { url: 'u' } })
    expect(tools.calls).toHaveLength(0)
    expect(record.newResult).toMatchObject({ isError: true, code: 'ASK_NO_LIVE_AGENT' })
  })

  it('policy=ask executes when a live agent exists (pipeline approval applies)', async () => {
    const tools = fakeTools({ result: { isError: false, value: 1, content: [] } })
    const provider = makeProvider({ policy: 'ask' }, { tools, liveAgent: true })
    const record = await provider.rerunTool(sessionWithCall(), { seq: 3, editedArgs: { url: 'u' } })
    expect(tools.calls).toHaveLength(1)
    expect(record.newResult).toMatchObject({ isError: false })
  })

  it('rejects a seq that is not a tool call', async () => {
    const provider = makeProvider()
    await expect(provider.rerunTool(sessionWithCall(), { seq: 99, editedArgs: {} })).rejects.toThrow(/no tool\/call/)
  })

  it('stores the experiment in the sidecar', async () => {
    const tools = fakeTools({ result: { isError: false, value: 1, content: [] } })
    const provider = makeProvider({ policy: 'sandbox' }, { tools })
    const record: ExperimentRecord = await provider.rerunTool(sessionWithCall(), { seq: 3, editedArgs: { url: 'u2' } })
    const listed = provider['sidecar'] as unknown as MemorySidecar
    expect(listed.listExperiments('session-1' as SessionId).map((r) => r.id)).toContain(record.id)
  })
})

describe('forkVariant (M2 live resume)', () => {
  it('forks at the nearest turn boundary and freezes without an instruction', async () => {
    const provider = makeProvider()
    const variant = await provider.forkVariant(sessionWithCall(), { boundarySeq: 5, label: 'baseline' })
    expect(variant.status).toBe('frozen')
    expect(variant.parentSessionId).toBe('session-1')
  })

  it('resumes the fork and follows up when an instruction is given', async () => {
    const provider = makeProvider({}, { resumeResult: 'ok' })
    const variant = await provider.forkVariant(sessionWithCall(), { boundarySeq: 5, instruction: 'retry with the new url' })
    expect(variant.status).toBe('live')
    expect(variant.sessionId).toMatch(/^child-/)
  })

  it('cascade=preserve replays later user inputs into the branch in order', async () => {
    const followups: string[] = []
    const provider = makeProvider({}, { resumeResult: 'ok' })
    // Capture followups through a custom agents fake.
    const ctx = new Context()
    const sidecar = new MemorySidecar()
    const agents = {
      get: () => undefined,
      resume: () =>
        Promise.resolve({
          agent: { followup: (msg: { content?: string }) => void followups.push(msg.content ?? '') },
          dispose: () => Promise.resolve(),
        }),
    }
    const patched = new TrajectoryDebugProvider(
      ctx,
      { rerunToolPolicy: 'record' },
      {
        sessions: { fork: () => ({ id: 'child-9' }), get: () => undefined } as never,
        agents: agents as never,
        sidecar,
      },
    )
    const events = sessionWithCall().events
    const withLaterInput = {
      id: 'session-1' as SessionId,
      events: [
        ...events.slice(0, events.length - 1), // drop the final turn/end
        ev({ type: 'user/message', content: 'later follow-up one' }),
        ev({ type: 'user/message', content: 'later follow-up two' }),
        ev({ type: 'turn/end', turn: 1, reason: 'completed' }),
      ],
    }
    const variant = await patched.forkVariant(withLaterInput, {
      boundarySeq: 5,
      cascade: 'preserve',
    })
    expect(variant.status).toBe('live')
    expect(followups).toEqual(['later follow-up one', 'later follow-up two'])
  })

  it('cascade=truncate (default) does not replay later inputs', async () => {
    const followups: string[] = []
    const provider = makeProvider({}, { resumeResult: 'ok' })
    const variant = await provider.forkVariant(sessionWithCall(), { boundarySeq: 5, cascade: 'truncate' })
    expect(variant.status).toBe('frozen') // no instruction, no preserved inputs → no resume
    expect(followups).toEqual([])
  })

  it('marks the variant failed when resume rejects', async () => {
    const provider = makeProvider({}, { resumeResult: 'error' })
    const variant = await provider.forkVariant(sessionWithCall(), { boundarySeq: 5, instruction: 'go' })
    expect(variant.status).toBe('failed')
    expect(variant.error).toContain('resume boom')
  })

  it('export trace renders OTel GenAI spans JSON', async () => {
    const provider = makeProvider()
    const payload = await provider.export(sessionWithCall(), 'trace')
    expect(payload.format).toBe('trace')
    expect(payload.content).toContain('gen_ai.operation.name')
    expect(payload.content).toContain('resourceSpans')
  })
})
