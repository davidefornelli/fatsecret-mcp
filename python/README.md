# FatSecret MCP Python Port

Python 3.11 port of the FatSecret MCP server using FastMCP v3. All 12 tools from the JavaScript server are supported.

## Quick Start

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest -q
```

## Running the MCP server

```bash
# From the python/ directory after installing
.venv/bin/python -c "from fatsecret_mcp.server import create_server; create_server().run()"
# Or use the entrypoint (after install)
fatsecret-mcp
```

Credentials can be set via the `set_credentials` tool or environment variables `CLIENT_ID` and `CLIENT_SECRET` (loaded when the config file is empty).
