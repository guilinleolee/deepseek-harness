# `@deepseek-ai/dsh-creator-workbench`

English | [中文](README.zh.md)

Self-media Creator Workbench — a DSH-native composition that turns the agent spine into a topic-to-publish factory. Driven by an authoritative SOP, six platform prompt templates, five quality gates, and a copy-paste export pipeline that reads the Tianlong Engine skills on disk as reference material.

## What it ships

| Path | Purpose |
|---|---|
| `cordis.yml` | Patch overlay loaded on top of `dsh-base` via `--patch`. |
| `sop/creator-workflow.md` | Authoritative 6-phase procedure (scout → plan → write → gate → export → review). |
| `sop/gate-{grammar,factual,compliance,tone,structure}.md` | One SOP per quality gate. |
| `prompts/platforms/{wechat,xiaohongshu,douyin,toutiao,zhihu,bilibili}.md` | Platform style templates. |
| `prompts/style/style-dna.md` | Brand DNA (mirrors `lib-bingling-v2` on the Tianlong Engine). |
| `scripts/scan_inputs.ps1` | Stage 1 input inventory. |
| `scripts/run_gate.py` | Mechanical gate runner (grammar / structure / compliance) plus claim extractors (factual / tone). |
| `scripts/illustrate.ps1` | Calls the Tianlong Engine `shibazi-illustrator` HTML engine; falls back to a built-in card when unavailable. |
| `scripts/export_content.ps1` | Stage 5 multi-platform export. |
| `src/index.ts` | Cordis plugin (named export). Registers one model-visible instruction pointing at the SOP. |

## Quick start

```sh
# 1. Install workspace deps (only needed once per repo).
pnpm install

# 2. Run the package's own vitest suite.
pnpm exec vitest run packages/creator-workbench/tests

# 3. Launch a Web session with the workbench overlay applied.
#    (Currently broken on Windows due to a dsh-base loader issue — see
#    "Known Limitations" below. The CLI workflow is the recommended
#    path today.)
# pnpm dsh web --patch "$PWD/cordis.yml"

# 3'. Recommended today: the CLI workflow. See "CLI workflow" below.

## Configuration

| Variable | Purpose | Default |
|---|---|---|
| `DEEPSEEK_API_KEY` | LLM credential resolved by `dsh-llm-deepseek`. | — |
| `DEEPSEEK_BASE_URL` | Override the chat endpoint. | — |
| `CREATOR_WORKBENCH_CWD` | Bash + fs tools root. | `process.cwd()` |
| `CREATOR_WORKBENCH_INPUT_DIR` | User material source. | `D:\知识库\FDE\秉凌自媒体工作台\输入内容\` |
| `CREATOR_WORKBENCH_OUTPUT_DIR` | Export target. | `D:\知识库\FDE\秉凌自媒体工作台\输出内容\` |
| `CREATOR_WORKBENCH_SKILLS_PATH` | Tianlong Engine skills root. | `C:\Users\li\.claude\projects\dragon-engine\skills` |
| `CREATOR_WORKBENCH_SESSION_ROOT` | JSONL session directory. | `./.sessions` |

## Model Experience

The persona in `cordis.yml` identifies the role only; the procedure lives in `sop/creator-workflow.md` and is loaded through the fs tool by the agent. Editing the SOP does not bind to `SESSION_FORMAT_VERSION=0`.

The agent's prompt includes:
- The static persona block (KV-cache-stable).
- A single short `agent-instructions` block pointing at the SOP, prompts, and scripts. The instruction body is small so it does not invalidate the cache across turns.
- Whatever the platform prompt template injects for the active stage.

#### KV Cache effect

None directly: the persona and instruction are static; SOP content is read through the fs tool and never enters the system prefix.

## Boundaries

- **No API publication.** The workbench exports copy-paste artifacts. Most target platforms do not offer stable, quota-bearing publication APIs.
- **Tianlong Engine is read-only.** The workbench never executes scripts under `dragon-engine/skills/...`; it loads them as model-facing reference material through `dsh-skill-filesystem`.
- **Persona does not encode steps.** Procedural detail stays in the SOP so edits decouple from the session log format.
- **Composition is a patch, not a full root.** The overlay assumes dsh-base has already inserted the LLM adapter, tools, persistence, approval, and sandbox rows.

## Known Limitations and Deferred Work

- **`dsh web --patch` launch is currently broken on Windows.** A dsh-base loader collision between `bash-sandbox` and `pwsh-sandbox` (both register the `shell` service) prevents the overlay from booting through `pnpm dsh web`. This is a dsh-base issue, not a workbench issue; the patch overlay is structurally correct and the unit / e2e tests pass. Until the upstream fix lands, the recommended workflow is the **CLI workflow** below.
- **OCR review pipeline not wired.** Stage 6 (analytics) currently expects the user to paste platform screenshots; tesseract-based extraction belongs to the next phase.
- **6 platforms only.** `wechat / xiaohongshu / douyin / toutiao / zhihu / bilibili` ship defaults. New platforms require a template under `prompts/platforms/<p>.md` plus an entry in `scripts/run_gate.py` (structure spec) and `scripts/export_content.ps1` (`sourceMap` + transform).
- **shibazi-illustrator CLI gate.** The Tianlong Engine's `shibazi-illustrator/scripts/html-export.ts` exits 0 without running `main()` under some `npx bun` invocations on Windows. `scripts/illustrate.ps1` detects the empty output and falls back to a built-in HTML card, so exports never block on art.
- **`./invariant` declares no runtime invariant.** This package only contributes a single agent instruction; all workflow execution delegates to other packages' invariants.

## CLI workflow (recommended today)

While the dsh-web launch issue is fixed upstream, the workbench delivers its full value through the CLI scripts alone — **no DSH runtime required, no LLM key required**. The e2e smoke (`tests/e2e_export.py`) drives every script in this path and asserts the artifacts.

```sh
# 1. Pick a task id (any short slug) and a topic id (also short)
export TASK_ID="work-001"
export TOPIC_ID="topic-001"

