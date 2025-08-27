import os
import time
import requests
import pandas as pd
from pathlib import Path

LASTFM_USER = os.getenv("LASTFM_USER")
LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
DATA_PATH = Path("./data/scrobbles_now.csv")
FETCH_INTERVAL = 60  # seconds

def fetch_recent_tracks():
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "user.getrecenttracks",
        "user": LASTFM_USER,
        "api_key": API_KEY,
        "format": "json",
        "limit": 50
    }
    r = requests.get(url, params=params).json()
    tracks = r.get("recenttracks", {}).get("track", [])
    scrobbles = []

    for item in tracks:
        # Skip "now playing" tracks or missing date
        date_info = item.get("date")
        if not date_info:
            continue

        # Some responses use "#uts" or "uts"
        uts = date_info.get("#uts") or date_info.get("uts")
        if not uts:
            continue

        played_at = pd.to_datetime(int(uts), unit="s")
        scrobbles.append({
            "artist": item["artist"]["#text"],
            "track": item["name"],
            "album": item["album"]["#text"],
            "played_at": played_at
        })

    return pd.DataFrame(scrobbles)



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
