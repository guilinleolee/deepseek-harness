# -*- coding: utf-8 -*-
"""Simple test for web-scraping-scrapling"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from core.fetcher import ScraplingFetcher

def main():
    print("=" * 50)
    print("Web Scraping SKILL - Simple Test")
    print("=" * 50)

    # Test 1: Create fetcher
    print("\n[TEST 1] Create ScraplingFetcher")
    try:
        fetcher = ScraplingFetcher()
        print("[PASS] Fetcher created successfully")
    except Exception as e:
        print(f"[FAIL] {e}")
        return

    # Test 2: Fetch single page
    print("\n[TEST 2] Fetch single page (example.com)")
    try:
        result = fetcher.fetch_single('https://example.com')
        print(f"[PASS] Page fetched successfully")
        print(f"  - Content length: {len(result)} characters")
        print(f"  - Preview: {result[:100]}...")
    except Exception as e:
        print(f"[FAIL] {e}")
        return

    # Test 3: Print stats
    print("\n[TEST 3] Performance statistics")
    stats = fetcher.get_stats()
    print(f"[INFO] Stats: {stats}")

    print("\n" + "=" * 50)
    print("All tests completed successfully!")
    print("=" * 50)

if __name__ == "__main__":
    main()
