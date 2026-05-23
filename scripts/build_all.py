"""Build a single page containing every image of every show in one scrollable gallery.

Reads all per-season / per-show CSVs in data/seasons/, removes cross-file
duplicates (the season-aggregate files and the per-designer files overlap on
identical image URLs), orders the looks sensibly, and renders one combined
gallery page at docs/all.html — reusing the exact same template, styling,
modal, star feature and filters as the per-season pages.
"""

from pathlib import Path

import pandas as pd

from build_gallery import df_to_items, render_gallery, TEMPLATE_STAR_KEY_PREFIX

SEASONS_CSV_DIR = Path("data/seasons")
OUT_PATH = Path("docs/all.html")


def _look_sort_key(value) -> int:
    s = str(value).strip()
    return int(s) if s.isdigit() else 10**9


def main() -> None:
    files = sorted(SEASONS_CSV_DIR.glob("*.csv"))
    if not files:
        print("No CSVs found in data/seasons/ — nothing to build.")
        return

    df = pd.concat((pd.read_csv(f).fillna("") for f in files), ignore_index=True)

    before = len(df)
    # The season-aggregate CSVs (e.g. fall-2026-ready-to-wear.csv) and the
    # per-designer CSVs share identical image URLs, so dedupe on image_url.
    df = df.drop_duplicates(subset=["image_url"], keep="first")
    after = len(df)

    # Readable scroll order: season, then designer, then look number.
    df["_lk"] = df["look_number"].map(_look_sort_key)
    df = df.sort_values(["season", "designer", "_lk"]).drop(columns=["_lk"])

    data = df_to_items(df, page_slug="all", page_url="all.html")

    n_seasons = df["season"].nunique()
    n_designers = df["designer"].nunique()
    source_label = (
        f"all shows · {after:,} looks · {n_seasons} seasons · {n_designers} designers"
    )

    render_gallery(
        data,
        OUT_PATH,
        title="Vogue Runway — All Shows",
        source_label=source_label,
        star_key=TEMPLATE_STAR_KEY_PREFIX + "all",
    )

    print(
        f"✅ docs/all.html built — {after:,} looks "
        f"({before - after:,} duplicates removed) "
        f"across {n_seasons} seasons, {n_designers} designers"
    )


if __name__ == "__main__":
    main()
