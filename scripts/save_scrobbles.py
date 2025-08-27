import requests
import pandas as pd
from datetime import datetime
import time
import os
from dotenv import load_dotenv

load_dotenv()

# ---- CONFIG ----
LASTFM_USER = os.getenv("LASTFM_USER")
API_KEY = os.getenv("LASTFM_API_KEY")
SAVE_FILE = "./data/scrobbles_now.csv"
FETCH_INTERVAL = 60  # seconds between checks
# ----------------

def fetch_lastfm_recent(user, api_key, limit=10):
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "user.getrecenttracks",
        "user": user,
        "api_key": api_key,
        "format": "json",
        "limit": limit
    }
    r = requests.get(url, params=params).json()
    tracks = r.get("recenttracks", {}).get("track", [])
    scrobbles = []

    for t in tracks:
        if "date" not in t:  # skip "now playing"
            continue
        scrobbles.append({
            "artist": t["artist"]["#text"],
            "track": t["name"],
            "album": t["album"]["#text"],
            "played_at": datetime.utcfromtimestamp(int(t["date"]["uts"]))
        })
    return pd.DataFrame(scrobbles)

# Load old file if exists
if os.path.exists(SAVE_FILE):
    scrobbles_df = pd.read_csv(SAVE_FILE, parse_dates=["played_at"])
else:
    scrobbles_df = pd.DataFrame(columns=["artist", "track", "album", "played_at"])

print(f"Currently stored: {len(scrobbles_df)} plays")

# ---- Loop to keep fetching ----
try:
    while True:
        new_df = fetch_lastfm_recent(LASTFM_USER, API_KEY, limit=50)
        print(new_df.head())

        # keep only truly new scrobbles
        if not new_df.empty:
            merged = pd.concat([scrobbles_df, new_df]).drop_duplicates(subset=["artist","track","played_at"])
            merged = merged.sort_values("played_at").reset_index(drop=True)

            if len(merged) > len(scrobbles_df):
                merged.to_csv(SAVE_FILE, index=False, encoding="utf-8")
                scrobbles_df = merged
                print(f"💾 Saved! Total plays stored: {len(scrobbles_df)}")

        time.sleep(FETCH_INTERVAL)

except KeyboardInterrupt:
    print("Stopped recording.")
