# kabage-admin-tools —— 管理类 DSH 工具（卡巴格平台阶段 12）

Cordis 插件：向实例注册 7 个经 HTTP 调用平台 console API 的管理工具，让
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

**未配置 token 时工具不崩**：调用返回中文配置错误（原因码 `token_missing`）。

## 工具清单

| 工具 | 参数 | 说明 |
|---|---|---|
| `user_list` | — | 成员列表（账号/部门/角色/启用/实例/当月点数摘要）；≤50 条 |
| `user_quota_query` | `account` | 当月点数/额度/余量（旧制 tokens 账号按旧口径标注） |
| `audit_query` | `action?` `actor?` `limit?≤50` | 平台审计查询（最新在前） |
| `user_create` | `account` `department?` `role?` `password?` `instance?` | 建号+签发虚拟钥匙；**一次性密码在结果中返回** |
| `user_update` | `account` `department?` `role?` | 改部门/角色（role 仅 employee/auditor） |
| `user_reset_password` | `account` | 重置密码（一次性新密码返回，全端下线） |
| `user_set_disabled` | `account` `disabled` | 禁用（下线+吊销钥匙）/启用 |

错误转译：平台 401 → `auth_failed`；403 → `forbidden`（readonly 令牌调变更
工具）；其他 4xx 透传平台中文文案；网络不可达 → `unreachable`。模型收到的
均为 `Error: <中文理由（含原因码）>`。

## 安全决策与警示

1. **不探测令牌角色**：7 个工具始终注册；readonly 令牌调用变更工具时由
   平台侧 403 转译为中文错误——注册逻辑与令牌角色解耦（换令牌无需重启实例）。
2. **会话记录含敏感结果**：`user_create` 与 `user_reset_password` 的一次性
   密码会留在管理员实例的会话日志（模型上下文）中。缓解：结果附带
   `notice` 提示引导成员尽快改密；密码同时可在管理台成员页重置。管理员
   应仅将本插件装入可信的管理员实例（e01），并避免把会话记录导出到
   低信任存储。
3. **服务令牌 = 管理凭据**：能读到它即能以对应角色调用管理台 API（readonly
   仅只读白名单）。只经 env 注入可信实例，绝不进仓库与日志；撤销经
   `revoke-service-token`，下一请求即生效。

## 测试

```sh
node platform/plugins/kabage-admin-tools/test/admin-tools-test.mjs
```

本地 mock 平台服务器（node:http）断言：请求路径/方法/鉴权头、响应到工具
结果的映射、401/403/4xx/网络错误转译、列表截断、token 缺失配置错误。
