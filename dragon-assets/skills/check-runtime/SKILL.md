---
name: check-runtime
description: >
  Check whether the local machine can actually run each dragon-assets capability
  path before quoting a delivery: probes the DeepSeek model/search/fetch endpoints,
  the muapi generation endpoint, and the browser and script runners. Use when
  preparing a quote, starting a client engagement, or when a run failed with an
  authentication or quota error. Reports each path as ok, auth, quota, cfg, net,
  or skip with the reason.
version: 1.0.0
license: MIT
commercial_use: yes
triggers: ["check runtime", "运行时体检", "环境检查", "能不能跑", "依赖体检"]
---

# check-runtime · 运行时依赖体检

报价或交付之前，先跑一次。每条能力路径给出明确结论与原因。

## 用法

```bash
python check-runtime.py            # 检查全部路径
python check-runtime.py --json     # 机器可读输出
python check-runtime.py --only deepseek,mupapi
```

## 结论含义

| 结论 | 含义 | 处理 |
|---|---|---|
| `ok` | 配置正确且可达 | — |
| `auth` | 凭据被拒或缺失（401/403） | 换 key 或配 key |
| `quota` | 余额或配额不足（402） | 充值 |
| `cfg` | 配置或端点错误（400/404） | 改 base URL 或换端点 |
| `net` | 网络不可达 | 检查出网策略 |
| `skip` | 该路径不适用 | 不在本次交付范围 |

## 检查项

| 名称 | 检查什么 | 前置条件 |
|---|---|---|
| `deepseek` | Messages / Search / Fetch 三个端点 | `DEEPSEEK_API_KEY` |
| `mupai` | `/v1/images/generations` | `MUAPI_API_KEY` |
| `browser` | 系统 Chrome / Chromium | 用于 `render-deck` 与 CDP 发布器 |
| `runner` | `bun` 或 `npx` | 用于 CDP 发布器 |
| `anysearch` | 是否配置了可选 key | 匿名低配额也可跑 |

## 已知的本机基线（2026-10-26）

- `DEEPSEEK_BASE_URL` 必须以 `/anthropic` 结尾（harness 用 Anthropic 兼容端点）。
  写成 `https://api.deepseek.com` 会 404。
- `MUAPI_API_KEY` 无效时返回 `Invalid API key`。
- `muapi` 的模型列表端点 `/v1/models` 是公开的，**永远返回 200，不验证 key**，
  不能用它判断 key 是否有效；必须打生成端点。

## 授权

MIT，随仓库分发。
