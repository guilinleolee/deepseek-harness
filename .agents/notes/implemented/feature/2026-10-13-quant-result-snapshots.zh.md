# Agent Note：结果快照把净值曲线送进面板

状态：已实现

[English](2026-10-13-quant-result-snapshots.md) | 中文

## 问题

Phase 3 以一条诚实边界收官：面板只画持仓权重与笔记列表，因为持久域没有权益历史，而从工具输出伪造曲线曾被明确拒绝。被点名的先决条件是一条会话→存储的结果通道。通道不存在时，面板无法展示绩效——这是研究型回测器最被期待的一个视图。

## 决策

- **通道是域表，不是会话记录解析。** `quant_research` 域 v3 新增 `result_snapshots`：每次成功的 `quant_run_backtest` 落一条记录，含运行参数、头条指标与下采样至至多 240 点的净值曲线（`downsampleEquity`，确定性步长，首点与末点必留）。表保留最新 50 条快照（`SNAPSHOT_KEEP_LIMIT`），保存时从最旧开始修剪。walk-forward 与寻优运行不写快照——只有拥有完整逐 bar 曲线的工具才写。
- **写入搭工具的成功路径，对模型不可见。** `quant_run_backtest` 在内核返回后、envelope 体内持久化快照；模型可见输出保持纯报告。存储失败让工具响亮失败（misconfiguration fails loud），合规门禁不受影响——Remote 面在构造上仍只读。
- **Remote 面新增两个读方法。** `listResultSnapshots` 投影不含净值点的摘要（列表保持轻量）；`getEquityCurve` 返回一条存量曲线。投影随既有 wire 家族放在 `./types`（`ResultSnapshotSummaryValue`、`EquityCurveValue`）。
- **面板复用 sparkline 绘制存量曲线。** 第三个面板区块列出快照卡片（标的、SMA 窗口、累计收益、最大回撤、交易数、日期）；展开一次性取曲线，按卡片尺寸以内联 SVG sparkline 绘制。没有新增图表几何——既有 `sparklinePoints` 映射已覆盖折线图。
- **域 v3 沿用既定演进立场**：加表、升版本、不迁移——v2 载体在打开时拒绝。

## 考虑过的替代方案

**解析会话记录取净值数据。** 否决：会话记录不持久、面板的 Remote 面不可查询，且把面板耦合到提示词记录的内部结构上。

**每个工具都写快照（walk-forward、压力、寻优）。** 延期：这些运行的报告形状不同，面板只有一种卡片；出现第二个消费者时再扩展 `kind` 是纯增量。

**单独的净值表。** 否决：指标与曲线分家会招致记录分叉；每次运行一行快照让投影保持平凡。

## 后果

代价：域版本升至 3（v2 载体打开即拒绝——预发布立场下可接受，本仓库所有组合都以新 spec 打开）；每次回测多一次小型持久写入。验证：quant 套件 265 vitest 全绿（快照下采样/修剪/排序用例、工具写快照用例、以及跑在真实存储栈上的 Remote 列表/曲线用例），面板套件覆盖空态与展开取曲线，全仓构建再生成 typert 面。本切片必须清掉的 master 构建阻塞是预存问题（`commander` 被从 bundle/web-app 误删而 `startup.ts` 仍在引用；七个 experimental/creation 的 tsconfig 仍指向已删除的 invariants 包）——已在同一变更内修复，`build:lib:host` 得以运行。
