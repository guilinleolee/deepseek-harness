import re
import unittest
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
BASE = "https://xshuiai.github.io/media-publish-check/"
PAGES = (
    "index.html",
    "douyin-publish-check/index.html",
    "xiaohongshu-publish-check/index.html",
    "ai-content-label-check/index.html",
    "cross-platform-publish-check/index.html",
    "weixin-video-accounts-publish-check/index.html",
    "kuaishou-live-commerce-review/index.html",
    "china-social-media-publish-rules/index.html",
    "for-overseas-creators/index.html",
)


class PublicSiteTests(unittest.TestCase):
    def test_every_discovery_page_has_title_description_and_canonical(self):
        for relative in PAGES:
            with self.subTest(page=relative):
                html = (DOCS / relative).read_text(encoding="utf-8")
                self.assertRegex(html, r"<title>.+?</title>")
                self.assertIn('name="description"', html)
                self.assertIn('rel="canonical"', html)
                self.assertIn(BASE, html)

    def test_sitemap_matches_discovery_pages(self):
        sitemap = (DOCS / "sitemap.xml").read_text(encoding="utf-8")
        locations = re.findall(r"<loc>([^<]+)</loc>", sitemap)
        self.assertEqual(9, len(locations))
        for location in locations:
            relative = urlparse(location).path.removeprefix("/media-publish-check/").strip("/")
            target = DOCS / (relative if relative else "index.html") / "index.html"
            if not relative:
                target = DOCS / "index.html"
            self.assertTrue(target.exists(), f"missing site page for {location}")

    def test_home_links_all_four_task_pages(self):
        home = (DOCS / "index.html").read_text(encoding="utf-8")
        for route in (
            "douyin-publish-check/",
            "xiaohongshu-publish-check/",
            "ai-content-label-check/",
            "cross-platform-publish-check/",
            "weixin-video-accounts-publish-check/",
            "kuaishou-live-commerce-review/",
            "china-social-media-publish-rules/",
            "for-overseas-creators/",
        ):
            self.assertIn(f'href="{route}"', home)

    def test_robots_advertises_the_site_sitemap(self):
        robots = (DOCS / "robots.txt").read_text(encoding="utf-8")
        self.assertIn(f"Sitemap: {BASE}sitemap.xml", robots)


if __name__ == "__main__":
    unittest.main()
