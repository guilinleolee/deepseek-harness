# @deepseek-ai/dsh-customer-acquisition-geo

English | [中文](README.zh.md)

GEO (generative-engine optimization) website diagnosis — module 1 of the customer-acquisition feature. Scans the site the user explicitly provides through a bounded serial crawler, analyzes AI-search visibility deterministically (llms.txt / robots.txt / sitemap presence, brand/product/FAQ/case content, structure and freshness), and produces a 0-100 score, a Markdown report, a deployable `llms.txt`, knowledge material, and an optimization checklist. One-way dependent on the main [`@deepseek-ai/dsh-customer-acquisition`](../customer-acquisition/README.md) package's frozen storage domain and audit trail; the main package never depends on this one.

## Installation

```sh
dsh plugin --profile web add @deepseek-ai/dsh-customer-acquisition-geo
```

The bundle patch inserts both rows — the main plugin (if absent) and this module. Restart the profile to load them.

## Compliance boundary (red line 1)

One `tools/pre-execute` gate plus the crawler enforce the fetch red lines regardless of what the parameter schema accepts: only an http(s) URL explicitly provided in the call; serial fetching (concurrency 1); per-page timeout ≤ 10 s; response body ≤ 2 MiB; at most 20 pages per scan (hard constant and settings cap); `robots.txt` checked before every fetch with `Disallow` paths skipped and recorded in the report; no cross-domain discovery; no phone/email harvesting. Each rule has an illegal-path unit test.

## Tools

| name | what it does |
|---|---|
| `customer_acquisition_geo_scan` | Run one bounded diagnosis: score, findings, `llms.txt`, material, checklist, full Markdown report. |
| `customer_acquisition_geo_history` | Paged scan history, newest first, filterable by URL prefix and time window. |
| `customer_acquisition_geo_report_get` | One report in full: findings, artifacts, skipped paths, report text. |
| `customer_acquisition_geo_compare` | Two reports from the same site: score delta, resolved vs introduced findings, summary. |

## Model Experience

### Local GEO state

#### What the model sees

Four tools joined to prompt assembly while the plugin loads; the scan render is the full Markdown report, history renders one line per scan, compare renders its summary. Scan timeouts surface as friendly Chinese tool errors.

#### Token effect

Bounded: four tool schemas (~700 tokens) in every assembled request while the plugin is loaded; report renders scale with finding count.

#### KV Cache effect

The schemas join the tool block of the prompt prefix; loading or unloading the plugin invalidates the reusable prefix from that point, as any tool registration does.

## Known Limitations and Deferred Work

- **The analyzer is deterministic, not model-based** — findings come from structural and content heuristics; an LLM-judged content-quality pass can join later behind the same service interface.
- **Site coverage is bounded by the scan** — pages beyond `max_pages`, JS-rendered content, and subdomains outside the start origin are out of scope by design.
- **Reports persist in the shared domain** — retention follows the main plugin's audit-retention stance (unbounded until a deployment requirement lands).
