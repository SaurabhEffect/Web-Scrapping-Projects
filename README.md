# Python Web Scraping Projects

A collection of five Python web scraping projects covering progressively advanced techniques -- from static HTML parsing and API consumption to browser automation and multi-stage ETL pipelines.

---

## Projects

| # | Project | Level | Core Libraries |
|---|---------|-------|-----------------|
| 1 | [Quotes Scraper](./01.%20quotesScraper) | Beginner | requests, BeautifulSoup, pandas |
| 2 | [Hacker News Scraper](./02.%20newsScraper) | Beginner+ | requests, BeautifulSoup, pandas |
| 3 | [Selenium Jobs Scraper](./03.%20selenium-jobs) | Intermediate | Selenium, WebDriverWait, pandas |
| 4 | [REST Countries API Collector](./04.%20api-collector) | Intermediate | requests, pandas, json |
| 5 | [Books Scraping Pipeline](./05.%20Book-Scraping-Pipeline) | Advanced | requests, BeautifulSoup, pandas, argparse |

---

## Concepts Learned

### Web Scraping Fundamentals
- Sending HTTP requests and handling response status codes using the `requests` library
- Parsing HTML documents with `BeautifulSoup` to extract structured data via CSS selectors and tag navigation
- Navigating paginated websites by programmatically following "next page" links
- Implementing polite crawl delays between requests to avoid overwhelming target servers

### Browser Automation
- Controlling a headless Chrome browser using `Selenium WebDriver` for JavaScript-rendered pages
- Using `WebDriverWait` and Expected Conditions for reliable element detection instead of arbitrary sleep calls
- Scrolling pages via JavaScript execution to trigger lazy-loaded content
- Handling dynamic "Load More" buttons through programmatic click events

### API Data Collection
- Consuming RESTful APIs and processing raw JSON responses
- Flattening deeply nested JSON structures into tabular rows without data loss
- Working with APIs that require no authentication (public endpoints)

### Data Cleaning and Transformation
- Using `pandas` for type-casting, null handling, sorting, and deduplication
- Computing derived metrics from raw data (e.g., population density, price tiers)
- Exporting clean datasets in both CSV and JSON formats with timestamped filenames

### Pipeline Architecture and ETL Design
- Designing a modular three-stage pipeline: Extract, Transform, Load
- Implementing raw data checkpoints to avoid redundant network calls on re-runs
- Separating valid records from rejected records during the validation stage
- Generating summary reports with key statistics after each pipeline run

### Error Handling and Resilience
- Implementing retry logic with exponential backoff for failed HTTP requests
- Graceful error handling to prevent silent crashes and ensure partial data is preserved
- Structured logging to both console and log files for traceability and debugging

### CLI and Configuration
- Using `argparse` to add command-line flags for runtime configuration (e.g., `--max-pages`, `--skip-scrape`)
- Designing configurable constants (retry count, delay intervals) for easy tuning

