"""Configuration load/save for FatSecret MCP. Uses same JSON keys as JS: clientId, clientSecret, accessToken, accessTokenSecret, userId."""

import json
from pathlib import Path


def get_config_path() -> Path:
    """Return path to config file in user home."""
    return Path.home() / ".fatsecret-mcp-config.json"


def _default_config() -> dict:
    return {
        "clientId": "",
        "clientSecret": "",
        "accessToken": "",
        "accessTokenSecret": "",
        "userId": "",
    }


def load_config() -> dict:
    """Load config from disk. Returns dict with JS key names; missing file or empty values use defaults."""
    path = get_config_path()
    if not path.exists():
        return _default_config()
    text = path.read_text()
    data = json.loads(text)
    out = _default_config()
    for key in out:
        if key in data and data[key] is not None:
            out[key] = data[key]
    return out


def save_config(config: dict) -> None:
    """Write config to disk. Creates parent dirs if needed. Use JS key names."""
    path = get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, indent=2))
