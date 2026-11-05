# Agent Note: 卡巴格 console v2 遗留六项收口（轮转/限流持久化/Origin/迁移/NAT/CLI 策略）

Status: implemented

[中文](2026-10-02-kabage-console-v2-leftovers-batch2.zh.md) | English

## Problem

The 2026-09-25 console v2 note recorded six deferred items. Each was a recorded MVP limitation with a concrete failure mode: an audit log that grows forever; a rate-limit state wiped by every daemon restart (wait out a lockout by crashing the daemon — or simply crash-recover into an unlocked attacker); no Origin check on the login/TOTP POSTs (login CSRF: an attacker page can submit the victim's browser to `/api/auth/login` with the attacker's credentials and silent-cookie the victim into the attacker's account); register rate limiting keyed on IP only (a NAT office shares one bucket — one person's typos lock out colleagues' registrations); no path from legacy `monthlyTokens` quotas to the points model; and CLI account/password commands bypassing the password policy the console enforces.

## Decision

**Audit rotation.** `audit.jsonl` rotates by size: before each append, `audit.mjs` (which now reads `security.json` per append) compares the tracked active-file size against `auditRotateBytes` (default 16 MB, range 1 KB–1 GB) and, over the line, renames the active file to `audit-<ts>.jsonl` and keeps only the newest `auditKeepArchives` (default 4) archives, deleting older ones. Rotation runs inside the existing per-append serial chain, so there is no concurrent-rename window, and any rotation failure degrades to appending into the current file. `auditQuery` scans active + archives newest-first and, per file, keeps only the newest entries still needed to fill `limit` — small bounded queries (the /me device list, the 500-line console page) never read more than the tail of the newest files, while the unbounded export naturally covers the full archive set. Old-line-per-archive timestamps make filename sort = chronological sort.

**Rate-bucket persistence.** `createLoginRateGuard(getLimits, persistence)` gained an optional `{dataDir, file}`: buckets load at construction (stale entries dropped), and every `fail`/`success`/check-induced lock atomically rewrites the file (`tmp` + rename; write failure logs and never affects in-memory judgment). The gateway uses `data/rate-limits.json`, register uses `data/register-limits.json` — two guard instances, two files, no clobbering. Files hold only live entries (non-zero fails or a future `lockedUntil`), so they shrink back on their own.

**Login origin check.** `sameOrigin` (already local to portal.mjs) is now exported and applied at the top of gateway's `/api/auth/login` and `/api/auth/totp`: an `Origin` header whose host differs from `Host` gets 403 before any state change. Absent Origin (curl, tests, service calls) passes — the same trade the console POST endpoints already make, layered over `SameSite=Strict`.

**Legacy→points migration.** `quotas.migrateLegacyQuotas(dataDir)` sets `monthlyPoints = monthlyTokens` (1:1 — the legacy judgment compared raw tokens, so the effective line is unchanged; the console 旧制 badge disappears), leaves already-migrated/unlimited accounts untouched, writes once atomically, and is idempotent. Exposed as `supervisor.mjs migrate-points` with a per-account report.

**NAT register buckets.** Register failures now pick a bucket by invite validity: an invalid/missing code counts into the IP bucket (code-guessing stays throttled even when the attacker rotates codes), while a valid code counts into a `code|ip` bucket — one colleague's password typos no longer lock the shared-IP office out of their own invites. The IP bucket is still checked first, so a code-guessing lockout still denies holders of valid invites (prior behavior preserved).

**CLI policy closure.** `checkPasswordPolicy` now runs inside `addAccount` and `setPassword` (config read per call), so console, register page, IdP sync and CLI share one constraint and the CLI has no bypass surface. The CLI's auto-generated passwords switch from `randomBytes(9).base64url` (three-class membership unguaranteed) to `generatePassword()`, which the policy test already proves compliant 20/20.

## Alternatives considered

**Time-based audit rotation (per month).** Rejected: size bounds the failure mode the item was about (unbounded growth) with no calendar coupling, and month naming would imply a retention guarantee the pruner does not keep per-month.

**Keying register limits on invite code alone.** Rejected: an attacker rotating invented codes would get a fresh bucket per guess; the dual-bucket scheme keeps the IP-level cap exactly for that case.

**Persisting rate buckets on every check.** Unnecessary: `check` only mutates state when it triggers a lock (persisted there); pure reads stay pure.

**Migrating via a conversion ratio (tokens→points).** Rejected: points already have their own semantic (model/group ratios); inventing a conversion would change effective lines. 1:1 preserves what the operator set.

## Consequences

Nine suites, 458 checks, all green (was 426): smoke +20 (persistence rebuild semantics, rotation archive/retention/cross-archive query, storage-layer policy, new config ranges), quota smoke +5 (1:1, isolation, idempotence), me-invite +7 (login/TOTP cross-origin 403, per-invite bucket lockout, same-IP other-invite success). Operators should know: rotation deletes pruned archives permanently (export first if retention beyond `auditKeepArchives` matters); `rate-limits.json` means a lockout now survives restarts by design — `delete data/rate-limits.json` is the manual override; `migrate-points` shares the CLI's usual write window against a live daemon (run while the console is idle). Deferred items now fully closed for console v2; remaining platform backlog unchanged (2FA hard-enforce 11b, TOTP replay counter, account-global rate bucket, guard approval groups, real-machine verifications).
