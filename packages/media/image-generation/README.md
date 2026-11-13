---
description: "Provider-neutral image-generation capability: a registry behind one service plus the OpenAI-compatible provider."
kind: "package-reference"
---
# @deepseek-ai/dsh-image-generation

English | [中文](README.zh.md)

## Summary

Image generation as a capability seam: one `ctx.imageGeneration` service through which any consumer produces images, with a provider registry and one bundled provider speaking the OpenAI-compatible `POST {baseURL}/images/generations` wire shape.

## Table of Contents

- [Use this package](#use-this-package)
- [Providers](#providers)
- [Model Experience](#model-experience)
- [Known Limitations and Deferred Work](#known-limitations-and-deferred-work)
- [Dev Note](#dev-note)

-----

<a id="use-this-package"></a>
## Use this package

The [Content Studio bundle patch](../../client/ui-content-studio/README.md) mounts this package alongside its host gateways, so installing Content Studio delivers the service; other compositions mount it explicitly. The bundled provider ships unconfigured: a request before `baseURL` is set fails with `INVALID_REQUEST` naming the setting, and a request without the credential fails with `MISSING_CREDENTIAL`. Consumers call `ctx.imageGeneration.generate(request)` with a prompt and an optional provider route; the request's empty provider, model, and dimensions take the configured defaults before validation. Another provider registers through `ctx.imageGeneration.register()`.

The bundled provider authenticates with the credential referenced by `apiKeyEnv` through the shared `ctx.credentials` service, so the key never appears in the plugin's own storage. It reads `baseURL`, `apiKeyEnv`, and the defaults live, so a settings change reaches the next request without a restart.

<a id="providers"></a>
## Providers

| Provider route | Wire shape |
|---|---|
| `openai-compatible` (bundled) | `POST {baseURL}/images/generations` with `model`, `prompt`, `n`, and optional `size`; accepts base64 entries in the `data` array |

The bundled provider is one route for every hosted image model whose API speaks the same shape; the endpoint and credential select which service it reaches.

<a id="model-experience"></a>
## Model Experience

None, as the package returns image bytes to its consumers; nothing here reaches a model request through the LLM service.

#### KV Cache effect

None; this package neither assembles nor sends a provider request.

## Known Limitations and Deferred Work

- **No URL image fetch.** A provider that answers with an image URL rather than image bytes is rejected; only base64 images are accepted, because a URL fetch would silently widen the request to a second network hop outside the provider's credential scope.
- **No model-facing tool.** The service is the seam only; a consumer decides whether to expose image generation to a model.
- **Failures are typed for degradation, not for the end user.** `NO_PROVIDER`, `MISSING_CREDENTIAL`, `INVALID_REQUEST`, `PROVIDER_FAILED`, and `ABORTED` let a consumer choose a text-only fallback; the bundled provider also bounds the response size and the request deadline and reports the provider's HTTP status.

<a id="dev-note"></a>
### Dev Note

None.
