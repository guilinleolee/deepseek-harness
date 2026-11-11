# kabage-admin-tools —— 管理类 DSH 工具（卡巴格平台阶段 12）

Cordis 插件：向实例注册 9 个经 HTTP 调用平台 console API 的管理工具，让
**可信实例**里的管理员 agent 直接执行成员管理、用量查询与审计检索。全部
调用以服务令牌（`kbsvc-…`，`Authorization: Bearer`）鉴权。零 npm 依赖
（仅 peer `@deepseek-ai/cordis`，经 profile 兜底目录解析）。

## 安装（平台 push 流程）

```sh
cd platform/supervisor
node supervisor.mjs plugin-precheck --plugin ../plugins/kabage-admin-tools
node supervisor.mjs add-service-token e01-admin            # 明文只显示一次
node supervisor.mjs plugin-push --plugin ../plugins/kabage-admin-tools --ids e01
node supervisor.mjs plugin-activate --id e01               # 重启生效
# 然后把明文 token 填入 instances.json e01.env 的 KABAGE_SERVICE_TOKEN 并重启实例
```

## 配置（cordis.patch.yml，`!!js` 读 env）

| 键 | env 回退 | 说明 |
|---|---|---|
| `token` | `KABAGE_SERVICE_TOKEN` | 服务令牌（**管理凭据，仅注入可信实例**；仓库不含任何真实值，由管理员 `add-service-token` 生成后手工填入） |
| `baseUrl` | `KABAGE_ADMIN_BASE_URL` | 平台管理接口地址，缺省 `http://127.0.0.1:8460` |
| `defaultInstance` | `KABAGE_ADMIN_DEFAULT_INSTANCE` | user_create 缺省绑定实例，缺省 `e01` |
| `timeoutMs` | `KABAGE_ADMIN_TIMEOUT_MS` | 单请求超时毫秒，缺省 `10000`（与平台侧抓取上限同量级） |
| `maxResponseBytes` | `KABAGE_ADMIN_MAX_RESPONSE_BYTES` | 响应体上限字节，缺省 `5242880`（5MB），超过即报错而非撑爆上下文 |
| `retryBackoffMs` | `KABAGE_ADMIN_RETRY_BACKOFF_MS` | 5xx 重试前退避毫秒，缺省 `250` |
| `retryMutations` | `KABAGE_ADMIN_RETRY_MUTATIONS` | 写操作是否自动重试（`1`/`true`），**缺省关**（见「安全决策」第 5 条） |
| `allowInsecureHttp` | `KABAGE_ADMIN_ALLOW_INSECURE_HTTP` | 是否允许「明文 HTTP + 非回环」地址（`1`/`true`），**缺省关** |

**未配置 token 时工具不崩**：调用返回中文配置错误（原因码 `token_missing`）。

## 工具清单

| 工具 | 参数 | 说明 |
|---|---|---|
| `user_list` | `q?` `department?` `role?` `disabled?` `instance?` `sort?` `order?` `limit?≤50` | 成员列表（账号/显示名/部门/角色/启用/实例/当月点数摘要）；支持过滤与排序，≤50 条 |
| `user_quota_query` | `account` | 当月点数/额度/余量（旧制 tokens 账号按旧口径标注） |
| `audit_query` | `action?` `actor?` `limit?≤50` | 平台审计查询（最新在前）；`truncated` 只在确有更多条目时为真 |
| `user_create` | `account` `displayName?` `department?` `role?` `password?` `instance?` | 建号 + 签发虚拟钥匙；**一次性密码与 vkey 在结果中返回一次** |
| `user_update` | `account` `displayName?` `department?` `role?` | 改显示名/部门/角色（role 仅 employee/auditor，非法值显式报错） |
| `user_reset_password` | `account` | 重置密码（一次性新密码返回，全端下线） |
| `user_set_disabled` | `account` `disabled` | 禁用（下线 + 吊销钥匙）/启用 |
| `user_set_quota` | `account` `points?` | 设月度点数额度（**留空 = 不限**；平台按点数硬停） |
| `user_reset_2fa` | `account` | 重置 2FA 绑定（成员丢失认证器的救援操作；解绑后登录只需密码） |

### 一次性凭据语义（vkey / 密码）

平台 `POST /console/api/member/create` 内部 `issueVkey()` 只在**这一次响应**
里给出虚拟钥匙明文（`vk-…`），存储侧只留 SHA-256 `tokenHash`；`user_create`
因此把 `vkey` 与一次性密码一并回传，并在结果里带 `sensitiveFields` 与醒目
警示语（`notice`）。**丢失即不可找回**：成员拿不到钥匙时需在管理台「令牌与
配额」页重新签发一次（`member/enable` 会重签但平台侧丢弃明文）。

### 错误分层（稳定原因码）

