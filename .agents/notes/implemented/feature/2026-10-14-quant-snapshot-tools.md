# Agent Note: Snapshot lifecycle tools — list and reviewed delete

Status: implemented

English | [中文](2026-10-14-quant-snapshot-tools.zh.md)

## Problem

The result-snapshot channel was append-only with no model-facing surface: the panel read snapshots through the Remote face, but the model could neither see what was stored nor remove a stale or mistaken record. With rolling runs writing up to 10 records per job, the keep-50 pruning alone decided what survives — a caller cleaning up after exploratory runs had no lever.

## Decision

- **`quant_list_snapshots` is the read side.** The model-visible projection of the panel's data source: newest first, id, symbol, parameters, headline metrics (return, drawdown, trade count), and creation time. Ids in the render are truncated to 8 characters — enough to quote in a delete request without flooding the context with UUIDs.
- **`quant_delete_snapshot` is a reviewed delete, not a silent one.** The durable domain is append-mostly by design, so removal follows the same human-approval gate as the PET rebalance: the approval reason names the snapshot's content (symbol, SMA windows, curve points, creation date) plus the caller's own reason, and only `allowed-once` proceeds. A denial fails loud (`RISK`) and the record stays; a missing id fails with a friendly `DATA` error before any approval is asked. After a grant, the Remote face serves one less card on the next panel read.
- **The approval carries the content, not just the id.** The reviewer sees what they are deleting, because an id alone is not an informed consent surface.
- **Tool count moves 18 → 20** with the registration, apply-spec, and README counts moved together; both tools live inside the same compliance RULES coverage as the rest (broker-marker scan applies; no caps needed — no numeric arguments exist).

## Alternatives considered

**Panel-side manual delete (a button).** Deferred: the panel is read-only by construction, and a browser-side mutation would need its own approval path through the host — the model-side tool reuses the audited `dsh-user-approval` seam that the rebalance already exercises.

**A `force` parameter skipping the review.** Rejected: the red line is that durable-domain mutations are reviewed acts; an escape hatch would make the review theater.

**Bulk delete by age.** Rejected for now: the keep-50 prune already bounds the table, and bulk removal multiplies the blast radius of one mistaken approval.

## Consequences

Costs: none at rest — the tools are pure table reads and one reviewed delete. Verification: 327 vitest green — six new cases (newest-first list with metrics, empty list, granted delete verifying the approval payload and the table state, denied delete keeping the record, missing runtime/agent failing loud, missing snapshot rejected before any approval is asked). Bilingual README updated with both rows and the twenty-tool count; Agent Note trio recorded.
