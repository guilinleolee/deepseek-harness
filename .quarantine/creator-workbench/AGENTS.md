# AGENTS.md — `@deepseek-ai/dsh-creator-workbench`

This package owns the Creator Workbench composition: the SOPs, the platform prompt templates, the quality-gate scripts, the export transforms, the Cordis overlay that wires them into a DSH session, the Python SDK glue in `creator_workbench/runner.py`, and the FastAPI entry in `creator_workbench/web/app.py`.

## Scope

- **In scope:** `cordis.yml` overlay; `sop/*.md`; `prompts/platforms/*.md`; `prompts/style/*.md`; `scripts/*.ps1` and `scripts/*.py`; the Cordis plugin in `src/index.ts`; the Python SDK glue in `creator_workbench/`; package tests.
- **Out of scope:** platform API publication; Tianlong Engine script execution; production-grade multi-tenant auth; per-platform OAuth token rotation.

## Boundaries

- **The SOP is the authoritative procedure.** Persona in `cordis.yml` only identifies the role. SOP edits never bind to `SESSION_FORMAT_VERSION=0`.
- **Tianlong Engine skills are read-only reference material.** The workbench never executes scripts under `dragon-engine/skills/...`; `dsh-skill-filesystem` exposes them as model-facing file content.
- **cordis.yml is a patch overlay.** It assumes `dsh-base` has already inserted the LLM adapter, base tools, persistence, approval, and sandbox rows. Same-id rows replace dsh-base defaults; new rows add workbench-only capabilities.
- **No API publication.** `scripts/export_content.ps1` writes copy-paste artifacts. The platform adapter pattern in the original proposal was replaced by deterministic transformations after most target platforms confirmed they offer no stable publication API.
- **scripts/illustrate.ps1 falls back.** The Tianlong Engine `shibazi-illustrator` ships with a `main()` gate that depends on `import.meta.url === file://${process.argv[1]}`. Some `npx bun` invocations on Windows break that equality, so the CLI exits 0 without running `main()`. The wrapper detects the empty output and falls back to a built-in HTML card so exports never block on art.

## Runtime environment

| Variable | Purpose |
|---|---|
| `DEEPSEEK_API_KEY` | Credential resolved by `dsh-llm-deepseek` |
| `DEEPSEEK_BASE_URL` | Override host endpoint |
| `CREATOR_WORKBENCH_CWD` | Bash + fs tools root (default: `process.cwd()`) |
| `CREATOR_WORKBENCH_SESSION_ROOT` | JSONL session directory (default: `./.sessions`) |
| `CREATOR_WORKBENCH_INPUT_DIR` | User material source (default: `D:\知识库\FDE\秉凌自媒体工作台\输入内容\`) |
| `CREATOR_WORKBENCH_OUTPUT_DIR` | Export target (default: `D:\知识库\FDE\秉凌自媒体工作台\输出内容\`) |
| `CREATOR_WORKBENCH_SKILLS_PATH` | Tianlong Engine skills root (default: `C:\Users\li\.claude\projects\dragon-engine\skills`) |

## Known Limitations and Deferred Work

- **OCR review pipeline not wired.** Stage 6 (analytics) expects the user to paste platform screenshots; tesseract-based extraction belongs to the next phase.
- **6 platforms only.** Adding a new platform requires a template under `prompts/platforms/<p>.md`, an entry in `scripts/run_gate.py` (structure spec), and entries in `scripts/export_content.ps1` (`sourceMap` + transform).
- **shibazi-illustrator CLI gate.** See Boundaries above.
- **`./invariant` declares no runtime invariant.** This package only contributes a single agent instruction; all workflow execution delegates to other packages' invariants.
- **PowerShell `[string]` parameter parsing on Windows.** `scripts/export_content.ps1` keeps `-Platforms` typed `[string]` because `[string[]]` parameters are dropped by `pwsh -File` invocations. The script normalizes comma, semicolon, whitespace, and pipe separators inline.
- **PowerShell variable-type inference caching.** `+=` on a hashtable value and `List<string>::Add()` on a string-typed variable have been observed to leave the variable typed `string` on this host. The export script works around it by using a fresh variable name and an explicit `foreach` loop.