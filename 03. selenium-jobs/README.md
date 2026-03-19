# Selenium Jobs Scraper

A Selenium-powered automation bot that scrapes **job listings** from a dynamic JavaScript-rendered jobs board. Handles page scrolling, lazy-loaded content, "Load More" button clicks, and deduplication.

---

## Problem It Solves

Many job boards render listings via JavaScript — standard `requests` won't see the content. This bot uses a full Chrome browser to interact with the page exactly like a human would, then extracts structured job data.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| `selenium` | Browser automation, JS rendering |
| `ChromeDriver` | Controlled Chrome instance |
| `WebDriverWait` | Smart waits instead of `time.sleep` |
| `pandas` | Export to CSV/JSON |

---

## Prerequisites

- **Google Chrome** installed on your machine
- `chromedriver` that matches your Chrome version
  - Auto-managed via `webdriver-manager` (included in requirements)

---

## Folder Structure

```
project3-selenium-jobs/
├── scraper/
│   └── jobs_scraper.py     # Core Selenium bot
├── data/
│   ├── jobs_YYYY-MM-DD.csv
│   └── jobs_YYYY-MM-DD.json
├── logs/
│   └── jobs_scraper.log
├── requirements.txt
└── README.md
```

---

## Setup & Run

```bash
cd project3-selenium-jobs
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run headless (default)
python scraper/jobs_scraper.py

# To watch the browser — edit jobs_scraper.py:
# scrape_jobs(headless=False)
```

---

## Example Output

| title | company | location | date_posted | apply_url |
|---|---|---|---|---|
| Senior Python Developer | SUSE | Scranton, PA | 2021-04-08 | https://... |
| Energy engineer | Becker-Carroll | Deckerhaven, TX | 2021-04-08 | https://... |
| Product Manager | Archer, Stone and Howard | Lake Constanceside | 2021-04-08 | https://... |

---

## Key Selenium Techniques

```python
# Wait for element to be clickable
WebDriverWait(driver, 10).until(EC.element_to_be_clickable(...))

# Scroll to trigger lazy loading
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

# Click through JS if normal click fails
driver.execute_script("arguments[0].click();", element)
```

---

## Future Improvements

- Add proxy rotation to avoid IP blocking
- Screenshot on error for debugging
- Filter by job title keyword / location
- Export to SQLite for historical tracking
- Add `argparse` CLI flags: `--headless`, `--max-pages`, `--keyword`
