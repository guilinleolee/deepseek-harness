#!/usr/bin/env python3
"""
Jina AI 统一客户端
整合Embedding和Reranker，提供统一的语义搜索接口

使用方法:
    python3 client.py --mode search --query "人工智能" --corpus ./docs/
    python3 client.py --mode index --path ./docs/ --index-name my-corpus
    python3 client.py --mode similarity --text1 "文本1" --text2 "文本2"
"""

import os
import sys
import json
import argparse
from typing import List, Optional, Dict

# 导入子模块
from embedding import JinaEmbeddingClient
from reranker import JinaRerankerClient


class JinaSemanticSearch:
    """Jina AI语义搜索客户端"""

    def __init__(self, api_key: Optional[str] = None):
        self.embedding_client = JinaEmbeddingClient(api_key)
        self.reranker_client = JinaRerankerClient(api_key)
        self.corpus_cache = {}  # 缓存已索引的语料

    def index_corpus(self, texts: List[str], index_name: str = "default") -> Dict:
        """索引语料库，返回embedding向量"""
        print(f"正在索引语料库: {index_name} ({len(texts)} 条文档)")

        embeddings = self.embedding_client.batch_encode(texts)

        self.corpus_cache[index_name] = {
            "texts": texts,
            "embeddings": embeddings
        }

        return {
            "index_name": index_name,
            "doc_count": len(texts),
            "embedding_dim": len(embeddings[0]) if embeddings else 0
        }

    def index_from_file(self, file_path: str, index_name: str = "default") -> Dict:
        """从文件索引语料库"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 按段落分割
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

        return self.index_corpus(paragraphs, index_name)

    def index_from_directory(self, dir_path: str, index_name: str = "default",
                            extensions: List[str] = [".md", ".txt", ".py"]) -> Dict:
        """从目录索引语料库"""
        texts = []
        for root, dirs, files in os.walk(dir_path):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["node_modules", "__pycache__"]]
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    # 按段落分割
                    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
                    texts.extend(paragraphs)

        print(f"从目录 {dir_path} 索引了 {len(texts)} 条文档")
        return self.index_corpus(texts, index_name)

    def load_index(self, index_file: str) -> Dict:
        """从文件加载索引"""
        with open(index_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        index_name = os.path.basename(index_file)
        self.corpus_cache[index_name] = {
            "texts": data.get("texts", []),
            "embeddings": data.get("embeddings", [])
        }

        return {
            "index_name": index_name,
            "doc_count": len(data.get("texts", []))
        }

    def save_index(self, index_name: str, output_file: str) -> bool:
        """保存索引到文件"""
        if index_name not in self.corpus_cache:
            print(f"错误: 索引 '{index_name}' 不存在")
            return False

        data = self.corpus_cache[index_name]
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"索引已保存到: {output_file}")
        return True

    def search(self, query: str, index_name: str = "default",
              top_k: int = 10, use_reranker: bool = True) -> List[Dict]:
        """语义搜索：query + reranker优化"""
        if index_name not in self.corpus_cache:
            print(f"错误: 索引 '{index_name}' 不存在")
            return []

        corpus = self.corpus_cache[index_name]
        texts = corpus["texts"]
        embeddings = corpus["embeddings"]

        # Step 1: 向量检索获取候选结果
        query_embedding = self.embedding_client.encode_single(query)

        # 计算余弦相似度
        similarities = []
        for i, doc_emb in enumerate(embeddings):
            dot = sum(q * d for q, d in zip(query_embedding, doc_emb))
            norm_query = sum(q ** 2 for q in query_embedding) ** 0.5
            norm_doc = sum(d ** 2 for d in doc_emb) ** 0.5
            similarity = dot / (norm_query * norm_doc + 1e-10)
            similarities.append((i, similarity))

        # 排序取top_k*3候选
        similarities.sort(key=lambda x: x[1], reverse=True)
        candidates = similarities[:top_k * 3]

        # Step 2: Reranker重排序
        if use_reranker:
            candidate_texts = [texts[i] for i, _ in candidates]
            reranked = self.reranker_client.rerank(query, candidate_texts, top_n=top_k)

            results = []
            for r in reranked:
                idx = r["index"]
                results.append({
                    "text": texts[idx] if idx < len(texts) else candidate_texts[idx],
                    "relevance_score": r["relevance_score"],
                    "vector_score": next((s for i, s in candidates if i == idx), 0)
                })
        else:
            results = []
            for i, sim in candidates[:top_k]:
                results.append({
                    "text": texts[i],
                    "vector_score": sim,
                    "relevance_score": sim  # 无reranker时用向量分数
                })

        return results

    def similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的余弦相似度"""
        return self.embedding_client.similarity(text1, text2)

    def batch_similarity(self, text_pairs: List[tuple]) -> List[float]:
        """批量计算文本对相似度"""
        results = []
        for text1, text2 in text_pairs:
            sim = self.similarity(text1, text2)
            results.append(sim)
        return results


