import pandas as pd
from pathlib import Path

data_file = Path("data/scrobbles_now.csv")
out_file = Path("docs/index.html")

if not data_file.exists():
    print("No data yet.")
    exit(0)

df = pd.read_csv(data_file)

# Keep only the most recent 20 plays
latest = df.sort_values("played_at", ascending=False).head(20)

# Simple HTML dashboard
html = """
<html>
<head>
  <meta charset="UTF-8">
  <title>🎶 My Live Scrobbles</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 2em; background: #fafafa; }
    h1 { font-size: 1.5em; }
    table { border-collapse: collapse; width: 100%%; }
    th, td { padding: 8px 12px; border-bottom: 1px solid #ddd; }
    tr:hover { background: #f1f1f1; }
  </style>
</head>
<body>
  <h1>🎶 My Recent Scrobbles</h1>
  <p>Auto-updated every 5 minutes from Last.fm</p>
  %s
</body>
</html>
""" % latest.to_html(index=False, escape=False)

out_file.parent.mkdir(exist_ok=True)
out_file.write_text(html, encoding="utf-8")

# Create .nojekyll so GitHub Pages serves raw HTML
Path("docs/.nojekyll").touch()

print(f"✅ Dashboard generated at {out_file}")
