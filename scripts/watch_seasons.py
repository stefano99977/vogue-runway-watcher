import json
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE = "https://www.vogue.com"
SOURCE_URLS = [
    "https://www.vogue.com/fashion-shows/seasons",
    "https://www.vogue.com/fashion-shows",
]
HEADERS = {"User-Agent": "RunwayWatcher/1.0 (automation)"}

DATA_DIR = Path("data")
STATE_PATH = DATA_DIR / "state_seasons.json"
NEW_PATH = DATA_DIR / "new_seasons.json"

# Matches /fashion-shows/<season-slug>
SEASON_HREF_RE = re.compile(r"^/fashion-shows/[a-z0-9-]+$")

# Matches /fashion-shows/<season-slug>/<designer-slug>
SHOW_HREF_RE = re.compile(r"^/fashion-shows/([a-z0-9-]+)/([a-z0-9-]+)$")

EXCLUDE = {
    "/fashion-shows/seasons",
    "/fashion-shows/latest-shows",
    "/fashion-shows/designers",
    "/fashion-shows/featured",
    "/fashion-shows/image-archive",
    "/fashion-shows/schedule",
    "/fashion-shows/runway",
}

def fetch(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text

def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"known_season_slugs": []}

def save_state(state: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(
        json.dumps(state, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

def extract_season_slugs(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    slugs = set()

    for a in soup.select("a[href]"):
        href = (a.get("href") or "").split("?")[0].strip()
        if not href:
            continue

        if href in EXCLUDE:
            continue

        if SEASON_HREF_RE.match(href):
            slug = href.split("/fashion-shows/")[1]
            slugs.add(slug)
            continue

        m = SHOW_HREF_RE.match(href)
        if m:
            season_slug = m.group(1)
            if f"/fashion-shows/{season_slug}" not in EXCLUDE:
                slugs.add(season_slug)

    return sorted(slugs)

def main() -> int:
    current_set = set()

    for url in SOURCE_URLS:
        print(f"🔎 Scanning source: {url}")
        html = fetch(url)
        current_set.update(extract_season_slugs(html))

    current_slugs = sorted(current_set)

    state = load_state()
    known_list = state.get("known_season_slugs", [])

    if not known_list:
        print(f"🧱 Bootstrap: saving {len(current_slugs)} season slugs as baseline (no scraping).")
        state["known_season_slugs"] = current_slugs
        save_state(state)
        return 0

    known = set(known_list)
    new_slugs = [s for s in current_slugs if s not in known]

    if not new_slugs:
        print("✅ No new season pages found.")
        return 0

    print(f"🆕 New season pages detected: {new_slugs}")

    state["known_season_slugs"] = current_slugs
    save_state(state)

    NEW_PATH.write_text(
        json.dumps({"new_seasons": new_slugs}, indent=2),
        encoding="utf-8",
    )

    return 1

if __name__ == "__main__":
    raise SystemExit(main())
