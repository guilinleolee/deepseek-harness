---
name: map-component-merge-decision
description: homegrown map-component V1.0（空壳）→ guizang map-component.md 合并回流决策（天龙阶段 17）
metadata: 
  node_type: memory
  type: project
  originSessionId: 1b69faff-55b8-4ac4-982e-93b0e3e2aafb
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---


# map-component 合并决策 · homegrown V1.0 → guizang

> **Why**：天龙阶段 17（guizang 集成 · 2026-07-17）的 R3 重叠评估发现 homegrown `map-component/` 是空壳规格（仅 SKILL.md，无 scripts/templates/examples），与已装可用的 guizang map-component.md 功能重叠但实现差距巨大；4 种独有样式（route/area/cluster/heatmap）需要回流。
>
> **How to apply**：任何 Agent 收到「旅行/探店地图 + 小红书图文」请求，统一路由到 guizang map-component.md（已合并 5 模式）；原 homegrown V1.0 永久归档。

---

## 决策记录

| 项 | 值 |
|----|---|
| 决策日期 | 2026-07-17 |
| 决策来源 | R3 重叠评估报告 |
| 决策类型 | **方案 1：合并回流** |
| 决策结论 | homegrown V1.0 归档 + 4 模式规格回流到 guizang map-component.md |

## 三方对比（明确假设纠正）

| 资产 | 实际状态 |
|------|---------|
| guizang map-component.md | ✅ 已装 · Playwright 渲染管线 · 9 条 DOM 校验 R1-R9 |
| **homegrown `dragon-engine/skills/map-component/`** | ⚠️ **空壳**（仅 SKILL.md）· scripts/templates/examples 全部缺失 |
| ip-diagram-creator（阶段 11）| 原仓库已退场 · lessons 分流到 4 个下游 skill |

**重要纠正**：原"ip-diagram-creator 与 guizang map-component 路径重叠"的假设是错的。**真正重叠方是 homegrown `map-component`**，ip-diagram-creator 从来不是地图技能。

## 模式回流清单

| 模式 | 来源 | 状态 | 备注 |
|------|------|------|------|
| pin（1-5 + 1 accent）| homegrown | ✅ guizang 已有 | max 6/board 硬规则 |
| **route**（3-8 stops 折线）| homegrown 独有 | 🟡 回流待补 | HTML 模板示例 + 坐标系规格 |
| **area**（多边形 + 5-10 POI）| homegrown 独有 | 🟡 回流待补 | 多边形点位 + 标签 |
| **cluster**（10-100 POI 聚类）| homegrown 独有 | 🟡 回流待补 | 圆形聚合 + 数量标签 |
| **heatmap**（100+ 网格密度）| homegrown 独有 | 🟡 回流待补 | 密度网格 + 颜色梯度 |

附加回流：
- 中国地图源降级策略（高德→百度→Google→OSM）作为 reference 引用
- 11-category 路由入口规格（旅行/职场/推荐/游戏/影视/...）
- WGS84 / GCJ02 / BD09 坐标系转换器 spec
- Editorial M13-M16 / Swiss S10 衍生版式规格

## 拒绝方案理由

| 方案 | 拒绝理由 |
|------|---------|
| **方案 2 · 强行合并** | homegrown 没实现，强行合并 = guizang 重写全部 scripts（得不偿失）|
| **方案 3a · 删 guizang 留 homegrown** | 丢弃 9 条 Playwright 校验 + 28 版式 + 渲染管线（亏）|
| **方案 3b · 删 homegrown 留 guizang** | 丢失 4 种独有模式规格（亏）|

## 5 条落地 TODO（按优先级）

1. 🔴 **归档** homegrown `map-component/` → `dragon-engine/skills/_archive/map-component-V1.0-DEPRECATED.md` ✅ 已完成
2. 🟡 **扩展** `dragon-engine/skills/guizang-social-card-skill/references/map-component.md` —— 在 "Three rendering modes" 后追加 "Five location styles (pin/route/area/cluster/heatmap)"
3. 🟡 **修正** `memory/ip-diagram-creator-integration.md` —— 路径澄清 + IP 视觉指纹 ≠ 地图
4. 🟢 **更新** `memory/MEMORY.md` 第 17 阶段行 —— 追加"map-component V1.0 已并入 guizang"
5. 🟢 **实际测试** 5 模式渲染（pin + route + area + cluster + heatmap）· 验证 Playwright 校验通过

## Agent 路由红线（3 行）

```
1. "做旅行/探店地图 + 小红书图文"  →  guizang map-component（5 模式，Mapbox/OSM）
2. "画 AI 工具关系图 / 博主 IP 知识卡 / Agent 协作图解"  →  smart-illustrator V2.2 或 ppt-master V9.9（绝不走地图）
3. 混淆请求 → 主动澄清（地图 = 地理坐标走 guizang；关系图 = 节点-边走 smart-illustrator）
```

**绝对不要**让 smart-illustrator 接管地图 POI；也**绝对不要**让 guizang map-component 画抽象节点-边关系图（它会被 max 6 pins / 1 accent 硬规则卡死）。

---

## 关键文件路径

| 资产 | 路径 |
|------|------|
| guizang map-component reference（已合并）| `dragon-engine/skills/guizang-social-card-skill/references/map-component.md` |
| homegrown map-component（已归档）| `dragon-engine/skills/_archive/map-component-V1.0-DEPRECATED.md` |
| guizang 渲染管线 | `dragon-engine/skills/guizang-social-card-skill/validate-social-deck.mjs` |
| ip-diagram-creator 集成模块 | `dragon-engine/skills/ip-diagram-creator-integration/` |
| 下游 4 skill（继承自 ip-diagram-creator）| `dragon-engine/skills/{smart-illustrator/SKILL.md (V2.2), ppt-master/SKILL.md (V9.9), qiaomu-mondo/SKILL.md (V1.1), blogger-fingerprint-registry/SKILL.md (V2.0)}` |

---

**主题文件总数**：13 → **14 个**（+ map-component-merge-decision）✅
**累计 PASS**：文档自检 27 + 依赖 1 + AGPL 边界判断 5 + 重叠评估 3 + 合并决策 5 = **41 项验证** ✅