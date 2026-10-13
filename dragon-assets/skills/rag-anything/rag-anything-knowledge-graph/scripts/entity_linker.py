"""实体链接模块"""

import logging
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class EntityLinker:
    """实体链接器

    将识别出的实体链接到知识库中的已有实体
    """

    def __init__(self, config: Optional[Any] = None):
        """初始化实体链接器

        Args:
            config: 配置对象
        """
        self.config = config
        self._knowledge_base = None

    async def link_entity(
        self, entity: Any, knowledge_base: Optional[Any] = None
    ) -> Optional[str]:
        """链接实体到知识库

        Args:
            entity: 待链接的实体
            knowledge_base: 知识库（可选）

        Returns:
            Optional[str]: 链接到的实体ID，如果没有匹配则返回None
        """
        if knowledge_base is None:
            knowledge_base = self._knowledge_base

        if knowledge_base is None:
            return None

        try:
            # 简单的名称匹配
            query = entity.name
            matches = await knowledge_base.search(query, top_k=1)

            if matches and matches[0].score > 0.9:
                return matches[0].entity_id

        except Exception as e:
            logger.warning(f"实体链接失败: {str(e)}")

        return None

    async def link_batch(
        self, entities: List[Any], knowledge_base: Optional[Any] = None
    ) -> Dict[str, Optional[str]]:
        """批量链接实体

        Args:
            entities: 实体列表
            knowledge_base: 知识库（可选）

        Returns:
            Dict[str, Optional[str]]: 实体ID到链接ID的映射
        """
        results = {}

        for entity in entities:
            linked_id = await self.link_entity(entity, knowledge_base)
            results[entity.entity_id] = linked_id

        return results

    async def disambiguate(
        self, entity: Any, candidates: List[Any]
    ) -> Optional[Any]:
        """消歧

        Args:
            entity: 待消歧实体
            candidates: 候选实体列表

        Returns:
            Optional[Any]: 最佳匹配实体
        """
        if not candidates:
            return None

        # 简单的相似度计算
        best_match = None
        best_score = 0.0

        entity_name = entity.name.lower()

        for candidate in candidates:
            candidate_name = candidate.name.lower()

            # 计算简单相似度
            common_chars = set(entity_name) & set(candidate_name)
            score = len(common_chars) / max(len(entity_name), len(candidate_name), 1)

            if score > best_score:
                best_score = score
                best_match = candidate

        return best_match if best_score > 0.3 else None
