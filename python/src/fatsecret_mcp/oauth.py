"""OAuth 1.0a signing helpers for FatSecret (RFC 5849)."""

import base64
import hmac
import hashlib
from urllib.parse import quote


def percent_encode(s: str) -> str:
    """Encode per OAuth 1.0a: safe='' so !'()* and space are encoded."""
    return quote(s, safe="")


def create_signature_base_string(
    method: str, url: str, parameters: dict[str, str]
) -> str:
    """Build signature base string: METHOD&encoded(url)&encoded(sorted_params)."""
    sorted_params = "&".join(
        f"{percent_encode(k)}={percent_encode(parameters[k])}"
        for k in sorted(parameters)
    )
    return "&".join([
        method.upper(),
        percent_encode(url),
        percent_encode(sorted_params),
    ])


def generate_signature(
    method: str,
    url: str,
    parameters: dict[str, str],
    client_secret: str,
    token_secret: str = "",
) -> str:
    """HMAC-SHA1 signature; signing key = encoded(client_secret)&encoded(token_secret)."""
    base_string = create_signature_base_string(method, url, parameters)
    signing_key = f"{percent_encode(client_secret)}&{percent_encode(token_secret)}"
    raw = hmac.new(
        signing_key.encode("utf-8"),
        base_string.encode("utf-8"),
        hashlib.sha1,
    ).digest()
    return base64.b64encode(raw).decode("ascii")
