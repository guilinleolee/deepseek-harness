# Agent Note: walk-forward 验证切一个样本，让寻优保持诚实

Status: implemented

[English](2026-10-08-quant-walk-forward.md) | 中文

## 问题

`quant_optimize_params` 自带警告"网格最优参数来自同一段历史样本，存在过拟合风险"——在一段样本上做网格寻优找到的是该样本的最优参数，但没有任何东西检验它们是否样本外有效。没有验证腿，插件的寻优故事恰恰在被警告的地方留了缺口。

## 决策

- **一次切分、两次内核请求、不新增操作。** `quant_walk_forward` 按 `train_ratio`（0.5–0.9，默认 0.7）把取回的 K 线切成训练/测试两段，在训练段跑 `runBacktestGrid`（仅指标——被审计的网格引擎），排名，选出最优 `(fast, slow)`，然后在测试段用该参数跑一次 `runBacktest`（完整报告，样本外的净值与成交都是真实的）。两个短生命周期 Python 进程——与 `optimizeParamsTool` 同一个"一次请求一个进程"契约——不是每腿每组合一个。
- **过拟合差距是报告的承重段。** `formatWalkForwardSummary` 渲染训练段排名表（复用 `formatOptimizationSummary`）、样本外指标，以及直接的"过拟合差距"段：训练与测试的总收益和夏普差。报告头明确警告测试段是一条样本路径，不是保证；为负且大于噪声的差距是训练最优参数过拟合的信号。
- **门禁在网格规则之上加一条 train-ratio 规则。** `inspectTrainRatioCap` 强制 `train_ratio ∈ [0.5, 0.9]`，使测试段不会被走私值饿死（比例过高）或喂撑（比例过低）。`TRAIN_RATIO_LIMITS` 与 `CONFIDENCE_LIMITS`、`SHOCK_LIMITS` 一样放在 `compliance.ts`——门禁必须持有它所强制的常量。walk-forward 工具复用 `inspectBrokerMarkers`、`inspectBarCap`、`inspectGridCaps` 不变（参数形状与 `quant_optimize_params` 一致）。
- **快照镜像寻优 driver 阶段。** headless driver 经 `ctx.tools.execute` 启动一次真实 `quant_walk_forward` 调用、轮询 `job_output` 到落定、并经真实门禁走一次 train-ratio 拒绝——与寻优轮确立的模式一致，把完成通知时机挡在转写之外。

## 备选方案

**滚动窗口再寻优（锚定或扩展）。** 本切片否决：它把内核请求数乘以窗口数，且复杂化报告（聚合样本外指标 vs 一条路径）；一次切分是检验过拟合声明的最小集，滚动作为延期项点名。

**新的 `walk_forward` 内核操作把训练→排名→测试折进一个进程。** 否决：`backtest_grid` + `backtest` 两个操作已是审计过的引擎；折进一个操作要么复制模拟器，要么撑大内核，而两次请求的代价是多拉起一个进程（同一个契约，不是新契约）。

**测试腿走 `backtest_grid`（仅指标）。** 否决：样本外报告欠读者所选参数的净值曲线与成交，不只是头条指标——`runBacktest` 返回完整报告。

## 后果

代价：walk-forward 是一次切分，不是滚动（作为限制点名）；测试腿参数来自训练排名，所以病态训练网格（所有组合都亏）仍会选出一个"亏得少"的最优——差距段让这件事可见。验证：新增 18 个 vitest 用例（切分、校验、门禁规则、runWalkForward 往返、格式化含空排名回退路径、完整工具生命周期含取消/失败/无 jobs 路径），新代码全覆盖——包内套件 255 绿，内核 pytest 套件无改动保持 28（无内核改动），无钥快照新增 `quant-walk-forward-check` driver 阶段，断言切分、样本外报告、过拟合差距与 train-ratio 拒绝。延期：滚动窗口再寻优、图表卡片、真面板。
