"""
中文文案排版自动修正器
基于 sparanoid/chinese-copywriting-guidelines (15.3k Stars)
"""

import re
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pathlib import Path
from typing import Dict, List, Tuple


class CopywritingFixer:
    """中文文案排版自动修正器"""

    def __init__(self):
        self.fixes: List[Tuple[str, str, str]] = []

    def fix(self, text: str) -> Dict:
        """修正文案"""
        original = text
        self.fixes = []

        # 规则1: 中文↔英文需空格
        text = self._fix_cn_en_space(text)
        # 规则2: 中文↔数字需空格
        text = self._fix_cn_digit_space(text)
        # 规则7: 叹号不叠加
        text = self._fix_exclaim_repeat(text)
        # 规则8: 问号不叠加
        text = self._fix_question_repeat(text)
        # 规则9: 使用中文省略号
        text = self._fix_ellipsis(text)
        # 规则10: 使用中文破折号
        text = self._fix_em_dash(text)
        # 规则11: 句号不叠加
        text = self._fix_period_repeat(text)

        return {
            "original": original,
            "fixed": text,
            "changes": len(self.fixes),
            "fix_list": self.fixes,
        }

    def _add_fix(self, old: str, new: str, desc: str):
        if old != new:
            self.fixes.append((old, new, desc))

    def _fix_cn_en_space(self, text: str) -> str:
        """规则1: 中文↔英文需空格"""
        # 中文后跟英文：加空格
        while re.search(r'[\u4e00-\u9fff][a-zA-Z]', text):
            text = re.sub(r'([\u4e00-\u9fff])([a-zA-Z])', r'\1 \2', text)
            self._add_fix("Chinese+English", "Chinese + English", "中文↔英文加空格")
        # 英文后跟中文：加空格
        while re.search(r'[a-zA-Z][\u4e00-\u9fff]', text):
            text = re.sub(r'([a-zA-Z])([\u4e00-\u9fff])', r'\1 \2', text)
            self._add_fix("English+Chinese", "English + Chinese", "英文↔中文加空格")
        return text

    def _fix_cn_digit_space(self, text: str) -> str:
        """规则2: 中文↔数字需空格"""
        # 中文后跟数字
        while re.search(r'[\u4e00-\u9fff]\d', text):
            text = re.sub(r'([\u4e00-\u9fff])(\d)', r'\1 \2', text)
            self._add_fix("Chinese+Digit", "Chinese + Digit", "中文↔数字加空格")
        # 数字后跟中文
        while re.search(r'\d[\u4e00-\u9fff]', text):
            text = re.sub(r'(\d)([\u4e00-\u9fff])', r'\1 \2', text)
            self._add_fix("Digit+Chinese", "Digit + Chinese", "数字↔中文加空格")
        return text

    def _fix_exclaim_repeat(self, text: str) -> str:
        """规则7: 叹号不叠加"""
        # 英文叹号叠加
        if '!!' in text:
            text = re.sub(r'!+', '!', text)
            self._add_fix("!!!", "!", "叹号去重")
        # 中文叹号叠加
        if '！！' in text:
            text = re.sub(r'！+', '！', text)
            self._add_fix("！！", "！", "中文叹号去重")
        return text

    def _fix_question_repeat(self, text: str) -> str:
        """规则8: 问号不叠加"""
        # 英文问号叠加
        if '??' in text:
            text = re.sub(r'\?+', '?', text)
            self._add_fix("???", "?", "问号去重")
        # 中文问号叠加
        if '？？' in text:
            text = re.sub(r'？+', '？', text)
            self._add_fix("？？", "？", "中文问号去重")
        return text

    def _fix_ellipsis(self, text: str) -> str:
        """规则9: 使用中文省略号"""
        if '...' in text:
            text = text.replace('...', '……')
            self._add_fix("...", "……", "英文省略号→中文省略号")
        return text

    def _fix_em_dash(self, text: str) -> str:
        """规则10: 使用中文破折号"""
        if '--' in text:
            text = text.replace('--', '——')
            self._add_fix("--", "——", "英文破折号→中文破折号")
        return text

    def _fix_period_repeat(self, text: str) -> str:
        """规则11: 句号不叠加"""
        # 中文句号叠加
        if '。。' in text:
            text = text.replace('。。', '。')
            self._add_fix("。。", "。", "句号去重")
        return text


def fix_file(file_path: str) -> Dict:
    """修正文件"""
    try:
        with open(file_path, encoding="utf-8") as f:
            text = f.read()
        fixer = CopywritingFixer()
        result = fixer.fix(text)
        result["file"] = file_path
        return result
    except Exception as e:
        return {"error": str(e), "file": file_path}


def main():
    if len(sys.argv) < 2:
        print("用法: python fixer.py <文本或文件路径> [--dry-run]")
        print("示例: python fixer.py '我很熟Linux!!!'")
        print("示例: python fixer.py ./docs/article.md")
        print("示例: python fixer.py ./docs/article.md --dry-run  # 仅预览不保存")
        sys.exit(1)

    dry_run = "--dry-run" in sys.argv
    if dry_run:
        sys.argv.remove("--dry-run")

    arg = sys.argv[1]

    # 检查是否是文件
    if Path(arg).is_file():
        result = fix_file(arg)
    else:
        fixer = CopywritingFixer()
        result = fixer.fix(arg)

    # 输出结果
    print(f"\n{'='*50}")
    print(f"中文文案排版修正结果")
    print(f"{'='*50}")

    if "error" in result:
        print(f"[ERROR] 错误: {result['error']}")
        sys.exit(1)

    if result["changes"] == 0:
        print(f"[OK] 无需修正，文案已符合规范。")
    else:
        print(f"[CHANGES] 共 {result['changes']} 处修正:\n")
        for i, (old, new, desc) in enumerate(result["fix_list"], 1):
            print(f"  {i}. {desc}")
            print(f"     {old} → {new}")

        if not dry_run and "file" in result:
            # 保存修正后的文件
            try:
                with open(result["file"], "w", encoding="utf-8") as f:
                    f.write(result["fixed"])
                print(f"\n[SAVED] 已保存修正后的文件: {result['file']}")
            except Exception as e:
                print(f"\n[ERROR] 保存失败: {e}")
        else:
            print(f"\n[DRY-RUN] 预览修正后内容:")
            print(f"{'='*50}")
            print(result["fixed"])

    return result


if __name__ == "__main__":
    main()
