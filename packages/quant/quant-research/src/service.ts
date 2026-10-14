/**
 * The quant-research Remote face service: serves account state and the
 * account list to the browser panel via Typert RPC. Read-only: every
 * mutation goes through the model-facing tools with their own approval
 * flows, so the Remote surface cannot bypass the compliance gate.
 * @module @deepseek-ai/dsh-quant-research/service
 */

/* v8 ignore start -- the Typert service face is exercised through the Remote integration tests (web browser mount), not the unit suite. */
import { Context, Service } from '@deepseek-ai/cordis'
import { TypertRemoteService, Remote } from '@deepseek-ai/dsh-typert-protocol'
import type { Domain } from '@deepseek-ai/dsh-storage-domain'
import { quantResearchDomainSpec } from './domain/spec.ts'
import { AccountId, ResultSnapshotId } from './domain/spec.ts'
import type { Account, ResearchNote, ResultSnapshot } from './domain/spec.ts'
import type {
  AccountListValue, AccountRef, AccountSummaryValue, EquityCurveValue, NoteListValue,
  NoteSummaryValue, ResultSnapshotSummaryValue, SnapshotListValue,
} from './types.ts'
export type {
  AccountListValue, AccountRef, AccountSummaryValue, EquityCurveValue, NoteListValue,
  NoteSummaryValue, ResultSnapshotSummaryValue, SnapshotListValue,
} from './types.ts'

declare module '@deepseek-ai/cordis' {
  interface Context {
    /** The quant-research Remote-face service, mounted by this plugin. */
    quantResearch: QuantResearchService
  }
}

/** Domain type alias for the quant-research service. */
type QuantDomain = Domain<typeof quantResearchDomainSpec>

/**
 * Storage-backed quant-research Remote service. Opens the domain at init,
 * serves read-only account data to the browser panel.
 */
export class QuantResearchService extends TypertRemoteService {
  static inject = ['storageDomain'] as const

  private domain: QuantDomain | undefined

  /**
   * Share the caller-owned domain when one is handed in; otherwise open the
   * domain here and own its lifetime. The plugin body (which already opened
   * the domain for the tool layer) passes its handle, so the Remote face and
   * the tools read one facility instance — the domain facility is
   * single-open per name.
   * @param sharedDomain - an already-open domain handle the caller owns.
   */
  constructor(ctx: Context, sharedDomain?: QuantDomain) {
    super(ctx, 'quantResearch')
    this.shared = sharedDomain !== undefined
    if (this.shared) {
      this.domain = sharedDomain
    }
  }

  private readonly shared: boolean

  /** Open the domain (when not shared) and bind its lifetime to this fiber. */
  protected async [Service.init](): Promise<void> {
    if (this.shared) return
    const domain = await this.ctx.storageDomain.open(quantResearchDomainSpec)
    this.ctx.effect(() => async () => {
      this.domain = undefined
      await domain.close()
    }, 'quant-research.domainClose')
    this.domain = domain
  }

  /** Authoritative domain, valid after init; a miss is a broken lifecycle. */
  requireDomain(): QuantDomain {
    if (this.domain === undefined) {
      throw new Error('quant-research: durable domain is not initialized')
    }
    return this.domain
  }

  /**
   * List all virtual accounts, projected to wire summaries.
   */
  @Remote('listAccounts')
  async listAccountsRemote(): Promise<AccountListValue> {
    const domain = this.requireDomain()
    const accounts: AccountSummaryValue[] = []
    for (const [, account] of domain.table('accounts').entries()) {
      accounts.push(projectAccount(account))
    }
    return { accounts: accounts.sort((a, b) => a.name.localeCompare(b.name)) }
  }

  /**
   * Read one account's full state.
   */
  @Remote('getAccountState')
  async getAccountStateRemote(ref: AccountRef): Promise<AccountSummaryValue> {
    const domain = this.requireDomain()
    const table = domain.table('accounts')
    let account: Account | undefined
    if (ref.account_id !== undefined) {
      account = table.get(AccountId(ref.account_id))
    }
    if (account === undefined && ref.name !== undefined) {
      for (const [, a] of table.entries()) {
        if (a.name === ref.name) { account = a; break }
      }
    }
    if (account === undefined) {
      throw new Error(`未找到账户：${ref.account_id ?? ref.name ?? '(未指定)'}`)
    }
    return projectAccount(account)
  }

  /**
   * List research notes, newest first, projected to wire summaries.
   */
  @Remote('listNotes')
  async listNotesRemote(): Promise<NoteListValue> {
    const domain = this.requireDomain()
    const notes: NoteSummaryValue[] = []
    for (const [, note] of domain.table('research_notes').entries()) {
      notes.push(projectNote(note))
    }
    return { notes: notes.sort((a, b) => b.created_at - a.created_at) }
  }

  /**
   * List persisted backtest snapshots, newest first, without equity points.
   */
  @Remote('listResultSnapshots')
  async listResultSnapshotsRemote(): Promise<SnapshotListValue> {
    const domain = this.requireDomain()
    const snapshots: ResultSnapshotSummaryValue[] = []
    for (const [, snapshot] of domain.table('result_snapshots').entries()) {
      snapshots.push(projectSnapshot(snapshot))
    }
    return { snapshots: snapshots.sort((a, b) => b.created_at - a.created_at) }
  }

  /**
   * Read one snapshot's equity curve.
   */
  @Remote('getEquityCurve')
  async getEquityCurveRemote(ref: { result_id: string }): Promise<EquityCurveValue> {
    const domain = this.requireDomain()
    const snapshot = domain.table('result_snapshots').get(ResultSnapshotId(ref.result_id))
    if (snapshot === undefined) {
      throw new Error(`未找到回测快照：${ref.result_id}`)
    }
    return {
      result_id: snapshot.id,
      symbol: snapshot.symbol,
      equity: snapshot.equity.map(point => ({ date: point.date, value: point.value })),
    }
  }
}

/** Project a domain ResearchNote record to the wire summary shape. */
function projectNote(note: ResearchNote): NoteSummaryValue {
  return {
    note_id: note.id,
    title: note.title,
    body: note.body,
    symbol: note.symbol ?? null,
    tags: [...note.tags],
    created_at: note.created_at,
  }
}

/** Project a domain ResultSnapshot record to the wire summary shape (no equity points). */
function projectSnapshot(snapshot: ResultSnapshot): ResultSnapshotSummaryValue {
  return {
    result_id: snapshot.id,
    symbol: snapshot.symbol,
    params: { ...snapshot.params },
    metrics: { ...snapshot.metrics },
    created_at: snapshot.created_at,
  }
}

/** Project a domain Account record to the wire summary shape. */
function projectAccount(account: Account): AccountSummaryValue {
  const equity = account.cash
    + account.positions.reduce((sum, p) => sum + p.shares * p.avg_cost, 0)
  return {
    account_id: account.id,
    name: account.name,
    cash: Math.round(account.cash * 100) / 100,
    initial_cash: account.initial_cash,
    equity: Math.round(equity * 100) / 100,
    positions: account.positions.map(p => ({
      symbol: p.symbol,
      shares: p.shares,
      avg_cost: p.avg_cost,
      market_value: Math.round(p.shares * p.avg_cost * 100) / 100,
    })),
  }
}
/* v8 ignore stop */
