# Customer-acquisition GEO diagnosis (P2)

Status: implemented

English | [中文](2026-10-04-customer-acquisition-geo-diagnosis.zh.md)

## Context

P2 of the 获客运营 plugin ships module 1 — GEO website diagnosis — in a sibling package (`packages/growth/customer-acquisition-geo/`) so its files never intersect the P1 lead/scoring ownership. The red lines bound every fetch: explicit URL only, serial concurrency 1, 10 s page timeout, 2 MiB body cap, 20-page cap, robots.txt `Disallow` skipping, no cross-domain discovery, no contact harvesting. The frozen contract pins scans and reports to the main plugin's storage domain.

## Decision

- **One-way sibling dependency through one seam file.** `src/main-package.ts` re-exports everything the GEO module reuses from the main package (contract types, audit writer, red-line constants, permission types); integration switched it from a worktree-relative stopgap to the package-name import once `tsconfig.base.json` mapped the `growth` group onto the `@deepseek-ai/dsh-*` source plane.
- **The domain stays single-open.** The service never opens the customer-acquisition domain itself; it resolves the already-open handle through the storage-domain facility and owns no lifecycle — the main plugin remains the sole owner and closer.
- **Boundary enforcement is two-layered.** A geo-owned `tools/pre-execute` gate (URL shape, page cap, settings caps, batch rules) runs ahead of the crawler, which independently enforces robots.txt, the body cap, the timeout, and serial execution; every rule has an illegal-path test.
- **The analyzer is deterministic.** Structural and content heuristics score llms.txt/robots/sitemap presence, brand/product/FAQ/case coverage, structure, and freshness; an LLM-judged pass can join later behind the same service interface without touching tools or tables.
- **Tests drive a scriptable FakeWeb provider** instead of a network: routes map URLs to bodies, fetches record call order and peak concurrency, so serial/robots/cap rules are pinned without a socket.

## Rejected

- **Model-based scoring in P2** — deterministic findings are reproducible and free; LLM judgment joins as a later enhancement, not the baseline.
- **Concurrent fetching** — the red line fixes concurrency at 1; parallelism would be a compliance change, not an optimization.
- **Opening the domain from the geo service** — the storage facility enforces single-open per name; borrowing keeps exactly one closer.

## Consequences, risks, trade-offs

The integration pass fixed what vite-only development had hidden: a missing `tsc -b` run left a readonly-array wire type, absent `required` flags, and a double-registered service in the composition test — all resolved before merge. Coverage fills for the geo module follow the P1 pattern and land with the merge.
