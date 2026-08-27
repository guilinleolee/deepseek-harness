# DSH 插件：Trajectory Debug Workbench（trajectory-debug）

[English](README.md) | 中文

> 目标宿主：DeepSeek Harness（`@deepseek-ai/dsh` v0.1.0-rc.x，开发者预览）
> 设计文档见仓库外 `Doc/`（产品/架构/技术/使用指南）。

把 DSH 的**事件溯源会话**变成可调试的资产：瀑布流轨迹、单步回放（零 Token）、断点暂停/继续、改参重跑（沙箱内）、分叉对比、性能分析，外加 OTel GenAI trace 导出与 `trajectory_*` 模型工具。

## 工作区结构

```text
packages/
├── trajectory-debug/              # Service Definition + wire 类型（纯类型包，无插件入口）
├── trajectory-debug-host/         # Host Provider：回放/性能/对比引擎、断点、投影、命令、RPC 传输
│   ├── src/adapt.ts               # DSH SessionEvent → DebugEvent（唯一接触 DSH 词汇的边界）
│   ├── src/replay-engine.ts       # 确定性回放（纯函数，零模型/工具调用）
│   ├── src/perf-analyzer.ts       # 性能折叠（口径对齐 dsh-session-stats）
│   ├── src/diff-engine.ts         # 分叉对比 + JSON diff
│   ├── src/breakpoint-manager.ts  # agent/pre-step waterfall 断点拦截
│   ├── src/projections.ts         # trajectory/perf 投影单元
│   ├── src/commands.ts            # /trajectory /perf
│   ├── src/sidecar.ts             # 侧车（memory/file 原子 JSON）
│   ├── src/transport.ts           # webserver 自定义路由 RPC（浏览器通道）
│   └── src/index.ts               # apply()：装配 + 卸载撤销
├── trajectory-debug-remotes/      # 双面 typert 骨架（浏览器 RPC 实际走 host transport）
├── client-ui-trajectory-debug/    # 浏览器 "Debug" Tab：瀑布流/性能 + 回放/断点/改参/对比面板
└── trajectory-debug-bundle/       # 组合包：dsh.bundle + cordis.patch.yml
```

## 命令

```sh
corepack pnpm install       # 需要 corepack；Node ≥ 22.19
corepack pnpm -r build      # 产出 lib/（lib-first 清单）
corepack pnpm -r typecheck  # 全部包类型检查
corepack pnpm test          # vitest 单元测试（56 个用例）
corepack pnpm check         # build + typecheck + test 组合门禁
corepack pnpm check:publish # 发布前清单校验
node scripts/smoke.mjs      # 真实 dsh 进程加载冒烟（自动重建 td-smoke profile）
```

## 状态

| 能力 | 说明 |
|---|---|
| 瀑布流数据（引擎） | `buildTrajectoryPage`：turn/step/tool 行、状态、耗时、Token、错误码、过滤、分页 |
| 单步回放（引擎） | `stepContextAt`：模型视角 + 行动视角；`ReplayCursor` 步进/seek |
| 性能分析（引擎） | `analyzePerf`：成功率/分位数、失败归类、Token 分布、TTFT/解码、轮次统计（可配价格表估算成本） |
| 分叉对比（引擎） | `compareTrajectories`：步对齐、工具变更、结果 diff、差异摘要 |
| 断点暂停/继续 | `BreakpointManager`：`agent/pre-step` waterfall 短路 + 超时自动放行 |
| 改参重跑 | `rerunTool` 走 `ctx.tools.execute` 完整管线；`record\|sandbox\|ask` 三档（ask 无 live agent fail-closed） |
| 分叉真实重跑 | `sessions.fork` + `agents.resume` + `followup`；级联 `cascade: truncate\|preserve` |
| 投影单元 | `trajectoryDebug/trajectory` + `perf`（session-projection 注册表，浏览器零代码消费） |
| 命令 | `/trajectory [stepIndex]`、`/perf` |
| 模型工具 | `trajectory_search / trajectory_step / trajectory_perf`（`enableModelTools` 开启） |
| trace 导出 | `export('trace')`：OTel GenAI 语义 spans（Langfuse/LangSmith 就绪） |
| 侧车持久化 | `FileSidecar` 原子 JSON 写入（`sidecar: 'memory'\|'file'`） |
| **浏览器 UI** | "Debug" 会话视图 Tab：**瀑布流 + 性能仪表盘**（投影推送实时渲染）+ **回放/断点/改参/对比控制台**（webserver RPC） |
| **浏览器 RPC 通道** | host 注册 `POST /api/trajectory-debug/rpc`（webserver 自定义路由，typert 无关），客户端 `fetch` 调用 |
| 真实加载 | `scripts/smoke.mjs`：装入独立 profile 并在真实 dsh 进程内加载成功 |

## 浏览器 RPC 传输（typert 无关通道）

DSH 的 typert Remote 链依赖构建期生成器；本插件改用 **webserver 自定义路由**（官方"web-transport 插件注册自己的路由"扩展点）：

