import os
from dotenv import load_dotenv
from save_scrobbles import fetch_lastfm_recent

load_dotenv()

user = os.getenv("LASTFM_USER")
api = os.getenv("LASTFM_API_KEY")

print("User:", user)
print("API:", api[:6] + "...")
df = fetch_lastfm_recent(user, api, limit=5)
print(df)

if not df.empty:
    df.to_csv("./data/test_scrobbles.csv", index=False)
    print("✅ Saved to data/test_scrobbles.csv")
else:
    print("⚠️ No scrobbles found")
