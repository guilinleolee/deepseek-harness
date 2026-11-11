"""Patcher P2-PET-2: compliance weight caps + PET tools into tools.ts + exports (worktree)."""
import io

WT = 'D:/dsh-wt-quant-p1/packages/quant/quant-research/src/'

def patch(path, old, new):
    s = io.open(WT + path, encoding='utf-8').read()
    assert old in s, f'{path}: missing {old[:70]!r}'
    s = s.replace(old, new)
    io.open(WT + path, 'w', encoding='utf-8', newline='\n').write(s)
    print('patched', path)

# ── compliance.ts: weight caps (no leverage / long-only) + inspector ──
patch('compliance.ts',
"""/** Hard bounds for a stress shock's total magnitude; not configurable. */
export const SHOCK_LIMITS = { min: 0.01, max: 0.5, default: 0.1 } as const""",
"""/** Hard bounds for a stress shock's total magnitude; not configurable. */
export const SHOCK_LIMITS = { min: 0.01, max: 0.5, default: 0.1 } as const
/** Hard cap for one rebalance target weight (no single-name overconcentration); not configurable. */
export const WEIGHT_POSITION_HARD_LIMIT = 1
/** Hard cap for the rebalance targets' weight sum (no leverage); not configurable. */
export const WEIGHT_TOTAL_HARD_LIMIT = 1""")

patch('compliance.ts',
"""/**
 * Decide one tool call against the red lines.""",
"""/**
 * Red line 6 (no leverage, long-only): every rebalance target weight stays
 * within `[0, 1]` and the weights' sum stays within `[0, 1]` — the virtual
 * book never goes short or levered, regardless of what the schema accepts.
 * @param args - raw tool arguments.
 * @returns the verdict for the weight-cap rule.
 */
export function inspectWeightCaps(args: RawArgs): ComplianceVerdict {
  const targets = (args as Record<string, unknown>)['targets']
  if (targets === undefined) return { kind: 'allow' }
  if (!Array.isArray(targets)) {
    return { kind: 'deny', reason: 'targets 必须是目标权重列表（合规硬上限：仅限多头、无杠杆）' }
  }
  let total = 0
  for (const item of targets) {
    const weight = (item as Record<string, unknown> | null)?.['weight']
    if (typeof weight !== 'number' || !Number.isFinite(weight) || weight < 0 || weight > WEIGHT_POSITION_HARD_LIMIT) {
      return {
        kind: 'deny',
        reason: `每个目标权重必须是 0-${String(WEIGHT_POSITION_HARD_LIMIT)} 之间的数值（合规硬上限：仅限多头、无杠杆）`,
      }
    }
    total += weight
  }
  if (total > WEIGHT_TOTAL_HARD_LIMIT + 1e-9) {
    return { kind: 'deny', reason: `目标权重合计 ${total.toFixed(4)} 超过 ${String(WEIGHT_TOTAL_HARD_LIMIT)}（合规硬上限：不允许杠杆）` }
  }
  return { kind: 'allow' }
}

/**
 * Decide one tool call against the red lines.""")

patch('compliance.ts',
"""  quant_stress_test: [inspectBrokerMarkers, inspectBarCap, inspectShockCap],
})""",
"""  quant_stress_test: [inspectBrokerMarkers, inspectBarCap, inspectShockCap],
  quant_execute_rebalance: [inspectBrokerMarkers, inspectWeightCaps],
})""")

# ── tools.ts: three PET builders + registration (8 tools) ──
patch('tools.ts',
"""import {
  annualVolatility, dailyReturns, historicalCVar, historicalVar, maxDrawdown, shockBars,
  validateStressParams,
} from './prt/risk.ts'""",
"""import {
  annualVolatility, dailyReturns, historicalCVar, historicalVar, maxDrawdown, shockBars,
  validateStressParams,
} from './prt/risk.ts'
import {
  applyTrades, computeRebalanceTrades, createAccount, latestClose, listAccounts, requireAccount,
} from './pet/service.ts'
import type { AccountsTable, OrdersTable } from './pet/service.ts'
import { computeRebalanceTrades as computePlan } from './pet/rebalance.ts'
import type { RebalanceTarget } from './pet/rebalance.ts'""")

