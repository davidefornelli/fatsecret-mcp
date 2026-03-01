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

## Testing by calling the server

You can call tools **in-process** (no MCP transport) for quick manual testing:

```bash
# List all tools
python scripts/call_server.py list
python scripts/call_server.py list -v   # with descriptions

# Call a tool (no arguments)
python scripts/call_server.py call check_auth_status

# Call a tool with JSON arguments
python scripts/call_server.py call search_foods --args '{"searchExpression": "apple", "maxResults": 5}'
python scripts/call_server.py call set_credentials --args '{"clientId": "YOUR_ID", "clientSecret": "YOUR_SECRET"}'
```

Config is read from `~/.fatsecret-mcp-config.json` (same as when the server runs under Cursor). To test with Cursor or another MCP client, add the server via stdio with command `fatsecret-mcp` (or `python -m fatsecret_mcp.server`).

## Testing with official MCP tools

The [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) is the official interactive tool for testing MCP servers. It opens a web UI where you can list tools, run them with custom arguments, and see results.

**Requirements:** Node.js (for `npx`). Install the Python package first (`pip install -e .`).

From the `python/` directory:

```bash
# Run Inspector with your server (replace $PWD with the full path to python/ if needed)
npx @modelcontextprotocol/inspector .venv/bin/python -m fatsecret_mcp.server
```

Or if `fatsecret-mcp` is on your PATH (e.g. after `pip install -e .`):

```bash
npx @modelcontextprotocol/inspector fatsecret-mcp
```

With [uv](https://docs.astral.sh/uv/), from the repo root:

```bash
npx @modelcontextprotocol/inspector uv --directory python run fatsecret-mcp
```

The Inspector opens at **http://localhost:6274/** (proxy on 6277). Use the **Tools** tab to call `check_auth_status`, `search_foods`, etc., with JSON arguments. The server uses the same config as above (`~/.fatsecret-mcp-config.json`).