- 端点：`POST /api/trajectory-debug/rpc`，请求 `{ method, params }`，响应 `{ ok, value | error }`；
- 方法：`trajectory.list / step.context / perf / replay.start|step|seek / breakpoint.set|remove|list|resume / intervention.rerunTool / variant.fork|list|compare / export`；
- 安全：服务器默认只绑定 loopback，路由不额外放行信任。

## 客户端 bundle 构建

`pnpm -r build && node scripts/bundle-client.mjs` 产出浏览器 bundle：

- 入口 `src/client/index.ts` → esbuild（CJS）→ 包装为 `window.__ModuleLoader__.load({ id, factory })`（DSH 官方客户端格式）；
- 运行时仅外部依赖 `react`（shell 种子词）；全部 dsh 引用均为 type-only（已擦除）；
- 产物 `packages/client-ui-trajectory-debug/lib/client.js`，经 `exports["./client"]` 提供给 modules 扫描器；
- 装入 profile 后需同步到 profile 的包目录（pnpm `file:` 依赖是拷贝）：
  `robocopy packages\client-ui-trajectory-debug\lib <profile>\node_modules\dsh-client-ui-trajectory-debug\lib /MIR`

## 安装到 DSH（profile）

**已发布到 npm，直接安装（无需构建）：**

```sh
dsh plugin --profile web add dsh-trajectory-debug-bundle
dsh web --dump-config        # 应看到 trajectory-debug-host / -remotes / ui-trajectory-debug 三行
```

源码树安装（开发者）：

```sh
corepack pnpm check          # 门禁
node scripts\smoke.mjs       # 真实加载冒烟
dsh plugin --profile web add ./packages/trajectory-debug-bundle
```

安装后重启 dsh web：会话顶部视图 Tab 出现 **Debug**；输入框可用 `/trajectory`、`/perf`。

## 发布状态

[![npm](https://img.shields.io/npm/v/dsh-trajectory-debug-bundle)](https://www.npmjs.com/package/dsh-trajectory-debug-bundle)

5 个包已全部发布到 npm（v0.1.0）：[`dsh-trajectory-debug`](https://www.npmjs.com/package/dsh-trajectory-debug)、[`dsh-trajectory-debug-host`](https://www.npmjs.com/package/dsh-trajectory-debug-host)、[`dsh-trajectory-debug-remotes`](https://www.npmjs.com/package/dsh-trajectory-debug-remotes)、[`dsh-client-ui-trajectory-debug`](https://www.npmjs.com/package/dsh-client-ui-trajectory-debug)、[`dsh-trajectory-debug-bundle`](https://www.npmjs.com/package/dsh-trajectory-debug-bundle)。

发布流程：

```sh
corepack pnpm check            # 门禁
corepack pnpm check:publish    # 清单校验（无 file: 依赖、版本合法、bundle 携带 patch+index.js）
corepack pnpm publish:all      # pnpm -r publish：workspace:* 自动转版本号；prepublishOnly 先构建
```

- 内部依赖 `workspace:*`（pnpm 发布自动改写为版本区间）；禁止提交 `file:` 依赖；
- 仓库 Topics 添加 **`dsh-plugin`**（deepseekdocs.com/ecosystem 自动收录）；精选收录见 `docs/awesome-submission.md`。

## 生态对比

见 [COMPARISON.md](./COMPARISON.md)：与 dsh-message-edit / dsh-plugin-cost / dsh-deeplink / dsh-eval 的定位差异与已落地改进。

## 运行时踩坑（rc.6 实测）

1. **Service 构造器即注册**：`super(ctx, 'trajectoryDebug')` 已完成 `ctx.provide`，apply() 再 provide 会抛 `has been registered`；
2. **`ctx.logger` 是可调用对象**：`ctx.logger(name).info(msg)`，且必须 try/catch 包裹；
3. **pnpm `file:` 依赖是拷贝**：改码后需 `pnpm -r build` + 在 profile 目录重装才会生效；
4. **pnpm 11 供应链策略**：`minimumReleaseAge` 拦截新发布包，冒烟 profile 用 `minimumReleaseAge: 0` 规避。

## 设计要点

- **事件模型自持**：引擎折叠自有 `DebugEvent` 最小模型，`adapt.ts` 是唯一接触 DSH `SessionEvent` 的边界 → 对 DSH 预览期破坏性变更免疫；
- **投影状态为纯 JSON**，满足 projection-cache 持久化契约；
- **"模型可见即已记录"不变式**：分支真实执行只走既有 agent 通道，源会话日志永不被改写；
- **回放零消耗**：引擎不依赖 LLM/工具；
- **客户端 bundle 自建**：不依赖 DSH 的 tsdown 链。

## 兼容性

- 依赖面：`@deepseek-ai/cordis` + `dsh-session / dsh-agent / dsh-commands / dsh-session-projection`（`^0.1.0-rc.6`，随 rc 更新）；
- 插件卸载 = 全部注册（effect）撤销，源会话零影响。
