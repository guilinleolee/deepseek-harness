# DSH Plugin: Trajectory Debug Workbench (trajectory-debug)

English | [中文](README.zh.md)

> Target host: DeepSeek Harness (`@deepseek-ai/dsh` v0.1.0-rc.x, developer preview)

Turn DSH's **event-sourced sessions** into debuggable assets: a waterfall trajectory view, deterministic single-step replay (zero token cost), breakpoints, sandboxed edit-and-rerun, fork comparison, and performance analytics — plus OTel GenAI trace export and `trajectory_*` model tools for agents to introspect their own runs.

## Packages

```text
packages/
├── trajectory-debug/              # Service Definition + wire types (pure types, no plugin entry)
├── trajectory-debug-host/         # Host provider: replay/perf/compare engines, breakpoints, projections, commands, RPC transport
├── trajectory-debug-remotes/      # dual-face typert skeleton (browser RPC actually rides the host transport)
├── client-ui-trajectory-debug/    # browser "Debug" tab: waterfall + perf dashboard + replay/breakpoint/rerun/compare console
└── trajectory-debug-bundle/       # installable bundle: dsh.bundle + cordis.patch.yml
```

## Commands

```sh
corepack pnpm install       # requires corepack; Node >= 22.19
corepack pnpm -r build      # emit lib/ (lib-first manifests)
corepack pnpm -r typecheck
corepack pnpm test          # 56 vitest cases
corepack pnpm check         # build + typecheck + test
corepack pnpm check:publish # pre-publish manifest validation
node scripts/smoke.mjs      # real dsh process load smoke (rebuilds the td-smoke profile)
```

## Feature Status

| Capability | Notes |
|---|---|
| Waterfall engine | `buildTrajectoryPage`: turn/step/tool rows, status, timing, tokens, error codes, filters, paging |
| Deterministic replay | `stepContextAt`: model view + action per step; `ReplayCursor` step/seek — **zero token, zero tool execution** |
| Performance analytics | `analyzePerf`: success rates/percentiles, failure taxonomy, token distribution, TTFT/decode, turn stats (optional price table → cost) |
| Fork compare | `compareTrajectories`: step alignment, tool changes, result diffs, summary |
| Breakpoints | `BreakpointManager`: `agent/pre-step` waterfall short-circuit + timeout auto-resume |
| Edit-and-rerun | `rerunTool` through the full `ctx.tools` pipeline; `record\|sandbox\|ask` (ask fails closed without a live agent) |
| Fork + live resume | `sessions.fork` + `agents.resume` + `followup`; `cascade: truncate\|preserve` |
| Projections | `trajectoryDebug/trajectory` + `trajectoryDebug/perf` on the session-projection registry — the browser consumes them with zero client folding |
| Commands | `/trajectory [stepIndex]`, `/perf` |
| Model tools | `trajectory_search / trajectory_step / trajectory_perf` (opt-in via `enableModelTools`) |
| Trace export | `export('trace')`: OTel GenAI semantic-convention spans (Langfuse/LangSmith ready) |
| Sidecar persistence | `FileSidecar` atomic JSON writes (`sidecar: 'memory'\|'file'`) |
| **Browser UI** | "Debug" conversation view tab: waterfall + perf dashboard (projection-pushed, live) + replay/breakpoint/rerun/compare console |
| **Browser RPC** | host registers `POST /api/trajectory-debug/rpc` (webserver custom route, typert-independent); the browser calls it with `fetch` |
| Real load | `scripts/smoke.mjs` installs into a standalone profile and boots in a real dsh process |

## Browser RPC transport (typert-free)

DSH's typert Remote chain depends on build-time codegen. This plugin instead uses the sanctioned **webserver custom-route** extension point:

