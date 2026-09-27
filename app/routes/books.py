from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database.connection import get_db, engine, Base
from app.schemas.book import BookResponse, ScrapeResponse
from app.crud.book import get_books, get_book_by_id
from app.scraper.books_scraper import run_scraper

router = APIRouter()


@router.get("/books", response_model=list[BookResponse])
def list_books(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db),
):
    books, total = get_books(db, skip, limit, category, min_price, max_price)
    return books


@router.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/scrape", response_model=ScrapeResponse)
def trigger_scrape(limit: Optional[int] = None, db: Session = Depends(get_db)):
    result = run_scraper(db, limit=limit)
    return result