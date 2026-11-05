# Agent Note: 卡巴格管理台阶段 9-12 — 工具 RBAC、个人中心与邀请、TOTP/邮件/SSO、管理工具挂平台

Status: implemented

[English](2026-09-26-kabage-console-stages-9-12.md) | [中文](2026-09-26-kabage-console-stages-9-12.zh.md)

## 问题

蓝图阶段 9-12（`卡巴格管理台栏目规划v2.md` 第七节）补齐安全/审计/配额两期之后的四个能力缺口：(1) 实例内 agent 可以无约束地使用命令行、文件、联网工具，没有按角色的管控；(2) 员工没有任何自助入口——改密、查额度、下线设备全要找管理员；(3) 没有第二验证因子、没有对外通知、没有企业 SSO；(4) DSH agent 无法代管平台本身（即最初规划的 `user:*` 工具清单）。四个阶段全部落在既有平台上：零依赖 Node ESM、`data/*.json` 存储、单 daemon 宿主 gateway+relay+console+supervisor 循环、一人一 DSH 实例。

## 决策

**阶段 9 —— 实例级工具 RBAC。** 一人一实例，所以策略按实例生效：`data/toolpolicy.json` 把角色映射到被拒工具组（`command` = bash/pwsh/terminal_*，`fs` = read/write/edit/glob/grep/str_replace_editor/read_image，`network` = web_search/web_fetch；其余放行）。控制台接口与「部门与角色」页把策略变更直接写入每个绑定实例的 `<home>/tool-policy.json`——插件经 mtime+size 缓存热加载，无需重启。`platform/plugins/kabage-tool-guard/` 注册全局 `ctx.tools.guard()`（已核实的契约：返回字符串即拒绝并呈现 `Error: <理由>`，守卫没有放行权；守卫抛错只失败当笔调用）。策略文件缺失=放行（管理员实例可以没有策略文件）；存在但非法=fail-loud。拒绝事件追加到 `<home>/guard-events.jsonl`；supervisor 既有的磁盘采样器每 30 秒把新行转写进平台审计（`guard.deny` 事件），且仅在文件指纹（mtime+size）未变时才截断。

**阶段 10 —— 个人中心 + 邀请注册。** 门户主机的 `/me` 服务员工（登录后自动跳转；管理员/审计员同样可用）：资料、改密（策略校验后 token epoch+1 全端下线）、本人当月点数用量（点数/旧制/不限三种渲染）、最近 5 次登录（审计日志精确匹配过滤）、下线所有设备。邀请只存 192-bit code 的 SHA-256；注册以常数时间比较校验，对已用/过期/撤销返回稳定原因码，经与建号完全相同的 `addAccount` 路径创建账号（白名单+密码策略+scrypt），签发虚拟钥匙、同步实例工具策略，**只有成功才消耗邀请码**——失败绝不烧码。公开注册端点以独立 per-IP 计数桶共享登录限流参数。

**阶段 11 —— TOTP、邮件、SSO。** `totp.mjs` 手写 RFC 4648 base32 与 RFC 6238（HMAC-SHA1、30s 步长、±1 窗口），以 RFC 附录 B 官方向量验收。密文 AES-256-GCM 加密落盘（密钥派生自既有 `auth-secret.key`）；登录改为两段式——密码正确返回 `{totp_required:true}` 且不发 cookie，`POST /api/auth/totp` 通过才签发会话。TOTP 失败与登录共享限流桶，且密码正确**不清零**失败计数（偷到密码的人无法无限猜码）。密文损坏的记录**fail-closed**：拒绝登录并给出救援文案、写 `security.twofa_broken` 审计事件、管理台重置按钮是唯一恢复路径。安全设置里的 `require2faRoles` 是软提示（横幅）而非硬锁——锁死最后一名管理员比晚开 2FA 更糟。邮件支持 `off`/`file`/`smtp`（手写最小客户端：多行 EHLO、宣告才 STARTTLS、AUTH LOGIN、应答码白名单、配置保存时拒绝 CRLF 注入）；配额告警在 80% 时每账号每月至多一次（在 usage 互斥锁内记账），账号变更通知绝不含密码内容，发送失败以 resolve 而非 reject 收尾——relay 主链路永远不会被邮件拖崩。SSO 交付企业微信与钉钉 OAuth 适配器，完全由 `data/sso.json` 驱动（密钥 GCM 加密、`authorizeBase`/`apiBase` 可配）：一次性 state、10s fetch 超时、state 表上限溢出 429、绑定走密码验证页且整体在 `withAccountLock` 内、未启用的 provider 一律拒绝。

