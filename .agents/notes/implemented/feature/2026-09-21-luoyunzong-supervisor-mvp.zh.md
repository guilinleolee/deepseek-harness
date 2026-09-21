# Agent Note：落云宗实例编排 supervisor MVP 以零依赖文件 IPC 形态独立于 harness 发布

Status: implemented

[English](2026-09-21-luoyunzong-supervisor-mvp.md) | 中文

## 问题

企业平台任务书（`落云宗企业平台任务书.md`，阶段 1）要求服务端托管的一人一实例：一账号、一实例、一独立目录，带健康检查、30 秒上限的崩溃自动重启，以及实例页数据（端口/pid/uid/内存/磁盘）。harness 本体是单用户的，没有实例概念；而 `DSH_HOME` 已完全参数化（`packages/util/home-paths`）、profile 首次使用自动初始化，所以"一人一 home 一进程"只差外层调度。问题是：这个调度器放哪、如何在不改 harness 的前提下与实例通信（任务书决定 4：独立控制面，不动 harness 本体）。

## 决策

`platform/supervisor/` —— 独立的零依赖 Node ESM CLI，刻意不进 pnpm workspace（`pnpm-workspace.yaml` 没有 `platform/` glob）。一个 daemon 进程持有全部实例子进程；短命命令（`up/status/stop/start/restart/logs`）只通过 `data/` 下的文件与它通信：状态文件（临时文件+rename 原子写）加每 2 秒轮询的控制文件。实例按清单（`instances.json`）以命令模板（`pnpm dsh web --no-open --port {port}`）和 `DSH_HOME=data/homes/<id>` 拉起。

关键机制：崩溃重启 2 秒退避，稳定运行 5 分钟清零计数，窗口内连续 5 次失败置 `failed` 等人工介入，避免重启风暴；健康轮询在启动期 2 秒一次、稳态 15 秒一次，180 秒启动超时按 dsh 的 tsx 源码模式冷启动校准（profile 初始化 pnpm 安装 ~137MB + 编译，约 3–5 分钟）；内存采样是**进程树求和**（记录的 pid 是 pnpm/cmd 外壳，不是 DSH node 进程）——Windows 走一次 PowerShell `Get-CimInstance Win32_Process` 全进程表，Linux 解析 `/proc/<pid>/stat`，建树在 node 侧统一；磁盘占用是对每个 home 的带上限递归遍历。

实测中抓到并同change修复了三个故障模式：(1) daemon 的 promise 在 setup 后立即 resolve，`main()` 的完成回调调了 `process.exit(0)` 把 daemon 杀了——现在 daemon 返回永不 resolve 的 promise；(2) `stop` 依赖 `taskkill /T` 的树语义，中间壳进程已退出时树会断链，而且 fire-and-forget 的 taskkill 子进程会在 CLI 进程先退出时被连带收割、一个都没跑成——现在 `stop` 显式遍历状态文件里的实例 pid 并逐一等待杀完；(3) portal 在实例拉起之后才绑定，`EADDRINUSE` 会留下三个半启动的孤儿实例——现在 portal 先绑定，任何绑定错误都在第一个 spawn 之前退出。

## 已否决的替代方案

**以 harness 插件贡献编排 capability。** 否决：实例生命周期按任务书的域映射属平台工程；走 `ctx.effect()` 会把 supervisor 语义（进程树、uid、端口）耦合进插件生命周期，还把 OS 相关的进程代码拖进 100% 覆盖率门。

**socket/HTTP 控制面替代文件 IPC。** MVP 否决：控制面（阶段 2）才有真正的 RPC 面；文件 IPC 为一个注定被替换的功能删光了服务端代码，而且 `status` 必须在 daemon 死了的时候也能用（读最后写入的状态、按 pid 诚实标注存活）。

**一实例一容器。** 任务书非目标（MVP 单机多进程）；清单里的命令模板就是未来插容器运行时的接缝。

## 后果

一台机器一条命令跑起 N 个隔离实例，阶段 1 的验收项里所有不依赖有余额模型 key 的部分都已实测：3 实例健康；kill → 2–6 秒 respawn；按 home 的会话/配置/凭证隔离——一次 headless 调用在 `.credentials.yaml` 拷进该实例 home 前后分别报 MISSING_CREDENTIAL 与路由解析成功；崩溃重启后会话文件原样保留。真实对话端到端仍被上游配额卡住（zhipu 429 余额不足），与代码无关。

代价：tsx 源码模式下实例重启到 HTTP 200 约 165 秒——任务书 30 秒预算对 supervisor 的重启动作成立，服务恢复时间则被 dsh 启动模式封顶；生产应改用构建产物或单 exe 启动，已记为已知优化项。portal 是落地页不是反代：web SPA 假设根路径，生产的统一入口是前置反代加阶段 2 认证层。`uid` 在 Windows 上是名义字段，Linux 部署路径再落真 setuid。supervisor 只采集进程与资源元数据，不碰会话内容（任务书决定 5）。
