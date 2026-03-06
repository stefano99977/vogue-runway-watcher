import json
import re
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://www.vogue.com"
SOURCE_URLS = [
    f"{BASE}/fashion-shows",
    f"{BASE}/fashion-shows/seasons",
]
HEADERS = {"User-Agent": "RunwayWatcher/1.0 (automation)"}

DATA_DIR = Path("data")
STATE_PATH = DATA_DIR / "state_shows.json"
NEW_PATH = DATA_DIR / "new_shows.json"

# Matches /fashion-shows/<season-slug>/<designer-slug>
SHOW_HREF_RE = re.compile(r"^/fashion-shows/([a-z0-9-]+)/([a-z0-9-]+)$")

EXCLUDE_PREFIXES = (
    "/fashion-shows/seasons",
    "/fashion-shows/designers",
    "/fashion-shows/featured",
    "/fashion-shows/image-archive",
    "/fashion-shows/latest-shows",
    "/fashion-shows/schedule",
    "/fashion-shows/runway",
)


def fetch(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text


def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"known_show_slugs": []}


def save_state(state: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(
        json.dumps(state, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def extract_show_slugs(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    show_slugs = set()

    for a in soup.select("a[href]"):
        href = (a.get("href") or "").split("?")[0].strip()
        if not href:
            continue

        if any(href.startswith(prefix) for prefix in EXCLUDE_PREFIXES):
            continue

        if "/gallery" in href:
            continue

        m = SHOW_HREF_RE.match(href)
        if not m:
            continue

        season_slug, designer_slug = m.groups()
        show_slugs.add(f"{season_slug}/{designer_slug}")

    return sorted(show_slugs)


def main() -> int:
    current_set = set()

    for url in SOURCE_URLS:
        print(f"🔎 Scanning source: {url}")
        html = fetch(url)
        current_set.update(extract_show_slugs(html))

    current_shows = sorted(current_set)

    state = load_state()
    known_list = state.get("known_show_slugs", [])
    known = set(known_list)

    new_shows = [s for s in current_shows if s not in known]

    if not new_shows:
        print("✅ No new show pages found.")
        return 0

    print(f"🆕 New show pages detected: {new_shows}")

    state["known_show_slugs"] = current_shows
    save_state(state)

    NEW_PATH.write_text(
        json.dumps({"new_shows": new_shows}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
