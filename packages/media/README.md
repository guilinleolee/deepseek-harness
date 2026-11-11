---
description: "Image-generation capability family: one provider-neutral service plus the OpenAI-compatible provider."
kind: "package-group"
---

# packages/media

English | [中文](README.zh.md)

## Summary

The media group owns the capabilities that produce non-text artifacts. It currently holds one package: the image-generation seam, through which any composition produces images behind a provider-neutral service, with one bundled provider speaking the OpenAI-compatible image wire shape.

## Table of Contents

- [Packages](#packages)
- [Related documentation](#related-documentation)
- [Dev Note](#dev-note)

-----

<a id="packages"></a>
## Packages

| Package | Role | ctx key |
|---|---|---|
| [`image-generation`](image-generation/README.md) | Provider-neutral image-generation registry plus the OpenAI-compatible provider | `ctx.imageGeneration` |

<a id="related-documentation"></a>
## Related documentation

- [Image generation subsystem](../../docs/subsystems/image-generation.md) — the request and result contract, the provider registry, and the bundled provider.

<a id="dev-note"></a>
## Dev Note

None.
