# @deepseek-ai/dsh-client-ui-quant-research

English | [中文](README.zh.md)

The quant-research web panel plugin: a sidebar entry plus a frame-wide surface with read-only views of the PET virtual accounts and the research notes, fed by the core package's Remote face mounted through this plugin itself (`ctx.remote.$mount`). Charts render as inline SVG (`charts.tsx` — a position-weight bar row and a sparkline); there is no chart-library dependency. The node half is an empty apply so the plugin can appear in a host cordis.yml; everything user-visible lives in the browser half exported as `./client`.

## Installation

Installed together with the core plugin through the bundle patch:

```sh
dsh plugin --profile web add @deepseek-ai/dsh-quant-research
```

## Surface

- A `sidebar.footer.action` entry opens the panel from both sidebar states (wide row and rail icon).
- A `shell.overlay` surface renders:
  - **Virtual accounts** — one card per account (name, cash, equity) with an inline-SVG bar row of the position weights; expanding a card refetches the full state through `getAccountState` and shows the position count.
  - **Research notes** — the newest-first list (title, symbol, date) read from the `research_notes` table.

Both registrations share one open/close controller and install for their declarations' lifetimes. The plugin mounts the core package's Remote contribution before registering the slots and registers the `quant-research` locale namespace (zh/en) for its copy.

## Model Experience

### Research panel

#### What the model sees

Nothing. The `sidebar.footer.action` entry and the `shell.overlay` surface are presentational; the panel adds no prompts, tools, or request-prefix content.

#### Token effect

Zero direct tokens on every request.

#### KV Cache effect

Independent of live requests: the panel never touches a request prefix.

## Known Limitations and Deferred Work

- **Read-only by design** — every mutation (account creation, rebalance, note saving) goes through the model-facing tools with their own compliance and approval flows; the Remote face exposes reads only, so the panel cannot bypass the gate.
- **No equity-curve cards yet** — the durable domain stores accounts, orders, and notes but no equity history, so the panel renders position weights rather than performance curves; equity cards wait for a session-to-storage results channel.
- **Panel charts are static SVG** — the bar row and sparkline have no tooltips or zoom; interactive charts stay an explicit review item against bundle size.
