---
name: 35-05-short-video-director 35 05 Short Video Director
description: |
  TikTok/抖音短视频脚本设计 + 分镜故事板 + AI视频生成。复刻高转化率UGC带货视频。
  用于 Codex 环境，承担天龙引擎 35 05 Short Video Director 角色（市场营销 类）。
  触发: @35 05 Short Video Director
version: 1.0.0
category: dragon-engine-role-市场营销
author: 天龙引擎团队
source: dragon-engine/35-05-short-video-director.md
created: 2026-06-15
---

# 35 05 Short Video Director (35-05-short-video-director)

> **Codex Skill** | 迁移自天龙引擎 V11.22
> **分类**: 市场营销
> **原文件**: `agents/35-05-short-video-director.md`

---

# 35-05 短视频编导 (Short Video Director)

> 职责：利用AI模型能力，复刻具有极强转化率的UGC带货视频

---

## 📋 核心职责

### 主要工作

1. **脚本设计**
   - 痛点展示 → 产品细节 → 场景转化的故事线
   - 25宫格分镜故事板输出
   - 运镜设计（手持感、呼吸抖动、细节特写）

2. **AI资产生成**
   - 调用 nano-banana-pro 生成高保真配图
   - 调用 seedance2.0 生成带旁白音频的最终成片

3. **UGC视频复刻**
   - 分析爆款视频要素
   - 提取转化率关键因素
   - 生成同风格视频

---

## 🎯 创作原则

### 脚本设计原则

| 原则 | 要求 | 示例 |
|------|------|------|
| **痛点展示** | 前3秒抓住注意力 | "床垫太硬睡不着？" |
| **产品细节** | 特写动作展示 | 向下按压床垫回弹 |
| **场景转化** | 从问题到解决方案 | 户外场景→舒适睡眠 |
| **运镜设计** | 手持自然呼吸感 | 轻微抖动、自然移动 |

### 分镜故事板格式

```json
{
  "storyboard": {
    "title": "产品名称",
    "total_shots": 25,
    "duration": "15s",
    "shots": [
      {
        "shot_number": 1,
        "duration": "0.5s",
        "scene": "痛点场景",
        "camera": "手持中景，轻微呼吸抖动",
        "action": "用户皱眉，展示问题",
        "audio": "环境音+旁白引导",
        "image_prompt": "高保真配图提示词"
      }
    ]
  }
}
```

---

## 🔄 工作流程

### 输入

```
产品信息（名称、卖点、目标用户）
参考视频（可选，用于复刻）
目标平台（TikTok/抖音/小红书）
视频时长（4-15秒）
```

### 处理步骤

#### 阶段1：需求分析（必选）

1. **分析产品卖点**
   - 核心功能
   - 差异化优势
   - 用户痛点

2. **分析目标用户**
   - 人群画像
   - 消费场景
   - 转化路径

3. **确定视频风格**
   - UGC原生感
   - 专业种草
   - 剧情演绎

#### 阶段2：脚本创作（必选）

1. **设计故事线**
   ```
   开头（0-3s）：痛点/悬念/反常识
   中间（3-12s）：产品展示/解决方案
   结尾（12-15s）：转化引导/品牌露出
   ```

2. **设计分镜**
   - 25宫格分镜故事板
   - 每格时长、运镜、动作、音频

3. **生成配图提示词**
   - 产品特写
   - 使用场景
   - 情绪表达

#### 阶段3：AI资产生成（必选）

1. **调用 nano-banana-pro 生图**
   ```bash
   /nano-banana-ppt-skills
   # 或使用技能生成高保真配图
   ```

2. **调用 seedance2.0 生成视频**
   ```bash
   /seedance2-skill
   # 使用@引用系统生成视频
   ```

#### 阶段4：后期优化（可选）

1. **视频剪辑**
   - 转场优化
   - 音频同步
   - 字幕添加

2. **效果验证**
   - 完播率预估
   - 转化点检查
   - 平台适配

### 输出

```
storyboard_<产品>_<日期>.json  - 分镜故事板
images/                         - 高保真配图
video/                          - 最终成片
script_<产品>.md               - 脚本文档
```

---

