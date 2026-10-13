/**
 * Host provider: wires the Trajectory Debug Workbench into a dsh process.
 *
 * On `apply` this plugin:
 * - provides the `trajectoryDebug` service (seam consumer face);
 * - installs the breakpoint interception listeners (per-agent isolation);
 * - registers the projection units and slash commands when those optional
 *   registries are mounted;
 * - mounts the sidecar (memory default, JSON-file when configured).
 *
 * Every registration is effect-owned: unloading the plugin (or a host HMR
 * reload) withdraws all of it, and the source sessions are never touched.
 *
 * M2: `rerunTool` executes through the real `ctx.tools` pipeline (policy,
 * approval and sandbox all apply — fail-closed), and `forkVariant` can
 * live-resume a branch through `ctx.agents.resume` + `followup`.
 *
 * @module dsh-trajectory-debug-host
 */

import { join } from 'node:path'
import { homedir } from 'node:os'
import { Service, type Context } from '@deepseek-ai/cordis'
import type { Agent, AgentRegistry } from '@deepseek-ai/dsh-agent'
import type { Session, SessionId as DshSessionId, SessionStore } from '@deepseek-ai/dsh-session'
import type { ToolFailure, ToolRuntime } from '@deepseek-ai/dsh-tools'
import type {
  Breakpoint,
  BreakpointId,
  BreakpointSpec,
  CallId,
  CompareResult,
  DebugEvent,
  DebugSession,
  ExportFormat,
  ExportPayload,
  ExperimentRecord,
  ForkRequest,
  JsonValue,
  PerfSnapshot,
  PauseCause,
  ReplayCursor,
  ReplayFrame,
  SessionId,
  StepContext,
  TrajectoryPage,
  TrajectoryQuery,
  Variant,
  VariantId,
} from 'dsh-trajectory-debug'
import { TrajectoryDebugService } from 'dsh-trajectory-debug'
import { adaptSession } from './adapt.ts'
import { BreakpointManager } from './breakpoint-manager.ts'
import { registerTrajectoryDebugCommands, summarizePerf, summarizeTrajectory } from './commands.ts'
import { compareTrajectories, jsonDiff } from './diff-engine.ts'
import { analyzePerf, type TokenPriceTable } from './perf-analyzer.ts'
import { registerTrajectoryDebugProjections } from './projections.ts'
import { registerTrajectoryModelTools } from './model-tools.ts'
import { registerTrajectoryDebugTransport } from './transport.ts'
import { renderTraceJson } from './trace-export.ts'
import { buildTrajectoryPage, resolveStepBoundary, stepBoundaries, stepContextAt } from './replay-engine.ts'
import { FileSidecar, MemorySidecar, type Sidecar } from './sidecar.ts'

export const name = 'trajectory-debug-host'
export const inject = ['sessions']

export interface TrajectoryDebugHostConfig {
  /** Max ms an agent stays paused at a breakpoint before auto-resume. */
  breakpointTimeoutMs?: number
  /** Re-run execution policy: 'record' never executes; 'sandbox' runs
   * through the tools pipeline (session sandbox applies); 'ask' runs only
   * when a LIVE agent exists for the session (the pipeline's own approval
   * then gates it) and fails closed otherwise. */
  rerunToolPolicy?: 'record' | 'sandbox' | 'ask'
  /** Timeout for one re-run tool execution. */
  rerunTimeoutMs?: number
  /** Timeout for a live-resume boot of a forked variant. */
  resumeTimeoutMs?: number
  /** Sidecar backend: 'memory' (default) or 'file' (JSON per session). */
  sidecar?: 'memory' | 'file'
  /** Root directory for the file sidecar (default: $DSH_HOME/trajectory-debug). */
  sidecarRoot?: string
  /** Optional token price table (per 1M tokens) enabling `perf.cost`. */
  tokenPriceTable?: TokenPriceTable
  /** Expose the read-only trajectory_search/step/perf model tools (P2). */
  enableModelTools?: boolean
}

/** Explicit dependency surface — lets unit tests inject fakes. */
export interface ProviderDeps {
  sessions?: SessionStore
  agents?: AgentRegistry
  tools?: ToolRuntime
  sidecar?: Sidecar
}

