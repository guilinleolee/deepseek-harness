"""
GraphRAG Builder - 知识图谱构建与推理
Based on MiroFish GraphRAG module
"""

import os
import json
import asyncio
from typing import Optional, Dict, List, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import re


class EntityType(Enum):
    """实体类型"""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    EVENT = "event"
    CONCEPT = "concept"
    PRODUCT = "product"
    ROLE = "role"


class RelationType(Enum):
    """关系类型"""
    WORKS_FOR = "works_for"
    LOCATED_IN = "located_in"
    RELATED_TO = "related_to"
    PART_OF = "part_of"
    INFLUENCES = "influences"
    OPPOSES = "opposes"
    HAS_ROLE = "has_role"
    CREATED = "created"
    USES = "uses"


@dataclass
class Entity:
    """实体"""
    name: str
    entity_type: EntityType
    attributes: Dict[str, Any] = field(default_factory=dict)
    mentions: int = 1
    sources: List[str] = field(default_factory=list)


@dataclass
class Relation:
    """关系"""
    source: str
    target: str
    relation_type: RelationType
    confidence: float = 1.0
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Persona:
    """人物设定"""
    name: str
    demographics: Dict[str, Any] = field(default_factory=dict)
    personality: Dict[str, float] = field(default_factory=dict)
    interests: List[str] = field(default_factory=list)
    values: List[str] = field(default_factory=list)
    communication_style: str = ""
    background: str = ""
    goals: List[str] = field(default_factory=list)
    challenges: List[str] = field(default_factory=list)


@dataclass
class KnowledgeGraph:
    """知识图谱"""
    entities: Dict[str, Entity] = field(default_factory=dict)
    relations: List[Relation] = field(default_factory=list)
    personas: Dict[str, Persona] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class EntityExtractor:
    """实体抽取器"""

    def __init__(
        self,
        llm_api_key: Optional[str] = None,
        model: str = "gpt-4o"
    ):
        self.llm_api_key = llm_api_key or os.getenv("OPENAI_API_KEY")
        self.model = model

        # 实体识别模式
        self.patterns = {
            EntityType.PERSON: [
                r'(?:张三|李四|王五|[A-Z][a-z]+\s+[A-Z][a-z]+)',
                r'(\w+(?:先生|女士|博士|教授|经理|总监|CEO))'
            ],
            EntityType.ORGANIZATION: [
                r'(\w+(?:公司|集团|企业|机构|大学|研究院))',
                r'([A-Z][A-Za-z]+(?:Inc|Corp|LLC|Ltd))'
            ],
            EntityType.LOCATION: [
                r'(\w+(?:市|省|区|县|镇|村))',
                r'((?:北京|上海|广州|深圳|杭州|成都|武汉|南京))'
            ],
            EntityType.CONCEPT: [
                r'((?:AI|人工智能|机器学习|深度学习|区块链|云计算|大数据))',
                r'(\w+(?:技术|系统|平台|框架|方法))'
            ]
        }

    async def extract(
        self,
        text: str,
        entity_types: Optional[List[EntityType]] = None
    ) -> List[Entity]:
        """从文本中抽取实体"""
        entities: Dict[str, Entity] = {}
        types = entity_types or list(EntityType)

        for entity_type in types:
            if entity_type in self.patterns:
                for pattern in self.patterns[entity_type]:
                    matches = re.findall(pattern, text)
                    for match in matches:
                        name = match if isinstance(match, str) else match[0]
                        if name in entities:
                            entities[name].mentions += 1
                        else:
                            entities[name] = Entity(
                                name=name,
                                entity_type=entity_type
                            )

        return list(entities.values())


