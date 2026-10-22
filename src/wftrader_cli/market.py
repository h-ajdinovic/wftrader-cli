import requests
import logging
from datetime import datetime, UTC

from wftrader_cli.exceptions import *


logger = logging.getLogger(__name__)

def getTopOrderData(item: str) -> tuple:
    url = f"https://api.warframe.market/v2/orders/item/{item}/top"

    try:
        response = requests.get(url, timeout=1)
        timestamp = datetime.now(UTC).isoformat(timespec="minutes")
    except requests.exceptions.RequestException as e:
        raise MarketUnavailableException(f"Request failed: {e}") from e

    code = response.status_code
    if code == 404:
        raise ItemNotFoundException(f'Item "{item}" has no orders or does not exist!')
    elif code in (429, 509) or code >= 500:
        raise MarketUnavailableException(f"Server Error: status {code}")

    data = response.json()
    try:
        price = data["data"]["sell"][0]["platinum"]
    except IndexError:
        raise NoSellOrdersFoundException(f'No sell orders were found for "{item}"')
    return item, price, timestamp

def slugCheck(item: str) -> bool:
    url = f"https://api.warframe.market/v2/item/{item}"

    try:
        response = requests.get(url, timeout=1)
    except requests.exceptions.RequestException as e:
        raise MarketUnavailableException(f"Request failed: {e}") from e
    code = response.status_code

    if code in (429, 509) or code >= 500:
        raise MarketUnavailableException(f"Server Error: status {code}")
    elif code == 404:
        raise ItemNotFoundException(f"Item {item} does not exist!")

    return True

    
if __name__ == "__main__":
    falseresponse = requests.get("https://api.warframe.market/v2/item/sluuhhh")
    trueresponse = requests.get("https://api.warframe.market/v2/item/shred")

    print(trueresponse.status_code)
    #print(trueresponse.json())
    print(falseresponse.status_code)
    #print(falseresponse.json())