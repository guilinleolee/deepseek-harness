#!/usr/bin/env python3
"""
Jina AI Reranker Client
免费文档重排序API封装

使用方法:
    python3 reranker.py --query "人工智能" --documents "AI是..." "机器学习是..."
    python3 reranker.py --query "什么是深度学习" --file ./docs/
"""

import os
import sys
import json
import argparse
import requests
from typing import List, Optional, Dict

# 默认API地址
DEFAULT_BASE_URL = "https://api.jina.ai/rerank"


class JinaRerankerClient:
    """Jina AI Reranker客户端"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("JINA_API_KEY")
        if not self.api_key:
            raise ValueError("需要设置 JINA_API_KEY 环境变量")
        self.base_url = DEFAULT_BASE_URL

    def rerank(
        self,
        query: str,
        documents: List[str],
        top_n: Optional[int] = None,
        model: str = "jina-reranker-v1-base-en",
        return_documents: bool = True
    ) -> List[Dict]:
        """对文档列表进行重排序"""
        response = requests.post(
            self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "query": query,
                "documents": documents,
                "top_n": top_n if top_n else len(documents),
                "return_documents": return_documents
            },
            timeout=60
        )

        if response.status_code == 200:
            return response.json()["results"]
        else:
            raise Exception(f"Rerank failed: {response.status_code} - {response.text}")

    def rerank_with_scores(
        self,
        query: str,
        documents: List[str],
        top_n: Optional[int] = None
    ) -> List[tuple]:
        """返回排序后的文档及其相关性分数"""
        results = self.rerank(query, documents, top_n)
        return [(r["document"]["text"], r["relevance_score"]) for r in results]

    def batch_rerank(
        self,
        queries: List[str],
        documents: List[str],
        top_n: Optional[int] = None
    ) -> List[List[Dict]]:
        """批量处理多个查询"""
        all_results = []
        for i, query in enumerate(queries):
            results = self.rerank(query, documents, top_n)
            all_results.append(results)
            print(f"  进度: {i + 1}/{len(queries)}", end="\r")
        print()
        return all_results


def read_file(file_path: str) -> List[str]:
    """读取文件内容并按段落分割"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return [p.strip() for p in content.split("\n\n") if p.strip()]


def main():
    parser = argparse.ArgumentParser(description="Jina AI Reranker工具")
    parser.add_argument("--query", "-q", required=True, help="查询文本")
    parser.add_argument("--documents", "-d", nargs="+", help="文档列表")
    parser.add_argument("--file", "-f", help="从文件读取文档")
    parser.add_argument("--top", "-t", type=int, help="返回前N个结果")
    parser.add_argument("--output", "-o", help="输出结果到文件")
    parser.add_argument("--json", action="store_true", help="JSON格式输出")
    parser.add_argument("--model", default="jina-reranker-v1-base-en", help="使用的模型")

    args = parser.parse_args()

    try:
        client = JinaRerankerClient()
    except ValueError as e:
        print(f"错误: {e}")
        print("请设置 JINA_API_KEY 环境变量")
        print("获取免费API Key: https://jina.ai/rerank/")
        sys.exit(1)

    # 获取文档
    if args.file:
        documents = read_file(args.file)
        print(f"从文件加载了 {len(documents)} 个文档")
    elif args.documents:
        documents = args.documents
    else:
        print("错误: 必须指定 --documents 或 --file")
        sys.exit(1)

    # 执行重排序
    try:
        results = client.rerank(
            query=args.query,
            documents=documents,
            top_n=args.top,
            model=args.model
        )
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)

    # 输出结果
    if args.json:
        output = {
            "query": args.query,
            "results": [
                {
                    "index": r["index"],
                    "relevance_score": r["relevance_score"],
                    "text": r["document"]["text"]
                }
                for r in results
            ]
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(f"\n查询: {args.query}")
        print(f"文档总数: {len(documents)}")
        print(f"返回结果: {len(results)}")
        print("\n" + "=" * 60)
        for i, r in enumerate(results, 1):
            score = r["relevance_score"]
            text = r["document"]["text"]
            # 截断长文本
            display_text = text[:100] + "..." if len(text) > 100 else text
            print(f"\n{i}. [分数: {score:.4f}] {display_text}")

    # 保存到文件
    if args.output:
        output_data = {
            "query": args.query,
            "model": args.model,
            "results": [
                {
                    "index": r["index"],
                    "score": r["relevance_score"],
                    "text": r["document"]["text"]
                }
                for r in results
            ]
        }
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存到: {args.output}")


if __name__ == "__main__":
    main()