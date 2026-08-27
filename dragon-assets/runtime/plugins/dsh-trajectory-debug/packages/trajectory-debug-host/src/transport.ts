/**
 * Browser RPC transport over the host webserver.
 *
 * DSH's typert Remote chain is generated at build time (not available in this
 * workspace), so the browser panels talk to the provider through a plain
 * JSON-RPC-ish POST route registered on the host webserver — the sanctioned
 * "web-transport plugins register their own routes" extension point. The
 * server binds loopback by default; the route carries no extra trust beyond
 * the server bind.
 *
 * Endpoint: `POST /api/trajectory-debug/rpc`
 * Body: `{ "method": string, "params": JsonValue }`
 * Response: `{ "ok": true, "value": JsonValue } | { "ok": false, "error": { code, message } }`
 *
 * @module dsh-trajectory-debug-host/transport
 */

import type { IncomingMessage, ServerResponse } from 'node:http'
import type { Context } from '@deepseek-ai/cordis'
import type { DebugSession, JsonValue, SessionId } from 'dsh-trajectory-debug'
import { adaptSession } from './adapt.ts'
import type { TrajectoryDebugProvider } from './index.ts'

export interface RpcRequest {
  method: string
  params: JsonValue
}

export type RpcResponse =
  | { ok: true; value: JsonValue }
  | { ok: false; error: { code: string; message: string } }

/** Minimal webserver surface (the full type comes from dsh-host-webserver). */
export interface WebServerLike {
  register(route: {
    kind: 'exact' | 'prefix'
    path: string
    handler: (req: IncomingMessage, res: ServerResponse) => void | Promise<void>
  }): () => void
}

function respond(res: ServerResponse, status: number, payload: RpcResponse): void {
  res.writeHead(status, { 'content-type': 'application/json' })
  res.end(JSON.stringify(payload))
}

async function readBody(req: IncomingMessage): Promise<string> {
  const chunks: Buffer[] = []
  for await (const chunk of req) chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk))
  return Buffer.concat(chunks).toString('utf8')
}

/** Dispatch one RPC request against the provider. */
export async function dispatchRpc(provider: TrajectoryDebugProvider, request: RpcRequest): Promise<JsonValue> {
  const params = (request.params ?? {}) as Record<string, JsonValue> & {
    sessionId?: string
    cursor?: JsonValue
    stepIndex?: number
    seq?: number
    editedArgs?: JsonValue
    variantId?: string
    base?: string
    head?: string
    query?: JsonValue
    spec?: JsonValue
    id?: string
    cause?: string
    format?: string
    req?: JsonValue
  }
  const resolveSession = (sessionId: string): DebugSession => provider.resolveDebugSession(sessionId as SessionId)

  switch (request.method) {
    case 'trajectory.list': {
      const session = resolveSession(String(params.sessionId))
      return (await provider.list(session, params.query as never)) as unknown as JsonValue
    }
    case 'step.context': {
      const session = resolveSession(String(params.sessionId))
      return (await provider.stepContext(session, Number(params.stepIndex))) as unknown as JsonValue
    }
    case 'perf': {
      const session = resolveSession(String(params.sessionId))
      return (await provider.perf(session)) as unknown as JsonValue
    }
    case 'replay.start': {
      const session = resolveSession(String(params.sessionId))
      return (await provider.startReplay(session, params.variantId as never)) as unknown as JsonValue
    }
    case 'replay.step': {
      return (await provider.stepReplay(params.cursor as never)) as unknown as JsonValue
    }
    case 'replay.seek': {
      return (await provider.seekReplay(params.cursor as never, Number(params.stepIndex))) as unknown as JsonValue
    }
    case 'breakpoint.set': {
      const session = resolveSession(String(params.sessionId))
      return (await provider.setBreakpoint(session, params.spec as never)) as unknown as JsonValue
    }
    case 'breakpoint.remove': {
      await provider.removeBreakpoint(String(params.sessionId) as SessionId, params.id as never)
      return null
    }
    case 'breakpoint.list': {
      return (await provider.listBreakpoints(String(params.sessionId) as SessionId)) as unknown as JsonValue
    }
    case 'breakpoint.resume': {
      await provider.resume(String(params.sessionId) as SessionId, (params.cause ?? 'user') as never)
      return null
    }
    case 'intervention.rerunTool': {
      const session = resolveSession(String(params.sessionId))
      return (await provider.rerunTool(session, { seq: Number(params.seq), editedArgs: params.editedArgs ?? null })) as unknown as JsonValue
    }
    case 'variant.fork': {
      const session = resolveSession(String(params.sessionId))
      return (await provider.forkVariant(session, params.req as never)) as unknown as JsonValue
    }
    case 'variant.list': {
      return (await provider.listVariants(String(params.sessionId) as SessionId)) as unknown as JsonValue
    }
    case 'variant.compare': {
      return (await provider.compare(params.base as never, params.head as never)) as unknown as JsonValue
    }
    case 'export': {
      const session = resolveSession(String(params.sessionId))
      return (await provider.export(session, params.format as never)) as unknown as JsonValue
    }
    default:
      throw new Error(`trajectory-debug: unknown rpc method "${request.method}"`)
  }
}

/** Register the POST route; returns the disposer, or `undefined` when the
 * webserver is not mounted. */
export function registerTrajectoryDebugTransport(
  ctx: Context,
  provider: TrajectoryDebugProvider,
): (() => void) | undefined {
  const webServer = ctx.get('webServer') as WebServerLike | undefined
  if (webServer === undefined) return undefined
  return webServer.register({
    kind: 'exact',
    path: '/api/trajectory-debug/rpc',
    handler: async (req, res) => {
      if (req.method !== 'POST') {
        respond(res, 405, { ok: false, error: { code: 'METHOD_NOT_ALLOWED', message: 'POST required' } })
        return
      }
      let request: RpcRequest
      try {
        request = JSON.parse(await readBody(req)) as RpcRequest
      } catch {
        respond(res, 400, { ok: false, error: { code: 'BAD_REQUEST', message: 'invalid JSON body' } })
        return
      }
      try {
        const value = await dispatchRpc(provider, request)
        respond(res, 200, { ok: true, value })
      } catch (error) {
        respond(res, 200, {
          ok: false,
          error: {
            code: 'RPC_ERROR',
            message: error instanceof Error ? error.message : String(error),
          },
        })
      }
    },
  })
}
