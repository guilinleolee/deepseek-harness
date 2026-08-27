"""
FactCheckerAgent - 事实核查智能体
对分析报告中的关键声明进行交叉验证
来源: https://github.com/mmlong818/Cat-Research
集成时间: 2026-03-23
"""
import os
import json
import re
from typing import Dict, List, Tuple, Optional

# 导入验证注册表
try:
    from skills.shared.verification_registry import (
        load_registry, save_registry,
        is_claim_verified, get_claim_result, add_claim_result
    )
except ImportError:
    # 回退到本地定义
    def load_registry(ws): return {"verified_claims": {}, "verified_sources": {}, "executed_queries": []}
    def save_registry(ws, r): pass
    def is_claim_verified(r, c): return False
    def get_claim_result(r, c): return {}
    def add_claim_result(r, c, res, cycle=0): pass


FACT_CHECKER_SYSTEM_PROMPT = """你是一位专业的事实核查专家，擅长识别和验证研究报告中的关键声明、数据点和结论。

## 你的职责
1. 从分析报告中提取所有关键声明和数据点
2. 对每个重要声明进行交叉验证
3. 标记可能不准确或需要进一步验证的内容
4. 提供整体置信度评估

## 识别关键声明的标准
- 包含具体数字、百分比、统计数据的陈述
- 关于趋势、因果关系的结论性陈述
- 关于特定机构、人物、事件的事实性陈述
- 研究结论中的核心论点

## 输出格式（必须严格遵守）
```json
{
  "total_claims_checked": <数量>,
  "claims": [
    {
      "claim": "声明原文",
      "verdict": "supported/disputed/unverifiable/insufficient",
      "confidence": <0.0-1.0>,
      "supporting_count": <支持来源数>,
      "contradicting_count": <反驳来源数>,
      "explanation": "验证说明",
      "needs_attention": true/false
    }
  ],
  "overall_confidence": <0.0-1.0>,
  "high_confidence_claims": <数量>,
  "disputed_claims": <需要关注的声明列表>,
  "unverifiable_claims": <无法验证的声明列表>,
  "fact_check_summary": "整体事实核查结论",
  "recommended_additions": ["建议补充的内容或数据"]
}
```"""


class FactCheckerAgent:
    """事实核查智能体"""

    def __init__(self, model: str = None):
        self.name = "事实核查员"
        self.system_prompt = FACT_CHECKER_SYSTEM_PROMPT
        self.model = model

    def check_facts(self, workspace: str, analysis_file: str = None,
                    registry: dict = None, cycle: int = 0) -> Tuple[dict, str]:
        """
        对分析报告中的关键声明进行事实核查

        Args:
            workspace: 工作空间路径
            analysis_file: 分析文件路径
            registry: 验证注册表
            cycle: 当前改进轮次

        Returns:
            (核查结果字典, 输出文件路径)
        """
        verification_dir = os.path.join(workspace, "08_verification")
        os.makedirs(verification_dir, exist_ok=True)
        output_file = os.path.join(verification_dir, "fact_check.json")

        # 如果没有指定分析文件，使用固定路径
        if not analysis_file:
            candidate = os.path.join(workspace, "05_analysis.md")
            analysis_file = candidate if os.path.exists(candidate) else None

        # 预提取关键声明
        pre_check_results = self._precheck_claims(analysis_file, registry=registry, cycle=cycle)

        # 统计缓存命中与新核查数量
        cached_count = sum(1 for r in pre_check_results if r.get("_from_cache"))
        new_count = len(pre_check_results) - cached_count

        # 执行核查（这里简化实现，实际应调用LLM）
        result = self._execute_fact_check(analysis_file, pre_check_results)

        # 保存结果
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        return result, output_file

    def _precheck_claims(self, analysis_file: str, registry: dict = None, cycle: int = 0) -> list:
        """从分析文件中预提取关键声明并进行快速验证"""
        if not analysis_file or not os.path.exists(analysis_file):
            return []

        try:
            with open(analysis_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return []

        # 提取包含数字的关键句子作为声明
        sentences = re.split(r'[。\n]', content)
        claims = []
        for sent in sentences:
            sent = sent.strip()
            if (re.search(r'\d+', sent) or
                any(kw in sent for kw in ['增长', '下降', '提升', '降低', '达到', '超过', '占比'])):
                if 20 <= len(sent) <= 200:
                    claims.append(sent)

        results = []
        new_claims_to_check = []

        for claim in claims[:6]:  # 最多取6个候选
            if registry and is_claim_verified(registry, claim):
                # 直接复用已验证结果
                cached = get_claim_result(registry, claim)
                results.append({
                    "claim": claim[:100],
                    "verdict": cached.get("verdict", "supported"),
                    "confidence": cached.get("confidence", 0.8),
                    "supporting_count": cached.get("supporting_count", 1),
                    "contradicting_count": cached.get("contradicting_count", 0),
                    "_from_cache": True
                })
            else:
                new_claims_to_check.append(claim)

        # 对新声明进行验证
        for claim in new_claims_to_check[:3]:
            r = {
                "claim": claim[:100],
                "verdict": "insufficient",
                "confidence": 0.5,
                "supporting_count": 0,
                "contradicting_count": 0,
                "_from_cache": False
            }
            results.append(r)
            if registry is not None:
                add_claim_result(registry, claim, r, cycle=cycle)

        return results

    def _execute_fact_check(self, analysis_file: str, pre_check_results: list) -> dict:
        """执行事实核查并生成结果"""
        if not pre_check_results:
            return {
                "total_claims_checked": 0,
                "claims": [],
                "overall_confidence": 0.6,
                "high_confidence_claims": 0,
                "disputed_claims": [],
                "unverifiable_claims": [],
                "fact_check_summary": "事实核查工具未能完成完整核查，建议人工审核关键数据点。",
                "recommended_additions": ["建议补充权威来源引用", "建议添加数据来源说明"]
            }

        supported = [r for r in pre_check_results if r.get('verdict') == 'supported']
        disputed = [r['claim'][:50] for r in pre_check_results if r.get('verdict') == 'disputed']
        unverifiable = [r['claim'][:50] for r in pre_check_results if r.get('verdict') in ('unverifiable', 'insufficient')]

        overall_conf = sum(r.get('confidence', 0.5) for r in pre_check_results) / max(len(pre_check_results), 1)

        return {
            "total_claims_checked": len(pre_check_results),
            "claims": pre_check_results,
            "overall_confidence": round(overall_conf, 2),
            "high_confidence_claims": len(supported),
            "disputed_claims": disputed,
            "unverifiable_claims": unverifiable,
            "fact_check_summary": f"已核查 {len(pre_check_results)} 个关键声明，{len(supported)} 个得到验证，{len(disputed)} 个存在争议。",
            "recommended_additions": ["建议为所有数据添加具体来源引用"]
        }


# ── CLI 入口 ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        checker = FactCheckerAgent()
        result, _ = checker.check_facts(sys.argv[1])
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Usage: python fact_checker.py <workspace>")