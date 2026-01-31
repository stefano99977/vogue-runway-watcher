from pathlib import Path

SITE_DIR = Path("site")
SEASONS_DIR = SITE_DIR / "seasons"

def main():
    SEASONS_DIR.mkdir(parents=True, exist_ok=True)
    pages = sorted(SEASONS_DIR.glob("*.html"))

    items = []
    for p in pages:
        rel = f"seasons/{p.name}"
        label = p.stem.replace("-", " ").title()
        items.append(f'<li><a href="{rel}">{label}</a></li>')

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Vogue Runway Watcher</title>
  <style>
    body {{
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
      margin: 40px;
      line-height: 1.4;
    }}
    a {{ text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .muted {{ color: #666; }}
    .card {{
      max-width: 900px;
      border: 1px solid #ddd;
      border-radius: 14px;
      padding: 18px;
    }}
  </style>
</head>
<body>
  <div class="card">
    <h1>Vogue Runway Watcher</h1>
    <p class="muted">Auto-generated galleries (one per season detected on Vogue).</p>

    <h2>Seasons</h2>
    <ul>
      {''.join(items) if items else '<li>No seasons processed yet.</li>'}
    </ul>
  </div>
</body>
</html>
"""
    (SITE_DIR / "index.html").write_text(html, encoding="utf-8")
    print("✅ site/index.html updated")

if __name__ == "__main__":
    main()

