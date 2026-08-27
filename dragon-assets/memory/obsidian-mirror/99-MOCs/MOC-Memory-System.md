---
type: moc
title: "MOC-Memory-System"
tags: [dragon-engine, status/active, meta/index]
created: 2026-08-07
updated: 2026-08-07
source: dragon-engine-obsidian-mvp
confidence: 1.0
agent: null
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---


# 🧠 记忆系统索引（MOC）

> **自动维护** · 数据源：Obsidian Vault · 由天龙引擎 `obsidian-writer.js` 写入
>
> **生效日期**：2026-08-07 · **MVP 版本**：V9.0 · **架构**：PARA + Daily Notes + 双链

---

## 📊 笔记分布（按 type）

```dataview
TABLE WITHOUT ID
  type as "类型",
  length(rows) as "数量"
FROM ""
WHERE type
GROUP BY type
SORT length(rows) DESC
```

---

## 🎓 最近 20 条经验教训（lessons）

```dataview
TABLE title, created, confidence, source
FROM ""
WHERE type = "lesson"
SORT created DESC
LIMIT 20
```

---

## ⚖️ 待复盘决策（outcome 为空）

```dataview
TABLE title, created, source
FROM "10-Areas"
WHERE type = "decision" AND outcome = null
SORT created DESC
```

---

## 🔥 最近 7 天新增

```dataview
TABLE type, title, created
FROM ""
WHERE created >= date(today) - dur(7 days)
SORT created DESC
```

---

## 📅 最近周报（weekly-memory-digest 自动维护）

| 周编号 | 起始日 | Lessons | Decisions | Concepts | 周报链接 |
| --- | --- | --- | --- | --- | --- |
| 2026-W33 | 2026-08-01 | 8 | 0 | 1 | [[50-Daily-Notes/2026-W33-digest.md|📊 周报]] |
| --- | --- | --- | --- | --- | --- |

---

## 🧭 领域导航（10-Areas）

### 天龙引擎

- [[10-Areas/Dragon-Engine/Architecture|天龙引擎架构]]
- [[10-Areas/Dragon-Engine/Hooks-Registry|Hooks 注册表]]
- [[10-Areas/Dragon-Engine/Lessons/|经验教训库]]

### 写作

- [[10-Areas/Writing/|写作]]

### 金融

- [[10-Areas/Finance/|金融]]

### IP

- [[10-Areas/IP-Laoyi/|IP-Laoyi]]

---

## 📂 目录结构

```
00-Inbox/                 ← 临时收件箱（QuickAdd 捕获）
10-Areas/                 ← 持续关注领域
  ├─ Dragon-Engine/
  ├─ Writing/
  ├─ Finance/
  └─ IP-Laoyi/
20-Resources/             ← 主题资源（人/书/工具）
30-Projects/              ← 有明确目标的项目
40-Archives/              ← 归档（已完成）
50-Daily-Notes/           ← 每日日记
90-Templates/             ← QuickAdd 模板（5 个）
  ├─ Concept.md
  ├─ Decision.md
  ├─ Lesson.md
  ├─ Person.md
  └─ Project.md
99-MOCs/                  ← 索引/地图（本目录）
```

---

## 🔗 相关 MOC

- [[MOC-Dragon-Engine]]（待建）
- [[MOC-Writing]]（待建）
- [[MOC-Finance]]（待建）

---

## 📝 元信息

- **创建者**：天龙引擎 · 01-调研师 → 02-架构师 → 03-构建师 协作
- **维护机制**：天龙引擎 `obsidian-writer.js` 自动写入 + Dataview 实时聚合
- **镜像路径**：`C:\Users\li\.claude\projects\dragon-engine\memory\obsidian-mirror\`
- **双写策略**：Vault 主存 + 本地镜像（V7.4 兼容）
- **回滚策略**：保留 Manual Edits，writer 默认 append 不覆盖

## 备注

-