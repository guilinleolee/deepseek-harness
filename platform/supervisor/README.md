# @luoyunzong/supervisor —— 落云宗企业平台阶段 1–6 全量交付（实例编排/认证网关/Relay 密钥代理与计量配额/漂移对齐/插件治理）

按 [任务书](../../落云宗企业平台任务书.md) 交付的服务端组件：把每个员工实例拉起为一个独立 DSH web 进程（独立 `DSH_HOME` + 独立端口 + 名义 uid），提供健康检查、崩溃自动重启、实例页数据；**认证网关**（阶段 2）：登录签发 JWT Cookie，按 `Host` 把已认证请求反代到该账号绑定的实例；**Relay 密钥代理与计量配额**（阶段 3–4）：真实上游 Key 的唯一容身处，实例只持可吊销的虚拟钥匙，月度 Token 额度硬停；**漂移对齐**（阶段 5）：授权集 vs 实例自报生效集比对，差异按时限标红；**插件治理**（阶段 6）：真启动预检 → 暂存 → 重启生效 → 禁用/回滚。**独立于 harness**：不修改 `packages/` 任何代码，零第三方依赖，也不在 pnpm workspace 内。

## 用法

```sh
cd platform/supervisor
node supervisor.mjs add-account <email> --instance e01 --role admin [--password <pw>]
                                # role ∈ admin|auditor|employee；不给密码则自动生成并打印
node supervisor.mjs list-accounts
node supervisor.mjs revoke --account <email>   # epoch+1，该账号全部登录令牌立即失效
node supervisor.mjs set-upstream <name> --baseURL <url> --models m1,m2 [--key <真实Key>]
node supervisor.mjs list-upstreams             # 真实 Key 只显示指纹
node supervisor.mjs issue-vkey --account <email> [--models m1,m2 | --all]
node supervisor.mjs list-vkeys                 # 只有哈希，token 不可见
node supervisor.mjs revoke-vkey --account <email>
node supervisor.mjs set-quota --account <email> --tokens <N> | --unlimited
node supervisor.mjs list-usage [--month YYYY-MM]
node supervisor.mjs drift [--json]     # 授权集 vs 实际生效集（差异按时限标红）
node supervisor.mjs plugin-precheck --plugin <spec|本地路径>
node supervisor.mjs plugin-push --plugin <spec|本地路径> [--ids all|e01,e02] [--skip-precheck]
node supervisor.mjs plugin-activate --id <实例id>
node supervisor.mjs plugin-remove --plugin <name> [--ids all|e01,e02] [--no-restart]
node supervisor.mjs plugin-rollback --id <实例id> --plugin <name>
node supervisor.mjs up          # 后台拉起驻留 daemon（网关 :8460 + Relay :9400 + 全部实例）
node supervisor.mjs status      # 实例页数据：端口/pid/uid/内存/磁盘/重启数/运行时长
node supervisor.mjs stop        # 停 daemon 与全部实例（--id 只停一个）
node supervisor.mjs restart --id e02
node supervisor.mjs logs --id e02
```

- 员工入口：`http://localhost:8460/`（各实例入口为 `http://<实例id>.localhost:8460/`；浏览器原生把 `*.localhost` 解析到 127.0.0.1，无需改 hosts。生产 = 真实域名 + 通配符 DNS + TLS）。
- 首次进入实例子域会看到登录页；账号绑定哪个实例，登录后就只能进哪个实例。
- 实例数据根：`data/homes/<id>/`（即该实例的 `DSH_HOME`）；账号：`data/accounts.json`（scrypt 哈希）；上游表：`data/upstreams.json`（真实 Key 唯一容身处）；虚拟钥匙：`data/vkeys.json`（只存 SHA-256）；日志：`data/logs/<id>.log` 与 `data/logs/relay.log`。

## 阶段 2 认证语义

- 实例自身零改动、只绑 127.0.0.1；网关用实例的 `--trusted-host <id>.localhost:8460` 信任围栏参数放行转发流量（该参数来自仓库现成的 `--trusted-host` CLI flag，非新代码）。
- 登录：`POST /api/auth/login`（任何主机名可登录，Cookie 落在登录所在主机）→ HS256 JWT，30 分钟，HttpOnly + SameSite=Strict。
- 撤销：`revoke --account` 使 tokenEpoch+1，旧令牌立即全端失效；账号↔实例绑定实时校验，改绑立即生效。
- WebSocket（`/api/events.mux`、`/api/events.host`）走同一认证与绑定检查后原样字节隧道穿透。
- `/status.json` 仅 admin（在 portal 主机上登录）。