# 2. Create the draft directory under your work root
export WORK_ROOT="D:\知识库\FDE\秉凌自媒体工作台\工作区"
export DRAFT_DIR="$WORK_ROOT\.work\$TASK_ID\drafts\$TOPIC_ID"
mkdir -p "$DRAFT_DIR"

# 3. Write the wechat draft (Markdown) by hand
code "$DRAFT_DIR\wechat-script.md"

# 4. Run the deterministic quality gates (mechanical checks)
python "$PWD/scripts/run_gate.py" grammar   --draft "$DRAFT_DIR\wechat-script.md" --platform wechat
python "$PWD/scripts/run_gate.py" structure --draft "$DRAFT_DIR\wechat-script.md" --platform wechat
python "$PWD/scripts/run_gate.py" compliance --draft "$DRAFT_DIR\wechat-script.md" --platform wechat

# 5. Copy + reshape to the other platforms (modify headings / length per template)
# OR: let an external model (your MINIMAX M3, Claude, etc.) rewrite per-platform

# 6. Export every platform at once
$env:CREATOR_WORKBENCH_SKILLS_PATH = "C:\Users\li\.claude\projects\dragon-engine\skills"
pwsh -NoProfile -File "$PWD/scripts/export_content.ps1" `
  -TaskId "$TASK_ID" -TopicId "$TOPIC_ID" `
  -Platforms "wechat,xiaohongshu,douyin,toutiao,zhihu,bilibili" `
  -WorkRoot "$WORK_ROOT" `
  -OutputDir "D:\知识库\FDE\秉凌自媒体工作台\输出内容"

# 7. End-to-end CI smoke (no key needed)
python "$PWD/tests/e2e_export.py"
```

The full output lands under `$OutputDir/<platform>/<date>/<task>-<topic>/` plus an `export_manifest.json` summarising every platform's files and any `export_errors.json` failures. The wechat column additionally emits `wechat-images/<basename>-poster.html` from the shibazi-illustrator pipeline (or its built-in fallback).

## Relationship to `examples/creator-workbench`

The `examples/creator-workbench` example composition is the throwaway PoC this package was extracted from. The package owns the canonical SOPs, prompts, scripts, and cordis overlay; the example keeps the Python SDK glue (`creator_workbench/runner.py`, FastAPI entry) and its dedicated smokes. Both share the same authoritative SOP file path.