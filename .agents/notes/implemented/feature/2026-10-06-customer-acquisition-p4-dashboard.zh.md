# 获客插件 P4：数据看板与八页工作台

Status: implemented

[English](2026-10-06-customer-acquisition-p4-dashboard.md) | 中文

## 背景

P4 收口获客插件的 manifest §9：一个 agent 可调的 `customer_acquisition_report_overview` 工具，加一个操作者在 Web 面板看到的八页工作台。P0 地基、P1 线索台账与 AI 打分、P2 有界 GEO 网站诊断、P3 培育文案与跟进 SOP 各自的域表都汇入同一处聚合缝；P4 是这座金字塔只读的顶——所有写仍留在原处，看板绝不改写。

## 决策

- **一个聚合服务同时喂两个面。** `ReportService` 是对已开域的无状态读：七项 manifest 指标（线索总量、区间新增趋势、意向/来源/打分分布、SOP 任务完成率、GEO 滚动汇总）每次调用塌缩为一个 `OverviewValue`。`report_overview` 工具服务 agent；`@Remote getOverview` 与各模块的 `@Remote list*` 面服务面板。没有第二条聚合路径，没有缓存投影——面板每次选择器变化都重读。
- **台账的 list scope 即看板的 scope。** `lead_scope=own` 操作者在所有按线索过滤的指标里只看到自己的线索加公海（计数、意向、来源、打分、任务）；GEO 指标是站级共享的，因为一次扫描的 URL 不是某个操作者的属性。面板每次调用都解析 web 操作者，所以同一个 Remote 面服务每个员工，无需按角色分叉。
- **窗口与下钻是请求期的，不落盘。** `period`（today/week/month/custom）与 `group_by`（none/industry/source）挂在 `OverviewRequest` 上；服务用注入的时钟（测试确定性）解析窗口，在内存里分组。自定义区间缺任一边界即响亮报错；起止颠倒即响亮报错。无持久化，无迁移。
- **wire 类型住在公共 type 子路径上。** Typert 生成器要求每个 `@Remote` boundary type 从公共非根 type 子路径导出，所以 overview 类型从 `src/report/types.ts` 上提到 `src/types.ts`，与其它 wire 投影并列；面板读面把 ledger/scoring 的 boundary 类型 re-export；Remote 参数去 default（改 optional）；读面用显式数组返回类型而非 `ReturnType` 查询。lib/typert.remote-client 工件带 14 个 Remote 方法供面板挂载。
- **工作台是一个共享开关 + 八个无分支页。** `useRemoteRead` 为每页持有 loading/ok/failed 生命周期；`ReadFallback` 在所有页面同构渲染两个非 ok 态，所以每页直接画自己的值表。OverviewPage 带 period 与 drill-down 选择器并在变化时重读；GEO 页行内展开单条报告；Settings 页通过 `updateSettings` 写页数上限并拒绝非整数输入。P0 占位面板退役。

## 否决

- **在投影表上做第二次聚合** —— 域里已有每条记录；投影表会复制状态并要求每次上游改动都迁移。聚合足够便宜，按调用重算即可。
- **按角色分叉面板** —— 同一个 Remote 面服务每个操作者，因为 list scope 是操作者的，不是面板的。角色分叉 UI 会复制读连线却无收益。
- **Remote 面用 `ReturnType<Service['method']>`** —— Typert 生成器要按名看到 boundary type，所以返回类型是显式数组；`ReturnType` 会把它藏到生成器无法 re-export 的别名后。
- **带默认值的 Remote 参数** —— Typert 生成器拒绝 `@Remote` 参数上的默认值；面板的 `?` optional 形式承载同样的"省略即用默认"契约，又不绊生成器。

## 后果、风险与取舍

看板只读且幂等；每页是其 Remote 读的纯函数，所以面板绝不通过看板写。共享读 Hook 意味着加一页只花一个读闭包加一张值表——loading 与 failure 态已布好。聚合信任域表的 `created_at` 做窗口、`intent_level` 做意向分布；未设意向的记录跳过（桶按零填）。Typert boundary-type 规则现是承重的：未来任何 `@Remote` 面若引入新 boundary type，必须从 `src/types.ts` re-export，否则生成器在构建时失败。八页 bundle 220 KB / gzip 39 KB——内容创作室先例依旧成立。
