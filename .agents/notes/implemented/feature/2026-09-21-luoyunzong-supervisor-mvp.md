# Agent Note: 落云宗实例编排 supervisor MVP 以零依赖文件 IPC 形态独立于 harness 发布

Status: implemented

[中文](2026-09-21-luoyunzong-supervisor-mvp.zh.md) | English

## Problem

The enterprise platform task book (`落云宗企业平台任务书.md`, stage 1) requires server-hosted per-employee DSH instances — one account, one instance, one isolated directory — with health checks, crash auto-restart within 30 seconds, and instance-page data (port/pid/uid/memory/disk). The harness itself is single-user and has no instance concept; `DSH_HOME` is fully parameterized (`packages/util/home-paths`) and profiles auto-initialize on first use, so "one user = one home = one process" only needs an outer scheduler. The question was where that scheduler lives and how it talks to the instances without touching the harness (task-book decision 4: standalone control plane, no harness-core changes).

## Decision

`platform/supervisor/` — a standalone, zero-dependency Node ESM CLI outside the pnpm workspace (the `platform/` glob is deliberately absent from `pnpm-workspace.yaml`). One daemon process owns all instance child processes; short-lived CLI commands (`up/status/stop/start/restart/logs`) communicate with it exclusively through files under `data/`: a state file (written atomically via temp+rename) and a control file polled every 2 seconds. Instances are spawned from a manifest (`instances.json`) with a command template (`pnpm dsh web --no-open --port {port}`) and `DSH_HOME=data/homes/<id>`.

Key mechanics: crash restart uses a 2-second delay with a counter that resets after 5 minutes of stability and gives up (state `failed`) after 5 restarts in a window; health polling is 2-second during startup and 15-second steady-state, with a 180-second startup timeout calibrated to dsh's tsx source-mode cold boot (profile init + pnpm install ≈ 137 MB + compile ≈ 3–5 minutes); memory is sampled as a **process-tree sum** (the recorded pid is the pnpm/cmd shell, not the DSH node process) via one PowerShell `Get-CimInstance Win32_Process` table on Windows and `/proc/<pid>/stat` parsing on Linux, with the tree built node-side; disk usage is a bounded recursive walk of each home.

Three failure modes found during live testing were fixed in the same change: (1) the daemon promise resolved immediately after setup, so `main()`'s completion callback called `process.exit(0)` and killed the daemon — the daemon now returns a never-resolving promise; (2) `stop` relied on `taskkill /T` tree semantics that break when an intermediate shell process has already exited, and its fire-and-forget `taskkill` children were reaped when the CLI process exited before they ran — `stop` now walks the state file's instance pids explicitly and awaits each kill; (3) the portal server bound *after* instances were spawned, so an `EADDRINUSE` orphaned three half-booted instances — the portal now binds first and any bind error exits before the first spawn.

## Alternatives considered

**A harness plugin contributing an orchestration capability.** Rejected: instance lifecycle is platform engineering per the task book's domain mapping; wiring it through `ctx.effect()` would couple supervisor semantics (process trees, uids, ports) to plugin lifecycles and drag the 100%-coverage gate over OS-specific process code.

**socket/HTTP control API instead of files.** Rejected for MVP: the control plane (stage 2) will own the real RPC surface; file IPC deletes all server code for a feature that will be replaced, and `status` must work when the daemon is dead (it reads the last written state and honestly marks liveness per pid).

**Container per instance.** Out of scope by the task book's non-goals (MVP is single-machine multi-process); the manifest's command template is the seam where a container runtime would slot in later.

## Consequences

One machine runs N isolated instances with a single command, and every acceptance criterion of stage 1 that does not require a funded model key has been demonstrated live (3 instances healthy; kill → 2–6 s respawn; per-home session/config/credential isolation — a headless call resolved credentials only after `.credentials.yaml` was copied into that instance's home; session files intact across crash-restart). The real-conversation end-to-end remains blocked by upstream quotas (zhipu 429 余额不足), not by code.

Costs: instance restart to HTTP 200 takes ~165 s under tsx source-mode boot — the 30-second task-book budget holds for the supervisor's restart action, while service recovery is bounded by dsh's boot mode; production should launch built output or the single-exe build, and this is recorded as the known optimization. The portal is a landing page, not a reverse proxy: the web SPA assumes root paths, so the unified entry for production is a front reverse proxy with the stage-2 auth layer. `uid` is nominal on Windows and awaits real setuid on the Linux deployment path. The supervisor only ever collects process and resource metadata — no session content, per task-book decision 5.
