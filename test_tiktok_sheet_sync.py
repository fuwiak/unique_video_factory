#!/usr/bin/env python3
"""Test helper: sync views for every URL in the specified blogger sheet (all platforms)."""

import argparse

from daily_views_report import DailyViewsReporter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Test syncing views for all platforms in a blogger sheet.")
    parser.add_argument("blogger", help="Sheet title, e.g. 'Нина'")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    reporter = DailyViewsReporter()

    if not reporter.gc:
        raise RuntimeError("Google Sheets not initialised - check credentials.")

    processed = reporter.process_sheet(args.blogger)
    print(f"✅ Przetworzono {processed} unikalnych URL-i z arkusza {args.blogger}")


if __name__ == "__main__":
    main()

