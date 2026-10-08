# @deepseek-ai/dsh-quant-research

English | [中文](README.md)

面向 DSH 的量化研究插件：内核支撑的行情获取、确定性 TypeScript 指标、含风险/压力/因子/PET 套件的日线双均线回测，以及跑在 jobs 运行时上的参数寻优——全部受"仅供研究"合规门禁约束。插件注册十七个模型工具（`quant_get_kline`、`quant_compute_indicator`、`quant_run_backtest`、`quant_assess_risk`、`quant_stress_test`、PET 账户工具、因子/IC 工具、笔记/报告工具、`quant_compare_backtests`、`quant_research_report` 与 `quant_optimize_params` 与 `quant_walk_forward`），打开 `quant_research` 存储域保存拒绝审计，Python 计算内核以"每次请求一个短生命周期受管子进程"的方式运行。插件不存在任何实盘通道：红线由 `tools/pre-execute` 监听器强制执行，并在每个工具输出中声明。

## 安装

```sh
dsh plugin --profile web add @deepseek-ai/dsh-quant-research
```

补丁会同时插入两行——本插件与 `@deepseek-ai/dsh-client-ui-quant-research` 面板——一条命令安装完整功能。内核要求宿主机有 Python 3 解释器（见 `kernelCommand`）；phase-1 数据源走 synthetic，完全离线可用。

## 配置

所有字段均可选，写在 bundle 行的 `config:` 下；非法值在插件加载时直接失败。

- `dataSource` — `synthetic`（默认；按标的播种的确定性离线随机游走）或 `akshare`（内核经 akshare 拉取 A 股日线；需先 `pip install -r kernel-py/requirements.txt`）。
- `kernelCommand` — 内核使用的 Python 解释器；默认取平台启动器（Windows 为 `python`，其余为 `python3`）。
- `cacheDir` — 内核的 K 线缓存目录；默认 `<dshHome>/quant-research/cache`（仅 `akshare` 源使用）。
- `toolTimeoutMs` / `kernelRequestTimeoutMs` — 模型侧工具预算与单次内核请求截止（内核截止必须小于工具预算）。
- `sourceMaxRetries` / `fuseThreshold` — 内核侧拉取重试次数，以及触发数据源熔断的连续失败次数。
- `defaultCash` / `feeRate` — 调用方省略时的回测初始资金与单边费率。

API 密钥（例如后续阶段的 Tushare token）不进配置：请求时由内核经 credentials 能力解析，内核继承的是脱敏后的父环境。

## 架构

参数寻优跑在 jobs 运行时上，而不是守护进程：`quant_optimize_params` 一次取回 K 线，把整个（快线, 慢线）网格通过一次 `backtest_grid` 内核请求跑完——每个组合都调用同一个被审计的模拟器，线上只传指标——整个过程在宿主 `ctx.jobs` 注册表（kind `quant-optimize`）启动的可取消后台任务里进行。工具立即返回任务 id；模型用 `job_output` 收取排名后的 Markdown 报告，用 `job_kill` 取消。组合里没有 jobs 运行时时，工具以友好的配置错误失败，而不是退化成阻塞调用。

模块名对应研究流水线：`src/pdat`（数据接入与熔断器）、`src/paat`（指标与因子）、`src/pcpt`（回测驱动、报告与寻优），另有 `src/kernel-client`（子进程协议）。TypeScript 侧校验全部参数、持有熔断状态机，并在本侧确定性实现 phase-1 指标，保证会话重放看到完全相同的数值；Python 内核（`kernel-py/`）负责 synthetic/akshare 行情，并把回测实现为"以传入 K 线为输入的纯函数"。线上协议是换行分隔 JSON，每个请求使用全新关联 id；一次请求拉起一个进程，所有退出路径——包括协作式 `exec.signal` 截止——都收敛到 subprocess 缝的 terminate 阶梯。没有自研强杀逻辑，也没有常驻子进程。

## 合规门禁（红线）

一个 `tools/pre-execute` 监听器对每个 `quant_*` 调用执行红线检查，其余调用经 `next()` 放行：

1. **仅限研究意图** — 任何参数字符串在任意嵌套深度命中实盘/券商标记（`实盘`、`券商`、`place_order`、`submit_order`、`cancel_order`）即拒绝，返回友好中文理由。
2. **硬上限** — K 线根数、回测资金、费率、VaR 置信度、压力幅度、调仓权重，以及寻优网格（轴界限、整数步长、快线整段严格低于慢线整段、组合数 ≤ 200，且按工具同样的默认值解析）即使绕过 schema 也被固定上限拦下。
3. **持久审计** — 每次拒绝向 `quant_research` 域（版本 1，冻结）追加一条 `compliance_denials` 记录，含工具名、理由、agent id 与时间戳；审计写入失败仅告警，绝不撤销拒绝。

每条红线至少有一条非法路径单测，无钥快照在真实组合中驱动了一次真实拒绝。

## 工具

