# twitter-adapter

> **Twitter/X平台适配器** — 内容发布与数据采集适配层

## 平台概览

| 维度 | 数值 |
|------|------|
| **日活用户** | 2.5亿+ |
| **内容形式** | 推文(280字)、图片、视频、Spaces音频 |
| **主要用户** | 25-45岁，全球用户 |
| **核心场景** | 新闻、观点、科技、名人娱乐 |

## 评分维度适配

### Twitter特有维度权重

| 维度 | 权重 | 说明 |
|------|------|------|
| ER (曝光率) | ×2.0 | **Twitter最重要指标**，ForYou推荐流量 |
| SR (互动率) | ×1.5 | 点赞/回复/转发 |
| HP (完播率) | ×0.5 | Twitter以图文为主，权重降低 |
| QL (质量分) | ×1.0 | 内容质量 |
| NA (数值锚) | ×1.5 | 数字吸引点击，权重提升 |
| AB (行动率) | ×1.0 | 关注转化 |
| SAT (满意度) | ×1.0 | 用户满意度 |

### 评分公式调整

```
总分 = (ER×2.0 + SR×1.5 + HP×0.5 + QL×1.0 + NA×1.5 + AB×1.0 + SAT×1.0) / 8.0 × 2.0
```

注意：ER权重提升到2.0，反映Twitter ForYou算法的曝光驱动逻辑。

## 发布流程

### 标准发布流程

```bash
# 1. 预测评分（发布前）
[@cheat-predict] 预测Twitter内容评分
# 输出：预测分数 + 信心指数

# 2. 提交预测（锁定）
[@cheat-publish] 提交Twitter内容预测
# 输出：预测ID + Buffer状态

# 3. 发布内容
[@twitter-adapter] 发布推文
# 参数：text, media, poll, reply_settings

# 4. Buffer -1
[@buffer-guard] ship --id <预测ID> --platform Twitter
```

### 发布参数

```yaml
platform: Twitter/X
content_type: text / text_with_media / poll / space
text_length: 1-280字 (单推) / 1-25000字 (长推文)
image_limit: 1-4张
video_duration: 140s - 10min
file_formats: jpg, png, gif, mp4
max_file_size: 10MB (图片) / 512MB (视频)
hashtags: #标签 最多10个
mentions: @用户
```

## 数据采集

### 采集指标

| 指标 | API字段 | 采集频率 |
|------|---------|---------|
| 曝光量 | impressions | 实时 |
| 点赞数 | like_count | 实时 |
| 转发数 | retweet_count | 实时 |
| 回复数 | reply_count | 实时 |
| 书签数 | bookmark_count | 每天 |
| 关注转化 | follow_count | 每天 |

### 数据采集命令

```bash
# 采集推文数据
python3 skills/cheat-on-content/tools/twitter-adapter.py fetch \
  --tweet-id <ID> \
  --metrics impressions,like_count,retweet_count,reply_count

# 批量采集
python3 skills/cheat-on-content/tools/twitter-adapter.py batch \
  --date-range 2026-05-22,2026-05-25 \
  --platform Twitter

# 导出到预测追踪
python3 skills/cheat-on-content/tools/twitter-adapter.py export \
  --tweet-id <ID> \
  --format json \
  --output predictions/2026-05/<ID>-actual.json
```

## 实际评分填写

### T+3d复盘数据

```bash
python3 skills/cheat-on-content/tools/retro-form.py fill \
  --id <预测ID> \
  --type t3d \
  --platform Twitter \
  --actual ER=<曝光率> \
  --actual SR=<互动率> \
  --actual HP=<完播率> \
  --actual QL=<质量分> \
  --actual NA=<数值锚> \
  --actual AB=<行动率> \
  --actual SAT=<满意度>
```

### Twitter特有指标

```yaml
extra_metrics:
  - name: 转发率
    key: share_rate
    importance: P0
  - name: 书签率
    key: bookmark_rate
    importance: P1
  - name: ForYou曝光占比
    key: foryou_ratio
    importance: P1
  - name: 话题参与量
    key: hashtag_engagement
    importance: P2
```

## 预测准确度参考

### Twitter预测偏差基线

