# STATUS

_generated: 2026-08-19 01:22:22_
_repo: `/home/runner/work/dragon-engine/dragon-engine`_

---

## 1. Five-asset index

- **schema**: `dragon-index/1.0`
- **total**: 1180

| kind | count | jsonl |
|------|-------|-------|
| skill | 799 | `SKILLS.jsonl` |
| agent | 147 | `AGENTS.jsonl` |
| hook | 87 | `HOOKS.jsonl` |
| command | 142 | `COMMANDS.jsonl` |
| plugin | 5 | `PLUGINS.jsonl` |

---

## 2. Data quality (skill-admin)

| class | count | threshold |
|-------|-------|-----------|
| A: license unknown | 0 | < 800 |
| B: triggers missing | 137 | < 600 |
| C: AGPL no NOTICE | 0 | == 0 |
| D: size / pycache | 0 | == 0 |
| E: stale (pre-2026) | 0 | < 100 |
| **TOTAL ISSUES** | **137** | |

---

## 3. Filename mojibake (CJK GBK-misread)

**[OK]** 0 corrupted filenames.

---

## 4. Health checklist (run these weekly)

```bash
python scripts/build-index.py --include-library
python tests/test_index.py
python scripts/skill-admin.py
python scripts/check-cjk-filenames.py --emit-runbook docs/cjk-rename-runbook.md
python scripts/gen-status-md.py
```

CI equivalent: `.github/workflows/index-sync.yml` runs steps 1-5
on every push to master/main and weekly on Sunday 03:00 UTC.
