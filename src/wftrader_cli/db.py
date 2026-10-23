import logging
import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path
from typing import Any

from wftrader_cli.exceptions import *

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent

DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "app.db"


@contextmanager
def _connect():
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        yield conn

logger = logging.getLogger(__name__)

def init():
    with _connect() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS history(
                            slug TEXT,
                            price INTEGER,
                            date TIMESTAMP)''')

        conn.execute('''CREATE TABLE IF NOT EXISTS watchlist(
                            slug TEXT PRIMARY KEY)''')


def save_price(order):
    query = '''INSERT INTO history VALUES (?, ?, ?)'''

    with _connect() as conn:
        if isinstance(order, list):
            conn.executemany(query, order)
        else:
            conn.execute(query, order)


def get_history(slug: str) -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM history WHERE slug = ?", (slug,)).fetchall()

    rows = [{"slug" : slug, "price" : price, "date" : date} for slug, price, date in rows]
    return rows


def add_watchlist_item(slug: str):
    with _connect() as conn:
        conn.execute('''INSERT OR IGNORE INTO watchlist VALUES (?)''', (slug,))


def remove_watchlist_item(slug: str):
    with _connect() as conn:
        cursor = conn.execute('''DELETE FROM watchlist WHERE slug = ?''', (slug,))
        if cursor.rowcount == 0:
            raise NotInWatchlistError(f'Item "{slug}" could not be deleted from Watchlist')
        

def get_watchlist():
    with _connect() as conn:
        rows = conn.execute('''SELECT * FROM watchlist''').fetchall()

    rows = [slug for (slug,) in rows]
    return rows

