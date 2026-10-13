# douyin-adapter

> **抖音平台适配器** — 内容发布与数据采集适配层

## 平台概览

| 维度 | 数值 |
|------|------|
| **日活用户** | 7亿+ |
| **内容形式** | 短视频(15s-10min)、图文 |
| **主要用户** | 18-35岁 |
| **核心场景** | 娱乐、种草、电商 |

## 评分维度适配

### 抖音特有维度权重

| 维度 | 权重 | 说明 |
|------|------|------|
| ER (曝光率) | ×1.5 | 抖音推荐算法为核心 |
| SR (互动率) | ×1.5 | 点赞/评论/收藏/分享 |
| HP (完播率) | ×2.0 | **抖音最重要指标**，权重提升 |
| QL (质量分) | ×1.0 | 内容质量 |
| NA (数值锚) | ×1.5 | 数字吸引点击，权重提升 |
| AB (行动率) | ×1.0 | 关注/购买转化 |
| SAT (满意度) | ×0.5 | 权重降低，完播优先 |

### 评分公式调整

```
总分 = (ER×1.5 + SR×1.5 + HP×2.0 + QL×1.0 + NA×1.5 + AB×1.0 + SAT×0.5) / 8.5 × 2.0
```

注意：HP权重提升到2.0，SAT权重降低到0.5，反映抖音完播率优先的推荐逻辑。

## 发布流程

### 标准发布流程

```bash
# 1. 预测评分（发布前）
[@cheat-predict] 预测抖音内容评分
# 输出：预测分数 + 信心指数

# 2. 提交预测（锁定）
[@cheat-publish] 提交抖音内容预测
# 输出：预测ID + Buffer状态

# 3. 发布内容
[@douyin-adapter] 发布视频
# 参数：video_path, title, description, tags

# 4. Buffer -1
[@buffer-guard] ship --id <预测ID> --platform 抖音
```

### 发布参数

```yaml
platform: 抖音
content_type: video
duration_range: 15s - 10min
aspect_ratio: 9:16 (竖版) / 16:9 (横版)
file_formats: mp4, mov
max_file_size: 4GB
title_length: 1-55字
description_length: 1-2000字
tags: 最多10个标签
```

## 数据采集

### 采集指标

| 指标 | API字段 | 采集频率 |
|------|---------|---------|
| 曝光量 | play_count | 实时 |
| 点赞数 | dig_count | 实时 |
| 评论数 | comment_count | 实时 |
| 收藏数 | collect_count | 实时 |
| 分享数 | share_count | 实时 |
| 完播率 | finish_rate | 每小时 |
| 关注转化 | follow_count | 每天 |

### 数据采集命令

```bash
# 采集内容数据
python3 skills/cheat-on-content/tools/douyin-adapter.py fetch \
  --content-id <ID> \
  --metrics play_count,dig_count,comment_count,finish_rate

# 批量采集
python3 skills/cheat-on-content/tools/douyin-adapter.py batch \
  --date-range 2026-05-22,2026-05-25 \
  --platform 抖音

# 导出到预测追踪
python3 skills/cheat-on-content/tools/douyin-adapter.py export \
  --content-id <ID> \
  --format json \
  --output predictions/2026-05/<ID>-actual.json
```

## 实际评分填写

### T+3d复盘数据

```bash
python3 skills/cheat-on-content/tools/retro-form.py fill \
  --id <预测ID> \
  --type t3d \
  --platform 抖音 \
  --actual ER=<曝光率> \
  --actual SR=<互动率> \
  --actual HP=<完播率> \
  --actual QL=<质量分> \
  --actual NA=<数值锚> \
  --actual AB=<行动率> \
  --actual SAT=<满意度>
```

### 抖音特有指标

```yaml
extra_metrics:
  - name: 完播率
    key: finish_rate
    importance: P0
  - name: 5秒完播率
    key: early_finish_rate
    importance: P1
  - name: 平均观看时长
    key: avg_watch_time
    importance: P1
  - name: 关注转化率
    key: follow_rate
    importance: P2
  - name: 商品点击率
    key: product_click_rate
    importance: P2 (电商内容)
```

## 预测准确度参考

