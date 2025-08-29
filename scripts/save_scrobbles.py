import os
import requests
import pandas as pd
from datetime import datetime

# Load environment variables
API_KEY = os.getenv("LASTFM_API_KEY")
USER = os.getenv("LASTFM_USER")

if not API_KEY or not USER:
    raise ValueError("❌ Missing LASTFM_API_KEY or LASTFM_USER. Did you set repository secrets?")

DATA_FILE = "scrobbles.csv"

def fetch_recent_tracks(limit=50):
    """Fetch recent tracks from Last.fm"""
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "user.getrecenttracks",
        "user": USER,
        "api_key": API_KEY,
        "format": "json",
        "limit": limit,
    }

    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()

    tracks = []
    for item in data.get("recenttracks", {}).get("track", []):
        # Skip "now playing" (no date)
        if "date" not in item:
            continue

        # Some APIs use 'uts', some use '#uts'
        played_at = item["date"].get("uts") or item["date"].get("#uts")
        if not played_at:
            continue

        tracks.append({
            "artist": item["artist"]["#text"],
            "track": item["name"],
            "album": item["album"]["#text"],
            "played_at": datetime.utcfromtimestamp(int(played_at)),
        })

    return pd.DataFrame(tracks)


def save_new_scrobbles():
    """Fetch new tracks and save them to CSV (no duplicates)."""
    new_df = fetch_recent_tracks()

    if new_df.empty:
        print("⚠️ No new tracks fetched.")
        return

    if os.path.exists(DATA_FILE):
        old_df = pd.read_csv(DATA_FILE, parse_dates=["played_at"])
        combined = pd.concat([old_df, new_df]).drop_duplicates(subset=["artist", "track", "played_at"])
    else:
        combined = new_df

    combined.sort_values("played_at", inplace=True)
    combined.to_csv(DATA_FILE, index=False)
    print(f"✅ Saved {len(new_df)} new scrobbles, total {len(combined)}.")


def main():
    print("⚡ Running once (GitHub Actions mode)")
    save_new_scrobbles()


if __name__ == "__main__":
    main()