## 阶段 3 Relay 语义

- 实例 provider 路由指到 Relay：`baseURL: http://127.0.0.1:9400/v1` + `apiKeyEnv: LYZ_VIRTUAL_KEY`；实例 home 的 `.credentials.yaml` 里只有虚拟钥匙（`vk-…`），真实 Key 永不下发。
- `POST /v1/chat/completions`：Bearer 虚拟钥匙认证（存储里只有 SHA-256）→ 模型授权（vkey 的 models 白名单或 `*`）→ 按模型找到上游、注入真实 Key 转发 `POST <上游 baseURL>/chat/completions`，流式/非流式原样透传。
- 吊销即时生效（每次请求按 mtime 缓存重读 vkeys.json）；已转发的 in-flight 请求不中断。
- 换上游供应商 = 改 Relay 的上游表（`set-upstream` / 直接编辑后 mtime 自动生效），实例零改动。
- `relay.log` 只记元数据（账号/实例/钥匙 id/模型/上游/状态/耗时/token 数），绝不落 prompt、completion 或消息正文（任务书决定 5）。
- 与任务书落点的一个有意偏离：任务书预设「credentials seam 新增 credentials-broker Provider」，实际用 provider 配置的 baseURL 接缝（Relay 即上游）实现同一验收，无需进仓库加 seam——符合「仅当扩展点不够时才进仓库」的架构约定。

## 阶段 4 计量配额语义

- **每请求检查链**（全在 Relay，实例内没有任何可篡改的配额状态）：虚拟钥匙认证 → 模型授权 → 月度额度 → 转发。
- **硬停**：账号设了 `monthlyTokens` 且本月（入+出）用量 ≥ 额度即拒新请求，返回可读 429（`insufficient_quota`，中文提示）；已转发的 in-flight 请求放行至完成。不设额度 = 不限（如管理员账号）。
- **计量**：从上游响应抽取 usage——非流式 JSON 解析整体（8MB 上限），SSE 逐行扫末块；流式请求自动补 `stream_options: {include_usage: true}`（上游已带则不覆盖）。抽取失败只降级计量精度，不影响转发。
- **月键**：部署服务器本地时区的 `YYYY-MM`（任务书决定 6），无 per-tenant 时区配置；月度自然滚动重置。
- 存储：`data/usage.json`（单进程内串行读改写 + 原子替换）；额度在 `data/accounts.json` 的 `monthlyTokens` 字段，`set-quota` 下一请求即生效。
- `list-usage [--month]`：每账号 入/出/请求数/已用/额度/剩余。
- 计价倍率（输入/输出/缓存读/缓存写，管理台展示用）不在本阶段：Relay 已抽取分开的入/出 token，倍率属控制台计费展示层。

## 管理台（控制台）

- 入口：网关 portal 上的 `/console`（总览）与 `/console/{members,models,instances,plugins}` 四个操作页；全部仅限平台管理员（JWT 门禁），POST 另校验 Origin 同源。
- 成员与额度：建号（自动签发虚拟钥匙）、改额度、重置密码（一次性显示）、禁用/启用——禁用打通全链（登录 401、实例子域 403、Relay 转发 401）；启用沿用历史模型白名单重签。
- 模型与权限：成员×模型授权矩阵，保存即替换该成员虚拟钥匙白名单（`"*"` = 全部），Relay 下一请求强制生效。
- 实例管理：重启/停止/启动经 daemon 控制通道（与 CLI 同机制）。
- 插件管理：期望态只读视图；投放操作待异步任务队列后迁入。
- `set-password --account <email>` CLI：重哈希 + epoch 踢会话。

## 阶段 5 漂移对齐语义

- **授权集（GrantedSet）**：模型 = 账号虚拟钥匙的白名单（`*` 展开为上游表全集）；插件 = `data/plugins.json` 的期望清单（排除已移除项）。
- **实际生效集（EffectiveSet）**：实例 home 磁盘内省——settings.yaml 各 provider 路由声明的模型 + web profile 已安装的第三方插件及版本。home 即实例启动组卷的事实来源；运行中实例的 boot 失败类漂移由阶段 6 预检拦截。
- `drift` 比对并持久化到 `data/drift.json`：持续未消除的差异保留**首次发现时间**，超过 `driftStaleHours`（默认 24 小时）标【红-超时未消除】，新差异标【黄-新发现】；修复后差异自动消除。`--json` 供管理台消费。
- 期望 spec 是裸包名时只比存在性（pnpm 落盘的是解析后版本号）；显式版本段才比版本漂移。

