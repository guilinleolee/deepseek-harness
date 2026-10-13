"""
中文文案排版检查器
基于 sparanoid/chinese-copywriting-guidelines (15.3k Stars)
"""

import re
import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pathlib import Path
from typing import List, Dict, Optional

# 加载专有名词库
def load_proper_nouns():
    """加载专有名词大小写规范"""
    try:
        with open(Path(__file__).parent.parent / "rules" / "proper_nouns.json", encoding="utf-8") as f:
            data = json.load(f)
        # 展平为简单的映射
        nouns = {}
        for category, items in data.get("rules", {}).items():
            for wrong, correct in items.items():
                nouns[wrong.lower()] = correct
        return nouns
    except Exception:
        return {}

PROPER_NOUNS = load_proper_nouns()


class CopywritingChecker:
    """中文文案排版检查器"""

    def __init__(self):
        self.issues = []
        self.rules = [
            (1, self._check_cn_en_space, "中文↔英文需空格"),
            (2, self._check_cn_digit_space, "中文↔数字需空格"),
            (3, self._check_digit_unit_space, "数字↔单位需空格"),
            (4, self._check_punct_after_cn, "全角标点后不空格"),
            (7, self._check_exclaim_repeat, "叹号不叠加"),
            (8, self._check_question_repeat, "问号不叠加"),
            (9, self._check_ellipsis, "使用中文省略号……"),
            (10, self._check_em_dash, "使用中文破折号——"),
            (13, self._check_cn_punct_fullwidth, "中文标点用全角"),
            (19, self._check_proper_nouns, "专有名词大小写"),
        ]

    def check(self, text: str) -> Dict:
        """检查文案"""
        self.issues = []
        for rule_id, check_func, desc in self.rules:
            check_func(text)
        return {
            "text": text,
            "issues": self.issues,
            "passed": len(self.issues) == 0,
            "issue_count": len(self.issues),
        }

    def _add_issue(self, rule: int, issue_type: str, desc: str, match: str = ""):
        self.issues.append({
            "rule": rule,
            "type": issue_type,
            "description": desc,
            "match": match,
        })

    def _check_cn_en_space(self, text: str):
        """规则1: 中文↔英文需空格"""
        # 中文后跟英文
        matches = re.findall(r'[\u4e00-\u9fff][a-zA-Z]', text)
        for m in matches:
            self._add_issue(1, "missing_space", "中文↔英文需空格", m)
        # 英文后跟中文
        matches = re.findall(r'[a-zA-Z][\u4e00-\u9fff]', text)
        for m in matches:
            self._add_issue(1, "missing_space", "英文↔中文需空格", m)

    def _check_cn_digit_space(self, text: str):
        """规则2: 中文↔数字需空格"""
        # 中文后跟数字
        matches = re.findall(r'[\u4e00-\u9fff]\d', text)
        for m in matches:
            self._add_issue(2, "missing_space", "中文↔数字需空格", m)
        # 数字后跟中文
        matches = re.findall(r'\d[\u4e00-\u9fff]', text)
        for m in matches:
            self._add_issue(2, "missing_space", "数字↔中文需空格", m)

    def _check_digit_unit_space(self, text: str):
        """规则3: 数字↔单位需空格"""
        # 检查常见的无空格数字单位
        patterns = [
            (r'\d+px', "px"),
            (r'\d+kb', "kb"),
            (r'\d+mb', "mb"),
            (r'\d+gb', "gb"),
            (r'\d+tb', "tb"),
        ]
        for pattern, unit in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for m in matches:
                if not m.startswith(' '):
                    self._add_issue(3, "missing_space", f"数字↔{unit}需空格（应改为数字 {unit}）", m)

    def _check_punct_after_cn(self, text: str):
        """规则4: 全角标点后不空格"""
        matches = re.findall(r'[，。：；！？][a-zA-Z0-9]', text)
        for m in matches:
            self._add_issue(4, "punct_space", "全角标点后不直接跟英文/数字", m)

    def _check_exclaim_repeat(self, text: str):
        """规则7: 叹号不叠加"""
        matches = re.findall(r'!{2,}', text)
        for m in matches:
            self._add_issue(7, "repeat_punct", "叹号不叠加", m)
        matches = re.findall(r'！{2,}', text)
        for m in matches:
            self._add_issue(7, "repeat_punct", "中文叹号不叠加", m)

    def _check_question_repeat(self, text: str):
        """规则8: 问号不叠加"""
        matches = re.findall(r'\?{2,}', text)
        for m in matches:
            self._add_issue(8, "repeat_punct", "问号不叠加", m)
        matches = re.findall(r'？{2,}', text)
        for m in matches:
            self._add_issue(8, "repeat_punct", "中文问号不叠加", m)

    def _check_ellipsis(self, text: str):
        """规则9: 使用中文省略号"""
        if '...' in text:
            self._add_issue(9, "ellipsis", "使用中文省略号……而非...", "...")

    def _check_em_dash(self, text: str):
        """规则10: 使用中文破折号"""
        if '--' in text:
            self._add_issue(10, "em_dash", "使用中文破折号——而非--", "--")

    def _check_cn_punct_fullwidth(self, text: str):
        """规则13: 检查可能有问题的标点"""
        # 检查连续的标点
        matches = re.findall(r'[，。：；！？]{2,}', text)
        for m in matches:
            self._add_issue(13, "punct_repeat", "标点不重复使用", m)

    def _check_proper_nouns(self, text: str):
        """规则19-22: 专有名词大小写"""
        text_lower = text.lower()
        for wrong, correct in PROPER_NOUNS.items():
            if wrong in text_lower and correct not in text:
                # 找到匹配的位置
                pattern = re.compile(re.escape(wrong), re.IGNORECASE)
                for m in pattern.finditer(text):
                    if text[m.start():m.end()] != correct:
                        self._add_issue(19, "proper_noun", f"应为 {correct}", m.group())


def check_file(file_path: str) -> Dict:
    """检查文件"""
    try:
        with open(file_path, encoding="utf-8") as f:
            text = f.read()
        checker = CopywritingChecker()
        result = checker.check(text)
        result["file"] = file_path
        return result
    except Exception as e:
        return {"error": str(e), "file": file_path}


def main():
    if len(sys.argv) < 2:
        print("用法: python checker.py <文本或文件路径>")
        print("示例: python checker.py '我很熟Linux'")
        print("示例: python checker.py ./docs/article.md")
        sys.exit(1)

    arg = sys.argv[1]

    # 检查是否是文件
    if Path(arg).is_file():
        result = check_file(arg)
    else:
        checker = CopywritingChecker()
        result = checker.check(arg)

    # 输出结果
    print(f"\n{'='*50}")
    print(f"中文文案排版检查结果")
    print(f"{'='*50}")

    if "error" in result:
        print(f"❌ 错误: {result['error']}")
        sys.exit(1)

    if result["passed"]:
        print(f"[PASS] 通过! 无排版问题。")
    else:
        print(f"[FAIL] 发现 {result['issue_count']} 个问题:\n")
        for i, issue in enumerate(result["issues"], 1):
            print(f"  {i}. [规则{issue['rule']}] {issue['description']}")
            if issue.get("match"):
                print(f"     匹配: {issue['match']}")
        print(f"\n建议修正后可提升排版质量至出版级标准。")

    return result


if __name__ == "__main__":
    main()
