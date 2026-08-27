---
license: UNKNOWN
triggers: ["aitoearn publish", "AiToEarn Publish Skill"]
---
# AiToEarn Publish Skill

## L0 一句话描述（≤15字）
> AI一键多平台内容分发+日历排期自动化

## L1 使用场景（50-100字）
适用于创作者、品牌方需要将同一内容高效分发到多个社交平台的场景。支持14+主流平台一键发布，内置内容适配引擎和日历排期功能，实现跨平台内容运营自动化。

## L2 详细文档

### 核心能力

| 功能 | 说明 | 特点 |
|------|------|------|
| **一键分发** | 单次操作多平台发布 | 14+平台 |
| **内容适配** | 自动适配各平台格式 | AI驱动 |
| **日历排期** | 内容发布计划管理 | 自动化 |
| **草稿管理** | 内容草稿存储编辑 | 本地+云端 |
| **批量发布** | 批量内容定时发布 | 队列管理 |

### 支持平台

| 中国平台 | 海外平台 | 格式支持 |
|----------|----------|----------|
| 抖音 | TikTok | 视频/图文 |
| 小红书 | YouTube | 视频/图文/文章 |
| 快手 | Facebook | 视频/图文 |
| B站 | Instagram | 视频/图文 |
| 视频号 | Threads | 视频/图文 |
| 微信公众号 | X/Twitter | 文章/图文 |
| - | Pinterest | 图文 |
| - | LinkedIn | 文章/图文 |

### 配置

```bash
# 环境配置
export AITOERN_API_KEY="your-key"
export AITOERN_ENV="cn"  # cn=中国版, ai=国际版

# 初始化
aitoearn publish init --platforms douyin,xiaohongshu,tiktok

# OAuth授权
aitoearn publish auth --platform douyin
aitoearn publish auth --platform xiaohongshu --relay
```

### 核心命令

```bash
# 单平台发布
aitoearn publish --platform douyin --content "视频路径" --title "标题"

# 多平台分发
aitoearn publish --platforms "douyin,xiaohongshu,tiktok" --content "视频路径"

# 日历排期
aitoearn schedule --add --platform douyin --time "2026-05-20 10:00"
aitoearn schedule --list --platform all
aitoearn schedule --edit "schedule-id" --time "2026-05-21 14:00"

# 草稿管理
aitoearn draft list
aitoearn draft create --platform douyin --title "标题"
aitoearn draft publish "draft-id" --platform douyin

# 批量发布
aitoearn batch --file content-list.csv --platforms "douyin,xiaohongshu"
aitoearn batch --queue --status
```

### API调用示例

```bash
# 单平台发布
curl -X POST https://api.aitoearn.cn/v1/publish \
  -H "x-api-key: YOUR_KEY" \
  -d '{
    "platform": "douyin",
    "contentType": "video",
    "filePath": "/path/to/video.mp4",
    "title": "视频标题",
    "description": "视频描述",
    "tags": ["标签1", "标签2"]
  }'

# 多平台分发
curl -X POST https://api.aitoearn.cn/v1/publish/batch \
  -H "x-api-key: YOUR_KEY" \
  -d '{
    "platforms": ["douyin", "xiaohongshu", "tiktok"],
    "contentType": "video",
    "filePath": "/path/to/video.mp4",
    "titles": {
      "douyin": "抖音标题",
      "xiaohongshu": "小红书标题",
      "tiktok": "TikTok标题"
    }
  }'

# 日历排期
curl -X POST https://api.aitoearn.cn/v1/schedule \
  -H "x-api-key: YOUR_KEY" \
  -d '{
    "platform": "douyin",
    "contentPath": "/path/to/content",
    "publishTime": "2026-05-20T10:00:00Z",
    "timezone": "Asia/Shanghai"
  }'
```

### 内容适配规则

| 平台 | 视频时长 | 图片尺寸 | 标题长度 |
|------|---------|----------|----------|
| 抖音 | 15s-10min | 9:16 | ≤20字 |
| 小红书 | 1min-10min | 3:4 | ≤30字 |
| TikTok | 15s-10min | 9:16 | ≤100字 |
| Instagram | 1min-60min | 1:1/4:5/9:16 | ≤220字 |

### 日历排期功能

```bash
# 创建排期
aitoearn schedule create \
  --platform douyin \
  --content "/path/to/video.mp4" \
  --time "2026-05-20 10:00:00" \
  --repeat "weekly"

# 查看排期
aitoearn schedule list --calendar --month 2026-05

# 编辑排期
aitoearn schedule edit 123 --time "2026-05-21 14:00:00"

# 取消排期
aitoearn schedule cancel 123
```

### 与天龙引擎协同

| 天龙岗位 | 协同方式 |
|---------|---------|
| **35-02 社媒运营** | 内容分发执行 + 排期管理 |
| **28-01 文案策划** | 内容创作 + 多平台适配 |
| **50-01 产品策划** | 产品发布自动化 |
| **08 发布师** | 发布流程编排 |

### 发布前检查清单

| 检查项 | 说明 | 优先级 |
|--------|------|--------|
| 平台授权 | OAuth授权是否有效 | P0 |
| 内容格式 | 文件格式/尺寸是否符合要求 | P0 |
| 标题合规 | 是否违反平台规则 | P1 |
| 标签合规 | 标签是否敏感 | P1 |
| 发布时间 | 是否在最佳时段 | P2 |

### 注意事项

1. **OAuth授权**：首次使用需要授权各平台账号
2. **Relay模式**：可借用官方OAuth凭据简化配置
3. **发布限制**：各平台每日发布数量有限制
4. **内容重复**：同一内容多平台发布可能触发审核

### 版本信息

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-15 | 初始集成 |

### 文件结构

```
aitoearn-publish/
├── SKILL.md              # 本文件
├── scripts/
│   ├── publish.sh        # 发布CLI
│   └── schedule.sh       # 排期CLI
└── templates/
    └── platform-specs.md # 平台规格参考