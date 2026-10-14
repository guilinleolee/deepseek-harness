# @deepseek-ai/dsh-client-ui-quant-research

English | [中文](README.zh.md)

The quant-research web panel plugin: a sidebar entry plus a frame-wide placeholder surface stating the plugin's research-only scope. Phase 1 ships the mount point and the disclaimer; the charts, the report cards, and the core package's Remote face arrive with phase 2. The node half is an empty apply so the plugin can appear in a host cordis.yml; everything user-visible lives in the browser half exported as `./client`.

## Installation

Installed together with the core plugin through the bundle patch:

```sh
dsh plugin --profile web add @deepseek-ai/dsh-quant-research
```

## Surface

- A `sidebar.footer.action` entry opens the panel from both sidebar states (wide row and rail icon).
- A `shell.overlay` surface renders the placeholder card: the research-only disclaimer, the no-live-trading statement, and what ships in later phases. Escape or the close button dismisses it.

Both registrations share one open/close controller and install for their declarations' lifetimes.

## Model Experience

### Placeholder panel

#### What the model sees

Nothing. The `sidebar.footer.action` entry and the `shell.overlay` surface are presentational; phase 1 adds no prompts, tools, or Remote reads.

#### Token effect

Zero direct tokens on every request.

#### KV Cache effect

Independent of live requests: the panel never touches a request prefix.

## Known Limitations and Deferred Work

- **Placeholder by design** — the real panel (kline/indicator/equity cards, backtest reports) lands with phase 2, together with the core package's Remote face and its locale dictionaries.
- **No locale dictionaries yet** — the placeholder copy is fixed Chinese; the locale namespace arrives with the real panel.
