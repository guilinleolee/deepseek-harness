---
license: UNKNOWN
github_repo: op7418/Youtube-clipper-skill
github_hash: f31f077ee0905c95a510a6f34bbd0c3c85b15129
triggers: ["youtube clipper skill", "YouTube Clipper Skill - AI智能视频剪辑师"]
---
# YouTube Clipper Skill - AI智能视频剪辑师

## V1.0 核心特性

> 基于 [op7418/Youtube-clipper-skill](https://github.com/op7418/Youtube-clipper-skill) (1.7k Stars, MIT License) 深度集成

### 核心价值
填补天龙引擎在 **YouTube视频AI智能剪辑** 领域的空白，实现：
- AI语义章节分割（非机械时间切分）
- 双语字幕翻译（API调用减少95%）
- 硬字幕烧录（FFmpeg libass）
- 社媒内容自动生成（小红书/抖音/公众号）

## 核心能力矩阵

```
┌─────────────────────────────────────────────────────────────────┐
│              YouTube Clipper 六大核心能力                          │
├─────────────────────────────────────────────────────────────────┤
│  🤖 AI语义分析    - 理解内容语义，识别自然分段                 │
│  ✂️ 精确剪辑      - FFmpeg帧级精确提取                         │
│  🌐 双语字幕      - 批量翻译，API调用减少95%                   │
│  🔥 硬字幕烧录    - 自定义样式，专业输出                       │
│  📝 内容摘要      - AI生成社媒文案                             │
│  📦 批量处理      - 多章节并行，自动化流水线                   │
└─────────────────────────────────────────────────────────────────┘
```

## 系统要求

| 组件 | 要求 | 安装命令 |
|------|------|---------|
| Python | 3.8+ | - |
| yt-dlp | 最新版 | `pip install yt-dlp` |
| FFmpeg (含libass) | ffmpeg-full | `brew install ffmpeg-full` (macOS) |
| 依赖 | yt-dlp, pysrt, openai/deepseek | 见 requirements.txt |

## 六阶段工作流

```
Phase 1: 环境检测 ──▶ Phase 2: 视频下载 ──▶ Phase 3: AI章节分析
     │                      │                      │
     ▼                      ▼                      ▼
 Phase 6: 输出          Phase 5: 处理          Phase 4: 用户选择
 (成品交付)          (剪辑/翻译/烧录)         (选章节/选项)
```

### Phase 1: 环境检测
```bash
# 检查 yt-dlp
yt-dlp --version

# 检查 FFmpeg libass 支持
ffmpeg -filters 2>&1 | grep subtitles

# 或使用 Python 脚本自动检测
python3 ~/.claude/skills/youtube-clipper-skill/scripts/env_check.py
```

### Phase 2: 视频下载
```python
from youtube_clipper import VideoDownloader

downloader = VideoDownloader(output_dir="./youtube-clips")
video_path, subtitle_path = downloader.download("https://youtube.com/watch?v=xxx")
```

### Phase 3: AI章节分析（核心差异化）
```python
from youtube_clipper import ChapterAnalyzer

analyzer = ChapterAnalyzer(model="gpt-4o")
chapters = analyzer.analyze(
    subtitle_path="video.en.vtt",
    min_duration=180,  # 最小章节时长(秒)
    max_duration=300   # 最大章节时长(秒)
)

# 输出示例:
# [
#   {
#     "title": "Claude Code入门教程",
#     "start": "00:00:00",
#     "end": "00:03:45",
#     "summary": "介绍Claude Code的基本概念和安装方法",
#     "keywords": ["Claude Code", "安装", "入门"]
#   },
#   ...
# ]
```

### Phase 4: 用户选择
```python
# 交互式选择
from youtube_clipper import ChapterSelector

selector = ChapterSelector(chapters)
selected = selector.interactive_select()

# 选项:
# - 保留原字幕
# - 生成双语字幕
# - 烧录硬字幕
# - 生成社媒摘要
```

### Phase 5: 处理
```python
from youtube_clipper import VideoProcessor

processor = VideoProcessor(
    ffmpeg_path="/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg",  # macOS
    output_dir="./youtube-clips/output"
)

for chapter in selected:
    # 1. 剪辑视频
    clip_path = processor.clip_video(video_path, chapter)

    # 2. 提取字幕段
    subtitle_segment = processor.extract_subtitle(
        subtitle_path,
        chapter["start"],
        chapter["end"]
    )

    # 3. 批量翻译 (20条/批，节省95% API)
    translator = BatchTranslator(batch_size=20)
    bilingual_srt = translator.translate(subtitle_segment, target_lang="zh-CN")

    # 4. 烧录硬字幕
    final_video = processor.burn_subtitles(clip_path, bilingual_srt)

    # 5. 生成社媒文案
    from youtube_clipper import SocialMediaGenerator
    generator = SocialMediaGenerator()
    content = generator.generate(
        chapter=chapter,
        platforms=["xiaohongshu", "douyin", "wechat"]
    )
```

### Phase 6: 输出
```
./youtube-clips/2026-04-14_143022/
├── Chapter_1_Claude_Code入门/
│   ├── Chapter_1_clip.mp4              # 原片剪辑
│   ├── Chapter_1_with_subtitles.mp4   # 烧录字幕版
│   ├── Chapter_1_bilingual.srt        # 双语字幕
│   └── Chapter_1_summary.md           # 社媒文案
├── Chapter_2_进阶技巧/
│   └── ...
```

## 技术亮点

### 1. FFmpeg路径空格处理
```python
import tempfile
import shutil

def process_with_temp_dir(video_path, subtitle_path):
    """FFmpeg无法处理含空格的路径，使用temp目录workaround"""
    temp_dir = tempfile.mkdtemp()
    try:
        temp_video = shutil.copy(video_path, temp_dir)
        temp_subtitle = shutil.copy(subtitle_path, temp_dir)
        # FFmpeg处理...
        result = ffmpeg_process(temp_video, temp_subtitle)
        # 移回原目录
        return result
    finally:
        shutil.rmtree(temp_dir)
```

### 2. 批量翻译优化（节省95% API）
```python
class BatchTranslator:
    """
    批量翻译策略：20条字幕/次
    - 30分钟视频 ≈ 600条字幕
    - 串行翻译: 600次API调用
    - 批量翻译: 30次API调用 (95%节省)
    """
    def __init__(self, batch_size=20):
        self.batch_size = batch_size

    def translate_batch(self, subtitles: list[Subtitle]) -> list[Subtitle]:
        # 将字幕分组
        batches = self._create_batches(subtitles)
        results = []
        for batch in batches:
            # 单次API调用翻译20条
            translated = self._translate_single_call(batch)
            results.extend(translated)
        return results
```

### 3. AI语义章节分割算法
```python
def semantic_chapter_split(subtitles: list[Subtitle]) -> list[Chapter]:
    """
    非机械时间切分，AI理解内容语义：
    1. 解析字幕文本，识别话题关键词
    2. 检测语义转折点（话题切换）
    3. 合并相似内容片段
    4. 生成章节标题和摘要
    """
    # 话题聚类
    topics = cluster_topics(subtitles)

    chapters = []
    for topic in topics:
        # 识别自然分段
        if topic.duration >= MIN_CHAPTER_DURATION:
            chapters.append(Chapter(
                title=generate_title(topic),
                start=topic.start,
                end=topic.end,
                summary=generate_summary(topic),
                keywords=extract_keywords(topic)
            ))

    return chapters
```

### 4. VTT到SRT转换
```python
def vtt_to_srt(vtt_content: str) -> str:
    """
    VTT格式:
    WEBVTT

    00:00:00.000 --> 00:00:02.000
    Hello, world!

    SRT格式:
    1
    00:00:00,000 --> 00:00:02,000
    Hello, world!
    """
    lines = vtt_content.strip().split('\n')
    srt_lines = []
    counter = 1

    for line in lines:
        # 跳过WEBVTT头
        if line.startswith('WEBVTT'):
            continue
        # 跳过空行
        if not line.strip():
            continue
        # 时间行转换 (点号→逗号)
        if '-->' in line:
            line = line.replace('.', ',')
            srt_lines.append(str(counter))
            srt_lines.append(line)
            counter += 1
        else:
            srt_lines.append(line)

    return '\n'.join(srt_lines)
```

## 天龙岗位升级

| 岗位 | 版本 | 新增能力 | 提升 |
|------|------|---------|------|
| **35-05 短视频编导** | V1.1 | YouTube视频AI智能剪辑 | ⭐⭐⭐⭐⭐ |
| **07记录师** | V8.86 | YouTube内容→知识库归档 | ⭐⭐⭐⭐ |
| **35-02社媒运营** | V12.4 | YouTube内容→社媒文案自动生成 | ⭐⭐⭐⭐⭐ |

## 核心命令速查

```bash
# 环境检测
python3 ~/.claude/skills/youtube-clipper-skill/scripts/env_check.py

# 下载并分析视频
python3 ~/.claude/skills/youtube-clipper-skill/scripts/clipper.py "https://youtube.com/watch?v=xxx"

# 仅下载视频
python3 ~/.claude/skills/youtube-clipper-skill/scripts/download.py "URL" --no-subtitles

# 仅生成章节
python3 ~/.claude/skills/youtube-clipper-skill/scripts/analyze.py "subtitle.vtt"

# 翻译字幕
python3 ~/.claude/skills/youtube-clipper-skill/scripts/translate.py "subtitle.srt" --target zh-CN

# 烧录字幕
python3 ~/.claude/skills/youtube-clipper-skill/scripts/burn.py "video.mp4" "subtitle.srt"
```

## 与现有天龙技能协同

| 天龙Skill | youtube-clipper | 协同效果 |
|-----------|----------------|---------|
| **summarize** | YouTube视频摘要 | 视频→知识卡片 |
| **xiaohongshu-cli** | 内容发布 | clipper→cli发布闭环 |
| **xiaohu-wechat-format** | 公众号排版 | clipper→format排版闭环 |
| **douyin-video-extractor** | 抖音视频 | YouTube+抖音双平台 |
| **translation** | 批量翻译 | 共享batch翻译优化 |
| **remotion-best-practices** | 视频生成 | clipper素材→Remotion加工 |

## 预期收益

| 指标 | V8.94 | V8.95 | 提升 |
|------|-------|-------|------|
| **YouTube视频剪辑能力** | ❌ 无 | ✅ 完整 | **质的飞跃** |
| **AI语义章节分割** | ❌ 无 | ✅ 完整 | **质的飞跃** |
| **字幕翻译成本** | 100% | **5%** | **-95%** |
| **短视频素材采集效率** | 手动 | **自动化** | **+500%** |
| **社媒内容产能** | 手动 | **AI自动生成** | **+300%** |
| **35-05编导能力** | V1.0 | V1.1 | ⭐⭐⭐⭐⭐ |
| **07记录师能力** | V8.86 | V8.87 | ⭐⭐⭐⭐ |
| **35-02社媒运营** | V12.3 | V12.4 | ⭐⭐⭐⭐⭐ |

## 安装验证

```bash
# 1. 安装依赖
pip install yt-dlp pysrt openai

# 2. 验证 FFmpeg libass
ffmpeg -filters 2>&1 | grep -i subtitles

# 3. 测试脚本
python3 ~/.claude/skills/youtube-clipper-skill/scripts/env_check.py

# 4. 快速测试
python3 ~/.claude/skills/youtube-clipper-skill/scripts/clipper.py "https://youtube.com/watch?v=dQw4w9WgXcQ" --dry-run
```

## 注意事项

1. **FFmpeg libass必须**：macOS需安装 `ffmpeg-full`，标准ffmpeg不含libass
2. **路径空格问题**：FFmpeg subtitles滤镜无法处理含空格的路径，使用temp目录workaround
3. **字幕优先级**：优先使用上传者字幕，次选YouTube自动字幕
4. **API成本**：批量翻译20条/次，大幅节省API调用
5. **版权合规**：仅下载自己有版权或允许下载的YouTube视频

## 技能文件

```
youtube-clipper-skill/
├── SKILL.md                              # 本文件
├── scripts/
│   ├── clipper.py                        # 主入口脚本
│   ├── env_check.py                      # 环境检测
│   ├── download.py                       # 视频下载
│   ├── chapter_analyzer.py               # AI章节分析
│   ├── video_processor.py                # 视频处理
│   ├── subtitle_translator.py            # 批量字幕翻译
│   └── social_media_generator.py         # 社媒内容生成
├── references/
│   ├── ffmpeg-guide.md                  # FFmpeg参考
│   └── ytdlp-guide.md                   # yt-dlp参考
└── requirements.txt                      # Python依赖
```

---

*Last updated: 2026-04-14 | V8.95*
