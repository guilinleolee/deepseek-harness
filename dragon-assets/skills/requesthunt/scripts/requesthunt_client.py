#!/usr/bin/env python3
"""
RequestHunt - Multi-platform User Research Engine
Supports: Reddit, X/Twitter, GitHub, YouTube, LinkedIn, Amazon
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, List, Dict

@dataclass
class ResearchResult:
    query: str
    platform: str
    data: list
    sentiment: dict = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.sentiment is None:
            self.sentiment = {"positive": 0, "negative": 0, "neutral": 0}

@dataclass
class SentimentResult:
    topic: str
    overall: dict
    breakdown: dict
    top_positive: list
    top_negative: list

@dataclass
class MonitorResult:
    brands: List[str]
    data: dict
    alerts: list
    trends: dict

class RedditClient:
    """Reddit user research client"""
    BASE_URL = "https://www.reddit.com"
    
    def search(self, query: str, subreddit: str = None, limit: int = 100, sort: str = "hot") -> list:
        if subreddit:
            url = f"{self.BASE_URL}/r/{subreddit}/search.json?q={query}&limit={limit}&sort={sort}"
        else:
            url = f"{self.BASE_URL}/search.json?q={query}&limit={limit}&sort={sort}"
        
        cmd = ["curl", "-s", url, "-H", "User-Agent: requesthunt/1.0"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            data = json.loads(result.stdout)
            posts = []
            for item in data.get("data", {}).get("children", []):
                post = item["data"]
                posts.append({
                    "id": post["id"],
                    "title": post["title"],
                    "score": post["score"],
                    "num_comments": post["num_comments"],
                    "subreddit": post["subreddit"],
                    "author": post["author"],
                    "created_utc": post["created_utc"],
                    "url": post["url"],
                    "selftext": post.get("selftext", "")[:500]
                })
            return posts
        except Exception as e:
            print(f"Reddit search error: {e}", file=sys.stderr)
            return []
    
    def get_comments(self, post_id: str, limit: int = 100, depth: int = 5) -> list:
        url = f"{self.BASE_URL}/r/aww/comments/{post_id}.json?limit={limit}"
        try:
            result = subprocess.run(["curl", "-s", url, "-H", "User-Agent: requesthunt/1.0"],
                                  capture_output=True, text=True, timeout=30)
            data = json.loads(result.stdout)
            comments = []
            def extract_comments(comment_list, current_depth=0):
                if current_depth >= depth:
                    return
                for item in comment_list:
                    if item.get("kind") == "t1":
                        d = item["data"]
                        comments.append({
                            "id": d["id"], "author": d["author"], "body": d["body"],
                            "score": d["score"], "depth": current_depth, "parent_id": d["parent_id"]
                        })
                        if d.get("replies"):
                            extract_comments(d["replies"]["data"]["children"], current_depth + 1)
            if len(data) > 1:
                extract_comments(data[1]["data"]["children"])
            return comments
        except Exception as e:
            print(f"Reddit comments error: {e}", file=sys.stderr)
            return []
    
    def analyze_sentiment(self, posts: list) -> dict:
        pos_kw = ["love", "great", "awesome", "amazing", "excellent", "fantastic", "wonderful", "best", "perfect", "helpful"]
        neg_kw = ["hate", "terrible", "awful", "horrible", "worst", "bad", "useless", "broken", "bug", "crash", "fail", "disappointed"]
        scores = {"positive": 0, "negative": 0, "neutral": 0}
        for post in posts:
            text = (post.get("title", "") + " " + post.get("selftext", "")).lower()
            pos_count = sum(1 for kw in pos_kw if kw in text)
            neg_count = sum(1 for kw in neg_kw if kw in text)
            if pos_count > neg_count:
                scores["positive"] += 1
            elif neg_count > pos_count:
                scores["negative"] += 1
            else:
                scores["neutral"] += 1
        total = len(posts) or 1
        return {k: round(v / total, 3) for k, v in scores.items()}

class TwitterClient:
    """X/Twitter user research client"""
    def __init__(self):
        self.use_xreach = self._check_xreach()
    
    def _check_xreach(self) -> bool:
        try:
            subprocess.run(["xreach", "--version"], capture_output=True, timeout=5)
            return True
        except:
            return False
    
    def search(self, query: str, limit: int = 100) -> list:
        if self.use_xreach:
            cmd = ["xreach", "search", query, "-n", str(limit), "--json"]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                return json.loads(result.stdout) if result.stdout else []
            except Exception as e:
                print(f"xreach error: {e}", file=sys.stderr)
        return [{"note": "Twitter API requires authentication"}]
    
    def get_user_tweets(self, username: str, limit: int = 100) -> list:
        if self.use_xreach:
            cmd = ["xreach", "tweets", f"@{username}", "-n", str(limit), "--json"]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                return json.loads(result.stdout) if result.stdout else []
            except:
                pass
        return []
    
    def analyze_sentiment(self, tweets: list) -> dict:
        pos_kw = ["love", "great", "amazing", "best", "awesome", "good", "excellent", "fantastic", "wonderful", "happy"]
        neg_kw = ["hate", "terrible", "worst", "awful", "bad", "horrible", "disappointed", "angry", "frustrated", "sucks"]
        scores = {"positive": 0, "negative": 0, "neutral": 0}
        for tweet in tweets:
            text = str(tweet.get("text", "")).lower()
            pos_count = sum(1 for kw in pos_kw if kw in text)
            neg_count = sum(1 for kw in neg_kw if kw in text)
            if pos_count > neg_count:
                scores["positive"] += 1
            elif neg_count > pos_count:
                scores["negative"] += 1
            else:
                scores["neutral"] += 1
        total = len(tweets) or 1
        return {k: round(v / total, 3) for k, v in scores.items()}

class GitHubClient:
    """GitHub user research client"""
    def __init__(self):
        self.gh_available = self._check_gh()
    
    def _check_gh(self) -> bool:
        try:
            subprocess.run(["gh", "--version"], capture_output=True, timeout=5)
            return True
        except:
            return False
    
    def search_repos(self, query: str, limit: int = 100) -> list:
        if not self.gh_available:
            return [{"error": "gh CLI not available"}]
        cmd = ["gh", "search", "repos", query, "--sort", "stars", "--limit", str(limit),
                "--json", "name,description,stars,language,url,owner"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return json.loads(result.stdout) if result.stdout else []
        except Exception as e:
            print(f"GitHub search error: {e}", file=sys.stderr)
            return []
    
    def get_issues(self, owner: str, repo: str, state: str = "open", limit: int = 100) -> list:
        if not self.gh_available:
            return []
        cmd = ["gh", "issue", "list", "-R", f"{owner}/{repo}", "--state", state,
                "--limit", str(limit), "--json", "number,title,body,author,labels,createdAt,state"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return json.loads(result.stdout) if result.stdout else []
        except:
            return []
    
    def analyze_sentiment(self, issues: list) -> dict:
        pos_kw = ["great", "awesome", "thank", "love", "perfect", "excellent", "amazing"]
        neg_kw = ["bug", "crash", "broken", "fail", "hate", "terrible", "issue", "problem", "error"]
        feat_kw = ["feature", "request", "would be nice", "suggestion", "enhancement", "improve"]
        scores = {"positive": 0, "negative": 0, "neutral": 0}
        features = []
        for issue in issues:
            text = (issue.get("title", "") + " " + issue.get("body", "")).lower()
            is_feat = any(kw in text for kw in feat_kw)
            pos_count = sum(1 for kw in pos_kw if kw in text)
            neg_count = sum(1 for kw in neg_kw if kw in text)
            if is_feat:
                features.append(issue)
            elif pos_count > neg_count:
                scores["positive"] += 1
            elif neg_count > pos_count:
                scores["negative"] += 1
            else:
                scores["neutral"] += 1
        total = len(issues) or 1
        result = {k: round(v / total, 3) for k, v in scores.items()}
        result["features"] = len(features) / total
        return result

class YouTubeClient:
    """YouTube user research client"""
    def search(self, query: str, limit: int = 50) -> list:
        cmd = ["yt-dlp", "--dump-json", f"ytsearch{limit}:{query}"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            videos = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    try:
                        data = json.loads(line)
                        videos.append({
                            "id": data.get("id"), "title": data.get("title"),
                            "channel": data.get("channel"), "view_count": data.get("view_count", 0),
                            "like_count": data.get("like_count", 0), "duration": data.get("duration"),
                            "upload_date": data.get("upload_date"), "url": data.get("webpage_url")
                        })
                    except:
                        continue
            return videos
        except Exception as e:
            print(f"YouTube search error: {e}", file=sys.stderr)
            return []
    
    def analyze_sentiment(self, videos: list) -> dict:
        if not videos:
            return {"positive": 0, "negative": 0, "neutral": 1}
        pos_count = sum(1 for v in videos if (v.get("like_count", 0) / max(v.get("view_count", 1), 1)) > 0.05)
        total = len(videos)
        neg_or_neutral = total - pos_count
        return {
            "positive": round(pos_count / total, 3),
            "negative": round(neg_or_neutral * 0.3 / total, 3),
            "neutral": round(neg_or_neutral * 0.7 / total, 3)
        }

class LinkedInClient:
    """LinkedIn user research client"""
    def __init__(self):
        self.use_mcporter = self._check_mcporter()
    
    def _check_mcporter(self) -> bool:
        try:
            subprocess.run(["mcporter", "--version"], capture_output=True, timeout=5)
            return True
        except:
            return False
    
    def search_people(self, keyword: str, limit: int = 100) -> list:
        if self.use_mcporter:
            cmd = ["mcporter", "call", f'linkedin.search_people(keyword: "{keyword}", limit: {limit})']
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                return json.loads(result.stdout) if result.stdout else []
            except:
                pass
        return [{"note": "LinkedIn requires mcporter or API access"}]
    
    def get_profile(self, url: str) -> dict:
        if self.use_mcporter:
            cmd = ["mcporter", "call", f'linkedin.get_person_profile(linkedin_url: "{url}")']
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                return json.loads(result.stdout) if result.stdout else {}
            except:
                pass
        return {"error": "mcporter not available"}

class AmazonClient:
    """Amazon user research client"""
    def search_products(self, query: str, limit: int = 50) -> list:
        url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}&ref=nb_sb_noss"
        try:
            cmd = ["curl", "-s", url, "-H", "User-Agent: Mozilla/5.0", "-H", "Accept: text/html"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return [{"query": query, "note": "Amazon has anti-scraping. Use official API or third-party tools."}]
        except Exception as e:
            print(f"Amazon search error: {e}", file=sys.stderr)
            return []
    
    def get_reviews(self, product_asin: str, limit: int = 100) -> list:
        return [{"product": product_asin, "note": "Amazon reviews require API access or scraping partner"}]
    
    def analyze_sentiment(self, reviews: list) -> dict:
        pos_kw = ["great", "excellent", "perfect", "amazing", "wonderful", "love", "best", "good", "awesome"]
        neg_kw = ["terrible", "horrible", "worst", "bad", "broken", "defective", "hate", "disappointed", "poor"]
        scores = {"positive": 0, "negative": 0, "neutral": 0}
        for review in reviews:
            text = str(review.get("text", "")).lower()
            pos_count = sum(1 for kw in pos_kw if kw in text)
            neg_count = sum(1 for kw in neg_kw if kw in text)
            if pos_count > neg_count:
                scores["positive"] += 1
            elif neg_count > pos_count:
                scores["negative"] += 1
            else:
                scores["neutral"] += 1
        total = len(reviews) or 1
        return {k: round(v / total, 3) for k, v in scores.items()}

class RequestHunt:
    """Multi-platform User Research Engine"""
    PLATFORMS = ["reddit", "twitter", "github", "youtube", "linkedin", "amazon"]
    
    def __init__(self):
        self.reddit = RedditClient()
        self.twitter = TwitterClient()
        self.github = GitHubClient()
        self.youtube = YouTubeClient()
        self.linkedin = LinkedInClient()
        self.amazon = AmazonClient()
    
    def research(self, query: str, platforms: list = None, limit: int = 100) -> dict:
        if platforms is None:
            platforms = self.PLATFORMS
        results = {"query": query, "platforms": platforms, "timestamp": datetime.now().isoformat(), "data": {}}
        for platform in platforms:
            if platform not in self.PLATFORMS:
                continue
            try:
                if platform == "reddit":
                    posts = self.reddit.search(query, limit=limit)
                    sentiment = self.reddit.analyze_sentiment(posts)
                    results["data"]["reddit"] = {"posts": posts, "sentiment": sentiment, "count": len(posts)}
                elif platform == "twitter":
                    tweets = self.twitter.search(query, limit=limit)
                    sentiment = self.twitter.analyze_sentiment(tweets)
                    results["data"]["twitter"] = {"tweets": tweets, "sentiment": sentiment, "count": len(tweets)}
                elif platform == "github":
                    repos = self.github.search_repos(query, limit=limit)
                    results["data"]["github"] = {"repos": repos, "count": len(repos)}
                elif platform == "youtube":
                    videos = self.youtube.search(query, limit=limit)
                    sentiment = self.youtube.analyze_sentiment(videos)
                    results["data"]["youtube"] = {"videos": videos, "sentiment": sentiment, "count": len(videos)}
                elif platform == "linkedin":
                    people = self.linkedin.search_people(query, limit=limit)
                    results["data"]["linkedin"] = {"people": people, "count": len(people)}
                elif platform == "amazon":
                    products = self.amazon.search_products(query, limit=limit)
                    results["data"]["amazon"] = {"products": products, "count": len(products)}
            except Exception as e:
                print(f"Error researching {platform}: {e}", file=sys.stderr)
                results["data"][platform] = {"error": str(e)}
        return results
    
    def sentiment(self, topic: str, platforms: list = None, time_range: str = "30d") -> SentimentResult:
        if platforms is None:
            platforms = self.PLATFORMS
        research_data = self.research(topic, platforms=platforms, limit=200)
        all_sentiments = []
        breakdown = {}
        for platform in platforms:
            if platform in research_data["data"]:
                platform_data = research_data["data"][platform]
                if "sentiment" in platform_data:
                    sentiment = platform_data["sentiment"]
                    breakdown[platform] = sentiment
                    all_sentiments.append(sentiment)
        if all_sentiments:
            overall = {
                "positive": sum(s.get("positive", 0) for s in all_sentiments) / len(all_sentiments),
                "negative": sum(s.get("negative", 0) for s in all_sentiments) / len(all_sentiments),
                "neutral": sum(s.get("neutral", 0) for s in all_sentiments) / len(all_sentiments)
            }
        else:
            overall = {"positive": 0, "negative": 0, "neutral": 1}
        return SentimentResult(topic=topic, overall=overall, breakdown=breakdown, top_positive=[], top_negative=[])
    
    def monitor(self, brands: list, platforms: list = None, alert: bool = False) -> MonitorResult:
        if platforms is None:
            platforms = ["reddit", "twitter", "github"]
        data, alerts, trends = {}, [], {}
        for brand in brands:
            brand_data = self.research(brand, platforms=platforms, limit=100)
            data[brand] = brand_data["data"]
            for platform in platforms:
                if platform in brand_data["data"]:
                    sentiment = brand_data["data"][platform].get("sentiment", {})
                    if sentiment.get("negative", 0) > 0.4:
                        alerts.append({"brand": brand, "platform": platform, "type": "negative_spike", "sentiment": sentiment})
            trends[brand] = {"mentions": sum(brand_data["data"].get(p, {}).get("count", 0) for p in platforms)}
        return MonitorResult(brands=brands, data=data, alerts=alerts, trends=trends)
    
    def reviews(self, product: str, platform: str = "amazon", limit: int = 200) -> list:
        if platform == "amazon":
            products = self.amazon.search_products(product, limit=10)
            if products and len(products) > 0:
                asin = products[0].get("asin", "")
                if asin:
                    return self.amazon.get_reviews(asin, limit=limit)
        research_data = self.research(product, platforms=[platform], limit=limit)
        return research_data.get("data", {}).get(platform, {}).get("posts", [])
    
    def export_json(self, data: dict, output_file: str):
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Exported to {output_file}")
    
    def export_markdown(self, data: dict, output_file: str):
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# Research Report: {data.get('query', 'Unknown')}\n\n")
            f.write(f"**Generated:** {data.get('timestamp', 'N/A')}\n\n")
            f.write(f"**Platforms:** {', '.join(data.get('platforms', []))}\n\n---\n\n")
            for platform, platform_data in data.get("data", {}).items():
                f.write(f"## {platform.title()}\n\n")
                if "error" in platform_data:
                    f.write(f"**Error:** {platform_data['error']}\n\n")
                    continue
                count = platform_data.get("count", 0)
                f.write(f"**Results:** {count} items\n\n")
                if "sentiment" in platform_data:
                    s = platform_data["sentiment"]
                    f.write(f"- Positive: {s.get('positive', 0):.1%}\n")
                    f.write(f"- Negative: {s.get('negative', 0):.1%}\n")
                    f.write(f"- Neutral: {s.get('neutral', 0):.1%}\n\n")
                f.write("---\n\n")
        print(f"Exported to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="RequestHunt - Multi-platform User Research Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n  %(prog)s research \"Claude AI\" --platforms reddit,twitter --limit 100\n  %(prog)s sentiment \"Tesla FSD\" --platforms all\n  %(prog)s monitor \"Apple,Samsung\" --platforms twitter,reddit --alert on\n  %(prog)s reviews \"MacBook Pro\" --platform amazon")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    research_parser = subparsers.add_parser("research", help="Multi-platform research")
    research_parser.add_argument("query", help="Research topic/keyword")
    research_parser.add_argument("--platforms", default="all", help="Comma-separated platforms")
    research_parser.add_argument("--limit", type=int, default=100, help="Results per platform")
    research_parser.add_argument("--output", "-o", help="Output file (JSON or MD)")
    
    sentiment_parser = subparsers.add_parser("sentiment", help="Sentiment analysis")
    sentiment_parser.add_argument("topic", help="Topic to analyze")
    sentiment_parser.add_argument("--platforms", default="all", help="Comma-separated platforms")
    sentiment_parser.add_argument("--time-range", default="30d", help="Time range")
    sentiment_parser.add_argument("--output", "-o", help="Output file")
    
    monitor_parser = subparsers.add_parser("monitor", help="Competitor monitoring")
    monitor_parser.add_argument("brands", help="Comma-separated brand names")
    monitor_parser.add_argument("--platforms", default="reddit,twitter,github", help="Comma-separated platforms")
    monitor_parser.add_argument("--alert", choices=["on", "off"], default="off")
    monitor_parser.add_argument("--output", "-o", help="Output file")
    
    reviews_parser = subparsers.add_parser("reviews", help="Review collection")
    reviews_parser.add_argument("product", help="Product name")
    reviews_parser.add_argument("--platform", default="amazon", choices=["amazon", "reddit", "youtube"])
    reviews_parser.add_argument("--limit", type=int, default=200)
    reviews_parser.add_argument("--output", "-o", help="Output file")
    
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    hunt = RequestHunt()
    if args.command == "research":
        platforms = args.platforms.split(",") if args.platforms != "all" else None
        result = hunt.research(args.query, platforms=platforms, limit=args.limit)
        if args.output:
            hunt.export_markdown(result, args.output) if args.output.endswith(".md") else hunt.export_json(result, args.output)
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "sentiment":
        platforms = args.platforms.split(",") if args.platforms != "all" else None
        result = hunt.sentiment(args.topic, platforms=platforms, time_range=args.time_range)
        output = asdict(result)
        if args.output:
            hunt.export_json(output, args.output)
        else:
            print(json.dumps(output, ensure_ascii=False, indent=2))
    elif args.command == "monitor":
        brands = args.brands.split(",")
        platforms = args.platforms.split(",")
        result = hunt.monitor(brands=brands, platforms=platforms, alert=args.alert == "on")
        output = asdict(result)
        if args.output:
            hunt.export_json(output, args.output)
        else:
            print(json.dumps(output, ensure_ascii=False, indent=2))
    elif args.command == "reviews":
        result = hunt.reviews(args.product, platform=args.platform, limit=args.limit)
        if args.output:
            hunt.export_json(result, args.output)
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
