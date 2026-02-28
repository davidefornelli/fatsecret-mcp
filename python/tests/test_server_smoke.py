from fatsecret_mcp.server import create_server


def test_create_server_returns_instance():
    server = create_server()
    assert server is not None
