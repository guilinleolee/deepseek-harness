---
description: "提供商无关的图像生成能力：一个注册表背靠一个服务，外加 OpenAI 兼容提供商。"
kind: "package-reference"
---
# @deepseek-ai/dsh-image-generation

[English](README.md) | 中文

## 概述

图像生成作为一种能力接口：一个 `ctx.imageGeneration` 服务，任何消费者都能通过它生成图像，配有一个提供商注册表和一个内置的、使用 OpenAI 兼容 `POST {baseURL}/images/generations` 线协议的提供商。

## 目录

- [使用本包](#use-this-package)
- [提供商](#providers)
- [模型体验](#model-experience)
- [已知限制与延期工作](#known-limitations-and-deferred-work)
- [开发备注](#dev-note)

-----

<a id="use-this-package"></a>
## 使用本包

在 Host 组合中挂载 `@deepseek-ai/dsh-image-generation` 并配置内置提供商，或通过 `ctx.imageGeneration.register()` 注册另一个提供商。消费者调用 `ctx.imageGeneration.generate(request)`，传入提示词和可选的提供商路由；请求中为空的提供商、模型和尺寸会在校验前取配置的默认值。

内置提供商通过共享的 `ctx.credentials` 服务，用 `apiKeyEnv` 引用的凭据进行认证，因此密钥不会出现在插件自己的存储里。它会实时读取 `baseURL`、`apiKeyEnv` 和默认值，设置变更无需重启即可作用于下一次请求。

<a id="providers"></a>
## 提供商

| 提供商路由 | 线协议 |
|---|---|
| `openai-compatible`（内置） | `POST {baseURL}/images/generations`，携带 `model`、`prompt`、`n` 和可选的 `size`；接受 `data` 数组中的 base64 条目 |

内置提供商是面向每一个使用相同线协议的托管图像模型的一条路由；端点和凭据决定它到达哪个服务。

<a id="model-experience"></a>
## 模型体验

无，本包向消费者返回图像字节；没有任何内容通过 LLM 服务进入模型请求。

#### KV Cache effect

无；本包不组装也不发送任何 provider 请求。

<a id="known-limitations-and-deferred-work"></a>
## 已知限制与延期工作

- **不抓取 URL 图像。** 以图像 URL 而非图像字节应答的提供商会遭到拒绝；只接受 base64 图像，因为抓取 URL 会把请求悄悄扩大为凭据范围之外的第二跳网络请求。
- **没有面向模型的工具。** 本服务只是接口；是否把图像生成暴露给模型由消费者决定。
- **失败是可降级的类型化结果，不是给终端用户看的。** `NO_PROVIDER`、`MISSING_CREDENTIAL`、`INVALID_REQUEST`、`PROVIDER_FAILED` 和 `ABORTED` 让消费者选择纯文本回退；内置提供商还限制响应大小和请求期限，并报告提供商的 HTTP 状态。

<a id="dev-note"></a>
### 开发备注

None.
