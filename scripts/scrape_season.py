import csv
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://www.vogue.com"
HEADERS = {"User-Agent": "RunwayWatcher/1.0 (automation)"}

DATA_DIR = Path("data/seasons")
DATA_DIR.mkdir(parents=True, exist_ok=True)


def fetch(url: str) -> str | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def normalize_show_ref(show_ref: str) -> tuple[str, str, str]:
    """
    Accepts either:
      - fall-2026-ready-to-wear/loewe
      - https://www.vogue.com/fashion-shows/fall-2026-ready-to-wear/loewe
    Returns:
      (season_slug, designer_slug, show_url)
    """
    show_ref = show_ref.strip()

    if show_ref.startswith("http://") or show_ref.startswith("https://"):
        show_url = show_ref.split("?")[0].rstrip("/")
        parts = show_url.replace(BASE, "").strip("/").split("/")
        if len(parts) != 3 or parts[0] != "fashion-shows":
            raise ValueError(f"Unsupported Vogue show URL: {show_ref}")
        season_slug = parts[1]
        designer_slug = parts[2]
        return season_slug, designer_slug, show_url

    parts = show_ref.strip("/").split("/")
    if len(parts) != 2:
        raise ValueError(
            "Expected show ref like 'fall-2026-ready-to-wear/loewe' or a full Vogue show URL"
        )

    season_slug, designer_slug = parts
    show_url = f"{BASE}/fashion-shows/{season_slug}/{designer_slug}"
    return season_slug, designer_slug, show_url


def safe_name(season_slug: str, designer_slug: str) -> str:
    return f"{season_slug}--{designer_slug}"


def extract_show_data(season_slug: str, designer_slug: str, show_url: str) -> list[dict]:
    print(f"🔭 Show page: {show_url}")
    html = fetch(show_url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    designer = designer_sl_
