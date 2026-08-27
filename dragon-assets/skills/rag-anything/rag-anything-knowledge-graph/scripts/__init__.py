"""RAG-Anything知识图谱模块"""

from .kg_builder import KGBuilder, KGData, Entity, Relation, CrossModalEdge
from .entity_linker import EntityLinker
from .relation_extractor import RelationExtractor

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