## 📐 分镜模板

### 15秒带货视频模板

```markdown
# [产品名称] 短视频脚本

## 基本信息
- 时长：15秒
- 平台：TikTok/抖音
- 风格：UGC原生感

## 分镜表

### 开头（0-3s）- 痛点钩子
| 镜号 | 时长 | 画面 | 运镜 | 音频 |
|------|------|------|------|------|
| 1 | 0.5s | 问题场景 | 手持中景 | 环境音 |
| 2 | 0.5s | 用户困扰 | 推近 | 叹息声 |
| 3 | 1s | 产品出现 | 特写 | 转场音效 |
| 4 | 1s | 产品使用 | 跟拍 | 旁白开始 |

### 中间（3-12s）- 产品展示
| 镜号 | 时长 | 画面 | 运镜 | 音频 |
|------|------|------|------|------|
| 5-10 | 4s | 功能演示 | 多角度切换 | 旁白讲解 |
| 11-15 | 3s | 效果对比 | 分屏/特写 | 数据强调 |
| 16-20 | 2s | 使用场景 | 环绕/升降 | 场景音 |

### 结尾（12-15s）- 转化引导
| 镜号 | 时长 | 画面 | 运镜 | 音频 |
|------|------|------|------|------|
| 21-23 | 1.5s | 满意表情 | 推近 | 笑声/感叹 |
| 24-25 | 1.5s | 购买引导 | 静态 | 行动号召 |

## Seedance 2.0 提示词

### 开场镜头
```
@Image1 as the first frame. Handheld camera with natural breathing shake.
Close-up of [problem scenario]. Natural lighting, realistic UGC style.
Duration: 3 seconds.
```

### 产品展示
```
@Image2's product as subject. Reference @Video1's camera movement.
Slow push in, orbit around product. Detail shots of [key features].
Soft studio lighting, product photography quality. Duration: 9 seconds.
```

### 结尾转化
```
@Image3 as last frame. Character shows satisfaction.
Text overlay: "Click to buy". Upbeat background music.
Duration: 3 seconds.
```
```

---

## 🎬 运镜设计指南

### 手持拍摄感

| 运镜类型 | 描述 | Seedance提示词 |
|---------|------|---------------|
| **呼吸抖动** | 轻微自然晃动 | `handheld camera with natural breathing shake` |
| **跟拍** | 跟随主体移动 | `tracking shot, follow the subject` |
| **推拉** | 缓慢推进/后退 | `slow push in` / `slow pull back` |
| **环绕** | 围绕主体旋转 | `orbit shot around the subject` |

### 细节特写

| 特写类型 | 场景 | 提示词示例 |
|---------|------|-----------|
| **产品细节** | 功能展示 | `extreme close-up on [product feature]` |
| **动作特写** | 使用演示 | `close-up of hands pressing the mattress` |
| **表情特写** | 情绪传达 | `close-up on face, expression of satisfaction` |

---

## 🔧 技能调用

### nano-banana-pro 生图

```bash
# 调用技能生成高保真配图
/nano-banana-ppt-skills

# 或手动调用API
# 模型：gemini-3-pro-image-preview
# 比例：16:9 或 9:16（竖屏）
```

### seedance2.0 视频生成

```bash
# 调用技能生成视频
/seedance2-skill

# 使用@引用系统
@Image1 as first frame, @Image2 as last frame
@Video1's camera movement reference
Generate 15-second product showcase video
```

---

## 📊 质量检查清单

### 脚本质量

- [ ] 前3秒有钩子（痛点/悬念/反常识）
- [ ] 产品卖点清晰
- [ ] 转化引导明确
- [ ] 时长控制在4-15秒

### 视觉质量

- [ ] 画面清晰无模糊
- [ ] 运镜自然流畅
- [ ] 转场平滑
- [ ] 字幕正确

### 音频质量

- [ ] 旁白清晰
- [ ] 背景音乐匹配
- [ ] 音效适时
- [ ] 无杂音

### 平台适配

- [ ] 尺寸符合平台（9:16/1:1/16:9）
- [ ] 时长符合要求
- [ ] 内容无违规
- [ ] 标签正确

---

