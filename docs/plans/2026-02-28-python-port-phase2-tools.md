# Python Port Phase 2 — All MCP Tools Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Port all 12 FatSecret MCP tools from the JavaScript server to the Python FastMCP v3 server with behavior parity: config storage, OAuth 1.0a, and FatSecret REST API calls.

**Architecture:** Implement a config module (JSON at `~/.fatsecret-mcp-config.json`), an OAuth/signing helper module (HMAC-SHA1, percent-encoding, base string), a thin FatSecret API client (GET/POST with optional access token), then register each tool on the existing FastMCP server. Use the same tool names, parameter names, and response shape (text content with JSON or message) as the JS server. User-scoped tools require loaded access token; public tools (food/recipe search/get) use client credentials only.

**Tech Stack:** Python 3.11, FastMCP v3, pytest, `httpx` for HTTP (add to `pyproject.toml` if not already present), stdlib `hmac`/`hashlib`/`urllib.parse` for OAuth. Use Context7 for FastMCP tool registration and FatSecret API docs if needed. For Task 4 tests, mock `httpx` with `unittest.mock` or add `respx` as a dev dependency.

**Reference:** `javascript/src/index.ts` — config shape, URLs, method names (`foods.search`, `food.get`, `recipes.search`, `recipe.get`, `profile.get`, `food_entries.get`, `food_entry.create`, `weights.get_month`), and date format (days since epoch).

---

## Task 1: Config module — load/save and path

**Files:**
- Create: `python/src/fatsecret_mcp/config.py`
- Create: `python/tests/test_config.py`

**Step 1: Write the failing test**

In `python/tests/test_config.py`:

```python
import json
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
```

**Step 2: Run test to verify it fails**

Run: `cd python && .venv/bin/pytest tests/test_config.py -v`
Expected: FAIL (e.g. module or function not found).

**Step 3: Implement config module**

In `python/src/fatsecret_mcp/config.py`:

- `get_config_path() -> Path`: return `Path.home() / ".fatsecret-mcp-config.json"`.
- `load_config() -> dict`: if path exists, read JSON and return dict with keys `client_id`, `client_secret`, `access_token`, `access_token_secret`, `user_id` (default "" or None). If file missing, return same structure with empty strings.
- `save_config(config: dict) -> None`: write JSON to path (create parent dirs if needed). Use same key names as above for compatibility with JS (we can use snake_case in Python and map to/from JS keys when reading/writing the file to keep JS-created configs readable, or match JS keys in file: `clientId`, `clientSecret`, `accessToken`, `accessTokenSecret`, `userId`). For parity with JS, store and read the exact keys the JS uses: `clientId`, `clientSecret`, `accessToken`, `accessTokenSecret`, `userId`. So Python code can use a dataclass or internal dict with snake_case and convert at load/save, or use the JS keys in the file. Simplest: use JS keys in file. So load returns dict with keys `clientId`, `clientSecret`, `accessToken`, `accessTokenSecret`, `userId`; save accepts that dict.
- Update tests to use `clientId`/`clientSecret` in the saved/loaded dict.

**Step 4: Run test to verify it passes**

Run: `cd python && .venv/bin/pytest tests/test_config.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add python/src/fatsecret_mcp/config.py python/tests/test_config.py
git commit -m "feat(python): add config load/save for FatSecret MCP"
```

---

## Task 2: Date conversion — days since epoch

**Files:**
- Create: `python/src/fatsecret_mcp/dates.py`
- Create: `python/tests/test_dates.py`

**Step 1: Write the failing test**

In `python/tests/test_dates.py`:

```python
from datetime import date

from fatsecret_mcp.dates import date_to_fatsecret_format


def test_date_to_fatsecret_epoch_is_zero():
    assert date_to_fatsecret_format("1970-01-01") == "0"


def test_date_to_fatsecret_today_positive():
    # 1970-01-02 -> 1 day
    assert date_to_fatsecret_format("1970-01-02") == "1"


def test_date_to_fatsecret_none_uses_today():
    result = date_to_fatsecret_format(None)
    assert result.isdigit()
    assert int(result) >= 0
```

**Step 2: Run test to verify it fails**

Run: `cd python && .venv/bin/pytest tests/test_dates.py -v`
Expected: FAIL.

**Step 3: Implement**

