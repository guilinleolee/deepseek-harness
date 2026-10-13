#!/usr/bin/env python3
"""
Enterprise Docs Search - RAG检索引擎

基于DocsGPT核心能力实现的企业文档搜索系统。

特性:
- 22+格式文档解析
- ChromaDB向量存储
- RAG检索增强生成
- 引用追踪与溯源

使用方法:
    from enterprise_docs_search import RAGEngine

    engine = RAGEngine()
    engine.ingest("./docs/")
    result = engine.query("如何配置API?")
"""

import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field

# 可选依赖
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


@dataclass
class Document:
    """文档对象"""
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: str = ""
    partition: str = "default"


@dataclass
class SearchResult:
    """搜索结果"""
    answer: str
    sources: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    tokens_used: int = 0


@dataclass
class IngestResult:
    """摄取结果"""
    success: bool
    documents_added: int = 0
    documents_skipped: int = 0
    errors: List[str] = field(default_factory=list)


class DocumentParser:
    """文档解析器，支持22+格式"""

    SUPPORTED_EXTENSIONS = {
        # 文档
        '.pdf', '.docx', '.doc', '.epub', '.md', '.rst', '.html', '.htm', '.mdx',
        # 表格
        '.csv', '.xlsx', '.xls',
        # 演示
        '.pptx', '.ppt',
        # 数据
        '.json', '.xml', '.yaml', '.yml',
        # 代码
        '.py', '.js', '.ts', '.java', '.go', '.rs', '.c', '.cpp', '.h',
        # 文本
        '.txt', '.log', '.cfg', '.ini', '.conf',
    }

    def __init__(self):
        self.parsers = {}

    def parse(self, file_path: str) -> List[Document]:
        """
        解析文档

        Args:
            file_path: 文件路径

        Returns:
            文档片段列表
        """
        path = Path(file_path)
        ext = path.suffix.lower()

        if ext not in self.SUPPORTED_EXTENSIONS:
            return []

        try:
            content = self._read_file(path, ext)
            if not content:
                return []

            # 创建文档对象
            doc_id = self._generate_id(file_path)
            doc = Document(
                id=doc_id,
                content=content,
                metadata={
                    'source': str(path),
                    'extension': ext,
                    'size': path.stat().st_size,
                },
                source=str(path),
            )

            return [doc]

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return []

    def _read_file(self, path: Path, ext: str) -> Optional[str]:
        """读取文件内容"""
        # 纯文本文件
        if ext in {'.md', '.rst', '.html', '.htm', '.mdx', '.txt', '.log',
                   '.cfg', '.ini', '.conf', '.py', '.js', '.ts', '.java',
                   '.go', '.rs', '.c', '.cpp', '.h', '.json', '.xml', '.yaml', '.yml'}:
            return path.read_text(encoding='utf-8', errors='ignore')

        # CSV
        if ext == '.csv':
            return path.read_text(encoding='utf-8', errors='ignore')

        # PDF (需要pypdf)
        if ext == '.pdf':
            try:
                import pypdf
                reader = pypdf.PdfReader(str(path))
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                return text
            except ImportError:
                print("Warning: pypdf not installed, skipping PDF")
                return None

        # DOCX (需要python-docx)
        if ext in {'.docx', '.doc'}:
            try:
                from docx import Document as DocxDocument
                doc = DocxDocument(str(path))
                return "\n".join(p.text for p in doc.paragraphs)
            except ImportError:
                print("Warning: python-docx not installed, skipping DOCX")
                return None

        # PPTX (需要python-pptx)
        if ext in {'.pptx', '.ppt'}:
            try:
                from pptx import Presentation
                prs = Presentation(str(path))
                text = ""
                for slide in prs.slides:
                    for shape in slide.shapes:
                        if hasattr(shape, "text"):
                            text += shape.text + "\n"
                return text
            except ImportError:
                print("Warning: python-pptx not installed, skipping PPTX")
                return None

        # XLSX (需要openpyxl)
        if ext in {'.xlsx', '.xls'}:
            try:
                import openpyxl
                wb = openpyxl.load_workbook(str(path))
                text = ""
                for sheet in wb.worksheets:
                    for row in sheet.iter_rows(values_only=True):
                        text += "\t".join(str(cell) if cell else "" for cell in row) + "\n"
                return text
            except ImportError:
                print("Warning: openpyxl not installed, skipping XLSX")
                return None

        return None

    def _generate_id(self, file_path: str) -> str:
        """生成文档ID"""
        return hashlib.md5(file_path.encode()).hexdigest()[:12]


