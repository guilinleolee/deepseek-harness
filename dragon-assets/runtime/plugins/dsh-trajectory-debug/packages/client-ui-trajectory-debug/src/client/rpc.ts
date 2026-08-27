/**
 * Browser RPC client for the host webserver transport
 * (`POST /api/trajectory-debug/rpc`, registered by the host plugin).
 */

export interface RpcError extends Error {
  code: string
}

/** Call one host RPC method; resolves to the `value` or throws RpcError. */
export async function rpc<T>(method: string, params: Record<string, unknown>): Promise<T> {
  let response: Response
  try {
    response = await fetch('/api/trajectory-debug/rpc', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ method, params }),
    })
  } catch (error) {
    const e = new Error(`trajectory-debug rpc: network error (${String(error)})`) as RpcError
    e.code = 'NETWORK'
    throw e
  }
  let payload: { ok: boolean; value?: unknown; error?: { code: string; message: string } }
  try {
    payload = (await response.json()) as typeof payload
  } catch {
    const e = new Error(`trajectory-debug rpc: non-JSON response (${response.status})`) as RpcError
    e.code = 'BAD_RESPONSE'
    throw e
  }
  if (!payload.ok) {
    const e = new Error(payload.error?.message ?? `trajectory-debug rpc ${method} failed`) as RpcError
    e.code = payload.error?.code ?? 'RPC_ERROR'
    throw e
  }
  return payload.value as T
}
