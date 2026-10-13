# @deepseek-ai/dsh-client-ui-quant-research

English | [中文](README.md)

量化研究的 Web 面板插件：一个侧边栏入口加一块框架级面板，只读展示 PET 虚拟账户与研究笔记，数据来自核心包的 Remote 面——由本插件自己经 `ctx.remote.$mount` 挂载。图表用内联 SVG（`charts.tsx`——持仓权重条形图与折线 sparkline），零图表库依赖。node 半边是空 apply（让插件可出现在宿主 cordis.yml），用户可见内容全部在以 `./client` 导出的浏览器半边。

## 安装

随核心插件经补丁一起安装：

```sh
dsh plugin --profile web add @deepseek-ai/dsh-quant-research
```

## 面板

- `sidebar.footer.action` 入口在侧边栏两种状态下都能打开面板（宽列为带标签行，窄栏为图标）。
- `shell.overlay` 面板渲染：
  - **虚拟账户** — 每账户一张卡片（名称、现金、权益），内联 SVG 条形图画持仓权重；展开卡片经 `getAccountState` 重取完整状态并显示持仓数。
  - **研究笔记** — 按时间倒序的列表（标题、标的、日期），读自 `research_notes` 表。

两个注册共享一个开合控制器，随各自声明的生命周期安装与卸载。插件在注册 slot 之前挂载核心包的 Remote 贡献，并注册 `quant-research` locale 命名空间（中/英）承载文案。

## 模型体验

### 研究面板

#### 模型看到什么

什么都不看。`sidebar.footer.action` 入口与 `shell.overlay` 面板纯展示；面板不新增提示、工具或请求前缀内容。

#### Token 影响

对每次请求零直接影响。

#### KV Cache 影响

与实时请求无关：面板不触碰请求前缀。

## 已知限制与延期工作

- **只读是设计使然** — 一切变更（创建账户、调仓、存笔记）都走模型工具自带的合规与审核流；Remote 面只暴露读操作，面板无法绕过门禁。
- **暂无净值曲线卡片** — 持久域存账户、订单与笔记，没有权益历史，面板画的是持仓权重而非绩效曲线；净值卡片等会话→存储的结果回流通道。
- **面板图表是静态 SVG** — 条形图与 sparkline 无 tooltip、无缩放；交互式图表仍是权衡包体后的显式评审项。
