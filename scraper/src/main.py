from pathlib import Path
from time import sleep
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
CACHE_DIR = Path(__file__).resolve().parents[1] / "cache"
TIMEOUT_SECONDS = 10
REQUEST_DELAY_SECONDS = 0.5
MAX_CATALOGUE_PAGES = 3

HEADERS = {
    "User-Agent": (
        "FlyRankInternship-A9/1.0 "
        "(educational scraper; contact: add-your-repo-link)"
    )
}


def fetch_page(url: str, cache_file: Path) -> str:
    """Fetch a page once and cache its original response bytes."""
    if cache_file.exists():
        content = cache_file.read_bytes()
        print(f"CACHE HIT: {url}")
        print(f"Response size: {len(content)} bytes")
        return content.decode("utf-8")

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Be polite before every live request after the first one.
    if getattr(fetch_page, "has_requested", False):
        sleep(REQUEST_DELAY_SECONDS)

    print(f"FETCH: {url}")
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=TIMEOUT_SECONDS,
    )
    fetch_page.has_requested = True

    if response.status_code != 200:
        raise requests.HTTPError(
            f"Expected HTTP 200 for {url}, got {response.status_code}",
            response=response,
        )

    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_bytes(response.content)

    print(f"HTTP status: {response.status_code}")
    print(f"Cached HTML: {cache_file}")
    print(f"Response size: {len(response.content)} bytes")
    return response.content.decode("utf-8")


def discover_catalogue_pages() -> list[tuple[str, str]]:
    """Follow the site's Next link for at most three catalogue pages."""
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
                f"Could not find the Next link on catalogue page {page_number}"
            )

        current_url = urljoin(current_url, next_link["href"])

    return pages


def discover_book_urls(
    catalogue_pages: list[tuple[str, str]],
) -> list[str]:
    """Extract and deduplicate book detail URLs in catalogue order."""
    unique_urls = []

    for page_url, html in catalogue_pages:
        soup = BeautifulSoup(html, "html.parser")

        for link in soup.select("article.product_pod h3 a"):
            href = link.get("href")
            if href:
                product_url = urljoin(page_url, href)
                if product_url not in unique_urls:
                    unique_urls.append(product_url)

    return unique_urls


def main() -> None:
    pages = discover_catalogue_pages()
    book_urls = discover_book_urls(pages)

    print(f"catalogue_pages={len(pages)}")
    print(f"discovered={len(book_urls)}")
    print(f"unique_urls={len(set(book_urls))}")


if __name__ == "__main__":
    main()
