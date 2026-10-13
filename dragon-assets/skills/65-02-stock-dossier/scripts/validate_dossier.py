#!/usr/bin/env python3
"""
个股档案校验器 (Stock Dossier Validator)

用于校验生成的个股档案是否满足以下要求：
1. 必填章节完整
2. 数据溯源标注
3. 风险提示存在
4. 无投资建议内容
"""

import re
import sys
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ValidationIssue:
    """校验问题"""
    section: str
    message: str
    severity: str  # error, warning, info


class DossierValidator:
    """个股档案校验器"""

    REQUIRED_SECTIONS = [
        ("title", r"^#\s+.+（\d{6}）个股档案", "一级标题需要标明股票代码"),
        ("basic_info", r"^##\s*1[.、]\s*基础信息", "缺少基础信息章节"),
        ("quote", r"^##\s*2[.、]\s*今日行情", "缺少今日行情章节"),
        ("money_flow", r"^##\s*3[.、]\s*资金流向", "缺少资金流向章节"),
        ("valuation", r"^##\s*4[.、]\s*估值", "缺少估值分析章节"),
        ("financial", r"^##\s*5[.、]\s*财务", "缺少财务数据章节"),
        ("research", r"^##\s*6[.、]\s*研报", "缺少研报摘要章节"),
        ("risk_warning", r"(风险提示|不构成.*投资建议|风险自担)", "缺少风险提示"),
        ("data_source", r"(数据来源|Pandadata|来源接口)", "缺少数据来源说明"),
        ("data_date", r"(数据日|报告期|T-1)", "缺少数据日期标注"),
    ]

    INVESTMENT_ADVICE_PATTERNS = [
        (r"建议.*买入", "可能存在买入建议"),
        (r"建议.*卖出", "可能存在卖出建议"),
        (r"建议.*持有", "可能存在持有建议"),
        (r"建仓", "可能存在建仓建议"),
        (r"加仓", "可能存在加仓建议"),
        (r"减仓", "可能存在减仓建议"),
        (r"清仓", "可能存在清仓建议"),
        (r"止损", "可能存在止损建议"),
        (r"止盈", "可能存在止盈建议"),
        (r"目标价.*买入", "可能存在目标价买入建议"),
        (r"应该.*买", "可能存在购买建议"),
        (r"值得.*买", "可能存在购买建议"),
        (r"不要.*买", "可能存在购买建议"),
        (r"操作建议", "可能存在操作建议"),
        (r"交易建议", "可能存在交易建议"),
    ]

    def __init__(self, text: str):
        self.text = text
        self.issues: List[ValidationIssue] = []

    def validate(self) -> List[ValidationIssue]:
        """执行完整校验"""
        self._check_sections()
        self._check_data_traceability()
        self._check_risk_warning()
        self._check_investment_advice()
        self._check_format()
        return self.issues

    def _add_issue(self, section: str, message: str, severity: str = "error"):
        """添加问题"""
        self.issues.append(ValidationIssue(
            section=section,
            message=message,
            severity=severity
        ))

    def _check_sections(self):
        """检查章节完整性"""
        for key, pattern, message in self.REQUIRED_SECTIONS:
            if not re.search(pattern, self.text, flags=re.MULTILINE):
                self._add_issue(key, message, "error")

    def _check_data_traceability(self):
        """检查数据溯源"""
        # 检查是否有接口调用记录
        if not re.search(r"(来源接口|接口调用|get_\w+)", self.text):
            self._add_issue(
                "traceability",
                "缺少接口调用记录或来源标注",
                "warning"
            )

        # 检查涨跌幅是否有正负号
        pct_chg_matches = re.findall(r"(\d+\.?\d*%)", self.text)
        has_unsigned = False
        for match in pct_chg_matches[:10]:  # 只检查前10个
            if match.replace("%", "").replace("+", "").replace("-", "").isdigit():
                # 检查这个数字是否在涨跌幅上下文中
                context_pattern = rf"涨跌幅[^\d]*({match}|{match.replace('.', '')})"
                if re.search(context_pattern, self.text):
                    # 检查是否有明确的涨跌标记
                    context = re.search(
                        rf".{{0,50}}{re.escape(match)}.{{0,50}}",
                        self.text
                    )
                    if context and ("+" not in context.group() and "-" not in context.group()):
                        has_unsigned = True
                        break

        if has_unsigned:
            self._add_issue(
                "traceability",
                "涨跌幅应包含正负号以明确涨跌方向",
                "warning"
            )

    def _check_risk_warning(self):
        """检查风险提示"""
        risk_patterns = [
            (r"风险提示", "风险提示"),
            (r"不构成.*投资建议", "非投资建议声明"),
            (r"风险自担", "风险自担声明"),
        ]

        found = 0
        for pattern, name in risk_patterns:
            if re.search(pattern, self.text):
                found += 1

        if found < 2:
            self._add_issue(
                "risk_warning",
                "风险提示不够完整，建议包含风险提示、非投资建议声明和风险自担",
                "warning"
            )

    def _check_investment_advice(self):
        """检查是否存在投资建议"""
        for pattern, message in self.INVESTMENT_ADVICE_PATTERNS:
            matches = re.finditer(pattern, self.text)
            for match in matches:
                # 获取上下文
                start = max(0, match.start() - 20)
                end = min(len(self.text), match.end() + 20)
                context = self.text[start:end]

                # 排除明显的引用或免责声明中的内容
                if not any(exclude in context for exclude in ["风险提示", "不构成", "免责声明"]):
                    self._add_issue(
                        "investment_advice",
                        f"{message}：...{context}...",
                        "warning"
                    )

    def _check_format(self):
        """检查格式规范"""
        # 检查档案长度
        if len(self.text.strip()) < 2000:
            self._add_issue(
                "format",
                "档案内容过短，可能缺少必要信息",
                "warning"
            )

        # 检查表格格式
        table_count = len(re.findall(r"\|[^|]+\|", self.text))
        if table_count < 10:
            self._add_issue(
                "format",
                "档案中表格较少，可能缺少数据支撑",
                "info"
            )

        # 检查是否使用绝对日期
        if re.search(r"(今天|昨日|明日)", self.text):
            self._add_issue(
                "format",
                    "档案中使用了相对日期（今天/昨日/明日），建议使用绝对日期",
                "warning"
            )

    def print_report(self):
        """打印校验报告"""
        print("=" * 60)
        print("个股档案校验报告")
        print("=" * 60)

        if not self.issues:
            print("✅ 校验通过，未发现问题")
            return

        errors = [i for i in self.issues if i.severity == "error"]
        warnings = [i for i in self.issues if i.severity == "warning"]
        infos = [i for i in self.issues if i.severity == "info"]

        print(f"\n📊 统计：")
        print(f"  - 错误: {len(errors)}")
        print(f"  - 警告: {len(warnings)}")
        print(f"  - 提示: {len(infos)}")

        if errors:
            print(f"\n❌ 错误 ({len(errors)}项)：")
            for issue in errors:
                print(f"  [{issue.section}] {issue.message}")

        if warnings:
            print(f"\n⚠️  警告 ({len(warnings)}项)：")
            for issue in warnings:
                print(f"  [{issue.section}] {issue.message}")

        if infos:
            print(f"\n💡 提示 ({len(infos)}项)：")
            for issue in infos:
                print(f"  [{issue.section}] {issue.message}")

        print("\n" + "=" * 60)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python validate_dossier.py <dossier-path>")
        sys.exit(1)

    path = sys.argv[1]

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"错误：找不到文件 {path}")
        sys.exit(1)
    except Exception as e:
        print(f"错误：读取文件失败 {e}")
        sys.exit(1)

    validator = DossierValidator(content)
    issues = validator.validate()
    validator.print_report()

    # 返回退出码
    errors = [i for i in issues if i.severity == "error"]
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
