from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import wftrader_cli.db as db
import wftrader_cli.market as market


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init()
    yield

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="src/wftrader_cli/static"), name="static")

@app.get("/", response_class=FileResponse)
def readMainPage():
    return "src/wftrader_cli/static/index.html"

@app.get("/price/{item}")
def readItem(item):
    return cheapestPrice(item)

@app.get("/history/{item}")
def readItemHistory(item):
    return db.history(item)

def cheapestPrice(item: str) -> str:
    data = market.getTopOrdersData(item)

    if data is None:
        raise HTTPException(status_code = 404)
    else:
        db.insertItemData(data)
        return {"item_name" : data[0], "price" : data[1], "date" : data[2]}

def main() -> None:
    uvicorn.run("wftrader_cli.cheapest_ask:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()

