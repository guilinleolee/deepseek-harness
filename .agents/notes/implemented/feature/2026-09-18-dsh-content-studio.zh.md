# Agent Note：Content Studio 通过两个现成的加法槽进入 web 外壳，不新增导航槽

Status: implemented

[English](2026-09-18-dsh-content-studio.md) | 中文

## 问题

Web 端此前没有"内容创作"入口：创作动词只存在于模型的技能目录里，用户不知道怎么提问就永远看不见。树里已有三次尝试（`packages/extensions/dsh-creation-workbench`、`packages/client/client-ui-creator-workbench`、已删除的 `dsh-web-ui/packages/dsh-customer-service`），但每一处调用的注入 API 在当前客户端运行时都不存在（`ctx.slots.sidebar.add`、`ctx.slots.page.register`、没有声明者的 `shell.tab.*` 槽、`ctx.webServer`），全部无法渲染。本质问题是：插件如何在不改框架的前提下，给组装后的 web 外壳加一个一等公民的功能入口和一个完整工作台页面。

## 决策

`packages/client/ui-content-studio` 只注册进外壳已声明的两个加法槽，不触碰任何其他包：

- **入口**填充 ui-sidebar 的 `sidebar.footer.action`（此前零注册者的 `list` 槽）。宽栏渲染带文字的行，56px 窄栏渲染图标——owner 契约（`{ wide }`）本来就覆盖两种状态。
- **页面**填充 ui-layout 的 `shell.overlay`（`list`，文档明确写着"这是你自己的全帧表面的加法位"）。overlay 层的 CSS 已给每个直接子元素开启 pointer events，固定全屏的工作台无需改动框架。打开态覆盖全帧；Escape 和头部关闭按钮收起；关闭态渲染 null 而注册保持挂载。

两个注册通过单个 `slots.inject('sidebar.footer.action', function* () { … })` 生成器按声明生命周期原子安装——`ui-brand-official` 确立的模式——并共享一个注入到两处的开关控制器，因为组件状态无法跨两个槽注册。

工作台提供双意图能力菜单（做内容按媒介分：图文/文章/视频/音频；做运营按阶段分：发现/策划/发布/复盘），每项带四态成熟度徽标（已验证 / 可用 / 需配置 / 接入中）。点击会把含【…】填空标记的结构化指令模板复制到剪贴板。

**内容库视图**通过 `contentOutputs/list` Remote 读取 agent 产物：`packages/creation/content-outputs` 是仅 Remote 的 Typert 网关（`@deepseek-ai/dsh-content-outputs`，无 ctx key），每次调用扫描 `<dsh home>/outputs` 并投影磁盘约定——一次创作一个目录、成品在根、中间素材在 `assets/`、`.dsh-output.json` 是唯一元数据（`formatVersion 0`，无兼容性承诺）。挂载是**自包含的**：工作台自己的异步 `apply` 通过 `ctx.remote.$mount()` 挂载两个 `/remote` 产物（把 api-remotes 的模式移进了插件），浏览器 bundle 自带完整服务端通信面，api-remotes 对这两个包毫无感知——从花名册移除本插件即整体下线该功能。损坏的元数据不会隐藏其项目（回退值 + `hasMetadata: false`）；无法读取的目录在快照的 `problems` 中具名报告。

**内容日历视图**用同一模式加上了变更面：`packages/creation/content-schedule`（`@deepseek-ai/dsh-content-schedule`）在库根的一个系统文件 `_schedule.json` 上提供 `contentSchedule/list|put|remove`——`_` 前缀让产物扫描器早已把它视为非项目条目。条目沿用 Easel 的 `idea → draft → scheduled → published` 流转；`put` 仅按生成的 UUID 做 upsert；每个方法都在 atomic-write 写者锁下读取或提交，读不加锁、写串行化。月历网格本身是纯模块（`calendar.ts`），不依赖 React 做单元测试；组件只持视图状态（当前月份、唯一打开的添加表单），每次变更按返回快照重渲染——磁盘文件仍是唯一事实，这也让 agent 通过普通文件工具读到同一份日历。

阶段 1 不读服务器数据。目录是随包发布的静态数据，展示文案在 `content-studio` locale 命名空间；invariant 伴随包与 ui-workspace 同理保持为空（纯展示型消费者，无跨插件可变状态）。

## 已否决的替代方案

**给 ui-sidebar 新增 `sidebar.nav.entry` 槽。** 原计划。审计发现 `sidebar.footer.action` 无人占用后，阶段 1 否决：为单一消费者新增框架槽不是默认选项，已有的文档化扩展点覆盖了该用例。导航槽扩展推迟到入口需要进入主列（workspaces 区域之上）而非脚部时再做。

**组合进 `sidebar.workspaces` 或 `conversation` 列。** 两者都是有占据者的 `single` 槽，注册即整体替换既有 UI，并把工作台耦合进 ui-workspace / ui-conversation 内部。overlay 保持工作台严格增量。

**现在就从 `ctx.skills` 派生目录。** `skill.list` RPC 存在但附着会话，且形态不符合菜单所需；自动派生成熟度无解。先发静态数据，等阶段 2 配套的目录 RPC（连同 outputs 项目树）落地后再接。

## 后果

第一次有真实先例证明：第三方插件仅凭文档化槽位即可给 web 外壳新增功能入口和完整页面——`dshmarket` 在花名册外预演过，这是树内模板。三个代价：点击能力项是复制到剪贴板而非预填 composer 草稿（客户端运行时没有 draft 通道，补通道仍是后续的运行时改动）；能力菜单的成熟度徽标在目录 RPC 出现前需手工维护；页面是 root 作用域、无会话上下文，不能展示会话级状态。内容库的读取刻意设计为逐次扫描的 Remote——产物根目录是 agent 的写入面，加缓存只会多出第二份事实。启动快照通道（`pnpm run test:web:built`）通过构建后的花名册覆盖本插件。