- Endpoint: `POST /api/trajectory-debug/rpc` — body `{ method, params }`, response `{ ok, value | error }`;
- Methods: `trajectory.list / step.context / perf / replay.start|step|seek / breakpoint.set|remove|list|resume / intervention.rerunTool / variant.fork|list|compare / export`;
- Security: the server binds loopback by default; the route adds no extra trust.

## Client bundle build

`pnpm -r build && node scripts/bundle-client.mjs` produces the browser bundle:

- entry `src/client/index.ts` → esbuild (CJS) → wrapped as `window.__ModuleLoader__.load({ id, factory })` (the official DSH client format);
- runtime externals: only `react` (shell seed); all dsh references are type-only (erased);
- output `packages/client-ui-trajectory-debug/lib/client.js`, served via `exports["./client"]`;
- after installing into a profile, sync the bundle into the profile copy (pnpm `file:` deps are copies):
  `robocopy packages\client-ui-trajectory-debug\lib <profile>\node_modules\dsh-client-ui-trajectory-debug\lib /MIR`

## Install into DSH

Published on npm — install directly (no build required):

```sh
dsh plugin --profile web add dsh-trajectory-debug-bundle
dsh web --dump-config   # expect trajectory-debug-host / -remotes / ui-trajectory-debug rows
```

From a source checkout:

```sh
corepack pnpm check
node scripts\smoke.mjs
dsh plugin --profile web add ./packages/trajectory-debug-bundle
```

Restart `dsh web`: the **Debug** tab appears in the conversation view ring; `/trajectory` and `/perf` work in the input box.

## Publish status

[![npm](https://img.shields.io/npm/v/dsh-trajectory-debug-bundle)](https://www.npmjs.com/package/dsh-trajectory-debug-bundle)

All five packages are published to npm as v0.1.0: [`dsh-trajectory-debug`](https://www.npmjs.com/package/dsh-trajectory-debug), [`dsh-trajectory-debug-host`](https://www.npmjs.com/package/dsh-trajectory-debug-host), [`dsh-trajectory-debug-remotes`](https://www.npmjs.com/package/dsh-trajectory-debug-remotes), [`dsh-client-ui-trajectory-debug`](https://www.npmjs.com/package/dsh-client-ui-trajectory-debug), [`dsh-trajectory-debug-bundle`](https://www.npmjs.com/package/dsh-trajectory-debug-bundle).

Release pipeline:

```sh
corepack pnpm check            # gates
corepack pnpm check:publish    # manifest validation (no file: deps, valid versions, bundle ships patch+index.js)
corepack pnpm publish:all      # pnpm -r publish: workspace:* → version ranges; prepublishOnly builds first
```

- Internal deps use `workspace:*` (pnpm rewrites to version ranges on publish); `file:` deps are rejected by the validator;
- Add the **`dsh-plugin`** topic to the repository (auto-listed on deepseekdocs.com/ecosystem); curated listing via `docs/awesome-submission.md`.

## Ecosystem Comparison

See [COMPARISON.md](./COMPARISON.md): positioning vs dsh-message-edit / dsh-plugin-cost / dsh-deeplink / dsh-eval, and the improvements already shipped.

## Design Notes

- **Self-contained event model**: engines fold a minimal `DebugEvent` model; `adapt.ts` is the only boundary touching DSH `SessionEvent` — immune to DSH's preview-period breaking changes;
- **Projection state is plain JSON** (records/arrays, no Maps/Sets), satisfying the projection-cache persistence contract;
- **"Model-visible == recorded" invariant**: branch execution only ever uses the existing agent channels; the source session log is never rewritten;
- **Replay is zero-cost**: engines never call the LLM or tools;
- **Self-built client bundle**: no dependency on DSH's tsdown chain.

## Compatibility

- Deps: `@deepseek-ai/cordis` + `dsh-session / dsh-agent / dsh-commands / dsh-session-projection` (all `^0.1.0-rc.6`, tracking rc releases);
- Unloading the plugin withdraws every registration (effect-owned); source sessions are untouched.
