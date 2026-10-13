# Agent Note: 真面板自带挂载的 Remote 面，图表用内联 SVG

Status: implemented

[English](2026-10-09-quant-real-panel.md) | 中文

## 问题

量化研究面板此前是一张声明"后续交付"的占位卡片，核心包导出了 `QuantResearchService` 却从未挂载——Remote 线路在前一切片被移除，因为没有消费者。Phase 3 点名的剩余项是"带核心包 Remote 面的真面板"，而图表问题（echarts 与包体权衡）是明确延期的评审项。

## 决策

- **自包含 Remote 装配，走 customer-acquisition 模式。** 浏览器插件自己挂载核心包的 Remote 贡献（`ctx.remote.$mount(quantResearchRemote)`），然后在注入确切命名空间（`remote.quantResearch`——Cordis 只把命名空间服务快照进 inject 列出该名字的 fiber）的 fiber 上跑面板主体。网关闭包拆 `{ok, value|error}` 信封，错误信息点名失败方法。不改 api-remotes、不动共享注册表：一个插件自带它的服务面。
- **核心包挂载它导出的服务。** `apply()` 现在把 `QuantResearchService` 实例化为服务 fiber（`ctx.plugin(QuantResearchService).await()`），服务在两个账户方法旁新增 `@Remote('listNotes')`。Wire 类型（`AccountSummaryValue`、`NoteSummaryValue` 等）迁到新的 `src/types.ts`，经 `./types` 子路径暴露——纯投影家族（无品牌 id、无 readonly 别名），生成的 Remote 客户端与面板共享同一类型家族。`files` 白名单补上 typert 产物（`lib/typert.*`、`lib/types/**/*.js`）——Remote 包不发生成面时 typert 构建会响亮失败。
- **内联 SVG，零图表库。** `charts.tsx` 渲染持仓权重条形行（HTML/CSS 轨道，宽度百分比来自纯函数 `barGeometry`）与 sparkline（纯函数 `sparklinePoints` 映射出的 SVG 折线）。零新依赖；几何函数由单测钉住，测试断言坐标无需渲染。echarts 问题的结论是"暂不"——记录为限制，不是代码里的决定。
- **诚实的数据边界：持仓权重，不是净值曲线。** 持久域存账户、订单与笔记——没有权益历史——面板画存在的东西（每账户持仓市值权重、笔记列表），不造假曲线。净值曲线卡片点名为等会话→存储的结果回流通道。
- **覆盖率补到门禁，而非进排除清单。** 客户端包用测试达到逐文件 100%：apply-spec 工作台（假 `$mount`、假命名空间、slot 声明）驱动挂载顺序、网关拆包含失败分支、共享控制器注入与 disposer 拆卸；面板测试驱动加载/取消/重试、空态、展开重取、非 Error 拒绝的字符串化。留下的 `v8 ignore` 都带理由（取消读的守卫）。

## 备选方案

**echarts（懒加载引入）。** 否决：仓库图表依赖为零，面板只需要两个小型静态可视化，约 1MB（即使 tree-shaken）买来只读面板用不上的 tooltip。交互式探索落地时再评审。

**净值曲线卡片取自工具输出。** 本切片否决：回测/寻优结果活在会话转写里，不在持久域；把它们接进存储是带独立保留策略问题的另一条通道。从无到有画曲线是落选的那条路。

**只在 web profile 挂载服务。** 否决：`apply()` 是插件唯一的组合路径；profile 条件挂载会让面板的 Remote 命名空间只在部分组合中存在，把缺失的面从加载期保证变成运行期意外。

## 后果

代价：核心插件现在打开域两次（插件主体 + 服务 fiber）——apply spec 断言两次 open 与两次 close；Remote 面按构造只读（两个账户读 + 一个笔记读），面板无法绕过合规门禁。验证：核心包 259 vitest 绿（真实存储栈上 4 个新服务用例），客户端包 25 vitest 绿且两包逐文件 100% 覆盖，`verify-client-packages` 以修正后的依赖拆分通过（静态客户端输入只进 devDependencies），全 workspace 构建再生 typert 面。延期：净值曲线卡片（等结果通道）、交互式图表、面板中的工具输出卡片。
