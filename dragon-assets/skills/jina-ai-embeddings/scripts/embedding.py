#!/usr/bin/env python3
"""
Jina AI Embedding Client
免费多语言Embedding API封装

使用方法:
    python3 embedding.py "测试文本"
    python3 embedding.py --input ./docs/ --output ./embeddings.json
"""

import os
import sys
import json
import argparse
import requests
from typing import List, Optional

# 默认API地址
DEFAULT_BASE_URL = "https://api.jina.ai/embed"


class JinaEmbeddingClient:
    """Jina AI Embedding客户端"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("JINA_API_KEY")
        if not self.api_key:
            raise ValueError("需要设置 JINA_API_KEY 环境变量")
        self.base_url = DEFAULT_BASE_URL

    def encode(self, texts: List[str], model: str = "jina-embeddings-v3") -> List[List[float]]:
        """将文本列表转换为embedding向量"""
        response = requests.post(
            self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "input": texts,
                "encoding_type": "float"
            },
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            return [item["embedding"] for item in sorted(data["data"], key=lambda x: x["index"])]
        else:
            raise Exception(f"Embedding failed: {response.status_code} - {response.text}")

    def encode_single(self, text: str, model: str = "jina-embeddings-v3") -> List[float]:
        """将单个文本转换为embedding向量"""
        embeddings = self.encode([text], model)
        return embeddings[0]

    def similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的余弦相似度"""
        import numpy as np

        emb1 = self.encode_single(text1)
        emb2 = self.encode_single(text2)

        dot_product = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)

        return dot_product / (norm1 * norm2)

    def batch_encode(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """批量处理文本，避免超出API限制"""
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = self.encode(batch)
            all_embeddings.extend(embeddings)
            print(f"  进度: {min(i + batch_size, len(texts))}/{len(texts)}", end="\r")

        print()
        return all_embeddings


def encode_file(file_path: str, client: JinaEmbeddingClient) -> dict:
    """读取文件内容并进行embedding"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 按段落分割
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

    if not paragraphs:
        return {"file": file_path, "embedding": None, "error": "无有效文本"}

    embeddings = client.batch_encode(paragraphs)

    return {
        "file": file_path,
        "paragraphs": paragraphs,
        "embeddings": embeddings,
        "count": len(paragraphs)
    }


def encode_directory(dir_path: str, client: JinaEmbeddingClient, extensions: List[str] = [".md", ".txt", ".py"]) -> List[dict]:
    """遍历目录处理所有文本文件"""
    import os

    results = []

    for root, dirs, files in os.walk(dir_path):
        # 跳过隐藏目录和特殊目录
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["node_modules", "__pycache__"]]

        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                try:
                    result = encode_file(file_path, client)
                    results.append(result)
                    print(f"  已处理: {file_path}")
                except Exception as e:
                    print(f"  跳过: {file_path} - {e}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Jina AI Embedding工具")
    parser.add_argument("text", nargs="?", help="要编码的文本")
    parser.add_argument("--input", "-i", help="输入文件或目录")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--similarity", nargs=2, metavar=("TEXT1", "TEXT2"), help="计算两个文本的相似度")
    parser.add_argument("--model", default="jina-embeddings-v3", help="使用的模型")

    args = parser.parse_args()

    try:
        client = JinaEmbeddingClient()
    except ValueError as e:
        print(f"错误: {e}")
        print("请设置 JINA_API_KEY 环境变量")
        print("获取免费API Key: https://jina.ai/embeddings/")
        sys.exit(1)

    # 相似度计算模式
    if args.similarity:
        text1, text2 = args.similarity
        similarity = client.similarity(text1, text2)
        print(f"\n文本1: {text1}")
        print(f"文本2: {text2}")
        print(f"相似度: {similarity:.4f}")
        return

    # 文件/目录模式
    if args.input:
        input_path = args.input

        if os.path.isdir(input_path):
            print(f"正在处理目录: {input_path}")
            results = encode_directory(input_path, client)
        elif os.path.isfile(input_path):
            print(f"正在处理文件: {input_path}")
            results = [encode_file(input_path, client)]
        else:
            print(f"错误: 路径不存在 - {input_path}")
            sys.exit(1)

        # 输出结果
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n结果已保存到: {args.output}")

        return results

    # 单文本模式
    if args.text:
        embedding = client.encode_single(args.text, args.model)
        print(f"\n文本: {args.text}")
        print(f"维度: {len(embedding)}")
        print(f"前5维: {embedding[:5]}")
        return {"embedding": embedding, "dimension": len(embedding)}

    # 无参数模式显示帮助
    parser.print_help()


if __name__ == "__main__":
    main()