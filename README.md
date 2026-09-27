# Book Price Tracker API

A backend service that scrapes book data from books.toscrape.com and exposes it through a REST API built with FastAPI and PostgreSQL.

## Tech Stack

- Python 3.11
- FastAPI
- PostgreSQL
- SQLAlchemy
- BeautifulSoup4 (web scraping)
- Docker & Docker Compose

## Project Structure

book-price-tracker/
├── app/
│   ├── database/       # DB connection setup
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── crud/             # Database query functions
│   ├── scraper/         # Web scraping logic
│   ├── routes/           # API route definitions
│   └── main.py           # FastAPI app entry point
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
└── README.md

## Setup & Run

### Prerequisites
- Docker & Docker Compose installed

### Steps

1. Clone the repository

   git clone https://github.com/ahmed-nawaz1/book-price-tracker-api.git
   cd book-price-tracker

2. Run the project with Docker Compose (this starts both the FastAPI app and PostgreSQL database together)

   docker compose up --build

3. The API will be available at:

   http://localhost:8000

4. Interactive API documentation (Swagger UI):

   http://localhost:8000/docs

## Running the Scraper

The scraper collects title, price, rating, availability, and category for each book from books.toscrape.com, and automatically skips duplicate entries on repeated runs.

Trigger it via the API:

POST /scrape

Optional: limit the number of books scraped (useful for testing):

POST /scrape?limit=20

Response example:

{
  "total_found": 20,
  "added": 20,
  "skipped": 0,
  "failed": 0
}

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Health check |
| GET | /books | List all books (paginated) |
| GET | /books?skip=0&limit=10 | Pagination |
| GET | /books?category=Poetry | Filter books by category |
| GET | /books?min_price=10&max_price=50 | Filter books by price range |
| GET | /books/{id} | Get details of a single book |
| POST | /scrape | Trigger scraper to fetch and store new books |

### Example Requests

GET  http://localhost:8000/books?limit=5&category=Poetry
GET  http://localhost:8000/books/1
GET  http://localhost:8000/books?min_price=10&max_price=25
POST http://localhost:8000/scrape?limit=20

## Database Schema

Table: books

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| title | String | Book title |
| price | Float | Book price |
| rating | Integer | Rating (1-5) |
| category | String | Book category |
| availability | String | Stock availability text |
| scraped_at | DateTime | Timestamp when scraped |

A unique constraint on (title, category) prevents duplicate entries when the scraper is run multiple times.

## Environment Variables

| Variable | Description |
|----------|-------------|
| DATABASE_URL | PostgreSQL connection string |

These are configured automatically in docker-compose.yml for the Dockerized setup.

## Notes

- Duplicate prevention is handled both at the application level (existence check) and database level (unique constraint).
- Errors during scraping (missing fields, failed page loads) are handled gracefully and reported in the /scrape response summary.