**阶段 12 —— 平台管理工具挂 DSH。** `data/service-tokens.json` 存 `kbsvc-…` Bearer 令牌的 SHA-256，两级角色（admin、readonly——readonly 是只读 API 精确路径 Set 白名单、默认拒绝、拒绝留审计）；撤销经 mtime 缓存下一请求生效；审计 actor 记为 `svc:<名称>`。`platform/plugins/kabage-admin-tools/` 注册七个工具（list/quota-query/audit-query 只读；create/update/reset-password/disable 变更），经 HTTP 调平台 API：显式 `inject:['tools']`、`presentCall` generic 呈现、所有动态参数 `encodeURIComponent`、`exec.signal` 透传、结果 50 行截断、401/403/4xx/网络错转译为中文结果。create/reset 返回的一次性密码附带「请尽快改密」提示，README 单列警示：管理员实例的会话记录将包含这些敏感结果。e01 的 env 预留 `KABAGE_SERVICE_TOKEN`（空占位；真实令牌由 CLI 生成后管理员手工填入——插件报 `token_missing` 中文错误而不是发出空凭据）。

**审查驱动的加固**（阶段 9-12 共三轮对抗审查，含探针实证）：写入/normalize/resolve 三层危险键过滤、`esc()` 引号转义、断连返还的单 `settled` 标志、严格预扣记账、注册队列必被响应、审计精确匹配过滤、转写截断的指纹守卫、上述 TOTP fail-closed、SSO 超时/上限/加锁、SMTP 应答码白名单与「发送失败从 reject 改 resolve」（一个潜在的 unhandled rejection 崩溃）、service-token 缓存按 dataDir 键控。

## 落选方案

**阶段 9 的 approval 组**（deny 之外的 `approval` 清单）。暂缓：守卫契约只支持拒绝，接 `ctx.approval` 需要实例侧管线，值得独立一个切片——字段已进策略 Schema，将来启用是纯增量。

**2FA 硬强制注册**（`require2faRoles` 阻断登录）。否决：密钥丢失或认证器损坏会锁死最后一名管理员且无自助恢复；软提示+管理台重置保留救援可能。

**TOTP 密文解密失败时 fail-open**（初版把解密失败当作「未绑定」）。审查后否决：密钥轮换或文件损坏会让已启用账号静默退化为单因子、`enabled:true` 卡死（无法自行重绑）、且审计零痕迹。fail-closed 加显式救援路径只多一个状态，三害全消。

**按令牌角色条件注册变更工具。** 否决：这会让工具注册依赖启动时探测令牌权限；改为全部注册、平台 403 转译为中文工具结果——授权判定只有平台一个事实源。

**等真实企业微信/钉钉凭证再交付 SSO。** 否决：两个适配器完全由配置驱动且 API base 可配，本地 mock OAuth 服务器即可演练 授权→回调→绑定→直达登录 全流程；真实凭证是配置问题不是代码问题。

## 后果

worktree 内零依赖验证：十一套测试共 575 项断言全绿（43+40+32+85+63+55+47+24+26+58+42），含对 mock 上游/供应商/SMTP 对端跑真实 HTTP 网关流；两个插件均通过真实 `precheck` 启动（隔离 home、pnpm 安装、插件加载注册、健康 200——35s 与 42s）。三轮对抗审查最终无 P0；五项 P1 与可消化的 P2 全部在提交前带断言修复。

已知遗留：TOTP 同码窗口内重放（尚无 last-used counter，上界约 90 秒）；无账号级全局限流桶（account+IP 桶随攻击者 IP 数线性放大）；`require2faRoles` 硬强制；guard 的 `approval` 组；真实外网 SMTP 与真实企业微信/钉钉端到端（均为配置门控、已 mock 验证）；真实 LLM agent 工具调用链（需有余额上游——部署路径已备好：`add-service-token`、填 e01 env、`plugin-push`、activate）。运维注意：部署必须保留生产 `instances.json`（网关 `0.0.0.0`）并合并 e01 的 env 占位；本沙盒环境跑插件 push 历史上会在负载下失败——如需手工执行，确切命令在平台 README。
