---
license: UNKNOWN
triggers: ["yt dlp subtitle", "yt-dlp-subtitle — 视频字幕下载技能"]
---
# yt-dlp-subtitle — 视频字幕下载技能

## L0: 一句话描述
使用 yt-dlp 下载视频字幕（支持 1000+ 平台）

## L1: 使用场景

**适用场景**：
- 下载 YouTube/B站等平台的字幕
- 批量提取课程视频字幕用于笔记
- 将字幕转换为 SRT/VTT 格式
- 提取字幕用于 AI 分析

**触发条件**：
- 用户提供视频 URL 并要求下载字幕
- 用户指定字幕语言和格式
- 用户要求列出可用字幕

**不适用**：
- 无 ffmpeg 环境时格式转换受限
- 需要登录的付费内容

## L2: 详细文档

### 安装

```bash
# 安装 yt-dlp 和 ffmpeg
pip install yt-dlp

# Windows: 下载 yt-dlp.exe
# macOS: brew install yt-dlp
# Linux: sudo apt install ffmpeg
```

### 核心功能矩阵

| 功能 | 命令 | 输出格式 |
|------|------|---------|
| 列出字幕 | `--list-subs` | JSON/表格 |
| 下载字幕 | `--write-subs` | srt/ass/vtt/lrc |
| 自动字幕 | `--write-auto-subs` | srt/ass/vtt |
| 嵌入视频 | `--embed-subs` | mp4/webm/mkv |
| 格式转换 | `--convert-subs` | srt/vtt/ass/lrc |

### CLI 使用

```bash
# 列出所有可用字幕
yt-dlp --list-subs "VIDEO_URL"

# 下载指定语言字幕（支持多语言）
yt-dlp --write-subs --sub-langs "en,zh" "VIDEO_URL"

# 下载所有字幕
yt-dlp --write-subs --sub-langs "all" "VIDEO_URL"

# 下载并转换格式为 SRT
yt-dlp --write-subs --sub-langs "en" --convert-subs srt "VIDEO_URL"

# 嵌入字幕到视频
yt-dlp --embed-subs --sub-langs "zh" "VIDEO_URL"

# 排除实时字幕
yt-dlp --write-subs --sub-langs "all,-live_chat" "VIDEO_URL"
```

### Python API 使用

```python
import yt_dlp

# 下载字幕
ydl_opts = {
    'write_subs': True,
    'sub_langs': 'en,zh',
    'outtmpl': '%(title)s.%(ext)s',
}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download(['VIDEO_URL'])

# 仅提取信息（含字幕列表）
with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
    info = ydl.extract_info('VIDEO_URL', download=False)
    print(f"字幕: {info.get('subtitles', {})}")
    print(f"自动字幕: {info.get('automatic_captions', {})}")
```

### 字幕格式说明

| 格式 | 说明 | 兼容性 |
|------|------|--------|
| srt | SubRip 字幕，最通用 | 播放器全支持 |
| vtt | WebVTT，Web 专用 | 浏览器原生 |
| ass | ASS 高级字幕，支持样式 | 播放器全支持 |
| lrc | LRC 歌词，时间轴歌词 | 音乐播放器 |

### 支持平台（部分）

| 平台 | 字幕支持 | 命令示例 |
|------|---------|---------|
| YouTube | ✅ 手动+自动 | `--sub-langs "en,zh"` |
| Bilibili | ✅ 手动+自动 | `--sub-langs "zh"` |
| Coursera | ✅ | `--sub-langs "en"` |
| TED | ✅ | `--sub-langs "en"` |
| Vimeo | ✅ 部分 | `--sub-langs "en"` |

### 典型工作流

```
1. 用户提供视频 URL
2. 列出可用字幕 → 用户选择语言
3. 下载字幕文件
4. 转换为目标格式（如需要）
5. 返回字幕文件路径或内容
```

## 脚本

### Python CLI 封装

```python
# scripts/yt_dlp_subtitle.py
import yt_dlp
import argparse
import json
import sys

def list_subs(url):
    """列出可用字幕"""
    ydl_opts = {'quiet': True, 'skip_download': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        subs = info.get('subtitles', {})
        auto_subs = info.get('automatic_captions', {})
        return {'manual': subs, 'auto': auto_subs, 'title': info.get('title')}

def download_subs(url, langs='en', format='srt', output_dir='.'):
    """下载字幕"""
    ydl_opts = {
        'write_subs': True,
        'sub_langs': langs,
        'convert_subs': format,
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--langs', default='en,zh')
    parser.add_argument('--format', default='srt')
    parser.add_argument('--output', default='.')
    args = parser.parse_args()

    if args.list:
        print(json.dumps(list_subs(args.url), indent=2))
    else:
        download_subs(args.url, args.langs, args.format, args.output)
```

## 天龙九部集成

| 岗位 | 集成方式 |
|------|---------|
| 01调研师 | 字幕采集→内容分析 |
| 07记录师 | 字幕→NotebookLM知识库 |
| 35-02社媒运营 | 视频字幕提取→内容创作 |
