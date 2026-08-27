"""知识图谱构建器"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """实体"""

    entity_id: str
    name: str
    entity_type: str  # text/table/formula/image
    subtype: str = ""  # person/organization/location/...
    description: str = ""
    page_num: int = 0
    bbox: tuple = (0, 0, 0, 0)
    properties: Dict[str, Any] = field(default_factory=dict)
    source_chunk_id: str = ""
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "name": self.name,
            "entity_type": self.entity_type,
            "subtype": self.subtype,
            "description": self.description,
            "page_num": self.page_num,
            "bbox": self.bbox,
            "properties": self.properties,
            "source_chunk_id": self.source_chunk_id,
            "confidence": self.confidence,
        }


@dataclass
class Relation:
    """关系"""

    relation_id: str
    source_id: str
    target_id: str
    relation_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "relation_id": self.relation_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type,
            "properties": self.properties,
            "confidence": self.confidence,
        }


@dataclass
class CrossModalEdge:
    """跨模态边"""

    edge_id: str
    source_entity_id: str
    target_entity_id: str
    source_modality: str  # text/table/formula/image
    target_modality: str
    edge_type: str  # refers_to/contains/related_to
    description: str = ""
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "source_entity_id": self.source_entity_id,
            "target_entity_id": self.target_entity_id,
            "source_modality": self.source_modality,
            "target_modality": self.target_modality,
            "edge_type": self.edge_type,
            "description": self.description,
            "confidence": self.confidence,
        }


@dataclass
class KGData:
    """知识图谱数据"""

    entities: List[Entity] = field(default_factory=list)
    relations: List[Relation] = field(default_factory=list)
    cross_modal_edges: List[CrossModalEdge] = field(default_factory=list)

    # 索引缓存
    _entity_index: Dict[str, Entity] = field(default_factory=dict, repr=False)
    _relation_index: Dict[str, List[Relation]] = field(default_factory=dict, repr=False)

    def __post_init__(self):
        """构建索引"""
        self._rebuild_index()

    def _rebuild_index(self) -> None:
        """重建索引"""
        self._entity_index = {e.entity_id: e for e in self.entities}
        self._relation_index = {}
        for r in self.relations:
            if r.source_id not in self._relation_index:
                self._relation_index[r.source_id] = []
            self._relation_index[r.source_id].append(r)

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """获取实体"""
        return self._entity_index.get(entity_id)

    def get_relations(self, entity_id: str) -> List[Relation]:
        """获取实体的关系"""
        return self._relation_index.get(entity_id, [])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entities": [e.to_dict() for e in self.entities],
            "relations": [r.to_dict() for r in self.relations],
            "cross_modal_edges": [e.to_dict() for e in self.cross_modal_edges],
            "stats": {
                "total_entities": len(self.entities),
                "total_relations": len(self.relations),
                "total_cross_modal_edges": len(self.cross_modal_edges),
                "entity_types": self._count_entity_types(),
                "relation_types": self._count_relation_types(),
            },
        }

    def _count_entity_types(self) -> Dict[str, int]:
        """统计实体类型"""
        counts = {}
        for e in self.entities:
            key = f"{e.entity_type}/{e.subtype}" if e.subtype else e.entity_type
            counts[key] = counts.get(key, 0) + 1
        return counts

    def _count_relation_types(self) -> Dict[str, int]:
        """统计关系类型"""
        counts = {}
        for r in self.relations:
            counts[r.relation_type] = counts.get(r.relation_type, 0) + 1
        return counts


class KGBuilder:
    """跨模态知识图谱构建器

    从解析的文档中构建知识图谱
    """

    def __init__(self, config: Optional[Any] = None):
        """初始化构建器

        Args:
            config: 配置对象
        """
        self.config = config
        self._entity_recognizer = None
        self._relation_extractor = None
        self._entity_linker = None

    async def build(self, parsed_doc: Dict[str, Any], **kwargs) -> KGData:
        """构建知识图谱

        Args:
            parsed_doc: 解析后的文档
            **kwargs: 额外参数

        Returns:
            KGData: 知识图谱数据
        """
        doc_id = parsed_doc.get("doc_id", str(uuid.uuid4())[:8])
        logger.info(f"开始构建知识图谱: {doc_id}")

        kg_data = KGData()

        # 1. 实体识别
        entities = await self._recognize_entities(parsed_doc, doc_id)
        kg_data.entities.extend(entities)

        # 2. 关系抽取
        relations = await self._extract_relations(entities)
        kg_data.relations.extend(relations)

        # 3. 跨模态边创建
        cross_modal_edges = await self._create_cross_modal_edges(entities, parsed_doc)
        kg_data.cross_modal_edges.extend(cross_modal_edges)

        # 重建索引
        kg_data._rebuild_index()

        logger.info(
            f"知识图谱构建完成: {len(kg_data.entities)} 实体, "
            f"{len(kg_data.relations)} 关系, {len(kg_data.cross_modal_edges)} 跨模态边"
        )

        return kg_data

    async def _recognize_entities(
        self, parsed_doc: Dict[str, Any], doc_id: str
    ) -> List[Entity]:
        """识别实体

        Args:
            parsed_doc: 解析后的文档
            doc_id: 文档ID

        Returns:
            List[Entity]: 识别出的实体列表
        """
        entities = []

        # 文本实体识别
        text_entities = await self._recognize_text_entities(parsed_doc, doc_id)
        entities.extend(text_entities)

        # 表格实体识别
        table_entities = await self._recognize_table_entities(parsed_doc, doc_id)
        entities.extend(table_entities)

        # 公式实体识别
        formula_entities = await self._recognize_formula_entities(parsed_doc, doc_id)
        entities.extend(formula_entities)

        # 图像实体识别
        image_entities = await self._recognize_image_entities(parsed_doc, doc_id)
        entities.extend(image_entities)

        return entities

    async def _recognize_text_entities(
        self, parsed_doc: Dict[str, Any], doc_id: str
    ) -> List[Entity]:
        """识别文本实体"""
        entities = []

        # 简单的关键词提取作为降级实现
        # 实际应该使用NER模型
        for page in parsed_doc.get("pages", []):
            page_num = page.get("page_num", 0)
            text = page.get("text", "")

            # 简单的词频统计
            words = self._extract_keywords(text)
            for i, word in enumerate(words[:20]):  # 限制数量
                entity = Entity(
                    entity_id=f"{doc_id}_text_ent_{page_num}_{i}",
                    name=word,
                    entity_type="text",
                    subtype="keyword",
                    page_num=page_num,
                    source_chunk_id=f"{doc_id}_text_{page_num}",
                    confidence=0.8,
                )
                entities.append(entity)

        return entities

    async def _recognize_table_entities(
        self, parsed_doc: Dict[str, Any], doc_id: str
    ) -> List[Entity]:
        """识别表格实体"""
        entities = []

        for i, table in enumerate(parsed_doc.get("tables", [])):
            page_num = table.get("page_num", 0)
            header = table.get("header", [])

            # 表格头作为实体
            for j, col_name in enumerate(header):
                entity = Entity(
                    entity_id=f"{doc_id}_table_ent_{page_num}_{i}_{j}",
                    name=col_name,
                    entity_type="table",
                    subtype="column_header",
                    page_num=page_num,
                    properties={
                        "table_id": f"table_{page_num}_{i}",
                        "column_index": j,
                    },
                    source_chunk_id=f"{doc_id}_table_{page_num}_{i}",
                    confidence=0.9,
                )
                entities.append(entity)

        return entities

    async def _recognize_formula_entities(
        self, parsed_doc: Dict[str, Any], doc_id: str
    ) -> List[Entity]:
        """识别公式实体"""
        entities = []

        for i, formula in enumerate(parsed_doc.get("formulas", [])):
            page_num = formula.get("page_num", 0)
            latex = formula.get("latex", "")

            # 公式作为实体
            entity = Entity(
                entity_id=f"{doc_id}_formula_ent_{page_num}_{i}",
                name=latex[:50],  # 截断长公式
                entity_type="formula",
                subtype="equation",
                description=latex,
                page_num=page_num,
                source_chunk_id=f"{doc_id}_formula_{page_num}_{i}",
                confidence=0.9,
            )
            entities.append(entity)

            # 提取公式中的变量
            variables = self._extract_formula_variables(latex)
            for j, var in enumerate(variables[:10]):  # 限制数量
                var_entity = Entity(
                    entity_id=f"{doc_id}_formula_var_{page_num}_{i}_{j}",
                    name=var,
                    entity_type="formula",
                    subtype="variable",
                    page_num=page_num,
                    properties={"formula_id": f"formula_{page_num}_{i}"},
                    source_chunk_id=f"{doc_id}_formula_{page_num}_{i}",
                    confidence=0.7,
                )
                entities.append(var_entity)

        return entities

    async def _recognize_image_entities(
        self, parsed_doc: Dict[str, Any], doc_id: str
    ) -> List[Entity]:
        """识别图像实体"""
        entities = []

        for i, image in enumerate(parsed_doc.get("images", [])):
            page_num = image.get("page_num", 0)
            description = image.get("description", "")

            # 图像描述中的关键词作为实体
            keywords = self._extract_keywords(description)
            for j, kw in enumerate(keywords[:5]):  # 限制数量
                entity = Entity(
                    entity_id=f"{doc_id}_image_ent_{page_num}_{i}_{j}",
                    name=kw,
                    entity_type="image",
                    subtype="description_keyword",
                    page_num=page_num,
                    properties={
                        "image_id": f"image_{page_num}_{i}",
                        "description": description[:100],
                    },
                    source_chunk_id=f"{doc_id}_image_{page_num}_{i}",
                    confidence=0.6,
                )
                entities.append(entity)

        return entities

    async def _extract_relations(self, entities: List[Entity]) -> List[Relation]:
        """抽取关系

        Args:
            entities: 实体列表

        Returns:
            List[Relation]: 关系列表
        """
        relations = []

        # 按页面分组实体
        page_entities: Dict[int, List[Entity]] = {}
        for e in entities:
            if e.page_num not in page_entities:
                page_entities[e.page_num] = []
            page_entities[e.page_num].append(e)

        # 同一页面的实体之间创建关系
        for page_num, page_ents in page_entities.items():
            for i, ent1 in enumerate(page_ents):
                for ent2 in page_ents[i + 1 :]:
                    # 检查是否有共现关系
                    if self._has_cooccurrence(ent1, ent2):
                        relation = Relation(
                            relation_id=f"rel_{ent1.entity_id}_{ent2.entity_id}",
                            source_id=ent1.entity_id,
                            target_id=ent2.entity_id,
                            relation_type="co_occurs_with",
                            confidence=0.6,
                        )
                        relations.append(relation)

        return relations

    async def _create_cross_modal_edges(
        self, entities: List[Entity], parsed_doc: Dict[str, Any]
    ) -> List[CrossModalEdge]:
        """创建跨模态边

        Args:
            entities: 实体列表
            parsed_doc: 解析后的文档

        Returns:
            List[CrossModalEdge]: 跨模态边列表
        """
        edges = []

        # 按source_chunk_id分组
        chunk_entities: Dict[str, List[Entity]] = {}
        for e in entities:
            if e.source_chunk_id not in chunk_entities:
                chunk_entities[e.source_chunk_id] = []
            chunk_entities[e.source_chunk_id].append(e)

        # 同一块中的不同模态实体之间创建边
        for chunk_id, chunk_ents in chunk_entities.items():
            modalities = {e.entity_type for e in chunk_ents}
            if len(modalities) > 1:
                # 选择代表性实体
                text_ent = next((e for e in chunk_ents if e.entity_type == "text"), None)
                table_ent = next((e for e in chunk_ents if e.entity_type == "table"), None)
                formula_ent = next((e for e in chunk_ents if e.entity_type == "formula"), None)
                image_ent = next((e for e in chunk_ents if e.entity_type == "image"), None)

                # 文本-表格边
                if text_ent and table_ent:
                    edge = CrossModalEdge(
                        edge_id=f"edge_{text_ent.entity_id}_{table_ent.entity_id}",
                        source_entity_id=text_ent.entity_id,
                        target_entity_id=table_ent.entity_id,
                        source_modality="text",
                        target_modality="table",
                        edge_type="contains",
                        description=f"文本提及表格: {table_ent.name}",
                        confidence=0.8,
                    )
                    edges.append(edge)

                # 文本-公式边
                if text_ent and formula_ent:
                    edge = CrossModalEdge(
                        edge_id=f"edge_{text_ent.entity_id}_{formula_ent.entity_id}",
                        source_entity_id=text_ent.entity_id,
                        target_entity_id=formula_ent.entity_id,
                        source_modality="text",
                        target_modality="formula",
                        edge_type="contains",
                        description=f"文本提及公式: {formula_ent.name}",
                        confidence=0.8,
                    )
                    edges.append(edge)

                # 文本-图像边
                if text_ent and image_ent:
                    edge = CrossModalEdge(
                        edge_id=f"edge_{text_ent.entity_id}_{image_ent.entity_id}",
                        source_entity_id=text_ent.entity_id,
                        target_entity_id=image_ent.entity_id,
                        source_modality="text",
                        target_modality="image",
                        edge_type="refers_to",
                        description=f"文本描述图像",
                        confidence=0.7,
                    )
                    edges.append(edge)

        return edges

    def _extract_keywords(self, text: str, max_keywords: int = 50) -> List[str]:
        """提取关键词（简单实现）

        Args:
            text: 文本
            max_keywords: 最大关键词数

        Returns:
            List[str]: 关键词列表
        """
        import re

        # 简单分词
        words = re.findall(r"\b[a-zA-Z\u4e00-\u9fff]{2,}\b", text.lower())

        # 简单停用词过滤
        stopwords = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "as", "is", "was", "are", "were",
            "这", "那", "是", "在", "和", "与", "或", "的", "了", "我",
        }

        keywords = [w for w in set(words) if w not in stopwords and len(w) > 2]

        # 返回频率最高的
        word_freq = {w: words.count(w) for w in keywords}
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

        return [w for w, _ in sorted_keywords[:max_keywords]]

    def _extract_formula_variables(self, latex: str) -> List[str]:
        """从LaTeX公式中提取变量

        Args:
            latex: LaTeX公式

        Returns:
            List[str]: 变量列表
        """
        import re

        # 匹配单个字母变量
        variables = re.findall(r"(?<![\\a-zA-Z])([a-zA-Z])(?![a-zA-Z])", latex)

        # 匹配带下标的变量
        subscript_vars = re.findall(r"\\([a-zA-Z])_\{([^}]+)\}", latex)
        variables.extend([v[0] + "_" + v[1][:3] for v in subscript_vars])

        return list(set(variables))

    def _has_cooccurrence(self, ent1: Entity, ent2: Entity) -> bool:
        """检查两个实体是否有共现关系

        Args:
            ent1: 实体1
            ent2: 实体2

        Returns:
            bool: 是否有共现
        """
        # 相同页面内，且类型不同
        if ent1.page_num != ent2.page_num:
            return False
        if ent1.entity_type == ent2.entity_type:
            return False

        # 简单的名称匹配
        name1 = ent1.name.lower()
        name2 = ent2.name.lower()

        # 名称相关
        if name1 in name2 or name2 in name1:
            return True

        # 共享关键词
        words1 = set(name1.split())
        words2 = set(name2.split())
        if words1 & words2:
            return True

        return False
