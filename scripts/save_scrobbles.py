import os
import requests
import pandas as pd
from datetime import datetime

USER = os.getenv("LASTFM_USER")
API_KEY = os.getenv("LASTFM_API_KEY")
ONCE = os.getenv("ONCE", "0") == "1"

URL = "http://ws.audioscrobbler.com/2.0/"

def fetch_scrobbles():
    params = {
        "method": "user.getrecenttracks",
        "user": USER,
        "api_key": API_KEY,
        "format": "json",
        "limit": 200,
    }
    r = requests.get(URL, params=params)
    r.raise_for_status()
    return r.json().get("recenttracks", {}).get("track", [])

def normalize(scrobbles):
    rows = []
    for t in scrobbles:
        rows.append({
            "artist": t.get("artist", {}).get("#text", ""),
            "track": t.get("name", ""),
            "album": t.get("album", {}).get("#text", ""),
            "timestamp": t.get("date", {}).get("uts", datetime.utcnow().timestamp()),
        })
    return pd.DataFrame(rows)

def main():
    scrobbles = fetch_scrobbles()
    df = normalize(scrobbles)

    # ✅ Always save to data/scrobbles_now.csv
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/scrobbles_now.csv", index=False)

    if not ONCE:
        # Optional: also append to history
        df.to_csv("data/scrobbles_history.csv", mode="a", header=False, index=False)

if __name__ == "__main__":
    main()
