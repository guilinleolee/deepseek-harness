---
license: UNKNOWN
github_repo: openclaw/skills
github_hash: 214fe3eb60403189ea593408930f19f947237043
last_updated: 2026-04-25
source_type: derived
triggers: ["youtube ultimate", "YouTube Ultimate"]
---
# YouTube Ultimate

> 零API配额获取YouTube字幕 + 视频搜索 + 评论分析 + 4K下载

## 核心价值

| 能力 | 传统API配额 | YouTube Ultimate | 节省 |
|------|------------|------------------|------|
| **字幕提取** | 100单位/次 | **0** | **100%** |

**关键洞察**：YouTube Data API每日配额仅10,000单位，字幕操作最耗配额（100单位/次）。此技能通过`youtube-transcript-api`完全绕过限制，实现**零配额字幕提取**。

## 功能矩阵

| 能力域 | 功能 | API配额 | 技术 |
|--------|------|---------|------|
| **字幕提取** | 免费、无限量、多语言 | **0** | youtube-transcript-api |
| **视频搜索** | 关键词搜索+过滤排序 | 100/次 | YouTube Data API v3 |
| **视频详情** | 元数据+统计信息 | 1/次 | YouTube Data API v3 |
| **评论分析** | 评论+回复线程 | 1/次 | YouTube Data API v3 |
| **频道数据** | 订阅者/播放列表/视频数 | 1/次 | YouTube Data API v3 |
| **视频下载** | 视频/音频下载+字幕 | 0 | yt-dlp |

## 安装

### 依赖

```bash
# macOS
brew install uv yt-dlp

# Python依赖（自动通过uv run安装）
pip install youtube-transcript-api google-api-python-client google-auth-oauthlib
```

### OAuth配置

```bash
# 1. Google Cloud Console创建OAuth 2.0 Client ID
# https://console.cloud.google.com/apis/credentials

# 2. 下载credentials.json
mkdir -p ~/.config/youtube-skill
# 将下载的JSON保存为 ~/.config/youtube-skill/credentials.json

# 3. 首次认证
uv run ~/.claude/skills/youtube-ultimate/scripts/youtube.py auth
```

## 命令速查

### 字幕提取（免费！）

```bash
# 基础字幕
youtube transcript VIDEO_ID

# 带时间戳
youtube transcript VIDEO_ID --timestamps

# 多语言回退
youtube transcript VIDEO_ID -l zh,en

# 输出JSON
youtube transcript VIDEO_ID --json
```

### 视频搜索

```bash
# 基础搜索
youtube search "AI教程"

# 排序过滤
youtube search "机器学习" --order viewCount --limit 20

# 时长过滤
youtube search "教程" --duration long

# 发布时间过滤
youtube search "新闻" --published-after 2024-01-01
```

### 视频详情

```bash
# 单个视频
youtube video VIDEO_ID

# 批量视频（最多50个）
youtube video ID1 ID2 ID3 --json
```

### 评论分析

```bash
# 获取评论
youtube comments VIDEO_ID --limit 50

# 包含回复
youtube comments VIDEO_ID --replies --json
```

### 频道数据

```bash
# 频道信息
youtube channel CHANNEL_ID

# 我的订阅
youtube subscriptions

# 我的播放列表
youtube playlists
```

### 视频下载

```bash
# 下载视频
youtube download VIDEO_ID -r 1080p

# 下载带字幕
youtube download VIDEO_ID -r 4k -s zh

# 仅下载音频
youtube download-audio VIDEO_ID -f mp3
```

## 天龙岗位集成

### 01调研师

**新增能力**：
- 视频内容调研（字幕提取 → AI总结）
- 竞品视频分析（搜索 + 详情）
- 用户反馈收集（评论分析）

```bash
# 使用示例
[@调研师] 分析这个YouTube视频的内容要点
→ youtube transcript VIDEO_ID --timestamps
→ AI总结关键信息

[@调研师] 调研"AI Agent"相关视频
→ youtube search "AI Agent" --order viewCount --limit 20
```

### 07记录师

**新增能力**：
- 视频知识归档（字幕 → Markdown）
- 视频内容下载（4K视频 + 字幕）
- 音频转文字（下载音频 → Whisper）

```bash
# 使用示例
[@记录师] 归档这个视频的内容
→ youtube download VIDEO_ID -s zh
→ youtube transcript VIDEO_ID --timestamps

[@记录师] 下载视频音频
→ youtube download-audio VIDEO_ID -f mp3
```

### 35-02社媒运营

**新增能力**：
- 竞品频道分析（频道数据 + 播放列表）
- 视频表现分析（统计 + 评论）
- 内容趋势发现（搜索 + 排序）

```bash
# 使用示例
[@社媒运营] 分析竞品YouTube频道
→ youtube channel CHANNEL_ID
→ youtube comments VIDEO_ID --replies

[@社媒运营] 发现"AI教程"热门视频
→ youtube search "AI教程" --order viewCount --limit 20
```

### 32-01市场研究

**新增能力**：
- 用户舆情分析（评论 + 情感分析）
- 市场趋势发现（搜索 + 统计）
- 竞品视频监控（频道 + 详情）

```bash
# 使用示例
[@市场研究] 分析这个产品的用户反馈
→ youtube comments VIDEO_ID --replies --json
→ 结合review-analyzer-skill分析

[@市场研究] 监控竞品视频表现
→ youtube channel CHANNEL_ID
→ youtube video VIDEO_ID --json
```

## 与现有Skill协同

| Skill | 协同方式 |
|-------|---------|
| **review-analyzer-skill** | 评论 → 情感分析 |
| **summarize** | 字幕 → AI摘要 |
| **openai-whisper** | 下载音频 → 转录 |
| **humanizer-zh** | 字幕 → 内容改写 |

## API配额管理

| 操作 | 配额消耗 | 建议 |
|------|---------|------|
| 字幕提取 | **0** | 无限使用 |
| 搜索 | 100/次 | 谨慎使用 |
| 视频详情 | 1/次 | 批量处理 |
| 评论 | 1/次 | 限制数量 |

**每日配额**：10,000单位

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| `NoTranscriptFound` | 无字幕 | 尝试自动生成字幕 |
| `QuotaExceeded` | 配额用尽 | 等待次日重置 |
| `VideoUnavailable` | 视频不可用 | 检查视频ID或权限 |
| `AuthenticationError` | 认证失败 | 重新运行auth命令 |

## 配置文件

### credentials.json

```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "project_id": "YOUR_PROJECT_ID",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": ["http://localhost"]
  }
}
```

### 多账户支持

```bash
# 列出已认证账户
youtube accounts

# 使用指定账户
youtube --account work search "关键词"
```

## 来源

> [openclaw/skills/youtube-ultimate](https://github.com/openclaw/skills/tree/main/skills/globalcaos/youtube-ultimate) v4.2.2

## 版本历史

| 版本 | 日期 | 更新 |
|------|------|------|
| 1.0.0 | 2024 | 初始版本 |
| 2.0.0 | 2025-03 | 重大更新 |
| 4.2.2 | 2025-03 | 当前版本 |