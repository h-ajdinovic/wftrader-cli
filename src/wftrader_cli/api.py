from contextlib import asynccontextmanager
from datetime import datetime, UTC
import time
import logging

import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler

import wftrader_cli.db as db
import wftrader_cli.market as market
from wftrader_cli.exceptions import *

class Slug(BaseModel):
    slug: str

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s")

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init()
    tracker = BackgroundScheduler()
    tracker.add_job(watchlistLoop, "cron", minute="*/1")
    tracker.start()
    yield
    tracker.shutdown()

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="src/wftrader_cli/static"), name="static")

@app.exception_handler(MarketUnavailableException)
def exc_market_unavailable(_request: Request, exc: MarketUnavailableException):
    logger.warning("MarketUnavailableException (Code 504) for %s with message: %s", str(_request.url) + _request.url.path, str(exc))
    return JSONResponse(status_code=504, content={"detail": "warframe.market is unavailable, try again later!"})

@app.exception_handler(ItemNotFoundException)
def exc_item_not_found(_request: Request, exc: ItemNotFoundException):
    logger.warning("ItemNotFoundException (Code 404) for %s with message: %s", str(_request.url) + _request.url.path, str(exc))
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(NotInWatchlistException)
def exc_not_in_watchlist(_request: Request, exc: NotInWatchlistException):
    logger.warning("NotInWatchlistException (Code 404) for %s with message: %s", str(_request.url) + _request.url.path, str(exc))
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(NoSellOrdersFoundException)
def exc_no_sell_orders(_request: Request, exc: NoSellOrdersFoundException):
    logger.warning("NoSellOrdersFoundException (Code 404) for %s with message: %s", str(_request.url) + _request.url.path, str(exc))
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.get("/", response_class=FileResponse)
def readMainPage():
    return "src/wftrader_cli/static/index.html"

@app.get("/watchlist/")
def readWatchlist():
    return db.fetchWatchlist()

@app.post("/addWL/")
def postWatchlist(item: Slug):
    market.slugCheck(item.slug)

    db.insertIntoWatchlist(item.slug)
    return item

@app.delete("/deleteWL/")
def deleteWatchlist(item: Slug):
    db.deleteFromWatchlist(item.slug)
    return item

@app.get("/price/{item}")
def readItem(item):
    return cheapestPrice(item)

@app.get("/history/{item}")
def readItemHistory(item): 
    return db.pullHistoryData(item)

def cheapestPrice(item: str) -> str:
    data = market.getTopOrderData(item)
    db.insertItemData(data)
    return {"item_name" : data[0], "price" : data[1], "date" : data[2]}

def watchlistLoop():
    start = time.time()
    watchlist = db.fetchWatchlist()
    failed = 0

    for slug in watchlist:
        try:
            data = market.getTopOrderData(slug)
            db.insertItemData(data)
        except MarketUnavailableException as e:
            failed += 1
            logger.warning("market unavailable for %s: %s", slug, e)
        except Exception:
            logger.exception("Unexpected error while tracking %s", slug)
        time.sleep(0.4)

    end = time.time()

    logger.info("watchlist run done in %d seconds: %d items, %d failed", end-start, len(watchlist), failed, end-start)
    
    

def main() -> None:
    uvicorn.run("wftrader_cli.api:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()