patch('tools.ts',
"""/** The tool layer's resolved dependencies. */
export interface QuantToolDeps {
  /** The resolved plugin configuration. */
  readonly config: ResolvedConfig
  /** The kernel client. */
  readonly kernel: QuantKernelClient
  /** The data-source circuit breaker. */
  readonly breaker: DataSourceBreaker
}""",
"""/** The ask face the plugin borrows from the user-approval capability. */
export interface ApprovalAsk {
  /**
   * Ask the composed answerers to decide one request.
   * @param req - agent, tool identity, reason, and signal.
   * @returns the closed outcome; `'allowed-once'` is the only grant.
   */
  request(req: {
    readonly agent: NonNullable<ToolExecution['agent']>
    readonly toolName: string
    readonly reason: string
    readonly signal?: AbortSignal
  }): Promise<'allowed-once' | 'rejected' | 'cancelled' | 'unavailable'>
}

/** The tool layer's resolved dependencies. */
export interface QuantToolDeps {
  /** The resolved plugin configuration. */
  readonly config: ResolvedConfig
  /** The kernel client. */
  readonly kernel: QuantKernelClient
  /** The data-source circuit breaker. */
  readonly breaker: DataSourceBreaker
  /** The PET virtual-account tables (domain v2). */
  readonly accounts: AccountsTable
  /** The simulated-fill table (domain v2). */
  readonly orders: OrdersTable
  /** The user-approval ask face, when the host composes it. */
  readonly approval?: ApprovalAsk
}""")

