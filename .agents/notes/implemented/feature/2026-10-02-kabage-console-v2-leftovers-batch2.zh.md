# Agent Note: 卡巴格 console v2 遗留六项收口（轮转/限流持久化/Origin/迁移/NAT/CLI 策略）

Status: implemented

[English](2026-10-02-kabage-console-v2-leftovers-batch2.md) | 中文

## 问题

2026-09-25 的管理台 v2 笔记记录了六项遗留，每一项都是已知 MVP 限制且有具体失效方式：审计日志无限增长；限流状态随 daemon 重启清零（攻击者靠等重启脱离锁定，崩溃恢复也会丢锁定）；登录/TOTP POST 没有同源校验（登录 CSRF：攻击者页面可用自己的凭据把受害者浏览器提交到 `/api/auth/login`，把受害者静默登进攻击者账号）；注册限流只按 IP 计数（NAT 办公室共享一个桶，一个人手误锁全办公室注册）；旧制 `monthlyTokens` 额度没有迁到点数模型的路径；CLI 建号/改密绕过管理台强制执行的密码策略。

## 决策

**审计轮转。** `audit.jsonl` 按大小轮转：每次追加前，audit.mjs（现读 security.json）比对所记 active 文件字节数与 `auditRotateBytes`（缺省 16MB，区间 1KB–1GB），超线即把 active 改名 `audit-<时间戳>.jsonl` 并只保留最新 `auditKeepArchives`（缺省 4）份归档、删除更早的。轮转在既有的追加串行链内执行，无并发改名窗口；任一步失败降级为继续写入当前文件。`auditQuery` 按 active→归档（新到旧）逐文件扫描，每个文件只取填满 `limit` 所需的最新条目——小限额查询（/me 设备列表、管理台 500 条页）只读最新文件的尾部，不限量的导出自然覆盖归档全量。归档文件名含时间戳，文件名排序即时间排序。

**限流桶持久化。** `createLoginRateGuard(getLimits, persistence)` 新增可选 `{dataDir, file}`：创建时载入桶（过期条目丢弃），每次 `fail`/`success`/check 触发锁定即原子重写文件（tmp+rename；写失败只记 stderr，不影响内存判定）。网关用 `data/rate-limits.json`，注册用 `data/register-limits.json`——两个 guard 实例两个文件，互不覆盖。文件只存活条目（有失败计数或未过期的 `lockedUntil`），自然回缩。

**登录同源校验。** portal.mjs 本地的 `sameOrigin` 导出，应用在网关 `/api/auth/login` 与 `/api/auth/totp` 顶部：`Origin` 存在且 host 与 `Host` 不符，在任何状态变更前 403。无 Origin（curl/测试/服务调用）放行——与管理台 POST 端点同一取舍，叠加在 `SameSite=Strict` 之上。

**旧制→点数迁移。** `quotas.migrateLegacyQuotas(dataDir)` 把 `monthlyPoints` 设为 `monthlyTokens` 同值（1:1——旧判据本就按裸 tokens 比较，生效线不变，控制台「旧制」标注消失），不动已迁移/不限额账号，一次原子写盘，幂等。经 `supervisor.mjs migrate-points` 暴露，逐账号报告。

**NAT 注册分桶。** 注册失败按邀请码有效性选桶：无效/缺失码计入 IP 桶（攻击者换码重试也共享计数，撞码穷举照旧被限流）；有效码计入「邀请码+IP」桶——同事的密码手误不再把共享出口的整间办公室锁在自己邀请之外。IP 桶仍最先判定，撞码锁定照样拒持有有效邀请者（原语义保留）。

**CLI 策略收口。** `checkPasswordPolicy` 现在在 `addAccount`/`setPassword` 内强制（每次现读 security.json）：控制台、注册页、IdP 同步与 CLI 共用一个约束，CLI 无绕过面。CLI 自动生成密码从 `randomBytes(9).base64url`（不保证三类字符）换成 `generatePassword()`——策略测试已证明其连续 20 个全合规。

## 落选方案

**按时间（月）轮转审计。** 否决：本项针对的失效方式是无限增长，按大小即封顶，无须日历耦合；按月命名会暗示一个清理器并不按月保留的保留承诺。

**注册限流只按邀请码分桶。** 否决：攻击者轮换编造的码，每次猜测都拿到新桶；双层分桶里的 IP 桶正是为这种情况保留的。

**每次 check 都持久化。** 不必要：check 只在触发锁定时改状态（在那时落盘）；纯读保持纯读。

**按换算比迁移（tokens→点数）。** 否决：点数有自己的语义（模型/分组倍率），发明换算会改变生效线；1:1 保住运营者设过的值。

## 后果

九套 458 项全绿（原 426）：smoke +20（持久化重建语义、轮转归档/保留/跨档查询、存储层策略、新参数区间）、quota smoke +5（1:1、隔离、幂等）、me-invite +7（登录/TOTP 跨域 403、邀请码桶锁定、同 IP 换码成功）。运维须知：轮转删除的归档不可恢复（如需超出 `auditKeepArchives` 的保留请先导出）；`rate-limits.json` 意味着锁定现在按设计跨越重启——手工解锁 = 删除该文件；`migrate-points` 与既有 CLI 命令同样存在对运行中 daemon 的写窗口（管理台空闲时执行）。console v2 遗留项至此全部关闭；平台其余 backlog 不变（2FA 硬强制 11b、TOTP 重放计数、账号级限流桶、guard 审批组、各项真机验证）。
