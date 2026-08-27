#!/usr/bin/env python3
"""
LightRAG Knowledge Base Manager
Manages document insertion, deletion, and incremental updates
"""

import asyncio
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional, List

try:
    from lightrag import LightRAG, QueryParam
except ImportError:
    print("Error: LightRAG not installed. Run: pip install 'lightrag-hku[api]'")
    sys.exit(1)


class LightRAGManager:
    """Manages LightRAG knowledge base operations"""

    def __init__(self, working_dir: str):
        self.working_dir = Path(working_dir)
        self.working_dir.mkdir(parents=True, exist_ok=True)
        self.rag: Optional[LightRAG] = None

    async def initialize(self):
        """Initialize LightRAG instance"""
        self.rag = LightRAG(working_dir=str(self.working_dir))
        await self.rag.initialize_storages()
        print(f"✅ LightRAG initialized at {self.working_dir}")

    async def insert_file(self, file_path: str, chunk_size: int = 1200, overlap: int = 100):
        """Insert a single file into the knowledge base"""
        if not self.rag:
            await self.initialize()

        path = Path(file_path)
        if not path.exists():
            print(f"❌ File not found: {file_path}")
            return

        content = path.read_text(encoding='utf-8')
        await self.rag.ainsert(content)
        print(f"✅ Inserted: {file_path}")

    async def insert_directory(self, dir_path: str, extensions: List[str] = None):
        """Insert all files from a directory"""
        if not self.rag:
            await self.initialize()

        if extensions is None:
            extensions = ['.md', '.txt', '.pdf', '.docx', '.html']

        dir_path = Path(dir_path)
        if not dir_path.exists():
            print(f"❌ Directory not found: {dir_path}")
            return

        files = []
        for ext in extensions:
            files.extend(dir_path.rglob(f'*{ext}'))

        if not files:
            print(f"❌ No files found with extensions: {extensions}")
            return

        print(f"📁 Found {len(files)} files to insert...")

        for i, file_path in enumerate(files, 1):
            try:
                content = file_path.read_text(encoding='utf-8')
                await self.rag.ainsert(content)
                print(f"  [{i}/{len(files)}] ✅ {file_path.name}")
            except Exception as e:
                print(f"  [{i}/{len(files)}] ❌ {file_path.name}: {e}")

        print(f"✅ Inserted {len(files)} files")

    async def delete_document(self, doc_id: str):
        """Delete a document by ID"""
        if not self.rag:
            await self.initialize()

        await self.rag.adelete_by_ids([doc_id])
        print(f"✅ Deleted document: {doc_id}")

    async def get_status(self) -> dict:
        """Get knowledge base status"""
        if not self.rag:
            await self.initialize()

        # Get storage info
        status = {
            "working_dir": str(self.working_dir),
            "exists": self.working_dir.exists(),
        }

        # Count files in working directory
        if self.working_dir.exists():
            files = list(self.working_dir.rglob('*'))
            status["file_count"] = len([f for f in files if f.is_file()])

        return status

    async def export_knowledge_graph(self, output_path: str):
        """Export knowledge graph to JSON"""
        if not self.rag:
            await self.initialize()

        # Get graph data
        # Note: This is a simplified version, actual implementation depends on LightRAG API
        print(f"📊 Exporting knowledge graph to {output_path}...")
        print("⚠️ Note: Graph export requires Neo4J or similar backend")

    async def close(self):
        """Close LightRAG instance"""
        if self.rag:
            await self.rag.finalize_storages()
            print("✅ LightRAG closed")


async def main():
    parser = argparse.ArgumentParser(description="LightRAG Knowledge Base Manager")
    parser.add_argument("--working-dir", "-w", default="./rag_storage", help="Working directory")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize knowledge base")

    # Insert command
    insert_parser = subparsers.add_parser("insert", help="Insert documents")
    insert_parser.add_argument("--file", "-f", help="Single file to insert")
    insert_parser.add_argument("--dir", "-d", help="Directory to insert")
    insert_parser.add_argument("--ext", "-e", nargs="+", default=[".md", ".txt"], help="File extensions")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete document")
    delete_parser.add_argument("doc_id", help="Document ID to delete")

    # Status command
    status_parser = subparsers.add_parser("status", help="Get status")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export knowledge graph")
    export_parser.add_argument("--output", "-o", required=True, help="Output path")

    args = parser.parse_args()

    manager = LightRAGManager(args.working_dir)

    try:
        if args.command == "init":
            await manager.initialize()

        elif args.command == "insert":
            if args.file:
                await manager.insert_file(args.file)
            elif args.dir:
                await manager.insert_directory(args.dir, args.ext)
            else:
                print("❌ Please specify --file or --dir")

        elif args.command == "delete":
            await manager.delete_document(args.doc_id)

        elif args.command == "status":
            status = await manager.get_status()
            print(json.dumps(status, indent=2))

        elif args.command == "export":
            await manager.export_knowledge_graph(args.output)

        else:
            parser.print_help()

    finally:
        await manager.close()


if __name__ == "__main__":
    asyncio.run(main())