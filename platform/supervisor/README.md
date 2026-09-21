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

## 已验证（本机 Windows，2026-09-20/21）

阶段 1：一键拉起 3 实例全部 running（HTTP 200）；`taskkill` 强杀实例进程树 → daemon 2–6 秒内重新拉起（到 HTTP 200 约 165 秒，开销在 dsh tsx 源码冷启动，生产换构建产物可数量级缩短）；会话/配置/凭证按 home 隔离；崩溃重启后会话文件原样保留。

阶段 2：未登录访问实例子域 HTTP 401（登录页）、WS 401；已认证 WS 握手穿透到实例返回 101（`Sec-WebSocket-Accept` 由实例计算，字节隧道成立）；admin→绑定的 e01 200、重放 admin 令牌到 e02 403；e01/e02 的 session id 集合互斥；`revoke` 后旧令牌 401、重登 200；`/status.json` admin-only。

阶段 3：实例 home 内真实 Key 出现次数 = 0（唯一容身 `data/upstreams.json`）；无/假钥匙 401；member-a 打未授权模型 403；授权模型转发上游拿到 429「余额不足」——上游认证通过才报余额，即真实 Key 注入成功的证据；`revoke-vkey` 后同钥匙立即 401；把 glm-5.3-flash 从上游 zhipu 迁到 zhipu-backup（`set-upstream` 两次），同一把 vkey 照常打通（relay.log 显示上游已切换），实例配置零改动；实例端到端：e01 的 headless 调用 → Relay → 上游，relay.log 记录完整元数据链。

阶段 4（用受控 mock 上游走真实 Relay 路径验证，非真实上游因无余额只返回 429 无 usage）：非流式 JSON 与流式 SSE 的 usage 均正确入账（admin 一次各 +100/+20，list-usage 200/40 requests=2）；member-a 额度 500 连打 test-json（每次 120）：5 次 200（用量 120→600）后第 6 次 429 硬停，错误体可读「本月 Token 额度已用完（600/500）」（`insufficient_quota`）；`set-quota --tokens 0` 的账号凭有效钥匙也立即 429；`set-quota` 下一请求即生效（mtime 重读）；月键 = 服务器本地时区 `YYYY-MM`。测试后已清理：mock 上游移除、usage 计数清零、测试额度恢复不限。

阶段 5：漂移检测器首轮运行即抓到真实漂移（实例 settings 残留 minimax 路由 3 个未授权模型 + 配额测试遗留的 test-json 白名单）；人为制造 2 处漂移（私授模型 glm-secret-trial + 残留旧插件依赖）均检出为【黄-新发现】；回拨首次发现时间 48 小时后标【红-超时未消除】；逐一修复后三实例全对齐；私授模型跨越实例重启仍持续标红（时限语义正确）。

阶段 6：坏插件夹具（非法 YAML 的 bundle patch）预检 FAIL（组合解析崩溃），拦截后任何实例未安装（e02 profile 零波及）；真实 npm 包 `@weibaohui/dsh-file-share` 预检 PASS（隔离启动健康）→ push 暂存（依赖 + bundles 层栈就位，运行中实例不受影响）→ activate 重启生效 → drift 对齐 → remove 禁用（卸载 + 重启，profile 零残留，入口消失语义成立）→ drift 对齐。

**未验证**：真实模型对话（三个上游 key 均无余额，zhipu 429 余额不足）；浏览器点击流（curl + `--resolve` 已覆盖等价语义）；跨月滚动重置（按月键构造成立，未跨月实测）；预检的「完整模型 turn」档（需有余额上游，当前为隔离真启动 + 健康探测档）。

## 设计决定与已知限制

- **daemon 与短命命令经 `data/` 文件通信**（状态文件 + 控制文件轮询），无 socket 依赖；控制面（阶段 3+）落地时换正式 RPC。
- **网关按 Host 路由而非路径前缀**：DSH web 是假设根路径的 SPA，路径重写必然破坏其绝对路径 API/WS；子域路由路径不重写，SPA 原样工作。生产部署 = 前置 TLS 反代按子域转发到网关，网关再按 Host 分发。
- **uid 是名义字段**：Windows 开发机无 uid 语义，仅入清单与状态页；Linux 生产部署由 supervisor 以 setuid 落地（后续阶段）。
- **崩溃重启护栏**：2 秒退避重启；稳定运行 5 分钟清零计数；连续 5 次失败置 `failed` 等人工介入。
- **首次启动慢**：新 home 首次 `dsh web` 要做 profile 初始化（pnpm ~137MB）+ tsx 编译，约 3–5 分钟；`starting` 超时 180 秒后标 `unhealthy`，进程仍被继续观测。
- **登录无速率限制、无 TLS**：MVP 明确未做（内网 + 后续前置反代 TLS 承担）；生产前必须补。
- **隐私边界**（任务书决定 5）：网关与 supervisor 只做身份/绑定判定与进程资源元数据采集，不读会话日志、不读内容正文。
