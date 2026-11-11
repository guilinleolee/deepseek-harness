---
description: "图像生成能力家族：一个提供商无关的服务，外加 OpenAI 兼容提供商。"
kind: "package-group"
---

# packages/media

[English](README.md) | 中文

## Summary

media 组拥有产生非文本产物的能力。目前只包含一个包：图像生成接口，通过一个提供商无关的服务，让任何组合都能生成图像，并带有一个使用 OpenAI 兼容图像线协议的内置提供商。

## Table of Contents

- [Packages](#packages)
- [Related documentation](#related-documentation)
- [Dev Note](#dev-note)

-----

<a id="packages"></a>
## Packages

| 包 | 职责 | ctx key |
|---|---|---|
| [`image-generation`](image-generation/README.zh.md) | 提供商无关的图像生成注册表，外加 OpenAI 兼容提供商 | `ctx.imageGeneration` |

<a id="related-documentation"></a>
## Related documentation

- [图像生成子系统](../../docs/subsystems/image-generation.zh.md) — 请求与结果契约、提供商注册表，以及内置提供商。

<a id="dev-note"></a>
## Dev Note

None.
