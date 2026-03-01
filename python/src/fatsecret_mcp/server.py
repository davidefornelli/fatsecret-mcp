"""FatSecret MCP server — FastMCP v3 with all tools."""

from fastmcp import FastMCP
from fastmcp.tools import ToolResult
from mcp.types import TextContent

from fatsecret_mcp.config import load_config, save_config


def create_server() -> FastMCP:
    """Create the FastMCP server instance with all FatSecret tools."""
    mcp = FastMCP(name="fatsecret")

    @mcp.tool()
    def set_credentials(clientId: str, clientSecret: str) -> ToolResult:
        """Set FatSecret API credentials (Client ID and Client Secret)."""
        cfg = load_config()
        cfg["clientId"] = clientId
        cfg["clientSecret"] = clientSecret
        save_config(cfg)
        msg = "FatSecret API credentials have been set successfully. You can now start the OAuth flow to authenticate users."
        return ToolResult(content=[TextContent(type="text", text=msg)])

    @mcp.tool()
    def check_auth_status() -> ToolResult:
        """Check if the user is authenticated with FatSecret."""
        cfg = load_config()
        has_credentials = bool(cfg.get("clientId") and cfg.get("clientSecret"))
        has_access_token = bool(cfg.get("accessToken") and cfg.get("accessTokenSecret"))
        if has_credentials and has_access_token:
            status = "Fully authenticated"
        elif has_credentials:
            status = "Credentials set, authentication needed"
        else:
            status = "Not configured"
        user_id = cfg.get("userId") or "N/A"
        text = (
            f"Authentication Status: {status}\n\n"
            f"Credentials configured: {has_credentials}\n"
            f"User authenticated: {has_access_token}\n"
            f"User ID: {user_id}"
        )
        return ToolResult(content=[TextContent(type="text", text=text)])

    return mcp
