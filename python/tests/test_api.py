from unittest.mock import MagicMock, patch

import httpx

from fatsecret_mcp.api import FatSecretClient


def test_food_search_calls_correct_url_and_method():
    with patch.object(httpx, "get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '{"foods": {}}'
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        client = FatSecretClient(client_id="cid", client_secret="csec")
        client.search_foods("apple")

        assert mock_get.called
        call_args = mock_get.call_args
        url = call_args[0][0]
        params = call_args[1].get("params", {})
        assert "platform.fatsecret.com" in url
        assert params.get("method") == "foods.search"
        assert params.get("search_expression") == "apple"
