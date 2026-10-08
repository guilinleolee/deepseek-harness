# @deepseek-ai/dsh-quant-research

English | [中文](README.zh.md)

Quant research for DSH: kernel-backed market data, deterministic TypeScript indicators, the daily SMA-cross backtester with its risk/stress/factor/PET suite, and jobs-runtime parameter optimization — all behind a research-only compliance gate. The plugin registers sixteen model-facing tools (`quant_get_kline`, `quant_compute_indicator`, `quant_run_backtest`, `quant_assess_risk`, `quant_stress_test`, the PET account tools, the factor/IC tools, the notes/report tools, `quant_compare_backtests`, `quant_research_report`, and `quant_optimize_params`), opens the `quant_research` storage domain for the denial audit trail, and runs its Python compute kernel as one short-lived managed subprocess per request. It contains no real-broker path of any kind: the red line is enforced by a `tools/pre-execute` listener and stated in every tool output.

## Installation

```sh
dsh plugin --profile web add @deepseek-ai/dsh-quant-research
```

The bundle patch inserts both rows — this plugin and the `@deepseek-ai/dsh-client-ui-quant-research` panel — so one command installs the whole feature. The kernel needs a Python 3 interpreter on the host (`kernelCommand`, below); phase-1 data works fully offline through the synthetic source.

## Configuration

All fields are optional and live under the bundle row's `config:`; invalid values fail plugin load.

- `dataSource` — `synthetic` (default; a deterministic, symbol-seeded offline walk) or `akshare` (live A-share daily data through the kernel; requires `pip install -r kernel-py/requirements.txt`).
- `kernelCommand` — Python interpreter for the kernel; defaults to the platform launcher (`python` on Windows, `python3` elsewhere).
- `cacheDir` — the kernel's kline cache directory; defaults to `<dshHome>/quant-research/cache` (used by the `akshare` source only).
- `toolTimeoutMs` / `kernelRequestTimeoutMs` — the model-facing tool budget and the per-request kernel deadline (kernel deadline must stay below the tool budget).
- `sourceMaxRetries` / `fuseThreshold` — kernel-side fetch retries and the consecutive-failure count that trips the data-source circuit breaker.
- `defaultCash` / `feeRate` — backtest starting cash and per-trade fee rate when a call omits them.

API keys (for example a Tushare token, a later-phase source) never live in the config: they resolve through the credentials capability inside the kernel at request time, and the kernel inherits a scrubbed parent environment.

## Architecture

Module names follow the plugin's research pipeline: `src/pdat` (data access and the circuit breaker), `src/paat` (indicators and factors), `src/pcpt` (backtest driving, reports, and optimization), plus `src/kernel-client` (the subprocess protocol). The TypeScript side validates every argument, owns the breaker state machine, and re-implements the phase-1 indicators deterministically so replayed sessions see identical numbers; the Python kernel (`kernel-py/`) computes the synthetic/akshare klines and runs the backtest simulation as a pure function of the bars it receives. The wire is newline-delimited JSON with a fresh correlation id per request; one request spawns one process, and every exit path — including the cooperative `exec.signal` deadline — ends in the subprocess seam's terminate ladder. There is no self-written kill logic and no long-lived child.

Parameter optimization rides the jobs runtime, not a daemon: `quant_optimize_params` fetches the bars once and runs the whole (fast, slow) grid through one `backtest_grid` kernel request — the same audited simulator re-invoked per combination, metrics only on the wire — inside a cancellable background job started on the host's `ctx.jobs` registry (kind `quant-optimize`). The tool returns the job id immediately; the model collects the ranked markdown report with `job_output` and cancels with `job_kill`. Without a composed jobs runtime the tool fails with a friendly config error instead of degrading to a blocking call.

## Compliance gate (red lines)

One `tools/pre-execute` listener owns enforcement for every `quant_*` call and delegates the rest via `next()`:

1. **Research-only intent** — any argument string carrying a real-trading or broker-API marker (`实盘`, `券商`, `place_order`, `submit_order`, `cancel_order`) is denied with a friendly Chinese reason, at any nesting depth.
2. **Hard caps** — bar counts, backtest cash, fee rates, VaR confidence, stress magnitude, rebalance weights, and the optimization grid (axis bounds, integer steps, the whole fast range strictly below the slow range, and at most 200 combinations, resolved against the same defaults the tool applies) stay within the fixed limits even if a caller smuggles larger values past the schema.
3. **Durable audit** — every denial appends one `compliance_denials` record to the `quant_research` domain (version 1, frozen) with the tool name, reason, agent id, and timestamp; a failed audit write warns and never un-denies.

Each red line has at least one illegal-path unit test, and the keyless snapshot drives a real denial through the assembled composition.

