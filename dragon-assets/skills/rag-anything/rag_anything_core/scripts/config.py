"""RAG-Anything配置管理模块"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path


@dataclass
class RAGAnythingConfig:
    """RAG-Anything配置类"""

    # 数据目录配置
    data_dir: str = "./data"
    cache_dir: str = "./cache"
    temp_dir: str = "./temp"

    # 模型配置
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536
    llm_model: str = "gpt-4o-mini"
    vision_model: str = "gpt-4o"

    # 向量存储配置
    vector_store: str = "chroma"
    vector_store_path: str = "./data/vector_store"
    collection_name: str = "rag_anything"

    # 知识图谱配置
    kg_enabled: bool = True
    kg_storage_path: str = "./data/kg"
    kg_embedding_model: str = "text-embedding-3-small"

    # 多模态配置
    multimodal_enabled: bool = True
    table_enabled: bool = True
    formula_enabled: bool = True
    image_enabled: bool = True

    # 解析配置
    pdf_parser: str = "mineru"
    chunk_size: int = 512
    chunk_overlap: int = 50
    min_table_rows: int = 2
    max_table_rows: int = 100

    # 检索配置
    retrieval_mode: str = "hybrid"  # local/global/hybrid/mix
    top_k: int = 10
    rerank_enabled: bool = True
    rerank_top_k: int = 5

    # 性能配置
    max_workers: int = 4
    batch_size: int = 32
    timeout: int = 30

    # 高级配置
    extra_headers: Dict[str, str] = field(default_factory=dict)
    api_base: Optional[str] = None
    api_key: Optional[str] = None

    def __post_init__(self):
        """后处理初始化"""
        # 确保目录存在
        for dir_path in [self.data_dir, self.cache_dir, self.temp_dir,
                         self.vector_store_path, self.kg_storage_path]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)

        # 环境变量支持
        if self.api_key is None:
            self.api_key = os.getenv("OPENAI_API_KEY")

        if self.api_base is None:
            self.api_base = os.getenv("OPENAI_API_BASE")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {}
        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                result[key] = value
        return result

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "RAGAnythingConfig":
        """从字典创建配置"""
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_dict = {k: v for k, v in config_dict.items() if k in valid_fields}
        return cls(**filtered_dict)

    def update(self, **kwargs) -> "RAGAnythingConfig":
        """更新配置"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self


def get_default_config() -> RAGAnythingConfig:
    """获取默认配置"""
    return RAGAnythingConfig()


def load_config_from_file(config_path: str) -> RAGAnythingConfig:
    """从文件加载配置"""
    import json

    config_path = Path(config_path)
    if not config_path.exists():
        return get_default_config()

    with open(config_path, "r", encoding="utf-8") as f:
        config_dict = json.load(f)

    return RAGAnythingConfig.from_dict(config_dict)


def save_config_to_file(config: RAGAnythingConfig, config_path: str) -> None:
    """保存配置到文件"""
    import json

    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