## 阶段 6 插件治理语义

- **暂存/生效两阶段**：`plugin-push` 把插件装进实例 profile——运行中实例组卷只发生在启动时，装完即「暂存」；`plugin-activate --id` 重启实例即「生效」。
- **真启动预检**：`plugin-precheck` 在隔离临时 DSH_HOME 安装同一插件并真启动（独立端口，健康探测，超时 `precheckTimeoutSeconds` 默认 120 秒/开发机 600 秒）；push 前自动预检，FAIL 即拦截、任何真实实例都不安装。启动失败/超时/进程早退都算 FAIL。
- **禁用/回滚**：`plugin-remove`（卸载 + 重启 = 禁用，员工工作台入口消失）；`plugin-rollback` 按期望态 history 回装上一个已知良好 spec 并重启。
- **期望态**：`data/plugins.json`（name/spec/state: staged|active|removed/history），是阶段 5 授权集的插件输入。
- **每实例 env 注入**（任务书 6a）：清单 `instances[].env` 支持 `{dataDir}` 占位符；三实例已注入 `CREATOR_WORKBENCH_SKILLS_PATH` 指向 `data/assets/creator-skills`（服务器侧管理员统一维护的技能库，员工只读），替代插件内 Windows 本机默认路径。
- 试点说明：分发/预检/生效/禁用链路用真实 npm 包 `@weibaohui/dsh-file-share` 验证；内容创作工作站为仓库内树插件（不经 npm 分发），其治理面 = 每实例 env 配置（6a 已落地）+ 后续控制台的启用开关。6b 的跨平台脚本移植与 6d 合规门禁上报属部署清单与控制台阶段事项。

## 安全与审计（栏目规划 v2 一期）

- **审计日志**：`data/audit.jsonl` 只追加 JSONL（谁/何时/对谁/动作/结果/标量 detail），永不落会话正文、密码原文、密钥原文。覆盖：登录成败/限流（`auth.*`，gateway）、成员/供应商/模型/实例/插件全部变更端点（`member.*`/`provider.*`/`model.*`/`instance.*`/`plugin.*`，ok/deny/fail 都留痕）、配额硬停（`quota.exceeded`，relay 与网关同进程直接共享 audit.mjs）、审计导出（`audit.export`）与安全设置修改（`security.config_change`，含旧值→新值）。
- **安全与审计页** `/console/audit`：审计日志按 action 前缀/账号关键词/结果筛选（倒序、500 条封顶），导出 JSONL 不限量（`/console/api/audit/export`）；下半页安全设置表单（`/console/api/security/config`，admin-only）。总览页新增告警卡：额度将尽成员数、24h 失败登录数、最近 5 条审计事件。
- **登录安全**：`data/security.json` 缺省自动生成（窗口 15 分钟内 10 次失败锁 15 分钟、密码最小 8 位 3 类字符）；速率限制按「账号+IP」内存滑动窗口（daemon 重启清零），成功登录清零，参数改动即时生效；密码策略作用于控制台建号与重置（弱密码 400 中文文案并留痕）。
- **角色门禁**：管理台页面与只读 GET API（含审计查询/导出、投放任务查询）放行 admin/auditor；全部变更 POST 仅 admin，auditor 得 403「审计员为只读角色」（拒绝也留 deny），employee 拒入。
- **测试**：`node test/security-audit-smoke.mjs`（单元冒烟：密码策略/限流全路径/审计查询/配置生成，临时目录）；`node test/auth-audit-http-verify.mjs`（HTTP 集成：随机端口 + mock 上游验证登录三路径审计、auditor 门禁、配额硬停审计，自动清理）。

## 配额点数模型（栏目规划 v2 六节）

- **公式**：`消耗点 = (输入 tokens × 模型倍率 + 输出 tokens × 模型倍率 × 补全倍率) × 分组倍率`；倍率未配置时模型倍率=1、补全倍率=`defaultCompletionRatio`（缺省 3，对齐主流对话模型输出/输入价格比）、分组倍率=1。倍率存 `data/ratios.json`，mtime 缓存，改动下一请求即生效：

```json
{
  "models": { "glm-5.3": { "ratio": 2, "completionRatio": 3 } },
  "defaultCompletionRatio": 3,
  "groups": { "设计部": 1.5 }
}
```