class RelationExtractor:
    """关系抽取器"""

    def __init__(
        self,
        llm_api_key: Optional[str] = None,
        model: str = "gpt-4o"
    ):
        self.llm_api_key = llm_api_key or os.getenv("OPENAI_API_KEY")
        self.model = model

        # 关系识别模式
        self.patterns = {
            RelationType.WORKS_FOR: [
                r'(\w+).{0,5}(?:在|任职|工作).{0,5}(\w+(?:公司|集团))',
                r'(\w+).{0,5}(?:担任|是).{0,5}(\w+(?:经理|总监|CEO))'
            ],
            RelationType.LOCATED_IN: [
                r'(\w+(?:公司|机构)).{0,5}(?:位于|在).{0,5}(\w+(?:市|省))',
                r'(\w+).{0,5}(?:住在|居住在).{0,5}(\w+(?:市|区))'
            ],
            RelationType.RELATED_TO: [
                r'(\w+).{0,5}(?:与|和|跟).{0,5}(\w+).{0,5}(?:相关|有关|关联)'
            ],
            RelationType.HAS_ROLE: [
                r'(\w+).{0,5}(?:担任|是|担任).{0,5}(\w+(?:经理|总监|工程师|设计师))'
            ]
        }

    async def extract(
        self,
        text: str,
        entities: Optional[List[str]] = None
    ) -> List[Relation]:
        """从文本中抽取关系"""
        relations: List[Relation] = []

        for relation_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    if isinstance(match, tuple) and len(match) >= 2:
                        source, target = match[0], match[1]
                        relations.append(Relation(
                            source=source,
                            target=target,
                            relation_type=relation_type,
                            confidence=0.8
                        ))

        return relations


class PersonaGenerator:
    """人物设定生成器"""

    def __init__(
        self,
        llm_api_key: Optional[str] = None,
        model: str = "gpt-4o"
    ):
        self.llm_api_key = llm_api_key or os.getenv("OPENAI_API_KEY")
        self.model = model

    async def generate(
        self,
        text: str,
        character_name: str
    ) -> Optional[Persona]:
        """生成人物设定"""
        # 简化的生成逻辑
        # 实际实现应该调用LLM

        # 提取年龄
        age_match = re.search(r'(\d+)(?:岁|年)', text)
        age = int(age_match.group(1)) if age_match else 30

        # 提取角色
        role_match = re.search(
            r'(?:担任|是|担任)(\w+(?:经理|总监|工程师|设计师|CEO))',
            text
        )
        role = role_match.group(1) if role_match else "未知"

        # 生成人设
        persona = Persona(
            name=character_name,
            demographics={
                "age": age,
                "occupation": role
            },
            personality={
                "openness": 0.5,
                "conscientiousness": 0.5,
                "extraversion": 0.5,
                "agreeableness": 0.5,
                "neuroticism": 0.5
            },
            interests=[],
            values=[],
            communication_style="professional",
            background=f"Auto-generated background for {character_name}"
        )

        return persona


class GraphRAGBuilder:
    """知识图谱构建器"""

    def __init__(
        self,
        llm_api_key: Optional[str] = None,
        model: str = "gpt-4o"
    ):
        self.llm_api_key = llm_api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.entity_extractor = EntityExtractor(llm_api_key, model)
        self.relation_extractor = RelationExtractor(llm_api_key, model)
        self.persona_generator = PersonaGenerator(llm_api_key, model)

    async def build_graph(
        self,
        text: str,
        output_format: str = "json"
    ) -> Dict[str, Any]:
        """从文本构建知识图谱"""
        # 抽取实体
        entities = await self.entity_extractor.extract(text)

        # 抽取关系
        entity_names = [e.name for e in entities]
        relations = await self.relation_extractor.extract(text, entity_names)

        # 生成人物设定
        personas = {}
        person_entities = [e for e in entities if e.entity_type == EntityType.PERSON]
        for person in person_entities[:5]:  # 限制数量
            persona = await self.persona_generator.generate(text, person.name)
            if persona:
                personas[person.name] = persona

        # 构建图谱
        graph = KnowledgeGraph(
            entities={e.name: e for e in entities},
            relations=relations,
            personas=personas,
            metadata={
                "source_length": len(text),
                "model": self.model
            }
        )

        # 输出
        if output_format == "json":
            return self._to_json(graph)
        elif output_format == "dict":
            return self._to_dict(graph)
        else:
            return self._to_json(graph)

    def _to_json(self, graph: KnowledgeGraph) -> Dict[str, Any]:
        """转换为JSON格式"""
        return {
            "entities": [
                {
                    "name": e.name,
                    "type": e.entity_type.value,
                    "mentions": e.mentions,
                    "attributes": e.attributes
                }
                for e in graph.entities.values()
            ],
            "relations": [
                {
                    "source": r.source,
                    "target": r.target,
                    "type": r.relation_type.value,
                    "confidence": r.confidence
                }
                for r in graph.relations
            ],
            "personas": [
                {
                    "name": p.name,
                    "demographics": p.demographics,
                    "personality": p.personality,
                    "interests": p.interests,
                    "background": p.background
                }
                for p in graph.personas.values()
            ],
            "metadata": graph.metadata,
            "created_at": graph.created_at.isoformat()
        }

    def _to_dict(self, graph: KnowledgeGraph) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "entities": graph.entities,
            "relations": graph.relations,
            "personas": graph.personas,
            "metadata": graph.metadata
        }

    async def build_from_file(
        self,
        file_path: str,
        output_format: str = "json"
    ) -> Dict[str, Any]:
        """从文件构建图谱"""
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        return await self.build_graph(text, output_format)

    async def build_from_directory(
        self,
        directory: str,
        output_dir: str
    ) -> List[Dict[str, Any]]:
        """从目录批量构建图谱"""
        results = []
        for filename in os.listdir(directory):
            if filename.endswith((".md", ".txt", ".json")):
                file_path = os.path.join(directory, filename)
                result = await self.build_from_file(file_path)

                # 保存结果
                output_path = os.path.join(
                    output_dir,
                    f"{filename}_graph.json"
                )
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)

                results.append(result)

        return results


