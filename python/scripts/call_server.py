#!/usr/bin/env python3
"""Call FatSecret MCP server tools in-process (no stdio). Use for manual testing.

Examples:
  python scripts/call_server.py list
  python scripts/call_server.py call check_auth_status
  python scripts/call_server.py call search_foods --args '{"searchExpression": "apple", "maxResults": 5}'
  python scripts/call_server.py call set_credentials --args '{"clientId": "x", "clientSecret": "y"}'
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Allow running from repo root or from python/; ensure src is on path
_root = Path(__file__).resolve().parent.parent
for p in (_root, _root / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from fatsecret_mcp.server import create_server  # noqa: E402


async def list_tools(verbose: bool) -> None:
    mcp = create_server()
    tools = await mcp.list_tools()
    for t in tools:
        print(t.name)
        if verbose and t.description:
            print(f"  {t.description.strip().split(chr(10))[0]}")
            if hasattr(t, "inputSchema") and t.inputSchema:
                print(f"  schema: {json.dumps(t.inputSchema, indent=4)}")


async def call_tool(name: str, args_json: str) -> None:
    mcp = create_server()
    tools = await mcp.list_tools()
    tool = next((t for t in tools if t.name == name), None)
    if not tool:
        print(f"Unknown tool: {name}", file=sys.stderr)
        print("Available:", ", ".join(t.name for t in tools), file=sys.stderr)
        sys.exit(1)
    arguments = json.loads(args_json) if args_json.strip() else {}
    try:
        result = await tool.run(arguments)
        # ToolResult has .content (list of TextContent)
        if result and hasattr(result, "content"):
            for part in result.content:
                if hasattr(part, "text"):
                    print(part.text)
        else:
            print(result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Call FatSecret MCP tools in-process (no MCP transport)."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="List all tools").add_argument(
        "-v", "--verbose", action="store_true", help="Show description and schema"
    )
    call_p = sub.add_parser("call", help="Call a tool by name")
    call_p.add_argument("name", help="Tool name (e.g. check_auth_status, search_foods)")
    call_p.add_argument(
        "--args",
        default="{}",
        help='JSON object of arguments (e.g. \'{"searchExpression": "apple"}\')',
    )
    args = parser.parse_args()

    if args.command == "list":
        asyncio.run(list_tools(getattr(args, "verbose", False)))
    else:
        asyncio.run(call_tool(args.name, args.args))
    return 0


if __name__ == "__main__":
    sys.exit(main())
