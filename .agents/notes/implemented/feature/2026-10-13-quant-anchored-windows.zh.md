# Agent Note：锚定滚动窗与逐窗快照

状态：已实现

[English](2026-10-13-quant-anchored-windows.md) | 中文

## 问题

滚动 walk-forward 切片留下的两个延期项：训练窗只有扩展形状（固定长度的锚定窗是更保守的替代，却没有旋钮）；滚动运行不写结果快照（面板的净值卡片——Phase4 的门面——因此对滚动运行全盲，只看得见单次回测）。

## 决策

- **`anchor` 钉住训练窗长度；缺省即扩展窗。** `quant_walk_forward` 新增 `anchor`（30-1000 根，`inspectAnchorCap` 合规封顶）。`windows ≥ 2` 且给出 anchor 时，`splitAnchoredWindows` 以 `segmentLength = floor((n − anchor) / windows)` 为步长前移：第 i 窗的训练段是紧邻其测试段之前的 `anchor` 根——固定长度、滑动位置、测试段互不重叠、无前瞻。报告切分节与任务标签都标明模式；扩展窗默认逐字节不变。
- **校验镜像切分。** `validateAnchoredParams` 检查窗口数、anchor 边界、anchor 覆盖最宽慢线（网格预热）、每个测试段同样覆盖，并把网格不变量委托给既有 `validateGridSpec` 按 anchor 长度校验。
- **滚动运行逐窗写快照。** `runRollingWalkForward` 接受可选 `onWindow(result, barsUsed)` 钩子；工具传入一个闭包，经已审计的 `saveSnapshot` 通道持久化每窗样本外报告（params = 该窗重选的参数对 + 两腿覆盖的K线数）。聚合 markdown 保持模型可见输出；快照是持久旁路，沿用保留 50 条的修剪。快照写失败让任务响亮失败——缺窗不报的滚动报告会误导面板。
- **启动返回携带形状。** envelope 仅在锚定时附 `anchor`，调用方与测试无需从几何反推模式。

## 考虑过的替代方案

**单独的 `quant_walk_forward_anchored` 工具。** 否决，理由同前：一个整数的模式差异不值得第二个工具表面积、第二个 JobKind、第二条规则链。

**给聚合写一条快照（每次滚动一条）。** 否决：快照 schema 承载一条净值曲线，聚合是 markdown。逐窗记录完全复用既有 schema，且给面板每段样本外一张卡——这正是目的。

**快照失败静默跳过该窗。** 否决：部分持久化会让滚动运行在面板上显示得比实际少，且无任何提示。响亮失败与插件的存储立场一致。

## 后果

代价：锚定运行只用 `anchor + segmentLength * windows` 根K线（不足一段的尾部丢弃——切分节已声明）；每次滚动运行至多写 10 条快照。验证：316 vitest 全绿——新用例覆盖锚定几何（定长、滑动、测试段不重叠、无前瞻）、锚定校验边界、anchor 合规上限、工具级锚定任务与其模式标签，以及滚动任务的逐窗快照写入（两窗 → 两条记录）。双语 README 已更新；延期清单划掉前两项。
