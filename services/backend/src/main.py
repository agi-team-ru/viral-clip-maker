import logging
import os
from fastapi import FastAPI

from .routers import main

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "WARNING").upper())

logger = logging.getLogger(__name__)


app = FastAPI()

app.include_router(main.router)

@app.get("/")
def read_root():
    return {"version": "1.0.0"}