- **扣减流程**（Relay 每请求，认证 → 模型授权 → 配额判定 → 预扣 → 转发）：预扣 = 估输入（`ceil(消息+system 字符数/4)`）× 模型倍率 + 估输出（`max_tokens` 缺省 1024）× 模型倍率 × 补全倍率，再乘分组倍率，转发前入账；实结 = 响应 usage（流式取 `include_usage` 终值）按实际 tokens 计点，与预扣多退少补（差值可负即返还）；请求失败/上游错误全额返还预扣；成功但 usage 抽取失败时保留预扣作为本次费用（防刷）。全部账目操作走同一 promise-mutex 串行链。
- **配额判定**：`account.monthlyPoints`（缺省 = 不限、0 = 即停）账面点数到线即拒（429 `insufficient_quota`，中文点数文案）；`monthlyPoints` 未定义而存在旧 `monthlyTokens` 时走旧 tokens 判据（「旧制」，控制台标注）；并存以 `monthlyPoints` 为准。`usage.json` 每账号每月新增 `points` 累计，tokens 进/出照旧累计。
- **控制台**：模型页每模型行内编辑「倍率/补全倍率」（`POST /console/api/model/ratio`，审计 `model.ratio_change` 旧值→新值）；「部门与角色」页编辑分组倍率（`POST /console/api/department/group-ratio`，审计 `quota.group_ratio_change`）并只读展示三角色权限矩阵；成员页额度列/改额度表单为点数口径（旧制账号显示「旧制 tokens」标注）；总览告警卡额度口径切换为点数（旧制并入）。`list-usage` CLI 输出点数列。

## 工具 RBAC（栏目规划 v2 阶段 9）

- **模型**：一人一实例 ⇒ 工具策略是实例级的——账号绑实例、角色定策略。平台把每个实例归属账号的角色对应的 deny 工具组写进实例 home 的 `tool-policy.json`，实例侧 [kabage-tool-guard](../plugins/kabage-tool-guard/README.md) 插件（`ctx.tools.guard()` 全局单调守卫）读该文件（mtime 缓存）**热生效，无需重启实例**。
- **策略存储**：`data/toolpolicy.json`（缺省自动生成）：`{"roles":{"admin":{"deny":[]},"auditor":{"deny":["command","network"]},"employee":{"deny":["command","network"]}}}`；deny 值为工具组名（`command` 命令行 = bash/pwsh/terminal_*，`fs` 文件 = read/write/edit/read_image/str_replace_editor/glob/grep，`network` 联网 = web_search/web_fetch；映射外的内置工具不分组、一律放行）。
- **下发**：实例归属账号的角色 → deny 列表 → 原子写 `<home>/tool-policy.json`（`{"role":"...","deny":[...]}`）。触发点：管理台「部门与角色 → 实例内工具组策略」保存（`POST /console/api/toolpolicy`，全量重写）、成员角色变更/建号/IdP 名册同步（重写该账号所在实例）、daemon 启动与 `sync-toolpolicy` CLI（全量）。写文件动作并入 `toolpolicy.change` 审计（含旧值→新值）。
- **拒绝收集**：guard 拒绝时把 `{"ts","tool","group","decision":"deny"}` 追加到 `<home>/guard-events.jsonl`（桥文件）；daemon 每 30 秒（`GUARD_TRANSCRIBE_INTERVAL_MS`）转写成 `data/audit.jsonl`：`action=guard.deny`、actor=实例归属账号、detail 只含工具名/分组/实例名标量，转写成功后清空桥文件（清空前崩溃会重放少量事件——审计只追加，重复好过丢失）。`sync-toolpolicy` 可手动触发同一转写。
- **插件语义**：策略文件不存在 = 全放行（fail-open，admin 实例可能从未下发、隔离 precheck 的临时 home 也没有）；文件存在但 JSON/结构非法 = fail-loud 抛错（加载时抛错实例起不来，运行中热更新出的坏文件让当笔调用失败）。被拒调用以 `Error: 工具策略拒绝：…` 返回给模型。零 npm 依赖（仅 peer `@deepseek-ai/cordis`，经 profile 兜底目录解析）。
- **测试**：`node platform/plugins/kabage-tool-guard/test/guard-test.mjs`（分类映射/策略校验/热生效/串行追加/fail-loud）；`node test/toolpolicy-http-verify.mjs`（随机端口真实网关：GET/POST API、三实例下发、非法策略 400、auditor 403、角色变更联动、桥文件转写与清空）。

## 个人中心与邀请注册（栏目规划 v2 阶段 10）

