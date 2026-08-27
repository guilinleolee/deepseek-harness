#!/usr/bin/env python3
"""
LightRAG Query Interface
Provides 4 query modes: local, global, hybrid, mix
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path
from typing import Optional

try:
    from lightrag import LightRAG, QueryParam
except ImportError:
    print("Error: LightRAG not installed. Run: pip install 'lightrag-hku[api]'")
    sys.exit(1)


class LightRAGQuerier:
    """LightRAG query interface"""

    MODES = {
        "local": "Text chunk similarity search - best for specific facts",
        "global": "Knowledge graph traversal - best for relationships",
        "hybrid": "Local + Global combined - balanced queries",
        "mix": "Graph + Vector + Reranker - best quality (default)",
    }

    def __init__(self, working_dir: str):
        self.working_dir = Path(working_dir)
        self.rag: Optional[LightRAG] = None

    async def initialize(self):
        """Initialize LightRAG instance"""
        if not self.working_dir.exists():
            print(f"❌ Working directory not found: {self.working_dir}")
            print("Please run 'lightrag_manager.py init' first")
            sys.exit(1)

        self.rag = LightRAG(working_dir=str(self.working_dir))
        await self.rag.initialize_storages()

    async def query(
        self,
        question: str,
        mode: str = "hybrid",
        stream: bool = False,
        only_context: bool = False,
    ) -> str:
        """Execute a query"""
        if not self.rag:
            await self.initialize()

        if mode not in self.MODES:
            print(f"❌ Invalid mode: {mode}")
            print(f"Available modes: {list(self.MODES.keys())}")
            return ""

        param = QueryParam(mode=mode, only_need_context=only_context)

        if stream:
            result = []
            async for chunk in self.rag.aquery_stream(question, param=param):
                print(chunk, end="", flush=True)
                result.append(chunk)
            print()  # New line after streaming
            return "".join(result)
        else:
            result = await self.rag.aquery(question, param=param)
            return result

    async def batch_query(
        self, questions: list, mode: str = "hybrid", output_file: str = None
    ):
        """Execute multiple queries"""
        if not self.rag:
            await self.initialize()

        results = []
        for i, question in enumerate(questions, 1):
            print(f"[{i}/{len(questions)}] Querying: {question[:50]}...")
            result = await self.query(question, mode=mode)
            results.append({"question": question, "answer": result, "mode": mode})

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"✅ Results saved to {output_file}")

        return results

    async def interactive(self, mode: str = "hybrid"):
        """Interactive query mode"""
        if not self.rag:
            await self.initialize()

        print(f"\n🔍 LightRAG Interactive Query (mode: {mode})")
        print("Type 'exit' to quit, 'mode <mode>' to change mode\n")

        while True:
            try:
                question = input("Query: ").strip()
                if not question:
                    continue
                if question.lower() == "exit":
                    break
                if question.lower().startswith("mode "):
                    new_mode = question.split()[1]
                    if new_mode in self.MODES:
                        mode = new_mode
                        print(f"Mode changed to: {mode}")
                    else:
                        print(f"Invalid mode. Available: {list(self.MODES.keys())}")
                    continue

                await self.query(question, mode=mode, stream=True)

            except KeyboardInterrupt:
                print("\nExiting...")
                break

    async def close(self):
        """Close LightRAG instance"""
        if self.rag:
            await self.rag.finalize_storages()


def print_modes():
    """Print available query modes"""
    print("\n📋 Available Query Modes:\n")
    for mode, desc in LightRAGQuerier.MODES.items():
        print(f"  {mode:10} - {desc}")
    print()


async def main():
    parser = argparse.ArgumentParser(description="LightRAG Query Interface")
    parser.add_argument("--working-dir", "-w", default="./rag_storage", help="Working directory")
    parser.add_argument("--mode", "-m", default="hybrid", choices=list(LightRAGQuerier.MODES.keys()), help="Query mode")
    parser.add_argument("--stream", "-s", action="store_true", help="Stream output")
    parser.add_argument("--only-context", "-c", action="store_true", help="Only return context")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--batch", "-b", help="Batch query from file (one question per line)")
    parser.add_argument("--output", "-o", help="Output file for batch results")
    parser.add_argument("question", nargs="?", help="Query question")

    args = parser.parse_args()

    querier = LightRAGQuerier(args.working_dir)

    try:
        if args.interactive:
            await querier.interactive(mode=args.mode)

        elif args.batch:
            with open(args.batch, encoding="utf-8") as f:
                questions = [line.strip() for line in f if line.strip()]
            await querier.batch_query(questions, mode=args.mode, output_file=args.output)

        elif args.question:
            if args.stream:
                await querier.query(args.question, mode=args.mode, stream=True)
            else:
                result = await querier.query(
                    args.question, mode=args.mode, only_context=args.only_context
                )
                print(result)

        else:
            print_modes()
            parser.print_help()

    finally:
        await querier.close()


if __name__ == "__main__":
    asyncio.run(main())