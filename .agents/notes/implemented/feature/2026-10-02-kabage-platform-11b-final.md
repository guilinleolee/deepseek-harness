# Agent Note: 卡巴格平台 11b 收官——2FA 硬强制、TOTP 重放、账号级限流、审批组、令牌页、角色矩阵

Status: implemented

[中文](2026-10-02-kabage-platform-11b-final.zh.md) | English

## Problem

Six backlog items closed the platform's deferred list: 2FA hard enforcement (11b — the soft-force banner only nagged), TOTP replay (a stolen code worked for its whole 30-second step, twice), rate limiting that a distributed attacker could outrun (per-account+IP buckets mean N IPs buy N fresh budgets), guard approval groups (dangerous tools were binary allow/deny — no per-use approval, and approval events never reached platform audit), the tokens & quotas page (栏目 5 — virtual keys were only manageable as a side effect of member operations), and role-matrix editing (the permission matrix was a static picture of hardcoded gates).

## Decision

**2FA hard enforcement as a restricted session, not a rejection.** The obvious design (403 at login) deadlocks: self-enrollment happens in /me, which requires a session. Login now always issues a session; when `require2faRoles` hits an unbound account the JWT carries `enr:1` and the gateway rejects every workspace-subdomain request (HTTP and WS) with copy pointing at the enrollment flow. /me and /console stay reachable — the employee can finish binding themselves, and a misconfigured admin can walk back their own config instead of being locked out. `supervisor.mjs reset-twofa --account` is the server-side rescue (audits `security.2fa_reset` via cli). SSO logins share `issueSession`, so they get the same restriction.

**TOTP replay.** `verifyTwofaForLogin` resolves the matched time-step and persists it as `lastStep` on the account record; a code whose step ≤ `lastStep` is rejected (RFC 6238 §5.2). Provisioning (`confirm`) deliberately does not burn a step — binding and first login typically share one 30-second window, and burning it would lock the fresh user out for up to 30 seconds.

**Account-global rate bucket.** The login guard now also counts failures into an `account|*` bucket capped by `accountMaxFails` (security.json, default 50, range 5–500): a distributed attack against one account locks the account for everyone, persisted in the same `rate-limits.json`. Empty-account buckets (register limiting) skip the global tier. `success` clears both tiers.

**Guard approval groups.** `tool-policy.json` gains an optional `approve` group list (deny∩approve is structurally invalid). The guard plugin now also registers a `tools/pre-execute` waterfall listener: an approve-group call returns `{kind:'ask'}`, and the DSH tools pipeline routes that through the approval seam — the employee gets the in-product approval prompt, `approval/asked`/`approval/decided` land in the instance session log, and rejection becomes a model-visible error. For platform audit (admins can never read instance session logs — privacy decision 5), the plugin pairs `asked`→`decided` by id and writes bridge events with `decision=approval-allowed/denied/cancelled/unavailable`; the daemon transcribes them as `guard.approval` (allowed → result ok, otherwise deny). The console roles page switches tool groups from checkboxes to three states: allow / approve-each-use / deny.

**Tokens & quotas page** (`/console/tokens`): key issuance (`token.issue`) and per-account revocation (`token.revoke`) move out of member-page side effects; the token plaintext appears exactly once in the issue response (audit stores no plaintext, same as the CLI), and a read-only monthly points overview fills the 栏目 5 second half.

**Role matrix editing.** `data/role-matrix.json` stores only sparse overrides over defaults that equal today's hardcoded behavior (admin all, auditor read+audit-export, employee nothing). The console's central gates now consult it: page/read access checks `console.read`, every change POST maps through `POINT_FOR_PATH` to a permission point, and audit export checks `audit.export` — all read per-request, so edits take effect immediately. The admin row is immutable server-side (editing the matrix is itself a `security.change` that admin can always perform — no self-lock). Admin service tokens keep their stage-12 change rights; readonly ones get an explicit deny with audit.

## Alternatives considered

**Flat 403 hard-enforcement.** Rejected — the enrollment deadlock above; the restricted-session form enforces the same workspace guarantee while keeping the escape hatches open.

**Burning the step at confirm.** Rejected — it punishes the normal bind-then-login flow for a non-authentication event.

**Global bucket at the same threshold as per-IP.** Rejected — one NAT office or a flaky password manager would hit it in normal use; 50 (5× the per-IP default) only trips under genuinely distributed guessing, and it is configurable.

**Doing approval inside the guard callback.** Impossible and wrong: `ToolGuard` is synchronous by contract ("guards have no allow result"); the `pre-execute` waterfall is the pipeline's designed ask path and already owns policy checks and audit pairing.

**Editable permission matrix as free-form role definitions.** Rejected — roles are fixed three; what was missing was toggling the existing gates. Sparse overrides over the current behavior keep the security model reviewable and the defaults identical to what shipped.

## Consequences

Ten suites, 573 checks, all green (was 458): twofa +8 (replay, next-step acceptance, workspace 403/enrollment-allowed/binding-recovers via raw-Host requests), smoke +6 (global bucket lock/clear/persist, empty-account exemption), auth-audit +23 (tokens page/API/audit incl. no-plaintext, matrix grant/revoke/restore, admin-row and unknown-point rejection, employee console.read grant), toolpolicy +6 (approval-decision transcription), guard +14 (approve validation/ask/next-pass-through, bridge pairing and filtering). Operators: the new guard plugin must be re-pushed (`plugin-push`/`plugin-activate`) before approval groups take effect in instances — the deny path works unchanged from the old deployment; `reset-twofa` joins the CLI surface; `accountMaxFails`/matrix changes need no restart. Remaining deferred list is now empty except the standing real-machine verifications (funded upstream, real SMTP, real WeCom/DingTalk SSO).
