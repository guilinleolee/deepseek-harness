# quant-research example

English | [中文](README.zh.md)

A runnable composition for the quant-research plugin: storage (denial audit), the subprocess capability for the Python kernel, the declarative agent loop, and the plugin with the offline `synthetic` data source. `cordis.yml` is the real-use base (DeepSeek adapter); `cordis.snapshot.yml` is its keyless counterpart that swaps in the scripted `quant-mock` adapter.

## Keyless snapshot

```sh
pnpm exec vitest run examples/quant-research --config vitest.expected.config.ts
```

The scenario drives three real tool rounds — a kline fetch, an SMA-cross backtest, and a red-line denial — through the assembled composition: the kernel subprocess, the synthetic source, the storage audit, and the compliance gate are all real; only the model is scripted. The final answer marker is `QUANT_RESEARCH_SNAPSHOT_OK`. The driver then runs the background-job stages through the same composition: parameter optimization, walk-forward validation, and the cross-sectional IC over a two-symbol panel (`ic_windows` included), each collected through `job_output` with one compliance denial; a `quant_list_snapshots` read closes the loop over the persisted results.

## Real run

```sh
pnpm dsh --config examples/quant-research/cordis.yml "获取 000001 最近 60 根日线并做一次双均线模拟回测"
```

Needs `DEEPSEEK_API_KEY` in the environment or the root `.env`. All outputs are research-only and carry the plugin's disclaimer.
