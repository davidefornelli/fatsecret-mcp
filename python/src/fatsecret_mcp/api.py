"""FatSecret REST API client with OAuth 1.0a signing."""

import json
import secrets
import time
from urllib.parse import urlencode

import httpx

from fatsecret_mcp.oauth import generate_signature, percent_encode

BASE_URL = "https://platform.fatsecret.com/rest/server.api"
REQUEST_TOKEN_URL = "https://authentication.fatsecret.com/oauth/request_token"
AUTHORIZE_URL = "https://authentication.fatsecret.com/oauth/authorize"
ACCESS_TOKEN_URL = "https://authentication.fatsecret.com/oauth/access_token"


class FatSecretClient:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        access_token: str | None = None,
        access_token_secret: str | None = None,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token or ""
        self.access_token_secret = access_token_secret or ""

    def _oauth_params(self, extra: dict | None = None, token: str | None = None) -> dict:
        out = {
            "oauth_consumer_key": self.client_id,
            "oauth_nonce": secrets.token_hex(16),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(time.time())),
            "oauth_version": "1.0",
        }
        if extra:
            out.update(extra)
        if token:
            out["oauth_token"] = token
        return out

    def _signed_request(
        self,
        method: str,
        url: str,
        params: dict,
        token: str | None = None,
        token_secret: str | None = None,
    ) -> dict:
        oauth = self._oauth_params(token=token)
        all_params = {**params, **oauth}
        sig = generate_signature(
            method, url, all_params, self.client_secret, token_secret or ""
        )
        all_params["oauth_signature"] = sig

        if method == "GET":
            resp = httpx.get(url, params=all_params, timeout=30.0)
        else:
            resp = httpx.post(
                url, data=all_params, timeout=30.0  # form-encoded
            )
        resp.raise_for_status()
        text = resp.text
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # query-string style response
            from urllib.parse import parse_qs
            parsed = parse_qs(text)
            return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}

    def request_token(self, callback_url: str = "oob") -> dict:
        """Get request token; returns oauth_token, oauth_token_secret."""
        return self._signed_request(
            "POST", REQUEST_TOKEN_URL, {"oauth_callback": callback_url}
        )

    def get_authorize_url(self, request_token: str) -> str:
        return f"{AUTHORIZE_URL}?oauth_token={percent_encode(request_token)}"

    def exchange_token(
        self, request_token: str, request_token_secret: str, verifier: str
    ) -> dict:
        """Exchange request token for access token; returns oauth_token, oauth_token_secret, user_id."""
        return self._signed_request(
            "GET",
            ACCESS_TOKEN_URL,
            {"oauth_verifier": verifier},
            token=request_token,
            token_secret=request_token_secret,
        )

    def api_request(self, params: dict, use_access_token: bool = True) -> dict:
        """REST API call; params must include 'method'. Adds format=json."""
        params = dict(params)
        params["format"] = "json"
        token = self.access_token if use_access_token else None
        token_secret = self.access_token_secret if use_access_token else None
        return self._signed_request(
            "GET", BASE_URL, params, token=token, token_secret=token_secret
        )

    def api_post(self, params: dict) -> dict:
        """POST to REST API (e.g. food_entry.create). Uses access token."""
        params = dict(params)
        params["format"] = "json"
        oauth = self._oauth_params(token=self.access_token)
        all_params = {**params, **oauth}
        sig = generate_signature(
            "POST", BASE_URL, all_params,
            self.client_secret, self.access_token_secret
        )
        all_params["oauth_signature"] = sig
        resp = httpx.post(BASE_URL, data=all_params, timeout=30.0)
        resp.raise_for_status()
        text = resp.text
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            from urllib.parse import parse_qs
            parsed = parse_qs(text)
            return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}

    def search_foods(
        self,
        search_expression: str,
        page_number: int = 0,
        max_results: int = 20,
    ) -> dict:
        return self.api_request(
            {
                "method": "foods.search",
                "search_expression": search_expression,
                "page_number": str(page_number),
                "max_results": str(max_results),
            },
            use_access_token=False,
        )

    def get_food(self, food_id: str) -> dict:
        return self.api_request(
            {"method": "food.get", "food_id": food_id},
            use_access_token=False,
        )

    def search_recipes(
        self,
        search_expression: str,
        page_number: int = 0,
        max_results: int = 20,
    ) -> dict:
        return self.api_request(
            {
                "method": "recipes.search",
                "search_expression": search_expression,
                "page_number": str(page_number),
                "max_results": str(max_results),
            },
            use_access_token=False,
        )

    def get_recipe(self, recipe_id: str) -> dict:
        return self.api_request(
            {"method": "recipe.get", "recipe_id": recipe_id},
            use_access_token=False,
        )

    def get_user_profile(self) -> dict:
        return self.api_request(
            {"method": "profile.get"},
            use_access_token=True,
        )

    def get_food_entries(self, date_str: str | None = None) -> dict:
        from fatsecret_mcp.dates import date_to_fatsecret_format
        date_param = date_to_fatsecret_format(date_str)
        return self.api_request(
            {"method": "food_entries.get", "date": date_param},
            use_access_token=True,
        )

    def add_food_entry(
        self,
        food_id: str,
        serving_id: str,
        quantity: float,
        meal_type: str,
        date_str: str | None = None,
    ) -> dict:
        from fatsecret_mcp.dates import date_to_fatsecret_format
        date_param = date_to_fatsecret_format(date_str)
        return self.api_post(
            {
                "method": "food_entry.create",
                "food_id": food_id,
                "serving_id": serving_id,
                "quantity": str(int(quantity) if quantity == int(quantity) else quantity),
                "meal": meal_type,
                "date": date_param,
            }
        )

    def get_weight_month(self, date_str: str | None = None) -> dict:
        from fatsecret_mcp.dates import date_to_fatsecret_format
        date_param = date_to_fatsecret_format(date_str)
        return self.api_request(
            {"method": "weights.get_month", "date": date_param},
            use_access_token=True,
        )
