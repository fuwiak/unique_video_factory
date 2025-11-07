#!/usr/bin/env python3
"""Quick helper that pushes TikTok video views straight into Google Sheets.

Usage examples:
    python add_tiktok_views_to_sheets.py --url https://www.tiktok.com/@user/video/123
    python add_tiktok_views_to_sheets.py --url ... --blogger "Имя блогера"

If you omit ``--url`` the script will look for comma-separated URLs in the
``TIKTOK_VIDEO_URLS`` environment variable.

Prerequisites:
- ``APIFY_TOKEN`` must be configured (environment or .env file).
- Google Sheets credentials must be set up as for ``google_sheets_integration``.
"""

from __future__ import annotations

import argparse
import os
from typing import Iterable, List

from dotenv import load_dotenv

from sync_tiktok_views_to_sheets import (  # type: ignore[import]
    fetch_tiktok_video_stats,
    load_apify_client,
    save_stats_to_sheets,
)
from google_sheets_integration import GoogleSheetsIntegration


def _gather_urls(url_args: Iterable[str], blogger_name: str | None = None) -> List[str]:
    urls = list(url_args)
    collected_from_blogger: List[str] = []

    # Jeśli nie podano URL-i wprost, a wskazano arkusz blogera, zbieramy je stamtąd
    if not urls and blogger_name:
        integration = GoogleSheetsIntegration()
        sheet = integration.get_or_create_blogger_sheet(blogger_name)
        if sheet:
            rows = sheet.get_all_values()
            # Kolumna "Видео" to zwykle index 1
            for row in rows[1:]:  # pomijamy nagłówki
                if len(row) > 1:
                    video_url = row[1].strip()
                    if video_url and "tiktok.com" in video_url:
                        collected_from_blogger.append(video_url)

    if collected_from_blogger:
        urls = collected_from_blogger

    if urls:
        # Usuwamy duplikaty zachowując kolejność
        seen = set()
        unique = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique.append(url)
        return unique

    env_urls = os.getenv("TIKTOK_VIDEO_URLS", "").strip()
    if not env_urls:
        raise RuntimeError(
            "No TikTok URLs provided. Pass them via --url or set TIKTOK_VIDEO_URLS."
        )

    return [part.strip() for part in env_urls.split(",") if part.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch TikTok views via Apify and append them to Google Sheets."
    )
    parser.add_argument(
        "--url",
        dest="urls",
        action="append",
        help="TikTok video URL. Repeat the flag for multiple URLs.",
    )
    parser.add_argument(
        "--blogger",
        dest="blogger_name",
        help="Optional blogger worksheet name for Google Sheets.",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()
    urls = _gather_urls(args.urls or [], blogger_name=args.blogger_name)

    client = load_apify_client()
    stats = fetch_tiktok_video_stats(client, urls)
    try:
        success = save_stats_to_sheets(stats, blogger_name=args.blogger_name)
    except RuntimeError as exc:
        print(f"⚠️ {exc}")
        success = False

    if success:
        print("✅ TikTok views appended to Google Sheets")
    else:
        print("❌ Failed to append TikTok views to Google Sheets")


if __name__ == "__main__":
    main()