| 情况 | 工具错误（中文） | 原因码 | 模型该怎么判断 |
|---|---|---|---|
| 未配置服务令牌 | 平台管理工具未配置服务令牌… | `token_missing` | 找管理员配 token，不要重试 |
| 明文 HTTP + 非回环地址 | 插件已拒绝向该地址发送服务令牌… | `insecure_transport` | 改地址（https / 回环），不要重试 |
| 平台 401 | 平台认证失败：服务令牌无效或已被撤销… | `auth_failed` | 找管理员换令牌，不要重试 |
| 平台 403 | 权限不足：readonly 服务令牌不能执行变更操作… | `forbidden` | 换 admin 令牌，不要重试 |
| 平台 404 | 账号不存在或目标不存在：平台返回「…」 | `not_found` | 先查账号是否存在 |
| 平台 429 | 平台限流：请求过于频繁… | `rate_limited` | 稍后重试 |
| 平台 5xx | 平台故障：平台内部错误（HTTP xxx），可稍后重试 | `platform_error` | 可重试 |
| 其他 4xx | 平台拒绝该操作（xxx）：<平台中文文案> | `rejected` | 按平台文案改参 |
| 请求超时（10s） | 平台管理接口响应超时… | `timeout` | 可重试 |
| 外部取消 | 工具调用已被外部取消 | `aborted` | 不重试 |
| 网络不可达 | 无法连接平台管理接口（…） | `unreachable` | 确认 daemon 在跑 |
| 响应体超限 | 平台响应体过大…已中止解析 | `response_too_large` | 缩小规模/让平台侧加分页 |
| 非法角色 / 非法额度 / 非法过滤值 | 参数 … 取值非法… | `invalid_role` / `invalid_points` / `invalid_parameter` | 改参，不要重试 |

模型收到的均为 `Error: <中文理由（含原因码）>`。错误文案不回显服务令牌，也不
回显 URL 内嵌凭据。

## 安全决策与警示

1. **不探测令牌角色**：9 个工具始终注册；readonly 令牌调用变更工具时由
   平台侧 403 转译为中文错误——注册逻辑与令牌角色解耦（换令牌无需重启实例）。
2. **会话记录含敏感结果**：`user_create` 与 `user_reset_password` 的一次性
   密码**与 vkey** 会留在管理员实例的会话日志（模型上下文）中。缓解：结果附带
   `notice` 提示引导成员尽快改密并立即转交本人；密码同时可在管理台成员页重置。
   管理员应仅将本插件装入可信的管理员实例（e01），并避免把会话记录导出到
   低信任存储。
3. **UI 卡片脱敏**：工具参数可能带 `password` / `vkey` / `token`，`presentCall`
   渲染的卡片内容一律对敏感字段打码（`***（已脱敏）`），明文凭据不进卡片与
   轨迹记录；**但工具结果本身仍含明文**（模型需要它转交成员），这是既定取舍。
4. **服务令牌 = 管理凭据**：能读到它即能以对应角色调用管理台 API（readonly
   仅只读白名单）。只经 env 注入可信实例，绝不进仓库与日志；撤销经
   `revoke-service-token`，下一请求即生效。
5. **重试策略**：5xx 自动重试 1 次（250ms 退避）**只对只读 GET 生效**；写操作
   默认不自动重试——`member/create` 幂等性未知，自动重试可能重复建号。需要时
   用 `retryMutations=1` 显式开启。
6. **传输安全**：`baseUrl` 若是「明文 HTTP + 非回环地址」，Bearer 令牌会在网络
   上明文传输——插件**默认直接拒绝**（`insecure_transport`）且不发出请求；确需
   内网明文时用 `allowInsecureHttp=1` 放开，此时每个结果都会附带高危告警字段
   `securityWarning`。

## 已知限制（平台侧，插件无法绕开）

- **成员列表无分页**：平台 `member/list` 一次性返回全部成员，插件只能在客户端
  过滤并截断到 ≤50 条；成员规模大时响应体会很大，超过 `maxResponseBytes` 即报
  `response_too_large`（不解析、不灌上下文）。根治需平台侧加分页。
- **建号端点忽略 `department`**：平台 `member/create` 未把 `body.department`
  传给 `addAccount`，建号时带的部门会被丢弃——插件在建号后自动补发一次
  `member/update` 落部门（幂等写；补写失败会写进结果的 `warnings`）。
- **`member/enable` 重签的 vkey 被平台侧丢弃**：启用成员时平台会重签一把钥匙
  但不返回明文，需要的管理员请在管理台「令牌与配额」页查看。

## 测试

```sh
node platform/plugins/kabage-admin-tools/test/admin-tools-test.mjs
```

本地 mock 平台服务器（node:http，127.0.0.1 随机端口，不触外网）断言：请求
路径/方法/鉴权头、响应到工具结果的映射、9 个工具的注册形态、错误分层与稳定
原因码、列表过滤/排序/截断、audit 截断判定、5xx 重试（GET 重试 / 写操作不
重试）、超时与外部取消、响应体闸门、非回环明文 HTTP 拦截与 opt-in 告警、
vkey 回传与 UI 卡片脱敏、非法角色显式报错、一次性凭据警示语。
