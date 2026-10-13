import { Service, type Context } from '@deepseek-ai/cordis'
import type {
  Breakpoint,
  BreakpointId,
  BreakpointSpec,
  CompareResult,
  DebugSession,
  ExportFormat,
  ExportPayload,
  ExperimentRecord,
  ForkRequest,
  InterventionResult,
  JsonValue,
  PerfSnapshot,
  ReplayCursor,
  ReplayFrame,
  SessionId,
  StepContext,
  TrajectoryPage,
  TrajectoryQuery,
  Variant,
  VariantId,
} from './types.ts'

/**
 * The Trajectory Debug Workbench service seam.
 *
 * The definition layer owns the Request/Result types and the service
 * contract; the provider (`dsh-trajectory-debug-host`) implements it.
 * Consumers (typert remotes, command plugins, browser UI) depend on this
 * package alone.
 *
 * All methods operate on {@link DebugSession} — the plugin's own read-side
 * adaptation of a DSH `Session` — so the seam is stable against DSH churn.
 *
 * @module dsh-trajectory-debug/service
 */

declare module '@deepseek-ai/cordis' {
  interface Context {
    trajectoryDebug: TrajectoryDebugService
  }
}

export abstract class TrajectoryDebugService extends Service {
  constructor(ctx: Context) {
    super(ctx, 'trajectoryDebug')
  }

  /* ── read-only surface ── */

  /** Page of waterfall rows for the browser ledger (windowed). */
  abstract list(session: DebugSession, query: TrajectoryQuery): Promise<TrajectoryPage>

  /** Model view + action at one step boundary (deterministic replay context). */
  abstract stepContext(session: DebugSession, stepIndex: number): Promise<StepContext>

  /** Whole-log performance snapshot (P0 panel data). */
  abstract perf(session: DebugSession): Promise<PerfSnapshot>

  /* ── deterministic replay ── */

  abstract startReplay(session: DebugSession, variantId?: VariantId): Promise<ReplayCursor>
  abstract stepReplay(cursor: ReplayCursor): Promise<ReplayFrame>
  abstract seekReplay(cursor: ReplayCursor, stepIndex: number): Promise<ReplayFrame>

  /* ── breakpoints (live interception) ── */

  /** Set a breakpoint; the session is used to resolve a `step` seq into the
   * (turn, step) pair the live loop can match. */
  abstract setBreakpoint(session: DebugSession, spec: BreakpointSpec): Promise<BreakpointId>
  abstract removeBreakpoint(sessionId: SessionId, id: BreakpointId): Promise<void>
  abstract listBreakpoints(sessionId: SessionId): Promise<readonly Breakpoint[]>
  /** Resume an agent paused at a breakpoint (user decision). */
  abstract resume(sessionId: SessionId, cause: 'user' | 'timeout' | 'cancelled'): Promise<void>

  /* ── intervention / variants / compare ── */

  /** Re-run one recorded tool call with edited args inside the session sandbox. */
  abstract rerunTool(
    session: DebugSession,
    req: { seq: number; editedArgs: JsonValue },
  ): Promise<ExperimentRecord>

  abstract forkVariant(session: DebugSession, req: ForkRequest): Promise<Variant>
  abstract compare(base: VariantId, head: VariantId): Promise<CompareResult>

  /* ── export ── */

  abstract export(session: DebugSession, format: ExportFormat): Promise<ExportPayload>
}
