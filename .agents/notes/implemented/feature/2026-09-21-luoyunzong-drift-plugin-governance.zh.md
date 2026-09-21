# Agent Note：落云宗漂移对齐以 home 内省为生效事实，插件治理以真启动预检为投放闸门

Status: implemented

[English](2026-09-21-luoyunzong-drift-plugin-governance.md) | 中文

## 问题

任务书阶段 5–6 收拢配置真相与第三方代码两条线。阶段 5（漂移对齐）：授权集（管理员授出的模型白名单、期望插件）要与实际生效集（实例实际服务的配置）比对，差异超时要标红。阶段 6（插件治理）：npm/Git/bundle 插件按实例（全局或定向）安装、暂存后重启生效、全局投放强制隔离真启动预检、失败自动回滚、禁用即员工可见入口消失。前期阶段带来的约束：零 harness 改动、零第三方依赖、实例是原生 DSH 进程（无法自建自报端点）、手头上游全部无余额——任何需要真实模型 turn 的验证都得有无余额策略。

## 决策

**阶段 5 —— 实例 home 就是生效集。** 原生 DSH 挂不了自定义自报端点，但它的 home 目录正是启动组卷的事实来源：模型取自 `settings.yaml` 里 provider 路由声明，插件取自 web profile 的 `package.json` 依赖（`dsh plugin` 转发器在那里按安装态对账 `dsh.profile.bundles`）。`drift` 把它与授权集比对——账号虚拟钥匙的模型白名单（`*` 按上游表展开）加阶段 6 的期望插件清单——并把差异持久化进 `data/drift.json`，每次检查保留差异的**首次发现时间**；超过 `driftStaleHours`（默认 24 小时）的标【红-超时未消除】，新差异标【黄-新发现】，修复即消除。期望 spec 是裸包名时只比存在性（pnpm 落盘的是解析后版本号，字符串相等会误报）。

**阶段 6 —— 预检就是隔离克隆里的真启动。** `plugin-precheck` 造一次性 DSH home、执行同一句 `dsh plugin --profile web add` 安装、用标准启动模板在空闲回环端口真启动一个实例并做健康探测；安装失败、启动崩溃或超过 `precheckTimeoutSeconds`（任务书默认 120 秒；开发机清单设 600 秒，因为 tsx 源码模式冷启动要 2–4 分钟）都算 FAIL。`plugin-push` 先预检，FAIL 即拒绝触碰任何真实实例；PASS 后装进目标实例的**在用 profile**——这是安全的暂存，因为组卷只发生在启动时——并记录期望态。`plugin-activate` 重启生效；`plugin-remove` 卸载加重启，既是回滚原语也是禁用（重启后的组卷里员工可见入口消失）；`plugin-rollback` 按期望态 history 回装上一个已知良好 spec。每实例 env 注入（`instances[].env`，支持 `{dataDir}` 占位符）落地任务书 6a：三实例注入 `CREATOR_WORKBENCH_SKILLS_PATH` 指向 `data/assets/creator-skills`（服务器侧管理员统一维护的只读技能库），替代插件内的 Windows 本机默认路径。

**无余额验证。** 坏插件用例不需要网络：bundle patch 为非法 YAML 的夹具包让组卷崩溃，预检 FAIL，push 被拦截且真实实例零波及（e02 的 profile 逐字节未变）。正路径用真实 npm 包（产品截图同款 `@weibaohui/dsh-file-share`）：预检 PASS（隔离启动健康）→ push 暂存（依赖与对账后的 bundles 层栈就位，运行中实例不受影响）→ activate → drift 对齐 → remove → profile 零残留且 drift 对齐。阶段 5 的检测器首轮运行就自证了价值——抓到真实漂移（残留 minimax 路由授出 3 个未授权模型）；人为制造脚本（私授模型 + 残留旧插件依赖）复现了黄→红（发现时间回拨 48 小时）→修复的完整循环，包括红色跨越实例重启持续。

## 已否决的替代方案

**实例内自报 RPC。** 否决：得先改 harness 或先给每个实例装插件——漂移检查必须在治理存在的第零天就能用；home 内省与组卷读的是同一份事实，只是从服务端观测。

**按重检时间标注差异。** 否决：老化要看首次发现时间，`mergeDiffs` 对存续差异保留 `detectedAt`、消失即删；红色的语义是「已授出、已见漂移、N 小时未修」。

**预检用静态分析（lint patch、干跑 loader）。** 否决：任务书的词是「真启动预检」——真启动能抓住组卷崩溃、peer 解析失败和启动期 throw，静态检查看不到。`--full-turn` 变体（一次真实模型 turn）等有余额上游落地，已记为生产强化项。

**超时先杀进程再判定。** 压测后修正：`killTree` 触发的 exit 事件会把「超时」误标成「进程早退」；现在先定结果再杀。

## 后果

阶段 5–6 验收全数成立：真实漂移在无人投放的情况下被抓到；制造漂移走完黄→红→修复；坏插件被拦截且实例零影响；完整 暂存→生效→禁用 生命周期对着真实 registry 包验证，且每一步 drift 都收敛。代价：漂移基于磁盘真相，装得上但首次模型调用才 throw 的插件要等会话踩到（预检的 full-turn 变体就是为它准备的）；预检要付一次完整冷编译（tsx 下数分钟，生产构建产物启动会大幅缩短）；`plugin-remove --no-restart` 时插件在下次重启前仍然生效，命令输出已明示。激活/禁用基于 DSH 启动组卷的语义，正是在用 profile 上暂存之所以安全的原因。顺带修掉两处：scoped 包名（`@scope/name`）曾被前缀启发式误判为文件路径（现 `isLocalPathSpec` 以 `@` 开头直接排除）；`main()` 的完成回调会覆盖失败命令设置的 `process.exitCode`。
