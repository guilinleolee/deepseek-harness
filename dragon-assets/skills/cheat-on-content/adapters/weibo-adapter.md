# weibo-adapter

> **微博平台适配器** — 内容发布与数据采集适配层

## 平台概览

| 维度 | 数值 |
|------|------|
| **日活用户** | 2.5亿+ |
| **内容形式** | 微博(140字)、长文章、图片、视频 |
| **主要用户** | 18-45岁 |
| **核心场景** | 热点、明星娱乐、意见领袖、新闻 |

## 评分维度适配

### 微博特有维度权重

| 维度 | 权重 | 说明 |
|------|------|------|
| ER (曝光率) | ×2.0 | **微博最重要指标**，粉丝流量+推荐流量 |
| SR (互动率) | ×1.5 | 转发/评论/点赞 |
| HP (完播率) | ×0.5 | 微博以图文为主，权重降低 |
| QL (质量分) | ×1.0 | 内容质量 |
| NA (数值锚) | ×1.5 | 数字吸引点击，权重提升 |
| AB (行动率) | ×1.0 | 关注转化 |
| SAT (满意度) | ×1.0 | 用户满意度 |

### 评分公式调整

```
总分 = (ER×2.0 + SR×1.5 + HP×0.5 + QL×1.0 + NA×1.5 + AB×1.0 + SAT×1.0) / 8.0 × 2.0
```

注意：ER权重提升到2.0，HP权重降低到0.5，反映微博曝光驱动的推荐逻辑。

## 发布流程

### 标准发布流程

```bash
# 1. 预测评分（发布前）
[@cheat-predict] 预测微博内容评分
# 输出：预测分数 + 信心指数

# 2. 提交预测（锁定）
[@cheat-publish] 提交微博内容预测
# 输出：预测ID + Buffer状态

# 3. 发布内容
[@weibo-adapter] 发布微博
# 参数：text, images, videos, topics

# 4. Buffer -1
[@buffer-guard] ship --id <预测ID> --platform 微博
```

### 发布参数

```yaml
platform: 微博
content_type: text / image_text / video / article
text_length: 1-2000字
image_limit: 1-9张
video_duration: 15s - 15min
file_formats: jpg, png, gif, mp4
max_file_size: 20MB (图片) / 500MB (视频)
topics: #话题 最多10个
mentions: @用户
```

## 数据采集

### 采集指标

| 指标 | API字段 | 采集频率 |
|------|---------|---------|
| 曝光量 | impressions | 实时 |
| 转发数 | reposts_count | 实时 |
| 评论数 | comments_count | 实时 |
| 点赞数 | attitudes_count | 实时 |
| 阅读数 | read_count | 每小时 |
| 关注转化 | follow_count | 每天 |

### 数据采集命令

```bash
# 采集微博数据
python3 skills/cheat-on-content/tools/weibo-adapter.py fetch \
  --weibo-id <ID> \
  --metrics impressions,reposts_count,comments_count,attitudes_count

# 批量采集
python3 skills/cheat-on-content/tools/weibo-adapter.py batch \
  --date-range 2026-05-22,2026-05-25 \
  --platform 微博

# 导出到预测追踪
python3 skills/cheat-on-content/tools/weibo-adapter.py export \
  --weibo-id <ID> \
  --format json \
  --output predictions/2026-05/<ID>-actual.json
```

## 实际评分填写

### T+3d复盘数据

```bash
python3 skills/cheat-on-content/tools/retro-form.py fill \
  --id <预测ID> \
  --type t3d \
  --platform 微博 \
  --actual ER=<曝光率> \
  --actual SR=<互动率> \
  --actual HP=<完播率> \
  --actual QL=<质量分> \
  --actual NA=<数值锚> \
  --actual AB=<行动率> \
  --actual SAT=<满意度>
```

### 微博特有指标

```yaml
extra_metrics:
  - name: 转发率
    key: repost_rate
    importance: P0
  - name: 阅读量
    key: read_count
    importance: P1
  - name: 上热搜概率
    key: hot_search_probability
    importance: P1
  - name: 话题参与量
    key: topic_engagement
    importance: P2
```

## 预测准确度参考

### 微博预测偏差基线

