import requests
import sqlite3
import datetime
import uvicorn
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/price/{item}")
def readItem(item):
    return cheapestPrice(item)

@app.get("/history/{item}")
def readItem(item):
    return history(item)

def save_price(item: str, price: int):
    con = sqlite3.connect("data/cheapest.db")
    cur = con.cursor()

    current_time = datetime.datetime.now().isoformat()

    cur.execute('''CREATE TABLE IF NOT EXISTS cheapest(
                name TEXT,
                price INTEGER,
                date TIMESTAMP)''')

    col = (item, price, current_time)
    cur.execute("INSERT INTO cheapest VALUES(?, ?, ?)", col)
    con.commit()

    print(cur.execute("SELECT * FROM cheapest").fetchall())
    con.close()

    return current_time

def history(item):
    con = sqlite3.connect("data/cheapest.db")
    cur = con.cursor()

    res = cur.execute("SELECT * FROM cheapest WHERE name = ?", (item,)).fetchall()
    con.close()

    return [
        {"item name" : name, "price" : price, "date" : date} 
        for name, price, date in res
    ]

def cheapestPrice(item: str) -> str:
    url = f"https://api.warframe.market/v2/orders/item/{item}/top"
    
    response = requests.get(url)
    
    if response.status_code != 200:
        raise HTTPException(status_code = response.status_code)
    else:
        data = response.json()
        price = data["data"]["sell"][0]["platinum"]
        timestamp = save_price(item, price)
        return {"item_name" : item, "price" : price, "date" : timestamp}

        # return f"Lowest Ask: {data["data"]["sell"][0]["platinum"]}"

def main() -> None:
    uvicorn.run("wftrader_cli.cheapest_ask:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()

