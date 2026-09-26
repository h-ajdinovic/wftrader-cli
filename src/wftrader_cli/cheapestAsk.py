import requests

def main() -> None:
    itemName = input("Item Name: ").lower().strip().replace(" ", "_")
    
    url = f"https://api.warframe.market/v2/orders/item/{itemName}/top"

    response = requests.get(url)

    if response.status_code != 200:
        print("Item not found!")
    else:
        data = response.json()
        print("Lowest Ask:", data["data"]["sell"][0]["platinum"])

main()
