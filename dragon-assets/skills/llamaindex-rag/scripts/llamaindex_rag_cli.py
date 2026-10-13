#!/usr/bin/env python3
"""
LlamaIndex RAG CLI - 知识库构建与检索命令行工具
用法: python llamaindex_rag_cli.py <command> [args]
"""
import argparse
import json
import sys
import os
import subprocess
from pathlib import Path
from typing import Optional

try:
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
    from llama_index.core.retrievers import VectorIndexRetriever, KeywordTableSimpleRetriever
    from llama_index.core.node_parser import SimpleNodeParser
    from llama_index.embeddings.openai import OpenAIEmbedding
    from llama_index.vector_stores.chroma import ChromaVectorStore
    import chromadb
    LLAMAINDEX_AVAILABLE = True
except ImportError:
    LLAMAINDEX_AVAILABLE = False

KB_DIR = Path.home() / ".claude" / "knowledge_bases"


class KnowledgeBase:
    """知识库管理"""

    def __init__(self, name: str):
        self.name = name
        self.kb_dir = KB_DIR / name
        self.index_file = self.kb_dir / "index.json"
        self.docs_dir = self.kb_dir / "documents"
        self._ensure_dirs()

    def _ensure_dirs(self):
        self.kb_dir.mkdir(parents=True, exist_ok=True)
        self.docs_dir.mkdir(exist_ok=True)

    def create(self) -> dict:
        """创建知识库"""
        if self.index_file.exists():
            return {"status": "exists", "message": f"知识库 '{self.name}' 已存在"}
        self._ensure_dirs()
        with open(self.index_file, "w") as f:
            json.dump({"name": self.name, "doc_count": 0, "created": str(Path(__file__).stat().st_ctime)}, f)
        return {"status": "created", "message": f"知识库 '{self.name}' 已创建"}

    def add_documents(self, doc_paths: list) -> dict:
        """添加文档"""
        self._ensure_dirs()
        added = []
        for path in doc_paths:
            p = Path(path)
            if p.is_file():
                dest = self.docs_dir / p.name
                import shutil
                shutil.copy2(p, dest)
                added.append(str(dest))
        metadata = self._load_metadata()
        metadata["doc_count"] = len(list(self.docs_dir.glob("*")))
        self._save_metadata(metadata)
        return {"status": "added", "count": len(added), "files": added}

    def list_kbs(self) -> list:
        """列出所有知识库"""
        if not KB_DIR.exists():
            return []
        return [d.name for d in KB_DIR.iterdir() if d.is_dir()]

    def info(self) -> dict:
        """知识库信息"""
        if not self.index_file.exists():
            return {"status": "error", "message": f"知识库 '{self.name}' 不存在"}
        metadata = self._load_metadata()
        docs = list(self.docs_dir.glob("*"))
        return {
            "name": self.name,
            "doc_count": len(docs),
            "files": [d.name for d in docs],
            "metadata": metadata
        }

    def delete(self) -> dict:
        """删除知识库"""
        import shutil
        if self.kb_dir.exists():
            shutil.rmtree(self.kb_dir)
            return {"status": "deleted", "message": f"知识库 '{self.name}' 已删除"}
        return {"status": "error", "message": f"知识库 '{self.name}' 不存在"}

    def query(self, query_text: str, top_k: int = 5, mode: str = "vector") -> dict:
        """检索查询"""
        if not LLAMAINDEX_AVAILABLE:
            return {"status": "error", "message": "llama_index未安装。请运行: pip install llama-index"}
        if not self.docs_dir.exists() or not list(self.docs_dir.glob("*")):
            return {"status": "error", "message": f"知识库 '{self.name}' 为空，请先添加文档"}
        try:
            docs = SimpleDirectoryReader(str(self.docs_dir)).load_data()
            node_parser = SimpleNodeParser.from_defaults(chunk_size=512, chunk_overlap=50)
            nodes = node_parser.get_nodes_from_documents(docs)

            index = VectorStoreIndex(nodes)

            if mode == "hybrid":
                retriever = VectorIndexRetriever(index=index, similarity_top_k=top_k)
            else:
                retriever = VectorIndexRetriever(index=index, similarity_top_k=top_k)

            results = retriever.retrieve(query_text)
            return {
                "status": "success",
                "query": query_text,
                "mode": mode,
                "results": [
                    {
                        "content": r.node.get_content()[:300] + ("..." if len(r.node.get_content()) > 300 else ""),
                        "score": round(r.score, 4),
                        "source": r.node.metadata.get("file_name", "unknown")
                    }
                    for r in results
                ]
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _load_metadata(self) -> dict:
        if self.index_file.exists():
            with open(self.index_file) as f:
                return json.load(f)
        return {"name": self.name, "doc_count": 0}

    def _save_metadata(self, data: dict):
        with open(self.index_file, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def cmd_create(args):
    kb = KnowledgeBase(args.name)
    result = kb.create()
    print(f"✅ {result['message']}")


def cmd_add(args):
    kb = KnowledgeBase(args.name)
    result = kb.add_documents(args.docs)
    print(f"✅ 已添加 {result['count']} 个文件到知识库 '{args.name}'")
    for f in result.get("files", []):
        print(f"   • {Path(f).name}")


def cmd_list(_args):
    kb_global = KnowledgeBase("")
    kbs = kb_global.list_kbs()
    if not kbs:
        print("📚 暂无知识库，请先创建: kb create <name>")
    else:
        print("📚 知识库列表:")
        for name in kbs:
            info_kb = KnowledgeBase(name)
            info = info_kb.info()
            print(f"   • {name} ({info.get('doc_count', 0)} 文档)")


def cmd_info(args):
    kb = KnowledgeBase(args.name)
    result = kb.info()
    if result["status"] == "error":
        print(f"❌ {result['message']}")
        return
    print(f"📊 知识库: {args.name}")
    print(f"   文档数: {result.get('doc_count', 0)}")
    print(f"   文件:")
    for f in result.get("files", []):
        print(f"   • {f}")


def cmd_delete(args):
    kb = KnowledgeBase(args.name)
    result = kb.delete()
    print(f"✅ {result['message']}")


def cmd_query(args):
    kb = KnowledgeBase(args.name)
    result = kb.query(args.query, top_k=args.top_k or 5, mode=args.mode or "vector")
    if result["status"] == "error":
        print(f"❌ {result['message']}")
        return
    print(f"🔍 查询: {args.query}")
    print(f"   模式: {result['mode']} | 结果: {len(result['results'])} 条\n")
    for i, r in enumerate(result["results"], 1):
        print(f"{'─'*50}")
        print(f"[{i}] 来源: {r['source']} | 相似度: {r['score']}")
        print(f"    {r['content']}")


def cmd_export(args):
    kb = KnowledgeBase(args.name)
    info = kb.info()
    if info["status"] == "error":
        print(f"❌ {info['message']}")
        return
    if args.format == "json":
        print(json.dumps(info, indent=2, ensure_ascii=False))
    elif args.format == "markdown":
        for f in info.get("files", []):
            print(f"## {f}\n")


def cmd_sync_obsidian(args):
    """同步Obsidian笔记到知识库"""
    vault = Path(args.vault)
    if not vault.exists():
        print(f"❌ Obsidian库不存在: {vault}")
        return
    md_files = list(vault.rglob("*.md"))
    md_files = [f for f in md_files if not f.name.startswith(".")]  # 排除隐藏文件
    if not md_files:
        print("❌ 未找到Markdown文件")
        return
    kb = KnowledgeBase(args.name)
    if not kb.index_file.exists():
        kb.create()
    result = kb.add_documents([str(f) for f in md_files[: args.max_files or 100]])
    print(f"✅ 已同步 {result['count']} 个Obsidian笔记到知识库 '{args.name}'")


def main():
    parser = argparse.ArgumentParser(description="LlamaIndex RAG CLI - 知识库构建与检索")
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # create
    p_create = subparsers.add_parser("create", help="创建知识库")
    p_create.add_argument("name", help="知识库名称")

    # add
    p_add = subparsers.add_parser("add", help="添加文档")
    p_add.add_argument("name", help="知识库名称")
    p_add.add_argument("docs", nargs="+", help="文档路径")

    # list
    subparsers.add_parser("list", help="列出所有知识库")

    # info
    p_info = subparsers.add_parser("info", help="查看知识库信息")
    p_info.add_argument("name", help="知识库名称")

    # delete
    p_del = subparsers.add_parser("delete", help="删除知识库")
    p_del.add_argument("name", help="知识库名称")

    # query
    p_q = subparsers.add_parser("query", help="检索查询")
    p_q.add_argument("name", help="知识库名称")
    p_q.add_argument("query", help="查询内容")
    p_q.add_argument("--top-k", "-k", type=int, help="返回数量")
    p_q.add_argument("--mode", "-m", choices=["vector", "keyword", "hybrid"], default="vector", help="检索模式")

    # export
    p_exp = subparsers.add_parser("export", help="导出知识库")
    p_exp.add_argument("name", help="知识库名称")
    p_exp.add_argument("--format", "-f", choices=["json", "markdown"], default="markdown", help="导出格式")

    # sync
    p_sync = subparsers.add_parser("sync-obsidian", help="同步Obsidian笔记")
    p_sync.add_argument("vault", help="Obsidian库路径")
    p_sync.add_argument("--name", "-n", required=True, help="知识库名称")
    p_sync.add_argument("--max-files", type=int, help="最大文件数")

    args = parser.parse_args()

    if args.command == "create":
        cmd_create(args)
    elif args.command == "add":
        cmd_add(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "info":
        cmd_info(args)
    elif args.command == "delete":
        cmd_delete(args)
    elif args.command == "query":
        cmd_query(args)
    elif args.command == "export":
        cmd_export(args)
    elif args.command == "sync-obsidian":
        cmd_sync_obsidian(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
