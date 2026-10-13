---
name: content-review-dashboard
description: |
  自媒体内容数据复盘：记录发布内容的表现数据，生成数据复盘看板。
  把发布到各平台的内容（阅读/点赞/评论/收藏/转发/涨粉）记录下来，统计效果，
  识别爆款与低效内容，反哺内容生产与选题。
  触发词: 数据复盘、内容复盘、记录内容、复盘看板、内容数据、看看数据、复盘
version: 1.0.0
category: dragon-engine-自媒体工作台
author: 秉凌
source: 秉凌自媒体工作台-数据复盘
created: 2026-08-11
---

# 内容数据复盘 (Content Review Dashboard)

> **自媒体工作台 · 数据复盘层** | 把发布内容变成数据反馈

## 用途

把发布到各平台的内容数据记录下来，形成持续更新的《数据复盘看板》：
- 记录：发布内容 + 各平台互动数据（阅读/点赞/评论/收藏/转发/涨粉）
- 统计：KPI 汇总 + 平台分布 + TOP 内容
- 洞察：哪个选题有效、哪个平台值得投入 → 反哺内容生产

## 数据存储

- CSV 文件：`~/viral-content-reports/dashboard/posts.csv`
- 每条内容一行，字段：id/date/platform/title/type/link/views/likes/comments/favorites/shares/fans/note

## 命令

### 记录内容
```bash
python scripts/run_dashboard.py add \
    --platform xiaohongshu \
    --title "AI训练师到底怎么入门" \
    --type 图文 \
    --views 1200 --likes 85 --comments 23 \
    --favorites 40 --shares 5 --fans 12 \
    --note "证书选题"
```

- `--platform`：`xiaohongshu`(小红书) / `douyin`(抖音) / `wechat`(公众号) / `zhihu`(知乎) / `bilibili`(B站) / `video`(视频号) / `weibo`(微博)
- `--type`：图文 / 短视频 / 长视频 / 文章 / 动态 / 其他
- 数据来源：各平台创作者中心（登录后查看互动数据，手动抄录）

### 查看列表
```bash
python scripts/run_dashboard.py list
python scripts/run_dashboard.py list --platform douyin
```

### 汇总统计
```bash
python scripts/run_dashboard.py stats
python scripts/run_dashboard.py stats --platform xiaohongshu
```

## 工作流

### Step 1 · 记录发布内容
每次发布内容后，从创作者中心抄录互动数据，用 `add` 命令记录（或通过 Streamlit UI 表单录入）。

### Step 2 · 查看数据
用 `list` / `stats` 查看记录和统计，识别：
- 🏆 TOP 内容（互动率高 = 选题/形式有效）
- 📉 低效内容（互动率低 = 需复盘改进）

### Step 3 · 反哺生产（核心价值）
把复盘结果反馈到内容生产：
1. **选题验证**：哪个需求库关键词的内容互动率高 → 该需求真实有效，加大投入
2. **平台选择**：哪个平台互动率高 → 主攻该平台
3. **形式优化**：图文/视频哪种形式效果好 → 调整内容形式

### Step 4 · 定期复盘
建议每周复盘一次：看当周 TOP 内容共性，调整下周内容计划。

## 质量门（交付前自查）

1. 每条记录数据真实（从创作者中心抄录，不编造）
2. 指标口径一致（同一平台的"阅读"定义一致）
3. 备注里注明选题来源（关联需求库关键词）
4. 复盘结论要有数据支撑（不凭感觉）

## 反向链接

- [[秉凌自媒体工作台]]
- [[数据复盘看板-规划方案]]
- [[天龙-viral-工作流-SOP-V2]]
- [[用户真实需求采集方案]]
