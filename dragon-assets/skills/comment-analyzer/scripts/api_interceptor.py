#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API拦截器模块
API Interceptor Module

专门用于拦截平台API请求，直接获取评论数据（微博优先）。

V2 改进：
- 更早注入拦截代码（页面加载前）
- 微博特定API响应格式处理
- 详细的调试日志
- 自动回退到DOM选择器
"""

import json
import asyncio
from typing import Dict, List, Optional


class APIInterceptor:
    """API拦截器类（改进版）"""

    def __init__(self, mcp_connector, platform_info: Dict):
        """
        初始化API拦截器

        Args:
            mcp_connector: MCP连接器实例
            platform_info: 平台信息
        """
        self.mcp = mcp_connector
        self.platform_info = platform_info
        self.all_comments = []
        self.debug = True  # 调试模式

    async def intercept_comments(self, url: str, max_comments: int = 500) -> List[Dict]:
        """
        拦截评论API请求

        Args:
            url: 目标URL
            max_comments: 最大评论数

        Returns:
            评论列表
        """
        self.all_comments = []

        # 打开页面
        page = await self.mcp.open_page(url)

        # ⭐ 改进：在DOM构建前立即注入拦截器（越早越好）
        await self._setup_early_interceptor(page)

        # 等待页面完全加载
        await asyncio.sleep(2)

        # 检查登录
        if self.platform_info.get("login_required", False):
            await self._check_login(page)

        # ⭐ 改进：点击评论按钮触发初始API请求
        await self._trigger_initial_api(page)

        # 滚动触发更多API请求
        await self._scroll_to_trigger_api(page, max_comments)

        # 提取拦截的评论
        await self._extract_intercepted_comments(page)

        # 去重
        unique_comments = self._deduplicate_comments()

        if self.debug:
            print(f"   📊 API拦截结果：{len(unique_comments)}条评论")

        # 如果拦截失败，返回None表示需要回退到DOM选择器
        if len(unique_comments) == 0:
            return None

        return unique_comments[:max_comments]

    async def _setup_early_interceptor(self, page):
        """
        ⭐ 新增：尽早注入拦截器（在页面完全加载前）

        策略：
        1. 使用MutationObserver监听DOM变化
        2. 在最早时机注入fetch/XHR拦截
        3. 监听网络请求事件
        """
        api_endpoints = self.platform_info.get("api_endpoints", [])

        # 构建增强版JavaScript拦截代码
        interceptor_script = f"""
        (function() {{
            console.log('[API拦截器] 开始注入...');

            // 全局存储拦截的评论
            window.__interceptedComments = [];
            window.__interceptedApis = [];

            // ⭐ 关键：立即执行，不等待DOM加载
            const apiEndpoints = {json.dumps(api_endpoints)};

            // ========== 微博特定API响应处理 ==========
            function parseWeiboComment(data) {{
                try {{
                    // 微博评论API响应格式复杂，需要多层解析
                    let comments = [];

                    // 格式1: data.data直接是数组
                    if (Array.isArray(data?.data)) {{
                        comments = data.data;
                    }}
                    // 格式2: data.data.comments是数组
                    else if (Array.isArray(data?.data?.comments)) {{
                        comments = data.data.comments;
                    }}
                    // 格式3: data.comments是数组
                    else if (Array.isArray(data?.comments)) {{
                        comments = data.comments;
                    }}
                    // 格式4: 单条评论
                    else if (data?.id && data?.text) {{
                        comments = [data];
                    }}

                    // 转换为统一格式
                    comments.forEach(comment => {{
                        // 处理嵌套的用户信息
                        const user = comment.user || comment.userInfo || {{}};

                        // 清理文本（移除HTML标签）
                        let content = comment.text || comment.text_raw || comment.content || '';
                        content = content.replace(/<[^>]*>/g, '').trim();

                        const parsedComment = {{
                            id: comment.id || comment.idstr || comment.mid || `c_${{Date.now()}}_${{Math.random()}}`,
                            author: user.screen_name || user.nickname || user.name || '匿名用户',
                            content: content,
                            likes: comment.like_counts || comment.like_count || comment.likes || 0,
                            publish_time: comment.created_at || comment.created_time || comment.time || ''
                        }};

                        // 去重检查
                        const exists = window.__interceptedComments.some(c => c.id === parsedComment.id);
                        if (!exists && parsedComment.content) {{
                            window.__interceptedComments.push(parsedComment);
                            console.log('[API拦截器] 捕获评论:', parsedComment.author, parsedComment.content.substring(0, 20));
                        }}
                    }});

                    console.log('[API拦截器] 当前已捕获评论数:', window.__interceptedComments.length);
                }} catch (e) {{
                    console.error('[API拦截器] 解析失败:', e);
                }}
            }}

            // ========== 拦截fetch请求 ==========
            const originalFetch = window.fetch;
            window.fetch = async function(...args) {{
                const url = args[0];
                const urlStr = typeof url === 'string' ? url : url.url;

                // 检查是否匹配评论API
                const isCommentApi = apiEndpoints.some(endpoint => urlStr.includes(endpoint));

                if (isCommentApi) {{
                    console.log('[API拦截器] 检测到fetch请求:', urlStr);
                    window.__interceptedApis.push({{ type: 'fetch', url: urlStr, timestamp: Date.now() }});
                }}

                const response = await originalFetch.apply(this, args);

                if (isCommentApi) {{
                    const clonedResponse = response.clone();
                    clonedResponse.json().then(data => {{
                        console.log('[API拦截器] fetch响应数据:', data);
                        parseWeiboComment(data);
                    }}).catch(e => {{
                        console.error('[API拦截器] JSON解析失败:', e);
                    }});
                }}

                return response;
            }};

            // ========== 拦截XMLHttpRequest ==========
            const originalOpen = XMLHttpRequest.prototype.open;
            const originalSend = XMLHttpRequest.prototype.send;

            XMLHttpRequest.prototype.open = function(method, url, ...args) {{
                this.__url = url;
                const isCommentApi = apiEndpoints.some(endpoint => url.includes(endpoint));

                if (isCommentApi) {{
                    console.log('[API拦截器] 检测到XHR请求:', url);
                    window.__interceptedApis.push({{ type: 'xhr', url: url, timestamp: Date.now() }});
                }}

                return originalOpen.apply(this, [method, url, ...args]);
            }};

            XMLHttpRequest.prototype.send = function(...args) {{
                const xhr = this;
                const url = xhr.__url;

                xhr.addEventListener('load', function() {{
                    const isCommentApi = apiEndpoints.some(endpoint => url?.includes(endpoint));

                    if (isCommentApi) {{
                        try {{
                            const data = JSON.parse(xhr.responseText);
                            console.log('[API拦截器] XHR响应数据:', data);
                            parseWeiboComment(data);
                        }} catch (e) {{
                            console.error('[API拦截器] XHR JSON解析失败:', e);
                        }}
                    }}
                }});

                return originalSend.apply(this, args);
            }};

            // ========== 监听页面状态变化 ==========
            window.addEventListener('load', function() {{
                console.log('[API拦截器] 页面加载完成');
                console.log('[API拦截器] 已拦截API请求数:', window.__interceptedApis.length);
                console.log('[API拦截器] 已捕获评论数:', window.__interceptedComments.length);
            }});

            console.log('[API拦截器] 注入完成');
        }})();
        """

        # 立即注入拦截脚本
        await self.mcp.evaluate_script(page, interceptor_script)

        if self.debug:
            print(f"   ✅ API拦截器已注入（端点：{api_endpoints}）")

    async def _trigger_initial_api(self, page):
        """
        ⭐ 新增：触发初始API请求

        微博评论通常需要点击评论按钮才会加载
        """
        try:
            # 尝试点击评论按钮
            result = await self.mcp.evaluate_script(
                page,
                """
                () => {
                    // 微博评论按钮选择器（多种可能）
                    const selectors = [
                        'a[href*="comment"]',
                        '.comment-btn',
                        '[action-type*="comment"]',
                        '.wooisohnxc',
                        '.f-collar'
                    ];

                    for (const selector of selectors) {
                        const btn = document.querySelector(selector);
                        if (btn) {
                            console.log('[触发API] 找到评论按钮:', selector);
                            btn.click();
                            return { success: true, selector };
                        }
                    }

                    return { success: false, error: '未找到评论按钮' };
                }
                """
            )

            if result and result.get("success"):
                if self.debug:
                    print(f"   ✅ 已点击评论按钮（{result.get('selector')}）")
                await asyncio.sleep(2)  # 等待API响应
            else:
                if self.debug:
                    print(f"   ⚠️  未找到评论按钮，可能页面已自动加载")

        except Exception as e:
            if self.debug:
                print(f"   ⚠️  点击评论按钮失败：{str(e)}")

    async def _extract_intercepted_comments(self, page):
        """
        ⭐ 新增：提取拦截的评论数据
        """
        try:
            # 获取拦截的评论
            comments = await self.mcp.evaluate_script(
                page,
                """
                () => {
                    return {
                        comments: window.__interceptedComments || [],
                        apis: window.__interceptedApis || [],
                        totalCount: (window.__interceptedComments || []).length
                    };
                }
                """
            )

            if comments:
                self.all_comments = comments.get("comments", [])

                if self.debug:
                    print(f"   📊 拦截统计：")
                    print(f"      - API请求数：{len(comments.get('apis', []))}")
                    print(f"      - 评论总数：{comments.get('totalCount', 0)}")

        except Exception as e:
            if self.debug:
                print(f"   ⚠️  提取拦截评论失败：{str(e)}")
            self.all_comments = []

    async def _check_login(self, page):
        """检查并等待登录"""
        has_login_prompt = await self.mcp.evaluate_script(
            page,
            """
            () => {
                return document.querySelector('.login-btn') !== null ||
                       document.querySelector('.unlogin') !== null ||
                       document.querySelector('[class*="login"]') !== null ||
                       document.body.textContent.includes('登录');
            }
            """
        )

        if has_login_prompt:
            print("   ⚠️  需要登录，请在45秒内扫码...")
            await asyncio.sleep(45)

    async def _scroll_to_trigger_api(self, page, max_comments: int):
        """
        ⭐ 改进：滚动触发更多API请求
        """
        no_new_count = 0
        last_count = 0
        max_scrolls = 100

        for i in range(max_scrolls):
            # 滚动到底部
            await self.mcp.evaluate_script(
                page,
                "window.scrollTo(0, document.body.scrollHeight)"
            )
            await asyncio.sleep(1.5)

            # 获取当前拦截的评论数量
            current_count = await self.mcp.evaluate_script(
                page,
                "() => window.__interceptedComments ? window.__interceptedComments.length : 0"
            )

            if current_count == last_count:
                no_new_count += 1
                if no_new_count >= 10:
                    if self.debug:
                        print(f"   ⏹️  连续10次无新评论，停止滚动")
                    break
            else:
                no_new_count = 0
                last_count = current_count
                if self.debug:
                    print(f"   📈 已拦截 {current_count} 条评论")

            if current_count >= max_comments:
                if self.debug:
                    print(f"   ✅ 已达到目标评论数：{max_comments}")
                break

    def _deduplicate_comments(self) -> List[Dict]:
        """
        ⭐ 改进：智能去重评论

        去重策略：
        1. 优先使用评论ID去重
        2. 备用：使用 (作者 + 内容 + 时间) 组合去重
        """
        seen_ids = set()
        seen_signatures = set()
        unique_comments = []

        for comment in self.all_comments:
            # 策略1：使用评论ID
            comment_id = comment.get("id")
            content = comment.get("content", "").strip()
            author = comment.get("author", "")
            time = comment.get("publish_time", "")

            # 如果有ID且不重复
            if comment_id and comment_id not in seen_ids:
                seen_ids.add(comment_id)
                unique_comments.append(comment)
                continue

            # 策略2：使用内容签名去重（备用）
            # 清理内容中的时间戳
            import re
            content_clean = re.sub(r'\d{2}-\d{1,2}\s+\d{1,2}:\d{2}', '', content)
            content_clean = ' '.join(content_clean.split()).strip()

            signature = f"{author}_{content_clean}_{time}"

            if signature not in seen_signatures and len(content_clean) >= 2:
                seen_signatures.add(signature)
                # 生成新的ID（如果没有）
                if not comment_id:
                    comment["id"] = f"gen_{len(unique_comments)}"
                unique_comments.append(comment)

        return unique_comments
