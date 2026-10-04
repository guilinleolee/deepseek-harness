# Agent Note: 量化研究插件以"双平面 + pre-execute 红线"的形态交付仅限研究的量化工具

Status: implemented

[English](2026-10-04-quant-research-plugin.md) | 中文

## 问题

harness 缺少量化研究面：行情、指标与回测都在 agent 之外，任何一个关于标的的研究问题都要离开会话去解决。直观的插件形态——一个进程、一个框架、指标"放哪儿都行"——掩盖了三个决定后续所有阶段走向的选择：数字从哪来、数学在哪算、以及什么机制阻止研究工具变成交易工具。

## 决策

- **两个包、两个计算平面。** 核心包（`@deepseek-ai/dsh-quant-research`，`packages/quant/quant-research`）负责编排：参数校验、数据源熔断器、phase-1 指标的 TypeScript 实现（MA/EMA/MACD/RSI/BOLL/ATR），以及三个 `quant_*` 工具。Python 内核（包内 `kernel-py/`，仅标准库）提供 `get_kline`（按标的播种的确定性 synthetic 游走，或懒加载的 akshare 加磁盘缓存）与 `backtest`（以调用方传入 K 线为输入的纯模拟器：收盘出信号、次日开盘成交、全进全出）。一次请求经 subprocess 能力拉起一个进程，所有退出路径——包括工具的协作式 `exec.signal` 截止——都收敛到缝的 terminate 阶梯；没有常驻子进程，也没有自研强杀逻辑。指标放在 TypeScript 侧而非内核，因为会话重放必须看到逐位相同的数值，不受宿主 Python 环境影响。
- **"仅供研究"红线是一个 `tools/pre-execute` 门禁，不是一句约定。** 一个监听器对每个 `quant_*` 调用负责：在冻结参数的任意嵌套深度命中实盘/券商标记（`实盘`、`券商`、`place_order`、`submit_order`、`cancel_order`）即拒绝；无论 schema 如何都执行固定的根数/资金/费率上限；每次拒绝审计进冻结的 `quant_research` 域 v1（`compliance_denials` 表）；审计写入失败仅告警，绝不撤销拒绝。插件的永久红线——无实盘通道——作为设计不变量写入文档而非缺失功能；内核只有虚拟账户。
- **无钥证明用脚本化模型，而非录制模型。** 示例（`examples/quant-research`）组合真实技术栈，快照只替换模型：脚本化的 `quant-mock` 适配器驱动两轮真实工具调用与一次真实红线拒绝，跑过内核子进程、synthetic 数据源、存储审计与门禁。若从真实模型录制，场景既不免费也更难迭代；脚本化转录已覆盖所有"模型并非必要"的环节。
- **插件形态跟随 Loader，而非 bundle。** 插件导出具名的 `apply`/`inject`/`Config`，没有默认导出：Loader 的默认解包会丢掉模块级 `inject`，没有它 `ctx.storageDomain`/`ctx.subprocess` 不可达（`cannot get property ... without inject`）。内核脚本经本包 manifest 解析，因而在 workspace 源码树与已安装 profile 中都能工作。

## 考虑过的替代方案

**指标放内核。** Phase 1 否决：在缺合适 Python 环境的机器上重放会话会改变渲染数值，违反重放一致性；等 phase 2–3 需要 pandas 规模的因子运算时，因子库本来就要进内核。

**常驻内核服务进程。** 否决：每请求拉起约 200 ms 的代价换来无状态协议，没有会话亲和类 bug；若回测变重，jobs 运行时（phase 2 的参数寻优）才是长任务的正规路径，而不是守护进程。

**从真实模型录制快照。** 否决：harvest/stabilize 机制服务于需要真实模型行为的产品路径场景；确定性工具管线只需要确定性工具调用，脚本化适配器让场景在所有机器上免钥。

**快照忽略拒绝路径。** 否决：门禁是插件的核心安全属性；从不拒绝的快照无法发现"静默停止注册"的门禁。

## 后果

代价：每请求的 Python 启动给每次内核调用增加时延（phase-1 数据量下可接受）；`akshare` 缓存尚无 TTL 策略（按存在性命中）；合规标记表是一份固定的中英词表，换一种说法的交易意图可能绕过——真正的承重屏障是上限与"不存在任何下单路径"，标记是响亮的拒绝。验证：两个包 133 个 vitest 用例、两棵 `src` 树逐文件 100% 覆盖，内核 25 个 pytest 用例，以及一条经 Loader 驱动"获取 → 回测 → 拒绝 → 回答"的无钥真组合快照；目录（tool/config/persistence/client/module）在同一变更中再生。延期至后续阶段：PRT 风控套件、带审批审核的 PET 虚拟账户、因子库、基于 jobs 的寻优、图表卡片、面板本地化词典与缓存 TTL 策略——各项均已列入包 README 的限制章节。
