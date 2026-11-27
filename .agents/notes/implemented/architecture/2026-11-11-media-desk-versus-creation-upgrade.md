# Agent Note: dsh-media-desk versus the in-tree creation domain

Status: implemented

English | [中文](2026-11-11-media-desk-versus-creation-upgrade.zh.md)

## Problem

The community plugin [`woniuniuniu/dsh-media-desk`](https://github.com/woniuniuniu/dsh-media-desk) (MIT) ships a creator workbench for the harness: an idea wall, one-click draft generation (title, spoken script, video cover, supporting images, six-panel storyboard), a publication calendar, review analytics, and style presets. Its README asked whether it should be installed alongside the harness or studied for ideas to fold into the existing content-creation packages.

The question was real because the harness already owned this domain:

| Package | Role |
| --- | --- |
| `packages/creation/content-outputs` | gather, create, publish, review, persona, competitor, interactions, sentiment, and template faces |
| `packages/creation/content-schedule` | the `_schedule.json` publication calendar |
| `packages/creation/content-topics` | the `_topics.json` topic bank |
| `packages/client/ui-content-studio` | the Content Studio client |

media-desk's five pages mapped onto existing Content Studio columns: ideas → topic bank, content → create face, schedule → content-schedule, review → review face, style → persona face. Where the surfaces coincided, media-desk was not ahead: its persona capture covered six platforms through a paid Monid dependency, while the harness persona face already covered eight (xhs, douyin, bili, zhihu, wechat, channels, weibo, toutiao) at no third-party cost, and its review face already parsed per-platform CSV exports.

Three capabilities were genuinely absent, and two smaller differences sat beside them: no image generation, no storyboard/cover/shot-list concept, no free-form conversational revision; seven persona style presets against media-desk's fifteen, and a list-shaped topic bank where media-desk drew an infinite canvas.

## Decision

media-desk's ideas were folded into the surfaces that already own the domain model rather than installing a second content system beside them.

**Image generation is a harness capability, not a creation-package feature.** It lives behind one documented extension point: `packages/media/image-generation` provides `ctx.imageGeneration` as a capability seam with a provider registry and one bundled OpenAI-compatible provider reading `baseURL`, `apiKeyEnv`, and its defaults live through `ctx.credentials`. The create face consumes it the way it consumes `ctx.llm` — read per call, so a composition may omit it without breaking the gateway's load.

**Storyboard and cover are create-face content types.** `storyboard` and `cover` join `video-script` and `xhs-note` in `CREATE_CONTENT_TYPES`, and their documents persist in the existing `assets/_create.json` manifest with no new storage format. `parseCreateStoryboard` and `parseCreateCoverPlan` read the model's markdown field-wise.

**Conversational revision extends the create face's rewrite surface.** The fixed toolbar is the quick-pick layer over a free-form `custom` instruction, bounded to 500 characters and reaching the prompt under the same "keep the facts, output only the rewrite" discipline as every other operation, so it shares the version history and the create face's prompt versioning instead of becoming a second assistant with its own state.

**Style presets extend `PERSONA_STYLE_PRESETS`.** The creator-domain dimension is a taxonomy addition to the existing persona model: seven tone presets plus eight creator domains, with no parallel persona store.

**The idea wall is a client-side view over `contentTopics/list`.** `TopicBankCanvas.tsx` is a projection of the topic bank — draggable, zoomable, with the keyword gather — not a second idea store.

Three follow-up gaps closed after the first shipping round:

- **Inline article figures.** The `xhs-note` brief already asked the model to write `[配图 N]` markers, but nothing rendered them. `parseCreateFigures` reads the markers and `generateFigureImages` renders the named figures into `assets/figure-NN.<ext>`, so a prose type reaches the image face without a second document format.
- **Per-target redraw.** `generateStoryboardImages` and `generateFigureImages` take the 1-based shot or figure numbers to render, so changing one shot costs one provider call instead of the whole set. Numbers the document does not carry, and targets with no brief, are skipped.
- **Typeset cover text.** A provider asked to draw text returns glyph-shaped noise, so the plan's main title is not part of the image prompt: `cover-text.ts` typesets it in the browser over the rendered image and exports one 1920×1080 file, falling back to a gradient card when no image was rendered.

### What is deliberately not ported

media-desk's Monid account-import path, its own `~/.dsh/media-desk/` storage, its DSH subscription image-tool integration (`dsh_subscriptions_image_generate`, absent from this tree, so its headline feature degrades to text-only out of the box), its hand-rolled image-provider settings panel, its `{ zh, en }` dictionaries (this repository ships eight locales and routes copy through typed locale dictionaries), and its parallel client application.

## Alternatives considered

**Install media-desk alongside the harness.** Rejected. Two content systems would compete for one user — one persona, one topic bank, one schedule — while storing state in two unrelated places (`~/.dsh/media-desk/` versus `<dsh home>/outputs`). The result is a duplicated workbench whose interactions do not reach the harness's own content domain. media-desk also pins itself to the DSH 0.2.x line.

**Port media-desk wholesale.** Rejected. It duplicates the topic bank, schedule, review, and persona faces that the harness already implements, and it would import a second storage convention, a third-party account-import dependency, a hand-rolled image-provider settings panel, a two-language copy path, and a pure-JavaScript surface with no typecheck — all of which the harness reaches through better-owned seams.

**Copy media-desk's host-side producer job model in the same round.** Deferred, not rejected. media-desk runs its production pipeline as a host job that survives a page close, streams plan text, and writes each image as it lands. The create face instead renders inside one Remote call, so the browser must wait. Adopting a job model would change the Remote contract and the polling surface together, which is a larger change than the capability it serves.

**Fold the whole style library in as prompts.** Rejected. media-desk ships sixteen hand-written creator personas with signature vocabulary and avoid-lists. The harness models the same dimension as a preset taxonomy on the persona entry, so the presets were extended rather than a second style library added.

## Consequences

The create face gained a provider seam, artifact storage under `assets/`, and a per-target render contract; the persona picker, packed prompt, and digest all read the widened preset taxonomy; and the client gained a canvas compositor that runs only in the browser, so a headless or CLI caller gets the bare rendered image without the typeset title.

Each capability landed on the surface that already owned its data, so one persona, one topic bank, one schedule, and one outputs library serve the whole workbench. The image seam is deployment-configurable rather than baked in, which means a composition that omits it keeps the text-only path and a composition that includes it fails loudly with the setting's name rather than silently degrading.

Still open, and deliberately outside this decision:

- **No host job model** — a draft's images render inside one Remote call, so a closed page interrupts the render. media-desk's `Producer` job map is the reference if this becomes worth the contract change.
- **No calendar page in the Content Studio nav** — `content-schedule` is mounted and the topic bank writes plan dates through it, but the surface has no month view; scheduling happens through the publish form and the topic plan-date field.
- **Domestic platforms only in the publish registry** — `publish/model.ts` registers seven platforms; media-desk's TikTok, Instagram, YouTube, and X legs need per-platform adaptation rules, not just a name.

## Testing

`create-storyboard.spec.ts` pins the storyboard, cover, and figure parsers including the unnumbered-marker and repeated-number cases; `create-images.spec.ts` pins per-target rendering, file naming by produced media type, and the reader's byte-prefix sniffing and size cap; `cover-text.client.spec.ts` pins the units, wrapping, font-size selection, paint order, image decode failure, and download-name sanitizing against a recording canvas stub.
