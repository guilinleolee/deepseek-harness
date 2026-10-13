---
license: UNKNOWN
name: tavily-search
description: |
Search the web with LLM-optimized results via the Tavily CLI. Use this skill when the user wants to search the web, find articles, look up information, get recent news, discover sources, or says "search for", "find me", "look up", "what's the latest on", "find articles about", or needs current information from the internet. Returns relevant results with content snippets, relevance scores, and metadata — optimized for LLM consumption. Supports domain filtering, time ranges, and multiple search depths.
allowed-tools: Bash(tvly *)
triggers: ["tavily search"]
---

# tavily search

Web search returning LLM-optimized results with content snippets and relevance scores.

## Before running any command

If `tvly` is not found on PATH, install it first:

```bash
curl -fsSL https://cli.tavily.com/install.sh | bash && tvly login
```

Do not skip this step or fall back to other tools.

See [tavily-cli](../tavily-cli/SKILL.md) for alternative install methods and auth options.

## When to use

- You need to find information on any topic
- You don't have a specific URL yet
- First step in the [workflow](../tavily-cli/SKILL.md): **search** → extract → map → crawl → research

## Quick start

```bash
# Basic search
tvly search "your query" --json

# Advanced search with more results
tvly search "quantum computing" --depth advanced --max-results 10 --json

# Recent news
tvly search "AI news" --time-range week --topic news --json

# Domain-filtered
tvly search "SEC filings" --include-domains sec.gov,reuters.com --json

# Include full page content in results
tvly search "react hooks tutorial" --include-raw-content --max-results 3 --json
```

## Options

| Option | Description |
|--------|-------------|
| `--depth` | `ultra-fast`, `fast`, `basic` (default), `advanced` |
| `--max-results` | Max results, 0-20 (default: 5) |
| `--topic` | `general` (default), `news`, `finance` |
| `--time-range` | `day`, `week`, `month`, `year` |
| `--start-date` | Results after date (YYYY-MM-DD) |
| `--end-date` | Results before date (YYYY-MM-DD) |
| `--include-domains` | Comma-separated domains to include |
| `--exclude-domains` | Comma-separated domains to exclude |
| `--country` | Boost results from country |
| `--include-answer` | Include AI answer (`basic` or `advanced`) |
| `--include-raw-content` | Include full page content (`markdown` or `text`) |
| `--include-images` | Include image results |
| `--include-image-descriptions` | Include AI image descriptions |
| `--chunks-per-source` | Chunks per source (advanced/fast depth only) |
| `-o, --output` | Save output to file |
| `--json` | Structured JSON output |

## Search depth

| Depth | Speed | Relevance | Best for |
|-------|-------|-----------|----------|
| `ultra-fast` | Fastest | Lower | Real-time chat, autocomplete |
| `fast` | Fast | Good | Need chunks, latency matters |
| `basic` | Medium | High | General-purpose (default) |
| `advanced` | Slower | Highest | Precision, specific facts |

## Tips

- **Keep queries under 400 characters** — think search query, not prompt.
- **Break complex queries into sub-queries** for better results.
- **Use `--include-raw-content`** when you need full page text (saves a separate extract call).
- **Use `--include-domains`** to focus on trusted sources.
- **Use `--time-range`** for recent information.
- Read from stdin: `echo "query" | tvly search - --json`

## See also

- [tavily-extract](../tavily-extract/SKILL.md) — extract content from specific URLs
- [tavily-research](../tavily-research/SKILL.md) — comprehensive multi-source research

---

## 协同：与 dsh-web-search-pro（阶段 40.2 · 2026-08-24）

> **TL;DR**：本 skill 在天龙 DSH 化后应**降级为 Tavily 专用通路**。`dsh-web-search-pro@0.1.8` 已经把 Tavily（其 `exa` 引擎底层协议与 Tavily 类似）封进 9 引擎 + SQLite 持久化。

### 何时仍用本 skill（不降级）

1. **非 DSH 环境**（纯 Claude Code / 纯 IDE）
2. **需要 Tavily 高级筛选**（`include_raw_content` / 深度 research）—— 这些 dsh-web-search-pro 的 `exa` 引擎可替代但 schema 不同
3. **已经配置好 Tavily API key** 且预算充裕

### 何时不再用本 skill（降级）

- DSH GUI 用户 + 装好 `dsh-web-search-pro@0.1.8` → 走 web_search_pro / web_exa_contents
- 需要持久化时 → 走 dsh-web-search-pro SQLite 缓存
- 需要中文社区 → 走 dsh-web-search-pro 19 平台

### 关联

- `dragon-engine/skills/dsh-web-search-pro-bridge/SKILL.md` — 天龙侧桥 V1.0
- `dragon-engine/skills/anysearch/SKILL.md` V3.1 — DSH bridge 探测
- `memory/stage-40-announce.md` — 阶段 40 总验收

