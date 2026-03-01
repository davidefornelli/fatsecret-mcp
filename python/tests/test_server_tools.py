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