- **员工门户** `/me`（:8460 portal 主机，新 [portal.mjs](portal.mjs)）：资料卡（账号/显示名/部门/角色/绑定实例+工作区链接）、改密（当前密码 + 新密码策略校验 → 重哈希 + tokenEpoch+1 全端下线，审计 `member.self_password_change` ok/fail）、本人当月用量（点数口径进度条；旧制 tokens 账号按旧口径并标注「旧制」；无额度显示不限，复用 quotas.mjs 计点展示）、设备管理 MVP（最近登录 5 条 = 审计 `auth.login_success` 本人过滤 + 「下线所有设备」`auth.revoke_all`）。
- **角色选择（写明）**：`/me` 对 admin/auditor **同样可用而不重定向**——两类角色同样有本人用量与设备管理需求，页顶提供「返回管理台」；管理台侧栏新增「个人中心」入口。employee 在 portal 主机登录成功后自动跳 `/me`（登录页按 portal 主机名 + 角色分流），在实例子域登录则照旧原地进入工作区。新增 `GET /login` 直达登录页（已认证按角色 303 跳 `/me` 或入口页）。
- **邀请注册**：管理台成员页新区块（部门/角色 employee|auditor/实例/有效期 1–720h 缺省 72）→ `POST /console/api/invite/create` 生成一次性链接 `/register?code=<明文>`——明文只在生成响应里出现一次，`data/invites.json` 只存 SHA-256，校验全表 `timingSafeEqual` 常数时间比较（防时序侧信道）；未用邀请列表 + 撤销（`POST /console/api/invite/revoke`，立即失效，重复撤销 404）。公开注册页 `/register?code=`（免登录，渲染预设部门/角色/有效期倒计时）+ `POST /api/register`：按 IP 复用登录速率限制参数（security.json，独立计数桶）→ code 校验 → `addAccount` 同一函数建号（白名单+密码策略+scrypt）→ 签发虚拟钥匙（models=*）→ 标记邀请已用 → 同步该实例 tool-policy（阶段 9 复用）→ 审计 `member.register`（fail detail 只含原因码；失败的注册不消耗邀请）。
- **审计 action**：`member.self_password_change` / `auth.revoke_all` / `invite.create` / `invite.revoke` / `member.register`——ok/deny/fail 全留痕，绝不含密码与明文 code。
- **测试**：`node test/me-invite-http-verify.mjs`（57 项；随机端口 + 临时目录，限流验收用独立第二网关隔离计数桶）。

## 两步验证 / 邮件通知 / SSO 骨架（栏目规划 v2 阶段 11）

### 11A TOTP 两步验证（[totp.mjs](totp.mjs)）

- **密码学**：手写 RFC 4648 base32 编解码 + RFC 6238 TOTP（HMAC-SHA1、30 秒步长、6 位、±1 窗口容错、timingSafeEqual 常数比较），以 RFC 6238 附录 B 标准测试向量验收（SHA1/8 位六时间片逐一断言）。
- **存储**：`data/twofa.json`；密钥 AES-256-GCM 加密落盘（`enc:v1:` 自描述格式，密钥由 auth-secret.key 经 SHA-256 派生），**绝不落明文**；解密失败按未绑定处理并告警（密钥轮换安全语义）。
- **绑定/管理**：`POST /api/me/2fa/setup`（生成密钥→pending，返回 base32 + `otpauth://` 链接文本，不做二维码）→ `/api/me/2fa/confirm {code}`（验证通过才 enabled，审计 `security.2fa_enabled`）→ `/api/me/2fa/disable {password}`（验当前密码，审计 `security.2fa_disabled`）；admin 救援 `POST /console/api/member/2fa/reset`（审计 `security.2fa_reset`，成员页「重置2FA」按钮仅对启用中的账号显示）。/me 页有 2FA 卡片（三态），管理台安全页可按角色勾选软强制。
- **登录**：密码通过后已启用 2FA → 不发 cookie，响应 `{totp_required:true}`，登录页进入验证码步骤 → `POST /api/auth/totp` 通过才签发 JWT；**TOTP 猜测与密码猜测同一限流桶**（错码 `auth.totp_fail` 留痕、计入失败、锁定期 429），成功后 `auth.login_success` detail 带 `totp:true`。
- **软强制**：security.json `require2faRoles`（缺省 `[]`，管理台安全页勾选）——清单角色登录但未绑定时响应附 `needs_2fa_enrollment:true` + /me 顶部横幅提醒；**不做硬锁**（硬强制属阶段 11b，避免管理员误配置锁死自己）。

### 11B 邮件通知（[notify.mjs](notify.mjs)）