| 维度 | 平均偏差 | 说明 |
|------|---------|------|
| ER (曝光率) | ±2.5分 | **偏差最大**，ForYou算法不可预测 |
| SR (互动率) | ±1.5分 | 点赞转发相对稳定 |
| HP (完播率) | ±0.5分 | 图文内容为主 |
| QL (质量分) | ±1.0分 | 主观评分稳定 |
| NA (数值锚) | ±1.2分 | 数字吸引可预测 |
| AB (行动率) | ±1.5分 | 关注转化波动大 |
| SAT (满意度) | ±1.0分 | 反馈较稳定 |

### Twitter高偏差预警

当ER偏差 > 3分时，触发Rubric验证：
- 可能原因：话题热度变化/蹭热点时机/账号权重变化

## 内容策略

### Twitter内容类型匹配

| 类型 | ER | SR | NA | AB | 适用场景 |
|------|----|----|----|----|---------|
| 热点评论 | 高 | 高 | 高 | 低 | 新闻/科技/娱乐 |
| 观点输出 | 中 | 高 | 中 | 高 | 职场/创业/生活 |
| 干货分享 | 中 | 中 | 高 | 高 | 技术/知识/教程 |
| 互动提问 | 中 | 高 | 低 | 中 | 社区运营/调研 |
| 产品推广 | 中 | 中 | 中 | 高 | 品牌/电商/工具 |

### Twitter传播法则

```
Twitter推荐权重因素：
1. 早期互动速度（最高权重）
2. ForYou算法匹配
3. 账号权重
4. 话题相关性

爆款推文公式：
- 开头钩子（前50字必须抓住）
- 中间价值（提供有用信息）
- 结尾引导（点赞/转发/关注）
```

### 高互动标题公式

```
高互动推文公式：
1. 争议观点："The most controversial take you'll read today..."
2. 数据支撑："I analyzed 1000 tweets and found..."
3. 逆向思维："Stop doing X. Do this instead."
4. 好奇悬念："The thing nobody talks about..."
5. 实用价值："How to do X in 5 steps"
```

## 配置

```yaml
twitter:
  platform_id: twitter
  display_name: Twitter/X
  content_types:
    - text
    - text_with_media
    - poll
    - space
  weights:
    ER: 2.0    # Twitter权重提升
    SR: 1.5
    HP: 0.5    # Twitter权重降低
    QL: 1.0
    NA: 1.5    # Twitter权重提升
    AB: 1.0
    SAT: 1.0
  thresholds:
    er_warning: 6.0
    er_critical: 5.0
  data_sources:
    - twitter_api_v2
    - alternative_data
```

## 数据存储

```
~/.claude/skills/cheat-on-content/
├── predictions/
│   └── YYYY-MM/
│       └── YYYY-MM-DD-XX-submitted.json  # 包含Twitter特定字段
├── retrospectives/
│   └── YYYY-MM/
│       ├── YYYY-MM-DD-XX-t3d.md
│       └── YYYY-MM-DD-XX-t7d.md
└── platforms/
    └── twitter/
        ├── tweet-metrics.json      # Twitter数据缓存
        ├── trend-analysis.json      # Twitter趋势分析
        └── competitor-benchmark.json  # 竞品对比
```

## 异常处理

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 数据采集失败 | API限流 | 使用缓存数据 + 延迟重试 |
| ER偏差 > 4分 | ForYou算法变化 | 更新发布策略观察 |
| 互动率偏低 | 内容不够引发讨论 | 优化观点输出方式 |

## 与其他平台对比

| 维度 | Twitter | 微博 | 抖音 |
|------|---------|------|------|
| ER权重 | 2.0 | 2.0 | 1.5 |
| SR权重 | 1.5 | 1.5 | 1.5 |
| HP权重 | 0.5 | 0.5 | 2.0 |
| 全球覆盖 | 强 | 中 | 中 |
| 热点效应 | 强 | 强 | 中 |

## 使用示例

```bash
# 完整工作流
[@cheat-init] 初始化Twitter内容项目
[@cheat-seed] 选择Twitter种子话题
[@cheat-shoot] 制作Twitter图文/视频
[@cheat-predict] 预测Twitter评分
[@cheat-publish] 提交预测并发布

# 复盘工作流
[@twitter-adapter] 采集T+3d数据
[@retro-form] 填写T+3d复盘
[@buffer-guard] 完成T+3d复盘
[@prediction-tracker] 分析偏差
[@rubric-calculator] 检查Rubric健康
```
