"""
MCP Integration Center
按需调用MCP服务 - 高效的MCP客户端池

Usage:
    from mcp_client import MCPClientPool, MCPServerType, MCPRequest

    async def main():
        pool = MCPClientPool()

        request = MCPRequest(
            server_type=MCPServerType.GEOCODER,
            operation="geocode",
            params={"address": "北京市朝阳区"}
        )
        response = await pool.call(request)
        print(response.data)

        pool.close_all()

    asyncio.run(main())
"""

from .mcp_client import (
    MCPClientPool,
    MCPServerType,
    MCPConfig,
    MCPRequest,
    MCPResponse,
)

__all__ = [
    "MCPClientPool",
    "MCPServerType",
    "MCPConfig",
    "MCPRequest",
    "MCPResponse",
]

__version__ = "1.0.0"
