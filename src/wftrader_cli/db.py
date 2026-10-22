import sqlite3
import logging
from contextlib import contextmanager, closing

from wftrader_cli.exceptions import *

DB_PATH = "data/app.db"


@contextmanager
def _connect():
    with closing(sqlite3.connect(DB_PATH)) as con, con:
        yield con

logger = logging.getLogger(__name__)

def init():
    with _connect() as con:
        con.execute('''CREATE TABLE IF NOT EXISTS history(
                            slug TEXT,
                            price INTEGER,
                            date TIMESTAMP)''')

        con.execute('''CREATE TABLE IF NOT EXISTS watchlist(
                            slug TEXT PRIMARY KEY)''')


def insertItemData(data):
    query = '''INSERT INTO history VALUES (?, ?, ?)'''

    with _connect() as con:
        if (isinstance(data, list)):
            con.executemany(query, data)
        else:
            con.execute(query, data)


def pullHistoryData(item: str) -> list:
    with _connect() as con:
        res = con.execute("SELECT * FROM history WHERE slug = ?", (item,)).fetchall()

    res = [{"item_name" : slug, "price" : price, "date" : date} for slug, price, date in res]
    return res


def insertIntoWatchlist(item: str):
    with _connect() as con:
        con.execute('''INSERT OR IGNORE INTO watchlist VALUES (?)''', (item,))


def deleteFromWatchlist(item: str):
    with _connect() as con:
        cur = con.execute('''DELETE FROM watchlist WHERE slug = ?''', (item,))
        if cur.rowcount == 0:
            raise NotInWatchlistException(f'Item "{item}" could not be deleted from Watchlist')
        

def fetchWatchlist():
    with _connect() as con:
        res = con.execute('''SELECT * FROM watchlist''').fetchall()

    res = [slug for (slug,) in res]
    return res

