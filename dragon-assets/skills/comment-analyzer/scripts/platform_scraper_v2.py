#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
平台爬虫模块 V2 - 改进版
Platform Scraper Module V2 - Improved

优化：
1. 自动检测登录状态
2. 提示用户手动登录
3. API拦截优先
4. 更好的评论去重
"""

import asyncio
import json
from typing import Dict, List, Optional
from datetime import datetime


class PlatformScraperV2:
    """平台爬虫类 V2"""

    def __init__(self, config: Dict = None):
        """
        初始化爬虫

        Args:
            config: 配置字典
        """
        self.config = config or self._load_config()
        self.platform = None
        self.comments = []

    def _load_config(self) -> Dict:
        """加载配置文件"""
        config_path = "config/comment-analyzer.json"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def identify_platform(self, url: str) -> Optional[str]:
        """
        识别平台

        Args:
            url: 目标URL

        Returns:
            平台名称
        """
        platform_rules = self.config.get("platforms", {})

        for platform, rules in platform_rules.items():
            domains = rules.get("domains", [])
            for domain in domains:
                if domain in url:
                    self.platform = platform
                    return platform

        return None

    async def check_login_required(self, page_data: Dict) -> bool:
        """
        检查是否需要登录

        Args:
            page_data: 页面数据（从MCP获取）

        Returns:
            是否需要登录
        """
        # 检查登录相关元素
        page_text = page_data.get("text", "").lower()

        login_indicators = [
            "登录",
            "login",
            "请登录",
            "扫码登录",
            "账号密码",
            "立即登录"
        ]

        for indicator in login_indicators:
            if indicator in page_text:
                return True

        # 检查评论区域是否隐藏
        if "评论" not in page_text and "comment" not in page_text:
            return True

        return False

    def generate_login_prompt(self, platform: str) -> str:
        """
        生成登录提示信息

        Args:
            platform: 平台名称

        Returns:
            提示信息
        """
        platform_names = {
            "weibo": "微博",
            "xiaohongshu": "小红书",
            "douyin": "抖音",
            "bilibili": "B站",
            "zhihu": "知乎"
        }

        cn_name = platform_names.get(platform, platform)

        return f"""
{'='*60}
⚠️  检测到需要登录

平台：{cn_name}
登录方式：扫码登录

操作步骤：
1. 打开手机上的{cn_name}App
2. 使用"扫一扫"功能扫描页面上的二维码
3. 确认登录

