# Agent Note: dsh-media-desk versus the in-tree creation domain

Status: proposed

English | [中文](2026-11-11-media-desk-versus-creation-upgrade.zh.md)

## Problem

The community plugin [`woniuniuniu/dsh-media-desk`](https://github.com/woniuniuniu/dsh-media-desk) (MIT, 997 stars) ships a creator workbench for the harness: an idea wall, one-click draft generation (title, spoken script, video cover, supporting images, six-panel storyboard), a publication calendar, review analytics, and style presets. Its README asks whether it should be installed alongside the harness or studied for ideas to fold into the existing content-creation packages.

The question is real because the harness already owns this domain:

| Package | Role |
| --- | --- |
| `packages/creation/content-outputs` | gather, create, publish, review, persona, competitor, interactions, sentiment, and template faces (~14k LOC host) |
| `packages/creation/content-schedule` | the `_schedule.json` publication calendar |
| `packages/creation/content-topics` | the `_topics.json` topic bank |
| `packages/client/ui-content-studio` | the Content Studio client (~19k LOC) |

media-desk's five pages map onto existing Content Studio columns: ideas → topic bank, content → create face, schedule → content-schedule, review → review face, style → persona face. Where the surfaces coincide, media-desk is not ahead: its persona capture covers six platforms through a paid Monid dependency, while the harness persona face already covers eight (xhs, douyin, bili, zhihu, wechat, channels, weibo, toutiao) with no third-party cost, and its review face already parses per-platform CSV exports, which is what media-desk's "paste CSV" review path does.

Three capabilities are genuinely absent from the harness:

1. **Image generation.** No image-generation tool exists in `packages/*/*/src` — the create face emits text only, while media-desk generates nine images per draft (cover, supporting illustrations, storyboard panels).
2. **Storyboard, cover, and shot-list concepts.** Nothing in the creation packages models a six-panel storyboard or a video cover.
3. **Conversational revision.** The harness offers a fixed rewrite toolbar (`CREATE_REWRITE_OPERATIONS`: condense, expand, style, perspective, extract, humanize-light, humanize-deep, titles), while media-desk offers free-form natural-language revision of a draft.

Two further differences are smaller: the harness ships seven persona style presets (`PERSONA_STYLE_PRESETS`) against media-desk's fifteen creator-domain styles, and the harness's topic bank is a list where media-desk draws an infinite canvas.

## Proposal

Fold media-desk's ideas into the surfaces that already own the domain model rather than installing a second content system beside them.

**Image generation is a harness capability, not a creation-package feature.** It belongs behind a documented extension point as an image-provider tool, with the create face consuming it the way it consumes `llm`. An image-provider seam plus an image-artifact store is new surface; the outputs library convention already accommodates the artifacts under `assets/`.

**Storyboard and cover are create-face content types.** They join `video-script` and `xhs-note` in `CREATE_CONTENT_TYPES`, and the storyboard persists in the existing `assets/_create.json` manifest — no new storage format.

**Conversational revision extends the create face's rewrite surface.** The fixed toolbar becomes the quick-pick layer over a free-form instruction, not a second assistant with its own state.

**Style presets extend `PERSONA_STYLE_PRESETS`.** The creator-domain dimension is a preset taxonomy addition to the existing persona model.

**The idea wall is a client-side view over `contentTopics/list`.** The canvas is a projection of the topic bank, not a second store.

### What is deliberately not ported

media-desk's Monid account-import path, its own `~/.dsh/media-desk/` storage, its DSH subscription image-tool integration (`dsh_subscriptions_image_generate` — absent from this tree, so its headline feature degrades to text-only out of the box), and its parallel client application.

## Alternatives considered

**Install media-desk alongside the harness.** Rejected. Two content systems would compete for one user — one persona, one topic bank, one schedule — while storing state in two unrelated places (`~/.dsh/media-desk/` versus `<dsh home>/outputs`). The result is a duplicated workbench whose interactions do not reach the harness's own content domain. media-desk also pins itself to the DSH 0.2.x line.

**Port media-desk wholesale.** Rejected. It duplicates the topic bank, schedule, review, and persona faces that the harness already implements, and it would import a second storage convention, a third-party account-import dependency, and a hand-rolled image-provider settings panel — all of which the harness reaches through better-owned seams.

## Acceptance criteria

- Image generation is reachable through a documented extension point and consumed by the create face, not reimplemented inside a creation package.
- Storyboard and cover appear as create-face content types persisted in the existing create manifest.
- Free-form revision is one operation on the existing rewrite surface, sharing its version history and the create face's prompt versioning.
- Style presets extend the persona preset list; no parallel persona store appears.
- The idea wall reads `contentTopics/list`; no second idea store appears.
- No package depends on Monid or on a DSH subscription image tool that the harness does not ship.

## Risks

- Image generation adds a provider seam, artifact storage, and cost accounting — the largest piece of work here, and it is the one capability that is new rather than extended.
- The create face's prompt contract changes when storyboard and cover join it, so the frozen prompt constants and their version markers need a bump and the JSON-contract faces need per-field problems for the new fields.
- Adding creator-domain presets widens the persona taxonomy that the picker, the packed prompt, and the digest all read.
