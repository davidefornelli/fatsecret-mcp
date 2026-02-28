from fastmcp import FastMCP


def create_server() -> FastMCP:
    """Create the FastMCP server instance."""
    return FastMCP(name="fatsecret")
