/**
 * Dual-face typert Remote bridge — HOST face (M1 skeleton).
 *
 * M2 wires the generated typert `/remote` artifacts. Pattern to follow
 * (mirrors `@deepseek-ai/dsh-api-remotes`):
 *
 * ```ts
 * import { TypertRemoteService } from '@deepseek-ai/dsh-typert-protocol'
 *
 * @RemoteScope({ service: 'trajectoryDebug' })
 * export class TrajectoryDebugRemote extends TypertRemoteService {
 *   @Remote() async list(args: { sessionId: SessionId; query: TrajectoryQuery }) { … }
 *   @Remote() async stepContext(args: { sessionId: SessionId; stepIndex: number }) { … }
 *   @Remote() async perf(args: { sessionId: SessionId }) { … }
 *   @Remote() async replayStep(args: { cursor: ReplayCursor }) { … }
 *   @Remote() async breakpointSet(args: { sessionId: SessionId; spec: BreakpointSpec }) { … }
 *   @Remote() async breakpointResume(args: { sessionId: SessionId; cause: PauseCause }) { … }
 *   @Remote() async rerunTool(args: { sessionId: SessionId; seq: number; editedArgs: JsonValue }) { … }
 *   @Remote() async forkVariant(args: { sessionId: SessionId; req: ForkRequest }) { … }
 *   @Remote() async compare(args: { base: VariantId; head: VariantId }) { … }
 *   @Remote() async export(args: { sessionId: SessionId; format: ExportFormat }) { … }
 * }
 * ```
 *
 * The generated client declaration is mounted by the client face via
 * `ctx.remote.$mount(trajectoryDebugRemote)` and withdrawn on unload.
 *
 * @module dsh-trajectory-debug-remotes
 */

import type { Context } from '@deepseek-ai/cordis'

export const name = 'trajectory-debug-remotes'

/** Host entry. M1 keeps the row loadable; endpoint registration is M2. */
export function apply(ctx: Context): void {
  ctx.effect(() => {
    // M2: ctx.typert.register({ ...contribution with @Remote endpoints })
    // and forward 'trajectory-debug/paused|resumed|experiment' events through
    // the remote-event allowlist (pattern: dsh-api-remotes remote-events.ts).
    return () => undefined
  })
}
