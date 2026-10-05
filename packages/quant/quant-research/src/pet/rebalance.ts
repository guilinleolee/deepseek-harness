/**
 * PET rebalance math, TypeScript side: target weights → simulated fills over
 * a virtual account. Pure and deterministic — the same targets, cash,
 * positions, and prices always produce the same trades. Sells settle before
 * buys so the plan funds itself when it can; any plan that still cannot
 * cover a buy (cash + proceeds, including fees) is rejected, never partially
 * filled. Long-only: negative weights are a validation error, and the
 * red-line caps (no leverage) live in the compliance gate.
 * @module @deepseek-ai/dsh-quant-research/pet/rebalance
 */

import { QuantError } from '../errors.ts'
import type { KlineBar } from '../pdat/datasource.ts'

/** One target of a rebalance plan. */
export interface RebalanceTarget {
  /** The symbol to rebalance. */
  readonly symbol: string
  /** The target weight of current equity in `[0, 1]`. */
  readonly weight: number
}

/** One current position of the account. */
export interface PetPosition {
  /** The symbol held. */
  readonly symbol: string
  /** Shares held. */
  readonly shares: number
  /** Average cost per share. */
  readonly avg_cost: number
}

/** One simulated fill produced by the rebalance. */
export interface RebalanceTrade {
  /** The symbol traded. */
  readonly symbol: string
  /** Fill side. */
  readonly side: 'buy' | 'sell'
  /** Shares filled. */
  readonly shares: number
  /** Fill price (the symbol's latest close). */
  readonly price: number
  /** Fee charged for this fill. */
  readonly fee: number
}

/** Inputs of one rebalance computation. */
export interface RebalanceInput {
  /** Account cash before the rebalance. */
  readonly cash: number
  /** Current long positions. */
  readonly positions: readonly PetPosition[]
  /** The target weights. */
  readonly targets: readonly RebalanceTarget[]
  /** Latest close per symbol — must cover every target and held symbol. */
  readonly prices: Readonly<Record<string, number>>
  /** Per-trade fee rate. */
  readonly feeRate: number
}

/** The computed plan: fills in execution order plus the post-trade cash. */
export interface RebalancePlan {
  /** The fills, sells first then buys. */
  readonly trades: readonly RebalanceTrade[]
  /** Cash after every fill settles (fees included). */
  readonly cashAfter: number
}

/** Tolerance for share and cash rounding (fractional shares to 1e-6). */
const EPS = 1e-6

/**
 * Validate one rebalance plan's inputs: targets are unique, non-negative,
 * leverage-free (their sum stays within `[0, 1]` within tolerance), every
 * traded symbol has a price, and fee rate is sane.
 * @param input - the rebalance inputs.
 * @throws {@link QuantError} code `DATA` on any invalid input.
 */
export function validateRebalanceInput(input: RebalanceInput): void {
  const seen = new Set<string>()
  let total = 0
  for (const target of input.targets) {
    if (seen.has(target.symbol)) {
      throw new QuantError('DATA', `调仓目标重复：${target.symbol}`)
    }
    seen.add(target.symbol)
    if (!Number.isFinite(target.weight) || target.weight < 0) {
      throw new QuantError('DATA', `目标权重必须是非负数值，${target.symbol} 收到 ${String(target.weight)}`)
    }
    total += target.weight
    if (input.prices[target.symbol] === undefined) {
      throw new QuantError('DATA', `缺少 ${target.symbol} 的最新价格，无法生成调仓单`)
    }
  }
  if (total > 1 + EPS) {
    throw new QuantError('RISK', `目标权重合计 ${total.toFixed(4)} 超过 1（不允许杠杆）`)
  }
  for (const position of input.positions) {
    if (input.prices[position.symbol] === undefined) {
      throw new QuantError('DATA', `缺少持仓 ${position.symbol} 的最新价格，无法估值`)
    }
    if (!(input.prices[position.symbol] as number > 0)) {
      throw new QuantError('DATA', `${position.symbol} 的最新价格必须为正数`)
    }
  }
  if (!Number.isFinite(input.feeRate) || input.feeRate < 0 || input.feeRate > 0.05) {
    throw new QuantError('DATA', `手续费率必须是 0-0.05 之间的数值，收到 ${String(input.feeRate)}`)
  }
}

/**
 * Compute the simulated fills for one rebalance. Current equity is valued at
 * the provided prices; every target gets `weight × equity` of value (symbols
 * held but absent from the targets are fully sold); sells settle first so a
 * plan funded by its own sales goes through, and a buy the remaining cash
 * cannot cover (fees included) rejects the whole plan.
 * @param input - cash, positions, targets, prices, and fee rate.
 * @returns the fills in execution order and the post-trade cash.
 * @throws {@link QuantError} code `DATA` when the plan is invalid or
 *   infeasible, `RISK` when the weights imply leverage.
 */
export function computeRebalanceTrades(input: RebalanceInput): RebalancePlan {
  validateRebalanceInput(input)
  const positionBySymbol = new Map(input.positions.map(position => [position.symbol, position]))
  const symbols = new Set<string>([
    ...input.targets.map(target => target.symbol),
    ...input.positions.map(position => position.symbol),
  ])
  const equity = input.cash
    + input.positions.reduce((sum, position) => sum + position.shares * (input.prices[position.symbol] as number), 0)

  const deltas: Array<{ symbol: string; delta: number; price: number }> = []
  for (const symbol of symbols) {
    const weight = input.targets.find(target => target.symbol === symbol)?.weight ?? 0
    const shares = positionBySymbol.get(symbol)?.shares ?? 0
    const price = input.prices[symbol] as number
    const delta = weight * equity - shares * price
    if (Math.abs(delta) > price * EPS) deltas.push({ symbol, delta, price })
  }
  deltas.sort((left, right) => left.delta - right.delta)

  let cash = input.cash
  const trades: RebalanceTrade[] = []
  for (const { symbol, delta, price } of deltas) {
    const shares = Math.abs(delta) / price
    const side: 'buy' | 'sell' = delta >= 0 ? 'buy' : 'sell'
    if (side === 'sell') {
      /* v8 ignore next */
      const held = positionBySymbol.get(symbol)?.shares ?? 0
      /* v8 ignore next 3 */
      if (shares > held + EPS) {
        throw new QuantError('DATA', `现金与持仓不足以完成调仓：${symbol} 需卖出 ${shares.toFixed(4)} 股，仅持有 ${held.toFixed(4)} 股`)
      }
    }
    const fee = shares * price * input.feeRate
    cash -= delta + fee
    if (cash < -EPS) {
      throw new QuantError('DATA', `现金不足以完成调仓（含手续费）：${symbol} 买入后将透支 ${Math.abs(cash).toFixed(2)}`)
    }
    trades.push({ symbol, side, shares: Math.round(shares * 1e6) / 1e6, price, fee })
  }
  return { trades, cashAfter: Math.max(cash, 0) }
}

/**
 * Latest close of one kline series (the execution price convention for PET
 * fills).
 * @param bars - the series, oldest first.
 * @returns the last close.
 */
export function latestClose(bars: readonly KlineBar[]): number {
  const last = bars[bars.length - 1]
  if (last === undefined) {
    throw new QuantError('DATA', 'K线序列为空，无法取执行价')
  }
  return last.close
}
