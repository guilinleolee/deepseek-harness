---
description: "The web panel half of the customer-acquisition feature: a sidebar entry plus the frame-wide workbench surface."
kind: "package-bundle"
---
# @deepseek-ai/dsh-client-ui-customer-acquisition

English | [中文](README.zh.md)

## Summary

The web panel half of the customer-acquisition feature: a sidebar entry plus the frame-wide placeholder workbench surface. The Node half lives in [`@deepseek-ai/dsh-customer-acquisition`](../../growth/customer-acquisition/README.md); installing either package pulls both through its bundle patch.

## Table of Contents

- [Installation](#installation)
- [How it wires](#how-it-wires)
- [Model Experience](#model-experience)
- [Known Limitations and Deferred Work](#known-limitations-and-deferred-work)
- [Dev Note](#dev-note)

-----

## Installation

```sh
dsh plugin --profile web add @deepseek-ai/dsh-client-ui-customer-acquisition
```

Restart the profile: the sidebar footer gains the acquisition entry, and the workbench opens over `shell.overlay`.

## How it wires

The browser apply mounts the generated `./remote` contribution of `@deepseek-ai/dsh-customer-acquisition` through `ctx.remote.$mount()`, then registers both slots on a fiber that declares `remote.customerAcquisition` by its exact service name (a namespace service resolves only into fibers that list it). The entry and the surface share one open/close controller. Copy rides the standard locale seat under the `customer-acquisition` namespace.

## Model Experience

### Local acquisition panel

#### What the model sees

Nothing. This package registers no tool, prompt section, or model-facing context; it is a browser-side consumer of the Remote face.

#### Token effect

Zero.

#### KV Cache effect

Independent.

## Known Limitations and Deferred Work

- **Placeholder surface** — the workbench shows the global settings snapshot and the newest audit entries to prove the full P0 chain; the eight-page panel ships with P4.
- **No offline state** — reads fail visibly when the Remote gateway is unreachable; no browser-local caching by design (business data never lives in localStorage).

<a id="dev-note"></a>
### Dev Note

<details>
<summary>Working context for maintainers — click to expand</summary>

None.

</details>