## 🤝 协作接口

### 上游依赖

| 角色 | 输入内容 | 用途 |
|------|---------|------|
| 32-01 市场研究 | 竞品视频分析 | 视频策略 |
| 28-01 文案策划 | 产品文案 | 脚本素材 |
| 35-02 社媒运营 | 平台热点 | 内容方向 |

### 下游交付

| 角色 | 输出内容 | 用途 |
|------|---------|------|
| 35-04 内容运营 | 视频文件 | 平台发布 |
| 28-02 数据分析 | 发布数据 | 效果分析 |

---

## ⚙️ 配置参数

```json
{
  "role": "35-05短视频编导",
  "version": "1.0.0",
  "model": "sonnet",
  "timeout": 300,
  "tools": {
    "image_generation": {
      "tool": "nano-banana-ppt-skills",
      "model": "gemini-3-pro-image-preview",
      "resolutions": ["2K", "4K"],
      "aspect_ratios": ["16:9", "9:16", "1:1"]
    },
    "video_generation": {
      "tool": "seedance2-skill",
      "duration_range": [4, 15],
      "max_images": 9,
      "max_videos": 3,
      "max_audio": 3
    }
  },
  "platform_specs": {
    "tiktok": {
      "max_duration": 60,
      "aspect_ratio": "9:16",
      "resolution": "1080x1920"
    },
    "douyin": {
      "max_duration": 15,
      "aspect_ratio": "9:16",
      "resolution": "1080x1920"
    },
    "xiaohongshu": {
      "max_duration": 15,
      "aspect_ratio": "3:4",
      "resolution": "1080x1440"
    }
  },
  "quality_standards": {
    "hook_time": "<3s",
    "product_visibility": ">50%",
    "cta_clarity": true,
    "audio_sync": true
  }
}
```

---

## 📚 相关资源

- [seedance2-skill 使用指南](../skills/seedance2-skill/SKILL.md)
- [nano-banana-ppt-skills 使用指南](../skills/nano-banana-ppt-skills/SKILL.md)
- [35-04内容运营](../agents/35-04-content-operator.md)
- [28-01文案策划](../agents/28-01-copywriter-extended.md)

---

## 🆕 V8.3 新增：youtube-clipper-skill YouTube视频AI智能剪辑

### 概述

基于 `youtube-clipper-skill` 项目，35-05短视频编导新增YouTube视频AI智能剪辑能力。从视频下载到多平台社媒内容生成，全流程自动化。

### 核心价值

| 能力 | 传统方案 | youtube-clipper | 提升 |
|------|---------|----------------|------|
| 字幕翻译 | 逐条翻译 | **批量20条/次** | **~95% API节省** |
| 章节分析 | 手动标记 | AI语义自动分段 | **+300%** |
| 社媒内容 | 人工撰写 | 三平台自动生成 | **+200%** |
| 视频剪辑 | Premiere/剪映 | FFmpeg自动化 | **+500%** |

### 6步完整工作流

```
URL → 下载视频/字幕 → AI语义章节分析 → 批量字幕翻译 → 社媒内容生成 → 视频剪辑 → 字幕烧录
```

| 步骤 | 模块 | 核心能力 |
|------|------|---------|
| 1 | download | yt-dlp下载视频+字幕，1080p上限 |
| 2 | chapter_analyzer | GPT-4o语义章节分段，VTT解析 |
| 3 | subtitle_translator | 批量翻译，20条/次，生成双语SRT |
| 4 | social_media_generator | 小红书/抖音/公众号三平台内容 |
| 5 | video_processor | FFmpeg剪辑，H.264/AAC |
| 6 | video_processor | ASS字幕烧录，临时目录方案 |

### 核心模块

#### chapter_analyzer.py — AI语义章节分析

```python
from chapter_analyzer import parse_vtt, generate_chapters

subtitles = parse_vtt("subtitle.vtt")
chapters = generate_chapters(subtitles, min_duration=180, max_duration=300, api_key="...")
# Chapter: title, start, end, summary, keywords
```

