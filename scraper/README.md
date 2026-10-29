# The Polite Scraper

A polite, cache-first web scraper that collects book information from [Books to Scrape](https://books.toscrape.com/), validates the extracted records, normalizes prices, and produces structured JSON output with a run report.

This project was built as **Assignment 5 — The Polite Scraper** for the Backend AI Engineering track. It demonstrates responsible web scraping, HTML parsing, data validation, error handling, caching, and reproducible command-line execution.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Target Classification and Scope](#target-classification-and-scope)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Running the Scraper](#running-the-scraper)
- [Output Files](#output-files)
- [Data Schema](#data-schema)
- [Politeness and Error Handling](#politeness-and-error-handling)
- [Limitations](#limitations)
- [Ethical Use](#ethical-use)

## Overview

The scraper discovers the first three catalogue pages on Books to Scrape, follows the book links found on those pages, and extracts information from each book's detail page.

The pipeline transforms the collected HTML into validated JSON records. It retains the original price text while adding a numeric GBP price, identifies records by product URL, and records failures instead of allowing a single failed detail-page request to terminate the entire run.

The scraper uses a local HTML cache to reduce repeated network requests during development and subsequent runs.

## Features

- **Catalogue discovery:** follows the website's Next-page links to discover three catalogue pages.
- **Product discovery:** extracts book links from catalogue HTML, resolves relative URLs, and removes duplicate URLs.
- **HTML caching:** saves downloaded pages locally and reuses cached HTML on subsequent runs.
- **Book extraction:** collects titles, product URLs, prices, availability, ratings, descriptions, source pages, and UTC timestamps.
- **Price normalization:** converts price text such as `£51.77` into the numeric value `51.77`.
- **Data validation:** uses Pydantic to validate records before saving them as normalized JSON.
- **Duplicate protection:** uses the canonical product URL as the record identity.
- **Failure handling:** retries eligible transient request failures once and records failed detail pages.
- **Run reporting:** records execution duration, fetch/cache counts, valid and invalid record totals, and failed pages.
- **Structured outputs:** separates validated records, validation errors, raw extracted records, and execution reports.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Requests | HTTP requests and timeouts |
| BeautifulSoup 4 | HTML parsing and data extraction |
| Pydantic | Record validation |
| JSON | Structured data storage |
| Git and GitHub | Version control and project hosting |

## Target Classification and Scope

**Target website:** [Books to Scrape](https://books.toscrape.com/)

**Robots.txt:** The URL `https://books.toscrape.com/robots.txt` was checked and returned HTTP 404 Not Found. A missing robots.txt file does not itself grant permission to scrape; the site's applicable terms and rules must still be considered.

**Scope:** The first three catalogue pages and the book detail pages linked from those pages.

**Data collected:**

- Book title
- Product URL
- Original price text
- Numeric price in GBP
- Availability text
- Star-rating label
- Description, when available
- Source catalogue page
- UTC fetch timestamp

This project is intended for educational practice on the designated test website.

## Project Structure

```text
scraper/
├── src/
│   └── main.py
├── cache/
│   ├── catalogue-page-1.html
│   ├── catalogue-page-2.html
│   ├── catalogue-page-3.html
│   └── details/
├── output/
│   ├── raw-books.json
│   ├── books.json
│   ├── errors.json
│   └── run-report.json
├── .gitignore
└── README.md
```

The cache and generated output directories are local runtime artifacts and are excluded from version control by the scraper's `.gitignore`. A small sample output can be published separately as project evidence.

## Getting Started

### Prerequisites

- Python 3.10 or later
- pip
- Git

### 1. Clone the repository

```bash
git clone https://github.com/shreya-n08/CRUD_API.git
cd CRUD_API
```

### 2. Create and activate a virtual environment

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

From the repository root:

```bash
python -m pip install -r requirements.txt
```

The project dependencies include Requests, BeautifulSoup 4, and Pydantic. If the repository's root requirements file does not include all three, install them explicitly:

```bash
python -m pip install requests beautifulsoup4 pydantic
```

## Running the Scraper

Run the scraper from the repository root:

```bash
python scraper/src/main.py
```

The scraper will:

1. Discover the first three catalogue pages.
2. Extract unique book URLs.
3. Fetch book detail pages or reuse cached HTML.
4. Extract the raw book records.
5. Validate and normalize the records.
6. Save JSON output files and a run report.

On a repeat run, cached HTML is reused when available. This reduces unnecessary network requests and makes development faster.

## Output Files

Generated files are written to `scraper/output/`.

| File | Description |
|---|---|
| `raw-books.json` | Raw extracted records before normalization |
| `books.json` | Validated records with numeric `price_gbp` |
| `errors.json` | Invalid records and validation or duplicate reasons |
| `run-report.json` | Execution metrics and failed-page details |

### Example normalized record

The following is an illustrative record showing the output structure:

```json
{
  "title": "A Light in the Attic",
  "product_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
  "price_text": "£51.77",
  "price_gbp": 51.77,
  "availability_text": "In stock (22 available)",
  "rating_text": "Three",
  "description": "Book description extracted from the detail page",
  "source_page": "https://books.toscrape.com/",
  "fetched_at": "2026-10-29T12:00:00+00:00"
}
```

The description and timestamp above illustrate the schema; the timestamp is not claimed to be the original fetch time for this example.

## Data Schema

Each normalized record contains the following fields:

| Field | Type | Description |
|---|---|---|
| `title` | String | Book title |
| `product_url` | URL string | Canonical product URL and record identity |
| `price_text` | String | Original price as displayed by the website |
| `price_gbp` | Number | Normalized numeric price in GBP |
| `availability_text` | String | Availability text from the detail page |
| `rating_text` | String | Star-rating label, such as `Three` |
| `description` | String or null | Book description, if available |
| `source_page` | URL string | Catalogue page where the book was discovered |
| `fetched_at` | ISO 8601 timestamp | Time the detail page was processed, in UTC |

Raw records contain the eight extraction fields; `price_gbp` is added during normalization.

## Politeness and Error Handling

The scraper follows these practices:

- Uses an identifiable User-Agent.
- Sets a request timeout.
- Accepts only HTTP 200 responses as successful page fetches.
- Waits at least 0.5 seconds between live requests.
- Caches downloaded HTML to avoid unnecessary repeat requests.
- Retries timeouts, connection errors, and HTTP 5xx errors once.
- Does not retry HTTP 403 or 404 responses.
- Records failed detail-page URLs and continues processing other books.
- Validates extracted data before including it in `books.json`.
- Records invalid records and their reasons in `errors.json`.

Catalogue-page discovery failures can still stop the run if the scraper cannot discover the required pages. Failed book detail pages are handled separately so that other successfully extracted books can survive.

## Limitations

- The scraper is designed for the current HTML structure of Books to Scrape; website markup changes may require updates.
- Cached pages may not reflect the website's latest content.
- A failed page may result in fewer than 60 validated records in a particular run.
- Extracted descriptions depend on the source page's content and quality.
- The scraper is not intended to bypass access controls, authentication, rate limits, or website restrictions.

## Ethical Use

Prefer an official API when one is available. Keep request rates low, collect only the data needed for the task, and respect applicable website terms and access rules. Do not use this project to bypass access controls or to collect sensitive personal information.

I will not reuse this code on another site without checking its rules and terms first.