- **配置**：`data/notify.json` `{"mode":"off"|"file"|"smtp", smtp:{host,port,secure,auth:{user,passEnc},from}, adminNotify:[]}` 缺省 off；SMTP 密码 AES-GCM 加密落盘；管理台安全页通知设置区（admin-only，`security.notify_change` 审计，密码回显打码、留空不改）。
- **发送**：`sendMail` 串行队列异步，失败只 console.error 不阻断主流程。file 模式渲染完整 MIME（Subject RFC 2047 / 正文 UTF-8 base64 / CRLF）写 `data/outbox/<ts>-<n>.eml`（每收件人一封）；smtp 模式为零依赖最小客户端（EHLO 多行应答解析、服务器宣告才 STARTTLS、AUTH LOGIN、MAIL/RCPT/DATA 点透明、QUIT，单命令 10 秒超时）。
- **触发点**：配额跨 80% 告警（relay 实结处，点数口径优先旧制并入，`usage.alerted` 标记**每账号每月一次**，收件人=本人+adminNotify 抄送，审计 `notify.quota_warn`）；建号/禁用/重置密码通知本人——**重置邮件绝不含新密码原文**。
- **待真机验证**：真实外网 SMTP（凭证）；file 模式与本地 mock SMTP 命令流已完整验证。

### 11C SSO 骨架（[sso.mjs](sso.mjs)，企业微信 + 钉钉）

- **配置**：`data/sso.json` 每 provider 独立 `enabled`（缺省全关）；secret/appSecret AES-GCM 加密；`authorizeBase`/`apiBase` 可配、缺省真实域名——**指向本地 mock 即可全流程验证**，真实供应商待凭证。
- **流程**（授权码模式）：登录页显示已启用 provider 按钮 → `GET /api/auth/sso/:provider/start`（一次性 state，内存 Map 5 分钟）→ 303 authorize → callback 校验 state → code 换 token → 用户标识（企业微信 userid / 钉钉 unionId，仅元数据）→ 按 `accounts.json` 的 `ssoIds` 数组查绑定：命中签发 JWT（与密码登录同一令牌语义，审计 `auth.sso_login`）；未命中渲染绑定页（bindToken 一次性 5 分钟）→ `POST /api/auth/sso/bind` 账号+密码验证后写绑定（审计 `auth.sso_bind`，密码错误计入登录限流同桶）。
- **待配置验证**：真实企业微信/钉钉（corpId/appKey/secret 凭证）；mock 全流程已验证。

## 服务令牌与 DSH 管理工具（栏目规划 v2 阶段 12）

- **服务令牌**：`data/service-tokens.json` 存 `{id, tokenHash(SHA-256), role: admin|readonly, createdAt}`；`node supervisor.mjs add-service-token <名称> [--readonly]` 生成 `kbsvc-<base64url 256bit>` 明文**只显示一次**（审计 `security.service_token_create/revoke`，detail 只含名称/角色）。比较走 timingSafeEqual；mtime 缓存读取，撤销下一请求生效。**服务令牌 = 管理凭据，仅注入可信实例**（能读到即能以对应角色调用管理台 API）。
- **console API 认证扩展**：`Authorization: Bearer kbsvc-…` 命中即等价角色——admin token 全部 API 可用；readonly 仅只读白名单（`member/list`、`member/usage`、`audit`、`toolpolicy`），白名单外 GET 403、任何 POST 403 deny 留痕。**仅 `/console/api/*` 生效**（页面路由一律 401 JSON）。审计 actor.account 记 `svc:<名称>` 与人区分。配套新增只读端点：`GET /console/api/member/list`（成员+当月用量摘要，工具 user_list 数据源）与 `GET /console/api/member/usage?account=`（点数/额度/余量，user_quota_query 数据源）。
- **管理类 DSH 工具**（[kabage-admin-tools](../plugins/kabage-admin-tools/README.md)，实例侧插件）：7 个工具（只读 `user_list`/`user_quota_query`/`audit_query`；变更 `user_create`/`user_update`/`user_reset_password`/`user_set_disabled`）经 HTTP 调平台 console API。注册走 raw `ctx.tools.register`（`export const inject = ['tools']` 声明服务依赖；显式 `presentCall` generic 卡片；raw 工具自带输入校验与强制 output 声明）。token 经 instances[].env 注入（`KABAGE_SERVICE_TOKEN`，仓库零真实值）；未配置时调用返回中文配置错误（`token_missing`）而非崩溃。**决策：不探测令牌角色**——7 个工具始终注册，readonly 调变更由平台 403 转译为中文错误（`forbidden`），注册逻辑与令牌角色解耦。一次性密码（create/reset）会留在管理员实例会话记录中——结果附提示引导尽快改密（详见插件 README 警示节）。
- **测试**：`node test/service-token-verify.mjs`（平台侧 22 项：生成/认证/白名单/撤销/审计 actor）；`node platform/plugins/kabage-admin-tools/test/admin-tools-test.mjs`（插件侧 42 项：mock 平台断言路径/方法/鉴权头/映射/转译/截断/token 缺失）。