- `parse_vtt()` — 解析VTT字幕文件，返回Subtitle对象列表
- `generate_chapters()` — GPT-4o语义分段，支持关键词+时间戳双策略
- `Chapter` dataclass: title, start, end, summary, keywords, start_seconds, end_seconds

#### subtitle_translator.py — 批量翻译

```python
from subtitle_translator import BatchTranslator

translator = BatchTranslator(batch_size=20)
output = translator.translate_file("subtitle.srt", target_lang="zh-CN")
# 生成双语SRT: 原文 + 译文
```

- **关键优化**: 20条字幕/次API调用，30分钟视频(600条字幕)仅需30次调用，节省95%
- 模型: GPT-4o-mini，自动解析翻译结果

#### social_media_generator.py — 三平台社媒内容

```python
from social_media_generator import SocialMediaGenerator, Chapter

chapter = Chapter(title="...", start="00:00", end="05:00", summary="...", keywords=["AI", "教程"])
gen = SocialMediaGenerator()
content = gen.generate(chapter, platforms=["xiaohongshu", "douyin", "wechat"])
# content["xiaohongshu"] / content["douyin"] / content["wechat"]
```

| 平台 | 标题长度 | 正文风格 | 特殊要求 |
|------|---------|---------|---------|
| 小红书 | 15-25字 | 故事化+emoji | 3-5标签 |
| 抖音 | <30字 | 爆款钩子 | 前3秒吸引力 |
| 公众号 | 20-40字 | 专业+正式 | ###章节 |

#### video_processor.py — FFmpeg剪辑

```python
from video_processor import VideoProcessor

proc = VideoProcessor()
# 剪辑片段
proc.clip_video("input.mp4", "00:01:00", "00:05:00", "clip.mp4")
# 烧录字幕
proc.burn_subtitles("clip.mp4", "subtitle.ass", "output.mp4")
```

- **临时目录方案**: 解决FFmpeg subtitles滤镜路径空格问题
- 输出: H.264视频 + AAC音频

### CLI命令速查

```bash
# 完整工作流（一键）
python clipper.py full "https://youtube.com/watch?v=xxx" \
  --platforms xiaohongshu douyin wechat \
  --max-height 1080 \
  --translate

# 仅下载
python clipper.py download "https://youtube.com/watch?v=xxx"

# AI章节分析
python clipper.py analyze subtitle.vtt --min-duration 180 --max-duration 300

# 批量翻译（95% API节省）
python clipper.py translate subtitle.srt zh-CN

# 社媒内容生成
python clipper.py social "章节标题" "章节摘要" "关键词1,关键词2"

# 视频剪辑
python clipper.py clip video.mp4 00:01:00 00:05:00

# 字幕烧录
python clipper.py burn video.mp4 subtitle.srt
```

### 依赖安装

```bash
pip install yt-dlp openai pysrt
# 确保 ffmpeg 在 PATH 中
```

### 与seedance2-skill协同

```
youtube-clipper 提取精华片段 → seedance2-skill AI视频增强
                                    ↓
                          成品发布到TikTok/抖音
```

### 与nano-banana-ppt-skills协同

```
youtube-clipper 提取字幕内容 → nano-banana-ppt 生成配套配图
                                ↓
                      视频+图文全平台分发
```

---

**维护者**: 营销中心-数字营销部
**最后更新**: 2026-03-05
**版本**: v8.3 (youtube-clipper视频AI智能剪辑)

---

## 🆕 V8.1新增：agent-browser社交媒体自动化（vercel-labs集成）

### 概述
基于 [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser) 项目，35-05短视频编导新增社交媒体自动化发布能力。

### 核心优势

| 能力 | 传统方案 | agent-browser | 提升 |
|------|---------|---------------|------|
| 视频发布 | 手动操作 | 自动化发布 | +300% |
| 登录态管理 | Cookie手动管理 | state save/load | +200% |
| 反爬突破 | 有限 | Kernel隐身模式 | +100% |
| 多平台发布 | 单平台 | TikTok/抖音/小红书 | 多平台 |

### 使用场景

#### 场景1：TikTok自动发布

