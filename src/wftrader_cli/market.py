import requests
from datetime import datetime, UTC

def getTopOrdersData(item: str) -> tuple:
    url = f"https://api.warframe.market/v2/orders/item/{item}/top"

    response = requests.get(url)
    timestamp = datetime.now(UTC).isoformat(timespec="minutes")

    if response.status_code != 200:
        return None
    else:
        data = response.json()
        try:
            price = data["data"]["sell"][0]["platinum"]
        except IndexError: 
            return None # return None if there is no sell order
        return item, price, timestamp

def slugCheck(item: str) -> bool:
    url = f"https://api.warframe.market/v2/item/{item}"

    response = requests.get(url)
    data = response.json()

    if (data["error"] is None):
        return True

    return False

if __name__ == "__main__":
    falseresponse = requests.get("https://api.warframe.market/v2/item/sluuhhh")
    trueresponse = requests.get("https://api.warframe.market/v2/item/shred")

    print(trueresponse.json())
    print(falseresponse.json())