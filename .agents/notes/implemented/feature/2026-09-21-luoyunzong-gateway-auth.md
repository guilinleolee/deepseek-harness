# Agent Note: 落云宗认证网关以 Host 子域路由实现实例零改动的登录边界

Status: implemented

[中文](2026-09-21-luoyunzong-gateway-auth.zh.md) | English

## Problem

Task-book stage 2 (`落云宗企业平台任务书.md`) requires login + JWT + instance binding, with two acceptance criteria: unauthenticated access to any entry is refused, and user A's session list never contains user B's session ids. DSH's web stack deliberately has no auth layer (`client/connection` blocks `0.0.0.0` "until a real authentication layer exists"; the webserver README states "No TLS, auth, or origin policy"), and the task book forbids harness-core changes when an extension point suffices. The open question: where does auth live so the DSH web SPA — which assumes root-path URLs for both `/api` and its WebSocket downlinks — keeps working untouched?

## Decision

An authenticated reverse gateway inside the supervisor (`platform/supervisor/gateway.mjs`, zero dependencies), replacing the stage-1 landing portal. Routing is **by Host header, never by path prefix**: `<instanceId>.localhost:8460` proxies verbatim to `127.0.0.1:<instancePort>`, so absolute-path API calls and WebSocket upgrades survive untouched. Instances need exactly two launch-arg changes, both existing CLI flags rather than new code: `--host 127.0.0.1` (employees cannot bypass the gateway on a real server) and `--trusted-host <id>.localhost:8460` (the instance's own DNS-rebinding trust fence accepts the forwarded Host — the fence's "until a real authentication layer exists" comment is the hook the task book predicted).

Auth semantics: accounts live in `data/accounts.json` with scrypt-hashed passwords; login (`POST /api/auth/login`, allowed on any host so the cookie lands on the subdomain the user actually visits) issues a hand-rolled HS256 JWT (30 min) as an HttpOnly SameSite=Strict host-only cookie; every proxied request and every WebSocket upgrade re-checks token validity, the account's `tokenEpoch` (bumping it via `revoke --account` kills all issued tokens instantly), and the account↔instance binding **live from the account store** (rebinding takes effect without revocation). `/status.json` is admin-only. WebSocket upgrades to `/api/events.mux` and `/api/events.host` are authenticated then tunneled as raw bytes (path from `client/connection/src/api-path.ts`; the SPA's real upgrade routes).

Verification (curl with `--resolve` standing in for browser `*.localhost` resolution, which needs no hosts-file edits): unauthenticated subdomain HTTP 401 + WS 401; authenticated WS handshake returns 101 with `Sec-WebSocket-Accept` computed by the instance — end-to-end byte tunneling proven; admin→bound instance 200, replaying admin's token against another instance 403; session-id sets of two instance homes are disjoint (A's list source is A's instance home only); revoke → old token 401, fresh login 200; `/status.json` 401 anonymous, 200 admin, 401 employee.

## Alternatives considered

**An auth plugin inside the harness web stack.** Rejected: the gateway enforces the same boundary with zero harness changes; a harness plugin would drag OS-adjacent proxy code into the 100%-coverage workspace gates and split the security boundary across two processes.

**Path-prefix proxy with `<base>` injection.** Rejected: `fetch('/api')` and WebSocket constructors ignore `<base href>` for root-relative URLs, so the SPA's absolute paths would still miss; path rewriting is a losing battle against an app that assumes root.

**Editing the hosts file for dev subdomains.** Unnecessary: browsers resolve `*.localhost` to 127.0.0.1 natively (RFC 6761 handling), and curl tests use `--resolve`.

**Session cookies without JWT.** Rejected in favor of stateless tokens + a per-account epoch: revocation needs no session store, and the control plane (stage 3+) can adopt refresh-token rotation without changing the gateway's routing role.

## Consequences

Both stage-2 acceptance criteria hold with the instances untouched: entry refusal at the gateway (HTTP and WS), and cross-user session invisibility by construction (binding + per-home storage). Costs and open items: login has no rate limiting and the gateway has no TLS — acceptable only for loopback/intranet MVP and explicitly flagged for production (front TLS reverse proxy); the cookie is host-only per subdomain, so users log in once per instance they visit (production wildcard-domain cookies collapse this); tokens are 30-minute access-only without refresh rotation, deferring to the stage-3 control plane; the accounts file stores hashes but sits on the same disk as everything else — a real control-plane database replaces it. During testing, the earlier fire-and-forget `taskkill` in `stop`'s daemon branch was found still live (a stale daemon kept serving port 8460 and respawned instances with old args); the stop path now awaits every kill.
