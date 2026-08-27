---
license: UNKNOWN
triggers: ["aitoearn engage", "AiToEarn Engage Skill"]
---
# AiToEarn Engage Skill

## L0 一句话描述（≤15字）
> AI自动化多平台互动运营（点赞/评论/关注/智能回复）

## L1 使用场景（50-100字）
适用于创作者、品牌方需要自动化运营多个社交平台账号的场景。AI自动完成点赞、评论、关注等互动操作，并智能回复粉丝评论，提升账号活跃度和粉丝粘性。

## L2 详细文档

### 核心能力

| 功能 | 说明 | 自动化程度 |
|------|------|-----------|
| **自动点赞** | 批量点赞目标内容 | 全自动 |
| **自动评论** | AI生成+批量发布评论 | 全自动 |
| **自动关注** | 批量关注目标用户 | 全自动 |
| **AI智能回复** | 自动回复粉丝评论 | AI驱动 |
| **互动统计** | 追踪互动数据 | 实时 |

### 支持平台

| 中国平台 | 海外平台 |
|----------|----------|
| 抖音、小红书、快手、B站 | TikTok、YouTube、Instagram |
| 视频号、微信公众号 | X、Facebook、LinkedIn、Pinterest |

### 配置

```bash
# 环境配置
export AITOERN_API_KEY="your-key"
export AITOERN_ENV="cn"  # cn=中国版, ai=国际版

# 初始化
aitoearn engage init --platform douyin
aitoearn engage init --platform xiaohongshu
```

### 核心命令

```bash
# 自动点赞
aitoearn engage like --target "用户/内容ID" --count 50
aitoearn engage like --hashtag "#话题" --count 100

# 自动评论
aitoearn engage comment --target "内容ID" --template "AI评论模板"
aitoearn engage comment --batch --file comments.csv

# 自动关注
aitoearn engage follow --target "用户ID" --count 30
aitoearn engage follow --followers-of "目标用户" --count 50

# AI智能回复
aitoearn engage reply --setup --mode intelligent
aitoearn engage reply --post "内容ID" --auto-reply true

# 互动统计
aitoearn engage stats --period 7d --platform douyin
aitoearn engage stats --all --period 30d
```

### API调用示例

```bash
# 自动点赞
curl -X POST https://api.aitoearn.cn/v1/engage/like \
  -H "x-api-key: YOUR_KEY" \
  -d '{
    "platform": "douyin",
    "targetId": "content-id",
    "count": 50
  }'

# 自动评论
curl -X POST https://api.aitoearn.cn/v1/engage/comment \
  -H "x-api-key: YOUR_KEY" \
  -d '{
    "platform": "xiaohongshu",
    "contentId": "post-id",
    "commentText": "写的真好！",
    "aiGenerate": true
  }'

# AI智能回复设置
curl -X POST https://api.aitoearn.cn/v1/engage/reply/setup \
  -H "x-api-key: YOUR_KEY" \
  -d '{
    "platform": "douyin",
    "mode": "intelligent",
    "replyTemplate": "感谢关注！",
    "keywords": ["谢谢", "喜欢", "关注"]
  }'
```

### 与天龙引擎协同

| 天龙岗位 | 协同方式 |
|---------|---------|
| **35-02 社媒运营** | 互动执行 + 内容运营 |
| **38-02 销售管理** | 粉丝增长 + 客户关系 |
| **32-01 市场研究** | 竞品互动分析 |
| **40-01 用户增长** | 自动化涨粉策略 |

### 互动策略矩阵

| 操作 | 适用场景 | 频率建议 |
|------|---------|---------|
| **自动点赞** | 目标用户/竞品粉丝 | 50-100/天 |
| **自动评论** | 热门内容/话题 | 20-50/天 |
| **自动关注** | 竞品粉丝/KOL关注者 | 30-50/天 |
| **AI智能回复** | 粉丝评论 | 全自动 |

### 安全配置

| 配置项 | 说明 | 建议值 |
|--------|------|-------|
| **每日限制** | 单日操作上限 | 100-200 |
| **间隔时间** | 操作间隔 | 5-30秒 |
| **冷却期** | 连续操作后休息 | 30-60分钟 |
| **智能过滤** | 过滤敏感内容 | 必须开启 |

### 注意事项

1. **平台限制**：各平台对自动化操作有不同限制
2. **频率控制**：避免高频操作触发风控
3. **内容合规**：评论内容需符合平台规范
4. **账号安全**：建议使用小号进行自动化操作

### 版本信息

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-15 | 初始集成 |

### 文件结构

```
aitoearn-engage/
├── SKILL.md              # 本文件
├── scripts/
│   ├── engage.sh         # 互动CLI
│   └── reply.sh          # AI回复配置
└── templates/
    └── comment-templates.md  # 评论模板库