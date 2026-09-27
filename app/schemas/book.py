from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class BookBase(BaseModel):
    title: str
    price: float
    rating: Optional[int] = None
    category: Optional[str] = None
    availability: Optional[str] = None


class BookResponse(BookBase):
    id: int
    scraped_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ScrapeResponse(BaseModel):
    total_found: int
    added: int
    skipped: int
    failed: int