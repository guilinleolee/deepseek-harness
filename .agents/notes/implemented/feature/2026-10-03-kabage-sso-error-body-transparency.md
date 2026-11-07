# Agent Note: SSO failure errors now carry the provider response body

Status: implemented

English | [中文](2026-10-03-kabage-sso-error-body-transparency.zh.md)

## Problem

`resolveSsoIdentity` threw only the HTTP status on provider failures (e.g.「钉钉用户接口失败（HTTP 403）」), but the actual cause of a 403 — missing permission, unpublished app, user outside visible range — lives only in the response body. During real-machine DingTalk verification the user saw a bare 403 and could not self-diagnose; every triage round required another guess.

## Decision

New `errBody(res)`: on a non-2xx response, append up to 300 chars of the body to the thrown message (all four throw sites: WeCom/DingTalk token and user endpoints); body-read failures degrade silently to an empty string. The portal error page already surfaces the thrown message, so DingTalk's own `code`/`message` becomes directly visible to the operator.

## Alternatives considered

- Keep throwing only the HTTP status (the pre-change behavior): rejected — the status alone cannot distinguish a missing permission from an unpublished app or an out-of-scope user, which is exactly what triage needed.
- Log the response body instead of putting it in the thrown message: rejected — the portal error page surfaces the thrown message directly, so a separate log would not reach the operator during real-machine verification.
- Parse and re-emit only the provider's `code`/`message` fields: rejected in favor of appending the raw body (up to 300 chars) — the shape differs per provider and the raw body is the honest payload when a field is missing.
## Consequences

The next real-machine failure will show DingTalk's own words (e.g. `{"code":"Forbidden","message":"..."}`), turning triage from guessing into reading. The existing 35 assertions do not pin these messages — suite stays green; no config or on-disk format changes.
