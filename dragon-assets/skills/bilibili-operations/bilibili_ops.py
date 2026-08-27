#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bilibili Operations - B站运营能力封装
为天龙引擎提供完整的B站数据采集、互动操作和内容发布能力
"""

import asyncio
import json
import sys
from typing import Dict, List, Any, Optional

# 设置UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    from bilibili_api import (
        video, hot, user, search, rank, dynamic,
        favorite_list, login_v2, Credential, sync
    )
    BILI_API_AVAILABLE = True
except ImportError:
    BILI_API_AVAILABLE = False
    print("Warning: bilibili_api not installed. Run: pip install bilibili-api-python")


class BilibiliOperations:
    """B站运营能力封装类"""

    def __init__(self, credential: Optional[Credential] = None):
        self.credential = credential

    # ==================== 数据获取 ====================

    def get_video_info(self, bvid: str) -> Dict[str, Any]:
        """获取视频详情"""
        if not BILI_API_AVAILABLE:
            return {"error": "bilibili_api not installed"}

        v = video.Video(bvid=bvid)
        info = sync(v.get_info())
        return {
            "title": info.get("title", ""),
            "description": info.get("desc", ""),
            "author": info.get("owner", {}).get("name", ""),
            "author_id": info.get("owner", {}).get("mid", 0),
            "bvid": bvid,
            "aid": info.get("aid", 0),
            "duration": info.get("duration", 0),
            "cover": info.get("pic", ""),
            "url": f"https://www.bilibili.com/video/{bvid}",
            "stats": {
                "view": info.get("stat", {}).get("view", 0),
                "like": info.get("stat", {}).get("like", 0),
                "coin": info.get("stat", {}).get("coin", 0),
                "share": info.get("stat", {}).get("share", 0),
                "favorite": info.get("stat", {}).get("favorite", 0),
                "danmaku": info.get("stat", {}).get("danmaku", 0),
            },
            "tags": [t.get("tag_name", "") for t in info.get("tag", [])],
            "pubdate": info.get("pubdate", 0),
        }

    def get_video_comments(self, bvid: str, page: int = 1) -> List[Dict]:
        """获取视频评论"""
        if not BILI_API_AVAILABLE:
            return []

        v = video.Video(bvid=bvid)
        comments = sync(v.get_comments(page_index=page))
        return [
            {
                "id": c.get("rpid", 0),
                "content": c.get("content", {}).get("message", ""),
                "author": c.get("member", {}).get("uname", ""),
                "likes": c.get("like", 0),
                "time": c.get("ctime", 0),
            }
            for c in comments.get("replies", []) or []
        ]

    def get_related_videos(self, bvid: str) -> List[Dict]:
        """获取相关推荐视频"""
        if not BILI_API_AVAILABLE:
            return []

        v = video.Video(bvid=bvid)
        related = sync(v.get_related())
        return [
            {
                "bvid": r.get("bvid", ""),
                "title": r.get("title", ""),
                "author": r.get("owner", {}).get("name", ""),
                "view": r.get("stat", {}).get("view", 0),
            }
            for r in related[:10]
        ]

    # ==================== 热门发现 ====================

    def get_hot_videos(self) -> List[Dict]:
        """获取热门视频列表"""
        if not BILI_API_AVAILABLE:
            return []

        result = sync(hot.get_hot_videos())
        videos = result.get("list", [])
        return [
            {
                "bvid": v.get("bvid", ""),
                "title": v.get("title", ""),
                "author": v.get("owner", {}).get("name", ""),
                "view": v.get("stat", {}).get("view", 0),
                "cover": v.get("pic", ""),
            }
            for v in videos
        ]

    def get_rank_videos(self) -> List[Dict]:
        """获取排行榜视频"""
        if not BILI_API_AVAILABLE:
            return []

        # 使用热门视频作为排行榜替代
        result = sync(hot.get_hot_videos())
        videos = result.get("list", [])
        return [
            {
                "rank": i + 1,
                "bvid": v.get("bvid", ""),
                "title": v.get("title", ""),
                "author": v.get("owner", {}).get("name", ""),
                "view": v.get("stat", {}).get("view", 0),
                "score": v.get("stat", {}).get("like", 0) + v.get("stat", {}).get("coin", 0) * 2,
            }
            for i, v in enumerate(videos)
        ]

    def get_user_videos(self, uid: int, page: int = 1) -> List[Dict]:
        """获取UP主视频列表"""
        if not BILI_API_AVAILABLE:
            return []

        u = user.User(uid=uid)
        result = sync(u.get_videos(pn=page))
        videos = result.get("list", {}).get("vlist", [])
        return [
            {
                "bvid": v.get("bvid", ""),
                "title": v.get("title", ""),
                "play": v.get("play", 0),
                "created": v.get("created", 0),
            }
            for v in videos
        ]

    def get_user_info(self, uid: int) -> Dict[str, Any]:
        """获取UP主资料"""
        if not BILI_API_AVAILABLE:
            return {"error": "bilibili_api not installed"}

        u = user.User(uid=uid)
        info = sync(u.get_user_info())
        return {
            "uid": uid,
            "name": info.get("name", ""),
            "sign": info.get("sign", ""),
            "level": info.get("level", 0),
            "fans": info.get("follower", 0),
            "following": info.get("following", 0),
            "avatar": info.get("face", ""),
        }

    def search_videos(self, keyword: str, page: int = 1) -> List[Dict]:
        """搜索视频"""
        if not BILI_API_AVAILABLE:
            return []

        s = search.Search(keyword)
        result = sync(s.next_page(page=page))
        videos = result.get("result", [])
        return [
            {
                "bvid": v.get("bvid", ""),
                "title": v.get("title", "").replace('<em class="keyword">', "").replace("</em>", ""),
                "author": v.get("author", ""),
                "play": v.get("play", 0),
            }
            for v in videos[:20]
        ]

    # ==================== 互动操作（需登录） ====================

    def like_video(self, bvid: str, like: bool = True) -> Dict:
        """点赞视频"""
        if not BILI_API_AVAILABLE or not self.credential:
            return {"error": "需要登录"}

        v = video.Video(bvid=bvid, credential=self.credential)
        result = sync(v.like(like))
        return {"success": True, "action": "like" if like else "unlike"}

    def coin_video(self, bvid: str, num: int = 1) -> Dict:
        """投币"""
        if not BILI_API_AVAILABLE or not self.credential:
            return {"error": "需要登录"}

        v = video.Video(bvid=bvid, credential=self.credential)
        result = sync(v.coin(num))
        return {"success": True, "coins": num}

    def triple_video(self, bvid: str) -> Dict:
        """一键三连"""
        if not BILI_API_AVAILABLE or not self.credential:
            return {"error": "需要登录"}

        v = video.Video(bvid=bvid, credential=self.credential)
        result = sync(v.triple())
        return {"success": True, "action": "triple"}

    def follow_user(self, uid: int, follow: bool = True) -> Dict:
        """关注/取关UP主"""
        if not BILI_API_AVAILABLE or not self.credential:
            return {"error": "需要登录"}

        u = user.User(uid=uid, credential=self.credential)
        result = sync(u.modify_relation(
            user.RelationType.FOLLOW if follow else user.RelationType.UNFOLLOW
        ))
        return {"success": True, "action": "follow" if follow else "unfollow"}

    # ==================== 收藏管理（需登录） ====================

    def get_favorites(self) -> List[Dict]:
        """获取收藏夹列表"""
        if not BILI_API_AVAILABLE or not self.credential:
            return []

        result = sync(favorite_list.get_video_favorite_list(
            credential=self.credential
        ))
        return [
            {
                "id": f.get("id", 0),
                "title": f.get("title", ""),
                "media_count": f.get("media_count", 0),
            }
            for f in result.get("list", [])
        ]

    # ==================== 动态发布（需登录） ====================

    def post_dynamic(self, text: str) -> Dict:
        """发布动态"""
        if not BILI_API_AVAILABLE or not self.credential:
            return {"error": "需要登录"}

        result = sync(dynamic.send_dynamic(text, credential=self.credential))
        return {"success": True, "dynamic_id": result.get("dyn_id", "")}


def main():
    """CLI入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Bilibili Operations CLI")
    parser.add_argument("command", choices=[
        "info", "comments", "related", "hot", "rank",
        "user", "user-videos", "search",
        "like", "coin", "triple", "follow"
    ])
    parser.add_argument("--bvid", help="视频BV号")
    parser.add_argument("--uid", type=int, help="用户UID")
    parser.add_argument("--keyword", help="搜索关键词")
    parser.add_argument("--coins", type=int, default=1, help="投币数量")
    parser.add_argument("--json", action="store_true", help="JSON输出")

    args = parser.parse_args()

    bili = BilibiliOperations()

    result = {}

    if args.command == "info" and args.bvid:
        result = bili.get_video_info(args.bvid)
    elif args.command == "comments" and args.bvid:
        result = {"comments": bili.get_video_comments(args.bvid)}
    elif args.command == "related" and args.bvid:
        result = {"related": bili.get_related_videos(args.bvid)}
    elif args.command == "hot":
        result = {"hot_videos": bili.get_hot_videos()}
    elif args.command == "rank":
        result = {"rank": bili.get_rank_videos()}
    elif args.command == "user" and args.uid:
        result = bili.get_user_info(args.uid)
    elif args.command == "user-videos" and args.uid:
        result = {"videos": bili.get_user_videos(args.uid)}
    elif args.command == "search" and args.keyword:
        result = {"results": bili.search_videos(args.keyword)}
    elif args.command in ["like", "coin", "triple", "follow"]:
        result = {"error": "互动操作需要登录，请使用: bili login"}
    else:
        result = {"error": "缺少必要参数"}

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result)


if __name__ == "__main__":
    main()