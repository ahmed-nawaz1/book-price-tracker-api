import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.book import Book

BASE_URL = "https://books.toscrape.com/"

RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def get_all_book_links():
    """Iterate through all catalogue pages and collect links to all books."""
    links = []
    page_url = BASE_URL + "catalogue/page-1.html"

    while page_url:
        try:
            resp = requests.get(page_url, timeout=10)
            if resp.status_code != 200:
                break
        except requests.RequestException as e:
            print(f"Page load error: {e}")
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        books = soup.select("article.product_pod h3 a")

        for b in books:
            href = b["href"].replace("../../../", "")
            links.append(BASE_URL + "catalogue/" + href)

        next_btn = soup.select_one("li.next a")

        if next_btn:
            next_href = next_btn["href"]
            page_url = (
                BASE_URL
                + "catalogue/"
                + next_href.replace("../../../", "").replace("catalogue/", "")
            )
        else:
            page_url = None

    return links


def scrape_book_detail(url: str):
    """Extract book details from a single book detail page."""
    try:
        resp = requests.get(url, timeout=10)

        if resp.status_code != 200:
            return None

    except requests.RequestException as e:
        print(f"Detail page error: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    try:
        title = soup.select_one("div.product_main h1").text.strip()

        price_text = soup.select_one("p.price_color").text.strip()
        price = float(price_text.replace("£", "").replace("Â", ""))

        rating_class = soup.select_one("p.star-rating")["class"]
        rating_word = [c for c in rating_class if c != "star-rating"][0]
        rating = RATING_MAP.get(rating_word, None)

        availability = soup.select_one("p.availability").text.strip()

        breadcrumb = soup.select("ul.breadcrumb li a")
        category = breadcrumb[-1].text.strip() if len(breadcrumb) >= 2 else "Unknown"

        return {
            "title": title,
            "price": price,
            "rating": rating,
            "availability": availability,
            "category": category,
        }

    except Exception as e:
        print(f"Parsing error for {url}: {e}")
        return None


def run_scraper(db: Session, limit: int = None):
    """Sab books scrape karke DB mein save karta hai (duplicates skip karke)."""
    print("🔍 Fetching book links...")
    links = get_all_book_links()
    print(f"✅ Found {len(links)} total book links")

    if limit:
        links = links[:limit]
        print(f"⚡ Limiting to {limit} books for this run")

    added, skipped, failed = 0, 0, 0

    for i, link in enumerate(links, start=1):
        print(f"[{i}/{len(links)}] Scraping: {link}")
        data = scrape_book_detail(link)
        if not data:
            print(f"   ❌ Failed to scrape this book")
            failed += 1
            continue

        exists = db.query(Book).filter(
            Book.title == data["title"],
            Book.category == data["category"]
        ).first()

        if exists:
            print(f"   ⏭️  Skipped (already exists): {data['title']}")
            skipped += 1
            continue

        book = Book(**data)
        db.add(book)
        try:
            db.commit()
            print(f"   ✅ Added: {data['title']} - £{data['price']}")
            added += 1
        except IntegrityError:
            db.rollback()
            print(f"   ⏭️  Skipped (duplicate): {data['title']}")
            skipped += 1

    print(f"\n🎉 Done! Total: {len(links)}, Added: {added}, Skipped: {skipped}, Failed: {failed}")
    return {"total_found": len(links), "added": added, "skipped": skipped, "failed": failed}