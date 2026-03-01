import asyncio

from fatsecret_mcp.server import create_server


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
