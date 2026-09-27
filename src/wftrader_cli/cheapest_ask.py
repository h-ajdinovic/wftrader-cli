import requests
import sqlite3
import datetime

def save_price(item: str, price: int):
    con = sqlite3.connect("data/cheapest.db")
    cur = con.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS cheapest(
                name TEXT,
                price INTEGER,
                date TIMESTAMP)''')

    col = (item, price, datetime.datetime.now().isoformat())
    cur.execute("INSERT INTO cheapest VALUES(?, ?, ?)", col)
    con.commit()

    print(cur.execute("SELECT * FROM cheapest").fetchall())
    con.close()

def cheapestPrice(item: str) -> str:
    url = f"https://api.warframe.market/v2/orders/item/{item}/top"
    
    response = requests.get(url)
    
    if response.status_code != 200:
        return "Item not found!"
    else:
        data = response.json()
        save_price(item, data["data"]["sell"][0]["platinum"])
        return f"Lowest Ask: {data["data"]["sell"][0]["platinum"]}"

def main() -> None:
    itemName = input("Item Name: ").lower().strip().replace(" ", "_")
    
    print(cheapestPrice(itemName))

if __name__ == "__main__":
    main()