In `python/src/fatsecret_mcp/dates.py`:

- `date_to_fatsecret_format(date_string: str | None) -> str`: if `date_string` is None or empty, use today. Parse as YYYY-MM-DD, compute days since 1970-01-01, return string of that integer.

**Step 4: Run test to verify it passes**

Run: `cd python && .venv/bin/pytest tests/test_dates.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add python/src/fatsecret_mcp/dates.py python/tests/test_dates.py
git commit -m "feat(python): add date_to_fatsecret_format (days since epoch)"
```

---

## Task 3: OAuth 1.0a signing helpers

**Files:**
- Create: `python/src/fatsecret_mcp/oauth.py`
- Create: `python/tests/test_oauth.py`

**Step 1: Write the failing test**

In `python/tests/test_oauth.py`:

```python
from fatsecret_mcp.oauth import percent_encode, create_signature_base_string, generate_signature


def test_percent_encode_special_chars():
    # RFC 5849: !'()* are reserved and must be encoded
    assert percent_encode("a!b") == "a%21b"
    assert "%2A" in percent_encode("*")


def test_signature_base_string_order():
    base = create_signature_base_string("GET", "https://example.com", {"b": "2", "a": "1"})
    assert base.startswith("GET&")
    assert "a%3D1" in base
    assert "b%3D2" in base


def test_generate_signature_deterministic():
    sig = generate_signature("GET", "https://example.com", {"c": "3"}, "client_secret", "")
    assert isinstance(sig, str)
    assert len(sig) > 0
    # Same inputs -> same signature
    sig2 = generate_signature("GET", "https://example.com", {"c": "3"}, "client_secret", "")
    assert sig == sig2
```

**Step 2: Run test to verify it fails**

Run: `cd python && .venv/bin/pytest tests/test_oauth.py -v`
Expected: FAIL.

**Step 3: Implement**

In `python/src/fatsecret_mcp/oauth.py`:

- `percent_encode(s: str) -> str`: encode per OAuth 1.0a (RFC 5849): `urllib.parse.quote(s, safe="")` and ensure `!` `'` `(` `)` `*` are encoded (e.g. replace `~` in safe if needed; standard quote encodes `!()*` when safe="").
- `create_signature_base_string(method: str, url: str, parameters: dict[str, str]) -> str`: sort params by key, build `key=value` joined with `&` (percent-encoded), then `METHOD&encoded(url)&encoded(params_string)`.
- `generate_signature(method, url, parameters, client_secret: str, token_secret: str = "") -> str`: signing key = `percent_encode(client_secret)&percent_encode(token_secret)`, base string as above, HMAC-SHA1 with signing key, return base64.
- Use stdlib `hmac`, `hashlib.sha1`, `base64.b64encode`.

**Step 4: Run test to verify it passes**

Run: `cd python && .venv/bin/pytest tests/test_oauth.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add python/src/fatsecret_mcp/oauth.py python/tests/test_oauth.py
git commit -m "feat(python): add OAuth 1.0a signing helpers"
```

---

## Task 4: FatSecret API client (HTTP + signing)

**Files:**
- Create: `python/src/fatsecret_mcp/api.py`
- Create: `python/tests/test_api.py`

**Step 1: Write the failing test**

In `python/tests/test_api.py`:

- Test that `build_oauth_headers` or the public request builder produces the expected header shape (e.g. contains `OAuth ` and `oauth_signature`). Prefer a unit test that does not hit the network: e.g. given a fixed timestamp/nonce, assert signature is deterministic, or mock `httpx` and assert request URL/body/headers for a simple `foods.search` call.

Example (mock-based):

```python
import respx
from httpx import Response

from fatsecret_mcp.api import FatSecretClient


@respx.mock
def test_food_search_calls_correct_url_and_method(respx_mock):
    respx_mock.get("https://platform.fatsecret.com/rest/server.api").mock(Response(200, json={"foods": {}}))
    client = FatSecretClient(client_id="cid", client_secret="csec")
    client.search_foods("apple")
    assert respx_mock.calls.call_count == 1
    assert "method=foods.search" in str(respx_mock.calls.last.request.url)
```

If you prefer not to add `respx` yet, use a simpler test: e.g. `FatSecretClient(client_id="a", client_secret="b")._build_params(method="foods.search", extra={"search_expression": "x"})` returns dict with `format=json`, `method=foods.search`, `search_expression=x`, and keys required for OAuth.

