import csv
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://www.vogue.com"
HEADERS = {"User-Agent": "RunwayWatcher/1.0 (automation)"}
RATE_LIMIT = 2.0

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

def get_show_links(season_slug: str) -> list[str]:
    season_url = f"{BASE}/fashion-shows/{season_slug}"
    print(f"🔭 Season page: {season_url}")
    html = fetch(season_url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    links: list[str] = []

    # Designer show links usually look like:
    # /fashion-shows/<season_slug>/<designer-slug>
    for a in soup.select(f"a[href*='/fashion-shows/{season_slug}/']"):
        href = a.get("href")
        if not href:
            continue

        full = urljoin(BASE, href.split("?")[0])

        # Skip gallery sub-pages
        if "/gallery" in full:
            continue

        # Keep canonical show pages: .../fashion-shows/<season>/<designer>
        parts = full.strip("/").split("/")
        if len(parts) >= 3 and parts[-2] == season_slug:
            if full not in links:
                links.append(full)

    return sorted(links)

def extract_show_data(season_slug: str, show_url: str) -> list[dict]:
    html = fetch(show_url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")

    designer = show_url.rstrip("/").split("/")[-1].replace("-", " ").title()

    looks: list[dict] = []
    for idx, fig in enumerate(soup.find_all("figure")):
        img = fig.find("img")
        if not img:
            continue

        img_src = img.get("data-src") or img.get("src")
        if not img_src:
            continue

        clean_img_url = urljoin(BASE, img_src.split("?")[0])

        cap_tag = fig.find("figcaption")
        caption = cap_tag.get_text(strip=True) if cap_tag else ""

        looks.append({
            "season": season_slug,
            "designer": designer,
            "look_number": idx + 1,
            "image_url": clean_img_url,
            "caption": caption,
            "source_url": show_url
        })

    return looks

def write_csv(season_slug: str, rows: list[dict]) -> Path:
    out = DATA_DIR / f"{season_slug}.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["season", "designer", "look_number", "image_url", "caption", "source_url"]
        )
        writer.writeheader()
        writer.writerows(rows)
    return out

def main(season_slug: str) -> int:
    show_urls = get_show_links(season_slug)
    print(f"Found {len(show_urls)} collections for {season_slug}.")

    all_rows: list[dict] = []
    for i, url in enumerate(show_urls, 1):
        print(f"[{i}/{len(show_urls)}] Scraping {url}")
        all_rows.extend(extract_show_data(season_slug, url))
        time.sleep(RATE_LIMIT)

    if not all_rows:
        print("⚠️ No looks extracted. Vogue layout may have changed.")
        return 2

    out = write_csv(season_slug, all_rows)
    print(f"✅ Wrote {len(all_rows)} looks → {out}")
    return 0

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python scripts/scrape_season.py <season-slug>")
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))

