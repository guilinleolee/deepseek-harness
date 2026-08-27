#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
平台爬虫模块
Platform Scraper Module

负责从各平台爬取评论数据，支持API拦截和DOM选择器两种方式。
"""

import json
import re
import asyncio
from typing import Dict, List, Optional
from pathlib import Path


class PlatformScraper:
    """平台爬虫类"""

    def __init__(self, url: str, mcp_connector, mode: str = 'mcp'):
        """
        初始化平台爬虫

        Args:
            url: 目标URL
            mcp_connector: MCP连接器实例
            mode: 爬取模式 ('mcp' | 'puppeteer' | 'identify')
        """
        self.url = url
        self.mcp = mcp_connector
        self.mode = mode

        # 加载平台规则
        self.platform_rules = self._load_platform_rules()
        self.platform_info = self.identify_platform()

    def _load_platform_rules(self) -> Dict:
        """加载平台规则配置"""
        config_path = Path(__file__).parent.parent / "config" / "platform_rules.json"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def identify_platform(self) -> Dict:
        """
        识别平台类型

        Returns:
            平台信息字典
        """
        url_lower = self.url.lower()

        # 检查短链接
        for platform_name, rules in self.platform_rules.items():
            if "shorteners" in rules:
                for shortener in rules["shorteners"]:
                    if shortener in url_lower:
                        return {
                            "name": rules["name"],
                            "key": platform_name,
                            "login_required": rules.get("login_required", False),
                            "use_api_intercept": rules.get("use_api_intercept", False)
                        }

        # 检查域名
        for platform_name, rules in self.platform_rules.items():
            for domain in rules.get("domains", []):
                if domain in url_lower:
                    return {
                        "name": rules["name"],
                        "key": platform_name,
                        "login_required": rules.get("login_required", False),
                        "use_api_intercept": rules.get("use_api_intercept", False),
                        "dom_selectors": rules.get("dom_selectors", {})
                    }

        # 默认返回未知平台
        return {
            "name": "未知平台",
            "key": "unknown",
            "login_required": False,
            "use_api_intercept": False
        }

    async def scrape_comments(self, max_comments: int = 500) -> Dict:
        """
        爬取评论数据

        Args:
            max_comments: 最大爬取评论数

        Returns:
            评论数据字典
        """
        platform_key = self.platform_info["key"]

        # 如果平台支持API拦截，优先使用
        if self.platform_info.get("use_api_intercept", False):
            print(f"   使用API拦截模式...")
            return await self._scrape_with_api_intercept(max_comments)
        else:
            print(f"   使用DOM选择器模式...")
            return await self._scrape_with_dom_selector(max_comments)

    async def _scrape_with_api_intercept(self, max_comments: int) -> Dict:
        """
        ⭐ 改进：使用API拦截爬取评论（微博优先）

        返回值：
        - 成功：包含评论的字典
        - 失败：None（表示需要回退到DOM选择器）
        """
        try:
            # 导入API拦截器
            from .api_interceptor import APIInterceptor

            interceptor = APIInterceptor(self.mcp, self.platform_info)
            comments = await interceptor.intercept_comments(self.url, max_comments)

            # ⭐ 新增：检查是否拦截成功
            if comments is None:
                print(f"   ⚠️  API拦截未捕获到评论，回退到DOM选择器")
                return await self._scrape_with_dom_selector(max_comments)

            # 拦截成功
            return {
                "success": True,
                "platform": self.platform_info["name"],
                "post_url": self.url,
                "comments": comments,
                "total_count": len(comments),
                "scrape_method": "api_intercept"
            }

        except Exception as e:
            print(f"   ⚠️  API拦截异常，回退到DOM选择器：{str(e)}")
            return await self._scrape_with_dom_selector(max_comments)

    async def _scrape_with_dom_selector(self, max_comments: int) -> Dict:
        """
        ⭐ 改进：使用DOM选择器爬取评论（备用方案）
        """
        # 打开页面
        page = await self.mcp.open_page(self.url)

        # 检查登录
        if self.platform_info.get("login_required", False):
            await self._check_login(page)

        # 滚动加载评论
        await self._scroll_to_load_comments(page, max_comments)

        # 提取评论数据
        selectors = self.platform_info.get("dom_selectors", {})
        comments = await self._extract_comments_from_dom(page, selectors)

        # 获取页面标题
        post_title = await self.mcp.evaluate_script(
            page,
            "() => document.title"
        )

        # ⭐ 新增：去重和过滤
        comments = self.deduplicate_comments(comments)
        comments = self.filter_valid_comments(comments)

        return {
            "success": True,
            "platform": self.platform_info["name"],
            "post_url": self.url,
            "post_title": post_title,
            "comments": comments,
            "total_count": len(comments),
            "scrape_method": "dom_selector"
        }

    async def _check_login(self, page):
        """检查并等待登录"""
        # 检测是否有登录提示
        has_login_prompt = await self.mcp.evaluate_script(
            page,
            """
            () => {
                return document.querySelector('.login-btn') !== null ||
                       document.querySelector('.unlogin') !== null ||
                       document.querySelector('[class*="login"]') !== null;
            }
            """
        )

        if has_login_prompt:
            print("   ⚠️  需要登录，请在45秒内扫码...")
            await asyncio.sleep(45)  # 等待45秒扫码

    async def _scroll_to_load_comments(self, page, max_comments: int):
        """滚动加载所有评论"""
        no_new_count = 0
        last_count = 0
        max_scrolls = 100

        for i in range(max_scrolls):
            # 滚动到底部
            await self.mcp.evaluate_script(
                page,
                "window.scrollTo(0, document.body.scrollHeight)"
            )
            await asyncio.sleep(1.5)  # 等待内容加载

            # 检查评论数量
            current_count = await self._get_comment_count(page)
            if current_count == last_count:
                no_new_count += 1
                if no_new_count >= 10:  # 连续10次无新评论，停止
                    break
            else:
                no_new_count = 0
                last_count = current_count

            if current_count >= max_comments:
                break

    async def _get_comment_count(self, page) -> int:
        """获取当前评论数量"""
        selectors = self.platform_info.get("dom_selectors", {})
        comment_selector = selectors.get("comment_item", ".comment-item")

        count = await self.mcp.evaluate_script(
            page,
            f"""
            () => {{
                return document.querySelectorAll('{comment_selector}').length;
            }}
            """
        )
        return count or 0

    async def _extract_comments_from_dom(self, page, selectors: Dict) -> List[Dict]:
        """从DOM提取评论数据"""
        if not selectors:
            return []

        comment_item = selectors.get("comment_item", ".comment-item")
        comment_text = selectors.get("comment_text", ".comment-text")
        comment_user = selectors.get("comment_user", ".user-name")
        comment_time = selectors.get("comment_time", ".time")

        comments = await self.mcp.evaluate_script(
            page,
            f"""
            () => {{
                return Array.from(document.querySelectorAll('{comment_item}'))
                    .map((item, index) => {{
                        const textEl = item.querySelector('{comment_text}');
                        const userEl = item.querySelector('{comment_user}');
                        const timeEl = item.querySelector('{comment_time}');
                        const likeEl = item.querySelector('.like-btn, [class*="like"]');

                        return {{
                            id: `comment_${index}}`,
                            content: textEl ? textEl.textContent.trim() : '',
                            author: userEl ? userEl.textContent.trim() : '匿名用户',
                            publish_time: timeEl ? timeEl.textContent.trim() : '',
                            likes: likeEl ? parseInt(likeEl.textContent) || 0 : 0
                        }};
                    }})
                    .filter(c => c.content.length > 0);
            }}
            """
        )

        return comments or []

    def deduplicate_comments(self, comments: List[Dict]) -> List[Dict]:
        """
        改进的评论去重逻辑

        Args:
            comments: 原始评论列表

        Returns:
            去重后的评论列表
        """
        seen = set()
        unique_comments = []

        for comment in comments:
            # 获取评论内容
            content = comment.get("content", "")
            username = comment.get("author", "")
            time = comment.get("publish_time", "")

            # 清理内容：
            # 1. 移除时间戳（格式：26-1-15 06:10）
            content_clean = re.sub(r'\d{2}-\d{1,2}\s+\d{1,2}:\d{2}', '', content)

            # 2. 移除多余空白
            content_clean = ' '.join(content_clean.split())

            # 3. 移除表情符号（保留文字）
            # emoji_pattern = re.compile("["
            # u"\U0001F600-\U0001F64F"  # emoticons
            # u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            # u"\U0001F680-\U0001F6FF"  # transport & map symbols
            # u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            # "]+", flags=re.UNICODE)
            # content_clean = emoji_pattern.sub('', content_clean)

            content_clean = content_clean.strip()

            # 生成唯一ID
            unique_id = f"{username}_{content_clean}_{time}"

            # 过滤无效评论
            if len(content_clean) < 2:
                continue

            # 检查是否包含"回复"、"赞"等提示词
            if any(keyword in content_clean for keyword in ["人 共", "条回复", "点击查看"]):
                continue

            # 检查是否为纯表情符号
            if content_clean in ["💔", "😭", "🙏", "💕", "🕯️"]:
                continue

            # 去重
            if unique_id not in seen:
                seen.add(unique_id)
                unique_comments.append(comment)

        return unique_comments

    def filter_valid_comments(self, comments: List[Dict]) -> List[Dict]:
        """
        过滤有效评论

        Args:
            comments: 原始评论列表

        Returns:
            有效评论列表
        """
        valid_comments = []

        for comment in comments:
            content = comment.get("content", "")

            # 过滤条件
            # 1. 内容长度合理
            if len(content) < 2 or len(content) > 500:
                continue

            # 2. 不包含回复提示
            if any(keyword in content for keyword in ["人 共", "条回复", "展开"]):
                continue

            # 3. 不是纯数字或符号
            if content.strip().isdigit() or len(content.strip()) < 2:
                continue

            valid_comments.append(comment)

        return valid_comments