### 抖音预测偏差基线

| 维度 | 平均偏差 | 说明 |
|------|---------|------|
| ER (曝光率) | ±1.5分 | 抖音流量波动大 |
| SR (互动率) | ±1.2分 | 互动相对稳定 |
| HP (完播率) | ±2.0分 | **偏差最大**，预测困难 |
| QL (质量分) | ±0.8分 | 主观评分稳定 |
| NA (数值锚) | ±1.0分 | 数字吸引较可预测 |
| AB (行动率) | ±1.5分 | 转化波动大 |
| SAT (满意度) | ±1.2分 | 反馈较稳定 |

### 抖音高偏差预警

当HP偏差 > 3分时，触发Rubric验证：
- 可能原因：开头不够抓人/话题热度变化/发布时间不当

## 内容策略

### 抖音内容类型匹配

| 类型 | ER | HP | SR | AB | 适用场景 |
|------|----|----|----|----|---------|
| 知识干货 | 中 | 高 | 中 | 高 | 职场/教育 |
| 娱乐搞笑 | 高 | 中 | 高 | 低 | 泛娱乐 |
| 剧情短片 | 高 | 中 | 高 | 中 | 情感/生活 |
| 种草安利 | 中 | 高 | 高 | 高 | 电商/美妆 |
| 热点新闻 | 高 | 低 | 高 | 中 | 时事/娱乐 |

### 开篇黄金3秒

```
抖音推荐权重因素：
1. 开头3秒留存率（最高权重）
2. 完播率
3. 互动率
4. 关注转化

开篇策略：
- 悬念式："你知道吗，80%的人..."
- 利益式："学会这3招，效率翻倍"
- 冲突式："老板绝对不会告诉你的..."
- 数据式："震惊！某公司..."（慎用）
```

## 配置

```yaml
douyin:
  platform_id: douyin
  display_name: 抖音
  content_types:
    - video
    - live_stream
    - image_text
  weights:
    ER: 1.5
    SR: 1.5
    HP: 2.0    # 抖音权重提升
    QL: 1.0
    NA: 1.5
    AB: 1.0
    SAT: 0.5   # 抖音权重降低
  thresholds:
    hp_warning: 5.5
    hp_critical: 4.5
  data_sources:
    - douyin_open_api
    - chorus_data
    - alternative_data
```

## 数据存储

```
~/.claude/skills/cheat-on-content/
├── predictions/
│   └── YYYY-MM/
│       └── YYYY-MM-DD-XX-submitted.json  # 包含抖音特定字段
├── retrospectives/
│   └── YYYY-MM/
│       ├── YYYY-MM-DD-XX-t3d.md
│       └── YYYY-MM-DD-XX-t7d.md
└── platforms/
    └── douyin/
        ├── content-metrics.json     # 抖音数据缓存
        ├── trend-analysis.json     # 抖音趋势分析
        └── competitor-benchmark.json  # 竞品对比
```

## 异常处理

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 数据采集失败 | API限流 | 使用缓存数据 + 延迟重试 |
| 完播率为0 | 视频未分发 | 等待1-2小时后重新采集 |
| HP偏差 > 4分 | 开头不够抓人 | 更新开篇策略观察 |

## 与其他平台对比

| 维度 | 抖音 | 快手 | 视频号 |
|------|------|------|--------|
| HP权重 | 2.0 | 1.5 | 1.5 |
| ER波动 | 大 | 中 | 小 |
| 社区氛围 | 弱 | 强 | 中 |
| 电商转化 | 高 | 高 | 中 |
| 时效性 | 高 | 中 | 低 |

## 使用示例

```bash
# 完整工作流
[@cheat-init] 初始化抖音内容项目
[@cheat-seed] 选择抖音种子话题
[@cheat-shoot] 制作抖音视频
[@cheat-predict] 预测抖音评分
[@cheat-publish] 提交预测并发布

# 复盘工作流
[@douyin-adapter] 采集T+3d数据
[@retro-form] 填写T+3d复盘
[@buffer-guard] 完成T+3d复盘
[@prediction-tracker] 分析偏差
[@rubric-calculator] 检查Rubric健康
```