| 维度 | 平均偏差 | 说明 |
|------|---------|------|
| ER (曝光率) | ±2.5分 | **偏差最大**，热搜效应不可预测 |
| SR (互动率) | ±1.5分 | 转发评论相对稳定 |
| HP (完播率) | ±0.5分 | 图文内容为主 |
| QL (质量分) | ±1.0分 | 主观评分稳定 |
| NA (数值锚) | ±1.2分 | 数字吸引可预测 |
| AB (行动率) | ±1.5分 | 关注转化波动大 |
| SAT (满意度) | ±1.0分 | 反馈较稳定 |

### 微博高偏差预警

当ER偏差 > 3分时，触发Rubric验证：
- 可能原因：话题热度变化/蹭热点时机/粉丝活跃度下降

## 内容策略

### 微博内容类型匹配

| 类型 | ER | SR | NA | AB | 适用场景 |
|------|----|----|----|----|---------|
| 热点蹭流量 | 高 | 高 | 高 | 低 | 时事/娱乐/明星 |
| 观点输出 | 中 | 高 | 中 | 高 | 职场/情感/生活 |
| 干货分享 | 中 | 中 | 高 | 高 | 知识/技能/职场 |
| 产品推广 | 中 | 中 | 中 | 高 | 电商/品牌/种草 |
| 日常分享 | 低 | 中 | 低 | 低 | 个人IP/生活 |

### 热搜蹭流量公式

```
微博传播权重因素：
1. 话题热度（最高权重）
2. 粉丝基础量
3. 发布时间
4. 互动率

蹭热点策略：
- 第一时间发声
- 独特视角差异化
- 简短有力易传播
- 引导互动评论
```

### 内容公式

```
高互动内容公式：
1. 观点鲜明法："我认为...，不服来辩"
2. 悬念法："没想到...，结果...（评论区见）"
3. 求助法："求助...，在线等挺急的"
4. 盘点法："盘点2026年...，第3个最意外"
5. 共鸣法："有没有人和我一样...的"
```

## 配置

```yaml
weibo:
  platform_id: weibo
  display_name: 微博
  content_types:
    - text
    - image_text
    - video
    - article
  weights:
    ER: 2.0    # 微博权重提升
    SR: 1.5
    HP: 0.5    # 微博权重降低
    QL: 1.0
    NA: 1.5    # 微博权重提升
    AB: 1.0
    SAT: 1.0
  thresholds:
    er_warning: 6.0
    er_critical: 5.0
  data_sources:
    - weibo_open_api
    - newrank_data
    - alternative_data
```

## 数据存储

```
~/.claude/skills/cheat-on-content/
├── predictions/
│   └── YYYY-MM/
│       └── YYYY-MM-DD-XX-submitted.json  # 包含微博特定字段
├── retrospectives/
│   └── YYYY-MM/
│       ├── YYYY-MM-DD-XX-t3d.md
│       └── YYYY-MM-DD-XX-t7d.md
└── platforms/
    └── weibo/
        ├── weibo-metrics.json      # 微博数据缓存
        ├── trend-analysis.json      # 微博趋势分析
        └── competitor-benchmark.json  # 竞品对比
```

## 异常处理

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 数据采集失败 | API限流 | 使用缓存数据 + 延迟重试 |
| ER偏差 > 4分 | 话题热度变化 | 更新热点监测策略 |
| 转发率偏低 | 内容不够引发讨论 | 优化观点输出方式 |

## 与其他平台对比

| 维度 | 微博 | 抖音 | 小红书 |
|------|------|------|--------|
| ER权重 | 2.0 | 1.5 | 1.5 |
| SR权重 | 1.5 | 1.5 | 2.0 |
| HP权重 | 0.5 | 2.0 | 1.0 |
| 热点效应 | 强 | 中 | 弱 |
| 传播速度 | 快 | 中 | 慢 |

## 使用示例

```bash
# 完整工作流
[@cheat-init] 初始化微博内容项目
[@cheat-seed] 选择微博种子话题
[@cheat-shoot] 制作微博图文/视频
[@cheat-predict] 预测微博评分
[@cheat-publish] 提交预测并发布

# 复盘工作流
[@weibo-adapter] 采集T+3d数据
[@retro-form] 填写T+3d复盘
[@buffer-guard] 完成T+3d复盘
[@prediction-tracker] 分析偏差
[@rubric-calculator] 检查Rubric健康
```