**Step 2: Run test to verify it fails**

Run: `cd python && .venv/bin/pytest tests/test_api.py -v`
Expected: FAIL.

**Step 3: Implement**

In `python/src/fatsecret_mcp/api.py`:

- Base URL: `https://platform.fatsecret.com/rest/server.api`.
- OAuth request token URL: `https://authentication.fatsecret.com/oauth/request_token`.
- Authorize URL: `https://authentication.fatsecret.com/oauth/authorize`.
- Access token URL: `https://authentication.fatsecret.com/oauth/access_token`.
- Class `FatSecretClient` (or equivalent functions) that:
  - Takes `client_id`, `client_secret`, and optionally `access_token`, `access_token_secret`.
  - Builds OAuth params (oauth_consumer_key, oauth_nonce, oauth_timestamp, oauth_signature_method, oauth_version, optionally oauth_token), merges with request params, adds `format=json`, computes signature, sends GET or POST with `httpx`. For POST, body is application/x-www-form-urlencoded.
- Methods: `request_token(callback_url: str)`, `exchange_token(request_token, request_token_secret, verifier)`, `get(path, params, use_token: bool)`, `post(path, params, use_token: bool)` or a single `api_request(method, params, use_access_token)` that builds the full URL and body. Match JS: `makeOAuthRequest` for request/access token; `makeApiRequest` for REST (adds `format=json`, signs with or without token).

**Step 4: Run test to verify it passes**

Run: `cd python && .venv/bin/pytest tests/test_api.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add python/src/fatsecret_mcp/api.py python/tests/test_api.py
git commit -m "feat(python): add FatSecret API client with OAuth and REST"
```

---

## Task 5: Wire config into server and add set_credentials + check_auth_status

**Files:**
- Modify: `python/src/fatsecret_mcp/server.py`
- Create: `python/tests/test_server_tools.py` (or extend existing)

**Step 1: Write the failing test**

In `python/tests/test_server_tools.py`:

```python
from unittest.mock import patch

from fatsecret_mcp.server import create_server


def test_server_has_set_credentials_tool():
    mcp = create_server()
    tool_names = [t.name for t in mcp._tool_manager.list_tools()]
    assert "set_credentials" in tool_names


def test_server_has_check_auth_status_tool():
    mcp = create_server()
    tool_names = [t.name for t in mcp._tool_manager.list_tools()]
    assert "check_auth_status" in tool_names
```

(Adjust to FastMCP v3 API for listing tools if different — e.g. inspect registered tools via public API.)

**Step 2: Run test to verify it fails**

Run: `cd python && .venv/bin/pytest tests/test_server_tools.py -v`
Expected: FAIL (tools not registered yet).

**Step 3: Implement**

In `python/src/fatsecret_mcp/server.py`:

- Import config and API client (or handlers). Load config at tool call time (like JS). Register two tools with FastMCP v3:
  - `set_credentials(clientId: str, clientSecret: str)`: save to config, return success text content.
  - `check_auth_status()`: read config, return text describing status (Not configured / Credentials set, authentication needed / Fully authenticated) and User ID.
- Use FastMCP tool decorator or equivalent to define name, description, and input schema matching JS (camelCase for MCP: clientId, clientSecret).

**Step 4: Run test to verify it passes**

Run: `cd python && .venv/bin/pytest tests/test_server_tools.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add python/src/fatsecret_mcp/server.py python/tests/test_server_tools.py
git commit -m "feat(python): register set_credentials and check_auth_status tools"
```

---

## Task 6: OAuth flow tools — start_oauth_flow, complete_oauth_flow

**Files:**
- Modify: `python/src/fatsecret_mcp/server.py`
- Modify: `python/tests/test_server_tools.py`

**Step 1: Write the failing test**

Add tests that after calling start_oauth_flow (with mocked API), response contains authorization URL and request token/secret; after complete_oauth_flow (mocked), config has access_token and user_id.

**Step 2: Run test to verify it fails**

Run: `cd python && .venv/bin/pytest tests/test_server_tools.py -v`
Expected: FAIL.

**Step 3: Implement**

