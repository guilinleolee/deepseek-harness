# Agent Note: 卡巴格平台 11b 收官——2FA 硬强制、TOTP 重放、账号级限流、审批组、令牌页、角色矩阵

Status: implemented

[English](2026-10-02-kabage-platform-11b-final.md) | 中文

## 问题

六项 backlog 关掉了平台遗留清单：2FA 硬强制（11b——软强制横幅只是提醒）、TOTP 重放（一个被窃验证码在整个 30 秒片内可用两次）、分布式攻击者可绕过的限流（账号+IP 桶意味着 N 个 IP 买 N 份新预算）、guard 审批组（危险工具只有允许/拒绝两态——没有按次审批，审批事件也到不了平台审计）、令牌与配额页（栏目 5——虚拟钥匙只能作为成员操作的副作用来管理）、角色矩阵编辑（权限矩阵是硬编码门禁的静态截图）。

## 决策

**2FA 硬强制 = 受限会话，不是拒绝。** 显而易见的设计（登录 403）会死锁：自助绑定发生在 /me，而 /me 需要会话。现在登录总是签发会话；当 `require2faRoles` 命中未绑定账号时，JWT 带 `enr:1`，网关对工作区子域的一切请求（HTTP 与 WS）返回指路绑定的 403。/me 与 /console 保持可达——员工能自己完成绑定，误配置的管理员能自己改回配置而不是被锁死。`supervisor.mjs reset-twofa --account` 是服务端救生门（审计 `security.2fa_reset` via cli）。SSO 登录共用 `issueSession`，同样受限。

**TOTP 重放。** `verifyTwofaForLogin` 解出命中的时间片并持久化为账号记录的 `lastStep`；时间片 ≤ `lastStep` 的验证码被拒（RFC 6238 §5.2）。配置阶段（confirm）有意不烧片——绑定与首次登录常共享同一个 30 秒窗口，烧片会把刚绑定的用户卡住最多 30 秒。

**账号级限流桶。** 登录限流器现在同时把失败计入 `account|*` 桶，上限 `accountMaxFails`（security.json，缺省 50，区间 5–500）：针对单账号的分布式攻击锁定该账号本身，与登录桶同一份 `rate-limits.json` 持久化。空账号桶（注册限流）不设全局层。`success` 清零两层。

**guard 审批组。** `tool-policy.json` 新增可选 `approve` 组列表（deny∩approve 相交即结构非法）。guard 插件现在还注册 `tools/pre-execute` 瀑布监听：命中 approve 组的调用返回 `{kind:'ask'}`，由 DSH 工具管道送审批缝——员工收到产品内审批提示，`approval/asked`/`approval/decided` 落实例会话日志，拒绝转为模型可见错误。为让平台审计可见（管理员永远不能读实例会话日志——隐私决定 5），插件按 id 配对 `asked→decided` 写桥事件 `decision=approval-allowed/denied/cancelled/unavailable`；daemon 转写为 `guard.approval`（批准 result=ok，其余 deny）。管理台角色页的工具组从勾选变三态：允许 / 每次审批 / 拒绝。

**令牌与配额页**（`/console/tokens`）：钥匙签发（`token.issue`）与按账号吊销（`token.revoke`）从成员页副作用中独立；token 明文只在签发响应出现一次（审计不落明文，与 CLI 一致），下半页是只读的当月点数总览，补齐栏目 5。

**角色矩阵编辑。** `data/role-matrix.json` 只存对缺省值的 sparse 覆盖（缺省=现行硬编码行为：admin 全开、auditor 只读+审计导出、employee 全否）。管理台中心门禁改为查它：页面/只读访问查 `console.read`，每个变更 POST 经 `POINT_FOR_PATH` 映射权限点，审计导出查 `audit.export`——每次请求现读，改动即生效。admin 行服务端固定不可改（改矩阵本身是 `security.change`，admin 永远可执行——不自锁）。admin 服务令牌保留阶段 12 变更权；readonly 得到显式拒绝并留痕。

## 落选方案

**裸 403 硬强制。** 否决——上面的绑定死锁；受限会话形式给出同样的工作区保证，同时留足逃生门。

**confirm 烧片。** 否决——它惩罚正常的绑定后登录流，而 confirm 不是认证事件。

**全局桶与单 IP 同阈值。** 否决——一个 NAT 办公室或手抖的密码管理器就会在正常使用中触发；50（单 IP 缺省的 5 倍）只在真正的分布式猜测下触发，且可配置。

**在 guard 回调里做审批。** 做不到也不该做：`ToolGuard` 按契约是同步的（"guards have no allow result"）；`pre-execute` 瀑布是管道设计的 ask 通道，策略检查与审计配对本就归它。

**把权限矩阵做成自由角色定义。** 否决——角色固定三个，缺的是对既有门禁的开关。对现行行为的 sparse 覆盖让安全模型可评审、缺省与已上线行为完全一致。

## 后果

十套 573 项全绿（原 458）：twofa +8（重放、下一片放行、工作区 403/绑定可用/绑定恢复——用原生 Host 头请求验证）、smoke +6（全局桶锁定/清零/持久化、空账号豁免）、auth-audit +23（令牌页/API/审计含无明文、矩阵授权/回收/恢复、admin 行与未知点拒绝、employee console.read 授予）、toolpolicy +6（审批决定转写）、guard +14（approve 校验/ask/next 放行、桥配对与过滤）。运维须知：审批组要在实例生效需重推 guard 插件（`plugin-push`/`plugin-activate`）——旧部署的 deny 路径不受影响；`reset-twofa` 加入 CLI；`accountMaxFails` 与矩阵改动无需重启。遗留清单至此清空，只剩既有的真机验证项（有余额上游、真实 SMTP、真实企微/钉钉 SSO）。
