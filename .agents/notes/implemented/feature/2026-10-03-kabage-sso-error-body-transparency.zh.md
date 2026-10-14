# Agent Note：SSO 失败报错带上供应商响应体

Status: implemented

[English](2026-10-03-kabage-sso-error-body-transparency.md) | 中文

## 问题

`resolveSsoIdentity` 在供应商接口失败时只抛「HTTP 状态码」（如「钉钉用户接口失败（HTTP 403）」），而 403 类失败的真正原因——权限未开通、应用未发布、不在可见范围——只存在于响应 body 里。真机验证钉钉 SSO 时用户只看到 403，无法自助定位，每轮排障都要多猜一次。

## 决策

新增 `errBody(res)`：非 2xx 响应的 body 截断 300 字符追加进异常文案（四个抛错点：企微/钉钉的 token 与用户接口），取 body 失败时静默降级为空串。门户的错误页会把它连同原句一起展示，钉钉的 `code`/`message` 原话直接可见。

## 后果

下次真机失败将显示钉钉的原话（如 `{"code":"Forbidden","message":"..."}`），排障从猜测变为直读。既有 35 项断言不校验这些文案，全绿不变；无配置或落盘格式变化。
