import requests
import datetime

def getTopOrdersData(item: str) -> tuple:
    url = f"https://api.warframe.market/v2/orders/item/{item}/top"

    response = requests.get(url)
    timestamp = datetime.now(timezone.utc).isoformat()

    if response.status_code != 200:
        return None
    else:
        data = response.json()
        price = data["data"]["sell"][0]["platinum"]
        return item, price, timestamp