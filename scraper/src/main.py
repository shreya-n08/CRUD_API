import re
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, ValidationError
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
from time import sleep, monotonic
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
CACHE_DIR = Path(__file__).resolve().parents[1] / "cache"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"

TIMEOUT_SECONDS = 10
REQUEST_DELAY_SECONDS = 0.5
MAX_CATALOGUE_PAGES = 3
RUN_STATS = {
    "pages_fetched": 0,
    "cache_hits": 0,
    "failed_pages": [],
}

HEADERS = {
    "User-Agent": (
        "FlyRankInternship-A9/1.0 "
        "(educational scraper; contact: "
        "https://github.com/shreya-n08/CRUD_API)"
    )
}



def fetch_page(url: str, cache_file: Path) -> str:
    """Fetch and cache a page, retrying timeouts and HTTP 5xx once."""
    if cache_file.exists():
        content = cache_file.read_bytes()
        RUN_STATS["cache_hits"] += 1
        print(f"CACHE HIT: {url}")
        print(f"Response size: {len(content)} bytes")
        return content.decode("utf-8")

    cache_file.parent.mkdir(parents=True, exist_ok=True)

    last_error = None

    for attempt in range(2):
        if getattr(fetch_page, "has_requested", False):
            sleep(REQUEST_DELAY_SECONDS)

        print(f"FETCH: {url} (attempt {attempt + 1}/2)")

        try:
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=TIMEOUT_SECONDS,
            )
            fetch_page.has_requested = True

            if response.status_code == 200:
                cache_file.write_bytes(response.content)
                RUN_STATS["pages_fetched"] += 1
                print(f"HTTP status: {response.status_code}")
                print(f"Cached HTML: {cache_file}")
                print(f"Response size: {len(response.content)} bytes")
                return response.content.decode("utf-8")

            error = requests.HTTPError(
                f"Expected HTTP 200 for {url}, got {response.status_code}",
                response=response,
            )

            if response.status_code < 500 or attempt == 1:
                raise error

            last_error = error
            print("Server error; waiting before one retry.")
            sleep(REQUEST_DELAY_SECONDS)

        except (requests.Timeout, requests.ConnectionError) as exc:
            last_error = exc

            if attempt == 1:
                raise

            print("Request failed; waiting before one retry.")
            sleep(REQUEST_DELAY_SECONDS)

    raise last_error


def discover_catalogue_pages() -> list[tuple[str, str]]:
    """Follow the Next link for at most three catalogue pages."""
    pages = []
    current_url = BASE_URL

    for page_number in range(1, MAX_CATALOGUE_PAGES + 1):
        cache_file = CACHE_DIR / f"catalogue-page-{page_number}.html"
        html = fetch_page(current_url, cache_file)
        pages.append((current_url, html))

        if page_number == MAX_CATALOGUE_PAGES:
            break

        soup = BeautifulSoup(html, "html.parser")
        next_link = soup.select_one("li.next a")

        if next_link is None or not next_link.get("href"):
            raise RuntimeError(
                f"Could not find the Next link on page {page_number}"
            )

        current_url = urljoin(current_url, next_link["href"])

    return pages


def discover_book_urls(
    catalogue_pages: list[tuple[str, str]],
) -> list[tuple[str, str]]:
    """Return unique product URLs with the catalogue page that listed them."""
    discovered = []
    seen_urls = set()

    for source_page, html in catalogue_pages:
        soup = BeautifulSoup(html, "html.parser")

        for link in soup.select("article.product_pod h3 a"):
            href = link.get("href")
            if not href:
                continue

            product_url = urljoin(source_page, href)

            if product_url not in seen_urls:
                seen_urls.add(product_url)
                discovered.append((product_url, source_page))

    return discovered


