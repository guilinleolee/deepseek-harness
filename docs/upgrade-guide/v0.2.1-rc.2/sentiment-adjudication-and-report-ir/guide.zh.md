---
kind: upgrade-guide
description: "舆情报告新增结构化 ir，告警新增可选研判结论，并新增 adjudicateSentimentAlert 远端。"
---

# 读取舆情报告 IR 与告警研判

[English](guide.md) | 中文

## 变更

`SentimentReport` 新增可选 `ir` 字段，保存报告所用模板名（`daily` 或 `crisis`）与各节的 key、标题、正文。报告改为按告警选定的模板、每节一次模型调用生成，因此章节集合取决于存量状态而非固定不变；本次变更之前存储的报告仍可读取，只是没有 `ir`。

`SentimentAlert` 新增可选 `adjudication` 字段，保存乐观视角、审慎视角与综合结论。新增的 `adjudicateSentimentAlert` 远端为一条告警填入该字段，重复研判会覆盖旧结论。

扫描改用 LLM 扩展出的搜索词检索平台源，并在最热的匹配条目后下钻评论层，因此存量提及会以独立平台标签承载评论行。

## 迁移

1. 读取 `SentimentReport` 时把 `ir` 当作可选；本次变更之前存储的报告没有该字段。比较报告时按各节的 `key` 而非 Markdown 标题比对。
2. 读取 `SentimentAlert` 时把 `adjudication` 当作可选；只有跑过 `adjudicateSentimentAlert` 的告警才带该字段。
3. 新的评论提及仍走既有的 `platform` 字段：它们以 `微博评论` 或 `B站评论` 行出现。确认方式：对 sources 含微博或 B 站的任务跑一次扫描，在提及列表里查这两个平台标签。
