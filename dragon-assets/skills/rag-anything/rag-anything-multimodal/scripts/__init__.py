"""RAG-Anything多模态模块"""

from .multimodal_processor import MultimodalProcessor
from .modal_retriever import ModalRetriever, RetrievalResult
from .cross_modal_embedding import CrossModalEmbedder

__all__ = [
    "MultimodalProcessor",
    "ModalRetriever",
    "RetrievalResult",
    "CrossModalEmbedder",
]

__version__ = "1.0.0"
