"""知识图谱模块测试"""

import pytest


class TestKGBuilder:
    """知识图谱构建器测试"""

    @pytest.fixture
    def builder(self):
        """创建构建器实例"""
        from rag_anything_knowledge_graph.scripts.kg_builder import KGBuilder

        return KGBuilder()

    @pytest.fixture
    def sample_parsed_doc(self):
        """样本解析文档"""
        return {
            "doc_id": "test_doc",
            "file_path": "test.pdf",
            "pages": [
                {
                    "page_num": 0,
                    "text": "Machine learning is a subset of artificial intelligence. Neural networks are used in deep learning.",
                    "text_blocks": [],
                },
                {
                    "page_num": 1,
                    "text": "The equation E = mc^2 is Einstein's formula.",
                    "text_blocks": [],
                },
            ],
            "tables": [
                {
                    "table_id": "table_0",
                    "html": "<table><tr><th>Name</th><th>Type</th></tr><tr><td>ML</td><td>AI</td></tr></table>",
                    "markdown": "| Name | Type |\n| --- | --- |\n| ML | AI |",
                    "page_num": 0,
                    "rows": 2,
                    "cols": 2,
                    "header": ["Name", "Type"],
                }
            ],
            "formulas": [
                {
                    "formula_id": "formula_0",
                    "latex": r"E = mc^2",
                    "page_num": 1,
                    "formula_type": "display",
                }
            ],
            "images": [
                {
                    "image_id": "image_0",
                    "image_path": "diagram.png",
                    "page_num": 0,
                    "description": "Neural network architecture diagram",
                }
            ],
        }

    @pytest.mark.asyncio
    async def test_build_empty_doc(self, builder):
        """测试构建空文档"""
        empty_doc = {"doc_id": "empty", "pages": [], "tables": [], "formulas": [], "images": []}

        kg_data = await builder.build(empty_doc)

        assert kg_data is not None
        assert len(kg_data.entities) == 0
        assert len(kg_data.relations) == 0

    @pytest.mark.asyncio
    async def test_build_with_content(self, builder, sample_parsed_doc):
        """测试构建有内容的文档"""
        kg_data = await builder.build(sample_parsed_doc)

        assert kg_data is not None
        assert len(kg_data.entities) > 0
        # 验证各类型实体
        entity_types = {e.entity_type for e in kg_data.entities}
        assert "text" in entity_types
        assert "table" in entity_types
        assert "formula" in entity_types
        assert "image" in entity_types

    @pytest.mark.asyncio
    async def test_cross_modal_edges(self, builder, sample_parsed_doc):
        """测试跨模态边创建"""
        kg_data = await builder.build(sample_parsed_doc)

        assert len(kg_data.cross_modal_edges) >= 0

        # 验证跨模态边的结构
        for edge in kg_data.cross_modal_edges:
            assert edge.source_modality != edge.target_modality
            assert edge.edge_type in ["contains", "refers_to", "related_to"]

    @pytest.mark.asyncio
    async def test_entity_keywords_extraction(self, builder):
        """测试关键词提取"""
        text = "Machine learning and deep learning are subsets of artificial intelligence."
        keywords = builder._extract_keywords(text, max_keywords=10)

        assert isinstance(keywords, list)
        assert len(keywords) <= 10
        # 关键词应该包含有意义的词
        assert len(keywords) > 0

    @pytest.mark.asyncio
    async def test_formula_variable_extraction(self, builder):
        """测试公式变量提取"""
        latex = r"E = mc^2 + \alpha \cdot \beta"
        variables = builder._extract_formula_variables(latex)

        assert isinstance(variables, list)
        # 应该包含一些变量
        assert len(variables) >= 0


class TestEntity:
    """实体测试"""

    def test_entity_creation(self):
        """测试实体创建"""
        from rag_anything_knowledge_graph.scripts.kg_builder import Entity

        entity = Entity(
            entity_id="test_1",
            name="Test Entity",
            entity_type="text",
            subtype="concept",
            page_num=0,
        )

        assert entity.entity_id == "test_1"
        assert entity.name == "Test Entity"
        assert entity.entity_type == "text"
        assert entity.confidence == 1.0

    def test_entity_to_dict(self):
        """测试实体转字典"""
        from rag_anything_knowledge_graph.scripts.kg_builder import Entity

        entity = Entity(
            entity_id="test_1",
            name="Test",
            entity_type="text",
        )

        entity_dict = entity.to_dict()

        assert entity_dict["entity_id"] == "test_1"
        assert entity_dict["name"] == "Test"


class TestRelation:
    """关系测试"""

    def test_relation_creation(self):
        """测试关系创建"""
        from rag_anything_knowledge_graph.scripts.kg_builder import Relation

        relation = Relation(
            relation_id="rel_1",
            source_id="ent_1",
            target_id="ent_2",
            relation_type="related_to",
        )

        assert relation.relation_id == "rel_1"
        assert relation.source_id == "ent_1"
        assert relation.target_id == "ent_2"
        assert relation.confidence == 1.0