class GraphSearcher:
    """图谱检索器"""

    def __init__(self, graph: KnowledgeGraph):
        self.graph = graph

    def search_entities(
        self,
        query: str,
        top_k: int = 10
    ) -> List[Entity]:
        """搜索实体"""
        results = []
        for entity in self.graph.entities.values():
            if query.lower() in entity.name.lower():
                results.append(entity)

        return sorted(results, key=lambda e: e.mentions, reverse=True)[:top_k]

    def get_relations(
        self,
        entity_name: str,
        depth: int = 1
    ) -> List[Relation]:
        """获取实体相关关系"""
        relations = []
        for relation in self.graph.relations:
            if relation.source == entity_name or relation.target == entity_name:
                relations.append(relation)

        return relations

    def find_path(
        self,
        source: str,
        target: str,
        max_depth: int = 3
    ) -> Optional[List[str]]:
        """查找两个实体间的路径"""
        # 简化的BFS实现
        if source not in self.graph.entities or target not in self.graph.entities:
            return None

        visited = {source}
        queue = [(source, [source])]

        while queue:
            current, path = queue.pop(0)

            if current == target:
                return path

            if len(path) >= max_depth:
                continue

            # 获取相邻实体
            for relation in self.graph.relations:
                if relation.source == current and relation.target not in visited:
                    visited.add(relation.target)
                    queue.append((relation.target, path + [relation.target]))
                elif relation.target == current and relation.source not in visited:
                    visited.add(relation.source)
                    queue.append((relation.source, path + [relation.source]))

        return None


# CLI接口
async def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="GraphRAG Builder")
    parser.add_argument("--input", help="输入文件路径")
    parser.add_argument("--output", default="graph.json", help="输出文件路径")
    parser.add_argument("--directory", help="输入目录路径")
    parser.add_argument("--extract-entities", action="store_true", help="仅抽取实体")
    parser.add_argument("--extract-relations", action="store_true", help="仅抽取关系")
    parser.add_argument("--generate-persona", help="生成指定人物设定")

    args = parser.parse_args()

    builder = GraphRAGBuilder()

    if args.input:
        result = await builder.build_from_file(args.input)

        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"图谱已保存到: {args.output}")
        print(f"实体数量: {len(result['entities'])}")
        print(f"关系数量: {len(result['relations'])}")
        print(f"人设数量: {len(result['personas'])}")

    elif args.directory:
        results = await builder.build_from_directory(args.directory, args.output)
        print(f"已处理 {len(results)} 个文件")

    elif args.generate_persona:
        text = input("请输入文本: ")
        persona = await builder.persona_generator.generate(text, args.generate_persona)
        if persona:
            print(json.dumps({
                "name": persona.name,
                "demographics": persona.demographics,
                "personality": persona.personality,
                "interests": persona.interests,
                "background": persona.background
            }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())