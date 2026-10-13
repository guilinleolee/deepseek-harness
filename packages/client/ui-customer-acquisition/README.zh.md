# @deepseek-ai/dsh-client-ui-customer-acquisition

[English](README.md) | 中文

获客运营功能的 Web 面板半边：侧边栏入口 + 全屏占位工作台。Node 半边在 [`@deepseek-ai/dsh-customer-acquisition`](../../growth/customer-acquisition/README.zh.md)；任一包安装时经各自 bundle patch 同时拉起两包。

## 安装

```sh
dsh plugin --profile web add @deepseek-ai/dsh-client-ui-customer-acquisition
```

重启 profile：侧边栏底部出现获客运营入口，工作台经 `shell.overlay` 打开。

## 接线方式

浏览器 apply 经 `ctx.remote.$mount()` 挂载 `@deepseek-ai/dsh-customer-acquisition` 生成的 `./remote` 工件，然后在声明了精确服务名 `remote.customerAcquisition` 的 fiber 上注册两个槽位（命名空间服务只解析进 inject 列出该名字的 fiber）。入口与面板共享一个开合控制器；文案走 `customer-acquisition` locale 命名空间。

## Model Experience

### 本地获客运营面板

#### 模型看到什么

无。本包不注册任何工具、提示词段或模型可见上下文；它是 Remote 面的浏览器侧消费者。

#### Token 影响

零。

#### KV Cache 影响

独立。

## Known Limitations and Deferred Work

- **占位面板**——工作台展示全局参数快照与最近审计条目以验证 P0 全链路；八页完整面板随 P4 交付。
- **无离线状态**——Remote 网关不可达时读取失败可见展示；按设计不做浏览器本地缓存（业务数据不进 localStorage）。
