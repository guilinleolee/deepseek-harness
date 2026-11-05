# Agent Note: 卡巴格管理台 v2 — 审计日志、登录安全、auditor 落地与配额点数模型

Status: implemented

[English](2026-09-25-kabage-console-v2-security-audit-quota.md) | [中文](2026-09-25-kabage-console-v2-security-audit-quota.zh.md)

## 问题

管理台最初的 9 栏目规划（v1）经开源同类产品（Open WebUI、LibreChat、one-api/new-api、authentik、Logto、FastGPT、Dify）与 DSH 核心实际约束的双重评审后，确认了四个比任何缺失页面都更要紧的缺口：(1) 管理台全部敏感操作——建号/禁用/改额度/重置密码、模型与供应商变更、实例操作、插件投放——**零审计留痕**；(2) 登录无速率限制、无密码策略（README 自己也标注了）；(3) `auditor` 角色只存在于 JWT 角色枚举中，**没有页面也没有 API 权限**；(4) 配额按裸 token 计量，既表达不了不同模型之间数量级的价差，也表达不了按部门的差异化定价。修订版规划 `卡巴格管理台栏目规划v2.md`（随本改动一并提交）把导航重切为 9 栏目，并给出审计事件分类、安全参数与「点数+倍率」配额模型的完整设计；本 Note 覆盖其前两个交付阶段。

## 决策

**审计**。`platform/supervisor/audit.mjs` 经串行 promise 链向 `data/audit.jsonl` 每事件追加一行 JSON（`fs.appendFile`；条目经 `JSON.stringify` 序列化，任何字段中的换行/控制字符都无法破坏行结构）。事件格式统一为 `{ts, actor{account,role,ip}, action, target, result, detail}`，action 按前缀分类（`auth.login_fail`、`member.reset_password`、`model.ratio_change`、`quota.exceeded`、`audit.export`、`security.config_change` 等）。管理台 18 个变更端点与网关三条登录结果全部埋点；deny（审计员试图变更）与 fail（校验失败、异常）路径同样留痕。detail 只放标量——配置型变更带旧值→新值——绝不落密码/密钥原文或会话正文。查询（`GET /console/api/audit`）与筛选导出（`…/audit/export`，ndjson 下载）对 admin 与 auditor 开放；导出动作本身写一条 `audit.export`。

**登录安全**。`security.mjs` 将参数存于 `data/security.json`（缺省自动生成：15 分钟窗口 / 10 次失败 / 锁 15 分钟 / 密码 ≥8 字符且 ≥3 类字符 / 实体名白名单 `^[\w@.\-…]{1,64}$`，放行中文部门名）。网关在校验凭据**之前**先过「账号+IP」内存滑动窗口（被限流的尝试写 `auth.login_rate_limited`）；密码与名称策略在数据入口函数（建号/更新/重置）处拦截，控制台与 CLI 同样被拒。安全设置可在新「安全与审计」页修改（仅 admin 可写，改动记事件）。

**auditor 落地**。管理台门禁在分发前一次性解析 JWT 角色：admin 全通；auditor 放行页面、只读 GET API 与审计查询/导出；任何变更 POST 一律 403「审计员为只读角色」并记 deny 事件；employee 维持 403。判定集中在分发闸门，不散落在各路由 case。

**配额模型 v2**。点数取代裸 token 成为计量单位：`点 = (输入tokens×模型倍率 + 输出tokens×模型倍率×补全倍率) × 分组倍率`，每模型倍率与每部门分组倍率存于 `data/ratios.json`（缺省 1/3/1，在模型页与新「部门与角色」页行内编辑）。relay 预扣估算值（请求字符数/4 为输入、`min(max_tokens,32768)` 为输出）到**只存在于内存 pending Map、从不落账面**的占用上，拒绝判定为 `账面点数 + pending ≥ monthlyPoints`；响应到达后按实际 usage 直接入账并清退 pending（实结 / 失败返还 / 断连返还互斥，由同一个 `settled` 标志保证三选一）。客户端断连会销毁上游请求（取消生成即停止上游计费）、全额返还预扣、requests 计 1、日志记 `aborted:true`——探针实证修复前这条高频路径会同时漏掉预扣沉淀与全部 token 计量。仅持有旧 `monthlyTokens` 的账号保持旧语义（UI/CLI 标注「旧制」）。

**对抗审查驱动的加固**。`__proto__`/`constructor`/`prototype` 键在倍率写入时拒绝、normalize 时剔除、resolve 时视为未配置（仅写入+normalize 过滤仍会留一条 NaN 路径：`groups['__proto__']` 命中原型 getter）；`esc()` 补引号转义（`?actor=` 反射型 XSS、部门名存储型 XSS）；账号变更收敛到串行 `withAccountLock` 队列并以 tmp+rename 原子落盘。

## 落选方案

**预扣直接落账面、仅按账面点数判定**（初版实现）。否决：在「usage 缺失保留预扣」的语义下，攻击者可控的 `max_tokens` 能给受害账号永久沉淀 3×10⁹ 幻影点数，而 `max_tokens=1e308` 产生的 `Infinity` 会被静默丢弃——免费调用。pending Map 模型让账面始终精确，同时让并发未实结预扣参与拒绝判定。

**断连后让上游响应跑完、照常实结**。否决：用户取消就应停止上游生成（真实成本），且「恢复」只在上游恰好已发完时成立——账目语义随时序漂移。统一的「断连=返还预扣、tokens 未知」可预测、可测试。

**把管理台嵌入 DSH `:3080` Web 应用**（v1 规划第五节第 4 条）。架构上否决：Web 前端是假设根路径的预构建 SPA，没有路由或 iframe 挂载点。独立管理台 + 按 Host 路由的网关是唯一不破坏现有集成的方式，也正是平台现行方案。

**引入现成 IAM（Casdoor/Logto）替代自研账号**。暂缓而非否决：若 SSO 需求落地，它仍是阶段 11 的选项；把外部 IdP 与一人一实例网关整合，比补齐本阶段缺口的变化面大得多。

## 后果

已在 worktree 内无密钥验证：`test/security-audit-smoke.mjs` 39 项（策略/限流守卫/审计/配置）、`test/quota-points-smoke.mjs` 40 项（倍率解析、危险键、公式手算对账）、`test/auth-audit-http-verify.mjs` 85 项——对 `test/mock-upstream.mjs` 跑真实 HTTP 流，覆盖登录审计三路径、锁定、守恒（预扣与实结差值）、倍率改动下一请求生效、点数 429 与审计 detail、断连返还、三个端点的 `__proto__` 拒绝、esc 转义、auditor 只读/403 矩阵、旧制 token 硬停。提交前由对抗审查轮（探针脚本，已删除）驱动了上述 P0/P1 修复。

已知遗留：登录页对 429 显示通用失败文案（具体文案仅在 JSON 响应体）；成员行暂无最后登录时间/IP（后续可由审计日志推导）；`add-account`/`set-password` CLI 绕过密码策略（管理员引导通道）；`audit.jsonl` 无轮转（以导出归档为流程）；限流计数为内存态、daemon 重启清零；登录 POST 无 Origin 校验（登录 CSRF，SameSite=Strict 下低危）；尚无把旧 `monthlyTokens` 账号批量换算为点数的 CLI（需先定倍率基线）；共享 NAT 出口下锁定的 IP 维度是集体的。阶段 9+（按蓝图）：实例侧工具 RBAC（`ctx.tools.guard()` + `ctx.approval` 事件回流审计）、个人中心、邀请注册、2FA/SSO/邮件。
