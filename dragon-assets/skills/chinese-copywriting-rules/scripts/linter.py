"""
中文文案排版批量检查工具
基于 sparanoid/chinese-copywriting-guidelines (15.3k Stars)
"""

import re
import sys
import io
from pathlib import Path
from typing import Dict, List, Tuple
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 加载专有名词数据库
PROPER_NOUNS: Dict[str, str] = {}


def load_proper_nouns():
    """加载专有名词数据库"""
    global PROPER_NOUNS
    json_path = Path(__file__).parent.parent / "rules" / "proper_nouns.json"
    if json_path.exists():
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
            for category in data.get("categories", []):
                for item in category.get("items", []):
                    PROPER_NOUNS[item["wrong"]] = item["correct"]


load_proper_nouns()


class CopywritingLinter:
    """中文文案批量检查器"""

    def __init__(self):
        self.issues: List[Dict] = []
        self.stats = {
            "total_files": 0,
            "files_with_issues": 0,
            "total_issues": 0,
            "by_rule": {},
        }

    def lint_file(self, file_path: str) -> Dict:
        """检查单个文件"""
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            self.issues = []
            for line_num, line in enumerate(lines, 1):
                self._check_line(file_path, line, line_num)

            return {
                "file": file_path,
                "issues": self.issues,
                "issue_count": len(self.issues),
            }
        except Exception as e:
            return {"file": file_path, "error": str(e), "issues": []}

    def _check_line(self, file_path: str, line: str, line_num: int):
        """检查单行内容"""
        checks = [
            # 规则1: 中文后跟英文需空格
            (r'[\u4e00-\u9fff][a-zA-Z]', 1, "中文后缺少空格"),
            # 规则1: 英文后跟中文需空格
            (r'[a-zA-Z][\u4e00-\u9fff]', 1, "英文后缺少空格"),
            # 规则2: 中文后跟数字需空格
            (r'[\u4e00-\u9fff]\d', 2, "中文后缺少空格"),
            # 规则2: 数字后跟中文需空格
            (r'\d[\u4e00-\u9fff]', 2, "数字后缺少空格"),
            # 规则7: 英文叹号叠加
            (r'!{2,}', 7, "叹号重复"),
            # 规则7: 中文叹号叠加
            (r'！{2,}', 7, "中文叹号重复"),
            # 规则8: 英文问号叠加
            (r'\?{2,}', 8, "问号重复"),
            # 规则8: 中文问号叠加
            (r'？{2,}', 8, "中文问号重复"),
            # 规则9: 英文省略号
            (r'\.{3,}', 9, "使用英文省略号"),
            # 规则10: 英文破折号
            (r'-{2,}', 10, "使用英文破折号"),
            # 规则11: 中文句号叠加
            (r'。{2,}', 11, "句号重复"),
        ]

        for pattern, rule_num, desc in checks:
            for match in re.finditer(pattern, line):
                self.issues.append({
                    "file": file_path,
                    "line": line_num,
                    "rule": rule_num,
                    "description": desc,
                    "text": match.group(),
                    "position": match.start(),
                })
                rule_key = f"规则{rule_num}"
                self.stats["by_rule"][rule_key] = self.stats["by_rule"].get(rule_key, 0) + 1

        # 规则19: 专有名词大小写检查
        for wrong, correct in PROPER_NOUNS.items():
            pattern = re.compile(re.escape(wrong), re.IGNORECASE)
            for match in pattern.finditer(line):
                if match.group() != correct:
                    self.issues.append({
                        "file": file_path,
                        "line": line_num,
                        "rule": 19,
                        "description": f"专有名词大小写: {wrong}",
                        "text": match.group(),
                        "expected": correct,
                        "position": match.start(),
                    })
                    self.stats["by_rule"]["规则19"] = self.stats["by_rule"].get("规则19", 0) + 1

    def lint_directory(self, dir_path: str, extensions: List[str] = None) -> List[Dict]:
        """批量检查目录"""
        if extensions is None:
            extensions = [".md", ".txt", ".py", ".js", ".ts"]

        results = []
        dir_path = Path(dir_path)

        for ext in extensions:
            for file_path in dir_path.rglob(f"*{ext}"):
                # 跳过 node_modules 和隐藏目录
                if "node_modules" in str(file_path) or any(
                    part.startswith(".") for part in file_path.parts
                ):
                    continue

                self.stats["total_files"] += 1
                result = self.lint_file(str(file_path))

                if result["issue_count"] > 0:
                    self.stats["files_with_issues"] += 1
                    self.stats["total_issues"] += result["issue_count"]
                    results.append(result)

        return results

    def print_report(self, results: List[Dict]):
        """打印检查报告"""
        print(f"\n{'='*60}")
        print(f"中文文案排版检查报告")
        print(f"{'='*60}")

        print(f"\n📊 统计信息:")
        print(f"  检查文件数: {self.stats['total_files']}")
        print(f"  有问题文件: {self.stats['files_with_issues']}")
        print(f"  问题总数:   {self.stats['total_issues']}")

        if self.stats["by_rule"]:
            print(f"\n📋 问题分类:")
            for rule, count in sorted(self.stats["by_rule"].items()):
                print(f"  {rule}: {count}处")

        if results:
            print(f"\n📝 问题详情:")
            for result in results:
                print(f"\n  📁 {result['file']}")
                for issue in result["issues"][:10]:  # 最多显示10条
                    expected = issue.get("expected", "")
                    extra = f" → 建议: {expected}" if expected else ""
                    print(f"     第{issue['line']}行: [{issue['description']}] {issue['text']}{extra}")

                if len(result["issues"]) > 10:
                    print(f"     ... 还有 {len(result['issues']) - 10} 处问题")

        if not results:
            print(f"\n✅ 所有文件均符合中文文案排版规范！")

        print(f"\n{'='*60}")


def main():
    if len(sys.argv) < 2:
        print("用法: python linter.py <文件或目录路径> [--extensions md,txt]")
        print("示例: python linter.py ./docs/")
        print("示例: python linter.py ./docs/ --extensions md,py")
        sys.exit(1)

    # 解析参数
    path = sys.argv[1]
    extensions = [".md"]  # 默认只检查 markdown

    for arg in sys.argv[2:]:
        if arg.startswith("--extensions="):
            extensions = [f".{ext.strip()}" for ext in arg.split("=")[1].split(",")]

    linter = CopywritingLinter()

    # 检查是文件还是目录
    if Path(path).is_file():
        linter.stats["total_files"] = 1
        result = linter.lint_file(path)
        results = [result] if result["issue_count"] > 0 else []
        if result["issue_count"] > 0:
            linter.stats["files_with_issues"] = 1
            linter.stats["total_issues"] = result["issue_count"]
    else:
        results = linter.lint_directory(path, extensions)

    linter.print_report(results)

    # 返回非零退出码表示有问题
    if results:
        sys.exit(1)
    return results


if __name__ == "__main__":
    main()