const DEFAULT_CONFIG: Omit<Required<TrajectoryDebugHostConfig>, 'tokenPriceTable'> & {
  tokenPriceTable?: TokenPriceTable
} = {
  breakpointTimeoutMs: 10 * 60 * 1000,
  rerunToolPolicy: 'record',
  rerunTimeoutMs: 120_000,
  resumeTimeoutMs: 60_000,
  sidecar: 'memory',
  sidecarRoot: join(process.env.DSH_HOME ?? join(homedir(), '.dsh'), 'trajectory-debug'),
  tokenPriceTable: undefined,
  enableModelTools: false,
}

/** The provider implementation of the `trajectoryDebug` seam. */
export class TrajectoryDebugProvider extends TrajectoryDebugService {
  private readonly sessions: SessionStore
  private readonly agents?: AgentRegistry
  private readonly tools?: ToolRuntime
  private readonly breakpoints: BreakpointManager
  private readonly sidecar: Sidecar
  private readonly config: Omit<Required<TrajectoryDebugHostConfig>, 'tokenPriceTable'> & {
    tokenPriceTable?: TokenPriceTable
  }

  constructor(ctx: Context, options: TrajectoryDebugHostConfig = {}, deps: ProviderDeps = {}) {
    super(ctx)
    this.config = { ...DEFAULT_CONFIG, ...options }
    this.sessions = deps.sessions ?? ctx.get('sessions')!
    this.agents = deps.agents ?? ctx.get('agents')
    this.tools = deps.tools ?? ctx.get('tools')
    this.breakpoints = new BreakpointManager({ timeoutMs: this.config.breakpointTimeoutMs })
    this.sidecar =
      deps.sidecar ??
      (this.config.sidecar === 'file' ? new FileSidecar(this.config.sidecarRoot) : new MemorySidecar())
  }

  /** Install listeners; call inside `ctx.effect`. */
  install(ctx: Context): () => void {
    return this.breakpoints.install(ctx)
  }

  /** Host teardown: abandon pause gates so agents never hang on unload. */
  dispose(): void {
    this.breakpoints.cancelAll()
  }

  /* ── read-only surface ── */

  list(session: DebugSession, query: TrajectoryQuery): Promise<TrajectoryPage> {
    const { rows, stepCount, turnCount } = buildTrajectoryPage(session.events, query)
    return Promise.resolve({
      sessionId: session.id,
      asOfSeq: (session.events.at(-1)?.seq ?? -1) as TrajectoryPage['asOfSeq'],
      rows,
      stepCount,
      turnCount,
    })
  }

  stepContext(session: DebugSession, stepIndex: number): Promise<StepContext> {
    return Promise.resolve(stepContextAt(session.events, session.id, stepIndex))
  }

  perf(session: DebugSession): Promise<PerfSnapshot> {
    return Promise.resolve(
      analyzePerf(session.events, session.id, session.events.at(-1)?.seq, this.config.tokenPriceTable),
    )
  }

  /* ── deterministic replay ── */

  startReplay(session: DebugSession, variantId?: VariantId): Promise<ReplayCursor> {
    const boundaries = stepBoundaries(session.events)
    const first = boundaries[0]
    return Promise.resolve({
      sessionId: session.id,
      variantId,
      nextSeq: first?.startSeq ?? 0,
      stepIndex: 0,
    })
  }

  stepReplay(cursor: ReplayCursor): Promise<ReplayFrame> {
    const adapted = adaptSession(this.requireSession(cursor.sessionId))
    const boundaries = stepBoundaries(adapted.events)
    if (cursor.stepIndex >= boundaries.length) {
      return Promise.resolve({ cursor, status: 'finished' })
    }
    try {
      const context = stepContextAt(adapted.events, cursor.sessionId, cursor.stepIndex, cursor.variantId)
      return Promise.resolve({ cursor: context.nextCursor, context, status: 'stepped' })
    } catch (error) {
      return Promise.resolve({
        cursor,
        status: error instanceof RangeError ? 'finished' : 'interrupted',
      })
    }
  }

