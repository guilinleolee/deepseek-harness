---
kind: upgrade-guide
description: "The sentiment report carries a structured ir, alerts carry an optional adjudication, and a new adjudicateSentimentAlert remote appears."
---

# Read the sentiment report IR and the alert adjudication

English | [中文](guide.zh.md)

## Change

`SentimentReport` gains an optional `ir` field holding the report's template name (`daily` or `crisis`) and its sections' key, title, and body. The report is now generated one model call per section over a template chosen by the stored alerts, so a report's section set depends on the state instead of being fixed; a stored report written before this change stays readable and has no `ir`.

`SentimentAlert` gains an optional `adjudication` field holding an optimistic stance, a cautious stance, and a synthesized conclusion. The new `adjudicateSentimentAlert` remote fills it for one alert and replaces an earlier verdict on a later run.

The scan searches the platform sources with LLM-expanded search terms and drills the comment layer behind the hottest matched entries, so the stored mentions carry comment rows on their own platform labels.

## Migration

1. Treat `ir` as optional when reading `SentimentReport`; a report stored before this change has none. Compare reports by their sections' `key` values rather than by Markdown headings.
2. Treat `adjudication` as optional on `SentimentAlert`; an alert carries one only after `adjudicateSentimentAlert` ran for it.
3. Consume the new comment mentions through the existing `platform` field: they arrive as `微博评论` or `B站评论` rows. Confirm by running a scan on a task whose sources include weibo or bilibili and checking the mention list for those platform labels.
