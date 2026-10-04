# @deepseek-ai/dsh-client-ui-quant-research

English | [中文](README.md)

量化研究的 Web 面板插件：一个侧边栏入口加一块声明"仅供研究"范围的框架级占位面板。Phase 1 交付挂载点与免责声明；图表、报表卡片与核心包的 Remote 面随 Phase 2 到来。node 半边是空 apply（让插件可出现在宿主 cordis.yml），用户可见内容全部在以 `./client` 导出的浏览器半边。

## 安装

随核心插件经补丁一起安装：

```sh
dsh plugin --profile web add @deepseek-ai/dsh-quant-research
```

## 面板

- `sidebar.footer.action` 入口在侧边栏两种状态下都能打开面板（宽列为带标签行，窄栏为图标）。
- `shell.overlay` 面板渲染占位卡片：仅供研究声明、无实盘通道声明，以及后续阶段的交付内容。Escape 或关闭按钮关闭。

两个注册共享一个开合控制器，随各自声明的生命周期安装与卸载。

## 模型体验

### 占位面板

#### 模型看到什么

什么都不看。`sidebar.footer.action` 入口与 `shell.overlay` 面板纯展示；Phase 1 不新增提示、工具或 Remote 读取。

#### Token 影响

对每次请求零直接影响。

#### KV Cache 影响

与实时请求无关：面板不触碰请求前缀。

## 已知限制与延期工作

- **占位是设计使然** — 真面板（K线/指标/净值卡片、回测报告）随 Phase 2 落地，连同核心包 Remote 面与本地化词典。
- **暂无本地化词典** — 占位文案为固定中文；locale 命名空间随真面板一起加入。
