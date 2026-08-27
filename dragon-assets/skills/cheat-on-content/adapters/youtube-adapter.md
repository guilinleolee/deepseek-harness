# youtube-adapter

> **YouTube平台适配器** — 内容发布与数据采集适配层

## 平台概览

| 维度 | 数值 |
|------|------|
| **日活用户** | 2.7亿+ |
| **内容形式** | 短视频(60s)、长视频(1-60min)、Shorts(15-60s) |
| **主要用户** | 18-65岁，全球用户 |
| **核心场景** | 娱乐、教育、知识、评测 |

## 评分维度适配

### YouTube特有维度权重

| 维度 | 权重 | 说明 |
|------|------|------|
| ER (曝光率) | ×1.5 | 搜索流量+推荐流量+订阅流量 |
| SR (互动率) | ×1.5 | 点赞/评论/分享 |
| HP (完播率) | ×2.0 | **YouTube最重要指标**，视频推荐核心 |
| QL (质量分) | ×1.0 | 视频质量 |
| NA (数值锚) | ×1.0 | 数字吸引点击 |
| AB (行动率) | ×1.0 | 订阅/点击外链 |
| SAT (满意度) | ×1.0 | 用户满意度 |

### 评分公式调整

```
总分 = (ER×1.5 + SR×1.5 + HP×2.0 + QL×1.0 + NA×1.0 + AB×1.0 + SAT×1.0) / 8.0 × 2.0
```

注意：HP权重提升到2.0，反映YouTube完播率驱动的推荐算法。

## 发布流程

### 标准发布流程

```bash
# 1. 预测评分（发布前）
[@cheat-predict] 预测YouTube内容评分
# 输出：预测分数 + 信心指数

# 2. 提交预测（锁定）
[@cheat-publish] 提交YouTube内容预测
# 输出：预测ID + Buffer状态

# 3. 发布内容
[@youtube-adapter] 发布视频
# 参数：title, description, tags, thumbnail, schedule

# 4. Buffer -1
[@buffer-guard] ship --id <预测ID> --platform YouTube
```

### 发布参数

```yaml
platform: YouTube
content_type: video / shorts
video_duration: 1min-60min (标准) / 15-60s (Shorts)
aspect_ratio: 16:9 (标准) / 9:16 (Shorts)
file_formats: mp4, mov, avi, mkv
max_file_size: 256GB
title_length: 1-100字
description_length: 1-5000字
tags: 最多500个标签
thumbnail: 1280x720px
```

## 数据采集

### 采集指标

| 指标 | API字段 | 采集频率 |
|------|---------|---------|
| 观看次数 | view_count | 实时 |
| 点赞数 | like_count | 实时 |
| 评论数 | comment_count | 实时 |
| 不喜欢数 | dislike_count | 每天 |
| 分享数 | share_count | 每天 |
| 订阅转化 | subscriber_count | 每天 |
| 平均观看时长 | average_view_duration | 每小时 |
| 观众留存 | audience_retention | 每小时 |

### 数据采集命令

```bash
# 采集视频数据
python3 skills/cheat-on-content/tools/youtube-adapter.py fetch \
  --video-id <ID> \
  --metrics view_count,like_count,comment_count,average_view_duration

# 批量采集
python3 skills/cheat-on-content/tools/youtube-adapter.py batch \
  --date-range 2026-05-22,2026-05-25 \
  --platform YouTube

# 导出到预测追踪
python3 skills/cheat-on-content/tools/youtube-adapter.py export \
  --video-id <ID> \
  --format json \
  --output predictions/2026-05/<ID>-actual.json
```

## 实际评分填写

### T+3d复盘数据

```bash
python3 skills/cheat-on-content/tools/retro-form.py fill \
  --id <预测ID> \
  --type t3d \
  --platform YouTube \
  --actual ER=<曝光率> \
  --actual SR=<互动率> \
  --actual HP=<完播率> \
  --actual QL=<质量分> \
  --actual NA=<数值锚> \
  --actual AB=<行动率> \
  --actual SAT=<满意度>
```

### YouTube特有指标

```yaml
extra_metrics:
  - name: 完播率
    key: watch_time_percentage
    importance: P0
  - name: 平均观看时长
    key: average_view_duration
    importance: P0
  - name: 观众留存曲线
    key: audience_retention
    importance: P1
  - name: CTR点击率
    key: click_through_rate
    importance: P1
  - name: 订阅转化率
    key: subscriber_conversion
    importance: P2
```

