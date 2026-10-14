# Agent Note: The quant-research plugin ships research-only quant tooling as a two-plane plugin with a pre-execute red line

Status: implemented

English | [中文](2026-10-04-quant-research-plugin.zh.md)

## Problem

The harness had no quantitative-research surface: market data, indicators, and backtesting lived outside the agent, so every research question about a symbol required leaving the session. The obvious plugin shape — one process, one framework, indicators "somewhere" — hides three decisions that shape every later phase: where the numbers come from, where the math runs, and what stops a research tool from becoming a trading tool.

## Decision

- **Two packages, two compute planes.** The core package (`@deepseek-ai/dsh-quant-research`, `packages/quant/quant-research`) owns orchestration: argument validation, the data-source circuit breaker, TypeScript implementations of the phase-1 indicators (MA/EMA/MACD/RSI/BOLL/ATR), and the three `quant_*` tools. The Python kernel (`kernel-py/` inside the package, stdlib-only) serves `get_kline` (deterministic symbol-seeded synthetic walk, or lazily-imported akshare over an on-disk cache) and `backtest` (a pure simulator over caller-supplied bars: signal on close, fill at next open, all-in/all-out). One request spawns one process through the subprocess capability and every exit — including the tool's cooperative `exec.signal` deadline — ends in the seam's terminate ladder; there is no long-lived child and no self-written kill logic. The indicators run in TypeScript, not the kernel, because replays must show bit-identical numbers regardless of the host's Python environment.
- **PRT risk lives in TypeScript and reuses the pure simulator for stress.** `quant_assess_risk` reports historical-simulation VaR/CVaR (empirical quantile of daily returns), annualized volatility, and window drawdown; `quant_stress_test` transforms the fetched bars (`crash` overnight gap, `liquidity` glide from the last pre-segment close with a volume hair-cut) and re-runs the SAME kernel backtest over the shocked path, so the stressed engine is the audited one. New red-line caps: confidence 0.8-0.99 and shock 0.01-0.5 are fixed constants enforced by the gate. The concentration checker ships with the module and waits for PET's positions.
- **The research-only red line is a `tools/pre-execute` gate, not a convention.** One listener owns every `quant_*` call: it denies real-trading/broker-API markers found at any depth of the frozen arguments (`实盘`, `券商`, `place_order`, `submit_order`, `cancel_order`), enforces the fixed bar/cash/fee caps regardless of the schema, and audits every denial into the frozen `quant_research` domain v1 (`compliance_denials` table); a failed audit write warns and never un-denies. The plugin's permanent red line — no real-broker channel — is documented as a design invariant, not a missing feature, and the kernel holds only virtual accounts.
- **Keyless proof through a scripted model, not a recorded one.** The example (`examples/quant-research`) composes the real stack and its snapshot swaps only the model: the scripted `quant-mock` adapter drives two real tool rounds and one real red-line denial through the kernel subprocess, the synthetic source, the storage audit, and the gate. Recording from a live model would have made the scenario non-free and slower to iterate; the scripted transcript exercises everything the model is not needed for.
- **Plugin shape follows the loader, not the bundle.** The plugin exports named `apply`/`inject`/`Config` with no default export: the loader's default unwrapping drops the module-level `inject`, and without it `ctx.storageDomain`/`ctx.subprocess` are unreachable (`cannot get property ... without inject`). The kernel script resolves through the package's own manifest so it works from a workspace tree and an installed profile alike.

## Alternatives considered

**Indicators in the kernel.** Rejected for phase 1: replaying a session on a machine without the right Python environment would change rendered numbers, violating replay identity; the kernel gets the factor library when phases 2–3 need pandas-scale factor math anyway.

**A long-lived kernel service process.** Rejected: per-request spawn costs ~200 ms and buys a stateless protocol with no session-affinity bugs; if backtests grow heavy, the jobs runtime (phase 2's parameter optimization) is the sanctioned long-work path, not a daemon.

**Recording the snapshot from a live model.** Rejected: the harvest/stabilize machinery exists for product-path scenarios that need real model behavior; a deterministic tool pipeline needs only deterministic tool calls, and the scripted adapter keeps the scenario keyless on every machine.

**Ignoring the denial path in the snapshot.** Rejected: the gate is the plugin's core safety property; a snapshot that never denies would not detect a gate that silently stops registering.

## Consequences

Costs: per-request Python startup adds latency to every kernel call (acceptable at phase-1 data volumes); the `akshare` cache has no TTL policy yet (hit-by-existence), and the compliance marker list is a fixed Chinese/English vocabulary that a paraphrased trading intent can skirt — the caps and the absence of any order path are the load-bearing barriers, the markers are the loud refusal. Verification: 177 vitest cases across the two packages (including the PRT metrics, cap, and stress-transform suites) with per-file 100% coverage on both `src` trees, 25 pytest cases for the kernel, and one keyless real-composition snapshot driving fetch → backtest → risk → stress → denial → answer through the Loader; catalogs (tool/config/persistence/client/module) regenerated in the same change. Deferred to later phases: PET virtual accounts with approval review (concentration checks already in place), the factor library, jobs-based optimization, chart cards, the locale dictionaries for the panel, and a cache TTL policy — each named in the package README's limitations section.
