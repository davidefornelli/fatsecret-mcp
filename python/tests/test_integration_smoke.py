"""Integration smoke test: server starts and exposes all 12 tools."""

import asyncio

from fatsecret_mcp.server import create_server


def test_server_lists_all_twelve_tools():
    async def _check():
        mcp = create_server()
        tools = await mcp.list_tools()
        names = [t.name for t in tools]
        assert len(names) == 12
        assert "set_credentials" in names
        assert "get_weight_month" in names

    asyncio.run(_check())
