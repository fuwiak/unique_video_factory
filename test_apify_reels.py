#!/usr/bin/env python3
"""Utility script to fetch Instagram Reel stats via Apify.

Usage:
    python test_apify_reels.py

The script expects the `APIFY_TOKEN` environment variable to be set. You can
store it in a local `.env` file (see `env.example`) or export it directly
before running the script.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable, List, Optional

from apify_client import ApifyClient
from dotenv import load_dotenv


# Instagram Reels provided by the user for validation.
DEFAULT_REEL_URLS: List[str] = [
    "https://www.instagram.com/reel/DQpG7DhjPEb/?igsh=MW45NTA5ZmlyYjRyYw==",
    "https://www.instagram.com/reel/DQpG2_BjMfc/?igsh=MWFmMTZpMGpmOWg2OQ==",
    "https://www.instagram.com/reel/DQpG053jNwZ/?igsh=MTEzMWFzZmRmaWd6OA==",
]


@dataclass
class ReelStats:
    """Container for a single reel statistics entry."""

    url: str
    shortcode: str
    views: Optional[int]
    likes: Optional[int]
    comments: Optional[int]

    def format_summary(self) -> str:
        return (
            f"{self.shortcode} | {self.url}\n"
            f"  views: {self.views} | likes: {self.likes} | comments: {self.comments}\n"
        )


@dataclass
class ApifyCredentials:
    username: str
    password: Optional[str] = None
    sessionid: Optional[str] = None


def load_client() -> ApifyClient:
    """Initialise an :class:`ApifyClient` from environment variables."""

    load_dotenv()
    token = os.getenv("APIFY_TOKEN")
    if not token:
        raise RuntimeError(
            "APIFY_TOKEN is not configured. Add it to your environment or .env file."
        )
    return ApifyClient(token)


def load_credentials() -> ApifyCredentials:
    username = os.getenv("APIFY_IG_USERNAME")
    password = os.getenv("APIFY_IG_PASSWORD")
    sessionid = os.getenv("APIFY_IG_SESSIONID")

    if not username:
        raise RuntimeError(
            "APIFY_IG_USERNAME is required by the apify/instagram-reel-scraper actor."
            " Set it in your environment or .env file."
        )

    return ApifyCredentials(username=username, password=password, sessionid=sessionid)


def fetch_reel_stats(client: ApifyClient, reel_urls: Iterable[str]) -> List[ReelStats]:
    """Fetch statistics for the provided reel URLs via the Apify actor."""

    urls_list = list(reel_urls)
    credentials = load_credentials()

    actor_input = {
        "username": [credentials.username],
        "reelUrls": urls_list,
        "includeComments": False,
        "maxReelsPerProfile": 0,
    }

    if credentials.password:
        actor_input["password"] = [credentials.password]
    if credentials.sessionid:
        actor_input["sessionid"] = credentials.sessionid

    run = client.actor("apify/instagram-reel-scraper").call(run_input=actor_input)
    dataset = client.dataset(run["defaultDatasetId"])

    results: List[ReelStats] = []
    for item in dataset.iterate_items():
        url = item.get("url") or item.get("reelUrl") or ""
        views = item.get("plays") or item.get("viewCount") or item.get("videoPlayCount")
        likes = item.get("likes")
        comments = item.get("commentsCount") or item.get("comments")
        shortcode = item.get("shortcode") or item.get("id") or "unknown"

        results.append(ReelStats(url=url, shortcode=shortcode, views=views, likes=likes, comments=comments))

    # Ensure every requested URL is represented, even if Apify missed it
    present_urls = {stat.url for stat in results}
    for url in urls_list:
        if url not in present_urls:
            results.append(ReelStats(url=url, shortcode="missing", views=None, likes=None, comments=None))

    return results


def main() -> None:
    client = load_client()
    stats = fetch_reel_stats(client, DEFAULT_REEL_URLS)

    print("📊 Instagram Reel stats fetched via Apify:")
    print("=" * 60)
    for entry in stats:
        print(entry.format_summary())


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - simple helper script
        print(f"❌ Failed to fetch reel stats: {exc}")
        raise

