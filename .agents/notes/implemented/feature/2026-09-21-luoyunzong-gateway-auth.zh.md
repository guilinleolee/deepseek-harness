# Agent Note：落云宗认证网关以 Host 子域路由实现实例零改动的登录边界

Status: implemented

[English](2026-09-21-luoyunzong-gateway-auth.md) | 中文

## 问题

任务书阶段 2（`落云宗企业平台任务书.md`）要求登录 + JWT + 实例绑定，验收两条：未登录访问任意入口被拒；用户 A 的会话列表不含用户 B 的 session id。DSH 的 web 栈刻意没有认证层（`client/connection` 对 `0.0.0.0` 的禁用注释写着"直到真正的认证层出现"；webserver README 声明"No TLS, auth, or origin policy"），而任务书禁止在扩展点够用时改动 harness 本体。悬而未决的问题是：认证放在哪，才能让假设根路径 URL（`/api` 与两条 WebSocket 下行）的 DSH web SPA 原样工作？

## 决策

在 supervisor 内做一个认证反代网关（`platform/supervisor/gateway.mjs`，零依赖），取代阶段 1 的落地 portal。路由**按 Host 头、绝不做路径前缀**：`<实例id>.localhost:8460` 原样反代到 `127.0.0.1:<实例端口>`，绝对路径的 API 调用与 WebSocket 升级原样穿透。实例侧只有两个启动参数变化、都是既有 CLI flag 而非新代码：`--host 127.0.0.1`（真实服务器上员工物理上绕不过网关）和 `--trusted-host <id>.localhost:8460`（实例自己的 DNS-rebinding 信任围栏接受转发来的 Host——围栏那句"直到真正的认证层出现"的注释正是任务书预言的挂点）。

认证语义：账号存 `data/accounts.json`，密码 scrypt 加盐哈希；登录（`POST /api/auth/login`，任何主机名可登录，Cookie 落在用户实际访问的子域上）签发手写 HS256 JWT（30 分钟），以 HttpOnly + SameSite=Strict 的 host-only Cookie 下发；每个反代请求与每次 WebSocket 升级都重新校验令牌、账号 `tokenEpoch`（`revoke --account` 递增即全端立即失效）和账号↔实例绑定——绑定从账号存储**实时读取**，改绑无需撤销令牌即生效。`/status.json` 仅 admin。发往 `/api/events.mux` 与 `/api/events.host` 的 WebSocket 升级先认证再做原始字节隧道（路径取自 `client/connection/src/api-path.ts`，即 SPA 真实的升级路由）。

验证（curl `--resolve` 顶替浏览器的 `*.localhost` 原生解析，无需改 hosts）：未登录子域 HTTP 401 + WS 401；已认证 WS 握手返回 101 且 `Sec-WebSocket-Accept` 由实例计算——端到端字节隧道成立；admin→绑定实例 200，把 admin 令牌重放到另一实例 403；两个实例 home 的 session id 集合互斥（A 的会话列表来源只是 A 的实例 home）；revoke 后旧令牌 401、重登 200；`/status.json` 匿名 401、admin 200、员工 401。

## 已否决的替代方案

**在 harness web 栈内做认证插件。** 否决：网关以零 harness 改动实现同一边界；进 harness 会把 OS 相关的代理代码拖进 100% 覆盖率的工作区门，还把安全边界拆到两个进程里。

**路径前缀反代 + `<base>` 注入。** 否决：`fetch('/api')` 与 WebSocket 构造器对根相对 URL 不理会 `<base href>`，SPA 的绝对路径照样打空；对一个假设根路径的应用做路径重写是打不赢的仗。

**开发机改 hosts 文件造子域。** 没必要：浏览器原生把 `*.localhost` 解析到 127.0.0.1（RFC 6761），curl 测试用 `--resolve`。

**纯会话 Cookie 不用 JWT。** 选择无状态令牌 + 每账号 epoch：撤销不需要会话存储，阶段 3 控制面引入 refresh 轮换时网关的路由角色不变。

## 后果

阶段 2 两条验收在实例零改动下成立：入口拒绝发生在网关（HTTP 与 WS），跨用户会话不可见由构造保证（绑定 + 按 home 存储）。代价与未尽事项：登录无速率限制、网关无 TLS——仅内网/回环 MVP 可接受，生产前必须补（前置 TLS 反代）；Cookie 按子域 host-only，用户每访问一个实例要登录一次（生产的通配符域 Cookie 会消掉这一点）；令牌是 30 分钟纯 access、无 refresh 轮换，留给阶段 3 控制面；账号文件存哈希但与其他数据同盘，真实控制面数据库会替换它。测试期间还发现 `stop` 的 daemon 分支残留一处 fire-and-forget `taskkill`（陈旧 daemon 一直占着 8460、还用旧参数重拉了实例）；stop 现在逐一等待每次杀进程完成。
