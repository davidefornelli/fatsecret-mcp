from fatsecret_mcp.oauth import (
    create_signature_base_string,
    generate_signature,
    percent_encode,
)


def test_percent_encode_special_chars():
    # RFC 5849: !'()* are reserved and must be encoded
    assert percent_encode("a!b") == "a%21b"
    assert "%2A" in percent_encode("*")


def test_signature_base_string_order():
    base = create_signature_base_string(
        "GET", "https://example.com", {"b": "2", "a": "1"}
    )
    assert base.startswith("GET&")
    assert "a%3D1" in base
    assert "b%3D2" in base


def test_generate_signature_deterministic():
    sig = generate_signature(
        "GET", "https://example.com", {"c": "3"}, "client_secret", ""
    )
    assert isinstance(sig, str)
    assert len(sig) > 0
    sig2 = generate_signature(
        "GET", "https://example.com", {"c": "3"}, "client_secret", ""
    )
    assert sig == sig2