class TextChunker:
    """文本分块器"""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, document: Document) -> List[Document]:
        """
        将文档分块

        Args:
            document: 原始文档

        Returns:
            文档块列表
        """
        if LANGCHAIN_AVAILABLE:
            return self._chunk_with_langchain(document)
        return self._chunk_simple(document)

    def _chunk_with_langchain(self, document: Document) -> List[Document]:
        """使用LangChain分块"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )

        chunks = splitter.split_text(document.content)

        return [
            Document(
                id=f"{document.id}_{i}",
                content=chunk,
                metadata={**document.metadata, 'chunk_index': i},
                source=document.source,
                partition=document.partition,
            )
            for i, chunk in enumerate(chunks)
        ]

    def _chunk_simple(self, document: Document) -> List[Document]:
        """简单分块"""
        text = document.content
        chunks = []

        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunk_text = text[i:i + self.chunk_size]
            chunks.append(Document(
                id=f"{document.id}_{len(chunks)}",
                content=chunk_text,
                metadata={**document.metadata, 'chunk_index': len(chunks)},
                source=document.source,
                partition=document.partition,
            ))

        return chunks


class VectorStore:
    """向量存储"""

    def __init__(self, persist_directory: str = None):
        if not CHROMADB_AVAILABLE:
            raise ImportError("chromadb is required. Install with: pip install chromadb")

        self.persist_directory = persist_directory or os.path.expanduser("~/.claude/kb/chroma")

        # 初始化ChromaDB
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )

        # 默认集合
        self.collection = self.client.get_or_create_collection("enterprise_docs")

    def add(self, documents: List[Document]) -> int:
        """
        添加文档到向量存储

        Args:
            documents: 文档列表

        Returns:
            添加的文档数量
        """
        if not documents:
            return 0

        ids = [doc.id for doc in documents]
        texts = [doc.content for doc in documents]
        metadatas = [
            {**doc.metadata, 'source': doc.source, 'partition': doc.partition}
            for doc in documents
        ]

        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
        )

        return len(documents)

    def search(
        self,
        query: str,
        n_results: int = 5,
        partition: str = None,
    ) -> List[Dict]:
        """
        搜索相似文档

        Args:
            query: 查询文本
            n_results: 返回数量
            partition: 分区过滤

        Returns:
            搜索结果列表
        """
        where_filter = None
        if partition:
            where_filter = {"partition": partition}

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter,
        )

        # 格式化结果
        formatted = []
        for i, doc in enumerate(results['documents'][0]):
            formatted.append({
                'content': doc,
                'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                'id': results['ids'][0][i],
                'distance': results['distances'][0][i] if results.get('distances') else 0,
            })

        return formatted

    def delete(self, doc_ids: List[str] = None, partition: str = None):
        """删除文档"""
        if doc_ids:
            self.collection.delete(ids=doc_ids)
        elif partition:
            self.collection.delete(where={"partition": partition})

    def count(self) -> int:
        """获取文档数量"""
        return self.collection.count()


class RAGEngine:
    """RAG检索引擎"""

    def __init__(
        self,
        persist_directory: str = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        self.parser = DocumentParser()
        self.chunker = TextChunker(chunk_size, chunk_overlap)
        self.vector_store = VectorStore(persist_directory)

    def ingest(
        self,
        path: str,
        recursive: bool = True,
        partition: str = "default",
        extensions: List[str] = None,
    ) -> IngestResult:
        """
        摄取文档

        Args:
            path: 文件或目录路径
            recursive: 是否递归扫描
            partition: 分区名称
            extensions: 文件扩展名过滤

        Returns:
            摄取结果
        """
        result = IngestResult(success=True)
        documents = []

        path_obj = Path(path)

        if path_obj.is_file():
            # 单文件
            docs = self.parser.parse(str(path_obj))
            for doc in docs:
                doc.partition = partition
            documents.extend(docs)

        elif path_obj.is_dir():
            # 目录
            pattern = "**/*" if recursive else "*"
            for file_path in path_obj.glob(pattern):
                if file_path.is_file():
                    if extensions and file_path.suffix.lower() not in extensions:
                        result.documents_skipped += 1
                        continue

                    docs = self.parser.parse(str(file_path))
                    for doc in docs:
                        doc.partition = partition
                    documents.extend(docs)

        # 分块并存储
        for doc in documents:
            chunks = self.chunker.chunk(doc)
            added = self.vector_store.add(chunks)
            result.documents_added += added

        return result

    def query(
        self,
        query: str,
        top_k: int = 5,
        partition: str = None,
        include_sources: bool = True,
    ) -> SearchResult:
        """
        查询知识库

        Args:
            query: 查询问题
            top_k: 返回文档数量
            partition: 分区过滤
            include_sources: 是否包含来源

        Returns:
            搜索结果
        """
        # 向量检索
        results = self.vector_store.search(
            query=query,
            n_results=top_k,
            partition=partition,
        )

        if not results:
            return SearchResult(
                answer="未找到相关文档。",
                sources=[],
            )

        # 构建上下文
        context = "\n\n".join(
            f"[文档{i+1}]\n{r['content']}"
            for i, r in enumerate(results)
        )

        # 生成答案（这里返回上下文，实际使用时需要LLM生成）
        answer = self._generate_answer(query, context, results)

        # 构建来源
        sources = []
        if include_sources:
            for r in results:
                sources.append({
                    'content': r['content'][:200] + "...",
                    'source': r['metadata'].get('source', 'unknown'),
                    'partition': r['metadata'].get('partition', 'default'),
                    'distance': r.get('distance', 0),
                })

        return SearchResult(
            answer=answer,
            sources=sources,
            confidence=1 - (results[0].get('distance', 0) if results else 1),
        )

    def _generate_answer(
        self,
        query: str,
        context: str,
        results: List[Dict],
    ) -> str:
        """
        生成答案（简化版，实际需要LLM）

        在实际使用中，这里会调用LLM生成答案
        """
        # 简化实现：直接返回相关内容
        if results:
            top_result = results[0]
            source = top_result['metadata'].get('source', 'unknown')
            return f"根据文档 {source} 的内容：\n\n{top_result['content'][:500]}..."

        return "未找到相关信息。"

    def status(self) -> Dict:
        """获取知识库状态"""
        return {
            'document_count': self.vector_store.count(),
            'persist_directory': self.vector_store.persist_directory,
        }


# 便捷函数
def create_engine(persist_directory: str = None) -> RAGEngine:
    """创建RAG引擎"""
    return RAGEngine(persist_directory=persist_directory)


if __name__ == "__main__":
    # 示例用法
    engine = create_engine()

    # 摄取文档
    result = engine.ingest("./docs/")
    print(f"Added {result.documents_added} documents")

    # 查询
    answer = engine.query("如何配置API?")
    print(f"Answer: {answer.answer}")
    print(f"Sources: {answer.sources}")