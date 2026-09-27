from sqlalchemy.orm import Session
from typing import Optional
from app.models.book import Book


def get_books(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
):
    query = db.query(Book)

    if category:
        query = query.filter(Book.category.ilike(category))
    if min_price is not None:
        query = query.filter(Book.price >= min_price)
    if max_price is not None:
        query = query.filter(Book.price <= max_price)

    total = query.count()
    books = query.offset(skip).limit(limit).all()
    return books, total


def get_book_by_id(db: Session, book_id: int):
    return db.query(Book).filter(Book.id == book_id).first()