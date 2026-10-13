import sqlite3

def init():
    con = sqlite3.connect("data/app.db")
    cur = con.cursor()
    
    cur.execute('''CREATE TABLE IF NOT EXISTS history(
                        slug TEXT,
                        price INTEGER,
                        date TIMESTAMP)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS watchlist(
                        slug TEXT PRIMARY KEY)''')

    
    con.commit()
    con.close()

def insertItemData(data):
    con = sqlite3.connect("data/app.db")
    cur = con.cursor()

    query = '''INSERT INTO history VALUES (?, ?, ?)'''

    if (isinstance(data, list)):
        cur.executemany(query, data)
    else:
        cur.execute(query, data)

    con.commit()
    con.close()

def pullHistoryData(item: str) -> list:
    con = sqlite3.connect("data/app.db")
    cur = con.cursor()

    res = cur.execute("SELECT * FROM history WHERE slug = ?", (item,)).fetchall()
    con.close()

    res = [{"item_name" : slug, "price" : price, "date" : date} for slug, price, date in res]

    return res

def insertIntoWatchlist(item: str):
    con = sqlite3.connect("data/app.db")
    cur = con.cursor()

    cur.execute('''INSERT OR IGNORE INTO watchlist VALUES (?)''', (item,))

    con.commit()
    con.close()

def deleteFromWatchlist(item: str):
    con = sqlite3.connect("data/app.db")
    cur = con.cursor()

    cur.execute('''DELETE FROM watchlist WHERE slug = ?''', (item,))

    rowcount = cur.rowcount

    con.commit()
    con.close()

    return rowcount

def fetchWatchlist():
    con = sqlite3.connect("data/app.db")
    cur = con.cursor()

    res = cur.execute('''SELECT * FROM watchlist''').fetchall()
    res = [slug for (slug,) in res]

    con.close()
    return res