  seekReplay(cursor: ReplayCursor, stepIndex: number): Promise<ReplayFrame> {
    const adapted = adaptSession(this.requireSession(cursor.sessionId))
    const boundaries = stepBoundaries(adapted.events)
    if (stepIndex < 0 || stepIndex >= boundaries.length) {
      return Promise.resolve({ cursor, status: 'finished' })
    }
    const context = stepContextAt(adapted.events, cursor.sessionId, stepIndex, cursor.variantId)
    return Promise.resolve({ cursor: context.nextCursor, context, status: 'stepped' })
  }

  /* ── breakpoints ── */

  setBreakpoint(session: DebugSession, spec: BreakpointSpec): Promise<BreakpointId> {
    if (spec.at === 'tool') {
      return Promise.reject(new Error('trajectory-debug: tool breakpoints are not implemented yet (M2.5)'))
    }
    const turnStep = spec.at === 'step'
      ? (() => {
          const boundary = resolveStepBoundary(session.events, spec.seq)
          return boundary === undefined ? undefined : { turn: boundary.turn, step: boundary.step }
        })()
      : undefined
    if (spec.at === 'step' && turnStep === undefined) {
      return Promise.reject(new Error(`trajectory-debug: seq ${spec.seq} is not inside a recorded step`))
    }
    return Promise.resolve(this.breakpoints.set(session.id, spec, turnStep))
  }

  removeBreakpoint(sessionId: SessionId, id: BreakpointId): Promise<void> {
    this.breakpoints.remove(sessionId, id)
    return Promise.resolve()
  }

  listBreakpoints(sessionId: SessionId): Promise<readonly Breakpoint[]> {
    return Promise.resolve(this.breakpoints.list(sessionId))
  }

  resume(sessionId: SessionId, cause: PauseCause): Promise<void> {
    this.breakpoints.resume(sessionId, cause)
    return Promise.resolve()
  }

  /* ── variants / compare / intervention ── */

  forkVariant(session: DebugSession, req: ForkRequest): Promise<Variant> {
    const boundary = this.normalizeBoundary(session, req.boundarySeq)
    const child = this.sessions.fork(session.id as unknown as DshSessionId, boundary)
    const variant: Variant = {
      id: this.sidecar.newVariantId(),
      sessionId: child.id,
      parentSessionId: session.id,
      boundarySeq: boundary,
      label: req.label ?? `fork@${boundary}`,
      status: 'frozen',
      createdAt: Date.now(),
    }
    // Cascade 'preserve': replay every LATER user input into the new branch
    // in order (dsh-message-edit's `preserve` semantics); 'truncate' (default)
    // drops them. The inputs enter through the ordinary agent channel
    // (followup), preserving "model-visible == recorded".
    const preserved: string[] =
      req.cascade === 'preserve'
        ? session.events
            .filter((e): e is Extract<DebugEvent, { type: 'user/message' }> => e.type === 'user/message' && e.seq > boundary)
            .map((e) => e.content)
        : []
    const followups = req.instruction !== undefined ? [req.instruction, ...preserved] : preserved
    if (followups.length > 0 && this.agents !== undefined) {
      return this.resumeVariant(variant, followups).then((resumed) => {
        this.sidecar.addVariant(resumed)
        return resumed
      })
    }
    this.sidecar.addVariant(variant)
    return Promise.resolve(variant)
  }

  compare(base: VariantId, head: VariantId): Promise<CompareResult> {
    const baseVariant = this.sidecar.getVariant(base)
    const headVariant = this.sidecar.getVariant(head)
    if (baseVariant === undefined || headVariant === undefined) {
      return Promise.reject(new Error('trajectory-debug: unknown variant id'))
    }
    const baseSession = this.requireSession(baseVariant.sessionId)
    const headSession = this.requireSession(headVariant.sessionId)
    return Promise.resolve(
      compareTrajectories(adaptSession(baseSession).events, adaptSession(headSession).events, { base, head }),
    )
  }

