#!/usr/bin/env python3
"""
Penpot Design System Sync - MCP Server
Provides programmatic access via Model Context Protocol.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sync import PenpotSync
from extract import TokenExtractor
from transform import TokenTransformer


# MCP Server instance
server = Server("penpot-design-system-sync")


# Define available tools
@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="extract_tokens",
            description="Extract design tokens from a Penpot file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "Penpot file ID"},
                    "api_key": {"type": "string", description="Penpot API key"},
                    "api_endpoint": {"type": "string", "description": "Penpot API endpoint"}
                },
                "required": ["file_id"]
            }
        ),
        Tool(
            name="transform_tokens",
            description="Transform design tokens to a specific format",
            inputSchema={
                "type": "object",
                "properties": {
                    "tokens": {"type": "object", "description": "Design tokens object"},
                    "format": {
                        "type": "string",
                        "enum": ["json", "css", "scss", "ios", "android", "yaml", "tailwind"],
                        "description": "Output format"
                    },
                    "prefix": {"type": "string", "description": "CSS variable prefix"},
                    "include_semantic": {"type": "boolean", "description": "Include semantic tokens"}
                },
                "required": ["tokens", "format"]
            }
        ),
        Tool(
            name="sync_tokens",
            description="Sync design tokens to multiple platforms",
            inputSchema={
                "type": "object",
                "properties": {
                    "tokens": {"type": "object", "description": "Design tokens object"},
                    "platforms": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Platforms: ios, android, web, css, scss, tailwind"
                    },
                    "output_dir": {"type": "string", "description": "Output directory"}
                },
                "required": ["tokens", "platforms"]
            }
        ),
        Tool(
            name="diff_tokens",
            description="Compare two versions of design tokens",
            inputSchema={
                "type": "object",
                "properties": {
                    "before": {"type": "object", "description": "Before tokens"},
                    "after": {"type": "object", "description": "After tokens"}
                },
                "required": ["before", "after"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    try:
        if name == "extract_tokens":
            return await handle_extract_tokens(arguments)
        elif name == "transform_tokens":
            return await handle_transform_tokens(arguments)
        elif name == "sync_tokens":
            return await handle_sync_tokens(arguments)
        elif name == "diff_tokens":
            return await handle_diff_tokens(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_extract_tokens(args: Dict[str, Any]) -> List[TextContent]:
    """Extract tokens from Penpot."""
    sync = PenpotSync(
        api_key=args.get("api_key"),
        api_endpoint=args.get("api_endpoint", "https://api.penpot.app/v1")
    )
    tokens = sync.extract_tokens(file_id=args["file_id"])
    return [TextContent(type="text", text=json.dumps(tokens, indent=2))]


async def handle_transform_tokens(args: Dict[str, Any]) -> List[TextContent]:
    """Transform tokens to format."""
    transformer = TokenTransformer(args["tokens"])
    options = {
        "prefix": args.get("prefix", ""),
        "includeSemantic": args.get("include_semantic", False),
        "includeW3C": args.get("include_w3c", False)
    }
    result = transformer.transform(args["format"], options)
    return [TextContent(type="text", text=result)]


async def handle_sync_tokens(args: Dict[str, Any]) -> List[TextContent]:
    """Sync tokens to platforms."""
    sync = PenpotSync()
    results = sync.export(
        tokens=args["tokens"],
        formats=args["platforms"],
        output_dir=args.get("output_dir", "./design-system")
    )

    output = []
    for platform, content in results.items():
        output.append(f"## {platform}\n\n```\n{content}\n```\n")

    return [TextContent(type="text", text="\n".join(output))]


async def handle_diff_tokens(args: Dict[str, Any]) -> List[TextContent]:
    """Diff two token versions."""
    from diff import TokenDiffer
    differ = TokenDiffer()
    result = differ.compare_tokens(args["before"], args["after"])
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
