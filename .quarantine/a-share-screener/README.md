# dsh-a-share-screener

A-share quant screener DSH plugin. Function plugin: `name`/`inject`/`Config`/`apply`, no default export.

## What it provides

- One model-facing tool, `a_share_screen`, registered through `ctx.tools.register(defineTool(...))`.
- One skill, `stock-screener`, registered through `ctx.skills.register(...)`.
- One local SQLite cache for daily bars (`better-sqlite3`).
- One Tushare Pro provider with an Eastmoney fallback, token resolved per call through `ctx.credentials`.

## Configuration

`cordis.yml` row:

```yaml
- id: a-share-screener
  name: '@deepseek-ai/dsh-a-share-screener'
  config:
    cacheRoot: !!js "process.env.DSH_A_SHARE_CACHE_ROOT ?? './.cache/a-share-screener'"
    defaultLimit: 30
    defaultUniverse: { kind: 'hot', size: 500 }
    jobOutputLimitBytes: 524288
```

## Required services

`inject` declares `tools`, `skills`, `credentials`, `jobs`. The example at
[`examples/a-share-screener/cordis.yml`](../../../examples/a-share-screener/cordis.yml)
loads them.

## Credentials

Set the Tushare token once through the credentials seam:

```sh
dsh credentials set TUSHARE_TOKEN <your-token>
```

The plugin refuses to start without it; calls surface a typed error rather
than silently degrading.

## Model experience

The plugin adds roughly 350 tokens of skill text and one tool schema to the
system prompt. The tool returns a `{ kind: 'background', jobId }` handle —
the canonical pattern for long-running work documented in
`docs/cookbook/adding-a-tool.md`. The model polls `ctx.jobs.read(jobId)`
until terminal, then summarizes the `matchedFilters` + `evidence` fields.

## Known limitations and deferred work

- `value-play` is deferred to a follow-up release; the registry leaves the id
  reserved.
- The skill prompt is English-only; bilingual coverage waits for the prompt
  to freeze.
- Eastmoney fallback returns an empty stock-list today; the screen tool
  still works on cached rows when the primary fails to refresh.
