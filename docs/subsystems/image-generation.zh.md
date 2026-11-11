# 图像生成

[English](image-generation.md) | 中文

图像生成让消费者通过一个提供商无关的服务 `ctx.imageGeneration` 生成图像。该能力有一个内置提供商，使用 OpenAI 兼容的 `POST {baseURL}/images/generations` 线协议；组合可以通过同一个注册表注册更多提供商。

[`image-generation` 包](../../packages/media/image-generation/README.zh.md)拥有该服务、请求与结果契约，以及内置提供商。

## Request and result

一个请求携带提示词、可选的提供商路由、可选的模型、可选的像素尺寸和图像数量。提供商、模型或尺寸为空的请求会在校验前取配置的默认值，因此消费者只写自己关心的部分。

| 类型 | 含义 |
|---|---|
| `ImageGenerationRequest` | 一个请求的提示词、提供商路由、模型、尺寸和数量。 |
| `ImageGenerationResult` | 一张生成图像的编码字节、媒体类型和生成它的模型。 |
| `ImageProviderInfo` | 一个已注册提供商的路由身份和显示名称。 |

请求契约在到达提供商前完成校验：提示词必须非空且有界，数量必须在 1 到 4 之间，写明了的尺寸必须在像素界限内。违规以 `INVALID_REQUEST` 失败，而不是到达提供商。

## Providers

提供商实现 `generate(request, signal)` 并返回至少一张图像。注册按路由身份进行；重复路由会失败且不替换原有注册。

| 提供商路由 | 线协议 |
|---|---|
| `openai-compatible`（内置） | `POST {baseURL}/images/generations`，携带 `model`、`prompt`、`n` 和可选的 `size`；接受 `data` 数组中的 base64 条目 |

内置提供商通过共享的 `ctx.credentials` 服务，用其 `apiKeyEnv` 设置引用的凭据进行认证。它的端点和凭据都是实时读取的，设置变更无需重启即可作用于下一次请求。以图像 URL 而非内联字节应答的提供商会遭到拒绝；该提供商不会抓取 URL。

## Failure behavior

每一个失败都是带代码的类型化 `ImageGenerationError`：

| 代码 | 含义 |
|---|---|
| `NO_PROVIDER` | 请求的路由下没有注册提供商。 |
| `MISSING_CREDENTIAL` | 内置提供商没有配置或存储凭据。 |
| `INVALID_REQUEST` | 请求违反请求契约，或内置提供商没有端点。 |
| `PROVIDER_FAILED` | 提供商以失败或不可用的正文应答。 |
| `ABORTED` | 调用方中止了请求。 |

消费者读取代码来降级：纯文本回退是对 `NO_PROVIDER` 或 `MISSING_CREDENTIAL` 的预期响应，而不是崩溃。

<!-- BEGIN GENERATED cordis-surface (gen-cordis-catalog.ts) — do not edit between markers -->

<a id="cordis-surface"></a>

## Cordis API

Generated from source by `scripts/gen-cordis-catalog.ts` (verified fresh by `pnpm run verify-cordis-catalog` in doc-sync; regenerate with `pnpm run gen-cordis-catalog`) — the language sides differ only in locale-specific paired document paths. Signature blocks use a `ts cordis-catalog` fence and keep the original source JSDoc; dispatch modes are defined in the [primer](../cordis-primer.zh.md#dispatch-modes), and the framework-inherited `ctx` API lives in [cordis-api/inherited.md](../cordis-api/inherited.md).

<a id="ctximagegeneration--imagegeneration"></a>

### `ctx.imageGeneration` — `ImageGeneration`

The image-generation service: the provider registry and the request path every consumer shares.

```ts cordis-catalog
/**
 * Register one provider; a duplicate route id fails without replacing the
 * original.
 * @param provider - the provider owned by the contributing fiber.
 * @returns the disposer that removes it.
 */
register(provider: ImageGenerationProvider): () => void

/**
 * The registered provider routes, in registration order.
 * @returns the route identities and display names.
 */
list(): readonly ImageProviderInfo[]

/**
 * Produce images for one request. The request's empty provider, model, and
 * dimensions take the configured defaults before validation.
 * @param request - the request.
 * @param signal - caller cancellation.
 * @returns the produced images.
 * @throws an {@link ImageGenerationError} when no provider serves the route,
 *   the request violates the request contract, or the provider fails.
 */
async generate(request: ImageGenerationRequest, signal?: AbortSignal): Promise<readonly ImageGenerationResult[]>
```

Source: [`packages/media/image-generation/src/index.ts`](../../packages/media/image-generation/src/index.ts)
<!-- END GENERATED cordis-surface -->
