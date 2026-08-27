#!/usr/bin/env python3
"""
Batch Subtitle Translator - 批量字幕翻译
20条字幕/批，节省95% API调用
"""

import sys
import re
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class Subtitle:
    index: int
    start_time: str
    end_time: str
    text: str
    translated: Optional[str] = None


class BatchTranslator:
    """
    批量字幕翻译器

    核心优化: 20条字幕/次API调用
    - 30分钟视频 ≈ 600条字幕
    - 串行翻译: 600次API调用
    - 批量翻译: 30次API调用
    - 节省: 95% API调用
    """

    def __init__(self, batch_size: int = 20, api_key: Optional[str] = None):
        self.batch_size = batch_size
        self.api_key = api_key

    def translate_file(
        self,
        subtitle_path: str,
        target_lang: str = "zh-CN",
        source_lang: str = "en"
    ) -> str:
        """
        翻译字幕文件

        Args:
            subtitle_path: 字幕文件路径(.srt)
            target_lang: 目标语言
            source_lang: 源语言

        Returns:
            翻译后的字幕文件路径
        """
        # 解析字幕
        subtitles = self._parse_srt(subtitle_path)

        # 批量翻译
        translated = self._translate_batch(subtitles, target_lang, source_lang)

        # 生成双语字幕
        bilingual = self._generate_bilingual(subtitles, translated)

        # 保存
        output_path = subtitle_path.replace('.srt', '_bilingual.srt')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(bilingual)

        return output_path

    def _parse_srt(self, path: str) -> list[Subtitle]:
        """解析SRT字幕"""
        subtitles = []
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        blocks = content.strip().split('\n\n')

        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) < 3:
                continue

            try:
                index = int(lines[0])
                time_line = lines[1]
                times = time_line.split('-->')
                start_time = times[0].strip()
                end_time = times[1].strip().split()[0]
                text = '\n'.join(lines[2:])

                subtitles.append(Subtitle(
                    index=index,
                    start_time=start_time,
                    end_time=end_time,
                    text=text
                ))
            except (ValueError, IndexError):
                continue

        return subtitles

    def _translate_batch(
        self,
        subtitles: list[Subtitle],
        target_lang: str,
        source_lang: str
    ) -> list[str]:
        """
        批量翻译

        关键优化: 将字幕分组，每组20条，一次API调用翻译整组
        """
        if not self.api_key:
            # 无API时返回原文
            return [s.text for s in subtitles]

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            results = []

            # 分批处理
            for i in range(0, len(subtitles), self.batch_size):
                batch = subtitles[i:i + self.batch_size]
                batch_texts = [s.text for s in batch]

                # 构建提示
                prompt = f"""Translate these subtitles from {source_lang} to {target_lang}.
Keep the original meaning and style. Each subtitle should be on its own line.

Subtitles:
{chr(10).join([f"[{j}] {t}" for j, t in enumerate(batch_texts, 1)])}

Output format (one translation per line, start with line number):
1. [translated text 1]
2. [translated text 2]
..."""

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": f"You are a professional translator. Translate from {source_lang} to {target_lang}."},
                        {"role": "user", "content": prompt}
                    ]
                )

                translations = response.choices[0].message.content.strip().split('\n')

                # 解析翻译结果
                for line in translations:
                    match = re.match(r'\d+\.\s*(.+)', line)
                    if match:
                        results.append(match.group(1).strip())
                    else:
                        results.append(line.strip())

                print(f"  Translated batch {i // self.batch_size + 1}/{(len(subtitles) - 1) // self.batch_size + 1}")

            return results

        except Exception as e:
            print(f"[WARN] Translation failed: {e}")
            return [s.text for s in subtitles]

    def _generate_bilingual(
        self,
        originals: list[Subtitle],
        translations: list[str]
    ) -> str:
        """生成双语字幕"""
        lines = []

        for i, sub in enumerate(originals):
            trans = translations[i] if i < len(translations) else sub.text

            lines.append(str(sub.index))
            lines.append(f"{sub.start_time} --> {sub.end_time}")
            lines.append(sub.text)
            lines.append(trans)
            lines.append("")  # 空行分隔

        return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python subtitle_translator.py <subtitle.srt> [target_lang] [api_key]")
        sys.exit(1)

    subtitle_path = sys.argv[1]
    target_lang = sys.argv[2] if len(sys.argv) > 2 else "zh-CN"
    api_key = sys.argv[3] if len(sys.argv) > 3 else None

    print(f"Translating: {subtitle_path}")
    print(f"Target: {target_lang}")
    print(f"Batch size: 20 (95% API savings)")

    translator = BatchTranslator(api_key=api_key)
    output_path = translator.translate_file(subtitle_path, target_lang)

    print(f"\n✓ Bilingual subtitle saved: {output_path}")


if __name__ == "__main__":
    main()