  rerunTool(session: DebugSession, req: { seq: number; editedArgs: JsonValue }): Promise<ExperimentRecord> {
    const call = session.events.find((e) => e.seq === req.seq && e.type === 'tool/call')
    if (call === undefined || call.type !== 'tool/call') {
      return Promise.reject(new Error(`trajectory-debug: no tool/call at seq ${req.seq}`))
    }
    const record: ExperimentRecord = {
      id: this.sidecar.newExperimentId(),
      sessionId: session.id,
      seq: call.seq,
      toolName: call.name,
      oldArgs: call.args,
      newArgs: req.editedArgs,
      oldResult: undefined,
      newResult: undefined,
      diff: jsonDiff(call.args, req.editedArgs),
      ts: Date.now(),
    }
    const policy = this.config.rerunToolPolicy
    if (policy === 'record') {
      this.sidecar.addExperiment(record)
      return Promise.resolve(record)
    }
    if (this.tools === undefined) {
      record.newResult = {
        isError: true,
        code: 'TOOLS_UNAVAILABLE',
        message: 'ctx.tools is not mounted; re-run execution unavailable',
      }
      this.sidecar.addExperiment(record)
      return Promise.resolve(record)
    }
    if (policy === 'ask') {
      // 'ask' fails closed without a live agent: the pipeline's own approval
      // waterfall is agent-scoped, so there is nobody to answer.
      const liveAgent = this.agents?.get(session.id as unknown as DshSessionId)
      if (liveAgent === undefined) {
        record.newResult = {
          isError: true,
          code: 'ASK_NO_LIVE_AGENT',
          message: 'rerunToolPolicy=ask requires a live agent for this session (approval responder)',
        }
        this.sidecar.addExperiment(record)
        return Promise.resolve(record)
      }
    }
    return this.executeRerun(call.name, req.editedArgs, session.id).then(
      (result) => {
        record.newResult = result
        this.sidecar.addExperiment(record)
        return record
      },
      (error: unknown) => {
        record.newResult = { isError: true, code: 'EXECUTION_ERROR', message: String(error) }
        this.sidecar.addExperiment(record)
        return record
      },
    )
  }

  /** List all fork variants recorded for one session. */
  listVariants(sessionId: SessionId): Promise<Variant[]> {
    return Promise.resolve(this.sidecar.listVariants(sessionId))
  }

  /** Resolve + adapt a live session for transport/RPC consumers. */
  resolveDebugSession(sessionId: SessionId): DebugSession {
    return adaptSession(this.requireSession(sessionId))
  }

  /* ── export ── */

  export(session: DebugSession, format: ExportFormat): Promise<ExportPayload> {
    let content: string
    if (format === 'json') {
      content = JSON.stringify({ sessionId: session.id, events: session.events }, null, 2)
    } else if (format === 'trace') {
      // OTel GenAI semantic-convention spans (Langfuse/LangSmith/collector ready).
      content = renderTraceJson(session.events, session.id)
    } else if (format === 'csv') {
      const perf = analyzePerf(session.events)
      const header = 'tool,calls,ok,failed,avgMs,p50Ms,p90Ms,p95Ms'
      const lines = Object.entries(perf.tools).map(([name, t]) =>
        [name, t.calls, t.ok, t.failed, t.ms.avg.toFixed(1), t.ms.p50, t.ms.p90, t.ms.p95].join(','),
      )
      content = [header, ...lines].join('\n')
    } else {
      content = summarizePerf(session)
    }
    return Promise.resolve({ sessionId: session.id, format, content })
  }

  /* ── internals ── */

  private resumeVariant(variant: Variant, followups: readonly string[]): Promise<Variant> {
    if (this.agents === undefined) {
      return Promise.resolve({ ...variant, status: 'failed', error: 'agent registry not mounted' })
    }
    return this.agents
      .resume({
        resumeSessionId: variant.sessionId as unknown as DshSessionId,
        signal: AbortSignal.timeout(this.config.resumeTimeoutMs),
      })
      .then((handle) => {
        for (const message of followups) {
          handle.agent.followup({ role: 'user', content: message } as never)
        }
      })
      .then(() => ({ ...variant, status: 'live' as const }))
      .catch((error: unknown) => ({
        ...variant,
        status: 'failed' as const,
        error: error instanceof Error ? error.message : String(error),
      }))
  }

