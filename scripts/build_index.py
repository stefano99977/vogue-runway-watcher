from pathlib import Path

SITE_DIR = Path("docs")
SEASONS_DIR = SITE_DIR / "seasons"


def main():
    SEASONS_DIR.mkdir(parents=True, exist_ok=True)
    pages = sorted(SEASONS_DIR.glob("*.html"))

    items = []
    for p in pages:
        rel = f"seasons/{p.name}"
        label = p.stem.replace("-", " ").title()
        items.append(f'  <li><a href="{rel}">{label}</a></li>')

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Vogue Runway Watcher</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 32px auto;
      max-width: 960px;
      padding: 0 16px;
      color: #111;
      background: #fafafa;
    }}
    h1 {{ margin-bottom: 8px; }}
    .lead {{ color: #555; margin-bottom: 24px; }}
    .card {{
      background: #fff;
      border: 1px solid #ddd;
      border-radius: 14px;
      padding: 18px;
      margin-bottom: 24px;
    }}
    .starred-link {{
      display: inline-block;
      padding: 12px 16px;
      border-radius: 10px;
      border: 1px solid #111;
      text-decoration: none;
      color: #111;
      font-weight: 600;
    }}
    ul {{ line-height: 1.8; }}
  </style>
</head>
<body>
  <h1>Vogue Runway Watcher</h1>
  <p class="lead">Auto-generated galleries (one per season detected on Vogue).</p>

  <div class="card">
    <a class="starred-link" href="starred.html">⭐ Open my starred moodboard</a>
  </div>

  <h2>Seasons</h2>
  <ul>
{''.join(items) if items else '  <li>No seasons processed yet.</li>'}
  </ul>
</body>
</html>
"""
    (SITE_DIR / "index.html").write_text(html, encoding="utf-8")
    print("✅ docs/index.html updated")


if __name__ == "__main__":
    main()
