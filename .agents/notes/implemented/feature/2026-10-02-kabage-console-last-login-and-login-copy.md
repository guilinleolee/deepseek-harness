# Agent Note: 卡巴格成员最后登录列与登录失败文案透传

Status: implemented

[中文](2026-10-02-kabage-console-last-login-and-login-copy.zh.md) | English

## Problem

Two deferred items from the console v2 review (2026-09-25): the member list has no last-login column (admins cannot see when an account was last active without querying the audit log), and the login page shows a fixed "账号或密码错误" for every failed login — a rate-limited (429), disabled, or 2FA-broken account is told its password was wrong, which misdirects the employee and generates support load.

## Decision

`lastLogin: {ts, ip}` now lives on the account record. The write happens in exactly one place: gateway's `issueSession(res, record, ip)`, which all three login paths share — password login and TOTP login previously re-inlined identical token-signing code, so both blocks were replaced with `issueSession` calls (the SSO paths already called it; they now pass `ip`). The write goes through the console's account lock (same serial queue as member mutations, so a login cannot lose a concurrent disable/quota update), rereads `accounts.json` fresh inside the lock, is asynchronous (`void`), and never blocks the response — a failed write logs and moves on. The audit log remains the complete login history; the account record keeps only the latest event so the member list needs no audit scan.

Surfaces: `listAccounts` projection and `/console/api/member/list` gained `lastLogin` (null when never logged in — IdP-synced fresh accounts included); the console member page gained a 最后登录 column (time + source IP, 从未登录 placeholder, colspan 11).

Copy: the bad-credentials response is now Chinese (`账号或密码错误`, matching the page and the SSO bind path), and the login page renders the server-provided `error` verbatim with an HTTP-status fallback — 429 lockout countdown, disabled-account, and 2FA-broken messages now reach the user. The TOTP step already behaved this way.

## Alternatives considered

**Deriving the column from audit events per member** (the /me device-list approach). Rejected for the table: N accounts × reverse audit scans per page render, and accounts outside the newest 500 events would display "never". The account record is O(1) at render time; the audit log stays authoritative for history.

**Writing lastLogin without the account lock.** Rejected: a bare read-modify-write of `accounts.json` from the gateway races the console's locked member mutations and can drop a concurrent disable. The lock is already exported for cross-module use (SSO bind).

**Front-end-only copy fix.** Rejected: showing the server error verbatim would have surfaced the English `invalid credentials` string, so the server copy was fixed first; the page change alone would have been wrong.

## Consequences

`node test/me-invite-http-verify.mjs` grew from 63 to 74 checks (lastLogin propagation with async-lock polling, member page column, Chinese 401 copy, page passthrough, and a login-rate-limit block on the second gateway asserting 429-after-lockout with readable copy); all nine supervisor suites are green (426 checks), covering the refactored TOTP/SSO issuance paths. Costs and deferred items: `accounts.json` gains one write per successful login — negligible at ≤100-employee scale, and the control-plane DB will absorb it later; existing accounts read as 从未登录 until their next login; the `kabage-admin-tools` `user_list` tool ignores the new field (its output contract is unchanged — surface it there only if asked). Remaining console v2 deferred items untouched: audit rotation, rate-map persistence, login Origin check, legacy→points migration CLI, NAT shared-IP lockout.
