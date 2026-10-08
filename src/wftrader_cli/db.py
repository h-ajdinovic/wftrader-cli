import sqlite3

def init():
    con = sqlite3.connect("data/cheapest.db")
    cur = con.cursor()
    
    cur.execute('''CREATE TABLE IF NOT EXISTS cheapest(
                        name TEXT,
                        price INTEGER,
                        date TIMESTAMP)''')

    con.close()

def insertItemData(item: str, price: int, timestamp: str):
    '''
    Takes item name, price and the timestamp of the sell order and 
    inserts it into a table
    '''
    con = sqlite3.connect("data/cheapest.db")
    cur = con.cursor()

    column = (item, price, timestamp)
    cur.execute("INSERT INTO cheapest VALUES(?, ?, ?)", column)
    con.commit()
    
    con.close()

def pullHistoryData(item: str) -> list:
    con = sqlite3.connect("data/cheapest.db")
    cur = con.cursor()

    res = cur.execute("SELECT * FROM cheapest WHERE name = ?", (item,)).fetchall()
    con.close()

    res = [{"item_name" : name, "price" : price, "date" : date} for name, price, date in res]

    return res

