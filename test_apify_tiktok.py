import os

from apify_client import ApifyClient  # type: ignore[import]
from dotenv import load_dotenv

# 1) export APIFY_TOKEN=...  (albo użyj .env – patrz niżej)
load_dotenv()
APIFY_TOKEN = os.getenv("APIFY_TOKEN")
if not APIFY_TOKEN:
    raise RuntimeError("APIFY_TOKEN is not configured. Add it to your environment or .env file.")

client = ApifyClient(APIFY_TOKEN)

# 2) Minimalny, poprawny input: użyj pustych list zamiast None i usuń puste stringi
run_input = {
    "resultsPerPage": 1,
    "profiles": [],                       # <-- pusta tablica zamiast None
    "profileScrapeSections": ["videos"],
    "profileSorting": "latest",
    "excludePinnedPosts": False,
    "maxProfilesPerQuery": 1,
    "postURLs": ["https://www.tiktok.com/@daniryb_fb/video/7568894968006331666?_r=1&_t=ZS-917ccFrU4Od"],                       # <-- pusta tablica zamiast None
    "scrapeRelatedVideos": False,

    # pola 'shouldDownload*' mogą zostać, ale nie są wymagane
    "shouldDownloadVideos": False,
    "shouldDownloadCovers": False,
    "shouldDownloadSubtitles": False,
    "shouldDownloadSlideshowImages": False,
    "shouldDownloadAvatars": False,
    "shouldDownloadMusicCovers": False,

    # Zostaw None (Python None), a nie string "None". Albo po prostu pomiń ten klucz.
    "proxyCountryCode": "None",
}

# 3) Uruchom aktora (ID który podałeś)
run = client.actor("GdWCkxBtKWOsKjdch").call(run_input=run_input)

# 4) Odczyt wyników – bezpiecznie wyciągnij z różnych możliwych pól
def extract_counts(item: dict):
    # Różne aktory zwracają różne kształty statystyk
    stats = item.get("stats") or item.get("authorStats") or {}
    return {
        "id": item.get("id") or item.get("awemeId") or item.get("videoId"),
        "url": item.get("webVideoUrl") or item.get("url") or item.get("shareUrl"),
        "caption": (item.get("desc") or item.get("text") or "")[:120],
        "views": item.get("playCount") or stats.get("playCount") or stats.get("playCountTotal"),
        "likes": item.get("diggCount") or stats.get("diggCount"),
        "comments": item.get("commentCount") or stats.get("commentCount"),
        "shares": item.get("shareCount") or stats.get("shareCount"),
    }

for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(extract_counts(item))
