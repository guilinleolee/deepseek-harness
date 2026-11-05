# Agent Note: DingTalk OAuth contract fix (endpoint + field names)

Status: implemented

[中文](2026-10-03-kabage-dingtalk-oauth-contract-fix.zh.md) | English

## Problem

Real-machine verification of DingTalk SSO (first live probe with real credentials) caught the code-exchange call hitting an endpoint DingTalk does not have: `POST /v1.0/oauth2/token` returned 404 "Specified api is not found". The correct new-OAuth2 contract is `POST /v1.0/oauth2/userAccessToken`; probing it also showed the request body must use camelCase (`clientId`/`clientSecret`/`grantType`) — the snake_case body got "clientId is mandatory". Neither failure could be caught by the existing suite: `test/sso-verify.mjs` covered only the WeCom branch (the mock served WeCom protocol paths), so the DingTalk branch had zero executed coverage.

## Decision

`resolveSsoIdentity` now calls `/v1.0/oauth2/userAccessToken` with a camelCase body (`clientId`, `clientSecret`, `grantType: 'authorization_code'`, `code`), with a comment pinning the external contract and the probe date. The WeCom branch is untouched (its `gettoken`/`auth/getuserinfo` oapi contract is different and correct). The mock server in `test/sso-verify.mjs` grows the DingTalk protocol shape (`/oauth2/auth` authorize, `/v1.0/oauth2/userAccessToken` capturing the request body, `/v1.0/contact/users/me` asserting the `x-acs-dingtalk-access-token` header), and a full DingTalk flow section asserts: login-page button, start → authorize redirect shape (`client_id`/`state`/`redirect_uri`), unbound → bind page, successful bind for a second account, the token request body's camelCase fields (the regression that matters), identity header, `auth.sso_bind` audit with `ssoId: dingtalk:<unionId>`, and `ssoIds` persistence. Verified against the real API before writing the fix: with the user's real credentials, the corrected endpoint + camelCase body move the error from "api not found" / "clientId is mandatory" to "不合法的临时授权码" (invalid authCode) — i.e., the client is accepted and only the deliberately fake code is rejected.

## Alternatives considered

**Keeping snake_case and switching endpoint only.** Rejected: the live probe shows the endpoint demands camelCase; a half fix would still fail at the first real login.

**Rewriting the whole SSO module against a DingTalk SDK.** Rejected: the module is deliberately zero-dependency; only the exchange call was wrong, and the flow (state, bind, audit) is already tested and unchanged.

## Consequences

Suite grows 24 → 35 checks, all green; the DingTalk branch now has a regression net that pins the real contract, so a future DingTalk-side change surfaces as a captured request-body mismatch instead of a 502 at first real login. No config or on-disk format changes. The probe that exposed the bug doubles as credential validation: the user's Client ID/Secret are confirmed accepted by api.dingtalk.com.
