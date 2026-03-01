import asyncio
from unittest.mock import patch

import pytest

from fatsecret_mcp.server import create_server
from fastmcp.exceptions import ToolError


def _tool_names():
    mcp = create_server()
    tools = asyncio.run(mcp.list_tools())
    return [t.name for t in tools]


def test_server_has_set_credentials_tool():
    assert "set_credentials" in _tool_names()


def test_server_has_check_auth_status_tool():
    assert "check_auth_status" in _tool_names()


def test_server_has_start_oauth_flow_tool():
    assert "start_oauth_flow" in _tool_names()


def test_server_has_complete_oauth_flow_tool():
    assert "complete_oauth_flow" in _tool_names()


def test_server_has_all_twelve_tools():
    names = _tool_names()
    expected = {
        "set_credentials",
        "start_oauth_flow",
        "complete_oauth_flow",
        "search_foods",
        "get_food",
        "search_recipes",
        "get_recipe",
        "get_user_profile",
        "get_user_food_entries",
        "add_food_entry",
        "check_auth_status",
        "get_weight_month",
    }
    assert expected == set(names), f"Missing or extra tools: {set(names) ^ expected}"


async def _call_tool(name: str, arguments: dict):
    mcp = create_server()
    # Resolve and run the tool
    tools = await mcp.list_tools()
    tool = next((t for t in tools if t.name == name), None)
    assert tool is not None
    result = await tool.run(arguments)
    return result


def test_search_foods_without_credentials_raises():
    """Without credentials set, search_foods should raise ToolError with clear message."""
    with patch("fatsecret_mcp.server.load_config", return_value={"clientId": "", "clientSecret": ""}):
        with pytest.raises(ToolError) as exc_info:
            asyncio.run(_call_tool("search_foods", {"searchExpression": "apple"}))
        assert "credentials" in str(exc_info.value).lower()


def test_get_user_profile_without_oauth_raises():
    """Without OAuth, get_user_profile should raise ToolError (user authentication required)."""
    with patch("fatsecret_mcp.server.load_config", return_value={
        "clientId": "a", "clientSecret": "b",
        "accessToken": "", "accessTokenSecret": "", "userId": "",
    }):
        with pytest.raises(ToolError) as exc_info:
            asyncio.run(_call_tool("get_user_profile", {}))
        assert "authentication" in str(exc_info.value).lower() or "oauth" in str(exc_info.value).lower()
