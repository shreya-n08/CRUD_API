# The Polite Scraper

## Target classification

- **Target website:** Books to Scrape — https://books.toscrape.com/
- **Purpose:** Educational web-scraping practice using a website designed for this activity.
- **Scope:** The first three catalogue pages and the book detail pages linked from those pages.
- **Data collected:** Title, product URL, price, availability, rating, description, source page, and fetch timestamp.
- **Why appropriate:** Books to Scrape is a practice catalogue intended for scraping exercises.

## Robots.txt check

Checked: https://books.toscrape.com/robots.txt

Result: HTTP 404 Not Found. No robots.txt file was found at this URL. A missing robots file does not itself grant permission; the site's rules and terms must still be respected.

## Politeness and limitations

- Use an identifiable User-Agent.
- Set request timeouts and check HTTP status codes.
- Cache downloaded HTML to avoid unnecessary repeat requests.
- Wait at least 0.5 seconds between live requests.
- Collect only the fields required by the assignment.
- Do not bypass access controls, login requirements, or blocks.
- Prefer an official API when one is available.
- This scraper is intended for this practice website only.

I will not reuse this code on another site without checking its rules and terms first.
