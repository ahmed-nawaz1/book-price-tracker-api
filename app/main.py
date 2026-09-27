from fastapi import FastAPI
from app.database.connection import Base, engine
from app.routes.books import router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Book Price Tracker API")

app.include_router(router)


@app.get("/")
def root():
    return {"message": "Book Price Tracker API is running"}