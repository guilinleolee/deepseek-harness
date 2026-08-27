---
name: opc-platform-bridge
description: OPC与天龙引擎9平台分发桥接——将OPC内容校准、潜客挖掘与天龙multi-platform-publisher打通，实现内容生产→质量门控→分发→追踪的完整闭环。
metadata:
  dragon-engine:
    emoji: 🌐
    version: 1.0
    source: xiaobei × dragon-engine
    license: OpenClaw + MIT
    tags:
      - opc
      - platform-bridge
      - 9-platform
      - integration
---

# OPC Platform Bridge — OPC × 天龙9平台分发桥接

> **来源**: xiaobei × dragon-engine融合
> **License**: OpenClaw + MIT
> **融合日期**: 2026-08-17

## 核心价值

打通**OPC内容校准**、**OPC潜客挖掘**与**天龙引擎9平台分发**，实现：
- 内容生产 → 质量门控 → 分发 → 追踪完整闭环
- 潜客触达 → 平台分发 → 互动追踪

---

## 与天龙引擎的融合架构

```
┌─────────────────────────────────────────────────────────────┐
│                   OPC能力层                                   │
├─────────────────────────────────────────────────────────────┤
│  opc-content-calibrator  │  opc-lead-hunting  │  opc-bd-record │
│  (7维打分)              │  (潜客挖掘)        │  (追踪数据库)  │
└────────────┬────────────┴────────┬─────────┴───────────────┘
             │                     │
             ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│              opc-platform-bridge (本技能)                    │
├─────────────────────────────────────────────────────────────┤
│  1. 内容质量门控：打分达标才分发                            │
│  2. 潜客触达分发：精准触达+分发                          │
│  3. 发布数据追踪：分发→数据闭环                           │
└────────────┬─────────────────────┴───────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│              dragon-engine 9平台分发                         │
├─────────────────────────────────────────────────────────────┤
│  multi-platform-publisher                                 │
│  小红书 | 公众号 | 视频号 | 抖音 | YouTube | TikTok | X | LinkedIn | 微博 │
└─────────────────────────────────────────────────────────────┘
```

---

## 使用流程

### 流程1：内容生产 → 校准 → 分发

```
1. 天龙引擎生成内容（小红书图文/视频脚本）
   ↓
2. opc-content-calibrator 7维打分
   ↓
3. 达标(通过阈值门) → multi-platform-publisher 分发
   ↓
4. opc-bd-record 记录发布
   ↓
5. T+3d → 数据复盘 → rubric进化
```

### 流程2：潜客触达 → 分发

```
1. opc-smart-search 搜索目标潜客
   ↓
2. opc-lead-hunting 挖掘潜客
   ↓
3. 天龙引擎生成个性化触达内容
   ↓
4. multi-platform-publisher 精准分发
   ↓
5. opc-bd-record 记录触达+互动
```

---

## 调用示例

### 内容分发

```bash
# 1. 内容打分
./skills/opc-content-calibrator/scripts/score-only.sh \
  --cal-er 3 --cal-hp 4 --cal-sr 3 --cal-ql 4 --cal-na 3 --cal-ab 4 --cal-pv 2

# 2. 达标后分发
node skills/multi-platform-publisher/publish.js \
  --platform xhs \
  --content "./output/article.md" \
  --images "./output/images/"

# 3. 记录发布
./skills/opc-bd-record/scripts/record-post.sh \
  --platform xhs \
  --post-url "https://..." \
  --strategy direct_comment
```

### 潜客触达分发

```bash
# 1. 挖掘潜客
./skills/opc-lead-hunting/scripts/hunt.sh \
  --platform xhs \
  --strategy creator

# 2. 生成个性化内容
# (天龙引擎三模态生成)

# 3. 精准分发
./skills/multi-platform-publisher/publish.js \
  --platform xhs \
  --target-user-id <潜客ID>

# 4. 记录触达
./skills/opc-bd-record/scripts/record-post.sh \
  --platform xhs \
  --strategy reply_dm
```

---

## 与天龙引擎的深度融合

| 天龙能力 | × OPC能力 | = 融合效果 |
|----------|-----------|------------|
| multi-platform-publisher | content-calibrator | **质量门控分发** |
| multi-platform-publisher | lead-hunting | **精准触达分发** |
| multi-platform-publisher | bd-record | **分发数据闭环** |
| viral-chaser | content-calibrator | **爆款规律提炼** |

---

## License合规

- **来源**: xiaobei (OpenClaw) + dragon-engine (MIT)
- **License**: OpenClaw + MIT双轨
- **合规状态**: ✅ 通过
