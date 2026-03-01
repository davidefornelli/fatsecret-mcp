from pathlib import Path
from unittest.mock import patch

from fatsecret_mcp.config import get_config_path, load_config, save_config


def test_get_config_path_returns_path_in_home():
    with patch.dict("os.environ", {"HOME": "/fake/home"}):
        p = get_config_path()
    assert p == Path("/fake/home/.fatsecret-mcp-config.json")


def test_load_config_missing_file_returns_defaults():
    with patch("pathlib.Path.exists", return_value=False):
        cfg = load_config()
    assert cfg.get("clientId") == ""
    assert cfg.get("clientSecret") == ""


def test_save_and_load_roundtrip(tmp_path):
    with patch("fatsecret_mcp.config.get_config_path", return_value=tmp_path / "config.json"):
        save_config({"clientId": "a", "clientSecret": "b"})
        cfg = load_config()
    assert cfg["clientId"] == "a"
    assert cfg["clientSecret"] == "b"
