"""关系抽取模块"""

import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class RelationExtractor:
    """关系抽取器

    从文本和实体中抽取关系
    """

    # 关系模式
    RELATION_PATTERNS = {
        "has_attribute": [
            (r"(\w+) is (?:a|an) (\w+)", "is_a"),
            (r"(\w+) is (?:known as|called) (\w+)", "also_known_as"),
        ],
        "related_to": [
            (r"(\w+) and (\w+) are (?:related|connected)", "related_to"),
            (r"(\w+) is associated with (\w+)", "associated_with"),
        ],
        "part_of": [
            (r"(\w+) is (?:part of|a member of) (\w+)", "part_of"),
            (r"(\w+) belongs to (\w+)", "belongs_to"),
        ],
        "causes": [
            (r"(\w+) (?:causes|leads to|result in) (\w+)", "causes"),
            (r"(\w+) (?:results in|brings about) (\w+)", "results_in"),
        ],
    }

    def __init__(self, config: Optional[Any] = None):
        """初始化关系抽取器

        Args:
            config: 配置对象
        """
        self.config = config

    async def extract_relations(
        self, text: str, entities: List[Any]
    ) -> List[Dict[str, Any]]:
        """从文本中抽取关系

        Args:
            text: 文本
            entities: 实体列表

        Returns:
            List[Dict[str, Any]]: 抽取的关系列表
        """
        relations = []

        # 使用模式匹配抽取关系
        for relation_type, patterns in self.RELATION_PATTERNS.items():
            for pattern, sub_type in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    source_name = match.group(1)
                    target_name = match.group(2)

                    # 检查实体是否在匹配中
                    source_ent = self._find_entity_by_name(source_name, entities)
                    target_ent = self._find_entity_by_name(target_name, entities)

                    if source_ent and target_ent:
                        relations.append({
                            "source_id": source_ent.entity_id,
                            "target_id": target_ent.entity_id,
                            "relation_type": relation_type,
                            "sub_type": sub_type,
                            "confidence": 0.8,
                        })

        return relations

    async def extract_from_entity_pair(
        self, entity1: Any, entity2: Any, context: str = ""
    ) -> Optional[Dict[str, Any]]:
        """从实体对抽取关系

        Args:
            entity1: 实体1
            entity2: 实体2
            context: 上下文文本

        Returns:
            Optional[Dict[str, Any]]: 关系（如果有）
        """
        # 简单的共现检测
        if entity1.page_num == entity2.page_num:
            # 同页面，检查名称相似度
            name1 = entity1.name.lower()
            name2 = entity2.name.lower()

            if name1 in name2 or name2 in name1:
                return {
                    "source_id": entity1.entity_id,
                    "target_id": entity2.entity_id,
                    "relation_type": "related_to",
                    "sub_type": "name_similarity",
                    "confidence": 0.7,
                }

        return None

    async def extract_cross_modal_relations(
        self,
        text_entity: Any,
        table_entity: Any,
        formula_entity: Any = None,
        image_entity: Any = None,
    ) -> List[Dict[str, Any]]:
        """抽取跨模态关系

        Args:
            text_entity: 文本实体
            table_entity: 表格实体
            formula_entity: 公式实体（可选）
            image_entity: 图像实体（可选）

        Returns:
            List[Dict[str, Any]]: 跨模态关系列表
        """
        relations = []

        # 文本-表格关系
        if text_entity and table_entity:
            relations.append({
                "source_id": text_entity.entity_id,
                "target_id": table_entity.entity_id,
                "source_modality": "text",
                "target_modality": "table",
                "relation_type": "mentions",
                "confidence": 0.8,
            })

        # 文本-公式关系
        if text_entity and formula_entity:
            relations.append({
                "source_id": text_entity.entity_id,
                "target_id": formula_entity.entity_id,
                "source_modality": "text",
                "target_modality": "formula",
                "relation_type": "explains",
                "confidence": 0.8,
            })

        # 文本-图像关系
        if text_entity and image_entity:
            relations.append({
                "source_id": text_entity.entity_id,
                "target_id": image_entity.entity_id,
                "source_modality": "text",
                "target_modality": "image",
                "relation_type": "describes",
                "confidence": 0.7,
            })

        return relations

    def _find_entity_by_name(
        self, name: str, entities: List[Any]
    ) -> Optional[Any]:
        """根据名称查找实体

        Args:
            name: 实体名称
            entities: 实体列表

        Returns:
            Optional[Any]: 找到的实体
        """
        name_lower = name.lower()
        for entity in entities:
            if entity.name.lower() == name_lower:
                return entity
        return None

    def _calculate_confidence(
        self, match_score: float, context_score: float
    ) -> float:
        """计算关系置信度

        Args:
            match_score: 匹配分数
            context_score: 上下文分数

        Returns:
            float: 置信度
        """
        return (match_score * 0.6 + context_score * 0.4)