# three builders inserted before register doc
patch('tools.ts',
"""/**
 * Register the research tools on one context.""",
"""/**
 * Build the account-creation tool.
 * @param deps - the tool layer dependencies.
 * @returns the tool definition.
 */
export function accountCreateTool(deps: QuantToolDeps): ToolDefinition {
  return defineTool({
    name: 'quant_account_create',
    description: '创建一个虚拟研究账户（PET，模拟盘）：仅用于记录模拟成交，没有任何实盘通道。',
    parameters: {
      name: { type: 'string', required: true, description: '账户名，需唯一' },
      initial_cash: { type: 'number', description: `初始资金，默认 ${String(DEFAULT_CASH_LIMITS.default)}` },
    },
    output: { schema: ENVELOPE_SCHEMA, render: (_args, value) => renderAccount(value) },
    timeoutMs: deps.config.toolTimeoutMs,
    presentCall: (args) => ({ card: 'generic' as const, title: `创建虚拟账户：${args.name}` }),
    async execute(args) {
      return envelopeFrom('ping', execNoop(), async () => {
        const account = await createAccount(
          deps.accounts,
          { name: args.name, initialCash: args.initial_cash ?? deps.config.defaultCash },
        )
        return { account_id: account.id, name: account.name, cash: account.cash }
      })
    },
  })
}

/**
 * Build the account-state tool.
 * @param deps - the tool layer dependencies.
 * @returns the tool definition.
 */
export function accountStateTool(deps: QuantToolDeps): ToolDefinition {
  return defineTool({
    name: 'quant_account_state',
    description: '查询虚拟研究账户（PET，模拟盘）：现金、持仓（股数/成本/最新价/市值）与总权益。',
    parameters: {
      account_id: { type: 'string', description: '账户 id；与 account_name 二选一' },
      account_name: { type: 'string', description: '账户名；与 account_id 二选一' },
    },
    output: { schema: ENVELOPE_SCHEMA, render: (_args, value) => renderAccount(value) },
    timeoutMs: deps.config.toolTimeoutMs,
    presentCall: (args) => ({ card: 'generic' as const, title: `查询账户：${String(args.account_name ?? args.account_id ?? '?')}` }),
    async execute(args) {
      return envelopeFrom('ping', execNoop(), async () => {
        const account = requireAccount(deps.accounts, args.account_id, args.account_name)
        let cash = account.cash
        let equity = cash
        const positions = account.positions.map((position) => {
          const shares = position.shares
          const value = shares * (position.avg_cost > 0 ? position.avg_cost : 0)
          equity += value
          return { symbol: position.symbol, shares, avg_cost: position.avg_cost, market_value: Math.round(value * 100) / 100 }
        })
        return { account_id: account.id, name: account.name, cash: Math.round(cash * 100) / 100, positions, equity: Math.round(equity * 100) / 100 }
      })
    },
  })
}

/**
 * Build the rebalance-execution tool: PRT concentration/leverage caps, then
 * the human approval ask, then simulated fills over the virtual account.
 * @param deps - the tool layer dependencies.
 * @returns the tool definition.
 */
export function executeRebalanceTool(deps: QuantToolDeps): ToolDefinition {
  return defineTool({
    name: 'quant_execute_rebalance',
    description: '对虚拟研究账户执行调仓（PET，模拟盘，需人工审核）：校验集中度与杠杆红线后请求人工批准，批准后以最新收盘价模拟成交并记录每一笔模拟单。',
    parameters: {
      account_name: { type: 'string', required: true, description: '账户名' },
      targets: {
        type: 'array', required: true,
        description: '目标权重列表（仅限多头，权重和 ≤ 1；越界由合规校验拒绝）',
        items: {
          type: 'object', required: true, additionalProperties: false,
          properties: {
            symbol: { type: 'string', required: true, description: '标的代码' },
            weight: { type: 'number', required: true, description: '目标权重（0-1）' },
          },
        },
      },
    },
    output: { schema: ENVELOPE_SCHEMA, render: (_args, value) => renderRebalance(value) },
    timeoutMs: deps.config.toolTimeoutMs,
    presentCall: (args) => ({ card: 'generic' as const, title: `调仓审核：${args.account_name}` }),
    async execute(args, exec) {
      return envelopeFrom('ping', exec, async () => {
        if (deps.approval === undefined) {
          throw new QuantError('CONFIG', '调仓需要人工审核：请在组合中加入 @deepseek-ai/dsh-user-approval 插件')
        }
        const targets = (args.targets as ReadonlyArray<{ symbol: string; weight: number }>).map(target => ({ ...target }))
        const account = requireAccount(deps.accounts, undefined, args.account_name)
        const prices: Record<string, number> = {}
        for (const symbol of new Set<string>([
          ...targets.map(target => target.symbol),
          ...account.positions.map(position => position.symbol),
        ])) {
          const series = await fetchKline(deps.kernel, deps.breaker, {
            source: deps.config.dataSource,
            symbol,
            bars: 5,
            retries: deps.config.sourceMaxRetries,
            cacheDir: deps.config.cacheDir,
            signal: exec.signal,
          })
          prices[symbol] = latestClose(series)
        }
        const plan = computeRebalanceTrades({
          cash: account.cash,
          positions: account.positions,
          targets,
          prices,
          feeRate: deps.config.feeRate,
        })
        if (exec.agent === undefined) {
          throw new QuantError('CONFIG', '调仓审核需要 agent 会话（approval 以回合为单位记账）')
        }
        const outcome = await deps.approval.request({
          agent: exec.agent,
          toolName: 'quant_execute_rebalance',
          reason: `对虚拟账户「${account.name}」执行调仓：${targets.map(t => `${t.symbol} ${(t.weight * 100).toFixed(1)}%`).join('、')}（模拟盘，仅供研究）`,
          signal: exec.signal,
        })
        if (outcome !== 'allowed-once') {
          throw new QuantError('RISK', `调仓方案未获批准（${outcome}），已放弃执行；模拟盘不会在未经审核的情况下变动`)
        }
        const updated = await applyTrades(deps.accounts, deps.orders, account, plan.trades, plan.cashAfter)
        return {
          account_id: updated.id,
          account_name: updated.name,
          executed: plan.trades,
          cash_after: Math.round(plan.cashAfter * 100) / 100,
        }
      })
    },
  })
}

/**
 * Register the research tools on one context.""")

