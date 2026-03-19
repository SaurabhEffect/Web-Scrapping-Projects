import requests
import pandas as pd
import json
import logging
import os
import time
from typing import Any, Optional

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    handlers=[
        logging.FileHandler("logs/api_collector.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

API_BASE = "https://restcountries.com/v3.1"
HEADERS = {"Accept": "application/json"}
MAX_RETRIES = 3
RETRY_DELAY = 2


def api_get(endpoint: str, params: Optional[dict] = None) -> Optional[Any]:
    url = f"{API_BASE}/{endpoint}"
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(url, headers=HEADERS, params=params, timeout=15)
            r.raise_for_status()
            logger.info(f"API OK [{r.status_code}]: {url}")
            return r.json()
        except requests.exceptions.HTTPError as e:
            logger.warning(f"HTTP error attempt {attempt}/{MAX_RETRIES}: {e}")
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Connection error attempt {attempt}/{MAX_RETRIES}: {e}")
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout attempt {attempt}/{MAX_RETRIES}: {url}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return None
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)
    logger.error(f"All {MAX_RETRIES} attempts failed for {url}")
    return None


def extract_country(raw: dict) -> dict:
    def safe_get(d: dict, *keys, default="N/A"):
        for k in keys:
            if not isinstance(d, dict):
                return default
            d = d.get(k, default)
        return d if d != {} else default

    name = safe_get(raw, "name", "official")
    common_name = safe_get(raw, "name", "common")

    capital_list = raw.get("capital", [])
    capital = capital_list[0] if capital_list else "N/A"

    region = raw.get("region", "N/A")
    population = raw.get("population", 0)
    area = raw.get("area", 0.0)

    currencies = raw.get("currencies", {})
    if currencies:
        first_key = next(iter(currencies))
        currency_code = first_key
        currency_name = currencies[first_key].get("name", "N/A")
        currency_symbol = currencies[first_key].get("symbol", "N/A")
    else:
        currency_code = currency_name = currency_symbol = "N/A"

    languages = raw.get("languages", {})
    languages_str = ", ".join(languages.values()) if languages else "N/A"

    timezones = raw.get("timezones", [])
    timezone = timezones[0] if timezones else "N/A"

    continents = raw.get("continents", [])
    continent = continents[0] if continents else "N/A"

    cca3 = raw.get("cca3", "N/A")

    return {
        "common_name": common_name,
        "official_name": name,
        "cca3": cca3,
        "capital": capital,
        "region": region,
        "continent": continent,
        "population": population,
        "area_km2": area,
        "currency_code": currency_code,
        "currency_name": currency_name,
        "currency_symbol": currency_symbol,
        "languages": languages_str,
        "timezone": timezone,
    }


def fetch_all_countries() -> list[dict]:
    logger.info("Fetching all countries from REST Countries API...")
    raw_data = api_get("all", params={"fields": "name,capital,region,population,area,currencies,languages,timezones,continents,cca3"})
    if not raw_data or not isinstance(raw_data, list):
        logger.error("No data returned from API.")
        return []
    logger.info(f"Raw records received: {len(raw_data)}")
    records = [extract_country(c) for c in raw_data]
    logger.info(f"Flattened {len(records)} country records")
    return records


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    logger.info(f"Cleaning dataset: {len(df)} rows")
    before = len(df)
    df.drop_duplicates(subset=["cca3"], inplace=True)
    logger.info(f"Dropped {before - len(df)} duplicate rows")

    df["population"] = pd.to_numeric(df["population"], errors="coerce").fillna(0).astype(int)
    df["area_km2"] = pd.to_numeric(df["area_km2"], errors="coerce").fillna(0.0)

    df["pop_density"] = df.apply(
        lambda r: round(r["population"] / r["area_km2"], 2) if r["area_km2"] > 0 else 0.0,
        axis=1,
    )

    str_cols = ["capital", "currency_name", "currency_symbol", "languages", "timezone"]
    for col in str_cols:
        df[col] = df[col].replace("N/A", "Unknown")

    df.sort_values("population", ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)

    logger.info(f"Cleaning complete. Final dataset: {len(df)} rows")
    return df


def print_summary(df: pd.DataFrame) -> None:
    print("\n" + "=" * 55)
    print("  REST Countries Dataset Summary")
    print("=" * 55)
    print(f"  Total countries  : {len(df)}")
    print(f"  Regions          : {df['region'].nunique()}")
    print(f"  Total population : {df['population'].sum():,}")
    print(f"  Avg area (km²)   : {df['area_km2'].mean():,.0f}")
    print("\n  Top 5 by population:")
    top5 = df[["common_name", "population", "region"]].head(5)
    for _, row in top5.iterrows():
        print(f"    {row['common_name']:<25} {row['population']:>15,}  [{row['region']}]")
    print("=" * 55 + "\n")


def export_data(df: pd.DataFrame, out_dir: str = "data") -> None:
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "countries.csv")
    json_path = os.path.join(out_dir, "countries.json")
    df.to_csv(csv_path, index=False, encoding="utf-8")
    df.to_json(json_path, orient="records", indent=2, force_ascii=False)
    logger.info(f"Exported -> {csv_path}")
    logger.info(f"Exported -> {json_path}")


if __name__ == "__main__":
    logger.info("=== API Data Collector Starting ===")
    records = fetch_all_countries()
    if records:
        df = pd.DataFrame(records)
        df = clean_dataframe(df)
        export_data(df)
        print_summary(df)
        print("[Done] Files saved to data/")
    else:
        logger.error("No records to process.")