- `start_oauth_flow(callbackUrl?: str)`: ensure credentials set; call API request_token(callback_url or "oob"); return text with request token, request token secret, and authorize URL (`authorize_url?oauth_token=...`).
- `complete_oauth_flow(requestToken, requestTokenSecret, verifier)`: call API exchange_token; save access_token, access_token_secret, user_id to config; return success text.

**Step 4: Run test to verify it passes**

Run: `cd python && .venv/bin/pytest tests/test_server_tools.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add python/src/fatsecret_mcp/server.py python/tests/test_server_tools.py
git commit -m "feat(python): add start_oauth_flow and complete_oauth_flow tools"
```

---

## Task 7: Food tools — search_foods, get_food

**Files:**
- Modify: `python/src/fatsecret_mcp/server.py`
- Modify: `python/tests/test_server_tools.py`

**Step 1: Write the failing test**

- Assert tool names `search_foods` and `get_food` are registered.
- Optionally: mock API and assert search_foods returns JSON text and get_food returns JSON text.

**Step 2: Run test to verify it fails**

Run: `cd python && .venv/bin/pytest tests/test_server_tools.py -v`
Expected: FAIL.

**Step 3: Implement**

- `search_foods(searchExpression: str, pageNumber?: int, maxResults?: int)`: require credentials; call API with method `foods.search`, params search_expression, page_number (default 0), max_results (default 20); return content as JSON string.
- `get_food(foodId: str)`: require credentials; call API `food.get` with food_id; return content as JSON string.

**Step 4: Run test to verify it passes**

Run: `cd python && .venv/bin/pytest tests/test_server_tools.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add python/src/fatsecret_mcp/server.py python/tests/test_server_tools.py
git commit -m "feat(python): add search_foods and get_food tools"
```

---

## Task 8: Recipe tools — search_recipes, get_recipe

**Files:**
- Modify: `python/src/fatsecret_mcp/server.py`
- Modify: `python/tests/test_server_tools.py`

**Step 1: Write the failing test**

- Assert `search_recipes` and `get_recipe` are registered (and optionally mock API for response shape).

**Step 2: Run test to verify it fails**

Run: `cd python && .venv/bin/pytest tests/test_server_tools.py -v`
Expected: FAIL.

**Step 3: Implement**

- `search_recipes(searchExpression, pageNumber?, maxResults?)`: API method `recipes.search`; same param pattern as foods.
- `get_recipe(recipeId: str)`: API method `recipe.get` with recipe_id.

**Step 4: Run test to verify it passes**

Run: `cd python && .venv/bin/pytest tests/test_server_tools.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add python/src/fatsecret_mcp/server.py python/tests/test_server_tools.py
git commit -m "feat(python): add search_recipes and get_recipe tools"
```

---

## Task 9: User profile and food diary — get_user_profile, get_user_food_entries, add_food_entry

**Files:**
- Modify: `python/src/fatsecret_mcp/server.py`
- Modify: `python/tests/test_server_tools.py`

**Step 1: Write the failing test**

- Assert tools `get_user_profile`, `get_user_food_entries`, `add_food_entry` are registered.

**Step 2: Run test to verify it fails**

Run: `cd python && .venv/bin/pytest tests/test_server_tools.py -v`
Expected: FAIL.

**Step 3: Implement**

- `get_user_profile()`: require access token; API `profile.get`; return JSON text.
- `get_user_food_entries(date?: str)`: require access token; convert date with date_to_fatsecret_format; API `food_entries.get` with date; return JSON text.
- `add_food_entry(foodId, servingId, quantity, mealType, date?)`: require access token; API POST `food_entry.create` with food_id, serving_id, quantity, meal (mealType), date (converted); return success text + JSON.

**Step 4: Run test to verify it passes**

Run: `cd python && .venv/bin/pytest tests/test_server_tools.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add python/src/fatsecret_mcp/server.py python/tests/test_server_tools.py
git commit -m "feat(python): add get_user_profile, get_user_food_entries, add_food_entry"
```

---

## Task 10: Weight tool — get_weight_month

**Files:**
- Modify: `python/src/fatsecret_mcp/server.py`
- Modify: `python/tests/test_server_tools.py`

**Step 1: Write the failing test**

- Assert `get_weight_month` is registered.

**Step 2: Run test to verify it fails**

Run: `cd python && .venv/bin/pytest tests/test_server_tools.py -v`
Expected: FAIL.