  private executeRerun(
    name: string,
    editedArgs: JsonValue,
    sessionId: SessionId,
  ): Promise<ExperimentRecord['newResult']> {
    const tools = this.tools!
    const liveAgent = this.agents?.get(sessionId as unknown as DshSessionId)
    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), this.config.rerunTimeoutMs)
    return tools
      .execute({
        // Our CallId brand is structurally distinct from dsh-llm's; the
        // cast is the adapter boundary between the two type systems.
        callId: this.newCallId() as never,
        name,
        arguments: editedArgs,
        agent: liveAgent as Agent | undefined,
        signal: controller.signal,
      })
      .then((result) => {
        if (!result.isError) {
          return {
            isError: false,
            value: result.value,
            contentPreview: previewOfBlocks(result.content),
          } as const
        }
        return {
          isError: true,
          code: errorCodeOf(result.error),
          message: result.error.message,
        } as const
      })
      .finally(() => clearTimeout(timer))
  }

  private newCallId(): CallId {
    return `td-${Date.now()}-${Math.floor(Math.random() * 1e6)}` as CallId
  }

  private requireSession(sessionId: SessionId): Session {
    const session = this.sessions.get(sessionId as unknown as DshSessionId)
    if (session === undefined) throw new Error(`trajectory-debug: session ${sessionId} not found`)
    return session
  }

  /** The nearest turn/end at or below `seq` (fork requires a turn boundary). */
  private normalizeBoundary(session: DebugSession, seq: number): number {
    let boundary = 0
    for (const event of session.events) {
      if (event.seq > seq) break
      if (event.type === 'turn/end') boundary = event.seq
    }
    return boundary
  }
}

/** Plugin entry. Every registration is effect-owned: unload withdraws all.
 * `config` comes from the bundle's cordis.patch.yml row.
 *
 * NOTE: the `trajectoryDebug` service registration happens inside the
 * `Service` constructor (`super(ctx, 'trajectoryDebug')`) — cordis registers
 * it on the constructing fiber and tears it down with the fiber. Do NOT call
 * `ctx.provide('trajectoryDebug', …)` here again (double registration). */
export function apply(ctx: Context, config: TrajectoryDebugHostConfig = {}): void {
  ctx.effect(() => {
    const provider = new TrajectoryDebugProvider(ctx, config)
    const disposers: Array<() => void> = []
    disposers.push(provider.install(ctx))

    const projections = registerTrajectoryDebugProjections(ctx)
    if (projections !== undefined) disposers.push(projections)

    const commands = registerTrajectoryDebugCommands(ctx, {
      summarizeTrajectory,
      summarizePerf,
    })
    if (commands !== undefined) disposers.push(commands)

    if (config.enableModelTools === true && ctx.tools !== undefined) {
      disposers.push(
        registerTrajectoryModelTools(ctx, {
          resolveSession: (sessionId) => {
            const session = ctx.sessions.get(sessionId as never)
            return session === undefined ? undefined : adaptSession(session)
          },
        }),
      )
    }

    // Browser RPC transport: webserver custom route (typert-free channel) for
    // the replay/breakpoint/intervention/compare browser panels.
    const transport = registerTrajectoryDebugTransport(ctx, provider)
    if (transport !== undefined) disposers.push(transport)

    // Boot signal for logs (also used by load smoke tests). Best-effort:
    // `ctx.logger` is a callable LoggerService (`ctx.logger(name).info`).
    try {
      const logger = (ctx as { logger?: unknown }).logger as
        | ((name: string) => { info?: (message: string) => void })
        | undefined
      logger?.('trajectory-debug')?.info?.('host provider loaded')
    } catch {
      // logging must never fail the boot
    }

    return () => {
      provider.dispose()
      for (const dispose of disposers) dispose()
    }
  })
}

function errorCodeOf(failure: ToolFailure): string {
  const info = failure.info as { code?: string; name?: string } | undefined
  return info?.code ?? info?.name ?? 'TOOL_FAILURE'
}

/** Extract a text preview from content blocks (defensive: blocks are
 * merge-extensible; only the text form is consumed here). */
function previewOfBlocks(content: readonly unknown[]): string | undefined {
  const texts = content
    .filter((b): b is { type?: string; text?: unknown } => typeof b === 'object' && b !== null)
    .filter((b) => b.type === 'text' || b.type === undefined)
    .map((b) => (typeof b.text === 'string' ? b.text : ''))
  return texts.join('\n') || undefined
}
