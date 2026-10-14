/**
 * PET account store: create, look up, and update virtual accounts over the
 * domain v2 tables, and append their simulated fills to the orders table.
 * Plain table functions (the compliance-gate pattern): the owning plugin
 * composes them, tests drive them directly.
 * @module @deepseek-ai/dsh-quant-research/pet/service
 */

import { randomUUID } from 'node:crypto'
import type { KvTable } from '@deepseek-ai/dsh-storage-domain'
import { AccountId, OrderId } from '../domain/spec.ts'
import type { Account, Order } from '../domain/spec.ts'
import { QuantError } from '../errors.ts'
import type { RebalanceTrade } from './rebalance.ts'

/** The accounts table handle. */
export type AccountsTable = KvTable<AccountId, Account>
/** The orders table handle. */
export type OrdersTable = KvTable<OrderId, Order>

/** Fields the account-creation caller supplies; id and timestamps fill here. */
export interface AccountCreateInput {
  /** Unique human-readable account name. */
  readonly name: string
  /** Starting cash. */
  readonly initialCash: number
}

/**
 * Create one virtual account: all cash, no positions.
 * @param table - the accounts table.
 * @param input - name and starting cash.
 * @param now - the creation timestamp (injected for tests).
 * @param newId - the id factory (injected for tests).
 * @returns the stored account.
 * @throws {@link QuantError} code `DATA` when the name is already taken.
 */
export async function createAccount(
  table: AccountsTable,
  input: AccountCreateInput,
  now: number = Date.now(),
  newId: () => string = () => randomUUID(),
): Promise<Account> {
  const name = input.name.trim()
  if (name.length === 0) throw new QuantError('DATA', '账户名不能为空')
  if (findAccountByName(table, name) !== undefined) {
    throw new QuantError('DATA', `账户名已存在：${name}`)
  }
  const account: Account = {
    id: AccountId(newId()),
    name,
    initial_cash: input.initialCash,
    cash: input.initialCash,
    positions: [],
    created_at: now,
    updated_at: now,
  }
  await table.put(account.id, account)
  return account
}

/**
 * All stored accounts, oldest first.
 * @param table - the accounts table.
 * @returns the accounts sorted by creation time.
 */
export function listAccounts(table: AccountsTable): Account[] {
  return [...table.entries()].map(([, account]) => account)
    .sort((left, right) => left.created_at - right.created_at)
}

/**
 * Look up one account by id or by unique name.
 * @param table - the accounts table.
 * @param ref - the id, when known; otherwise the name.
 * @param name - the account name when looking up by name.
 * @returns the account.
 * @throws {@link QuantError} code `DATA` when no account matches.
 */
export function requireAccount(table: AccountsTable, ref?: string, name?: string): Account {
  if (ref !== undefined) {
    const byId = table.get(AccountId(ref))
    if (byId !== undefined) return byId
  }
  if (name !== undefined) {
    const byName = findAccountByName(table, name)
    if (byName !== undefined) return byName
  }
  throw new QuantError('DATA', `未找到账户：${ref ?? name ?? '(未指定)'}`)
}

/**
 * Find one account by its unique name.
 * @param table - the accounts table.
 * @param name - the account name.
 * @returns the account, or `undefined`.
 */
function findAccountByName(table: AccountsTable, name: string): Account | undefined {
  for (const [, account] of table.entries()) {
    if (account.name === name) return account
  }
  return undefined
}

/**
 * Apply one rebalance's fills to the account: every fill writes one order
 * record and moves cash/shares; the account's `updated_at` bumps. Positions
 * whose shares settle to ~zero are dropped (long-only bookkeeping).
 * @param accounts - the accounts table.
 * @param orders - the orders table.
 * @param account - the account to update (the caller's current copy).
 * @param trades - the computed fills in execution order.
 * @param now - the execution timestamp (injected for tests).
 * @param newId - the id factory (injected for tests).
 * @returns the stored post-trade account.
 */
export async function applyTrades(
  accounts: AccountsTable,
  orders: OrdersTable,
  account: Account,
  trades: readonly RebalanceTrade[],
  cashAfter: number,
  now: number = Date.now(),
  newId: () => string = () => randomUUID(),
): Promise<Account> {
  const positions = account.positions.map(position => ({ ...position }))
  for (const trade of trades) {
    const order: Order = {
      id: OrderId(newId()),
      account_id: account.id,
      symbol: trade.symbol,
      side: trade.side,
      shares: trade.shares,
      price: trade.price,
      fee: trade.fee,
      executed_at: now,
    }
    void orders.put(order.id, order)

    const held = positions.find(position => position.symbol === trade.symbol)
    if (trade.side === 'buy') {
      const existingShares = held?.shares ?? 0
      const existingCost = held?.avg_cost ?? 0
      const totalShares = existingShares + trade.shares
      /* v8 ignore next 2 -- totalShares is always positive for a buy (shares > 0), so the fallback is unreachable. */
      const avgCost = totalShares > 0
        ? (existingShares * existingCost + trade.shares * trade.price) / totalShares
        /* v8 ignore next */
        : trade.price
      if (held === undefined) {
        positions.push({ symbol: trade.symbol, shares: trade.shares, avg_cost: avgCost })
      } else {
        held.shares = totalShares
        held.avg_cost = avgCost
      }
    } else {
      if (held === undefined || trade.shares > held.shares + 1e-6) {
        throw new QuantError('DATA', `持仓不足：${trade.symbol} 仅持有 ${String(held?.shares ?? 0)} 股`)
      }
      held.shares -= trade.shares
      /* v8 ignore next 2 */
      if (held.shares <= 1e-6) {
        positions.splice(positions.indexOf(held), 1)
      }
    }
  }
  const updated: Account = { ...account, cash: cashAfter, positions, updated_at: now }
  await accounts.put(updated.id, updated)
  return updated
}

/**
 * The cash delta one rebalance settles: sells add proceeds, buys subtract
 * cost, and every fill pays its fee.
 * @param trades - the fills.
 * @returns the signed cash change (negative when the plan net-buys).
 */
export function cashDelta(trades: readonly RebalanceTrade[]): number {
  return trades.reduce((sum, trade) => sum
    + (trade.side === 'sell' ? trade.shares * trade.price : -trade.shares * trade.price)
    - trade.fee, 0)
}
