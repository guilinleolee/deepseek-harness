---
name: dragon-engine-synergy-matrix
description: 天龙引擎 skill/agent 关键协同矩阵（拆自 MEMORY.md）· 2026-08-07
metadata:
  node_type: memory
  type: reference
  originSessionId: ea8cdbe2-f3f1-4e15-9336-dfc87b23f437
  modified: 2026-08-07T00:00:00.000Z
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---


# 天龙引擎 · 关键协同矩阵（拆自 MEMORY.md）

> **Why**: MEMORY.md 行数约束 ≤140 行，§关键协同矩阵段是 28 行 ASCII 图，不常被主索引检索但内容重要；拆分后 MEMORY.md 留指针，详情走本文件。
>
> **How to apply**: 查"哪些 skill/agent 之间有协同关系、上下游链路" → 查本文件；查"阶段时间线 / 资产总数" → 查 `MEMORY.md` / `dragon-engine-meta-log.md`。

---

## 关键协同矩阵（压缩）

```
khazix-writer V1.1 ─┬─► laoli-writer V1.0 ─► 28-01 V10.3 ─► 35-02/35-05/35-06
                    └─► 28-04 内容策划师 ─► aihot V1.0
laoli-collab V1.0 ─► 35-02 V13.3 + 35-05 V10.3 + 28-04
agent-reach V1.5.0 ─► 28-04 + aihot(账号态证据)
anysearch V1.0 ⭐NEW ─┬─► core + 3 自研封装(academic/business/finance)
                  ├─► Apache-2.0 NOTICE(§apache-attribution-statements)
                  ├─► 01-investigator + 10-02-ai-researcher V8.74
                  └─► 与 agent-reach 双轨:anysearch 匿名摸底盘 → agent-reach 取账号态
xhs-visual-director V1.0 ─┬─► 24 风格决策 + 苏格拉底 10 问 ─► gpt-image-2-style-library ─► baoyu-xhs-images
guizang V1.0 ⚠️AGPL ─┬─► 28 版式 × 10 主题(仅 PNG 商单)
                  ├─► 5 模式地图(已合并 homegrown V1.0,见 map-merge-decision)
                  └─► 双源分工:guizang(AGPL) vs rednote-cover(MIT 单品)
huashu-design V2.2 ─┬─► 设计底座 + 9 维博主全息 V3
                  └─► html2pptx.js + render-video.js + tts-voxcpm.mjs
generative-media-skills V1.0 ⭐NEW ─┬─► 78 SKILL.md·MIT 零红线·200+ 模型 fallback
                              ├─► cinema-director+seedance-2 → 35-05 V11
                              ├─► ugc-video-factory → 35-06 V1.3 第 10 维
                              ├─► rednote-cover → baoyu-xhs-images 双源
                              ├─► nano-banana → GPT-Image2 reasoning brief
                              ├─► ai-clipping → baoyu-youtube-transcript 搭档
                              └─► core/ → async-task-pattern(5 原语+5 adapter)
voxcpm-voice-distillery ─► blogger-fingerprint-registry V3.0
hv-analysis ─► 35-07 横纵研究师 V1.0
ip-diagram-creator ─► smart-illustrator V2.2 + ppt-master V9.9
```

---

## 阅读指引

| 你想查... | 看这里 |
|---|---|
| 资产 / 路径 | `MEMORY.md` §关键文件路径（压缩）|
| 阶段 N 时间线 | `stage-N-announce.md` |
| 主题文件清单 | `dragon-engine-meta-log.md` |
| **协同关系** | **本文件** |