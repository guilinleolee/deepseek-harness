---
github_repo: runesleo/x-reader.git
github_hash: f7ac0fe08ad9104ddbd12f907fce9b702f17900f
last_updated: 2026-04-25
source_type: derived
triggers: ["x reader", "x-reader - Universal Content Reader"]
---
# x-reader - Universal Content Reader

> Universal content reader — fetch, transcribe, and digest content from 7+ platforms.

---

## 触发词

`抓取内容`、`读取URL`、`视频字幕`、`公众号文章`、`B站视频`、`小红书笔记`、`YouTube字幕`

---

## 支持的平台

| 平台 | 文本抓取 | 视频转录 | 使用场景 |
|------|---------|---------|---------|
| **微信公众号** | ✅ Jina → Playwright | - | 技术文章、行业资讯 |
| **B站** | ✅ API | ✅ 字幕提取 | 技术视频、教程 |
| **小红书** | ✅ Jina → Playwright | - | 产品测评、用户反馈 |
| **X/Twitter** | ✅ Jina → Playwright | - | 技术动态、行业趋势 |
| **YouTube** | ✅ Jina | ✅ yt-dlp + Whisper | 技术演讲、教程 |
| **Telegram** | ✅ Telethon | - | 技术社区、资讯频道 |
| **RSS** | ✅ feedparser | - | 技术博客、新闻源 |
| **小宇宙** | - | ✅ Whisper | 播客内容 |
| **Apple Podcasts** | - | ✅ Whisper | 播客内容 |

---

## MCP 工具

### read_url

读取任意 URL 内容，返回结构化结果。

```bash
mcp__x-reader__read_url(url="https://mp.weixin.qq.com/s/abc123")
```

**返回字段**：
- `title` - 标题
- `content` - 正文内容
- `url` - 原始链接
- `source_type` - 来源类型（wechat/bilibili/youtube/...）
- `source_name` - 来源名称
- `media_type` - 媒体类型（text/video/audio）
- `fetched_at` - 抓取时间

### read_batch

批量读取多个 URL，并发执行。

```bash
mcp__x-reader__read_batch(urls=[
  "https://url1.com",
  "https://url2.com",
  "https://url3.com"
])
```

### detect_platform

检测 URL 所属平台。

```bash
mcp__x-reader__detect_platform(url="https://www.bilibili.com/video/xxx")
# 返回: "bilibili"
```

### list_inbox

查看已抓取的内容收件箱。

```bash
mcp__x-reader__list_inbox()
```

---

## 使用示例

### 场景1：技术文章调研

```yaml
任务: 调研 React 19 新特性
步骤:
  1. mcp__x-reader__read_url(url="https://react.dev/blog/...")
  2. mcp__x-reader__read_batch(urls=[相关文章列表])
  3. 整理成调研报告
```

### 场景2：视频内容分析

```yaml
任务: 分析 B站 技术教程
步骤:
  1. mcp__x-reader__read_url(url="https://www.bilibili.com/video/xxx")
  2. 自动提取字幕内容
  3. 整理成学习笔记
```

### 场景3：竞品内容监控

```yaml
任务: 监控竞品公众号更新
步骤:
  1. mcp__x-reader__read_batch(urls=[竞品文章列表])
  2. 对比分析内容差异
  3. 生成竞品动态报告
```

---

## 配置

### 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| `GROQ_API_KEY` | 可选 | Whisper 转录 API 密钥（视频转录需要） |
| `TG_API_ID` | 可选 | Telegram API ID |
| `TG_API_HASH` | 可选 | Telegram API Hash |

### MCP 配置

已配置在 `~/.claude/mcp_settings.json`：

```json
{
  "mcpServers": {
    "x-reader": {
      "command": "python",
      "args": ["C:\\Users\\li\\.claude\\skills\\x-reader\\mcp_server.py"],
      "env": {
        "GROQ_API_KEY": "${GROQ_API_KEY}"
      }
    }
  }
}
```

---

## 关联 Agent

- **01调研师** - 代码考古、技术调研
- **32-01市场研究** - 竞品分析、市场调研
- **35-05短视频编导** - 视频分析、脚本提取
- **35-04内容运营** - 内容监控、竞品追踪
- **00分析师** - 多源信息聚合、需求分析

---

## 安装

```bash
# 安装 Python 包
pip install git+https://github.com/runesleo/x-reader.git

# 安装完整依赖（含浏览器、MCP）
pip install "x-reader[all] @ git+https://github.com/runesleo/x-reader.git"
playwright install chromium
```

---

## 来源

- GitHub: https://github.com/runesleo/x-reader
- 作者: @runes_leo
- 许可证: MIT

---

**版本**: v0.2.0
**最后更新**: 2026-03-03