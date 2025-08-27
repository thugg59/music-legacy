import os
import time
import requests
import pandas as pd
from pathlib import Path

LASTFM_USER = os.getenv("LASTFM_USER")
LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
DATA_PATH = Path("./data/scrobbles_now.csv")
FETCH_INTERVAL = 60  # seconds

def fetch_recent_tracks(limit=50):
    url = (
        "http://ws.audioscrobbler.com/2.0/"
        f"?method=user.getrecenttracks&user={LASTFM_USER}"
        f"&api_key={LASTFM_API_KEY}&format=json&limit={limit}"
    )
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    tracks = []

    for item in data["recenttracks"]["track"]:
        if "date" not in item:
            continue  # skip "now playing" (no timestamp yet)
        played_at = item["date"]["#uts"]
        tracks.append({
            "artist": item["artist"]["#text"],
            "track": item["name"],
            "album": item["album"]["#text"],
            "played_at": pd.to_datetime(int(played_at), unit="s")
        })
    return pd.DataFrame(tracks)

def ensure_csv():
    if not DATA_PATH.exists():
        df = pd.DataFrame(columns=["artist", "track", "album", "played_at"])
        df.to_csv(DATA_PATH, index=False)
        print(f"📄 Created empty CSV at {DATA_PATH}")

def save_new_scrobbles():
    ensure_csv()
    scrobbles_df = pd.read_csv(DATA_PATH, parse_dates=["played_at"])
    new_df = fetch_recent_tracks()

    merged = pd.concat([scrobbles_df, new_df]).drop_duplicates(
        subset=["artist", "track", "album", "played_at"], keep="first"
    ).sort_values("played_at")

    merged.to_csv(DATA_PATH, index=False)
    print(f"💾 Saved! Total plays stored: {len(merged)}")

def main():
    run_once = os.getenv("ONCE") == "1"

    if run_once:
        print("⚡ Running once (GitHub Actions mode)")
        save_new_scrobbles()
    else:
        print("🔁 Continuous mode (local logging)")
        while True:
            save_new_scrobbles()
            time.sleep(FETCH_INTERVAL)

if __name__ == "__main__":
    main()