def extract_book(
    product_url: str,
    source_page: str,
    html: str,
) -> dict:
    """Extract the eight required raw fields from one book page."""
    soup = BeautifulSoup(html, "html.parser")

    title_element = soup.select_one("div.product_main h1")
    price_element = soup.select_one("p.price_color")
    availability_element = soup.select_one("p.instock.availability")
    rating_element = soup.select_one("p.star-rating")

    description_heading = soup.find(id="product_description")
    description_element = (
        description_heading.find_next("p")
        if description_heading
        else None
    )

    rating_classes = rating_element.get("class", []) if rating_element else []
    rating_text = (
        next((value for value in rating_classes if value != "star-rating"), None)
    )

    return {
        "title": (
            title_element.get_text(" ", strip=True)
            if title_element else None
        ),
        "product_url": product_url,
        "price_text": (
            price_element.get_text(" ", strip=True)
            if price_element else None
        ),
        "availability_text": (
            availability_element.get_text(" ", strip=True)
            if availability_element else None
        ),
        "rating_text": rating_text,
        "description": (
            description_element.get_text(" ", strip=True)
            if description_element else None
        ),
        "source_page": source_page,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


class BookRecord(BaseModel):
    """Validated, normalized book record."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)
    product_url: HttpUrl
    price_text: str = Field(min_length=1)
    price_gbp: float = Field(ge=0)
    availability_text: str = Field(min_length=1)
    rating_text: str = Field(min_length=1)
    description: str | None
    source_page: HttpUrl
    fetched_at: datetime


def normalize_price(price_text: str) -> float:
    """Convert a price such as £51.77 into a numeric GBP value."""
    match = re.search(r"\d+(?:\.\d{1,2})?", price_text.replace(",", ""))

    if not match:
        raise ValueError(f"Could not parse price: {price_text!r}")

    return float(match.group())


def validate_raw_books(raw_books: list[dict]) -> tuple[list[dict], list[dict]]:
    """Validate records, remove duplicate URLs, and collect errors."""
    valid_books = []
    errors = []
    seen_urls = set()

    for index, raw_book in enumerate(raw_books, start=1):
        try:
            normalized = {
                **raw_book,
                "price_gbp": normalize_price(raw_book["price_text"]),
            }
            book = BookRecord.model_validate(normalized)
            record = book.model_dump(mode="json")

            # Use a canonical URL string as the record identity.
            product_url = str(book.product_url)
            if product_url in seen_urls:
                errors.append({
                    "record_index": index,
                    "product_url": product_url,
                    "reason": "Duplicate product_url",
                })
                continue

            seen_urls.add(product_url)
            valid_books.append(record)

        except (ValidationError, ValueError, KeyError, TypeError) as exc:
            errors.append({
                "record_index": index,
                "product_url": raw_book.get("product_url"),
                "reason": str(exc),
            })

    return valid_books, errors


def save_validated_books(
    valid_books: list[dict],
    errors: list[dict],
) -> None:
    """Save validated records and validation errors as JSON."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    (OUTPUT_DIR / "books.json").write_text(
        json.dumps(valid_books, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (OUTPUT_DIR / "errors.json").write_text(
        json.dumps(errors, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> None:
    started_at = datetime.now(timezone.utc)
    start_clock = monotonic()

    # Reset counters so repeated runs in the same process are independent.
    RUN_STATS["pages_fetched"] = 0
    RUN_STATS["cache_hits"] = 0
    RUN_STATS["failed_pages"] = []
    fetch_page.has_requested = False

    catalogue_pages = discover_catalogue_pages()
    discovered_books = discover_book_urls(catalogue_pages)

    print(f"catalogue_pages={len(catalogue_pages)}")
    print(f"discovered={len(discovered_books)}")
    print(f"unique_urls={len({url for url, _ in discovered_books})}")

    raw_books = []

    for index, (product_url, source_page) in enumerate(
        discovered_books, start=1
    ):
        slug = product_url.rstrip("/").split("/")[-2]
        cache_file = CACHE_DIR / "details" / f"{slug}.html"

        try:
            html = fetch_page(product_url, cache_file)
            raw_book = extract_book(product_url, source_page, html)
            raw_books.append(raw_book)

            if index == 1:
                print("\nFirst complete raw record:")
                print(json.dumps(raw_book, indent=2, ensure_ascii=False))

        except (requests.RequestException, OSError, UnicodeError) as exc:
            failure = {
                "url": product_url,
                "source_page": source_page,
                "reason": str(exc),
            }
            RUN_STATS["failed_pages"].append(failure)
            print(f"FAILED; skipping page: {product_url} — {exc}")
            continue

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    raw_output = OUTPUT_DIR / "raw-books.json"
    raw_output.write_text(
        json.dumps(raw_books, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    valid_books, errors = validate_raw_books(raw_books)
    save_validated_books(valid_books, errors)

    duration_seconds = round(monotonic() - start_clock, 2)

    report = {
        "started_at": started_at.isoformat(),
        "duration_seconds": duration_seconds,
        "pages_fetched": RUN_STATS["pages_fetched"],
        "cache_hits": RUN_STATS["cache_hits"],
        "valid_records": len(valid_books),
        "invalid_records": len(errors),
        "failed_pages": RUN_STATS["failed_pages"],
    }

    report_path = OUTPUT_DIR / "run-report.json"
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\ndetail_pages={len(raw_books)}")
    print(f"valid_records={len(valid_books)}")
    print(f"invalid_records={len(errors)}")
    print(f"failed_pages={len(RUN_STATS['failed_pages'])}")
    print(f"Run report saved to: {report_path}")

if __name__ == "__main__":
    main()
