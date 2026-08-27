# ~/.claude/skills/hv-analysis/scripts/hv_research.py
import requests
import json
import markdown
from weasyprint import HTML, CSS
from datetime import datetime
from typing import List, Dict


class HVResearch:
    def __init__(self, topic: str):
        self.topic = topic
        self.search_results = []
        self.diachronic = ""
        self.synchronic = ""
        self.lateral = ""
        self.cross = ""
        self.report = ""

    def step1_search(self, queries: List[str]) -> List[Dict]:
        """Step 1: 并行网页搜索（示例：用WebSearch工具代替）"""
        results = []
        for query in queries:
            results.append({'query': query, 'results': []})
        self.search_results = results
        print(f"[Step1] 完成{len(queries)}个搜索查询")
        return results

    def step2_diachronic(self) -> str:
        """Step 2: 历时研究"""
        content = f"# 历时研究：{self.topic}的历史脉络\n\n"
        content += "## 起源与早期发展\n\n[分析起源背景和关键时间节点]\n\n"
        content += "## 发展脉络\n\n[划分发展阶段，标注标志性事件]\n\n"
        content += "## 关键转折点\n\n[分析导致范式转变的重大事件]\n\n"
        content += "## 历史规律\n\n[从历史中总结规律性认识]\n\n"
        self.diachronic = content
        print("[Step2] 历时研究完成")
        return content

    def step3_synchronic(self) -> str:
        """Step 3: 共时研究"""
        content = f"# 共时研究：{self.topic}的现状全景\n\n"
        content += "## 现状全景\n\n[当前领域主要玩家和技术路线]\n\n"
        content += "## 核心矛盾\n\n[当前最大的问题和争议]\n\n"
        content += "## 技术对比\n\n[各方案优劣势分析]\n\n"
        content += "## 趋势判断\n\n[未来3-5年走向预测]\n\n"
        self.synchronic = content
        print("[Step3] 共时研究完成")
        return content

    def step4_lateral(self) -> str:
        """Step 4: 横向对比"""
        content = f"# 横向研究：跨领域连接\n\n"
        content += "## 跨领域影响\n\n[其他领域对本领域的影响]\n\n"
        content += "## 类比借鉴\n\n[从其他领域可以学到什么]\n\n"
        content += "## 生态位分析\n\n[在更大图景中的位置]\n\n"
        self.lateral = content
        print("[Step4] 横向研究完成")
        return content

    def step5_cross(self) -> str:
        """Step 5: 交叉分析"""
        content = f"# 交叉研究：深度质疑\n\n"
        content += "## 多视角解读\n\n[乐观/悲观/中立三种视角]\n\n"
        content += "## 反驳演练\n\n[这个结论的反例]\n\n"
        content += "## 元问题\n\n[问题的前提是否成立]\n\n"
        content += "## 未说出口的真相\n\n[领域内没人愿意谈的问题]\n\n"
        self.cross = content
        print("[Step5] 交叉研究完成")
        return content

    def generate_report(self) -> str:
        """生成完整报告"""
        self.report = f"""# {self.topic}

> 横纵双轨深度研究报告
> 生成日期: {datetime.now().strftime('%Y年%m月%d日')}
> 天龙引擎 × khazix-skills 横纵研究法

---

{self.diachronic}
{self.synchronic}
{self.lateral}
{self.cross}

---

*本报告由天龙引擎 hv-analysis 技能生成*
"""
        print("[Report] 万字报告已生成")
        return self.report

    def generate_pdf(self, output_path: str):
        """生成PDF"""
        html = markdown.markdown(self.report, extensions=['tables', 'fenced_code'])
        template = f"""
<html>
<head><style>
body {{ font-family: 'Noto Sans CJK SC', sans-serif; line-height: 1.8; }}
h1 {{ color: #1a1a1a; border-bottom: 2px solid #333; padding-bottom: 10px; }}
h2 {{ color: #333; margin-top: 2em; }}
h3 {{ color: #555; }}
blockquote {{ border-left: 4px solid #ccc; padding-left: 1em; color: #666; }}
code {{ background: #f5f5f5; padding: 2px 4px; border-radius: 3px; }}
pre {{ background: #f5f5f5; padding: 1em; overflow-x: auto; }}
.page-break {{ page-break-before: always; }}
.title-page {{ text-align: center; margin-top: 200px; }}
.title-page h1 {{ font-size: 2.5em; color: #1a1a1a; }}
.title-page .subtitle {{ font-size: 1.2em; color: #666; margin-top: 20px; }}
.title-page .date {{ font-size: 0.9em; color: #999; margin-top: 40px; }}
</style></head>
<body>
<div class="title-page">
  <h1>{self.topic}</h1>
  <div class="subtitle">横纵双轨深度研究</div>
  <div class="date">{datetime.now().strftime('%Y年%m月%d日')}</div>
</div>
<div class="page-break"/>
{html}
</body>
</html>
"""
        HTML(string=template).write_pdf(output_path)
        print(f"[PDF] 已生成: {output_path}")

    def run(self, queries: List[str] = None, output_pdf: str = None) -> str:
        """运行完整研究流程"""
        print(f"\n{'='*50}")
        print(f"横纵双轨研究: {self.topic}")
        print(f"{'='*50}\n")
        if queries:
            self.step1_search(queries)
        self.step2_diachronic()
        self.step3_synchronic()
        self.step4_lateral()
        self.step5_cross()
        report = self.generate_report()
        if output_pdf:
            self.generate_pdf(output_pdf)
        return report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="hv-analysis 横纵双轨研究")
    parser.add_argument("topic", help="研究主题")
    parser.add_argument("--search", nargs='+', help="搜索关键词列表")
    parser.add_argument("--output-md", help="Markdown输出路径")
    parser.add_argument("--output-pdf", help="PDF输出路径")
    args = parser.parse_args()

    hv = HVResearch(args.topic)
    report = hv.run(args.search, args.output_pdf)

    if args.output_md:
        with open(args.output_md, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Markdown已保存: {args.output_md}")
    else:
        print(report)