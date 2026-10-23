import logging
from datetime import UTC, datetime

import requests

from wftrader_cli.exceptions import (
    ItemNotFoundError,
    MarketUnavailableError,
    NoSellOrdersFoundError,
)

logger = logging.getLogger(__name__)

def fetch_top_order(slug: str) -> tuple:
    url = f"https://api.warframe.market/v2/orders/item/{slug}/top"

    try:
        response = requests.get(url, timeout=1)
        timestamp = datetime.now(UTC).isoformat(timespec="minutes")
    except requests.exceptions.RequestException as e:
        raise MarketUnavailableError(f"Request failed: {e}") from e

    code = response.status_code
    if code == 404:
        raise ItemNotFoundError(f'Item "{slug}" has no orders or does not exist!')
    elif code in (429, 509) or code >= 500:
        raise MarketUnavailableError(f"Server Error: status {code}")

    order = response.json()
    try:
        price = order["data"]["sell"][0]["platinum"]
    except IndexError:
        raise NoSellOrdersFoundError(f'No sell orders were found for "{slug}"')
    return (slug, price, timestamp)

def check_slug(slug: str) -> bool:
    url = f"https://api.warframe.market/v2/item/{slug}"

    try:
        response = requests.get(url, timeout=1)
    except requests.exceptions.RequestException as exc:
        raise MarketUnavailableError(f"Request failed: {exc}") from exc
    code = response.status_code

    if code in (429, 509) or code >= 500:
        raise MarketUnavailableError(f"Server Error: status {code}")
    elif code == 404:
        raise ItemNotFoundError(f"Item {slug} does not exist!")

    return True