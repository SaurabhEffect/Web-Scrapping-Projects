import time
import logging
import os
import csv
import json
from datetime import datetime
from typing import Optional

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementClickInterceptedException,
)

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    handlers=[
        logging.FileHandler("logs/jobs_scraper.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

TARGET_URL   = "https://realpython.github.io/fake-jobs/"
SCRAPE_DATE  = datetime.now().strftime("%Y-%m-%d")
PAGE_WAIT    = 2
IMPLICIT_WAIT = 10

def build_driver(headless: bool = True) -> webdriver.Chrome:
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")

    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=opts)
    driver.implicitly_wait(IMPLICIT_WAIT)
    logger.info("Chrome WebDriver initialised (headless=%s)", headless)
    return driver

def scroll_to_bottom(driver: webdriver.Chrome, pause: float = 1.0) -> None:
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    logger.debug("Scrolled to bottom of page")

def wait_for_cards(driver: webdriver.Chrome, timeout: int = 15) -> bool:
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.card"))
        )
        return True
    except TimeoutException:
        logger.warning("Timed out waiting for job cards")
        return False

def extract_job_cards(driver: webdriver.Chrome) -> list[dict]:
    cards = driver.find_elements(By.CSS_SELECTOR, "div.card")
    logger.info(f"  Found {len(cards)} job cards on current view")

    jobs = []
    for card in cards:
        try:
            title    = card.find_element(By.CSS_SELECTOR, "h2.title.is-5").text.strip()
            company  = card.find_element(By.CSS_SELECTOR, "h3.subtitle.is-6").text.strip()
            location = card.find_element(By.CSS_SELECTOR, "p.location").text.strip()

            try:
                date_tag = card.find_element(By.CSS_SELECTOR, "time")
                date_posted = date_tag.get_attribute("datetime") or date_tag.text.strip()
            except NoSuchElementException:
                date_posted = "N/A"

            try:
                apply_btn = card.find_element(By.XPATH, ".//a[contains(text(),'Apply')]")
                apply_url = apply_btn.get_attribute("href")
            except NoSuchElementException:
                apply_url = "N/A"

            jobs.append({
                "title":       title,
                "company":     company,
                "location":    location,
                "date_posted": date_posted,
                "apply_url":   apply_url,
                "scraped_at":  SCRAPE_DATE,
            })

        except NoSuchElementException as e:
            logger.debug(f"Skipped malformed card: {e}")

    return jobs

def click_show_more(driver: webdriver.Chrome) -> bool:
    try:
        btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'More')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", btn)
        time.sleep(0.5)
        btn.click()
        logger.info("Clicked 'Load More' button")
        time.sleep(PAGE_WAIT)
        return True
    except (TimeoutException, ElementClickInterceptedException, NoSuchElementException):
        return False

def scrape_jobs(headless: bool = True) -> list[dict]:
    driver = build_driver(headless=headless)
    all_jobs: list[dict] = []
    seen_titles: set[str] = set()

    try:
        logger.info(f"Opening: {TARGET_URL}")
        driver.get(TARGET_URL)
        time.sleep(PAGE_WAIT)

        if not wait_for_cards(driver):
            logger.error("Job cards never appeared. Aborting.")
            return []

        scroll_to_bottom(driver, pause=1.0)
        jobs = extract_job_cards(driver)
        for j in jobs:
            key = (j["title"], j["company"])
            if key not in seen_titles:
                seen_titles.add(key)
                all_jobs.append(j)

        page = 1
        while click_show_more(driver):
            page += 1
            logger.info(f"Extracting page {page}")
            scroll_to_bottom(driver, pause=0.8)
            jobs = extract_job_cards(driver)
            added = 0
            for j in jobs:
                key = (j["title"], j["company"])
                if key not in seen_titles:
                    seen_titles.add(key)
                    all_jobs.append(j)
                    added += 1
            logger.info(f"  {added} new jobs added (total: {len(all_jobs)})")

    finally:
        driver.quit()
        logger.info("WebDriver closed.")

    logger.info(f"Scraping complete. Total jobs: {len(all_jobs)}")
    return all_jobs

def export_jobs(jobs: list[dict], out_dir: str = "data") -> None:
    os.makedirs(out_dir, exist_ok=True)
    df = pd.DataFrame(jobs)

    csv_path  = os.path.join(out_dir, f"jobs_{SCRAPE_DATE}.csv")
    json_path = os.path.join(out_dir, f"jobs_{SCRAPE_DATE}.json")

    df.to_csv(csv_path, index=False)
    df.to_json(json_path, orient="records", indent=2)

    logger.info(f"Saved {len(df)} jobs -> {csv_path}")
    logger.info(f"Saved {len(df)} jobs -> {json_path}")


if __name__ == "__main__":
    logger.info("=== Selenium Jobs Scraper Starting ===")

    jobs = scrape_jobs(headless=True)

    if jobs:
        export_jobs(jobs)
        df = pd.DataFrame(jobs)
        print(f"\n[SUCCESS] Scraped {len(df)} jobs\n")
        print(df[["title", "company", "location"]].head(10).to_string(index=False))
    else:
        logger.warning("No jobs collected. Check logs/jobs_scraper.log")
