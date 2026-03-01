"""FatSecret MCP server — FastMCP v3 with all tools."""

import json

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.tools import ToolResult
from mcp.types import TextContent

from fatsecret_mcp.api import FatSecretClient
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

    @mcp.tool()
    def start_oauth_flow(callbackUrl: str = "oob") -> ToolResult:
        """Start the 3-legged OAuth flow to get user authorization."""
        cfg = load_config()
        if not cfg.get("clientId") or not cfg.get("clientSecret"):
            raise ToolError("Please set your FatSecret API credentials first using set_credentials")
        try:
            client = FatSecretClient(cfg["clientId"], cfg["clientSecret"])
            resp = client.request_token(callback_url=callbackUrl)
            token = resp.get("oauth_token", "")
            token_secret = resp.get("oauth_token_secret", "")
            auth_url = client.get_authorize_url(token)
            text = (
                f"OAuth flow started successfully!\n\n"
                f"Request Token: {token}\nRequest Token Secret: {token_secret}\n\n"
                f"Please visit this URL to authorize the application:\n{auth_url}\n\n"
                "After authorization, you'll receive a verifier code. Use the complete_oauth_flow tool "
                "with the request token, request token secret, and verifier to complete the authentication."
            )
            return ToolResult(content=[TextContent(type="text", text=text)])
        except Exception as e:
            raise ToolError(f"Failed to start OAuth flow: {e}") from e

    @mcp.tool()
    def complete_oauth_flow(
        requestToken: str, requestTokenSecret: str, verifier: str
    ) -> ToolResult:
        """Complete the OAuth flow with the authorization code/verifier."""
        cfg = load_config()
        if not cfg.get("clientId") or not cfg.get("clientSecret"):
            raise ToolError("Please set your FatSecret API credentials first")
        try:
            client = FatSecretClient(cfg["clientId"], cfg["clientSecret"])
            resp = client.exchange_token(requestToken, requestTokenSecret, verifier)
            cfg["accessToken"] = resp.get("oauth_token", "")
            cfg["accessTokenSecret"] = resp.get("oauth_token_secret", "")
            cfg["userId"] = resp.get("user_id", "")
            save_config(cfg)
            user_id = cfg.get("userId", "")
            text = (
                f"OAuth flow completed successfully! You are now authenticated with FatSecret.\n\n"
                f"User ID: {user_id}\n\n"
                "You can now use user-specific tools like get_user_profile, get_user_food_entries, and add_food_entry."
            )
            return ToolResult(content=[TextContent(type="text", text=text)])
        except Exception as e:
            raise ToolError(f"Failed to complete OAuth flow: {e}") from e

    @mcp.tool()
    def search_foods(
        searchExpression: str,
        pageNumber: int = 0,
        maxResults: int = 20,
    ) -> ToolResult:
        """Search for foods in the FatSecret database."""
        cfg = load_config()
        if not cfg.get("clientId") or not cfg.get("clientSecret"):
            raise ToolError("Please set your FatSecret API credentials first")
        try:
            client = FatSecretClient(cfg["clientId"], cfg["clientSecret"])
            resp = client.search_foods(searchExpression, pageNumber, maxResults)
            return ToolResult(
                content=[TextContent(type="text", text=json.dumps(resp, indent=2))]
            )
        except Exception as e:
            raise ToolError(f"Failed to search foods: {e}") from e

    @mcp.tool()
    def get_food(foodId: str) -> ToolResult:
        """Get detailed information about a specific food item."""
        cfg = load_config()
        if not cfg.get("clientId") or not cfg.get("clientSecret"):
            raise ToolError("Please set your FatSecret API credentials first")
        try:
            client = FatSecretClient(cfg["clientId"], cfg["clientSecret"])
            resp = client.get_food(foodId)
            return ToolResult(
                content=[TextContent(type="text", text=json.dumps(resp, indent=2))]
            )
        except Exception as e:
            raise ToolError(f"Failed to get food: {e}") from e

    @mcp.tool()
    def search_recipes(
        searchExpression: str,
        pageNumber: int = 0,
        maxResults: int = 20,
    ) -> ToolResult:
        """Search for recipes in the FatSecret database."""
        cfg = load_config()
        if not cfg.get("clientId") or not cfg.get("clientSecret"):
            raise ToolError("Please set your FatSecret API credentials first")
        try:
            client = FatSecretClient(cfg["clientId"], cfg["clientSecret"])
            resp = client.search_recipes(searchExpression, pageNumber, maxResults)
            return ToolResult(
                content=[TextContent(type="text", text=json.dumps(resp, indent=2))]
            )
        except Exception as e:
            raise ToolError(f"Failed to search recipes: {e}") from e

    @mcp.tool()
    def get_recipe(recipeId: str) -> ToolResult:
        """Get detailed information about a specific recipe."""
        cfg = load_config()
        if not cfg.get("clientId") or not cfg.get("clientSecret"):
            raise ToolError("Please set your FatSecret API credentials first")
        try:
            client = FatSecretClient(cfg["clientId"], cfg["clientSecret"])
            resp = client.get_recipe(recipeId)
            return ToolResult(
                content=[TextContent(type="text", text=json.dumps(resp, indent=2))]
            )
        except Exception as e:
            raise ToolError(f"Failed to get recipe: {e}") from e

    def _user_client(cfg: dict) -> FatSecretClient:
        if not cfg.get("accessToken") or not cfg.get("accessTokenSecret"):
            raise ToolError(
                "User authentication required. Please complete the OAuth flow first."
            )
        return FatSecretClient(
            cfg["clientId"],
            cfg["clientSecret"],
            access_token=cfg.get("accessToken"),
            access_token_secret=cfg.get("accessTokenSecret"),
        )

    @mcp.tool()
    def get_user_profile() -> ToolResult:
        """Get the authenticated user's profile information."""
        cfg = load_config()
        if not cfg.get("clientId") or not cfg.get("clientSecret"):
            raise ToolError("Please set your FatSecret API credentials first")
        try:
            client = _user_client(cfg)
            resp = client.get_user_profile()
            return ToolResult(
                content=[TextContent(type="text", text=json.dumps(resp, indent=2))]
            )
        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Failed to get user profile: {e}") from e

    @mcp.tool()
    def get_user_food_entries(date: str | None = None) -> ToolResult:
        """Get user's food diary entries for a specific date."""
        cfg = load_config()
        if not cfg.get("clientId") or not cfg.get("clientSecret"):
            raise ToolError("Please set your FatSecret API credentials first")
        try:
            client = _user_client(cfg)
            resp = client.get_food_entries(date)
            return ToolResult(
                content=[TextContent(type="text", text=json.dumps(resp, indent=2))]
            )
        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Failed to get food entries: {e}") from e

    @mcp.tool()
    def add_food_entry(
        foodId: str,
        servingId: str,
        quantity: float,
        mealType: str,
        date: str | None = None,
    ) -> ToolResult:
        """Add a food entry to the user's diary."""
        cfg = load_config()
        if not cfg.get("clientId") or not cfg.get("clientSecret"):
            raise ToolError("Please set your FatSecret API credentials first")
        try:
            client = _user_client(cfg)
            resp = client.add_food_entry(foodId, servingId, quantity, mealType, date)
            text = f"Food entry added successfully!\n\n{json.dumps(resp, indent=2)}"
            return ToolResult(content=[TextContent(type="text", text=text)])
        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Failed to add food entry: {e}") from e

    @mcp.tool()
    def get_weight_month(date: str | None = None) -> ToolResult:
        """Get user's weight entries for a specific month."""
        cfg = load_config()
        if not cfg.get("clientId") or not cfg.get("clientSecret"):
            raise ToolError("Please set your FatSecret API credentials first")
        try:
            client = _user_client(cfg)
            resp = client.get_weight_month(date)
            return ToolResult(
                content=[TextContent(type="text", text=json.dumps(resp, indent=2))]
            )
        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Failed to get weight entries for month: {e}") from e

    return mcp
