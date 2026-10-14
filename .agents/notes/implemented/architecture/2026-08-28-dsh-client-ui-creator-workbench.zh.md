# Agent Note: `@deepseek-ai/dsh-client-ui-creator-workbench` 以零依赖三栏 Tab 形态接入既有 DSH slot 系统发布

Status: implemented

[English](2026-08-28-dsh-client-ui-creator-workbench.md) | 中文

## Problem

Creator Workbench 有 host 半（`@deepseek-ai/dsh-creator-workbench`）通过标准 DSH 会话驱动 SOP，但创作长稿的创作者希望有一个独立三栏视图（文件树 / Markdown 编辑器 / 流水线状态）放在聊天抽屉旁边，而不是替代它。DSH Web shell 已经有 slot 化的 UI 组合系统；问题是 workbench Tab 注册到什么位置，以及它的组件读什么。

最直接的回答是一个 DSH 全感知的客户端包，依赖 runtime、conversation、slots、layout 包，再加上一个状态库。约束集只有三个真实需求：文件树（状态：选中路径、展开集合）、编辑器（状态：打开文档、active 路径、dirty 标记）、流水线面板（状态：5 阶段状态）。"第三方状态库"答案把一个文件的状态变成两个新维护包；"import 每个 DSH 客户端 primitive"答案让 workbench 依赖它根本不用的图标和按钮 primitive，仅仅为了保持 bundle 形态一致。

## Decision

浏览器半以 `@deepseek-ai/dsh-client-ui-creator-workbench` 形态发布，是一个自包含的 DSH 客户端插件，只贡献一个顶级 Tab。包唯一的 state 管理是一个 60 行的 `stores.ts`：在三个小 bundle（file tree、editor、pipeline）上定义 `getState` / `subscribe` / `actions`，通过一行 `useStoreState` hook 绑定到 React 18 内置的 `useSyncExternalStore`。没有 `zustand`、没有 `Redux`、没有 observable 库；`React 18` 原语是组件满足 `packages/client/AGENTS.md` 四 props shares 契约所需的唯一东西。

图标是内联 SVG（`FileTreePanel.tsx` 里的 `ChevronRight`、`FolderIcon`、`FileIcon`），编辑器的"保存"控件就是普通 `<button>`。包通过 `dsh.client.inject`（信息性依赖边，不是 Cordis 激活顺序）只依赖 `clsx` 和 `@deepseek-ai/dsh-client-ui-{connection,locale,runtime,ui-conversation,ui-layout,ui-sidebar}`。Slot 注册是 `ctx.effect()` 内的一次 `ctx.slots.register({ name: 'shell.tab.creator-workbench', store: { fileTree, editor, pipeline } }, Component)`，套 try/catch，这样未挂载 slots service（headless smoke harness）就是 no-op 而非加载错误。

`apply()` 本身在 host 半（`src/index.ts`）为空；浏览器半是 `src/client/index.ts`，包通过标准三个注册面接入 dsh-web bundle：包 `tsconfig.json` 和根 `tsconfig.client.json` aggregate 的 references；包 `package.json` 里的 `dsh.client` 行声明 `platform: 'web'` 和 inject 列表；`packages/bundle/web-app/package.json` 对 `@deepseek-ai/dsh-client-ui-creator-workbench` 的依赖让 workspace 的 `node_modules/@deepseek-ai/...` 解析能找到这一行。`dsh.client` 行的 platform 值驱动客户端插件扫描器，`./client` 导出（`lib/client.js`）是发到浏览器的 dynamic bundle。

## Alternatives considered

**每个 workbench 列一个 DSH 客户端包（`dsh-client-ui-creator-workbench-tree`、`dsh-client-ui-creator-workbench-editor`、`dsh-client-ui-creator-workbench-pipeline`）。** 三个更小的包通过 slots 组合，每个可独立复用。否决因为（a）三个 store 在 workbench 之外没有消费者，（b）slot 组合会强制每个用户按正确顺序注册三个 slot，（c）拆分把测试面从 3 个 spec 涨到 9 个，行为不变。单包组合是同样的 slot 注册；区别只是谁来负责保持三个 store 同步。

**Zustand 做状态管理。** runtime 包已经在用 zustand，所以加进 workbench 感觉是自然之选。否决因为 zustand 是 runtime-layer 关注点（数据对象层），而 workbench 状态是每个 tab 的视图关注点，完全活在展示层。把 zustand 引入浏览器半也需要一个 `dsh.client.external` 条目——zustand 是 non-baseline dynamic 请求——`verify-client-packages` 脚本会强制要求。手工的 `useSyncExternalStore` 适配器 60 行，没有第三方面，跑在平台自己的 React 原语上。

**把三栏渲染进既有的 conversation 面（右侧抽屉）。** 这意味着没有新 Tab、没有新 slot、完全没有客户端包。否决因为 conversation 抽屉 320px 宽且可滚动，光文件树就要 240px 静态宽度，把三栏塞进 320px 抽屉需要 CSS 魔法，在大多数屏幕上隐藏编辑器和流水线。Tab 给 workbench 一个真实画布，用户保留 conversation 抽屉走模型驱动阶段。

## Consequences

workbench Tab 是 opt-in：不依赖 bundle 的 web-app patch 的 profile 永远看不到它，dsh-web profile 因为依赖现在在 bundle 的 `package.json` 里所以自动看到。三个结果。第一，workbench 状态是 per-tab 而不是 per-session：开新 Tab 给一个全新的 `createFileTreeStore()` / `createEditorStore()` / `createPipelineStore()` 三元组，关 Tab 让 React fiber 释放，意味着 host 不需要考虑跨 Tab 状态泄漏。第二，包可以通过删 bundle 依赖和一行 `tsconfig.client.json` 条目来移除；workbench 暴露的 runtime 词汇（`shell.tab.creator-workbench`）是单一 slot 名，没 schema。第三，`useSyncExternalStore` 意味着组件在 snapshot 变化时重渲染而无需手动订阅簿记，`actions` handle 保持引用稳定，所以依赖 `store.actions.foo` 的子组件不在每个 parent tick 上重渲染。

组件套件跑 3 个 jsdom spec（默认 mount、流水线状态更新、通过文件树打开文件），首次运行 11 秒用于 jsdom 环境启动。内联 SVG 图标相对于 dsh-web 其它部分是轻微的视觉回归（其它部分用 `@deepseek-ai/dsh-client-ui-primitives` 图标集）；生产接线上 primitives 出三个字形（chevron-right、folder、file）的稳定面后替换它们。
