---
description: "The Content Studio web workbench: a browser plugin whose left nav renders the sentiment, benchmark, topic-bank, create, publish, review, interaction, accounts, persona, and template surfaces over the content-outputs Remotes."
kind: "package-bundle"
---

# @deepseek-ai/dsh-client-ui-content-studio

English | [中文](README.zh.md)

## Summary

Content Studio is the web workbench for the content-creation domain: one install adds a sidebar entry that opens a frame-wide surface whose left nav renders the workbench home, sentiment, competitors, topic bank, create, publish, review, interaction, accounts, persona, and template views, all reading and writing the outputs library through the plugin's self-mounted `contentOutputs` / `contentSchedule` / `contentTopics` Remotes. The shipped web profile already includes it; install it into any other DSH web profile with one command. Picking a capability copies a structured instruction template (【…】 fill-in markers) to the clipboard — the paste-into-session hop is the user's one action because no composer-draft seam exists yet.

## Table of Contents

- [Use this package](#use-this-package)
- [Understand the implementation](#understand-the-implementation)
- [Further Exploration](#further-exploration)
- [Model Experience](#model-experience)
- [Known Limitations and Deferred Work](#known-limitations-and-deferred-work)
- [Dev Note](#dev-note)

-----

<a id="use-this-package"></a>
## Use this package

Content Studio plugin: the sidebar entry plus the frame-wide creation workbench surface. The entry fills the sidebar shell's `sidebar.footer.action` hole (labeled row while the column is wide, icon on the rail), and the workbench fills the frame's additive `shell.overlay` hole, so both registrations are additive chrome — nothing shipped is replaced.

Install into any DSH web profile with one command: `dsh plugin --profile web add @deepseek-ai/dsh-client-ui-content-studio` — the package declares `dsh.bundle.patch`, whose insert list brings its two host Remote gateways (`content-outputs`, `content-schedule`) along, so nothing else is manual.

The plugin is a **self-contained Remote assembly**: `apply` mounts its own host contributions (`contentOutputs`, `contentSchedule`) through `ctx.remote.$mount()` — the pattern api-remotes established — so the browser bundle carries its whole server face and no in-tree BFF assembly needs to know this plugin exists.

The workbench surface renders its views from one left nav — workbench home, sentiment, competitors, topic bank, create, publish, review, interaction, accounts, persona, and templates. **Create** is the dual-intent capability menu: the finished-artifact tab groups verbs by medium (visual & cards, writing, video, audio), and the operation tab groups them by process stage (discover & topics, plan & positioning, publish & quality gate, data & review). Every capability carries a maturity badge — **Verified**, **Ready**, **Needs setup**, **Incoming** — so a pick sets expectations before it runs. Picking copies a structured instruction template (【…】 fill-in markers) to the clipboard; the paste-into-session hop is the user's one action because no composer-draft seam exists yet.

Escape or the header close button dismisses the surface; closed state renders null while the slot entry stays mounted. Both target slots are declared by other plugins, so `apply` installs both registrations atomically through one `slots.inject()` generator for the declaration lifetime, and the components share one open/close controller injected into each.

The **Review** view (复盘) closes the operations loop: platform metric exports import as CSV through a parse-preview-commit flow (unknown columns surface as checkboxes, bad rows are named, never dropped), only works bound to a creation content id enter the analysis pool, and the dashboard, per-work AI diagnosis, and the frozen six-section period report judge everything against persisted account baselines (viral at twice the baseline engagement rate, weak below half, long-tail by a 30-day pace gate). A failed AI call still lands a data-only report; conclusions reflow into the topic bank with one click, and viral templates save under `assets/review/templates/`. Storage lives in the theme's `_review.json` sidecar plus a hidden global index — `.dsh-output.json` is never touched.

The competitors view (对标) gained a fourth **Volume compare** (声量对比) section: the word rows are the union of the rival accounts' niche tags, and each row counts my sentiment mentions hitting the word (title or summary, through one `getSentiment` read per visit) against the theme's library works whose title hits it — both sides are data the two columns already own, so the section is one optional injected read face and a table, with every empty state naming its next action (scan first / tag the accounts).

The competitors works library gained two collection affordances beyond manual import. The **sort select** orders works by publish date, interaction score, or the newest saves count — tutorial accounts collect far more than they like, so like-only rankings hide their real top works. The **browser-sync import** (导入浏览器同步) accepts the version-1 JSON an out-of-band ego-browser collector writes (account name/platform/followers/bio plus a works array with platform ids, titles, likes): every entry upserts through the same dedup path as manual import, the matched account's follower tier backfills (positioning only when empty), and the account's `syncedAt` stamps so the catch-up banner quiets. The payload is a convenience export, not a trusted wire — malformed entries are skipped, never fatal. The collector script itself stays outside this package; it drives a logged-in browser session per platform, and the works row now shows the 赞/藏/评 triple from each work's newest snapshot. The account card's **Account audit** button (账号体检) runs the eight-dimension health audit — an `audit` report kind whose digest pairs the registry facts (follower tier, positioning, monetization) with median-based distribution facts, and whose report lands in the Reports tab like the other two kinds.

The **Sentiment** view (企业舆情分析) is the opinion-monitoring surface over the `_sentiment.json` faces: monitor-task management (keyword groups with polarity bias, per-task source toggles over RSS feeds plus weibo visitor search and bilibili public hot search — one anonymous page each on the first subject, degraded to an empty page on any block, with the account blacklist now live against social authors), a dashboard with polarity shares, the 14-day trend, and the per-platform top list, the mention list linking each classified row to its original article, an alert inbox of task+day aggregated negative events (level 1–4 from heat against the configured threshold) where each row also offers a one-click reflow into the topic bank as an `idea` tagged 舆情 through the shared topics Remote, an AI report tab (one gateway call renders the five-section daily report over the stored snapshot, with a Markdown download link and an explicit degraded banner when the model call fell back to the data-only template), and a settings form (the push master switch, Dingtalk/WeCom webhook URLs, the SMTP transport fields, thresholds, domain and account blacklists, retention). The scan is manual-first — one button runs the gateway's single-slot scan (RSS fetch through the shared gather fetcher, lexicon presale, batched LLM refinement for the ambiguous, alert aggregation, then one digest per configured channel — webhooks and SMTP email — when new alerts land). Everything persists through the `contentOutputs` sentiment Remotes; nothing is simulated.

<a id="model-experience"></a>
## Model Experience

Indirectly, through the `dsh-content-outputs` Remotes its buttons trigger: that gateway assembles every framed request on the shared `llm` service, while this package owns only the click, the pending state, and the retry affordance.

#### KV Cache effect

None; this package never assembles or sends a provider request, so it owns no request prefix.

<a id="known-limitations-and-deferred-work"></a>
## Known Limitations and Deferred Work

One orienting sentence, then top-level bullets naming current package constraints.

- **No composer hand-off** — picking a capability copies the instruction instead of prefilling a session draft; a runtime draft/prefill seam would remove the paste hop.
- **The capability catalog is static** — menu items are shipped data, not derived from the mounted skill registry, so maturity badges must be maintained by hand until a catalog RPC exists.
- **Single-surface state** — open/closed state lives in one controller instance per apply; the surface is not per-session and holds no session context.

<a id="understand-the-implementation"></a>
## Understand the implementation

<details>
<summary>Implementation internals — click to expand</summary>

The plugin mounts its own host Remote contributions (`contentOutputs`, `contentSchedule`, `contentTopics`) through `ctx.remote.$mount()` before a workbench fiber that declares each namespace by exact service name runs the controllers and the two slot registrations. Both target slots (`sidebar.footer.action`, `shell.overlay`) are declared by other plugins, so `apply` installs both registrations atomically through one `slots.inject()` generator for the declaration lifetime, and the components share one open/close controller injected into each. Escape or the header close button dismisses the surface; closed state renders null while the slot entry stays mounted.

| File | Role |
|---|---|
| [`src/client/index.ts`](src/client/index.ts) | The browser half: Remote mounting, the gateway closures, and the slot registrations |
| [`src/client/ContentStudio.tsx`](src/client/ContentStudio.tsx) | The surface shell: nav, identity injection, and the per-view mounts |
| [`src/client/capabilities.ts`](src/client/capabilities.ts) | The static capability catalog and its maturity badges |
| [`src/client/locales.ts`](src/client/locales.ts) | The typed locale dictionaries the whole surface routes copy through |
| [`tests/apply.client.spec.ts`](tests/apply.client.spec.ts) | Slot registration, inject face, and envelope-unwrapping behavior |

</details>

-----

<a id="further-exploration"></a>
## Further Exploration

- [creation group README](../../creation/README.md) — the outputs domain this surface reads and writes.
- [content-outputs package](../../creation/content-outputs/README.md) — the Remote gateway behind every write face.
- [Slots subsystem page](../../../docs/subsystems/slots.md) — the registration seam the two slot installs use.
- [Bilingual UI copy decision note](../../../.agents/notes/implemented/architecture/2026-08-23-locale-owned-client-ui-copy.md) — why every label routes through the locale dictionaries.

-----

<a id="dev-note"></a>
### Dev Note

<details>
<summary>Working context for maintainers — click to expand</summary>

None.

</details>