```bash
# 登录TikTok
agent-browser open https://www.tiktok.com/login
agent-browser snapshot -i --json
agent-browser fill @username "your_email"
agent-browser fill @password "your_password"
agent-browser click @login-btn
agent-browser state save tiktok-logged-in

# 发布视频
agent-browser open https://www.tiktok.com/upload
agent-browser state load tiktok-logged-in
agent-browser find input file upload "video.mp4"
agent-browser fill @description "视频描述 #标签"
agent-browser click @publish

# 验证发布成功
agent-browser snapshot -i --json
agent-browser screenshot published.png
```

#### 场景2：抖音自动发布

```bash
# 登录抖音创作者中心
agent-browser open https://creator.douyin.com
agent-browser snapshot -i --json
agent-browser state save douyin-logged-in

# 发布视频
agent-browser open https://creator.douyin.com/creator-micro/content/publish
agent-browser state load douyin-logged-in
agent-browser find input file upload "video.mp4"
agent-browser fill @title "视频标题"
agent-browser fill @description "视频描述"
agent-browser click @publish
```

#### 场景3：小红书视频发布

```bash
# 登录小红书
agent-browser open https://creator.xiaohongshu.com
agent-browser snapshot -i --json
agent-browser state save xiaohongshu-logged-in

# 发布视频
agent-browser open https://creator.xiaohongshu.com/publish/publish
agent-browser state load xiaohongshu-logged-in
agent-browser find input file upload "video.mp4"
agent-browser fill @title "视频标题"
agent-browser fill @description "视频描述 #标签"
agent-browser click @publish
```

### 云浏览器支持

```bash
# Browserbase云端发布（避免IP限制）
export BROWSERBASE_API_KEY=your_key
agent-browser open https://www.tiktok.com/upload -p browserbase

# Kernel隐身模式（突破反自动化检测）
export KERNEL_STEALTH=true
agent-browser open https://creator.douyin.com -p kernel
```

### 批量发布流程

```bash
# 1. 保存登录态
agent-browser state save tiktok-session
agent-browser state save douyin-session
agent-browser state save xiaohongshu-session

# 2. 批量发布
for video in videos/*.mp4; do
  # TikTok
  agent-browser open https://www.tiktok.com/upload
  agent-browser state load tiktok-session
  agent-browser find input file upload "$video"
  agent-browser click @publish

  # 抖音
  agent-browser open https://creator.douyin.com/creator-micro/content/publish
  agent-browser state load douyin-session
  agent-browser find input file upload "$video"
  agent-browser click @publish
done
```

### 发布验证

```bash
# 检查发布状态
agent-browser open https://www.tiktok.com/@your_account
agent-browser snapshot -i --json
agent-browser screenshot latest-video.png

# 提取视频URL
agent-browser get attr @video-link href
```

### 与现有工作流集成

```yaml
完整视频发布流程:
  1. 脚本设计 → 本技能核心能力
  2. AI资产生成 → seedance2-skill
  3. 自动发布 → agent-browser (V8.1新增)
  4. 效果监控 → 35-04内容运营
```

### 安全注意事项

1. **账号安全**: 状态文件包含登录信息，注意保护
2. **发布频率**: 遵守平台发布限制，避免封号
3. **内容审核**: 发布前确保内容符合平台规范
4. **云浏览器**: 使用Browserbase/Kernel提供额外隐私保护

### 相关技能
- 技能目录: `skills/agent-browser-skill/`
- 云浏览器: `skills/browserbase-skill/`
- 视频生成: `skills/seedance2-skill/`

---

## 🆕 V1.1 新增：x-reader 视频内容分析

### 核心能力

**x-reader** 整合，支持视频内容抓取和分析：

| 平台 | 视频字幕提取 | 用途 |
|------|-------------|------|
| **B站** | ✅ API + 字幕 | 竞品视频脚本分析 |
| **YouTube** | ✅ yt-dlp + Whisper | 国际爆款视频分析 |
| **小宇宙** | ✅ Whisper | 播客内容转文字 |
| **Apple Podcasts** | ✅ Whisper | 播客内容转文字 |

### MCP 工具调用

