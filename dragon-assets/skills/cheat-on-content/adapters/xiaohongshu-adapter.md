# xiaohongshu-adapter

> **小红书平台适配器** — 内容发布与数据采集适配层

## 平台概览

| 维度 | 数值 |
|------|------|
| **日活用户** | 2.6亿+ |
| **内容形式** | 图文笔记(1-9图)、短视频(15s-10min) |
| **主要用户** | 18-35岁，女性占比75%+ |
| **核心场景** | 种草、购物决策、生活方式 |

## 评分维度适配

### 小红书特有维度权重

| 维度 | 权重 | 说明 |
|------|------|------|
| ER (曝光率) | ×1.5 | 搜索流量+推荐流量 |
| SR (互动率) | ×2.0 | **小红书最重要指标**，收藏/评论/点赞 |
| HP (完播率) | ×1.0 | 视频笔记权重降低 |
| QL (质量分) | ×1.5 | 封面+正文质量权重提升 |
| NA (数值锚) | ×1.0 | 数字吸引点击 |
| AB (行动率) | ×1.5 | 收藏+购买转化 |
| SAT (满意度) | ×1.0 | 用户满意度 |

### 评分公式调整

```
总分 = (ER×1.5 + SR×2.0 + HP×1.0 + QL×1.5 + NA×1.0 + AB×1.5 + SAT×1.0) / 9.5 × 2.0
```

注意：SR和AB权重提升到2.0和1.5，反映小红书收藏驱动的内容生态。

## 发布流程

### 标准发布流程

```bash
# 1. 预测评分（发布前）
[@cheat-predict] 预测小红书内容评分
# 输出：预测分数 + 信心指数

# 2. 提交预测（锁定）
[@cheat-publish] 提交小红书内容预测
# 输出：预测ID + Buffer状态

# 3. 发布内容
[@xiaohongshu-adapter] 发布笔记
# 参数：title, content, images, tags

# 4. Buffer -1
[@buffer-guard] ship --id <预测ID> --platform 小红书
```

### 发布参数

```yaml
platform: 小红书
content_type: image_text / video
image_limit: 1-9张
video_duration: 15s - 10min
aspect_ratio: 3:4 (竖图) / 1:1 (方图) / 16:9 (横图)
file_formats: jpg, png, mp4
max_file_size: 100MB (图片) / 1GB (视频)
title_length: 1-20字
content_length: 50-1000字
tags: 最多10个标签
```

## 数据采集

### 采集指标

| 指标 | API字段 | 采集频率 |
|------|---------|---------|
| 曝光量 | show_count | 实时 |
| 点赞数 |liked_count | 实时 |
| 收藏数 | collected_count | 实时 |
| 评论数 | comment_count | 实时 |
| 分享数 | share_count | 实时 |
| 关注转化 | follow_count | 每天 |
| 商品点击 | product_click | 每天 |

### 数据采集命令

```bash
# 采集笔记数据
python3 skills/cheat-on-content/tools/xiaohongshu-adapter.py fetch \
  --note-id <ID> \
  --metrics show_count,liked_count,collected_count,comment_count

# 批量采集
python3 skills/cheat-on-content/tools/xiaohongshu-adapter.py batch \
  --date-range 2026-05-22,2026-05-25 \
  --platform 小红书

# 导出到预测追踪
python3 skills/cheat-on-content/tools/xiaohongshu-adapter.py export \
  --note-id <ID> \
  --format json \
  --output predictions/2026-05/<ID>-actual.json
```

## 实际评分填写

### T+3d复盘数据

```bash
python3 skills/cheat-on-content/tools/retro-form.py fill \
  --id <预测ID> \
  --type t3d \
  --platform 小红书 \
  --actual ER=<曝光率> \
  --actual SR=<互动率> \
  --actual HP=<完播率> \
  --actual QL=<质量分> \
  --actual NA=<数值锚> \
  --actual AB=<行动率> \
  --actual SAT=<满意度>
```

### 小红书特有指标

```yaml
extra_metrics:
  - name: 收藏率
    key: collection_rate
    importance: P0
  - name: 笔记互动率
    key: engagement_rate
    importance: P0
  - name: 关注转化率
    key: follow_conversion
    importance: P1
  - name: 商品点击率
    key: product_click_rate
    importance: P1 (种草内容)
  - name: 搜索曝光占比
    key: search_exposure_ratio
    importance: P2
```

## 预测准确度参考

### 小红书预测偏差基线

