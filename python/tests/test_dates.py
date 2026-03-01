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
