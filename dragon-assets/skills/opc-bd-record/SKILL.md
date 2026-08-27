---
name: opc-bd-record
description: OPC BD记录——维护SQLite追踪数据库，记录已探索的创作者和已互动的帖子，避免重复追踪和重复互动。与opc-lead-hunting和opc-comment-engagement配合使用。
metadata:
  dragon-engine:
    emoji: 📝
    version: 1.0
    source: xiaobei/TeamWiseFlow
    license: OpenClaw
    tags:
      - opc
      - bd-record
      - database
      - tracking
---

# OPC BD Record — 商务拓展记录

> **来源**: xiaobei (TeamWiseFlow/OpenClaw)
> **License**: OpenClaw开源协议
> **融合日期**: 2026-08-17

## 核心价值

与**opc-lead-hunting**和**opc-comment-engagement**配合使用：
- 避免重复探索同一创作者
- 避免重复互动同一帖子
- 记录潜客档案

---

## 数据库位置

```
./db/bd_record.db
```

初始化（幂等）：`./skills/opc-bd-record/scripts/init-db.sh`

---

## 表结构

### lead_creators（创作者探索）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 自增主键 |
| platform | TEXT | 平台标识（xhs/douyin/weibo/bilibili/twitter） |
| creator_id | TEXT | 创作者ID |
| nickname | TEXT | 创作者昵称 |
| homepage_url | TEXT | 创作者主页URL |
| qualified | INTEGER | 是否符合潜客标准（1=是，0=否） |
| notes | TEXT | 备注 |
| created_at | TEXT | 记录时间 |

### comment_posts（帖子互动）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 自增主键 |
| platform | TEXT | 平台标识 |
| post_title | TEXT | 帖子标题 |
| post_url | TEXT | 帖子URL |
| strategy | TEXT | 互动策略 |
| replied | INTEGER | 是否已互动（1=是，0=否） |
| reply_content | TEXT | 互动内容 |
| reply_target_id | TEXT | 互动目标ID |
| created_at | TEXT | 记录时间 |

---

## 与天龙引擎的融合

### 融合点

| 天龙能力 | × OPC BD记录 | = 融合效果 |
|----------|-------------|------------|
| 博主全息克隆 | 潜客档案 | **博主商业价值数据库** |
| 9平台分发 | 互动记录 | **全域用户追踪** |
| viral-chaser | 爆款互动 | **爆款传播路径** |

### 典型使用

```bash
# 初始化数据库
./skills/opc-bd-record/scripts/init-db.sh

# 检查创作者是否已记录
./skills/opc-bd-record/scripts/check-creator.sh --platform xhs --creator-id xxx

# 记录创作者
./skills/opc-bd-record/scripts/record-creator.sh \
  --platform xhs \
  --creator-id xxx \
  --nickname "xxx" \
  --qualified 1 \
  --notes "符合条件：xxx"

# 检查帖子是否已互动
./skills/opc-bd-record/scripts/check-post.sh --platform xhs --post-url "xxx"

# 记录互动
./skills/opc-bd-record/scripts/record-post.sh \
  --platform xhs \
  --post-url "xxx" \
  --strategy reply_dm \
  --reply-content "xxx"
```

---

## License合规

- **来源**: xiaobei (OpenClaw开源)
- **License**: OpenClaw开源协议
- **天龙融合**: MIT兼容
