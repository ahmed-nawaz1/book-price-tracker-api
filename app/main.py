import time

from fastapi import FastAPI
from sqlalchemy.exc import OperationalError

from app.database.connection import Base, engine
from app.routes.books import router


def init_db(retries=15, delay=2):
    for i in range(retries):
        try:
            Base.metadata.create_all(bind=engine)
            return
        except OperationalError:
            print(f"Waiting for database... ({i + 1}/{retries})")
            time.sleep(delay)
    raise RuntimeError("Database not reachable")


init_db()

app = FastAPI(title="Book Price Tracker API")

app.include_router(router)


@app.get("/")
def root():
    return {"message": "Book Price Tracker API is running"}