## 已验证（本机 Windows，2026-09-20/21）

阶段 1：一键拉起 3 实例全部 running（HTTP 200）；`taskkill` 强杀实例进程树 → daemon 2–6 秒内重新拉起（到 HTTP 200 约 165 秒，开销在 dsh tsx 源码冷启动，生产换构建产物可数量级缩短）；会话/配置/凭证按 home 隔离；崩溃重启后会话文件原样保留。

阶段 2：未登录访问实例子域 HTTP 401（登录页）、WS 401；已认证 WS 握手穿透到实例返回 101（`Sec-WebSocket-Accept` 由实例计算，字节隧道成立）；admin→绑定的 e01 200、重放 admin 令牌到 e02 403；e01/e02 的 session id 集合互斥；`revoke` 后旧令牌 401、重登 200；`/status.json` admin-only。

阶段 3：实例 home 内真实 Key 出现次数 = 0（唯一容身 `data/upstreams.json`）；无/假钥匙 401；member-a 打未授权模型 403；授权模型转发上游拿到 429「余额不足」——上游认证通过才报余额，即真实 Key 注入成功的证据；`revoke-vkey` 后同钥匙立即 401；把 glm-5.3-flash 从上游 zhipu 迁到 zhipu-backup（`set-upstream` 两次），同一把 vkey 照常打通（relay.log 显示上游已切换），实例配置零改动；实例端到端：e01 的 headless 调用 → Relay → 上游，relay.log 记录完整元数据链。

阶段 4（用受控 mock 上游走真实 Relay 路径验证，非真实上游因无余额只返回 429 无 usage）：非流式 JSON 与流式 SSE 的 usage 均正确入账（admin 一次各 +100/+20，list-usage 200/40 requests=2）；member-a 额度 500 连打 test-json（每次 120）：5 次 200（用量 120→600）后第 6 次 429 硬停，错误体可读「本月 Token 额度已用完（600/500）」（`insufficient_quota`）；`set-quota --tokens 0` 的账号凭有效钥匙也立即 429；`set-quota` 下一请求即生效（mtime 重读）；月键 = 服务器本地时区 `YYYY-MM`。测试后已清理：mock 上游移除、usage 计数清零、测试额度恢复不限。

阶段 5：漂移检测器首轮运行即抓到真实漂移（实例 settings 残留 minimax 路由 3 个未授权模型 + 配额测试遗留的 test-json 白名单）；人为制造 2 处漂移（私授模型 glm-secret-trial + 残留旧插件依赖）均检出为【黄-新发现】；回拨首次发现时间 48 小时后标【红-超时未消除】；逐一修复后三实例全对齐；私授模型跨越实例重启仍持续标红（时限语义正确）。

阶段 6：坏插件夹具（非法 YAML 的 bundle patch）预检 FAIL（组合解析崩溃），拦截后任何实例未安装（e02 profile 零波及）；真实 npm 包 `@weibaohui/dsh-file-share` 预检 PASS（隔离启动健康）→ push 暂存（依赖 + bundles 层栈就位，运行中实例不受影响）→ activate 重启生效 → drift 对齐 → remove 禁用（卸载 + 重启，profile 零残留，入口消失语义成立）→ drift 对齐。

阶段 9（2026-09-25）：`sync-toolpolicy` CLI 真路径——新建三清单账号后 e01/e02/e03 home 各得一份按角色的 `tool-policy.json`；模拟桥文件两笔拒绝 → CLI 转写出两条 `guard.deny`（actor=member-a、detail 只含 tool/group/instance）且桥文件清空；本地路径插件 `kabage-tool-guard` 真启动预检 PASS（隔离 home 安装 + 健康 35 秒，peer `@deepseek-ai/cordis` 经 profile 兜底目录解析、pnpm 零重复安装）；插件单元测试 58 项（含同秒二次改写的 size 缓存感知）、平台 HTTP 集成 32 项（API 门禁/三实例下发/角色变更联动/转写清空/幂等/截断前指纹比对）全过；CLI `add-account`/`set-role` 成功后自动全量重发策略（daemon 未运行时提示生效时机）。**待真机验证**：真实 LLM 发起工具调用的端到端拦截（需有余额上游——守卫在 `tools/pre-execute` 后单调生效，管道语义已由 DSH 侧测试背书）。

