"""RAG-Anything知识图谱模块"""

from .scripts.kg_builder import KGBuilder, KGData, Entity, Relation, CrossModalEdge
from .scripts.entity_linker import EntityLinker
from .scripts.relation_extractor import RelationExtractor

__all__ = [
    "KGBuilder",
    "KGData",
    "Entity",
    "Relation",
    "CrossModalEdge",
    "EntityLinker",
    "RelationExtractor",
]

__version__ = "1.0.0"
