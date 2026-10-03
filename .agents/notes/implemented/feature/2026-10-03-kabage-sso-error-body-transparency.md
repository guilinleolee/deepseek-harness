# Agent Note: SSO failure errors now carry the provider response body

Status: implemented

[中文](2026-10-03-kabage-sso-error-body-transparency.zh.md) | English

## Problem

`resolveSsoIdentity` threw only the HTTP status on provider failures (e.g.「钉钉用户接口失败（HTTP 403）」), but the actual cause of a 403 — missing permission, unpublished app, user outside visible range — lives only in the response body. During real-machine DingTalk verification the user saw a bare 403 and could not self-diagnose; every triage round required another guess.

## Decision

New `errBody(res)`: on a non-2xx response, append up to 300 chars of the body to the thrown message (all four throw sites: WeCom/DingTalk token and user endpoints); body-read failures degrade silently to an empty string. The portal error page already surfaces the thrown message, so DingTalk's own `code`/`message` becomes directly visible to the operator.

## Consequences

The next real-machine failure will show DingTalk's own words (e.g. `{"code":"Forbidden","message":"..."}`), turning triage from guessing into reading. The existing 35 assertions do not pin these messages — suite stays green; no config or on-disk format changes.
