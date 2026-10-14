# Customer-acquisition flash-model parser hardening

Status: implemented

English | [中文](2026-10-06-customer-acquisition-flash-parser-hardening.zh.md)

## Context

The P1 extractor and P1/P3 scorer call flash-tier models and parse their answers as strict JSON against the frozen field contract. Against the real DeepSeek endpoint the raw answers drifted in four recurring ways while still being substantively correct: Chinese echoes of the contract keys（"公司名称" instead of `company_name`）, literal line breaks inside string values, full-width separators（，：、）at structural positions, and the whole answer wrapped under an arbitrary natural-language key（"抽取结果"…）. The strict parse rejected these, so the real-API e2e failed on outputs a human would accept.

## Decision

- **Repair at the parse seam, once, in the extractor module.** `repairJsonBody` is a single string-state scan: inside strings it escapes literal newlines and passes everything else through; outside strings it rewrites the full-width separators to their JSON equivalents. Sharing the scan is what makes both repairs safe at once — a naive global regex cannot tell a structural `，` from one inside 预算50万，3天答复, and a separator before a number（"score"：85）must repair too. The scorer imports the same function.
- **Normalize drifted keys through a matcher table.** `canonicalKeyOf` maps Chinese and English key variants onto the contract keys; the parse descends through single-object wrappers (up to three levels), re-normalizing at each level, until a level actually carries field keys.
- **Drift surfaces in notes, never silently.** Unknown `decision_role` values and unrecognized keys are dropped but recorded in the output's `notes`; a missing `company_name` names the keys the model did emit. Operators can see what the model invented.
- **One self-heal retry.** On a parse failure the service re-prompts once with a stiffer instruction（严格只输出一个 JSON 对象，键名用英文契约键名）; a second failure fails loud.

## Rejected

- **Prompt-only discipline** — flash models drift regardless of instructions; retrying on every drift doubles latency for a deterministic fix.
- **A lenient JSON parser (json5-style)** — it accepts prose and comment-polluted bodies; non-JSON output must still fail loud so the audit trail records the failure.
- **Dropping unrecognized keys silently** — the drift is exactly what operators need to see when a template stops matching.

## Consequences, risks, trade-offs

The repair is confined to structural positions, so value text keeps its full-width punctuation; the string-state scan is pinned by tests both ways. Key normalization is table-driven — a Chinese alias not in the table still lands in `notes` rather than a field. The retry costs one extra model call in the failure case only. Anything the repair cannot recover still rejects with a friendly message after one retry.
