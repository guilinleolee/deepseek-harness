# Agent Note：钉钉 OAuth 对接契约修复（端点 + 字段名）

Status: implemented

[English](2026-10-03-kabage-dingtalk-oauth-contract-fix.md) | 中文

## 问题

钉钉 SSO 真机验证（首次持真实凭证探针）发现：平台的 code 换身份调用打在钉钉不存在的端点上——`POST /v1.0/oauth2/token` 返回 404「Specified api is not found」。新版 OAuth2 的正确契约是 `POST /v1.0/oauth2/userAccessToken`；继续探针还发现请求体必须用驼峰字段（`clientId`/`clientSecret`/`grantType`），snake_case 会被回「clientId is mandatory」。既有测试抓不到这两处：`test/sso-verify.mjs` 只覆盖企微分支（mock 只建了企微协议路径），钉钉分支零已执行覆盖。

## 决策

`resolveSsoIdentity` 改调 `/v1.0/oauth2/userAccessToken`、请求体驼峰（`clientId`、`clientSecret`、`grantType: 'authorization_code'`、`code`），注释钉明外部契约与探针日期。企微分支不动（其 `gettoken`/`auth/getuserinfo` 是另一套 oapi 契约，本就正确）。`test/sso-verify.mjs` 的 mock 长出钉钉协议形态（`/oauth2/auth` 授权、`/v1.0/oauth2/userAccessToken` 捕获请求体、`/v1.0/contact/users/me` 断言 `x-acs-dingtalk-access-token` 头），并新增钉钉全流程段断言：登录页按钮、start → authorize 跳转形态（`client_id`/`state`/`redirect_uri`）、未绑定 → 绑定页、第二账号绑定成功、token 请求体驼峰字段（核心回归点）、身份头、`auth.sso_bind` 审计（`ssoId: dingtalk:<unionId>`）与 `ssoIds` 落盘。写修复前已对真实 API 验证：用用户真实凭证，修正后的端点+驼峰请求体把错误从「api not found」/「缺 clientId」推进到「不合法的临时授权码」——客户端已被接受，仅故意伪造的 code 被拒。

## 落选方案

**只换端点、保留 snake_case。** 否决：真机探针已证明该端点要求驼峰，半截修复仍会在首次真实登录时失败。

**改用钉钉 SDK 重写整个 SSO 模块。** 否决：模块刻意零依赖；错的只是换身份这一处调用，state/绑定/审计流程本就有测试且未变。

## 后果

套件 24 → 35 项检查全绿；钉钉分支从此有钉死真实契约的回归网——将来钉钉侧契约再变，会以捕获的请求体不匹配暴露，而不是首次真实登录 502。无配置或落盘格式变化。暴露 bug 的探针顺带完成了凭证验证：用户的 Client ID/Secret 已确认被 api.dingtalk.com 接受。
