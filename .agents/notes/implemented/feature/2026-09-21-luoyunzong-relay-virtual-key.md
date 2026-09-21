# Agent Note: 落云宗 Relay 以 OpenAI 兼容上游接缝实现真实 Key 零下发

Status: implemented

[中文](2026-09-21-luoyunzong-relay-virtual-key.zh.md) | English

## Problem

Task-book stage 3 (`落云宗企业平台任务书.md`): real upstream keys must live only in a Relay process; instances hold only revocable virtual keys; acceptance = no real key anywhere in an instance (env, config dump, disk), revocation rejects new requests immediately, and switching upstream vendors requires zero instance changes. The DSH LLM path already resolves credentials per request through the credentials capability and sends them as `Authorization: Bearer` to a provider-configured `baseURL` — the question was whether that seam is enough or a new `credentials-broker` Provider seam (the task book's default landing spot) is required.

## Decision

`platform/supervisor/relay.mjs` — a Relay process bound to `127.0.0.1:9400` exposing the OpenAI-compatible `POST /v1/chat/completions`. A virtual key (`vk-…`, random 24 bytes, stored only as SHA-256) authenticates the caller; the request body's `model` is checked against the key's model allowlist (`*` or explicit ids); the model resolves to one upstream in `data/upstreams.json` (name, real baseURL, real key, served models), the Authorization header is swapped to the real key, and the request is forwarded to `<upstream baseURL>/chat/completions` with streaming and non-streaming responses piped through verbatim. Instance homes change only their provider route: `baseURL: http://127.0.0.1:9400/v1`, `apiKeyEnv: LYZ_VIRTUAL_KEY`, and a `.credentials.yaml` containing only the virtual key — the previous interim copies of real credentials were deleted. Revocation reads `vkeys.json` through an mtime cache, so a revoked key is rejected at the very next request; in-flight forwarded requests are not interrupted. `relay.log` records metadata only (account, instance, key id, model, upstream, status, latency) — never bodies, per task-book decision 5.

Two subtleties mattered. First, pi-ai's openai-completions adapter auto-detects wire-compatibility from `model.provider` and `model.baseUrl` (`open.bigmodel.cn` triggers the zai profile: no `store`, no `developer` role, no `reasoning_effort`, zai thinking format). Pointing instances at `127.0.0.1` would silently lose that profile, so the instance's provider route is renamed `zai` (the `providers` dict key is a free-form route name) — detection fires on the name and the wire format stays identical through the Relay. Second, upstreams may be https: the forward picks `node:https` vs `node:http` by protocol, and construction is wrapped so one misconfigured upstream answers 502 instead of crashing the control process.

## Alternatives considered

**A `credentials-broker` Provider seam inside the harness.** Rejected: the provider-config `baseURL` seam already exists and accepts any OpenAI-compatible endpoint, so a Relay posing as the upstream achieves every acceptance criterion with zero harness changes — the task book's own rule ("only add a seam when extension points fall short") applies. A broker Provider would also still need a client-side trust credential (the virtual key by another name), adding moving parts without removing any.

**Mutating the credentials capability to proxy resolution over RPC.** Same objection with more surface: it changes harness-owned resolution semantics to save one config line.

## Consequences

Every stage-3 acceptance criterion holds keylessly (the only upstreams on hand have zero balance): instance homes contain zero real-key occurrences (grep against the real value); missing/forged/revoked keys get 401; an authorized model forwards upstream and the 429 "余额不足" response itself proves real-key injection (upstream authentication precedes balance checks — a failed injection would 401); moving `glm-5.3-flash` from upstream `zhipu` to `zhipu-backup` via two `set-upstream` calls rerouted the same virtual key (relay.log shows the new upstream) with instances untouched; an end-to-end headless call from instance e01 traversed instance → Relay → upstream with full metadata logged (7 entries including the agent's retry burst — the exact behavior stage-4 quotas will cap). Revocation was verified live: same token 400 (forwarded; empty messages rejected by upstream param validation) before, 401 immediately after `revoke-vkey`.

Costs and deferred items: the Relay trusts loopback only — remote deployment puts it behind the same host boundary as the gateway; upstream keys sit in a plaintext JSON file (fingerprint-only display) until the stage-3+ control-plane database replaces it; `model` allowlists are per-key and static until the console manages them; streaming usage metadata (token counts) is not yet extracted into the metering store — that lands with stage 4, where per-request quota enforcement joins the existing per-request model check. During load testing a latent stage-1 defect surfaced: the disk-usage sampler walked pnpm-heavy homes synchronously every 60 s, starving the event loop for tens of seconds at a time (requests served only between walks); the walk is now async (`fs/promises`, thread-pool I/O), interval 120 s, same entry cap.
