# Agent Note：横截面计算下沉内核

状态：已实现

[English](2026-10-13-quant-kernel-cross-ic.md) | 中文

## 问题

横截面 IC 工具的面板数学跑在 TypeScript，而每个标的的行情获取本来就是内核往返——每标的一个子进程取K线，宿主再自行做对齐、四个因子与秩相关。延期项说得明白：把面板计算下沉内核，让相关性在已审计模拟器旁边跑，一个请求完成。

## 决策

- **一个新内核 op：`cross_section_ic`。** `kernel-py/pcpt/cross_ic.py` 逐字镜像 TypeScript 管线——共享日对齐（交集、排序）、四个已审计因子（momentum、volatility、volume_ratio、price_position 及其窗口与空预热）、逐日因子横截面对 horizon 日前视收益横截面的 Spearman、以及聚合（平均 IC、std、ICIR、正占比、t 统计），并带同样的亚基点离散度钳制。TS 的 `KernelOp` 联合类型与 HANDLERS 表同步生长。
- **数字必须一致；约定必须一致。** 内核携带与 `inspectCrossPanelCaps` 相同的硬上限（面板 2-10、horizon 1-20），未知因子与共享日不足以 `PanelError`（`ValueError` 子类，线上映射为 BAD_REQUEST）拒绝，其 pytest 钉住完美排序面板、对齐丢弃、退化钳制、上限与响亮失败。
- **TS 管线退化为薄投影。** `runCrossSectionICKernel` 发出携带逐标的K线映射的单个请求；`projectKernelIC` 把内核 snake_case 摘要改名为 TS 词汇（`mean_ic` → `meanIC`……），报告格式化、分窗透镜与合规链零改动。纯 TS 函数（`alignPanel`、`crossSectionIC`、`summarizeIC`）保持导出与测试——它们是内核所镜像的可执行规格。
- **工具任务体缩为取数 + 一个请求。** 逐标的 `get_kline` 保留（已审计的数据路径），随后单个 `cross_section_ic` 调用替换宿主侧的因子/对齐/相关块。启动 envelope、合规规则、快照边界与报告形状不变。

## 考虑过的替代方案

**删除 TS 纯函数、只留内核路径。** 否决：纯函数是内核据以验证的规格，让报告与分窗透镜在没有 Python 运行时时可测；删掉会让内核失去镜像。

**把K线批量获取折进同一 op。** 延期：获取路径带熔断器、缓存与重试；折进 op 会在 Python 里复制这套策略，只省一次往返。

**线上 schema 升版。** 不需要：op 是纯增量，协议版本自会携带。

## 后果

代价：内核现在拥有第二个需保持同步的数学模块——靠两侧的镜像测试（内核 33 pytest、TS 321 vitest）与两侧文档块中声明的共享约定缓解。一次横截面 IC 运行整个面板一个子进程（取数仍逐标的）。验证：TS 321 全绿，工具 fake 断言新 op 序列（三次取数后一个携带完整K线映射的面板请求）；内核 33 pytest 全绿，含新增横截面 IC 用例。双语 README 行已更新；Agent Note 三件套已记录。