**Step 3: Implement**

- `get_weight_month(date?: str)`: require access token; date to FatSecret format; API `weights.get_month` with date; return JSON text.

**Step 4: Run test to verify it passes**

Run: `cd python && .venv/bin/pytest tests/test_server_tools.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add python/src/fatsecret_mcp/server.py python/tests/test_server_tools.py
git commit -m "feat(python): add get_weight_month tool"
```

---

## Task 11: Error handling and validation

**Files:**
- Modify: `python/src/fatsecret_mcp/server.py` (and optionally `api.py` / `config.py`)
- Modify: `python/tests/test_server_tools.py`

**Step 1: Write the failing test**

- Call search_foods without credentials set; expect clear error (no crash). Call get_user_profile without completing OAuth; expect "User authentication required" style message.

**Step 2: Run test to verify it fails**

Run: `cd python && .venv/bin/pytest tests/test_server_tools.py -v`
Expected: FAIL or existing tests fail if errors are not yet returned as MCP tool errors.

**Step 3: Implement**

- For tools that need credentials: if client_id/client_secret missing, return/raise tool error: "Please set your FatSecret API credentials first using set_credentials".
- For user tools: if access_token/access_token_secret missing, return/raise: "User authentication required. Please complete the OAuth flow first."
- On API/network errors, surface message in tool result (or raise) so client sees actionable text.

**Step 4: Run test to verify it passes**

Run: `cd python && .venv/bin/pytest tests/test_server_tools.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add python/src/fatsecret_mcp/server.py python/tests/test_server_tools.py
git commit -m "fix(python): consistent error messages for missing credentials and auth"
```

---

## Task 12: README and runnable entrypoint

**Files:**
- Modify: `python/README.md`
- Modify: `python/pyproject.toml` (optional script entry point)

**Step 1: Document run command**

- In `python/README.md`: add section "Running the MCP server" with:
  - `python -m fatsecret_mcp.server` or `uv run fatsecret run` (if using FastMCP CLI), or the one-liner that starts the server (e.g. `python -c "from fatsecret_mcp.server import create_server; create_server().run()"`).
- Add note that credentials can be set via `set_credentials` tool or env vars `CLIENT_ID` / `CLIENT_SECRET` (load from env in config when file is empty, to match JS).

**Step 2: Optional entry point**

- In `pyproject.toml` under `[project.scripts]`: e.g. `fatsecret-mcp = "fatsecret_mcp.server:main"` if you add a `def main(): create_server().run()` and call it when `__name__ == "__main__"`, so users can run `fatsecret-mcp` after install.

**Step 3: Commit**

```bash
git add python/README.md python/pyproject.toml
git commit -m "docs(python): README run instructions and optional entrypoint"
```

---

## Task 13: Full integration smoke test

**Files:**
- Create or extend: `python/tests/test_integration_smoke.py`

**Step 1: Write the failing test**

- Start server in-process or subprocess; send MCP initialize + tools/list (or equivalent); assert response includes all 12 tool names. Prefer in-process if FastMCP supports it, else subprocess with timeout.

**Step 2: Run test to verify it fails or passes**

Run: `cd python && .venv/bin/pytest tests/test_integration_smoke.py -v`
Expected: PASS after implementation.

**Step 3: Commit**

```bash
git add python/tests/test_integration_smoke.py
git commit -m "test(python): integration smoke test for all 12 tools"
```

---

## Summary

| Task | Description |
|------|-------------|
| 1 | Config load/save and path |
| 2 | Date conversion (days since epoch) |
| 3 | OAuth 1.0a signing helpers |
| 4 | FatSecret API client (HTTP + signing) |
| 5 | set_credentials + check_auth_status |
| 6 | start_oauth_flow + complete_oauth_flow |
| 7 | search_foods + get_food |
| 8 | search_recipes + get_recipe |
| 9 | get_user_profile + get_user_food_entries + add_food_entry |
| 10 | get_weight_month |
| 11 | Error handling and validation |
| 12 | README and entrypoint |
| 13 | Integration smoke test |

After execution, run the Python MCP server locally and verify with MCP Inspector or Cursor that all tools appear and that set_credentials → start_oauth_flow → complete_oauth_flow → user tools work against the real FatSecret API (with test credentials).
