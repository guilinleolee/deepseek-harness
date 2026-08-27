#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统化加载并提取所有微博评论
使用MCP Chrome DevTools自动点击"加载更多"并提取评论
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# 评论数据结构
class Comment:
    def __init__(self, username: str, content: str, time: str, likes: int = 0):
        self.username = username
        self.content = content
        self.time = time
        self.likes = likes

    def to_dict(self):
        return {
            "username": self.username,
            "content": self.content,
            "time": self.time,
            "likes": self.likes
        }

    @property
    def unique_id(self):
        """生成唯一ID用于去重"""
        content_clean = re.sub(r'\d{2}-\d{1,2}\s+\d{1,2}:\d{2}', '', self.content)
        content_clean = ' '.join(content_clean.split())
        return f"{self.username}_{content_clean}_{self.time}"


async def extract_comments_from_page(page) -> List[Comment]:
    """从当前页面DOM提取评论"""

    # 使用JavaScript提取评论数据
    js_code = """
    () => {
        const comments = [];
        const userLinks = document.querySelectorAll('a[href*="/u/"]');

        userLinks.forEach(link => {
            const username = link.textContent?.trim();
            if (!username || username.length < 2) return;

            // 获取冒号后面的内容
            let content = '';
            let time = '';
            let likes = 0;

            // 查找评论内容
            let node = link.nextSibling;
            let contentNodes = [];
            while (node && contentNodes.length < 50) {
                if (node.nodeType === Node.TEXT_NODE) {
                    contentNodes.push(node.textContent);
                } else if (node.nodeType === Node.ELEMENT_NODE) {
                    const tag = node.tagName;
                    if (tag === 'A' && node !== link) {
                        break;
                    }
                    if (tag !== 'IMG' && tag !== 'SVG') {
                        const text = node.textContent?.trim();
                        if (text && !text.includes('来自') && !text.match(/^\d{2}-\d{1,2}\s+\d{1,2}:\d{2}$/)) {
                            contentNodes.push(text);
                        }
                    }
                }
                node = node.nextSibling;
            }

            content = contentNodes.join('').trim();

            // 查找时间和点赞数
            let parent = link.closest('div');
            let searchDepth = 0;
            while (parent && searchDepth < 10) {
                const parentText = parent.textContent || '';

                // 查找时间
                const timeMatch = parentText.match(/(\d{2}-\d{1,2}\s+\d{1,2}:\d{2})/);
                if (timeMatch) {
                    time = timeMatch[1];
                }

                // 查找点赞按钮
                const likeBtn = parent.querySelector('button[description*="赞"]');
                if (likeBtn) {
                    const likeText = likeBtn.textContent?.trim();
                    if (likeText && likeText !== '赞') {
                        likes = parseInt(likeText) || 0;
                    }
                }

                parent = parent.parentElement;
                searchDepth++;
            }

            if (content && content.length >= 2) {
                comments.push({
                    username,
                    content,
                    time,
                    likes
                });
            }
        });

        return comments;
    }
    """

    try:
        result = await page.evaluate_js(js_code)
        comments = []
        for item in result:
            comment = Comment(
                username=item['username'],
                content=item['content'],
                time=item['time'],
                likes=item['likes']
            )
            comments.append(comment)
        return comments
    except Exception as e:
        print(f"提取评论失败: {e}")
        return []


async def scrape_all_weibo_comments(url: str, max_iterations: int = 100):
    """
    系统化爬取所有微博评论

    Args:
        url: 微博文章URL
        max_iterations: 最大点击次数
    """

    # 导入MCP连接器
    import sys
    sys.path.insert(0, str(Path(__file__).parent))

    print("\n" + "="*60)
    print("📊 微博评论完整爬取")
    print("="*60 + "\n")

    print(f"📍 目标URL: {url}")
    print(f"🎯 目标评论数: 680条")
    print(f"🔄 最大迭代次数: {max_iterations}\n")

    # 使用MCP Chrome DevTools
    from mcp_connector import MCPConnector

    mcp = MCPConnector()

    print("1️⃣  打开页面...")
    page = await mcp.open_page(url)
    print("   ✅ 页面已打开\n")

    # 等待页面加载
    await asyncio.sleep(3)

    all_comments = {}
    last_count = 0
    no_new_count = 0

    print("2️⃣  开始加载和提取评论...")

    for i in range(max_iterations):
        # 提取当前页面的评论
        comments = await extract_comments_from_page(page)

        # 去重并添加到总列表
        new_count = 0
        for comment in comments:
            if comment.unique_id not in all_comments:
                all_comments[comment.unique_id] = comment
                new_count += 1

        current_total = len(all_comments)

        # 进度显示
        if i % 5 == 0 or i == 0:
            print(f"   迭代 {i+1:3d}: {current_total:3d} 条评论 (新增: {new_count})")

        # 检查是否达到目标
        if current_total >= 680:
            print(f"\n   🎉 已达到目标评论数: {current_total}条")
            break

        # 检查是否有新评论
        if current_total == last_count:
            no_new_count += 1
            if no_new_count >= 5:
                print(f"\n   ⚠️  连续5次无新评论，停止")
                break
        else:
            no_new_count = 0
            last_count = current_total

        # 点击"加载更多"
        try:
            click_js = """
            () => {
                const loadMoreBtn = Array.from(document.querySelectorAll('*')).find(el =>
                    el.textContent && el.textContent.includes('点击加载更多')
                );
                if (loadMoreBtn) {
                    loadMoreBtn.click();
                    return true;
                }
                return false;
            }
            """
            clicked = await page.evaluate_js(click_js)

            if not clicked:
                print(f"\n   ⚠️  未找到'加载更多'按钮")
                break

        except Exception as e:
            print(f"\n   ❌ 点击失败: {e}")
            break

        # 等待加载
        await asyncio.sleep(1.5)

    print(f"\n3️⃣  评论提取完成!")
    print(f"   总计: {len(all_comments)} 条评论\n")

    # 保存评论数据
    output_dir = Path.home() / 'comment-analysis-reports'
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f'weibo_raw_comments_{timestamp}.json'

    comments_list = [c.to_dict() for c in all_comments.values()]

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'url': url,
            'total_count': len(comments_list),
            'extracted_at': datetime.now().isoformat(),
            'comments': comments_list
        }, f, ensure_ascii=False, indent=2)

    print(f"💾 评论数据已保存: {output_file}\n")

    # 打印部分评论示例
    print("="*60)
    print("📋 评论预览 (前10条)")
    print("="*60 + "\n")

    for i, comment in enumerate(list(all_comments.values())[:10]):
        print(f"{i+1}. @{comment.username}")
        print(f"   {comment.content[:100]}...")
        print(f"   {comment.time} | 👍 {comment.likes}")
        print()

    print("="*60)
    print(f"✅ 爬取完成! 共获取 {len(all_comments)} 条评论")
    print(f"📁 数据文件: {output_file}")
    print("="*60 + "\n")

    return comments_list


if __name__ == "__main__":
    import sys

    url = "https://weibo.com/7985254173/QmWvGrm7G#comment"

    if len(sys.argv) > 1:
        url = sys.argv[1]

    asyncio.run(scrape_all_weibo_comments(url))
