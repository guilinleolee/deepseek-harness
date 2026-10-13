"""RAG-Anything多模态模块"""

from .scripts.multimodal_processor import MultimodalProcessor
from .scripts.modal_retriever import ModalRetriever, RetrievalResult
from .scripts.cross_modal_embedding import CrossModalEmbedder

__all__ = [
    "MultimodalProcessor",
    "ModalRetriever",
    "RetrievalResult",
    "CrossModalEmbedder",
]

__version__ = "1.0.0"