## 预测准确度参考

### YouTube预测偏差基线

| 维度 | 平均偏差 | 说明 |
|------|---------|------|
| ER (曝光率) | ±1.5分 | 搜索/推荐流量相对稳定 |
| SR (互动率) | ±1.2分 | 互动相对稳定 |
| HP (完播率) | ±2.5分 | **偏差最大**，预测困难 |
| QL (质量分) | ±0.8分 | 主观评分稳定 |
| NA (数值锚) | ±1.0分 | 数字吸引可预测 |
| AB (行动率) | ±1.5分 | 订阅转化波动大 |
| SAT (满意度) | ±1.0分 | 反馈较稳定 |

### YouTube高偏差预警

当HP偏差 > 3分时，触发Rubric验证：
- 可能原因：开头不够抓人/视频节奏问题/话题选择偏差

## 内容策略

### YouTube内容类型匹配

| 类型 | ER | HP | SR | AB | 适用场景 |
|------|----|----|----|----|---------|
| 知识教程 | 高 | 高 | 中 | 高 | 教育/技能/职场 |
| 产品评测 | 高 | 高 | 高 | 高 | 科技/美妆/家居 |
| 娱乐搞笑 | 高 | 中 | 高 | 低 | 娱乐/生活 |
| Vlog日常 | 中 | 中 | 高 | 中 | 个人IP/生活方式 |
| 热点评论 | 高 | 低 | 高 | 中 | 新闻/时事/观点 |

### YouTube推荐权重因素

```
YouTube推荐权重因素：
1. 观看时长/完播率（最高权重）
2. 点击率CTR
3. 观众留存曲线
4. 互动率
5. 订阅转化

开篇黄金5秒：
- 直接切入主题
- 制造悬念
- 承诺价值
- 视觉冲击
```

### 视频脚本结构

```
高完播率视频结构：
1. 开头（0-30秒）：Hook + 价值承诺
2. 正文（30秒-80%）：信息密度高，节奏紧凑
3. 高潮（80-95%）：最精彩内容
4. 结尾（95-100%）：CTA + 下期预告
```

## 配置

```yaml
youtube:
  platform_id: youtube
  display_name: YouTube
  content_types:
    - video
    - shorts
  weights:
    ER: 1.5
    SR: 1.5
    HP: 2.0    # YouTube权重提升
    QL: 1.0
    NA: 1.0
    AB: 1.0
    SAT: 1.0
  thresholds:
    hp_warning: 5.5
    hp_critical: 4.5
  data_sources:
    - youtube_data_api
    - vidiq_data
    - alternative_data
```

## 数据存储

```
~/.claude/skills/cheat-on-content/
├── predictions/
│   └── YYYY-MM/
│       └── YYYY-MM-DD-XX-submitted.json  # 包含YouTube特定字段
├── retrospectives/
│   └── YYYY-MM/
│       ├── YYYY-MM-DD-XX-t3d.md
│       └── YYYY-MM-DD-XX-t7d.md
└── platforms/
    └── youtube/
        ├── video-metrics.json      # YouTube数据缓存
        ├── trend-analysis.json      # YouTube趋势分析
        └── competitor-benchmark.json  # 竞品对比
```

## 异常处理

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 数据采集失败 | API限流 | 使用缓存数据 + 延迟重试 |
| HP偏差 > 3分 | 开头不够抓人 | 更新开篇策略观察 |
| 完播率偏低 | 视频节奏问题 | 优化内容结构 |

## 与其他平台对比

| 维度 | YouTube | 抖音 | 小红书 |
|------|---------|------|--------|
| HP权重 | 2.0 | 2.0 | 1.0 |
| ER波动 | 中 | 大 | 中 |
| 全球覆盖 | 强 | 中 | 弱 |
| 长视频优势 | 强 | 弱 | 弱 |
| 变现能力 | 强 | 强 | 中 |

## 使用示例

```bash
# 完整工作流
[@cheat-init] 初始化YouTube内容项目
[@cheat-seed] 选择YouTube种子话题
[@cheat-shoot] 制作YouTube视频
[@cheat-predict] 预测YouTube评分
[@cheat-publish] 提交预测并发布

# 复盘工作流
[@youtube-adapter] 采集T+3d数据
[@retro-form] 填写T+3d复盘
[@buffer-guard] 完成T+3d复盘
[@prediction-tracker] 分析偏差
[@rubric-calculator] 检查Rubric健康
```
