import { Context } from '@deepseek-ai/cordis'
import { describe, expect, it } from 'vitest'
import type { DebugSession, SessionId } from 'dsh-trajectory-debug'
import { registerTrajectoryModelTools, type SessionResolver } from '../src/model-tools.ts'
import { ev, resetSeq } from './helpers.ts'

/** Tool definition captured by the fake registry. */
interface CapturedTool {
  name: string
  description: string
  parameters: unknown
  execute: (args: never) => Promise<unknown>
}

function sampleSession(): DebugSession {
  resetSeq()
  return {
    id: 'session-1' as SessionId,
    events: [
      ev({ type: 'turn/start', turn: 1 }),
      ev({ type: 'user/message', content: 'go' }),
      ev({ type: 'step/start', turn: 1, step: 1 }),
      ev({ type: 'assistant/message', turn: 1, step: 1, usage: { input: 50, output: 10 } }),
      ev({ type: 'tool/call', step: 1, callId: 'c1', name: 'bash', args: { command: 'pnpm test' } }),
      ev({ type: 'tool/result', step: 1, callId: 'c1', isError: true, code: 'EXIT_1', message: 'exit 1', contentPreview: '1 failed' }),
      ev({ type: 'step/end', turn: 1, step: 1 }),
      ev({ type: 'tool/call', step: 1, callId: 'c2', name: 'read', args: { path: 'a.ts' } }),
      ev({ type: 'tool/result', step: 1, callId: 'c2', isError: false, contentPreview: 'ok' }),
      ev({ type: 'turn/end', turn: 1, reason: 'completed' }),
    ],
  }
}

function makeTools() {
  const registered: CapturedTool[] = []
  const ctx = new Context() as unknown as {
    tools: { register: (def: CapturedTool) => () => void }
  }
  ctx.tools = {
    register: (def) => {
      registered.push(def)
      return () => undefined
    },
  }
  return { ctx, registered }
}

describe('registerTrajectoryModelTools', () => {
  it('registers three read-only tools and returns a disposer', () => {
    const { ctx, registered } = makeTools()
    const dispose = registerTrajectoryModelTools(ctx as never, {
      resolveSession: (() => sampleSession()) as SessionResolver,
    })
    expect(registered.map((t) => t.name)).toEqual(['trajectory_search', 'trajectory_step', 'trajectory_perf'])
    dispose()
    // registration effects are caller-owned; the disposer is a no-op here
  })

  it('trajectory_search filters by tool name and reports rows', async () => {
    const { ctx, registered } = makeTools()
    registerTrajectoryModelTools(ctx as never, {
      resolveSession: (() => sampleSession()) as SessionResolver,
    })
    const tool = registered.find((t) => t.name === 'trajectory_search')!
    const out = (await tool.execute({ sessionId: 'session-1', toolName: 'bash', limit: 5 } as never)) as string
    expect(out).toContain('bash')
    expect(out).toContain('[EXIT_1]')
    expect(out).not.toContain('read')
  })

  it('trajectory_step renders the step action', async () => {
    const { ctx, registered } = makeTools()
    registerTrajectoryModelTools(ctx as never, {
      resolveSession: (() => sampleSession()) as SessionResolver,
    })
    const tool = registered.find((t) => t.name === 'trajectory_step')!
    const out = (await tool.execute({ sessionId: 'session-1', stepIndex: 0 } as never)) as string
    expect(out).toContain('history')
    expect(out).toContain('bash')
  })

  it('trajectory_perf summarizes the snapshot', async () => {
    const { ctx, registered } = makeTools()
    registerTrajectoryModelTools(ctx as never, {
      resolveSession: (() => sampleSession()) as SessionResolver,
    })
    const tool = registered.find((t) => t.name === 'trajectory_perf')!
    const out = (await tool.execute({ sessionId: 'session-1' } as never)) as string
    expect(out).toContain('perf:')
    expect(out).toContain('EXIT_1')
  })

  it('returns a helpful error for an unknown session', async () => {
    const { ctx, registered } = makeTools()
    registerTrajectoryModelTools(ctx as never, { resolveSession: (() => undefined) as SessionResolver })
    const tool = registered.find((t) => t.name === 'trajectory_search')!
    const out = (await tool.execute({ sessionId: 'nope' } as never)) as string
    expect(out).toContain('session not found')
  })
})