## Tools

| name | what it does |
|---|---|
| `quant_get_kline` | Fetch the latest N daily bars (OHLCV) for one symbol through the kernel. |
| `quant_compute_indicator` | Compute `ma` / `ema` / `macd` / `rsi` / `boll` / `atr` over the fetched closes. |
| `quant_run_backtest` | Run the daily SMA-cross simulation (signal on close, fill at next open, all-in/all-out) and return the equity curve, fills, and metrics. |
| `quant_assess_risk` | Historical-simulation tail risk for one symbol: VaR, CVaR, annualized volatility, and window max drawdown. |
| `quant_stress_test` | Re-run the same backtest over a stressed price path (`crash` overnight gap, `liquidity` cascading slide) and compare baseline vs stressed metrics. |
| `quant_account_create` / `quant_account_state` | Create and read PET virtual accounts (simulated, research-only). |
| `quant_execute_rebalance` | Rebalance a virtual account after concentration checks and a fail-closed human approval ask; fills are simulated at the latest close. |
| `quant_compute_factor` / `quant_factor_ic` | Cross-sectional factors (momentum, volatility, volume ratio, price position) and Spearman IC / Information Ratio. |
| `quant_save_note` / `quant_list_notes` / `quant_export_report` | Durable research notes with symbol/tag filters and a markdown export. |
| `quant_compare_backtests` | Run two parameter sets on the same symbol and compare return, drawdown, and Sharpe side by side. |
| `quant_research_report` | Run one backtest and format the structured markdown research report (parameters, metrics, equity, fills). |
| `quant_optimize_params` | Grid-search the SMA windows as one cancellable background job on the jobs runtime; collect the ranked markdown report with `job_output`. |

Every result is the unified `{code, msg, data}` envelope — `code: 0` on success, the error tier's numeric code with `data: null` on failure (`NETWORK`, `DATA`, `KERNEL`, `RISK`, `CONFIG`, `CANCELLED`, `INTERNAL`) — and every rendered output ends with the research-only disclaimer.

## Session events

`quant/kernel-fault` records one kernel-plane fault (spawn failure, crash, deadline, wire violation) as a log-only diagnostic the moment the client classifies it; it never enters a model request, and the friendly failure itself rides the tool result. In-repo event vocabulary is registered through the generated persistence catalog; the `ignorable` envelope marker is reserved for out-of-tree plugins.

## Model Experience

### Research tools

#### What the model sees

`quant_get_kline`, `quant_compute_indicator`, `quant_run_backtest`, `quant_assess_risk`, `quant_stress_test`, the PET/factor/notes tool schemas, and the Phase-3 reporting and optimization tools joined to prompt assembly while the plugin is loaded, plus text renders: the kline tail as a dated OHLCV list, the indicator's recent readings with its window, the backtest's headline metrics (total/annual return, max drawdown, Sharpe, win rate, trade count, final equity), the historical-simulation tail metrics (VaR/CVaR/volatility/drawdown), the stress comparison (baseline vs stressed return/drawdown/Sharpe), the comparison winner line, the full research report markdown, and the optimization start card (job id, grid shape, combination count, and the `job_output` collection instruction). Denials surface as error results carrying the gate's Chinese reason.

#### Token effect

Bounded: sixteen tool schemas (roughly 3,000 tokens) in every assembled request while loaded; renders cap the kline tail at ten rows and indicator readings at five.

#### KV Cache effect

The schemas join the tool block of the prompt prefix; loading or unloading the plugin invalidates the reusable prefix from that point, as any tool registration does.

## Known Limitations and Deferred Work

- **No live-trading channel, by design** — this is the plugin's permanent red line, not a missing feature; the gate denies intent markers and the kernel holds only virtual accounts.
- **Phase 3 remaining** — strategy comparison, the research report, and jobs-runtime parameter optimization are live; the chart cards (echarts vs bundle size) and the real panel with the core package's Remote face land next.
- **Optimization reports top-N only** — per-combination equity curves and fills are dropped on the kernel wire to keep the response bounded; re-run `quant_run_backtest` on a chosen pair for the full curve.
- **Kernel cache has no TTL policy** — `akshare` cache files are read by existence, not freshness; a refresh strategy waits for a concrete deployment requirement.
- **`akshare` depends on the host environment** — the source fails with a friendly config error until `kernel-py/requirements.txt` is installed; Tushare is a later optional source (its open-source library has been stale since 2024-03).
- **pytest coverage is informational** — the repository's per-file 100% gate covers the TypeScript `src` only; the kernel's pytest suite runs independently and reports separately.
- **Excel export and echarts cards are deferred** — Markdown-first reporting avoids the xlsx dependency; the chart-library decision is an explicit phase-3 review against bundle size.
