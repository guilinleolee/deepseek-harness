# quant-research 示例

English | [中文](README.md)

量化研究插件的可运行组合：存储（拒绝审计）、承载 Python 内核的 subprocess 能力、agent spine，以及带离线 `synthetic` 数据源的插件本体。`cordis.yml` 是真实用法基座（DeepSeek 适配器）；`cordis.snapshot.yml` 是其无钥快照对应物，换入脚本化的 `quant-mock` 适配器。

## 无钥快照

```sh
pnpm exec vitest run examples/quant-research --config vitest.snapshot.config.ts
```

场景驱动三轮真实工具调用——一次 K 线获取、一次双均线回测、一次红线拒绝——全部跑在真实组合上：内核子进程、synthetic 数据源、存储审计与合规门禁都是真的，只有模型是脚本化的。最终回答标记为 `QUANT_RESEARCH_SNAPSHOT_OK`。

## 真实运行

```sh
pnpm dsh --config examples/quant-research/cordis.yml "获取 000001 最近 60 根日线并做一次双均线模拟回测"
```

需要环境变量或根目录 `.env` 中提供 `DEEPSEEK_API_KEY`。所有输出仅供研究参考，均携带插件免责声明。
