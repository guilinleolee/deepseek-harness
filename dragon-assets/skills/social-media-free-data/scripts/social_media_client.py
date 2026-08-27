#!/usr/bin/env python3
"""
Social Media Free Data Client - Reddit API + TikTok API 客户端
来源: 天龙引擎 V11.13 免费API替代方案
文档: skills/social-media-free-data/SKILL.md
"""

import os
import json
import time
import re
from typing import Optional, Literal
from dataclasses import dataclass
from datetime import datetime

try:
    import requests
except ImportError:
    print("请安装 requests: pip install requests")
    exit(1)


@dataclass
class RedditPost:
    """Reddit帖子数据结构"""
    id: str
    title: str
    content: str
    author: str
    subreddit: str
    score: int
    num_comments: int
    url: str
    permalink: str
    created_utc: float
    flair: Optional[str] = None
    media_url: Optional[str] = None
    is_self: bool = True

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "author": self.author,
            "subreddit": self.subreddit,
            "score": self.score,
            "num_comments": self.num_comments,
            "url": self.url,
            "permalink": self.permalink,
            "created_utc": self.created_utc,
            "created_at": datetime.fromtimestamp(self.created_utc).isoformat(),
            "flair": self.flair,
            "media_url": self.media_url,
            "is_self": self.is_self
        }


@dataclass
class RedditComment:
    """Reddit评论数据结构"""
    id: str
    parent_id: str
    content: str
    author: str
    score: int
    created_utc: float
    depth: int
    replies: list = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "parent_id": self.parent_id,
            "content": self.content,
            "author": self.author,
            "score": self.score,
            "created_utc": self.created_utc,
            "created_at": datetime.fromtimestamp(self.created_utc).isoformat(),
            "depth": self.depth,
            "replies": [r.to_dict() if hasattr(r, 'to_dict') else r for r in (self.replies or [])]
        }


@dataclass
class TikTokVideo:
    """TikTok视频数据结构"""
    id: str
    title: str
    author: str
    author_id: str
    description: str
    create_time: int
    share_count: int
    comment_count: int
    play_count: int
    download_url: str
    cover_image: str
    hashtags: list = None
    mentions: list = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "author_id": self.author_id,
            "description": self.description,
            "create_time": self.create_time,
            "created_at": datetime.fromtimestamp(self.create_time).isoformat() if self.create_time else None,
            "share_count": self.share_count,
            "comment_count": self.comment_count,
            "play_count": self.play_count,
            "download_url": self.download_url,
            "cover_image": self.cover_image,
            "hashtags": self.hashtags or [],
            "mentions": self.mentions or []
        }


class SocialMediaError(Exception):
    """社交媒体API异常"""
    pass


