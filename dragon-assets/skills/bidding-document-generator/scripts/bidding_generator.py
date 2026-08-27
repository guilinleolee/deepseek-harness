#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bidding Document Generator - 天龙引擎封装版
招投标文档智能生成器

功能:
- 招标文件生成
- 投标文件(标书)生成
- 评标报告生成
- 答疑函件生成
- 中标通知书生成

使用:
    python bidding_generator.py tender --project "项目名称" --budget "预算"
    python bidding_generator.py proposal --tender-file "招标文件.pdf" --company "公司名称"
    python bidding_generator.py evaluation --project "项目名称" --bidders "公司A,公司B"
    python bidding_generator.py winning --project "项目名称" --winner "中标公司"
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from jinja2 import Template
    HAS_JINJA2 = True
except ImportError:
    HAS_JINJA2 = False

try:
    from docx import Document
    from docx.shared import Inches, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False


class BiddingGenerator:
    """招投标文档生成器"""

    def __init__(self, template_dir: Optional[str] = None, output_dir: str = "./output"):
        """
        初始化生成器

        Args:
            template_dir: 模板目录路径
            output_dir: 输出目录路径
        """
        self.base_dir = Path(__file__).parent.parent
        self.template_dir = Path(template_dir) if template_dir else self.base_dir / "templates"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 加载模板
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, dict]:
        """加载所有JSON模板"""
        templates = {}
        for template_file in self.template_dir.glob("*.json"):
            with open(template_file, 'r', encoding='utf-8') as f:
                template_name = template_file.stem
                templates[template_name] = json.load(f)
        return templates

    def generate_tender(
        self,
        project_name: str,
        project_budget: str,
        project_scope: str,
        bidding_start: Optional[str] = None,
        bidding_end: Optional[str] = None,
        project_id: Optional[str] = None,
        project_type: Optional[str] = None,
        project_description: Optional[str] = None,
        tech_requirements: Optional[List[str]] = None,
        eligibility_criteria: Optional[List[str]] = None,
        output_format: str = "json"
    ) -> Dict[str, Any]:
        """
        生成招标文件

        Args:
            project_name: 项目名称
            project_budget: 项目预算
            project_scope: 项目范围
            bidding_start: 招标开始日期
            bidding_end: 招标截止日期
            project_id: 项目编号
            project_type: 项目类型
            project_description: 项目描述
            tech_requirements: 技术要求列表
            eligibility_criteria: 投标资格要求列表
            output_format: 输出格式 (json/docx)

        Returns:
            生成的招标文件内容
        """
        current_date = datetime.now().strftime("%Y-%m-%d")
        project_id = project_id or f"ZB-{datetime.now().strftime('%Y%m%d')}-001"
        project_description = project_description or project_scope

        # 准备模板数据
        data = {
            "project_name": project_name,
            "current_date": current_date,
            "project_id": project_id,
            "project_type": project_type or "软件开发",
            "project_description": project_description,
            "project_budget": project_budget,
            "bidding_start_date": bidding_start or current_date,
            "bidding_end_date": bidding_end or self._add_days(current_date, 15),
            "tech_standards": "、".join(tech_requirements) if tech_requirements else "按照国家相关标准执行",
            "eligibility_criteria": eligibility_criteria or [
                "投标方应具备相应的资质，在相关行业有一定年限的从业经验",
                "提供所需的资质证明文件，包括但不限于营业执照、行业资质证书等"
            ]
        }

        # 渲染模板
        result = self._render_template("bidding_template", data)

        # 输出文件
        if output_format == "docx" and HAS_DOCX:
            self._save_as_docx(result, f"招标文件_{project_name}.docx")

        return result

    def generate_proposal(
        self,
        tender_file: str,
        company_name: str,
        company_qualifications: Optional[List[str]] = None,
        tech_solution: Optional[str] = None,
        quotation: Optional[Dict[str, str]] = None,
        project_team: Optional[List[Dict[str, str]]] = None,
        implementation_plan: Optional[Dict[str, str]] = None,
        output_format: str = "json"
    ) -> Dict[str, Any]:
        """
        生成投标文件(标书)

        Args:
            tender_file: 招标文件路径
            company_name: 投标公司名称
            company_qualifications: 公司资质列表
            tech_solution: 技术方案
            quotation: 报价明细
            project_team: 项目团队
            implementation_plan: 实施计划
            output_format: 输出格式

        Returns:
            生成的投标文件内容
        """
        current_date = datetime.now().strftime("%Y-%m-%d")

        # 分析招标文件（简化版，实际应使用AI模型）
        tender_info = self._analyze_tender_file(tender_file)

        # 准备模板数据
        data = {
            "project_name": tender_info.get("project_name", "项目"),
            "current_date": current_date,
            "company_name": company_name,
            "company_qualifications": "、".join(company_qualifications) if company_qualifications else "具备相关资质",
            "tech_solution": tech_solution or "详细技术方案见附件",
            "quotation": quotation or {"总计": "详见报价明细表"},
            "project_team": project_team or [],
            "implementation_plan": implementation_plan or {}
        }

        # 创建投标文件模板
        proposal_template = {
            "header": {
                "title": f"{company_name}投标文件",
                "date": current_date,
                "project_name": data["project_name"],
                "company_name": company_name
            },
            "body": {
                "company_overview": f"{company_name}是一家专业的技术服务企业，具备{'、'.join(company_qualifications) if company_qualifications else '丰富的行业经验'}。",
                "qualifications": company_qualifications or ["具备相关资质"],
                "tech_solution": tech_solution or "详细技术方案见附件",
                "quotation": quotation or {},
                "commitment": "我方承诺按照招标文件和投标文件的要求履行合同义务，保证项目质量和进度。"
            }
        }

        result = proposal_template

        # 输出文件
        if output_format == "docx" and HAS_DOCX:
            self._save_proposal_as_docx(result, f"投标文件_{company_name}.docx")

        return result

    def generate_evaluation(
        self,
        project_name: str,
        bidders: List[Dict[str, Any]],
        experts: Optional[List[str]] = None,
        recommendation: Optional[str] = None,
        output_format: str = "json"
    ) -> Dict[str, Any]:
        """
        生成评标报告

        Args:
            project_name: 项目名称
            bidders: 投标方列表，包含名称、技术分、价格分、总分
            experts: 评标专家列表
            recommendation: 推荐中标方
            output_format: 输出格式

        Returns:
            生成的评标报告内容
        """
        current_date = datetime.now().strftime("%Y-%m-%d")

        # 排序投标方
        sorted_bidders = sorted(bidders, key=lambda x: x.get("total", 0), reverse=True)
        winner = recommendation or sorted_bidders[0]["name"] if sorted_bidders else None

        data = {
            "project_name": project_name,
            "current_date": current_date,
            "expert_names": "、".join(experts) if experts else "评标专家",
            "expert_expertises": "相关专业领域",
            "bidders": sorted_bidders,
            "recommendation": winner
        }

        result = self._render_template("evaluation_report_template", data)

        if output_format == "docx" and HAS_DOCX:
            self._save_as_docx(result, f"评标报告_{project_name}.docx")

        return result

    def generate_winning_notice(
        self,
        project_name: str,
        winner: str,
        winning_amount: str,
        project_id: Optional[str] = None,
        output_format: str = "json"
    ) -> Dict[str, Any]:
        """
        生成中标通知书

        Args:
            project_name: 项目名称
            winner: 中标方名称
            winning_amount: 中标金额
            project_id: 项目编号
            output_format: 输出格式

        Returns:
            生成的中标通知书内容
        """
        current_date = datetime.now().strftime("%Y-%m-%d")

        data = {
            "project_name": project_name,
            "current_date": current_date,
            "project_id": project_id or f"ZB-{datetime.now().strftime('%Y%m%d')}-001",
            "winner": winner,
            "winning_amount": winning_amount
        }

        result = self._render_template("winning_notice_template", data)

        if output_format == "docx" and HAS_DOCX:
            self._save_as_docx(result, f"中标通知书_{winner}.docx")

        return result

    def generate_answer_letter(
        self,
        project_name: str,
        question: str,
        answer: Optional[str] = None,
        output_format: str = "json"
    ) -> Dict[str, Any]:
        """
        生成答疑函件

        Args:
            project_name: 项目名称
            question: 问题内容
            answer: 答复内容（可选，不提供则生成模板）
            output_format: 输出格式

        Returns:
            生成的答疑函件内容
        """
        current_date = datetime.now().strftime("%Y-%m-%d")

        result = {
            "header": {
                "title": f"{project_name}答疑函件",
                "date": current_date,
                "project_name": project_name
            },
            "body": {
                "question": question,
                "answer": answer or "请根据实际情况填写答复内容"
            }
        }

        if output_format == "docx" and HAS_DOCX:
            self._save_as_docx(result, f"答疑函件_{project_name}.docx")

        return result

    def _render_template(self, template_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """渲染JSON模板"""
        if template_name not in self.templates:
            return data

        template = self.templates[template_name]

        def render_value(value, context):
            if isinstance(value, str) and HAS_JINJA2:
                try:
                    return Template(value).render(**context)
                except Exception:
                    return value
            elif isinstance(value, dict):
                return {k: render_value(v, context) for k, v in value.items()}
            elif isinstance(value, list):
                return [render_value(item, context) for item in value]
            return value

        return render_value(template, data)

    def _analyze_tender_file(self, tender_file: str) -> Dict[str, Any]:
        """分析招标文件（简化版）"""
        # 实际应用中应使用AI模型分析
        return {
            "project_name": Path(tender_file).stem if tender_file else "项目",
            "project_budget": "待定",
            "project_scope": "详见招标文件"
        }

    def _add_days(self, date_str: str, days: int) -> str:
        """添加天数到日期"""
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            new_date = date.replace(day=date.day + days)
            return new_date.strftime("%Y-%m-%d")
        except Exception:
            return date_str

    def _save_as_docx(self, content: Dict[str, Any], filename: str) -> str:
        """保存为Word文档"""
        if not HAS_DOCX:
            print("Warning: python-docx not installed, skipping DOCX generation")
            return ""

        doc = Document()
        output_path = self.output_dir / filename

        # 标题
        header = content.get("header", {})
        title = header.get("title", "文档")
        title_para = doc.add_heading(title, level=0)
        title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # 日期
        if "date" in header:
            doc.add_paragraph(f"日期: {header['date']}")

        # 正文
        body = content.get("body", {})
        for key, value in body.items():
            if isinstance(value, str):
                doc.add_paragraph(value)
            elif isinstance(value, list):
                for item in value:
                    doc.add_paragraph(f"• {item}" if isinstance(item, str) else str(item))
            elif isinstance(value, dict):
                doc.add_paragraph(f"{key}:")
                for k, v in value.items():
                    doc.add_paragraph(f"  {k}: {v}")

        doc.save(str(output_path))
        return str(output_path)

    def _save_proposal_as_docx(self, content: Dict[str, Any], filename: str) -> str:
        """保存投标文件为Word文档"""
        if not HAS_DOCX:
            return ""

        doc = Document()
        output_path = self.output_dir / filename

        header = content.get("header", {})
        body = content.get("body", {})

        # 封面
        doc.add_heading(header.get("title", "投标文件"), level=0)
        doc.add_paragraph(f"项目名称: {header.get('project_name', '')}")
        doc.add_paragraph(f"投标单位: {header.get('company_name', '')}")
        doc.add_paragraph(f"日期: {header.get('date', '')}")

        doc.add_page_break()

        # 正文
        doc.add_heading("一、公司概况", level=1)
        doc.add_paragraph(body.get("company_overview", ""))

        doc.add_heading("二、资质证明", level=1)
        for q in body.get("qualifications", []):
            doc.add_paragraph(f"• {q}")

        doc.add_heading("三、技术方案", level=1)
        doc.add_paragraph(body.get("tech_solution", ""))

        doc.add_heading("四、报价明细", level=1)
        quotation = body.get("quotation", {})
        for k, v in quotation.items():
            doc.add_paragraph(f"{k}: {v}")

        doc.add_heading("五、承诺书", level=1)
        doc.add_paragraph(body.get("commitment", ""))

        doc.save(str(output_path))
        return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="招投标文档智能生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s tender --project "智慧城市项目" --budget "500万"
  %(prog)s proposal --tender-file "招标文件.pdf" --company "XX科技"
  %(prog)s evaluation --project "智慧城市项目" --bidders "公司A:90:85:87.5,公司B:85:90:87.0"
  %(prog)s winning --project "智慧城市项目" --winner "公司A" --amount "480万"
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="文档类型")

    # 招标文件
    tender_parser = subparsers.add_parser("tender", help="生成招标文件")
    tender_parser.add_argument("--project", required=True, help="项目名称")
    tender_parser.add_argument("--budget", required=True, help="项目预算")
    tender_parser.add_argument("--scope", default="软件开发", help="项目范围")
    tender_parser.add_argument("--start", help="招标开始日期")
    tender_parser.add_argument("--end", help="招标截止日期")
    tender_parser.add_argument("--format", choices=["json", "docx"], default="json", help="输出格式")

    # 投标文件
    proposal_parser = subparsers.add_parser("proposal", help="生成投标文件")
    proposal_parser.add_argument("--tender-file", required=True, help="招标文件路径")
    proposal_parser.add_argument("--company", required=True, help="投标公司名称")
    proposal_parser.add_argument("--qualifications", help="公司资质，逗号分隔")
    proposal_parser.add_argument("--format", choices=["json", "docx"], default="json", help="输出格式")

    # 评标报告
    evaluation_parser = subparsers.add_parser("evaluation", help="生成评标报告")
    evaluation_parser.add_argument("--project", required=True, help="项目名称")
    evaluation_parser.add_argument("--bidders", required=True, help="投标方，格式: 名称:技术分:价格分:总分")
    evaluation_parser.add_argument("--experts", help="评标专家，逗号分隔")
    evaluation_parser.add_argument("--format", choices=["json", "docx"], default="json", help="输出格式")

    # 中标通知书
    winning_parser = subparsers.add_parser("winning", help="生成中标通知书")
    winning_parser.add_argument("--project", required=True, help="项目名称")
    winning_parser.add_argument("--winner", required=True, help="中标方名称")
    winning_parser.add_argument("--amount", required=True, help="中标金额")
    winning_parser.add_argument("--format", choices=["json", "docx"], default="json", help="输出格式")

    # 答疑函件
    answer_parser = subparsers.add_parser("answer", help="生成答疑函件")
    answer_parser.add_argument("--project", required=True, help="项目名称")
    answer_parser.add_argument("--question", required=True, help="问题内容")
    answer_parser.add_argument("--answer", help="答复内容")
    answer_parser.add_argument("--format", choices=["json", "docx"], default="json", help="输出格式")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    generator = BiddingGenerator()

    if args.command == "tender":
        result = generator.generate_tender(
            project_name=args.project,
            project_budget=args.budget,
            project_scope=args.scope,
            bidding_start=args.start,
            bidding_end=args.end,
            output_format=args.format
        )
    elif args.command == "proposal":
        qualifications = args.qualifications.split(",") if args.qualifications else None
        result = generator.generate_proposal(
            tender_file=args.tender_file,
            company_name=args.company,
            company_qualifications=qualifications,
            output_format=args.format
        )
    elif args.command == "evaluation":
        bidders = []
        for bidder_str in args.bidders.split(","):
            parts = bidder_str.split(":")
            if len(parts) >= 4:
                bidders.append({
                    "name": parts[0],
                    "tech_score": float(parts[1]),
                    "price_score": float(parts[2]),
                    "total": float(parts[3])
                })
        experts = args.experts.split(",") if args.experts else None
        result = generator.generate_evaluation(
            project_name=args.project,
            bidders=bidders,
            experts=experts,
            output_format=args.format
        )
    elif args.command == "winning":
        result = generator.generate_winning_notice(
            project_name=args.project,
            winner=args.winner,
            winning_amount=args.amount,
            output_format=args.format
        )
    elif args.command == "answer":
        result = generator.generate_answer_letter(
            project_name=args.project,
            question=args.question,
            answer=args.answer,
            output_format=args.format
        )
    else:
        parser.print_help()
        return

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()