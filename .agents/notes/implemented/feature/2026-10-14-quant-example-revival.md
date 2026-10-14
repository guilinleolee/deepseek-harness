# Agent Note: The example composition rides the current architecture

Status: implemented

English | [中文](2026-10-14-quant-example-revival.zh.md)

## Problem

The quant-research example — the keyless end-to-end driver over the real composition — was authored against the pre-upstream architecture and stopped running somewhere in the Phase3-4 merge chain: its vitest lane no longer included it, its composition referenced retired packages, and its model fixture used APIs that no longer exist. The plugin itself was fully tested at the unit level, but the one test that boots the whole stack (kernel subprocess, storage, gate, jobs registry, model loop) had gone dark — precisely the coverage the repository's model-visible-change rule asks for.

## Decision

- **The spec moves to the expected lane under the golden convention.** Upstream's `refactor(test): reserve snapshots for session recordings` (1cfe0f9942) renamed example snapshot tests to `*.golden.e2e.ts` and moved the recorded-session replays under `snapshots/`; the quant example is owner-local assembled expected output (no recorded session), so it joins `vitest.expected.config.ts` with an `examples/*/tests/**/*.golden.e2e.ts` include. The spec renames from `quant-research.snapshot.ts` to `quant-research.golden.e2e.ts`.
- **The composition rides the current packages.** The retired `dsh-agent-spine-demo` row becomes the declarative `dsh-agent-loop` with one startup agent (persona via `system-prompt`'s `personaPrefix` — the demo's `persona`/`workspaceContext`/`dshHome` knobs no longer exist); the merged `dsh-settings` row drops (it now injects `configEditor` + `profileContext`, services this composition does not provide, and the plugin reads no settings); the `llm`, `session`, `agent`, `session-projection`, and `tools` service hubs join as explicit rows the loop awaits. `examples/package.json` returns as the single workspace umbrella so plain-Node resolution of every cordis.yml package works — the pattern the original umbrella documented.
- **The mock rides the current LLM shapes.** `CallId` became `ToolCallId`; tool results are now `role: 'tool'` messages (the old `content.find(block => block.type === 'tool-result')` never matched, so the mock replayed round one forever — the timeout that hid every other failure).
- **The driver gains the Phase4/5 stages.** After optimize and walk-forward: one cross-sectional IC job over the `000001`/`600519` panel with `ic_windows: 2` (through the `cross_section_ic` kernel op), one panel-cap denial, and a `quant_list_snapshots` read asserting the persisted results of the rounds above. The spec asserts the start card, the settled markdown (windowed-stability section included), the denial reason, and the snapshot list.
- **The double domain open closes at the source.** Reviving the example exposed that `apply()` opens the domain twice (plugin body + service fiber) and the storage-domain facility is single-open per name — the unit suites never booted the real composition, so only the example caught it. `QuantResearchService` now accepts the caller's already-open handle; `apply()` passes its domain to the service fiber, and the apply spec moves to one open / one close.

## Alternatives considered

**Deleting the example.** Rejected: it is the only composition-level test of the plugin (boot ordering, service injection, kernel subprocess through the real seam, gate over real tool dispatch) and the repository's stated policy for model-visible changes.

**Recording a session snapshot instead.** Rejected: the value here is the live composed stack with a scripted model, not a replayed recording; the expected lane exists for exactly this shape.

**Keeping the service's own open and disabling the plugin body's.** Rejected: the tool layer's domain handle carries the tables; making it dependent on the service inverts the ownership the apply() disposer already documents.

## Consequences

Costs: the example is back on the beaten path — upstream retirements will hit it again, but now visibly (the lane runs it). Verification: the golden spec passes end to end (five tool rounds, three background-job stages, three denials, the snapshot list) on the current master tip; the quant unit suites stay 330 green with the shared-domain design; kernel pytest 33 green. The expected lane's pre-existing failures (typert artifacts missing from un-built `lib/` trees) are unrelated and unchanged by this work — that lane needs a prior `build`.
