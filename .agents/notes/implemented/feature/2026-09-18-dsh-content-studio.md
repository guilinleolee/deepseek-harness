# Agent Note: Content Studio enters the web shell through the two existing additive slots, not a new navigation slot

Status: implemented

English | [中文](2026-09-18-dsh-content-studio.zh.md)

## Problem

The web app had no "content creation" surface: creation verbs lived only in the model's skill catalog, invisible until a user knew to type a prompt. Three earlier attempts existed in the tree (`packages/extensions/dsh-creation-workbench`, `packages/client/client-ui-creator-workbench`, the deleted `dsh-web-ui/packages/dsh-customer-service`), and every one of them calls injection APIs that do not exist on the current client runtime (`ctx.slots.sidebar.add`, `ctx.slots.page.register`, a `shell.tab.*` slot with no declarer, `ctx.webServer`), so none of them can render. The underlying question: how does a plugin add a first-class feature entry plus a full workbench page to the assembled web shell without touching the framework?

## Decision

`packages/client/ui-content-studio` registers into the two additive slots the shell already declares, and touches no other package:

- **The entry** fills ui-sidebar's `sidebar.footer.action` (a `list` slot that had zero registrants). Wide column renders a labeled row, the 56px rail an icon — the owner share (`{ wide }`) already covers both states.
- **The surface** fills ui-layout's `shell.overlay` (`list`, documented as "the additive seat for a frame-wide surface of your own"). The overlay layer's CSS already hands every direct child pointer events, so a fixed-inset workbench needs no frame change. Open state covers the frame; Escape and the header close button dismiss; closed state renders null with the entry mounted.

Both registrations install atomically through one `slots.inject('sidebar.footer.action', function* () { … })` generator for the declaration lifetime — the pattern `ui-brand-official` established — and share one open/close controller injected into each entry, because component state cannot cross two slot registrations.

The workbench ships the dual-intent capability menu (Create by medium: visual/writing/video/audio; Operate by stage: discover/plan/publish/review), each item carrying a four-state maturity badge (verified / ready / needs-setup / incoming). Picking copies a structured instruction template (【…】 fill-in markers) to the clipboard.

The **Library view** reads the agent's outputs through the `contentOutputs/list` Remote: `packages/creation/content-outputs` is a Remote-only Typert gateway (`@deepseek-ai/dsh-content-outputs`, no ctx key) that scans `<dsh home>/outputs` on every call and projects the on-disk convention — one directory per creation, finished files at the root, intermediate material under `assets/`, `.dsh-output.json` as the only metadata (`formatVersion 0`, no compatibility promise). The mount is **self-contained**: the studio's own async `apply` mounts both `/remote` artifacts through `ctx.remote.$mount()` (the api-remotes pattern moved into the plugin), so the browser bundle carries its whole server face and api-remotes knows nothing about these packages — dropping the plugin from the roster removes the feature entirely. A malformed metadata file never hides its project (fallbacks plus `hasMetadata: false`); an unreadable directory is named in the snapshot's `problems`.

The **Calendar view** adds the same pattern with a mutation face: `packages/creation/content-schedule` (`@deepseek-ai/dsh-content-schedule`) serves `contentSchedule/list|put|remove` over one system file — `_schedule.json` at the library root, whose `_` prefix the outputs scanner already treats as non-project. Items follow Easel's `idea → draft → scheduled → published` progression; `put` upserts by generated-UUID id alone; every method reads or commits under the atomic-write writer lock so reads stay lock-free and writers serialize. The month grid itself is a pure module (`calendar.ts`), unit-tested without React; the component holds only view state (current month, the one open add form) and re-renders from each mutation's returned snapshot — the file on disk remains the single truth, which is also what keeps an agent able to read the same calendar through plain file tools.

## Alternatives considered

**A new `sidebar.nav.entry` slot in ui-sidebar.** The original plan. Rejected for phase 1 once the audit showed `sidebar.footer.action` unoccupied: a framework slot added for a single consumer is the wrong default while a documented extension point covers the use case. The nav-slot extension stays deferred until an entry needs to live inside the main column (above the workspaces region) rather than at the foot.

**Composing the studio into `sidebar.workspaces` or the `conversation` column.** Both are `single` slots with occupants; registering there replaces shipped UI outright and couples the studio to ui-workspace/ui-conversation internals. The overlay keeps the studio strictly additive.

**Deriving the catalog from `ctx.skills` now.** The `skill.list` RPC exists but is session-attached and not user-invocable-aware in the shape a menu needs; deriving maturity automatically is unsolved. Shipped data keeps the badges honest until a dedicated catalog RPC lands (phase 2, alongside the outputs project tree).

## Consequences

The first real-world proof that a third-party plugin can add a feature entry and a full page to the web shell through documented slots alone — `dshmarket` previewed this from outside the roster, this is the in-tree template. Three costs: picking a capability copies to the clipboard instead of prefilling a composer draft (no draft seam exists in the client runtime; adding one is a runtime change still deferred); the catalog's maturity badges are hand-maintained until a catalog RPC exists; and the surface is root-scoped with no session context, so it cannot show per-session state. The library read is a scan-per-call Remote on purpose — the outputs root is the agent's write surface, so caching would add a second truth. The boot snapshot lane (`pnpm run test:web:built`) exercises the plugin through the built roster.
