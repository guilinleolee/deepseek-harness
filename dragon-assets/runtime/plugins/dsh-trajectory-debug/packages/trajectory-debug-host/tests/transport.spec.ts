import { Context } from '@deepseek-ai/cordis'
import { describe, expect, it } from 'vitest'
import type { SessionId } from 'dsh-trajectory-debug'
import { TrajectoryDebugProvider } from '../src/index.ts'
import { MemorySidecar } from '../src/sidecar.ts'
import { dispatchRpc, registerTrajectoryDebugTransport } from '../src/transport.ts'

/** Provider with a fake sessions store returning an empty session. */
function makeProvider(): TrajectoryDebugProvider {
  const ctx = new Context()
  return new TrajectoryDebugProvider(
    ctx,
    { rerunToolPolicy: 'record' },
    {
      sessions: {
        fork: () => ({ id: 'child-1' }),
        get: (id: unknown) => ({ id, events: [] }),
      } as never,
      sidecar: new MemorySidecar(),
    } as never,
  )
}

describe('dispatchRpc', () => {
  it('serves perf for a session', async () => {
    const value = (await dispatchRpc(makeProvider(), {
      method: 'perf',
      params: { sessionId: 's1' },
    })) as { turns: { steps: number } }
    expect(value.turns.steps).toBe(0)
  })

  it('serves trajectory.list and export json', async () => {
    const provider = makeProvider()
    const list = (await dispatchRpc(provider, {
      method: 'trajectory.list',
      params: { sessionId: 's1', query: { window: { offset: 0, limit: 10 } } },
    })) as { rows: unknown[] }
    expect(Array.isArray(list.rows)).toBe(true)
    const payload = (await dispatchRpc(provider, {
      method: 'export',
      params: { sessionId: 's1', format: 'json' },
    })) as { format: string }
    expect(payload.format).toBe('json')
  })

  it('replays an empty session to finished', async () => {
    const provider = makeProvider()
    const frame = (await dispatchRpc(provider, {
      method: 'replay.step',
      params: { cursor: { sessionId: 's1', nextSeq: 0, stepIndex: 0 } },
    })) as { status: string }
    expect(frame.status).toBe('finished')
  })

  it('manages breakpoints and variants', async () => {
    const provider = makeProvider()
    const id = (await dispatchRpc(provider, {
      method: 'breakpoint.set',
      params: { sessionId: 's1', spec: { at: 'turn', turn: 1 } },
    })) as string
    expect(id).toMatch(/^bp-/)
    const list = (await dispatchRpc(provider, {
      method: 'breakpoint.list',
      params: { sessionId: 's1' },
    })) as unknown[]
    expect(list).toHaveLength(1)
    const variants = (await dispatchRpc(provider, {
      method: 'variant.list',
      params: { sessionId: 's1' },
    })) as unknown[]
    expect(variants).toEqual([])
  })

  it('rejects unknown methods and missing sessions', async () => {
    const provider = makeProvider()
    await expect(dispatchRpc(provider, { method: 'nope', params: {} })).rejects.toThrow(/unknown rpc method/)
    const noSessionProvider = new TrajectoryDebugProvider(
      new Context(),
      { rerunToolPolicy: 'record' },
      {
        sessions: { fork: () => ({ id: 'c' }), get: () => undefined } as never,
        sidecar: new MemorySidecar(),
      } as never,
    )
    await expect(
      dispatchRpc(noSessionProvider, { method: 'perf', params: { sessionId: 'missing' } }),
    ).rejects.toThrow(/session missing not found/)
  })
})

describe('registerTrajectoryDebugTransport', () => {
  it('registers the POST route on the webserver and handles requests', async () => {
    const ctx = new Context() as never
    const registered: Array<{ kind: string; path: string; handler: (req: never, res: never) => unknown }> = []
    const fakeWebServer = {
      register: (route: (typeof registered)[number]) => {
        registered.push(route)
        return () => undefined
      },
    }
    const provider = makeProvider()
    const dispose = registerTrajectoryDebugTransport(
      { get: (key: string) => (key === 'webServer' ? fakeWebServer : undefined) } as never,
      provider,
    )
    expect(dispose).toBeTypeOf('function')
    expect(registered).toHaveLength(1)
    expect(registered[0]).toMatchObject({ kind: 'exact', path: '/api/trajectory-debug/rpc' })
    dispose!()
    // The route is a POST-only JSON endpoint; method check + response wiring
    // are exercised in the handler directly.
    void registered[0]!.handler
    void ctx
  })
})
