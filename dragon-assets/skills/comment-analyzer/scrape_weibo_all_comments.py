#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微博完整评论爬取脚本 - 针对680+条评论
Weibo Complete Comment Scraper

核心策略：
1. 使用正确的选择器 .wbpro-list
2. 点击"按时间"排序获取更多评论
3. 渐进式滚动触发虚拟滚动
4. 智能等待和检测
"""

import asyncio
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set


class WeiboCommentScraper:
    """微博完整评论爬取器"""

    def __init__(self, url: str, target_count: int = 680):
        self.url = url
        self.target_count = target_count
        self.all_comments: Dict[str, Dict] = {}
        self.seen_ids: Set[str] = set()

    async def scrape(self):
        """执行完整爬取流程"""
        print("\n" + "="*70)
        print("🔥 微博完整评论爬取工具")
        print("="*70)
        print(f"📍 目标URL: {self.url}")
        print(f"🎯 目标评论数: {self.target_count}条")
        print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")

        # 导入MCP连接器
        sys.path.insert(0, str(Path(__file__).parent))
        from scripts.mcp_connector import MCPConnector

        mcp = MCPConnector()

        # 步骤1：打开页面
        print("📖 步骤1：打开页面...")
        page = await mcp.open_page(self.url)
        await asyncio.sleep(3)
        print("   ✅ 页面已打开\n")

        # 步骤2：点击评论区域确保评论加载
        print("💬 步骤2：定位评论区域...")
        await self._focus_comment_area(page)
        print("   ✅ 评论区域已定位\n")

        # 步骤3：切换排序方式
        print("🔄 步骤3：切换排序方式为'按时间'...")
        await self._switch_sort_order(page)
        print("   ✅ 排序方式已切换\n")

        # 步骤4：渐进式滚动加载
        print("📜 步骤4：开始渐进式滚动加载评论...")
        await self._progressive_scroll(page)
        print(f"   ✅ 滚动加载完成\n")

        # 步骤5：最终数据提取
        print("📊 步骤5：提取所有评论数据...")
        await self._extract_all_comments(page)
        print(f"   ✅ 提取完成\n")

        # 步骤6：保存结果
        print("💾 步骤6：保存评论数据...")
        output_path = await self._save_results()
        print(f"   ✅ 数据已保存\n")

        # 打印统计信息
        self._print_summary(output_path)

        return list(self.all_comments.values())

    async def _focus_comment_area(self, page):
        """定位到评论区域"""
        try:
            result = await page.evaluate_js("""
            () => {
                // 查找评论区域的多种可能选择器
                const selectors = [
                    'a[href*="comment"]',
                    '.comment-btn',
                    '[action-type*="comment"]',
                    '.WB_feed_like',
                    '.f-collar'
                ];

                for (const selector of selectors) {
                    const el = document.querySelector(selector);
                    if (el) {
                        el.scrollIntoView({behavior: 'smooth', block: 'center'});
                        return {found: true, selector: selector};
                    }
                }

                // 如果没找到按钮，尝试直接滚动到评论区
                const commentList = document.querySelector('.wbpro-list, .comment_list, .list_con');
                if (commentList) {
                    commentList.scrollIntoView({behavior: 'smooth', block: 'center'});
                    return {found: true, selector: 'comment-area'};
                }

                return {found: false};
            }
            """)
            print(f"   🔍 定位结果: {result}")
        except Exception as e:
            print(f"   ⚠️  定位评论区域失败: {e}")

    async def _switch_sort_order(self, page):
        """切换排序方式为'按时间'"""
        try:
            result = await page.evaluate_js("""
            () => {
                // 查找排序按钮
                const sortButtons = Array.from(document.querySelectorAll('*')).filter(el => {
                    const text = el.textContent || '';
                    return text.includes('按时间') || text.includes('按热度');
                });

                if (sortButtons.length > 0) {
                    // 点击"按时间"按钮
                    for (const btn of sortButtons) {
                        if (btn.textContent.includes('按时间')) {
                            btn.click();
                            return {clicked: true, text: '按时间'};
                        }
                    }
                }

                return {clicked: false};
            }
            """)
            if result.get('clicked'):
                print(f"   ✅ 已点击排序按钮: {result.get('text')}")
                await asyncio.sleep(2)  # 等待重新排序
            else:
                print(f"   ⚠️  未找到排序按钮")
        except Exception as e:
            print(f"   ⚠️  切换排序失败: {e}")

    async def _progressive_scroll(self, page):
        """渐进式滚动加载所有评论"""
        no_new_count = 0
        last_count = 0
        max_iterations = 200  # 增加最大迭代次数
        scroll_delay = 1200   # 滚动延迟（毫秒）

        for i in range(max_iterations):
            # 提取当前评论
            current_count = await self._extract_current_comments(page)

            # 进度显示
            if i % 5 == 0 or current_count >= self.target_count:
                progress = min(100, int(current_count / self.target_count * 100))
                print(f"   📈 [{i:3d}/{max_iterations}] 已加载: {current_count:3d}条 ({progress}%)")

            # 检查是否达到目标
            if current_count >= self.target_count:
                print(f"\n   🎉 已达到目标评论数: {current_count}条")
                break

            # 检查是否有新评论
            if current_count == last_count:
                no_new_count += 1
                if no_new_count >= 15:  # 连续15次无新评论，停止
                    print(f"\n   ⚠️  连续15次无新评论，停止滚动")
                    break
            else:
                no_new_count = 0
                last_count = current_count

            # 执行滚动
            await self._smart_scroll(page)
            await asyncio.sleep(scroll_delay / 1000)

    async def _smart_scroll(self, page):
        """智能滚动策略"""
        try:
            await page.evaluate_js("""
            () => {
                // 方法1：滚动到评论容器底部
                const commentList = document.querySelector('.wbpro-list');
                if (commentList) {
                    commentList.scrollTop = commentList.scrollHeight;
                }

                // 方法2：滚动到页面底部
                window.scrollTo(0, document.body.scrollHeight);

                // 方法3：查找并点击"加载更多"
                const loadMoreBtn = Array.from(document.querySelectorAll('*')).find(el => {
                    const text = el.textContent || '';
                    return text.includes('加载更多') || text.includes('点击加载') || text.includes('展开');
                });

                if (loadMoreBtn && loadMoreBtn.offsetParent !== null) {
                    loadMoreBtn.click();
                }

                return true;
            }
            """)
        except Exception as e:
            print(f"   ⚠️  滚动执行异常: {e}")

    async def _extract_current_comments(self, page) -> int:
        """提取当前页面的评论"""
        try:
            # 使用之前成功的 .wbpro-list 选择器
            js_code = """
            () => {
                const comments = [];
                const commentList = document.querySelector('.wbpro-list');

                if (!commentList) {
                    console.log('[提取器] 未找到 .wbpro-list');
                    return 0;
                }

                // 获取所有评论节点
                const nodes = commentList.children;

                for (let i = 0; i < nodes.length; i++) {
                    const node = nodes[i];
                    const text = node.textContent || '';

                    // 解析评论
                    const colonIndex = text.indexOf(':');
                    if (colonIndex === -1) continue;

                    // 提取用户名
                    const username = text.substring(0, colonIndex).trim();

                    // 提取时间
                    const timeMatch = text.match(/(\\d{1,2}-\\d{1,2}-\\d{1,2})\\s+(\\d{1,2}:\\d{2})/);
                    if (!timeMatch) continue;

                    const time = `${timeMatch[1]} ${timeMatch[2]}`;
                    const timeStartIndex = text.indexOf(timeMatch[0]);

                    // 提取内容
                    let content = text.substring(colonIndex + 1, timeStartIndex).trim();

                    // 清理内容
                    content = content.replace(/@[\\u4e00-\\u9fa5a-zA-Z0-9_]+/g, '').trim();
                    content = content.replace(/^:+/, '').trim();
                    content = content.replace(/\\s+/g, ' ');

                    // 过滤无效评论
                    if (content.length < 2) continue;

                    // 提取点赞数
                    const likeMatch = text.match(/(\\d+)$/);
                    const likes = likeMatch ? parseInt(likeMatch[1]) : 0;

                    // 生成唯一ID
                    const uniqueId = `${username}_${content}_${time}`;

                    comments.push({
                        username,
                        content,
                        time,
                        likes,
                        uniqueId
                    });
                }

                // 存储到全局变量
                if (!window.__extractedComments) {
                    window.__extractedComments = {};
                }

                let newCount = 0;
                comments.forEach(c => {
                    if (!window.__extractedComments[c.uniqueId]) {
                        window.__extractedComments[c.uniqueId] = c;
                        newCount++;
                    }
                });

                return Object.keys(window.__extractedComments).length;
            }
            """

            count = await page.evaluate_js(js_code)
            return count or 0

        except Exception as e:
            print(f"   ⚠️  提取评论失败: {e}")
            return 0

    async def _extract_all_comments(self, page):
        """最终提取所有评论数据"""
        try:
            result = await page.evaluate_js("""
            () => {
                const allComments = window.__extractedComments || {};
                return Object.values(allComments);
            }
            """)

            if result:
                for comment in result:
                    self.all_comments[comment['uniqueId']] = comment

        except Exception as e:
            print(f"   ⚠️  最终提取失败: {e}")

    async def _save_results(self) -> Path:
        """保存爬取结果"""
        output_dir = Path.home() / 'comment-analysis-reports'
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f'weibo_complete_comments_{timestamp}.json'

        # 准备数据
        comments_list = list(self.all_comments.values())
        comments_list.sort(key=lambda x: x.get('likes', 0), reverse=True)

        data = {
            'url': self.url,
            'target_count': self.target_count,
            'actual_count': len(comments_list),
            'completion_rate': f"{len(comments_list)/self.target_count*100:.1f}%",
            'extracted_at': datetime.now().isoformat(),
            'comments': comments_list
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return output_file

    def _print_summary(self, output_path: Path):
        """打印统计摘要"""
        print("\n" + "="*70)
        print("📊 爬取完成统计")
        print("="*70)

        total = len(self.all_comments)
        rate = total / self.target_count * 100

        print(f"🎯 目标评论数: {self.target_count}条")
        print(f"✅ 实际提取: {total}条")
        print(f"📈 完成率: {rate:.1f}%")

        if total >= self.target_count:
            print(f"🎉 恭喜！已达到目标评论数！")
        else:
            missing = self.target_count - total
            print(f"⚠️  差距: 还差 {missing} 条评论")

        print(f"\n📁 数据文件: {output_path}")
        print("="*70 + "\n")

        # 显示TOP10热门评论
        comments_list = list(self.all_comments.values())
        comments_list.sort(key=lambda x: x.get('likes', 0), reverse=True)

        print("💬 热门评论 TOP10")
        print("-"*70)
        for i, comment in enumerate(comments_list[:10]):
            print(f"{i+1}. @{comment['username']} | 👍 {comment['likes']} | {comment['time']}")
            print(f"   {comment['content'][:80]}...")
            print()


async def main():
    """主函数"""
    url = "https://weibo.com/7985254173/QmWvGrm7G#comment"

    if len(sys.argv) > 1:
        url = sys.argv[1]

    scraper = WeiboCommentScraper(url, target_count=680)
    await scraper.scrape()


if __name__ == "__main__":
    asyncio.run(main())