class SocialMediaClient:
    """
    社交媒体数据客户端 - Reddit API + TikTok API

    使用方式:
        client = SocialMediaClient()  # 使用环境变量
        client = SocialMediaClient(reddit_token="xxx")  # 显式指定

    环境变量:
        REDDIT_CLIENT_ID: Reddit应用客户端ID
        REDDIT_CLIENT_SECRET: Reddit应用客户端密钥
        TIKTOK_ACCESS_TOKEN: TikTok API访问令牌

    免费额度:
        Reddit: 无限制 (需要Reddit账号创建应用)
        TikTok Data API: 500请求/天 (需要TikTok for Developers注册)
    """

    REDDIT_BASE_URL = "https://www.reddit.com"
    REDDIT_API_URL = "https://oauth.reddit.com"

    TIKTOK_API_URL = "https://open.tiktokapis.com/v2"

    def __init__(
        self,
        reddit_client_id: Optional[str] = None,
        reddit_client_secret: Optional[str] = None,
        reddit_username: Optional[str] = None,
        reddit_password: Optional[str] = None,
        tiktok_access_token: Optional[str] = None,
        use_cache: bool = True,
        cache_ttl: int = 300
    ):
        self.reddit_client_id = reddit_client_id or os.getenv("REDDIT_CLIENT_ID")
        self.reddit_client_secret = reddit_client_secret or os.getenv("REDDIT_CLIENT_SECRET")
        self.reddit_username = reddit_username or os.getenv("REDDIT_USERNAME")
        self.reddit_password = reddit_password or os.getenv("REDDIT_PASSWORD")
        self.tiktok_access_token = tiktok_access_token or os.getenv("TIKTOK_ACCESS_TOKEN")

        self.use_cache = use_cache
        self.cache_ttl = cache_ttl
        self._cache = {}
        self._reddit_token = None
        self._reddit_token_expiry = 0

        if not self.reddit_client_id and not self.tiktok_access_token:
            raise SocialMediaError(
                "需要设置以下环境变量之一:\n"
                "  Reddit: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD\n"
                "  TikTok: TIKTOK_ACCESS_TOKEN\n\n"
                "获取地址:\n"
                "  Reddit: https://www.reddit.com/prefs/apps\n"
                "  TikTok: https://developers.tiktok.com/"
            )

    def _check_cache(self, key: str) -> Optional[list]:
        """检查缓存"""
        if not self.use_cache:
            return None
        if key in self._cache:
            cached, timestamp = self._cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return cached
        return None

    def _set_cache(self, key: str, data: list):
        """设置缓存"""
        if self.use_cache:
            self._cache[key] = (data, time.time())

    def _get_reddit_token(self) -> str:
        """获取Reddit访问令牌"""
        if self._reddit_token and time.time() < self._reddit_token_expiry:
            return self._reddit_token

        if not self.reddit_client_id or not self.reddit_client_secret:
            raise SocialMediaError("需要REDDIT_CLIENT_ID和REDDIT_CLIENT_SECRET")

        auth = requests.auth.HTTPBasicAuth(self.reddit_client_id, self.reddit_client_secret)

        data = {
            "grant_type": "password",
            "username": self.reddit_username,
            "password": self.reddit_password
        }

        headers = {"User-Agent": "TianlongEngine/1.0 SocialMediaClient/1.0"}

        try:
            resp = requests.post(
                f"{self.REDDIT_BASE_URL}/api/v1/access_token",
                auth=auth,
                data=data,
                headers=headers,
                timeout=10
            )
            resp.raise_for_status()
            token_data = resp.json()

            self._reddit_token = token_data["access_token"]
            self._reddit_token_expiry = time.time() + token_data.get("expires_in", 3600) - 60

            return self._reddit_token

        except requests.RequestException as e:
            raise SocialMediaError(f"Reddit认证失败: {e}")

    def _reddit_headers(self) -> dict:
        """获取Reddit请求头"""
        token = self._get_reddit_token()
        return {
            "Authorization": f"Bearer {token}",
            "User-Agent": "TianlongEngine/1.0 SocialMediaClient/1.0"
        }

    def _parse_reddit_post(self, post: dict) -> RedditPost:
        """解析Reddit帖子"""
        data = post.get("data", post)

        # 提取媒体URL
        media_url = None
        if data.get("is_video") and data.get("media"):
            media_url = data["media"].get("reddit_video", {}).get("dash_url")
        elif data.get("url"):
            url = data["url"]
            if any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                media_url = url
            elif data.get("preview") and data.get("preview", {}).get("images"):
                images = data["preview"]["images"]
                if images and images[0].get("source"):
                    media_url = images[0]["source"].get("url")

        return RedditPost(
            id=data.get("id", ""),
            title=data.get("title", ""),
            content=data.get("selftext", ""),
            author=data.get("author", "[deleted]"),
            subreddit=data.get("subreddit", ""),
            score=data.get("score", 0),
            num_comments=data.get("num_comments", 0),
            url=data.get("url", ""),
            permalink=data.get("permalink", ""),
            created_utc=data.get("created_utc", 0),
            flair=data.get("link_flair_text"),
            media_url=media_url,
            is_self=data.get("is_self", True)
        )

    def _parse_reddit_comment(self, comment: dict, depth: int = 0) -> RedditComment:
        """递归解析Reddit评论"""
        data = comment.get("data", comment)

        if data.get("body") == "[deleted]":
            return None

        replies = []
        if data.get("replies") and isinstance(data["replies"], dict):
            for reply in data["replies"]["data"]["children"]:
                reply_comment = self._parse_reddit_comment(reply, depth + 1)
                if reply_comment:
                    replies.append(reply_comment)

        return RedditComment(
            id=data.get("id", ""),
            parent_id=data.get("parent_id", ""),
            content=data.get("body", ""),
            author=data.get("author", "[deleted]"),
            score=data.get("score", 0),
            created_utc=data.get("created_utc", 0),
            depth=depth,
            replies=replies
        )

    def reddit_search(
        self,
        query: str,
        subreddit: Optional[str] = None,
        sort: Literal["relevance", "hot", "top", "new", "comments"] = "relevance",
        time_filter: Literal["hour", "day", "week", "month", "year", "all"] = "month",
        limit: int = 25
    ) -> list[RedditPost]:
        """
        搜索Reddit帖子

        参数:
            query: 搜索关键词
            subreddit: 限定子版块 (可选)
            sort: 排序方式 (relevance, hot, top, new, comments)
            time_filter: 时间范围 (hour, day, week, month, year, all)
            limit: 返回数量

        返回:
            RedditPost列表
        """
        cache_key = f"reddit_search_{query}_{subreddit}_{sort}_{time_filter}_{limit}"
        cached = self._check_cache(cache_key)
        if cached:
            return [RedditPost(**p) if isinstance(p, dict) else p for p in cached]

        params = {
            "q": query,
            "sort": sort,
            "t": time_filter,
            "limit": min(limit, 100)
        }

        endpoint = "/search"
        if subreddit:
            endpoint = f"/r/{subreddit}/search"
            params["restrict_sr"] = "on"

        try:
            resp = requests.get(
                f"{self.REDDIT_API_URL}{endpoint}",
                params=params,
                headers=self._reddit_headers(),
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()

            posts = [self._parse_reddit_post(p) for p in data.get("data", {}).get("children", [])]
            posts = [p for p in posts if p.title]  # 过滤空帖子

            self._set_cache(cache_key, [p.to_dict() for p in posts])
            return posts

        except requests.RequestException as e:
            raise SocialMediaError(f"Reddit搜索失败: {e}")

    def reddit_hot(self, subreddit: str, limit: int = 25) -> list[RedditPost]:
        """
        获取子版块热门帖子

        参数:
            subreddit: 子版块名称 (不含r/)
            limit: 返回数量

        返回:
            RedditPost列表
        """
        cache_key = f"reddit_hot_{subreddit}_{limit}"
        cached = self._check_cache(cache_key)
        if cached:
            return [RedditPost(**p) if isinstance(p, dict) else p for p in cached]

        try:
            resp = requests.get(
                f"{self.REDDIT_API_URL}/r/{subreddit}/hot",
                params={"limit": min(limit, 100)},
                headers=self._reddit_headers(),
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()

            posts = [self._parse_reddit_post(p) for p in data.get("data", {}).get("children", [])]

            self._set_cache(cache_key, [p.to_dict() for p in posts])
            return posts

        except requests.RequestException as e:
            raise SocialMediaError(f"Reddit获取热门失败: {e}")

    def reddit_comments(
        self,
        post_id: str,
        subreddit: str,
        limit: int = 100,
        depth: int = None
    ) -> list[RedditComment]:
        """
        获取帖子评论

        参数:
            post_id: 帖子ID
            subreddit: 子版块名称
            limit: 评论数量限制
            depth: 最大深度 (可选)

        返回:
            RedditComment列表
        """
        cache_key = f"reddit_comments_{post_id}_{limit}"
        cached = self._check_cache(cache_key)
        if cached:
            return [RedditComment(**c) if isinstance(c, dict) else c for c in cached]

        params = {"limit": min(limit, 500)}
        if depth is not None:
            params["depth"] = depth

        try:
            resp = requests.get(
                f"{self.REDDIT_API_URL}/r/{subreddit}/comments/{post_id}",
                params=params,
                headers=self._reddit_headers(),
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()

            # 评论在第二个元素中
            comments_data = data[1] if len(data) > 1 else data[0]
            comments = []

            for comment in comments_data.get("data", {}).get("children", []):
                parsed = self._parse_reddit_comment(comment)
                if parsed:
                    comments.append(parsed)

            self._set_cache(cache_key, [c.to_dict() for c in comments])
            return comments

        except requests.RequestException as e:
            raise SocialMediaError(f"Reddit获取评论失败: {e}")

    def reddit_subreddit_info(self, subreddit: str) -> dict:
        """获取子版块信息"""
        cache_key = f"reddit_subreddit_{subreddit}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached

        try:
            resp = requests.get(
                f"{self.REDDIT_API_URL}/r/{subreddit}/about",
                headers=self._reddit_headers(),
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json().get("data", {})

            info = {
                "name": data.get("display_name"),
                "title": data.get("title"),
                "description": data.get("description"),
                "subscribers": data.get("subscribers", 0),
                "active_users": data.get("active_user_count", 0),
                "created_utc": data.get("created_utc"),
                "public_description": data.get("public_description"),
                "icon_img": data.get("icon_img"),
                "banner_img": data.get("banner_img")
            }

            self._cache[cache_key] = (info, time.time())  # 永久缓存子版块信息
            return info

        except requests.RequestException as e:
            raise SocialMediaError(f"Reddit获取子版块信息失败: {e}")

    def tiktok_fetch(
        self,
        username: str,
        count: int = 20,
        fields: str = "video_id,video_description,video_create_time,video_share_count,video_comment_count,video_play_count,video_cover_image_url,video_download_addr"
    ) -> list[TikTokVideo]:
        """
        获取TikTok用户视频 (需要TikTok for Developers)

        参数:
            username: TikTok用户名
            count: 返回数量
            fields: 请求字段

        返回:
            TikTokVideo列表
        """
        if not self.tiktok_access_token:
            raise SocialMediaError(
                "需要TIKTOK_ACCESS_TOKEN\n"
                "获取地址: https://developers.tiktok.com/"
            )

        cache_key = f"tiktok_user_{username}_{count}"
        cached = self._check_cache(cache_key)
        if cached:
            return [TikTokVideo(**v) if isinstance(v, dict) else v for v in cached]

        headers = {
            "Authorization": f"Bearer {self.tiktok_access_token}",
            "Content-Type": "application/json"
        }

        query = """
        query userinfo($username: String) {
            userinfo(username: $username) {
                user_id
            }
        }
        """

        try:
            # 先获取用户ID
            resp = requests.post(
                f"{self.TIKTOK_API_URL}/query/",
                headers=headers,
                json={"query": query, "variables": {"username": username}},
                timeout=10
            )
            resp.raise_for_status()
            user_data = resp.json()

            if user_data.get("data", {}).get("userinfo"):
                user_id = user_data["data"]["userinfo"]["user_id"]
            else:
                raise SocialMediaError(f"未找到用户: {username}")

            # 获取视频列表
            videos_query = """
            query user_videos($user_id: String, $count: Int, $fields: String) {
                user_videos(user_id: $user_id, max_count: $count) {
                    videos {
                        %(fields)s
                    }
                }
            }
            """ % {"fields": fields}

            resp = requests.post(
                f"{self.TIKTOK_API_URL}/query/",
                headers=headers,
                json={
                    "query": videos_query,
                    "variables": {
                        "user_id": user_id,
                        "count": min(count, 50),
                        "fields": fields
                    }
                },
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()

            videos = []
            for v in data.get("data", {}).get("user_videos", {}).get("videos", []):
                # 提取话题标签
                description = v.get("video_description", "")
                hashtags = re.findall(r'#(\w+)', description)
                mentions = re.findall(r'@(\w+)', description)

                videos.append(TikTokVideo(
                    id=v.get("video_id", ""),
                    title=description[:100] if description else "",
                    author=username,
                    author_id=user_id,
                    description=description,
                    create_time=v.get("video_create_time", 0),
                    share_count=v.get("video_share_count", 0),
                    comment_count=v.get("video_comment_count", 0),
                    play_count=v.get("video_play_count", 0),
                    download_url=v.get("video_download_addr", {}).get("url_list", [None])[0] or "",
                    cover_image=v.get("video_cover_image_url", ""),
                    hashtags=hashtags,
                    mentions=mentions
                ))

            self._set_cache(cache_key, [v.to_dict() for v in videos])
            return videos

        except requests.RequestException as e:
            raise SocialMediaError(f"TikTok获取视频失败: {e}")

    def tiktok_search(
        self,
        query: str,
        count: int = 20
    ) -> list[TikTokVideo]:
        """
        搜索TikTok视频 (需要TikTok for Developers)

        参数:
            query: 搜索关键词
            count: 返回数量

        返回:
            TikTokVideo列表
        """
        if not self.tiktok_access_token:
            raise SocialMediaError(
                "需要TIKTOK_ACCESS_TOKEN\n"
                "获取地址: https://developers.tiktok.com/"
            )

        cache_key = f"tiktok_search_{query}_{count}"
        cached = self._check_cache(cache_key)
        if cached:
            return [TikTokVideo(**v) if isinstance(v, dict) else v for v in cached]

        headers = {
            "Authorization": f"Bearer {self.tiktok_access_token}",
            "Content-Type": "application/json"
        }

        search_query = """
        query search($query: String, $count: Int) {
            video_search(query: $query, max_count: $count) {
                videos {
                    video_id
                    video_description
                    video_create_time
                    video_share_count
                    video_comment_count
                    video_play_count
                    video_cover_image_url
                    video_download_addr
                    author {
                        user_id
                        nickname
                    }
                }
            }
        }
        """

        try:
            resp = requests.post(
                f"{self.TIKTOK_API_URL}/query/",
                headers=headers,
                json={
                    "query": search_query,
                    "variables": {
                        "query": query,
                        "count": min(count, 50)
                    }
                },
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()

            videos = []
            for v in data.get("data", {}).get("video_search", {}).get("videos", []):
                description = v.get("video_description", "")
                hashtags = re.findall(r'#(\w+)', description)
                mentions = re.findall(r'@(\w+)', description)
                author = v.get("author", {})

                videos.append(TikTokVideo(
                    id=v.get("video_id", ""),
                    title=description[:100] if description else "",
                    author=author.get("nickname", ""),
                    author_id=author.get("user_id", ""),
                    description=description,
                    create_time=v.get("video_create_time", 0),
                    share_count=v.get("video_share_count", 0),
                    comment_count=v.get("video_comment_count", 0),
                    play_count=v.get("video_play_count", 0),
                    download_url=v.get("video_download_addr", {}).get("url_list", [None])[0] or "",
                    cover_image=v.get("video_cover_image_url", ""),
                    hashtags=hashtags,
                    mentions=mentions
                ))

            self._set_cache(cache_key, [v.to_dict() for v in videos])
            return videos

        except requests.RequestException as e:
            raise SocialMediaError(f"TikTok搜索失败: {e}")

    def to_json(self, data: list) -> str:
        """转换为JSON格式"""
        return json.dumps([item.to_dict() for item in data], ensure_ascii=False, indent=2)


def main():
    """CLI入口"""
    import argparse

    parser = argparse.ArgumentParser(description="社交媒体数据客户端 - Reddit + TikTok")
    parser.add_argument("--platform", choices=["reddit", "tiktok", "all"], default="reddit", help="平台")
    parser.add_argument("--search", "-s", help="搜索关键词")
    parser.add_argument("--subreddit", "-r", help="Reddit子版块")
    parser.add_argument("--username", "-u", help="TikTok用户名")
    parser.add_argument("--hot", action="store_true", help="获取热门帖子")
    parser.add_argument("--comments", help="获取评论 (帖子ID)")
    parser.add_argument("--count", type=int, default=10, help="返回数量")
    parser.add_argument("--format", "-f", choices=["json", "text"], default="text", help="输出格式")
    parser.add_argument("--no-cache", action="store_true", help="禁用缓存")

    args = parser.parse_args()

    try:
        client = SocialMediaClient(use_cache=not args.no_cache)

        if args.platform in ["reddit", "all"]:
            if args.hot:
                if not args.subreddit:
                    print("❌ 需要指定--subreddit/-r")
                    return
                posts = client.reddit_hot(args.subreddit, limit=args.count)
                print(f"📊 r/{args.subreddit} 热门帖子")

            elif args.search:
                posts = client.reddit_search(
                    args.search,
                    subreddit=args.subreddit,
                    limit=args.count
                )
                print(f"🔍 Reddit搜索结果: {args.search}")

            elif args.comments:
                if not args.subreddit:
                    print("❌ 需要指定--subreddit/-r")
                    return
                comments = client.reddit_comments(args.comments, args.subreddit, limit=args.count)

                if args.format == "json":
                    print(client.to_json(comments))
                else:
                    print(f"💬 评论 (共{len(comments)}条)")
                    for c in comments:
                        indent = "  " * c.depth
                        print(f"\n{indent}👤 {c.author} ({c.score} upvotes)")
                        print(f"{indent}{c.content[:200]}...")

                return

            else:
                posts = client.reddit_hot("technology", limit=args.count)
                print("📊 技术类热门帖子")

            if args.format == "json":
                print(client.to_json(posts))
            else:
                for i, post in enumerate(posts, 1):
                    print(f"\n{i}. {post.title}")
                    print(f"   r/{post.subreddit} | 👤 {post.author} | ⬆️ {post.score} | 💬 {post.num_comments}")
                    if post.content and len(post.content) > 100:
                        print(f"   {post.content[:100]}...")
                    print(f"   链接: https://reddit.com{post.permalink}")

        if args.platform in ["tiktok", "all"]:
            if not args.username:
                print("\n❌ TikTok需要指定--username/-u")
                return

            if not os.getenv("TIKTOK_ACCESS_TOKEN"):
                print("\n❌ 需要设置TIKTOK_ACCESS_TOKEN环境变量")
                print("   获取地址: https://developers.tiktok.com/")
                return

            if args.search:
                videos = client.tiktok_search(args.search, count=args.count)
                print(f"\n🔍 TikTok搜索结果: {args.search}")
            else:
                videos = client.tiktok_fetch(args.username, count=args.count)
                print(f"\n📹 @{args.username} 的视频")

            if args.format == "json":
                print(client.to_json(videos))
            else:
                for i, video in enumerate(videos, 1):
                    print(f"\n{i}. {video.title or '无标题'}")
                    print(f"   👤 @{video.author}")
                    print(f"   播放: {video.play_count} | 评论: {video.comment_count} | 分享: {video.share_count}")
                    if video.hashtags:
                        print(f"   标签: {' '.join(['#'+h for h in video.hashtags[:5]])}")

    except SocialMediaError as e:
        print(f"❌ 错误: {e}")
        exit(1)


if __name__ == "__main__":
    main()