def main():
    parser = argparse.ArgumentParser(description="Jina AI语义搜索客户端")
    parser.add_argument("--mode", "-m", choices=["search", "index", "similarity", "load"],
                       default="search", help="运行模式")
    parser.add_argument("--query", "-q", help="搜索查询")
    parser.add_argument("--index-name", default="default", help="索引名称")
    parser.add_argument("--index-file", help="索引文件路径")
    parser.add_argument("--path", help="索引路径（文件或目录）")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--top", type=int, default=10, help="返回前N个结果")
    parser.add_argument("--no-reranker", action="store_true", help="禁用Reranker")
    parser.add_argument("--text1", help="相似度计算文本1")
    parser.add_argument("--text2", help="相似度计算文本2")

    args = parser.parse_args()

    try:
        client = JinaSemanticSearch()
    except ValueError as e:
        print(f"错误: {e}")
        print("请设置 JINA_API_KEY 环境变量")
        sys.exit(1)

    # 索引模式
    if args.mode == "index":
        if not args.path:
            print("错误: 需要指定 --path")
            sys.exit(1)

        if os.path.isdir(args.path):
            result = client.index_from_directory(args.path, args.index_name)
        elif os.path.isfile(args.path):
            result = client.index_from_file(args.path, args.index_name)
        else:
            print(f"错误: 路径不存在 - {args.path}")
            sys.exit(1)

        print(f"索引完成: {result}")

        if args.output:
            client.save_index(args.index_name, args.output)

        return

    # 加载索引
    if args.mode == "load":
        if not args.index_file:
            print("错误: 需要指定 --index-file")
            sys.exit(1)

        result = client.load_index(args.index_file)
        print(f"加载完成: {result}")
        return

    # 相似度模式
    if args.mode == "similarity":
        if not args.text1 or not args.text2:
            print("错误: 需要指定 --text1 和 --text2")
            sys.exit(1)

        sim = client.similarity(args.text1, args.text2)
        print(f"\n文本1: {args.text1[:50]}...")
        print(f"文本2: {args.text2[:50]}...")
        print(f"相似度: {sim:.4f}")
        return

    # 搜索模式
    if args.mode == "search":
        if not args.query:
            print("错误: 需要指定 --query")
            sys.exit(1)

        if args.index_name not in client.corpus_cache:
            print(f"错误: 索引 '{args.index_name}' 不存在，请先运行index模式")
            print(f"可用索引: {list(client.corpus_cache.keys())}")
            sys.exit(1)

        results = client.search(args.query, args.index_name, args.top, not args.no_reranker)

        print(f"\n查询: {args.query}")
        print(f"索引: {args.index_name}")
        print(f"返回结果: {len(results)}")
        print("\n" + "=" * 60)

        for i, r in enumerate(results, 1):
            print(f"\n{i}. [相关度: {r['relevance_score']:.4f}] [向量分: {r['vector_score']:.4f}]")
            text = r["text"]
            display = text[:200] + "..." if len(text) > 200 else text
            print(f"   {display}")

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump({
                    "query": args.query,
                    "index": args.index_name,
                    "results": results
                }, f, ensure_ascii=False, indent=2)
            print(f"\n结果已保存到: {args.output}")

        return


if __name__ == "__main__":
    main()