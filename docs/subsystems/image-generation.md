# Image generation

English | [中文](image-generation.zh.md)

Image generation lets a consumer produce images through a provider-neutral service, `ctx.imageGeneration`. The capability has one bundled provider speaking the OpenAI-compatible `POST {baseURL}/images/generations` wire shape; a composition can register more providers through the same registry.

The [`image-generation` package](../../packages/media/image-generation/README.md) owns the service, the request and result contract, and the bundled provider.

## Request and result

One request carries a prompt, an optional provider route, an optional model, optional pixel dimensions, and an image count. A request with an empty provider, model, or dimensions takes the configured defaults before validation, so a consumer names only what it cares about.

| Type | Meaning |
|---|---|
| `ImageGenerationRequest` | The prompt, provider route, model, dimensions, and count of one request. |
| `ImageGenerationResult` | One produced image's encoded bytes, media type, and producing model. |
| `ImageProviderInfo` | One registered provider's route identity and display name. |

The request contract is validated before it reaches a provider: a prompt must be non-empty and bounded, the count must be between 1 and 4, and a stated dimension must sit inside the pixel bounds. A violation fails with `INVALID_REQUEST` instead of reaching the provider.

## Providers

A provider implements `generate(request, signal)` and returns at least one image. Registration is by route identity; a duplicate route fails without replacing the original.

| Provider route | Wire shape |
|---|---|
| `openai-compatible` (bundled) | `POST {baseURL}/images/generations` with `model`, `prompt`, `n`, and optional `size`; accepts base64 entries in the `data` array |

The bundled provider authenticates with the credential referenced by its `apiKeyEnv` setting through the shared `ctx.credentials` service. Its endpoint and credential are read live, so a settings change reaches the next request without a restart. A provider that answers with an image URL rather than inline bytes is rejected; the provider does not fetch URLs.

## Failure behavior

Every failure is a typed `ImageGenerationError` with a code:

| Code | Meaning |
|---|---|
| `NO_PROVIDER` | No provider is registered under the requested route. |
| `MISSING_CREDENTIAL` | The bundled provider has no credential configured or stored. |
| `INVALID_REQUEST` | The request violates the request contract or the bundled provider has no endpoint. |
| `PROVIDER_FAILED` | The provider answered with a failure or an unusable body. |
| `ABORTED` | The caller aborted the request. |

A consumer reads the code to degrade: text-only fallback is the expected response to `NO_PROVIDER` or `MISSING_CREDENTIAL`, not a crash.

<!-- BEGIN GENERATED cordis-surface (gen-cordis-catalog.ts) — do not edit between markers -->

<a id="cordis-surface"></a>

## Cordis API

Generated from source by `scripts/gen-cordis-catalog.ts` (verified fresh by `pnpm run verify-cordis-catalog` in doc-sync; regenerate with `pnpm run gen-cordis-catalog`) — the language sides differ only in locale-specific paired document paths. Signature blocks use a `ts cordis-catalog` fence and keep the original source JSDoc; dispatch modes are defined in the [primer](../cordis-primer.md#dispatch-modes), and the framework-inherited `ctx` API lives in [cordis-api/inherited.md](../cordis-api/inherited.md).

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
