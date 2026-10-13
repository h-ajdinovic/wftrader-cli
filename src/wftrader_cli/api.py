from contextlib import asynccontextmanager
from datetime import datetime, UTC
from time import sleep

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler

import wftrader_cli.db as db
import wftrader_cli.market as market

class Slug(BaseModel):
    slug: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init()
    tracker = BackgroundScheduler()
    tracker.add_job(watchlistLoop, "cron", minute="*/10")
    tracker.start()
    yield
    tracker.shutdown()

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="src/wftrader_cli/static"), name="static")

@app.get("/", response_class=FileResponse)
def readMainPage():
    return "src/wftrader_cli/static/index.html"

@app.post("/addWL/")
def postWatchlist(item: Slug):
    if (not market.slugCheck(item.slug)):
        raise HTTPException(status_code=404)
    db.insertIntoWatchlist(item.slug)
    return item

@app.delete("/deleteWL/")
def deleteWatchlist(item: Slug):
    if (db.deleteFromWatchlist(item.slug) == 0):
        raise HTTPException(status_code=400)
    return item

@app.get("/price/{item}")
def readItem(item):
    return cheapestPrice(item)

@app.get("/history/{item}")
def readItemHistory(item):
    return db.pullHistoryData(item)

def cheapestPrice(item: str) -> str:
    data = market.getTopOrdersData(item)

    if data is None:
        raise HTTPException(status_code = 404)
    else:
        db.insertItemData(data)
        return {"item_name" : data[0], "price" : data[1], "date" : data[2]}

def watchlistLoop():
    watchlist = db.fetchWatchlist()
    res = []

    for slug in watchlist:
        res.append(market.getTopOrdersData(slug))
        sleep(0.4)

    for data in res:
        if data is not None:
            db.insertItemData(data)
    

def main() -> None:
    uvicorn.run("wftrader_cli.api:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()