| 维度 | 平均偏差 | 说明 |
|------|---------|------|
| ER (曝光率) | ±1.8分 | 搜索/推荐流量波动大 |
| SR (互动率) | ±2.5分 | **偏差最大**，收藏行为不稳定 |
| HP (完播率) | ±1.0分 | 图文内容为主 |
| QL (质量分) | ±0.8分 | 封面质量主观评分稳定 |
| NA (数值锚) | ±1.2分 | 数字吸引可预测 |
| AB (行动率) | ±2.0分 | 收藏转化波动大 |
| SAT (满意度) | ±1.0分 | 反馈较稳定 |

### 小红书高偏差预警

当SR偏差 > 3分时，触发Rubric验证：
- 可能原因：封面不够吸引/话题选择偏差/发布时间不当

## 内容策略

### 小红书内容类型匹配

| 类型 | ER | SR | QL | AB | 适用场景 |
|------|----|----|----|----|---------|
| 种草安利 | 中 | 高 | 高 | 高 | 美妆/穿搭/家居 |
| 干货教程 | 高 | 高 | 高 | 高 | 知识/职场/技能 |
| 探店打卡 | 中 | 中 | 高 | 中 | 美食/旅行/娱乐 |
| 生活方式 | 高 | 高 | 中 | 中 | 日常分享/情感 |
| 产品测评 | 中 | 高 | 高 | 高 | 科技/美妆/家居 |

### 封面黄金法则

```
小红书推荐权重因素：
1. 封面点击率（最高权重）
2. 收藏数
3. 互动率
4. 关注转化

封面策略：
- 真人出镜 > 物拍 > 文字
- 竖图3:4 > 方图1:1 > 横图16:9
- 颜色鲜艳对比度高
- 文字简洁有冲击力
```

### 标题公式

```
高点击率标题公式：
1. 身份认同法："月薪3000到3万，我做对了这3件事"
2. 数字法："5个让我脱胎换骨的习惯"
3. 情绪法："真的！后悔没早点知道"
4. 好奇法："原来这样才是最省钱的"
5. 对比法："vs传统做法，这个绝了"
```

## 配置

```yaml
xiaohongshu:
  platform_id: xiaohongshu
  display_name: 小红书
  content_types:
    - image_text
    - video
  weights:
    ER: 1.5
    SR: 2.0    # 小红书权重提升
    HP: 1.0
    QL: 1.5    # 小红书权重提升
    NA: 1.0
    AB: 1.5    # 小红书权重提升
    SAT: 1.0
  thresholds:
    sr_warning: 5.5
    sr_critical: 4.5
  data_sources:
    - xiaohongshu_open_api
    - hxyl_data
    - alternative_data
```

## 数据存储

```
~/.claude/skills/cheat-on-content/
├── predictions/
│   └── YYYY-MM/
│       └── YYYY-MM-DD-XX-submitted.json  # 包含小红书特定字段
├── retrospectives/
│   └── YYYY-MM/
│       ├── YYYY-MM-DD-XX-t3d.md
│       └── YYYY-MM-DD-XX-t7d.md
└── platforms/
    └── xiaohongshu/
        ├── note-metrics.json      # 小红书数据缓存
        ├── trend-analysis.json    # 小红书趋势分析
        └── competitor-benchmark.json  # 竞品对比
```

## 异常处理

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 数据采集失败 | API限流 | 使用缓存数据 + 延迟重试 |
| SR偏差 > 3分 | 封面不够吸引 | 更新封面策略观察 |
| 收藏率偏低 | 话题选择偏差 | 优化话题标签 |

## 与其他平台对比

| 维度 | 小红书 | 抖音 | 微博 |
|------|--------|------|------|
| SR权重 | 2.0 | 1.5 | 1.5 |
| QL权重 | 1.5 | 1.0 | 1.0 |
| ER波动 | 中 | 大 | 大 |
| 收藏驱动 | 强 | 中 | 弱 |
| 电商转化 | 高 | 高 | 中 |

## 使用示例

```bash
# 完整工作流
[@cheat-init] 初始化小红书内容项目
[@cheat-seed] 选择小红书种子话题
[@cheat-shoot] 制作小红书图文/视频
[@cheat-predict] 预测小红书评分
[@cheat-publish] 提交预测并发布

# 复盘工作流
[@xiaohongshu-adapter] 采集T+3d数据
[@retro-form] 填写T+3d复盘
[@buffer-guard] 完成T+3d复盘
[@prediction-tracker] 分析偏差
[@rubric-calculator] 检查Rubric健康
```
