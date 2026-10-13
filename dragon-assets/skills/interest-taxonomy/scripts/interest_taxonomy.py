#!/usr/bin/env python3
"""
Interest Taxonomy - 兴趣分类体系+动态调整
配合TrendRadar实现精准舆情监控
来源: sansan0/TrendRadar 56k Stars
"""

import json
import os
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


@dataclass
class InterestCategory:
    """兴趣分类"""
    name: str           # 分类名称
    priority: int       # 优先级分 (1-10)
    keywords: list[str]  # 关键词列表
    weight: float = 1.0  # 权重
    score_threshold: float = 0.7  # 告警阈值
    is_active: bool = True
    last_triggered: str = ""
    trigger_count: int = 0


@dataclass
class TaxonomyConfig:
    """分类配置"""
    categories: dict[str, InterestCategory] = field(default_factory=dict)
    version: str = "1.0"
    last_updated: str = ""


class InterestTaxonomy:
    """兴趣分类管理器"""

    def __init__(self, config_path: str = "config/ai_interests.txt"):
        self.config_path = config_path
        self.categories: dict[str, InterestCategory] = {}
        self._load_config()

    def _load_config(self):
        """加载分类配置"""
        if not os.path.exists(self.config_path):
            self._init_default_taxonomy()
            return

        with open(self.config_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                parts = line.split("|")
                if len(parts) >= 4:
                    name, priority, keywords_str = parts[0], int(parts[1]), parts[2]
                    weight = float(parts[3]) if len(parts) > 3 else 1.0
                    threshold = float(parts[4]) if len(parts) > 4 else 0.7

                    keywords = [k.strip() for k in keywords_str.split(",")]

                    self.categories[name] = InterestCategory(
                        name=name,
                        priority=priority,
                        keywords=keywords,
                        weight=weight,
                        score_threshold=threshold
                    )

    def _init_default_taxonomy(self):
        """初始化默认分类体系"""
        default_taxonomy = [
            ("科技", 10, "AI,大模型,LLM,ChatGPT,GPT,机器学习,深度学习", 1.0, 0.7),
            ("金融", 10, "比特币,以太坊,加密货币,区块链,股票,基金,证券", 1.0, 0.7),
            ("地缘政治", 8, "贸易战,制裁,外交,中美,一带一路,RCEP", 0.9, 0.6),
            ("消费", 7, "电商,零售,消费者,新零售,直播带货", 0.8, 0.6),
            ("汽车", 6, "新能源汽车,自动驾驶,电动车,特斯拉,比亚迪", 0.7, 0.5),
            ("房地产", 5, "房价,调控,地产,万科,恒大,碧桂园", 0.6, 0.5),
            ("能源", 5, "光伏,风电,储能,氢能,碳中和,石油", 0.6, 0.5),
            ("医疗", 5, "疫苗,创新药,医疗器械,医保,集采", 0.6, 0.5),
            ("教育", 4, "K12,职业教育,考研,留学,双减", 0.5, 0.4),
            ("娱乐", 4, "电影,剧集,综艺,明星,短视频", 0.5, 0.4),
            ("体育", 3, "足球,篮球,NBA,奥运,亚运", 0.4, 0.3),
            ("旅游", 3, "旅游,酒店,航空,景区,出境游", 0.4, 0.3),
            ("食品", 3, "餐饮,奶茶,咖啡,预制菜,食品安全", 0.4, 0.3),
            ("环保", 2, "碳中和,ESG,可持续发展,垃圾分类", 0.3, 0.3),
            ("军事", 2, "军演,武器,国防,航母,战机", 0.3, 0.3),
        ]

        for name, priority, keywords_str, weight, threshold in default_taxonomy:
            keywords = keywords_str.split(",")
            self.categories[name] = InterestCategory(
                name=name,
                priority=priority,
                keywords=keywords,
                weight=weight,
                score_threshold=threshold
            )

        self._save_config()

    def _save_config(self):
        """保存分类配置"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

        with open(self.config_path, "w", encoding="utf-8") as f:
            f.write("# AI兴趣分类配置: name|priority|keywords|weight|score_threshold\n")
            f.write("# 优先级: 1-10 (10最高)\n\n")

            for cat in self.categories.values():
                keywords_str = ",".join(cat.keywords)
                f.write(f"{cat.name}|{cat.priority}|{keywords_str}|{cat.weight}|{cat.score_threshold}\n")

    def add_category(self, name: str, priority: int, keywords: list[str],
                     weight: float = 1.0, threshold: float = 0.7) -> bool:
        """添加分类"""
        if name in self.categories:
            return False

        self.categories[name] = InterestCategory(
            name=name,
            priority=priority,
            keywords=keywords,
            weight=weight,
            score_threshold=threshold
        )
        self._save_config()
        return True

    def remove_category(self, name: str) -> bool:
        """删除分类"""
        if name not in self.categories:
            return False
        del self.categories[name]
        self._save_config()
        return True

    def update_priority(self, name: str, priority: int) -> bool:
        """更新优先级"""
        if name not in self.categories:
            return False
        self.categories[name].priority = priority
        self._save_config()
        return True

    def match_content(self, title: str, content: str = "") -> list[dict]:
        """匹配内容返回分类"""
        text = (title + " " + content).lower()
        matches = []

        for cat in self.categories.values():
            if not cat.is_active:
                continue

            # 关键词匹配
            matched_keywords = []
            for kw in cat.keywords:
                if kw.lower() in text:
                    matched_keywords.append(kw)

            if matched_keywords:
                # 计算基础分数
                base_score = len(matched_keywords) / len(cat.keywords)

                # 应用权重和优先级
                final_score = base_score * cat.weight * (cat.priority / 10)

                matches.append({
                    "category": cat.name,
                    "priority": cat.priority,
                    "score": round(final_score, 3),
                    "matched_keywords": matched_keywords,
                    "triggered": final_score >= cat.score_threshold
                })

        # 按分数排序
        matches.sort(key=lambda x: x["score"], reverse=True)
        return matches

    def get_top_category(self, title: str, content: str = "") -> Optional[dict]:
        """获取最高匹配分类"""
        matches = self.match_content(title, content)
        return matches[0] if matches else None

    def get_high_priority_categories(self) -> list[InterestCategory]:
        """获取高优先级分类 (priority >= 8)"""
        return [c for c in self.categories.values()
                if c.is_active and c.priority >= 8]

    def get_stats(self) -> dict:
        """获取统计信息"""
        active = [c for c in self.categories.values() if c.is_active]
        total = len(self.categories)

        by_priority = {"P8+": 0, "P5-7": 0, "P1-4": 0}
        for c in active:
            if c.priority >= 8:
                by_priority["P8+"] += 1
            elif c.priority >= 5:
                by_priority["P5-7"] += 1
            else:
                by_priority["P1-4"] += 1

        return {
            "total_count": total,
            "active_count": len(active),
            "by_priority": by_priority,
            "top_triggered": self._get_top_triggered()
        }

    def _get_top_triggered(self) -> list[dict]:
        """获取触发最多的分类"""
        sorted_cats = sorted(
            self.categories.values(),
            key=lambda c: c.trigger_count,
            reverse=True
        )
        return [
            {"name": c.name, "trigger_count": c.trigger_count}
            for c in sorted_cats[:5]
        ]

    def record_trigger(self, name: str):
        """记录分类触发"""
        if name in self.categories:
            from datetime import datetime
            self.categories[name].last_triggered = datetime.now().isoformat()
            self.categories[name].trigger_count += 1
            self._save_config()

    def list_categories(self) -> list[dict]:
        """列出所有分类"""
        return [
            {
                "name": c.name,
                "priority": c.priority,
                "keywords": c.keywords[:5],
                "weight": c.weight,
                "threshold": c.score_threshold,
                "is_active": c.is_active,
                "trigger_count": c.trigger_count
            }
            for c in self.categories.values()
        ]

    def export_taxonomy(self) -> dict:
        """导出分类体系"""
        return {
            "version": "1.0",
            "categories": [
                {
                    "name": c.name,
                    "priority": c.priority,
                    "keywords": c.keywords,
                    "weight": c.weight,
                    "threshold": c.score_threshold
                }
                for c in self.categories.values()
            ]
        }


# ============ 天龙引擎集成函数 ============

def classify_news(title: str, content: str = "") -> str:
    """快速分类新闻"""
    taxonomy = InterestTaxonomy()
    result = taxonomy.get_top_category(title, content)
    if result:
        return f"[{result['category']}] 评分:{result['score']:.2f} 关键词:{','.join(result['matched_keywords'][:3])}"
    return "未匹配任何分类"


def batch_classify(news_items: list[dict]) -> list[dict]:
    """批量分类新闻"""
    taxonomy = InterestTaxonomy()
    results = []
    for item in news_items:
        result = taxonomy.get_top_category(
            item.get("title", ""),
            item.get("content", "")
        )
        results.append({
            "item": item,
            "primary_category": result["category"] if result else None,
            "score": result["score"] if result else 0,
            "all_matches": taxonomy.match_content(
                item.get("title", ""),
                item.get("content", "")
            )
        })
    return results


def show_taxonomy_status() -> str:
    """显示分类体系状态"""
    taxonomy = InterestTaxonomy()
    stats = taxonomy.get_stats()
    cats = taxonomy.list_categories()

    lines = [f"📊 兴趣分类体系: 共{stats['total_count']}个分类, {stats['active_count']}个激活"]
    lines.append(f"   P8+: {stats['by_priority']['P8+']} P5-7: {stats['by_priority']['P5-7']} P1-4: {stats['by_priority']['P1-4']}")
    lines.append("\n📋 分类列表:")

    for c in sorted(cats, key=lambda x: x["priority"], reverse=True)[:10]:
        icon = "✅" if c["is_active"] else "⏸️"
        lines.append(f"  {icon} [{c['priority']}] {c['name']} - {','.join(c['keywords'][:3])}")

    return "\n".join(lines)


if __name__ == "__main__":
    # 测试
    taxonomy = InterestTaxonomy()
    print(f"加载 {len(taxonomy.categories)} 个分类")
    print(show_taxonomy_status())

    # 测试分类
    result = classify_news("OpenAI发布GPT-5新功能", "ChatGPT迎来重大更新")
    print(f"\n分类结果: {result}")