阶段 10（2026-09-25）：HTTP 集成 63 项全过（`test/me-invite-http-verify.mjs`）——/me 访问矩阵（employee 200 只含本人数据且查询参数被忽略、admin/auditor 同样可用、未认证 401、/login 按角色 303、入口页 account 插值转义）；改密四路径（错当前密码/弱密码/不一致 400 全留痕，成功后旧 JWT 401、新密码可登录、旧密码失效）；用量三形态渲染（320/1000 点数、120/500 旧制标注、不限额度）；revoke-all 留痕 + 旧 JWT 401；邀请全流程（生成留痕不含明文 code → 注册页预设渲染 → 注册成功角色/部门/实例正确 + tool-policy 下发 → 二次注册 used 拒 → 撤销/过期/无效/手改 admin 角色 invite 拒 → 失败不消耗邀请 → 畸形 code 白名单拒绝不回流 → 内部抛错转 500 且不挂死不消耗邀请）；employee 调 invite API 403；限流专项（独立网关：3 次无效后第 4 次 429、有效邀请也 429、deny 留痕）。既有冒烟零回归（smoke 43 含 actor exact 匹配隔离断言）。

阶段 11（2026-09-25）：**A-TOTP**（`test/twofa-http-verify.mjs` 51 项）：RFC 6238 附录 B 六时间片向量逐一通过 + base32/AES-GCM 往返与坏密文拒绝；HTTP 全流程（setup→错码 confirm 拒→对码 enabled→登录 totp_required 不发 cookie→错 code 401 留痕→对 code 登录 detail totp:true→disable 恢复单因子→admin reset 救援→软强制 enrollment 标记与 /me 横幅→TOTP 错 3 次后对码也 429 同桶限流）。**B-邮件**（`test/notify-verify.mjs` 40 项）：MIME 纯函数头/编码/折行断言；file 模式 outbox .eml 逐项解码断言；relay 80% 告警恰好本人+抄送两封、alerted 每月一次、notify.quota_warn 留痕；建号/禁用/重置三类通知且重置邮件不含新密码原文；本地 mock SMTP 命令流（EHLO 多行/AUTH LOGIN base64/MAIL/RCPT/DATA/QUIT 顺序）与消息体断言。**C-SSO**（`test/sso-verify.mjs` 20 项）：mock OAuth 全流程（登录页按钮→start 303→authorize→callback 未绑定出绑定页→bind 错密码拒/对密码绑定落 ssoIds→二次 SSO 直达 303+cookie→伪造/缺 state 400→未启用 404→secret 加密落盘）。九套测试 432 项全绿。**待真机验证**：真实 SMTP 凭证、真实企业微信/钉钉凭证。

**未验证**：真实模型对话（三个上游 key 均无余额，zhipu 429 余额不足）；浏览器点击流（curl + `--resolve` 已覆盖等价语义）；跨月滚动重置（按月键构造成立，未跨月实测）；预检的「完整模型 turn」档（需有余额上游，当前为隔离真启动 + 健康探测档）。

## 设计决定与已知限制

- **daemon 与短命命令经 `data/` 文件通信**（状态文件 + 控制文件轮询），无 socket 依赖；控制面（阶段 3+）落地时换正式 RPC。
- **网关按 Host 路由而非路径前缀**：DSH web 是假设根路径的 SPA，路径重写必然破坏其绝对路径 API/WS；子域路由路径不重写，SPA 原样工作。生产部署 = 前置 TLS 反代按子域转发到网关，网关再按 Host 分发。
- **uid 是名义字段**：Windows 开发机无 uid 语义，仅入清单与状态页；Linux 生产部署由 supervisor 以 setuid 落地（后续阶段）。
- **崩溃重启护栏**：2 秒退避重启；稳定运行 5 分钟清零计数；连续 5 次失败置 `failed` 等人工介入。
- **首次启动慢**：新 home 首次 `dsh web` 要做 profile 初始化（pnpm ~137MB）+ tsx 编译，约 3–5 分钟；`starting` 超时 180 秒后标 `unhealthy`，进程仍被继续观测。
- **登录无速率限制、无 TLS**：MVP 明确未做（内网 + 后续前置反代 TLS 承担）；生产前必须补。
- **隐私边界**（任务书决定 5）：网关与 supervisor 只做身份/绑定判定与进程资源元数据采集，不读会话日志、不读内容正文。
