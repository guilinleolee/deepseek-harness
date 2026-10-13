#!/usr/bin/env python3
"""
Wiki AI味检测器
检测Wiki笔记中的AI生成内容特征

Usage:
    python3 detector.py --scan
    python3 detector.py --note "微服务架构的最佳实践"
    python3 detector.py --batch
"""

import argparse
import json
import re
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

WIKI_DIR = Path.home() / ".claude" / "wiki"


AI_PHRASES = {
    # 认知限制类
    "cognitive": [
        "As an AI", "I cannot", "I do not have", "I don't have access",
        "my knowledge cutoff", "based on my training", "I'm not able to",
        "I don't possess", "I don't have the ability to"
    ],
    # 过度确定性
    "overconfidence": [
        "It's important to note", "It is worth noting", "It should be noted",
        "it is crucial to", "it is essential to", "it is vital to",
        "it is important to", "it is necessary to"
    ],
    # 免责声明
    "disclaimer": [
        "Please note that", "Keep in mind that", "It is important to remember",
        "you should consult", "you may want to consider",
        "it is recommended that", "you might want to"
    ],
    # 过度量化
    "over_quantification": [
        "in today's rapidly", "in the ever-changing", "in today's digital age",
        "increasingly important", "plays a crucial role", "is of paramount importance",
        "cannot be overstated", "is a key factor"
    ],
    # 公式化开头
    "formulaic_opening": [
        "Let me explain", "In this article", "In this guide", "In this post",
        "In today's world", "When it comes to", "First and foremost",
        "Last but not least", "It goes without saying"
    ],
    # 公式化结尾
    "formulaic_ending": [
        "I hope this helps", "Feel free to", "Please let me know",
        "If you have any questions", "Thank you for reading",
        "Looking forward to", "Don't hesitate to"
    ]
}


@dataclass
class DetectionResult:
    note_id: str
    title: str
    score: int
    grade: str
    ai_probability: float
    details: dict
    flags: list
    suggestions: list
    ai_phrases_found: dict


