import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from wftrader_cli import db, market
from wftrader_cli.exceptions import (
    ItemNotFoundError,
    MarketUnavailableError,
    NoSellOrdersFoundError,
    NotInWatchlistError,
)

CURRENT_DIR = Path(__file__).resolve().parent

STATIC_DIR = CURRENT_DIR / "static"
INDEX_FILE = STATIC_DIR / "index.html"

class WatchlistRequest(BaseModel):
    slug: str

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s")

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init()
    tracker = BackgroundScheduler()
    tracker.add_job(track_watchlist, "cron", minute="*/10")
    tracker.start()
    yield
    tracker.shutdown()

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.exception_handler(MarketUnavailableError)
def exc_market_unavailable(request: Request, exc: MarketUnavailableError) -> JSONResponse:
    logger.warning("MarketUnavailableError (Code 504) for %s with message: %s", str(request.url) + request.url.path, str(exc))
    return JSONResponse(status_code=504, content={"detail": "warframe.market is unavailable, try again later!"})

@app.exception_handler(ItemNotFoundError)
def exc_item_not_found(request: Request, exc: ItemNotFoundError) -> JSONResponse:
    logger.warning("ItemNotFoundError (Code 404) for %s with message: %s", str(request.url) + request.url.path, str(exc))
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(NotInWatchlistError)
def exc_not_in_watchlist(request: Request, exc: NotInWatchlistError) -> JSONResponse:
    logger.warning("NotInWatchlistError (Code 404) for %s with message: %s", str(request.url) + request.url.path, str(exc))
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(NoSellOrdersFoundError)
def exc_no_sell_orders(request: Request, exc: NoSellOrdersFoundError) -> JSONResponse:
    logger.warning("NoSellOrdersFoundError (Code 404) for %s with message: %s", str(request.url) + request.url.path, str(exc))
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
  return FileResponse(STATIC_DIR / "favicon.ico")

@app.get("/", response_class=FileResponse)
def show_main_page() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/watchlist/")
def get_watchlist() -> dict[str, Any]:
    return db.get_watchlist()

@app.post("/watchlist/", response_model=WatchlistRequest)
def add_to_watchlist(model: WatchlistRequest) -> WatchlistRequest:
    slug = model.slug
    market.check_slug(slug)

    db.add_watchlist_item(slug)
    return model

@app.delete("/watchlist/{slug}", response_class=PlainTextResponse)
def delete_from_watchlist(slug: str) -> str:
    db.remove_watchlist_item(slug)
    return slug

@app.get("/price/{slug}", response_class=PlainTextResponse)
def get_price(slug: str) -> str:
    return get_cheapest_price(slug)

@app.get("/history/{slug}", response_class=PlainTextResponse)
def get_price_history(slug: str) -> str: 
    return db.get_history(slug)

def get_cheapest_price(slug: str) -> dict[str, Any]:
    (slug, price, timestamp) = market.fetch_top_order(slug)
    db.save_price((slug, price, timestamp))
    return {"slug" : slug, "price" : price, "date" : timestamp}

def track_watchlist():
    start = time.time()
    watchlist = db.get_watchlist()
    failed = 0

    for slug in watchlist:
        try:
            data = market.fetch_top_order(slug)
            db.save_price(data)
        except MarketUnavailableError as e:
            failed += 1
            logger.warning("market unavailable for %s: %s", slug, e)
        except Exception:
            logger.exception("Unexpected error while tracking %s", slug)
        time.sleep(0.4)

    end = time.time()

    logger.info("watchlist run done in %d seconds: %d items, %d failed", end-start, len(watchlist), failed)
    
    

def main() -> None:
    uvicorn.run("wftrader_cli.api:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()

