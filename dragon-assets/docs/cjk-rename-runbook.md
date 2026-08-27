# CJK Filename Rename Runbook

Generated: 2026-08-19 01:22
Repo: `/home/runner/work/dragon-engine/dragon-engine`
Corrupted count: **0**

## Why

These filenames were stored with GBK bytes interpreted as UTF-8
(`璋冪爺甯` style). Original characters are NOT algorithmically
recoverable from the bytes — recover is LOSSY.

The first 1-2 codepoints of each corrupted name are recognizable:
common patterns below:

| Source codepoints | Likely original | Confidence |
|-------------------|-----------------|------------|
| `璋冪爺甯`        | `调研师`         | HIGH (x12) |
| `鏋舵瀯甯`        | `架构师`         | HIGH (x4)  |
| `鏋勫缓甯`        | `建模师`         | HIGH (x2)  |
| `楠岃瘉甯`        | `验证师`         | HIGH (x6)  |
| `瀹夊叏甯`        | `安全师`         | HIGH (x4)  |
| `瀹℃煡甯`        | `审查师`         | HIGH (x4)  |
| `璁板綍甯`        | `记录师`         | HIGH (x4)  |
| `鍙戝竷甯`        | `发布师`         | HIGH (x4)  |
| `浣跨敤璇存槑`    | `使用说明`       | HIGH (x3)  |
| `浣跨敤鎸囧崡`    | `使用指南`       | HIGH (x1)  |
| `鐢靛晢杩愯惀`    | `电商运营`       | HIGH (x1)  |
| `杞...婕忔枟...妯℃澘` | `...婕忔枟...模板` | LOW (x1) |
| `MVP楠岃瘉...`   | `MVP验证...`     | HIGH (x1)  |
| `涓夌幆瀹氫綅绀轰緥` | `三环定位范例` | HIGH (x1)  |

## Runbook (manual `git mv`)

Open **Windows cmd** (not bash — bash mojibake hides original codepoints).
cd to repo root. For each line below, decide the target name,
then run:

```cmd
git mv "<source>" "<target>"
```

After all moves: `git status` should show renames; `git diff --cached --stat`
should list 100% renames (not delete+add) to preserve history.

### Files to rename

| # | Current path (from disk) | Suggested target | Type |
|---|--------------------------|------------------|------|

## After rename

```bash
python scripts/build-index.py --include-library
python tests/test_index.py
python scripts/check-cjk-filenames.py   # should report 0
```