| 名称 | 作用 |
|---|---|
| `quant_get_kline` | 经内核获取某标的最近 N 根日线（OHLCV）。 |
| `quant_compute_indicator` | 对收盘价计算 `ma` / `ema` / `macd` / `rsi` / `boll` / `atr`。 |
| `quant_run_backtest` | 运行日线双均线模拟（收盘出信号、次日开盘成交、全进全出），返回净值曲线、成交与绩效指标。 |
| `quant_assess_risk` | 单标的历史模拟法尾部风险：VaR、CVaR、年化波动率与区间最大回撤。 |
| `quant_stress_test` | 在冲击后的价格路径上重跑同一回测（crash 黑天鹅跳空 / liquidity 流动性阴跌），对比基准与冲击后指标。 |
| `quant_account_create` / `quant_account_state` | 创建与查询 PET 虚拟账户（模拟盘，仅供研究）。 |
| `quant_execute_rebalance` | 集中度校验 + 失败即拒的人工审核后，对虚拟账户按最新收盘价模拟调仓。 |
| `quant_compute_factor` / `quant_factor_ic` | 截面因子（动量/波动率/量比/价格位置）与 Spearman IC / Information Ratio。 |
| `quant_save_note` / `quant_list_notes` / `quant_export_report` | 持久化研究笔记，支持标的/标签筛选与 Markdown 导出。 |
| `quant_compare_backtests` | 同标的同时跑两组参数，并排对比收益、回撤与夏普。 |
| `quant_research_report` | 运行一次回测并输出结构化 Markdown 研究报告（参数/指标/净值/成交）。 |
| `quant_optimize_params` | 在 jobs 运行时上以可取消后台任务做双均线网格寻优；用 `job_output` 收取排名报告。 |
| `quant_walk_forward` | 切训练/测试两段，训练段网格寻优，用最优参数在测试段跑一次回测；以后台任务报告样本外指标与过拟合差距。 |

所有结果都是统一的 `{code, msg, data}` 信封——成功 `code: 0`，失败返回错误档位数字码与 `data: null`（`NETWORK`、`DATA`、`KERNEL`、`RISK`、`CONFIG`、`CANCELLED`、`INTERNAL`），且每个渲染输出都以"仅供研究参考"声明结尾。

## 会话事件

`quant/kernel-fault` 在内核客户端完成分类的瞬间，把一次内核平面故障（拉起失败、崩溃、超时、协议违例）记录为 log-only 诊断事件；它不进入模型请求，友好失败信息由工具结果承载。仓内事件词表经生成的持久化目录登记；`ignorable` 信封标记保留给出仓插件。

## 模型体验

### 研究工具

#### 模型看到什么

插件加载后，`quant_get_kline`、`quant_compute_indicator`、`quant_run_backtest`、`quant_assess_risk`、`quant_stress_test`、PET/因子/笔记工具，以及 Phase3 的报告与寻优工具 schema 加入提示装配；文本渲染包括：K 线尾部的日期化 OHLCV 列表、指标近期读数与窗口、回测头条指标（总/年化收益、最大回撤、夏普、胜率、交易笔数、期末净值）、历史模拟尾部指标（VaR/CVaR/波动率/回撤）、压力对比（基准 vs 冲击后收益/回撤/夏普）、对比优胜行、完整研究报告 Markdown，以及寻优启动卡片（任务 id、网格形状、组合数与 `job_output` 收取指引）。拒绝以错误结果形式出现，携带门禁的中文理由。

#### Token 影响

有界：插件加载期间，每次装配请求包含十六个工具 schema（约 3,200 token）；渲染最多输出 10 行 K 线与 5 条指标读数。

#### KV Cache 影响

schema 加入提示前缀的工具块；加载或卸载插件会从该点起使可复用前缀失效，与一切工具注册一致。

## 已知限制与延期工作

- **无实盘通道（设计使然）** — 这是插件的永久红线，不是缺失功能；门禁拒绝意图标记，内核只有虚拟账户。
- **Phase 3 剩余** — 策略对比、研究报告、jobs 运行时参数寻优与 walk-forward 样本外验证均已上线；图表卡片（echarts 与包体权衡）与带核心包 Remote 面的真面板随后落地。
- **寻优报告只保留前 N 名** — 每组合的净值曲线与成交流量在内核线上被丢弃以控制响应体积；选中某组参数后用 `quant_run_backtest` 取完整曲线。
- **walk-forward 是单次切分，非滚动** — `quant_walk_forward` 按调用方指定比例做一次训练/测试切分；滚动窗口再寻优（锚定或扩展）延期。
- **内核缓存无 TTL 策略** — `akshare` 缓存按文件存在性命中，不看新鲜度；刷新策略等具体部署需求出现后再定。
- **`akshare` 依赖宿主环境** — 未安装 `kernel-py/requirements.txt` 前该源以友好配置错误失败；Tushare 是后续可选源（其开源库自 2024-03 起停滞）。
- **pytest 覆盖率为信息性指标** — 仓库的逐文件 100% 门禁只覆盖 TypeScript `src`；内核 pytest 套件独立运行、独立报告。
- **Excel 导出与 echarts 卡片延期** — Markdown 优先的报表避免引入 xlsx 依赖；图表库去留是 Phase 3 的显式评审项（权衡包体）。
