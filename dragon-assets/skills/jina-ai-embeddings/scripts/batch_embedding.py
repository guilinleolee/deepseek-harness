#!/usr/bin/env python3
"""
Jina AI Batch Embedding Client
批量embedding处理工具，支持大文件分割和进度追踪

使用方法:
    python3 batch_embedding.py --input ./docs/ --output ./embeddings.json --batch-size 32
    python3 batch_embedding.py --file large_file.txt --output embeddings.json --chunk-size 500
"""

import os
import sys
import json
import argparse
from typing import List, Optional, Dict
import time

# 导入embedding客户端
from embedding import JinaEmbeddingClient


class BatchEmbeddingProcessor:
    """批量embedding处理器"""

    def __init__(self, api_key: Optional[str] = None):
        self.client = JinaEmbeddingClient(api_key)
        self.total_tokens = 0

    def count_tokens(self, texts: List[str]) -> int:
        """估算token数量（简单估算：中文~2字符=1token，英文~4字符=1token）"""
        total = 0
        for text in texts:
            # 简单估算
            chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
            other_chars = len(text) - chinese_chars
            total += chinese_chars // 2 + other_chars // 4
        return total

    def process_file(self, file_path: str, chunk_size: int = 500, overlap: int = 50) -> Dict:
        """处理单个大文件，按段落分割"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 按段落分割
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

        # 如果段落太大，进一步分割
        chunks = []
        for para in paragraphs:
            if len(para) > chunk_size * 5:
                # 长段落按行分割
                lines = para.split("\n")
                current_chunk = ""
                for line in lines:
                    if len(current_chunk) + len(line) > chunk_size * 5:
                        if current_chunk:
                            chunks.append(current_chunk)
                        current_chunk = line
                    else:
                        current_chunk += "\n" + line if current_chunk else line
                if current_chunk:
                    chunks.append(current_chunk)
            else:
                chunks.append(para)

        # 估算token
        estimated_tokens = self.count_tokens(chunks)
        print(f"  文件: {os.path.basename(file_path)}")
        print(f"  段落数: {len(chunks)}, 估算tokens: {estimated_tokens}")

        # 检查免费额度
        if estimated_tokens > 2000000:
            print(f"  警告: 预估tokens({estimated_tokens})超过月免费额度200万")
            return {"error": "exceeds_free_quota", "tokens": estimated_tokens}

        # 批量处理
        embeddings = self.client.batch_encode(chunks)

        return {
            "file": file_path,
            "chunks": chunks,
            "embeddings": embeddings,
            "count": len(chunks),
            "estimated_tokens": estimated_tokens
        }

    def process_directory(self, dir_path: str, extensions: List[str] = [".md", ".txt", ".py", ".json"],
                         batch_size: int = 32) -> List[Dict]:
        """处理目录下的所有文件"""
        results = []
        total_files = 0
        total_tokens = 0

        for root, dirs, files in os.walk(dir_path):
            # 跳过隐藏目录和特殊目录
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["node_modules", "__pycache__"]]

            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    try:
                        result = self.process_file(file_path)
                        if "error" not in result:
                            results.append(result)
                            total_files += 1
                            total_tokens += result.get("estimated_tokens", 0)
                            print(f"  已处理: {file_path}")
                        else:
                            print(f"  跳过: {file_path} - {result['error']}")
                    except Exception as e:
                        print(f"  错误: {file_path} - {e}")

        print(f"\n总计: {total_files}个文件, {total_tokens} tokens")
        return results

    def search_similar(self, query: str, documents: List[str], top_k: int = 5) -> List[Dict]:
        """语义搜索：query与documents的余弦相似度"""
        query_embedding = self.client.encode_single(query)
        doc_embeddings = self.client.encode(documents)

        # 计算余弦相似度
        results = []
        for i, doc_emb in enumerate(doc_embeddings):
            dot = sum(q * d for q, d in zip(query_embedding, doc_emb))
            norm_query = sum(q ** 2 for q in query_embedding) ** 0.5
            norm_doc = sum(d ** 2 for d in doc_emb) ** 0.5
            similarity = dot / (norm_query * norm_doc + 1e-10)
            results.append({
                "index": i,
                "text": documents[i][:200],
                "similarity": round(similarity, 4)
            })

        # 排序返回top_k
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]


def main():
    parser = argparse.ArgumentParser(description="Jina AI批量Embedding工具")
    parser.add_argument("--input", "-i", help="输入文件或目录")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--file", "-f", help="单文件处理模式")
    parser.add_argument("--batch-size", type=int, default=32, help="批量大小")
    parser.add_argument("--chunk-size", type=int, default=500, help="单段落最大字符数")
    parser.add_argument("--search", "-s", help="语义搜索模式")
    parser.add_argument("--top", type=int, default=5, help="返回前N个结果")
    parser.add_argument("--model", default="jina-embeddings-v3", help="使用的模型")

    args = parser.parse_args()

    try:
        processor = BatchEmbeddingProcessor()
    except ValueError as e:
        print(f"错误: {e}")
        print("请设置 JINA_API_KEY 环境变量")
        sys.exit(1)

    # 语义搜索模式
    if args.search:
        print("语义搜索模式")
        print("请提供要搜索的文档（每行一个，按Ctrl+D结束输入）:")
        documents = []
        try:
            while True:
                line = input()
                if line.strip():
                    documents.append(line)
        except EOFError:
            pass

        if not documents:
            print("错误: 未提供文档")
            sys.exit(1)

        results = processor.search_similar(args.search, documents, args.top)

        print(f"\n查询: {args.search}")
        print(f"文档总数: {len(documents)}")
        print(f"返回结果: {len(results)}")
        print("\n" + "=" * 60)
        for i, r in enumerate(results, 1):
            print(f"\n{i}. [相似度: {r['similarity']:.4f}]")
            print(f"   {r['text'][:150]}...")

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump({
                    "query": args.search,
                    "results": results
                }, f, ensure_ascii=False, indent=2)
            print(f"\n结果已保存到: {args.output}")

        return

    # 文件处理模式
    if args.input:
        input_path = args.input

        if os.path.isdir(input_path):
            print(f"批量处理目录: {input_path}")
            results = processor.process_directory(input_path, batch_size=args.batch_size)
        elif os.path.isfile(input_path):
            print(f"处理单个文件: {input_path}")
            result = processor.process_file(input_path, chunk_size=args.chunk_size)
            results = [result]
        else:
            print(f"错误: 路径不存在 - {input_path}")
            sys.exit(1)

        # 输出结果
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n结果已保存到: {args.output}")

        return

    # 单文件模式
    if args.file:
        result = processor.process_file(args.file, chunk_size=args.chunk_size)
        print(f"\n处理完成: {result['count']}个段落")
        print(f"估算tokens: {result.get('estimated_tokens', 0)}")

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"结果已保存到: {args.output}")

        return

    # 无参数模式显示帮助
    parser.print_help()


if __name__ == "__main__":
    main()