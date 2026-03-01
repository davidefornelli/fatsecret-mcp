"""Date conversion for FatSecret API: YYYY-MM-DD to days since 1970-01-01."""

from datetime import date, datetime


def date_to_fatsecret_format(date_string: str | None) -> str:
    """Convert date to FatSecret format: days since epoch (1970-01-01). None/empty uses today."""
    if date_string:
        d = datetime.strptime(date_string.strip()[:10], "%Y-%m-%d").date()
    else:
        d = date.today()
    epoch = date(1970, 1, 1)
    days = (d - epoch).days
    return str(days)
