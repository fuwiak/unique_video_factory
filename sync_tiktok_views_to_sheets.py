#!/usr/bin/env python3
"""Synchronise TikTok video views fetched via Apify into Google Sheets.

Usage:
    python sync_tiktok_views_to_sheets.py <tiktok_video_url> [<tiktok_video_url> ...]

Environment:
    - ``APIFY_TOKEN`` must be set (or stored in a local ``.env`` file).
    - Google Sheets credentials must be configured as for ``google_sheets_integration``.

Optional flags:
    --blogger BLOGGER_NAME  # save rows into a dedicated blogger worksheet instead of the default sheet
"""

from __future__ import annotations

import argparse
import os
from typing import Any, Dict, Iterable, List

from apify_client import ApifyClient  # type: ignore[import]
from dotenv import load_dotenv

from google_sheets_integration import GoogleSheetsIntegration


ACTOR_ID = "GdWCkxBtKWOsKjdch"


def load_apify_client() -> ApifyClient:
    """Initialise an ``ApifyClient`` using ``APIFY_TOKEN`` from the environment."""

    load_dotenv()
    token = os.getenv("APIFY_TOKEN")
    if not token:
        raise RuntimeError("APIFY_TOKEN is not configured. Add it to your environment or .env file.")
    return ApifyClient(token)


def build_actor_input(video_urls: Iterable[str]) -> Dict[str, Any]:
    """Prepare a minimal, valid input payload for the TikTok actor."""

    urls = [url for url in video_urls if url]
    if not urls:
        raise ValueError("At least one TikTok video URL must be provided.")

    actor_input: Dict[str, Any] = {
        "resultsPerPage": 1,
        "profiles": [],
        "profileScrapeSections": ["videos"],
        "profileSorting": "latest",
        "excludePinnedPosts": False,
        "maxProfilesPerQuery": 1,
        "postURLs": urls,
        "scrapeRelatedVideos": False,
        "shouldDownloadVideos": False,
        "shouldDownloadCovers": False,
        "shouldDownloadSubtitles": False,
        "shouldDownloadSlideshowImages": False,
        "shouldDownloadAvatars": False,
        "shouldDownloadMusicCovers": False,
    }

    sessionid = os.getenv("APIFY_TT_SESSIONID")
    if sessionid:
        actor_input["sessionid"] = sessionid

    return actor_input


def _collect_urls_from_blogger(blogger_name: str) -> List[str]:
    integration = GoogleSheetsIntegration()
    sheet = integration.get_or_create_blogger_sheet(blogger_name)
    if not sheet:
        return []

    urls: List[str] = []
    for row in sheet.get_all_values()[1:]:  # skip header
        if len(row) > 1:
            url = row[1].strip()
            if url and "tiktok.com" in url:
                urls.append(url)

    # deduplicate preserving order
    seen = set()
    unique_urls: List[str] = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
    return unique_urls


def extract_counts(item: Dict[str, Any]) -> Dict[str, Any]:
    """Normalise the key metrics returned by the Apify dataset."""

    stats = item.get("stats") or item.get("authorStats") or {}
    create_time = (
        item.get("createTimeISO")
        or item.get("createTimeIso")
        or item.get("createTime")
        or stats.get("createTimeISO")
        or stats.get("createTime")
    )

    def _safe_int(value: Any) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    return {
        "id": item.get("id") or item.get("awemeId") or item.get("videoId"),
        "url": item.get("webVideoUrl") or item.get("url") or item.get("shareUrl"),
        "caption": (item.get("desc") or item.get("text") or "")[:120],
        "views": _safe_int(item.get("playCount") or stats.get("playCount") or stats.get("playCountTotal")),
        "likes": _safe_int(item.get("diggCount") or stats.get("diggCount")),
        "comments": _safe_int(item.get("commentCount") or stats.get("commentCount")),
        "shares": _safe_int(item.get("shareCount") or stats.get("shareCount")),
        "create_time": create_time,
    }


def fetch_tiktok_video_stats(client: ApifyClient, video_urls: Iterable[str]) -> List[Dict[str, Any]]:
    """Run the Apify actor and collect stats for the provided TikTok video URLs."""

    actor_input = build_actor_input(video_urls)
    run = client.actor(ACTOR_ID).call(run_input=actor_input)
    dataset = client.dataset(run["defaultDatasetId"])

    results: List[Dict[str, Any]] = [extract_counts(item) for item in dataset.iterate_items()]

    # Ensure every requested URL is represented, even if missing in the dataset
    requested_urls = set(actor_input["postURLs"])
    returned_urls = {entry.get("url") for entry in results if entry.get("url")}

    for url in requested_urls - returned_urls:
        results.append({"url": url, "views": None, "caption": "", "id": None})

    return results


def build_sheet_payload(stats: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    """Convert TikTok stats into the structure expected by ``GoogleSheetsIntegration``."""

    videos: List[Dict[str, Any]] = []
    seen_urls = set()
    for entry in stats:
        views = entry.get("views")
        url = entry.get("url")
        if not url:
            continue

        if url in seen_urls:
            continue
        seen_urls.add(url)

        if views is None:
            videos.append(
                {
                    "url": url,
                    "views": "⚠️ Контент доступен только авторизованным пользователям",
                    "date": entry.get("create_time"),
                }
            )
            continue

        videos.append(
            {
                "url": url,
                "views": views,
                "date": entry.get("create_time"),
            }
        )

    if not videos:
        return {}

    return {
        "TikTok": {
            "platform": "TikTok",
            "videos": videos,
        }
    }


def save_stats_to_sheets(stats: Iterable[Dict[str, Any]], blogger_name: str | None = None) -> bool:
    """Persist TikTok stats to Google Sheets. Returns ``True`` on success."""

    payload = build_sheet_payload(stats)
    if not payload:
        raise RuntimeError("No TikTok data available to write to Google Sheets.")

    integration = GoogleSheetsIntegration()

    if blogger_name:
        return integration.save_to_blogger_sheet(blogger_name, payload)
    return integration.save_to_sheets(payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch TikTok video stats via Apify and write them to Google Sheets.")
    parser.add_argument("urls", nargs="*", help="TikTok video URLs to process. If omitted, use --blogger to pull from sheet.")
    parser.add_argument(
        "--blogger",
        dest="blogger_name",
        help="Optional blogger worksheet name. When provided, data is stored in that worksheet.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = load_apify_client()
    urls = args.urls

    if not urls and args.blogger_name:
        urls = _collect_urls_from_blogger(args.blogger_name)

    if not urls:
        raise RuntimeError("No TikTok URLs provided and blogger sheet had none.")

    stats = fetch_tiktok_video_stats(client, urls)

    success = save_stats_to_sheets(stats, blogger_name=args.blogger_name)
    if success:
        print("✅ TikTok views saved to Google Sheets")
    else:
        print("❌ Failed to save TikTok views to Google Sheets")


if __name__ == "__main__":
    main()