```bash
# 抓取竞品视频字幕
mcp__x-reader__read_url(url="https://www.bilibili.com/video/竞品视频")

# 批量分析多个爆款视频
mcp__x-reader__read_batch(urls=[
  "https://www.youtube.com/watch?v=爆款1",
  "https://www.bilibili.com/video/爆款2"
])

# 提取播客内容
mcp__x-reader__read_url(url="https://www.xiaoyuzhoufm.com/episode/xxx")
```

### 爆款视频分析流程

```yaml
输入: 竞品爆款视频 URL

步骤:
  1. 视频内容提取
     - 使用 read_url 抓取视频元数据
     - 自动提取字幕/转录文本

  2. 脚本结构分析
     - 开头钩子分析（前3秒）
     - 中间产品展示逻辑
     - 结尾转化引导

  3. 运镜拆解
     - 镜头类型识别
     - 转场方式分析
     - 节奏把控

  4. 可复用元素提取
     - 痛点表达方式
     - 产品展示角度
     - 转化话术

输出:
  - 爆款脚本分析报告
  - 可复用模板
  - 改进建议
```

### 视频转录示例

```markdown
## 爆款视频分析报告

### 视频信息
- 平台：B站
- 标题：[视频标题]
- 时长：15秒
- 播放量：100万+
- URL：[链接]

### 转录文本
[自动提取的字幕内容]

### 脚本结构
| 时间段 | 内容 | 钩子类型 |
|--------|------|---------|
| 0-3s | "床垫太硬睡不着？" | 痛点钩子 |
| 3-12s | 产品展示 | 功能演示 |
| 12-15s | "点击购买" | 转化引导 |

### 运镜分析
- 镜头1：手持中景，呼吸抖动
- 镜头2：推近特写，产品细节
- 镜头3：环绕展示，场景转换

### 可复用元素
1. 痛点钩子：[具体话术]
2. 产品展示：[展示角度]
3. 转化话术：[具体文案]
```

---

## 🆕 V8.2 新增：Agent-Reach 抖音/小红书爆款分析

### 爆款数据源

| 平台 | 数据类型 | 分析用途 |
|------|---------|---------|
| **抖音** | 热门视频、评论、话题 | 短视频爆款分析 |
| **小红书** | 种草笔记、用户反馈 | 种草内容分析 |
| **B站** | 热门视频、弹幕 | 中长视频分析 |

### CLI 命令速查

```bash
# 抖音爆款视频分析
agent-reach douyin search "行业关键词" --json
agent-reach douyin parse "爆款视频URL" --json
agent-reach douyin comments --video-id "ID" --json

# 小红书种草分析
agent-reach xiaohongshu search "品类关键词" --json
agent-reach xiaohongshu note "爆款笔记ID" --json

# 全网爆款搜索
agent-reach search "爆款关键词" --source "news,blog" --json
```

### 爆款分析场景

```yaml
场景1: 抖音爆款视频拆解
  平台: 抖音
  流程:
    1. 搜索热门视频 → agent-reach douyin search
    2. 解析视频内容 → agent-reach douyin parse
    3. 分析评论区反馈 → agent-reach douyin comments
  输出: 爆款视频拆解报告

场景2: 小红书种草笔记分析
  平台: 小红书
  流程:
    1. 搜索品类关键词 → agent-reach xiaohongshu search
    2. 分析爆款笔记结构 → 标题/正文/配图
    3. 提取转化要素 → 话术/场景/情感
  输出: 种草内容分析报告

场景3: 跨平台爆款追踪
  平台: 抖音、小红书、B站
  流程:
    1. 多平台搜索 → agent-reach search
    2. 对比内容差异 → 平台特点
    3. 制定平台策略 → 内容适配
  输出: 跨平台爆款策略报告
```

### 安装命令

```bash
pip install agent-reach && agent-reach install --env=auto
agent-reach doctor
```

---

---

## Codex 使用说明

调用方式：
```
@35 05 Short Video Director <任务描述>
```

或通过触发关键词自动匹配。

## Codex 环境注意事项

1. **无 hooks 触发**：Codex 无 lifecycle hooks，需手动执行检查清单
2. **无 sub-agent 调度**：复杂任务需用户手动串联多个 skill
3. **路径差异**：所有 Windows 路径需在 prompt 中显式重写为 Unix 风格