⏱️  系统将等待最多45秒...
{'='*60}
"""

    async def scrape_with_login_check(self, url: str, mcp_connector) -> Dict:
        """
        带登录检查的爬取

        Args:
            url: 目标URL
            mcp_connector: MCP连接器

        Returns:
            爬取结果
        """
        # 1. 识别平台
        platform = self.identify_platform(url)
        if not platform:
            return {
                "success": False,
                "error": "无法识别平台",
                "url": url
            }

        # 2. 打开页面
        print(f"\n✅ 平台识别：{platform}")
        print(f"📄 正在打开页面...")

        # 这里需要调用MCP打开页面
        # page = await mcp_connector.open_page(url)

        # 3. 检查是否需要登录
        # page_data = await mcp_connector.get_page_data(page)
        # login_required = await self.check_login_required(page_data)

        # 模拟检测
        login_required = self.config.get("platforms", {}).get(platform, {}).get("login_required", False)

        if login_required:
            prompt = self.generate_login_prompt(platform)
            print(prompt)

            # 等待登录
            login_success = await self._wait_for_login(mcp_connector, timeout=45)

            if not login_success:
                return {
                    "success": False,
                    "error": "登录超时或失败",
                    "platform": platform
                }

        # 4. 开始爬取评论
        print("📥 开始爬取评论...")

        # 这里调用具体的爬取逻辑
        comments = await self._scrape_comments(mcp_connector, platform)

        return {
            "success": True,
            "platform": platform,
            "url": url,
            "comments": comments,
            "total_count": len(comments),
            "scraped_at": datetime.now().isoformat()
        }

    async def _wait_for_login(self, mcp_connector, timeout: int = 45) -> bool:
        """
        等待用户登录

        Args:
            mcp_connector: MCP连接器
            timeout: 超时时间（秒）

        Returns:
            是否登录成功
        """
        print("\n⏳ 等待登录中...\n")

        for i in range(timeout):
            await asyncio.sleep(1)

            # 每5秒检查一次
            if i % 5 == 0 and i > 0:
                print(f"⏱️  {i}/{timeout} 秒...")

            # 这里需要实际检查登录状态
            # logged_in = await mcp_connector.check_login_status()
            # if logged_in:
            #     return True

        return False

    async def _scrape_comments(self, mcp_connector, platform: str) -> List[Dict]:
        """
        爬取评论

        Args:
            mcp_connector: MCP连接器
            platform: 平台名称

        Returns:
            评论列表
        """
        # 根据平台选择爬取策略
        use_api_intercept = self.config.get("platforms", {}).get(platform, {}).get("use_api_intercept", False)

        if use_api_intercept:
            # API拦截模式
            return await self._scrape_via_api(mcp_connector, platform)
        else:
            # DOM选择器模式
            return await self._scrape_via_dom(mcp_connector, platform)

    async def _scrape_via_api(self, mcp_connector, platform: str) -> List[Dict]:
        """
        通过API拦截爬取

        Args:
            mcp_connector: MCP连接器
            platform: 平台名称

        Returns:
            评论列表
        """
        # 注入API拦截脚本
        api_endpoints = self.config.get("platforms", {}).get(platform, {}).get("api_endpoints", [])

        script = f"""
        (function() {{
          window.capturedComments = [];

          // 拦截fetch
          const originalFetch = window.fetch;
          window.fetch = function(...args) {{
            const url = args[0];
            if (typeof url === 'string' && {json.dumps(api_endpoints)}) {{
              for (let endpoint of {json.dumps(api_endpoints)}) {{
                if (url.includes(endpoint)) {{
                  console.log('🎯 API拦截成功:', url);
                  return originalFetch.apply(this, args).then(response => {{
                    return response.clone().json().then(data => {{
                      window.capturedComments.push({{url, data}});
                      return response;
                    }});
                  }});
                }}
              }}
            }}
            return originalFetch.apply(this, args);
          }};

          return {{ injected: true }};
        }})();
        """

        # 注入脚本
        # await mcp_connector.evaluate_script(script)

        # 滚动页面触发API调用
        # ...

        # 获取捕获的评论
        # comments = await mcp_connector.evaluate_script("window.capturedComments")

        return []

    async def _scrape_via_dom(self, mcp_connector, platform: str) -> List[Dict]:
        """
        通过DOM选择器爬取

        Args:
            mcp_connector: MCP连接器
            platform: 平台名称

        Returns:
            评论列表
        """
        # 平台特定的DOM选择器
        selectors = {
            "weibo": "div.woo-box-item-flex",
            "xiaohongshu": "div.comment-item",
            "douyin": "div.comment-item",
            "bilibili": "div.reply-item",
            "zhihu": "div.List-item"
        }

        selector = selectors.get(platform)

        if not selector:
            return []

        # 滚动加载所有评论
        # for i in range(10):
        #     await mcp_connector.scroll_page()
        #     await asyncio.sleep(1)

        # 提取评论
        # comments = await mcp_connector.extract_comments(selector)

        return []

    def deduplicate_comments(self, comments: List[Dict]) -> List[Dict]:
        """
        评论去重

        Args:
            comments: 原始评论列表

        Returns:
            去重后的评论列表
        """
        seen = set()
        unique_comments = []

        for comment in comments:
            # 生成唯一ID：基于用户名、内容、时间
            content = comment.get("content", "")
            username = comment.get("username", "")
            time = comment.get("time", "")

            # 清理内容
            content_clean = content.strip()

            # 生成唯一标识
            unique_id = f"{username}_{content_clean}_{time}"

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

            # 2. 不包含"回复"、"赞"等提示词
            if any(word in content for word in ["人 共", "条回复", "点击查看"]):
                continue

            # 3. 不是纯表情符号
            if content.strip() in ["💔", "😭", "🙏", "💕"]:
                continue

            valid_comments.append(comment)

        return valid_comments


# 使用示例
async def main():
    """主函数示例"""
    scraper = PlatformScraperV2()

    # 测试平台识别
    url = "https://weibo.com/ttarticle/p/show?id=2309405255148850249780"
    platform = scraper.identify_platform(url)
    print(f"识别平台: {platform}")

    # 测试登录提示
    if platform:
        prompt = scraper.generate_login_prompt(platform)
        print(prompt)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
