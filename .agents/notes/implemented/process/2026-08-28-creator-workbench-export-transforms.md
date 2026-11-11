# Agent Note: Creator Workbench's `export_content.ps1` ships deterministic per-platform transforms with a shibazi-illustrator fallback

Status: implemented

English | [中文](2026-08-28-creator-workbench-export-transforms.zh.md)

## Problem

The Creator Workbench's stage-5 export must turn a single Markdown draft under `.work/<task_id>/drafts/<topic_id>/` into copy-paste artifacts for every target platform, and the artifacts must respect each platform's structural conventions (wechat length, xiaohongshu image count and tag block, douyin shot timing, toutiao single-paragraph style, zhihu reference-block separation, bilibili shot+subtitle+voiceover breakdown). The draft body is one canonical Markdown, but the platform-side structure is genuinely per-platform; one universal template that ignores the differences yields unusable output, and shipping six independent CLI scripts multiplies the surface area to maintain.

A second problem is the host's `bash` parameter parsing on Windows. PowerShell's `[string[]]` typed parameters are dropped by `pwsh -File` invocations, so the call `-Platforms @('a','b')` arrives at the script as a single string. A pipeline that uses `.Split()` on the value and pipes the result into `ForEach-Object` then sees the array collapsed back to a single string on the next pipeline boundary, which means a clean `for ($i in $array) { ... }` loop is not enough; the variable holding the array must be a fresh name with no previous string-typed assignment, and the split must happen on a `[System.StringSplitOptions]` enum value rather than the default overload.

## Decision

The export lives in `scripts/export_content.ps1` and uses a single `$transforms` hashtable keyed by platform name, with each entry a PowerShell script-block (`wechat`, `xiaohongshu`, `douyin`, `toutiao`, `zhihu`, `bilibili`). The main loop dispatches per platform and collects the result into a per-platform `result`, a per-error `errors_list` (`List[object]`), and a per-platform `platformOutputs` (`List[object]`); all three are typed as `System.Collections.Generic.List[object]` because hashtable property mutations through `+=` on the previous-name string binding silently leave the variable typed `string` on this PowerShell host. The manifest is written last as one JSON object whose `platforms` field references `platformOutputs.ToArray()`.

Each transform reads the same source Markdown but extracts a platform-specific subset:

- **wechat** — emit `wechat-richtext.html` with `<section>` wrapping, H1/H2 styled, `<blockquote>` for `>` lines, `<li>` for `- ` lines, `<p>[图片位 N]</p>` for `<插入点 N>` placeholders. Calls `illustrate.ps1` to fill `wechat-images/` with one HTML card per placeholder; embeds `<img src="wechat-images/...html" />` in the richtext when a card exists.
- **xiaohongshu** — extract title (first H1), cover line (`> 封面文案：...`), tag block (`## 标签` ... until next H2), and the body between `## 正文` and the next H2. Write `xhs-text.txt` plus `xhs-source.md` and create an empty `xhs-images/` for the user to drop generated images.
- **douyin / toutiao / zhihu / bilibili** — pure Markdown reshape: keep the body verbatim (douyin, bilibili), strip down to a single paragraph (toutiao), separate references from body (zhihu), or annotate the shot/subtitle/voiceover markers (bilibili).

The `-Platforms` parameter is typed `[string]` and normalizes comma, semicolon, whitespace, and pipe separators inline. The split is `[regex]::Split($normalized, ',')` and the result is iterated with an explicit `foreach` loop into a fresh `$plist` variable (`List[string]`); the main loop binds to `$plist`, not the previous `$platforms`, because the previous binding still carries the string-typed inference. The script fails loud at load time when an unknown platform is requested (`unknown_platform` in `export_errors.json`) and never aborts the run on a single-platform failure.

`scripts/illustrate.ps1` is the second seam. It tries the Tianlong Engine `shibazi-illustrator/scripts/html-export.ts` first (HTML engine, no API key needed), and on detection of empty output (the shibazi CLI exits 0 but `main()` does not run on Windows because `import.meta.url !== file://${process.argv[1]}` under some `npx bun` invocations), it falls back to a built-in HTML card template (`kabager` / `minimal` / `dramatic` style, 1200×512). The detection is "did shibazi actually write a file under `$OutputDir`?" — `exit 0` is not sufficient on its own. The fallback uses theme tokens (`--dsw-bg-1`, `--dsw-fg-1`, `--dsw-accent`) so the card inherits the dsh-web surface styling.

## Alternatives considered

**One template per platform driven by a templating engine (Handlebars, Liquid).** Brings in a parser, a render pipeline, and a new config DSL. Rejected because each platform's transform is a deterministic one-pass reshape of one Markdown file with at most a `replace` and a `substring`; a 30-line script-block per platform is easier to read than a 5-template-by-platform setup, and the power of a templating engine is wasted when every template is a single fixed structure with no branching.

**A unified YAML/JSON manifest per platform (`config.yaml → wechat.yaml`, `zhihu.yaml`, ...).** Cleaner separation of structure from code. Rejected because (a) the transforms are not data — they are control flow over a parsed Markdown tree, and (b) loading a YAML parser (`js-yaml` or PowerShell-yaml) into a script that otherwise has zero runtime dependencies is a cost the workbench does not need. The transform code is the spec.

**Treat shibazi-illustrator's "exit 0 with no output" as a fatal error and surface the bug upstream to the Tianlong Engine maintainer.** Correct long-term behavior, wrong near-term UX: every user on Windows who runs the export gets a broken wechat-richtext until a fix ships. The fallback HTML card is good enough to demonstrate the export pipeline works, and the Tianlong-side fix is queued separately as a follow-up.

## Consequences

Three consequences. First, the export is reproducible and offline: a single `.work/<task_id>/drafts/<topic_id>/wechat-script.md` produces the same `wechat-richtext.html`, `wechat-source.md`, and `wechat-images/*-poster.html` on every run, and a re-run with a fixed draft does not depend on network, on the shibazi service, or on a model call. The CI keyless smoke is therefore a deterministic file diff, not a model-output comparison. Second, the export manifest is the single source of truth for "what shipped": every platform's `output_dir`, every file the platform produced, and every per-platform error land in `export_manifest.json` (and `export_errors.json` when applicable). A creator who needs to re-publish six months later can `cd` into the manifest's `output_dir` and copy each artifact back into the platform editor without re-running the model.

The real cost is shibazi-fallback's visual quality. The built-in card uses theme tokens and a 4px accent bar with a 38px title, which is good enough to publish but does not match the visual polish of a hand-tuned shibazi export. Production wiring will swap the fallback for a hand-curated set of three style presets per platform once the shibazi CLI gate is fixed upstream, and the `kabager` / `minimal` / `dramatic` enum stays stable across the change. The other cost is the PowerShell quirk surface: the `[string]` typing, the `List[object]` casting, and the explicit `foreach` loop are three independent quirks that future contributors will not see in any other script in the workbench, so the script carries an inline comment in each spot explaining why.
