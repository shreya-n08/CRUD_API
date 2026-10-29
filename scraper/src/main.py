from pathlib import Path

import requests

BASE_URL = "https://books.toscrape.com/"
CACHE_DIR = Path(__file__).resolve().parents[1] / "cache"
CACHE_FILE = CACHE_DIR / "catalogue-page-1.html"

HEADERS = {
    "User-Agent": (
        "FlyRankInternship-A9/1.0 "
        "(educational scraper; contact: add-your-repo-link)"
    )
}
TIMEOUT_SECONDS = 10


def fetch_catalogue_page() -> str:
    """Fetch the first catalogue page once and cache its HTML."""
    if CACHE_FILE.exists():
        content = CACHE_FILE.read_bytes()
        html = content.decode("utf-8")
        print(f"CACHE HIT: {CACHE_FILE}")
        print(f"Response size: {len(content)} bytes")
        return html

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    print(f"FETCH: {BASE_URL}")
    response = requests.get(
        BASE_URL,
        headers=HEADERS,
        timeout=TIMEOUT_SECONDS,
    )

    if response.status_code != 200:
        raise requests.HTTPError(
            f"Expected HTTP 200, received {response.status_code}",
            response=response,
        )

    html = response.text
    CACHE_FILE.write_bytes(response.content)

    print(f"HTTP status: {response.status_code}")
    print(f"Cached HTML: {CACHE_FILE}")
    print(f"Response size: {len(response.content)} bytes")
    return html


def main() -> None:
    fetch_catalogue_page()


if __name__ == "__main__":
    main()