# registration: 5 → 8
patch('tools.ts',
"""  const tools = [
    getKlineTool(deps),
    computeIndicatorTool(deps),
    runBacktestTool(deps),
    assessRiskTool(deps),
    stressTestTool(deps),
  ]""",
"""  const tools = [
    getKlineTool(deps),
    computeIndicatorTool(deps),
    runBacktestTool(deps),
    assessRiskTool(deps),
    stressTestTool(deps),
    accountCreateTool(deps),
    accountStateTool(deps),
    executeRebalanceTool(deps),
  ]""")

# render helpers for account/rebalance (insert before "Build the kline tool")
patch('tools.ts',
"""/**
 * Build the kline tool.""",
"""/**
 * Render the account envelope: cash, positions, and equity.
 * @param value - the tool result value.
 * @returns the model-facing text blocks.
 */
function renderAccount(value: unknown): { type: 'text'; text: string }[] {
  const failed = failureLine(value)
  if (failed !== undefined) return [{ type: 'text', text: `${failed}\\n\\n${DISCLAIMER}` }]
  const data = successData(value) as {
    account_id?: string
    name?: string
    cash?: number
    equity?: number
    positions?: { symbol: string; shares: number; market_value: number }[]
  } | undefined
  if (data?.name === undefined || data.cash === undefined) {
    return [{ type: 'text', text: `账户信息为空。\\n\\n${DISCLAIMER}` }]
  }
  const positionLines = (data.positions ?? []).map(position =>
    `- ${position.symbol}：${String(position.shares)} 股，市值 ${String(position.market_value)}`
  )
  const equityLine = data.equity === undefined ? '' : `\\n总权益 ${String(data.equity)}`
  return [{
    type: 'text',
    text: `虚拟账户「${data.name}」：现金 ${String(data.cash)}\\n${positionLines.join('\\n')}${equityLine}`
      + `\\n\\n（模拟盘记录仅供研究参考，不构成投资建议）`,
  }]
}

/**
 * Render the rebalance-execution envelope: the fills and the post-trade cash.
 * @param value - the tool result value.
 * @returns the model-facing text blocks.
 */
function renderRebalance(value: unknown): { type: 'text'; text: string }[] {
  const failed = failureLine(value)
  if (failed !== undefined) return [{ type: 'text', text: `${failed}\\n\\n${DISCLAIMER}` }]
  const data = successData(value) as {
    account_name?: string
    executed?: { symbol: string; side: string; shares: number; price: number; fee: number }[]
    cash_after?: number
  } | undefined
  if (data?.executed === undefined || data.account_name === undefined) {
    return [{ type: 'text', text: `调仓结果为空。\\n\\n${DISCLAIMER}` }]
  }
  const lines = data.executed.map(fill =>
    `- ${fill.side === 'buy' ? '买入' : '卖出'} ${fill.symbol} ${String(fill.shares)} 股 @ ${String(fill.price)}（费 ${String(fill.fee)}）`
  )
  return [{
    type: 'text',
    text: `虚拟账户「${data.account_name}」调仓完成（模拟成交 ${String(data.executed.length)} 笔）：\\n${lines.join('\\n')}`
      + `\\n现金余额 ${String(data.cash_after ?? '?')}`
      + `\\n\\n（模拟盘记录仅供研究参考，不构成投资建议）`,
  }]
}

/**
 * Build the kline tool.""")

print('tools.ts PET builders done')
