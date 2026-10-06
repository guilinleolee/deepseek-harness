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
import { AccountId } from './domain/spec.ts'
import type { Account } from './domain/spec.ts'

/** Domain type alias for the quant-research service. */
type QuantDomain = Domain<typeof import('./domain/spec.ts').quantResearchDomainSpec>

/** Account summary projected to the wire (no internal bookkeeping fields). */
export interface AccountSummaryValue {
  readonly account_id: string
  readonly name: string
  readonly cash: number
  readonly initial_cash: number
  readonly equity: number
  readonly positions: readonly { readonly symbol: string; readonly shares: number; readonly avg_cost: number; readonly market_value: number }[]
}

/**
 * Storage-backed quant-research Remote service. Opens the domain at init,
 * serves read-only account data to the browser panel.
 */
export class QuantResearchService extends TypertRemoteService {
  static inject = ['storageDomain'] as const

  private domain: QuantDomain | undefined

  /**
   * @param ctx - host context providing storage.
   */
  constructor(ctx: Context) {
    super(ctx, 'quantResearch')
  }

  /** Open the domain and bind its lifetime to this fiber. */
  protected async [Service.init](): Promise<void> {
    const domain = await this.ctx.storageDomain.open(
      (await import('./domain/spec.ts')).quantResearchDomainSpec,
    )
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
  async listAccountsRemote(): Promise<{ accounts: AccountSummaryValue[] }> {
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
  async getAccountStateRemote(ref: { account_id?: string; name?: string }): Promise<AccountSummaryValue> {
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