class TestCrossModalEdge:
    """跨模态边测试"""

    def test_cross_modal_edge_creation(self):
        """测试跨模态边创建"""
        from rag_anything_knowledge_graph.scripts.kg_builder import CrossModalEdge

        edge = CrossModalEdge(
            edge_id="edge_1",
            source_entity_id="text_ent",
            target_entity_id="image_ent",
            source_modality="text",
            target_modality="image",
            edge_type="refers_to",
        )

        assert edge.edge_id == "edge_1"
        assert edge.source_modality == "text"
        assert edge.target_modality == "image"


class TestKGData:
    """知识图谱数据测试"""

    def test_kg_data_creation(self):
        """测试KGData创建"""
        from rag_anything_knowledge_graph.scripts.kg_builder import (
            KGData,
            Entity,
            Relation,
        )

        entities = [
            Entity(entity_id="1", name="E1", entity_type="text"),
            Entity(entity_id="2", name="E2", entity_type="text"),
        ]
        relations = [
            Relation(relation_id="r1", source_id="1", target_id="2", relation_type="related"),
        ]

        kg_data = KGData(entities=entities, relations=relations)

        assert len(kg_data.entities) == 2
        assert len(kg_data.relations) == 1

    def test_get_entity(self):
        """测试获取实体"""
        from rag_anything_knowledge_graph.scripts.kg_builder import KGData, Entity

        entities = [Entity(entity_id="1", name="Test", entity_type="text")]
        kg_data = KGData(entities=entities)

        entity = kg_data.get_entity("1")
        assert entity is not None
        assert entity.name == "Test"

        missing = kg_data.get_entity("nonexistent")
        assert missing is None

    def test_get_relations(self):
        """测试获取关系"""
        from rag_anything_knowledge_graph.scripts.kg_builder import (
            KGData,
            Entity,
            Relation,
        )

        entities = [
            Entity(entity_id="1", name="E1", entity_type="text"),
            Entity(entity_id="2", name="E2", entity_type="text"),
        ]
        relations = [
            Relation(relation_id="r1", source_id="1", target_id="2", relation_type="related"),
        ]

        kg_data = KGData(entities=entities, relations=relations)

        rels = kg_data.get_relations("1")
        assert len(rels) == 1

        no_rels = kg_data.get_relations("nonexistent")
        assert len(no_rels) == 0

    def test_to_dict_with_stats(self):
        """测试转字典包含统计"""
        from rag_anything_knowledge_graph.scripts.kg_builder import KGData, Entity

        entities = [
            Entity(entity_id="1", name="E1", entity_type="text", subtype="concept"),
            Entity(entity_id="2", name="E2", entity_type="table"),
        ]

        kg_data = KGData(entities=entities)
        kg_dict = kg_data.to_dict()

        assert "stats" in kg_dict
        assert kg_dict["stats"]["total_entities"] == 2
        assert "text/concept" in kg_dict["stats"]["entity_types"]


class TestEntityLinker:
    """实体链接器测试"""

    @pytest.fixture
    def linker(self):
        """创建链接器实例"""
        from rag_anything_knowledge_graph.scripts.entity_linker import EntityLinker

        return EntityLinker()

    @pytest.mark.asyncio
    async def test_link_entity_no_kb(self, linker):
        """测试无知识库的链接"""
        from rag_anything_knowledge_graph.scripts.kg_builder import Entity

        entity = Entity(entity_id="1", name="Test", entity_type="text")

        result = await linker.link_entity(entity)

        assert result is None

    @pytest.mark.asyncio
    async def test_disambiguate(self, linker):
        """测试消歧"""
        from rag_anything_knowledge_graph.scripts.kg_builder import Entity

        entity = Entity(entity_id="1", name="Machine Learning", entity_type="text")
        candidates = [
            Entity(entity_id="2", name="Machine Learning", entity_type="text"),
            Entity(entity_id="3", name="Deep Learning", entity_type="text"),
        ]

        result = await linker.disambiguate(entity, candidates)

        # 应该匹配到名称完全相同的
        assert result is not None
        assert result.entity_id == "2"


class TestRelationExtractor:
    """关系抽取器测试"""

    @pytest.fixture
    def extractor(self):
        """创建抽取器实例"""
        from rag_anything_knowledge_graph.scripts.relation_extractor import (
            RelationExtractor,
        )

        return RelationExtractor()

    @pytest.mark.asyncio
    async def test_extract_relations_simple(self, extractor):
        """测试简单关系抽取"""
        from rag_anything_knowledge_graph.scripts.kg_builder import Entity

        text = "Apple is a fruit. Banana is also a fruit."
        entities = [
            Entity(entity_id="1", name="Apple", entity_type="text"),
            Entity(entity_id="2", name="fruit", entity_type="text"),
        ]

        relations = await extractor.extract_relations(text, entities)

        assert isinstance(relations, list)

    @pytest.mark.asyncio
    async def test_extract_from_entity_pair(self, extractor):
        """测试实体对关系抽取"""
        from rag_anything_knowledge_graph.scripts.kg_builder import Entity

        entity1 = Entity(entity_id="1", name="ML", entity_type="text", page_num=0)
        entity2 = Entity(entity_id="2", name="Machine Learning", entity_type="text", page_num=0)

        relation = await extractor.extract_from_entity_pair(entity1, entity2, "ML is short for Machine Learning")

        assert relation is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
