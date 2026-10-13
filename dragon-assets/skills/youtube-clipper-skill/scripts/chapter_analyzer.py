#!/usr/bin/env python3
"""
AI Chapter Analyzer - 语义章节分析
非机械时间切分，AI理解内容语义生成精细章节
"""

import re
import sys
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Subtitle:
    index: int
    start_time: str  # HH:MM:SS.mmm
    end_time: str
    text: str


@dataclass
class Chapter:
    title: str
    start: str  # HH:MM:SS
    end: str
    summary: str
    keywords: list[str] = field(default_factory=list)
    start_seconds: int = 0
    end_seconds: int = 0


def parse_vtt(vtt_path: str) -> list[Subtitle]:
    """解析VTT字幕文件"""
    subtitles = []
    with open(vtt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 移除WEBVTT头
    content = re.sub(r'^WEBVTT.*?\n', '', content, flags=re.MULTILINE)

    # 分割字幕块
    blocks = re.split(r'\n\n+', content.strip())

    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 2:
            continue

        # 查找时间行
        time_line_idx = 0
        for i, line in enumerate(lines):
            if '-->' in line:
                time_line_idx = i
                break

        if time_line_idx >= len(lines):
            continue

        time_line = lines[time_line_idx]
        times = time_line.split('-->')
        if len(times) != 2:
            continue

        start_time = times[0].strip().replace(',', '.')
        end_time = times[1].strip().split()[0].replace(',', '.')

        # 合并文本行
        text = ' '.join(lines[time_line_idx + 1:]).strip()

        if text:
            subtitles.append(Subtitle(
                index=len(subtitles) + 1,
                start_time=start_time,
                end_time=end_time,
                text=text
            ))

    return subtitles


def time_to_seconds(time_str: str) -> int:
    """将时间字符串转换为秒数"""
    # 支持格式: HH:MM:SS.mmm 或 HH:MM:SS
    match = re.match(r'(\d+):(\d+):([\d.]+)', time_str)
    if match:
        h, m, s = match.groups()
        return int(h) * 3600 + int(m) * 60 + float(s)
    return 0


def generate_chapters(
    subtitles: list[Subtitle],
    min_duration: int = 180,
    max_duration: int = 300,
    llm_api_key: Optional[str] = None
) -> list[Chapter]:
    """
    生成语义章节

    策略:
    1. 如果有LLM API，使用AI语义分析
    2. 否则使用基于关键词的启发式分段

    Args:
        subtitles: 解析后的字幕列表
        min_duration: 最小章节时长(秒)
        max_duration: 最大章节时长(秒)

    Returns:
        章节列表
    """
    if not subtitles:
        return []

    # 准备字幕文本用于分析
    full_text = ' '.join([s.text for s in subtitles])

    # 检测是否使用LLM
    if llm_api_key:
        return generate_chapters_with_llm(subtitles, full_text, min_duration, max_duration, llm_api_key)
    else:
        return generate_chapters_heuristic(subtitles, min_duration, max_duration)


def generate_chapters_with_llm(
    subtitles: list[Subtitle],
    full_text: str,
    min_duration: int,
    max_duration: int,
    api_key: str
) -> list[Chapter]:
    """
    使用LLM进行语义章节分析

    这是YouTube Clipper的核心差异化能力：
    非机械时间切分，而是理解内容语义
    """
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        # 构建提示词
        prompt = f"""Analyze this video transcript and divide it into semantic chapters.

Requirements:
- Each chapter should be {min_duration}-{max_duration} seconds
- Chapters should be based on TOPIC TRANSITIONS, not arbitrary time points
- Each chapter needs: title (in Chinese), summary (1-2 sentences), keywords (3-5)

Transcript:
{full_text[:8000]}

Output format (JSON array):
[
  {{
    "title": "章节标题",
    "start": "00:00:00",
    "end": "00:03:00",
    "summary": "章节摘要",
    "keywords": ["关键词1", "关键词2", "关键词3"]
  }}
]

Remember:
- Focus on semantic topic changes
- Avoid splitting mid-thought
- Ensure natural chapter boundaries"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a video content analyst."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        import json
        result = json.loads(response.choices[0].message.content)

        chapters = []
        for item in result.get("chapters", []):
            start_sec = time_to_seconds(item["start"])
            end_sec = time_to_seconds(item["end"])
            chapters.append(Chapter(
                title=item["title"],
                start=item["start"],
                end=item["end"],
                summary=item["summary"],
                keywords=item.get("keywords", []),
                start_seconds=start_sec,
                end_seconds=end_sec
            ))

        return chapters

    except Exception as e:
        print(f"[WARN] LLM analysis failed: {e}, falling back to heuristic")
        return generate_chapters_heuristic(subtitles, min_duration, max_duration)


def generate_chapters_heuristic(
    subtitles: list[Subtitle],
    min_duration: int = 180,
    max_duration: int = 300
) -> list[Chapter]:
    """
    启发式章节分割（无LLM时使用）

    基于关键词检测和字幕长度进行简单分段
    """
    if not subtitles:
        return []

    chapters = []
    current_chapter = {
        "subtitles": [],
        "start": subtitles[0].start_time
    }

    total_duration = 0
    keywords = set()

    for subtitle in subtitles:
        # 添加关键词
        words = re.findall(r'\b[a-zA-Z]{4,}\b', subtitle.text.lower())
        keywords.update(words)

        current_chapter["subtitles"].append(subtitle)

        # 计算当前章节时长
        start_sec = time_to_seconds(current_chapter["start"])
        end_sec = time_to_seconds(subtitle.end_time)
        duration = end_sec - start_sec

        # 如果达到最小时长，考虑结束当前章节
        if duration >= min_duration:
            # 查找合适的话题切换点
            has_transition = any(kw in subtitle.text.lower() for kw in [
                'next', 'now', 'moving on', 'let\'s', 'first', 'second',
                'finally', 'in conclusion', 'to summarize', 'so far',
                '接下来', '现在', '首先', '其次', '最后', '总结'
            ])

            if duration >= max_duration or (duration >= min_duration and has_transition):
                # 结束当前章节
                text = ' '.join([s.text for s in current_chapter["subtitles"]])

                chapters.append(Chapter(
                    title=generate_title_heuristic(text[:200]),
                    start=current_chapter["start"],
                    end=subtitle.end_time,
                    summary=truncate_text(text, 150),
                    keywords=list(keywords)[:5],
                    start_seconds=start_sec,
                    end_seconds=end_sec
                ))

                # 开始新章节
                current_chapter = {
                    "subtitles": [],
                    "start": subtitle.end_time
                }
                keywords = set()

    # 处理最后一个章节
    if current_chapter["subtitles"]:
        subtitle = current_chapter["subtitles"][-1]
        start_sec = time_to_seconds(current_chapter["start"])
        end_sec = time_to_seconds(subtitle.end_time)
        text = ' '.join([s.text for s in current_chapter["subtitles"]])

        chapters.append(Chapter(
            title=generate_title_heuristic(text[:200]),
            start=current_chapter["start"],
            end=subtitle.end_time,
            summary=truncate_text(text, 150),
            keywords=list(keywords)[:5],
            start_seconds=start_sec,
            end_seconds=end_sec
        ))

    return chapters


def generate_title_heuristic(text: str) -> str:
    """从文本生成标题"""
    # 提取前几个实词作为标题
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text)[:5]
    if words:
        return ' '.join(words).title()
    return "Video Chapter"


def truncate_text(text: str, max_len: int) -> str:
    """截断文本"""
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


def main():
    if len(sys.argv) < 2:
        print("Usage: python chapter_analyzer.py <subtitle.vtt> [min_duration] [max_duration]")
        sys.exit(1)

    vtt_path = sys.argv[1]
    min_duration = int(sys.argv[2]) if len(sys.argv) > 2 else 180
    max_duration = int(sys.argv[3]) if len(sys.argv) > 3 else 300

    print(f"Analyzing: {vtt_path}")
    print(f"Duration range: {min_duration}-{max_duration}s")

    subtitles = parse_vtt(vtt_path)
    print(f"Parsed {len(subtitles)} subtitles")

    chapters = generate_chapters(subtitles, min_duration, max_duration)

    print("\n" + "=" * 50)
    print(f"Generated {len(chapters)} chapters:\n")

    for i, ch in enumerate(chapters, 1):
        duration = ch.end_seconds - ch.start_seconds
        print(f"[{i}] {ch.title}")
        print(f"    {ch.start} - {ch.end} ({duration}s)")
        print(f"    Summary: {ch.summary}")
        print(f"    Keywords: {', '.join(ch.keywords)}")
        print()


if __name__ == "__main__":
    main()