class AITasteDetector:
    """AI味检测器"""

    def __init__(self):
        self.results = []

    def count_ai_phrases(self, content: str) -> tuple[int, dict]:
        """统计AI特征短语"""
        content_lower = content.lower()
        found_by_category = {}

        for category, phrases in AI_PHRASES.items():
            count = 0
            for phrase in phrases:
                count += len(re.findall(re.escape(phrase), content_lower, re.IGNORECASE))
            found_by_category[category] = count

        total = sum(found_by_category.values())
        return total, found_by_category

    def score_ai_phrases(self, count: int) -> int:
        """AI特征短语评分 (0-4)"""
        if count == 0:
            return 4
        elif count < 5:
            return 3
        elif count <= 15:
            return 2
        elif count <= 30:
            return 1
        else:
            return 0

    def score_sentence_variety(self, content: str) -> int:
        """句式多样性评分 (0-3)"""
        sentences = re.split(r'[.!?。！？]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) < 2:
            return 0

        # 计算句式复杂度
        simple_count = sum(1 for s in sentences if len(s) < 30)
        complex_count = sum(1 for s in sentences if ', which' in s or '，因此' in s or '，但是' in s)
        question_count = sum(1 for s in sentences if '?' in s or '？' in s)
        exclamation_count = sum(1 for s in sentences if '!' in s or '！' in s)

        # 计算句式多样性指数
        variety_score = (complex_count + question_count + exclamation_count) / len(sentences)

        if variety_score > 0.3 and len(sentences) > 5:
            return 3
        elif variety_score > 0.15:
            return 2
        elif variety_score > 0.05:
            return 1
        else:
            return 0

    def score_opinion_expression(self, content: str) -> int:
        """观点表达评分 (0-3)"""
        content_lower = content.lower()

        # 第一人称指示词
        first_person = sum(1 for w in ['i ', '我认为', '我觉得', '在我看来', '我发现', '我的经验'] if w in content_lower)

        # 经验性表达
        experiential = sum(1 for w in ['我曾经', '我之前', '有一次', '经验表明', '实践中', '踩坑'] if w in content_lower)

        # 确定性较低的词
        uncertainty = sum(1 for w in ['可能', '也许', '不确定', '不太确定', '我个人'] if w in content_lower)

        # 绝对化表述 (负面指标)
        absolute = sum(1 for w in ['总是', '从来不', '每个人', '所有'] if w in content_lower)

        opinion_score = first_person * 0.5 + experiential * 0.5 + uncertainty * 0.3 - absolute * 0.2

        if opinion_score >= 3:
            return 3
        elif opinion_score >= 1.5:
            return 2
        elif opinion_score >= 0.5:
            return 1
        else:
            return 0

    def score_specific_details(self, content: str) -> int:
        """具体细节评分 (0-2)"""
        # 数字检测
        numbers = re.findall(r'\d+', content)

        # 具体代码示例
        code_blocks = len(re.findall(r'```[\s\S]*?```', content))

        # 链接引用
        links = len(re.findall(r'\[.+?\]\(.+?\)', content))

        # 时间戳
        timestamps = len(re.findall(r'\d{4}[-/]\d{2}[-/]\d{2}', content))

        detail_score = len(numbers) * 0.1 + code_blocks * 0.5 + links * 0.3 + timestamps * 0.2

        if detail_score >= 3:
            return 2
        elif detail_score >= 1:
            return 1
        else:
            return 0

    def score_structure_naturalness(self, content: str) -> int:
        """结构自然度评分 (0-2)"""
        # 检测明显的模板结构
        template_markers = [
            r'^\d+\.\s+\w+',  # 1. 2. 3.
            r'^第[一二三四五六七八九十]+',  # 第一 第二
            r'#{1,6}\s',  # Markdown标题
            r'\*\*\w+\*\*',  # 粗体标题
        ]

        template_count = 0
        for marker in template_markers:
            template_count += len(re.findall(marker, content, re.MULTILINE))

        # 检测过渡短语
        transitions = ['此外', '另外', '更重要的是', '总的来说', '综上所述']
        transition_count = sum(1 for t in transitions if t in content)

        # 段落数量
        paragraphs = [p for p in content.split('\n\n') if p.strip()]
        paragraph_count = len(paragraphs)

        structure_score = template_count + transition_count * 0.5

        if paragraph_count > 20 or structure_score > 15:
            return 0
        elif paragraph_count > 10 or structure_score > 8:
            return 1
        else:
            return 2

    def detect(self, note_content: str, note_id: str = "unknown", title: str = "") -> DetectionResult:
        """检测AI味"""
        ai_phrase_count, ai_phrases_found = self.count_ai_phrases(note_content)

        # 各维度评分
        ai_phrases_score = self.score_ai_phrases(ai_phrase_count)
        sentence_score = self.score_sentence_variety(note_content)
        opinion_score = self.score_opinion_expression(note_content)
        detail_score = self.score_specific_details(note_content)
        structure_score = self.score_structure_naturalness(note_content)

        # 总分
        total_score = ai_phrases_score + sentence_score + opinion_score + detail_score + structure_score

        # 等级
        if total_score >= 12:
            grade = "A"
            ai_prob = 5.0
        elif total_score >= 9:
            grade = "B"
            ai_prob = 25.0
        elif total_score >= 5:
            grade = "C"
            ai_prob = 55.0
        else:
            grade = "D"
            ai_prob = 85.0

        # 生成标记
        flags = []
        if ai_phrase_count >= 30:
            flags.append("大量AI特征短语")
        elif ai_phrase_count >= 15:
            flags.append("中等AI特征短语")
        elif ai_phrase_count >= 5:
            flags.append("少量AI特征短语")

        if ai_phrases_found.get("cognitive", 0) > 0:
            flags.append("检测到AI身份声明")
        if ai_phrases_found.get("overconfidence", 0) >= 3:
            flags.append("过度使用确定性表达")
        if opinion_score == 0:
            flags.append("完全客观陈述，无个人观点")
        if structure_score == 0:
            flags.append("结构过于模板化")

        # 生成建议
        suggestions = []
        if ai_phrase_count > 5:
            suggestions.append("删除或改写AI特征短语")
        if opinion_score < 2:
            suggestions.append("添加个人实践经验或观点")
        if detail_score < 2:
            suggestions.append("加入具体案例、数据或代码示例")
        if structure_score < 1:
            suggestions.append("减少公式化结构，增加自然过渡")

        return DetectionResult(
            note_id=note_id,
            title=title,
            score=total_score,
            grade=grade,
            ai_probability=ai_prob,
            details={
                "ai_phrases": ai_phrases_score,
                "sentence_variety": sentence_score,
                "opinion_expression": opinion_score,
                "specific_details": detail_score,
                "structure_naturalness": structure_score
            },
            flags=flags,
            suggestions=suggestions,
            ai_phrases_found=ai_phrases_found
        )

    def scan_all(self) -> list[DetectionResult]:
        """扫描所有Wiki笔记"""
        results = []

        if not WIKI_DIR.exists():
            print(f"Wiki目录不存在: {WIKI_DIR}")
            return results

        for md_file in WIKI_DIR.glob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")

                # 提取标题
                title = ""
                if content.startswith("# "):
                    title = content.split("\n")[0][2:].strip()
                elif content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        for line in parts[1].split("\n"):
                            if line.startswith("title:"):
                                title = line.split(":", 1)[1].strip()
                                break

                result = self.detect(content, md_file.stem, title)
                results.append(result)
            except Exception as e:
                print(f"处理失败 {md_file.name}: {e}")

        return results

    def format_result(self, result: DetectionResult) -> str:
        """格式化检测结果"""
        flags_str = "\n".join(f"  - {f}" for f in result.flags) if result.flags else "  (无)"
        suggestions_str = "\n".join(f"  - {s}" for s in result.suggestions) if result.suggestions else "  (无)"

        return f"""
{'='*60}
笔记: {result.title or result.note_id}
{'='*60}
总分: {result.score}/14 | 等级: {result.grade} | AI概率: {result.ai_probability:.0f}%

各维度得分:
  AI特征短语: {result.details['ai_phrases']}/4
  句式多样性: {result.details['sentence_variety']}/3
  观点表达: {result.details['opinion_expression']}/3
  具体细节: {result.details['specific_details']}/2
  结构自然度: {result.details['structure_naturalness']}/2

AI特征短语统计:
  认知限制类: {result.ai_phrases_found.get('cognitive', 0)}
  过度确定性: {result.ai_phrases_found.get('overconfidence', 0)}
  免责声明: {result.ai_phrases_found.get('disclaimer', 0)}
  过度量化: {result.ai_phrases_found.get('over_quantification', 0)}
  公式化开头: {result.ai_phrases_found.get('formulaic_opening', 0)}
  公式化结尾: {result.ai_phrases_found.get('formulaic_ending', 0)}

标记:
{flags_str}

建议:
{suggestions_str}
"""


def main():
    parser = argparse.ArgumentParser(description="Wiki AI味检测器")
    parser.add_argument("--scan", action="store_true", help="扫描所有Wiki笔记")
    parser.add_argument("--note", help="检测指定笔记内容")
    parser.add_argument("--batch", action="store_true", help="批量检测并输出JSON")
    parser.add_argument("--json", action="store_true", help="JSON格式输出")
    parser.add_argument("--file", help="检测指定文件")
    args = parser.parse_args()

    detector = AITasteDetector()

    if args.file:
        content = Path(args.file).read_text(encoding="utf-8")
        result = detector.detect(content, Path(args.file).stem)
        if args.json:
            print(json.dumps({
                "score": result.score,
                "grade": result.grade,
                "ai_probability": result.ai_probability,
                "details": result.details,
                "flags": result.flags,
                "suggestions": result.suggestions,
                "ai_phrases_found": result.ai_phrases_found
            }, ensure_ascii=False, indent=2))
        else:
            print(detector.format_result(result))

    elif args.note:
        result = detector.detect(args.note, "input")
        if args.json:
            print(json.dumps({
                "score": result.score,
                "grade": result.grade,
                "ai_probability": result.ai_probability,
                "details": result.details,
                "flags": result.flags,
                "suggestions": result.suggestions,
                "ai_phrases_found": result.ai_phrases_found
            }, ensure_ascii=False, indent=2))
        else:
            print(detector.format_result(result))

    elif args.scan or args.batch:
        results = detector.scan_all()

        if args.batch and args.json:
            output = [{
                "note_id": r.note_id,
                "title": r.title,
                "score": r.score,
                "grade": r.grade,
                "ai_probability": r.ai_probability,
                "details": r.details,
                "flags": r.flags,
                "suggestions": r.suggestions
            } for r in results]
            print(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            print(f"\n检测了 {len(results)} 篇Wiki笔记:\n")
            for r in results:
                print(detector.format_result(r))

            # 汇总统计
            grades = {"A": 0, "B": 0, "C": 0, "D": 0}
            for r in results:
                grades[r.grade] += 1

            print(f"\n{'='*60}")
            print(f"汇总统计:")
            print(f"  A级 (人类写作): {grades['A']} 篇")
            print(f"  B级 (少量AI味): {grades['B']} 篇")
            print(f"  C级 (AI味较重): {grades['C']} 篇")
            print(f"  D级 (AI生成): {grades['D']} 篇")
            print(f"{'='*60}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
