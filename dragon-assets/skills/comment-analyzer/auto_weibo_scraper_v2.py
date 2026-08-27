#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微博评论自动化爬取SKILL
完全自动化 - 无需手动操作
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# 设置控制台输出为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

# JavaScript爬取脚本
WEIBO_SCRAPER_JS = """
(function() {
    console.log("Starting Weibo comment scraper...");

    window.ALL_COMMENTS = new Map();
    window.SCROLL_STATS = {
        iterations: 0,
        lastCount: 0,
        noNewCount: 0,
        maxIterations: 200
    };

    function parseComment(text) {
        const colonIndex = text.indexOf(':');
        if (colonIndex === -1) return null;
        const username = text.substring(0, colonIndex).trim();
        const timeMatch = text.match(/(\\d{1,2}-\\d{1,2}-\\d{1,2})\\s+(\\d{1,2}:\\d{2})/);
        if (!timeMatch) return null;
        const time = timeMatch[1] + ' ' + timeMatch[2];
        const timeStartIndex = text.indexOf(timeMatch[0]);
        let content = text.substring(colonIndex + 1, timeStartIndex).trim();
        content = content.replace(/@[\\u4e00-\\u9fa5a-zA-Z0-9_]+/g, '').trim();
        content = content.replace(/^:+/, '').trim();
        content = content.replace(/\\s+/g, ' ');
        if (content.length < 2) return null;
        const likeMatch = text.match(/(\\d+)$/);
        const likes = likeMatch ? parseInt(likeMatch[1]) : 0;
        const uniqueId = username + '_' + content + '_' + time;
        return { username, content, time, likes, uniqueId };
    }

    function extractCurrentComments() {
        const commentList = document.querySelector('.wbpro-list');
        if (!commentList) return 0;
        const nodes = commentList.children;
        for (let i = 0; i < nodes.length; i++) {
            const text = nodes[i].textContent || '';
            const comment = parseComment(text);
            if (comment && !window.ALL_COMMENTS.has(comment.uniqueId)) {
                window.ALL_COMMENTS.set(comment.uniqueId, comment);
            }
        }
        return window.ALL_COMMENTS.size;
    }

    function smartScroll() {
        const commentList = document.querySelector('.wbpro-list');
        if (commentList) commentList.scrollTop = commentList.scrollHeight;
        window.scrollTo(0, document.body.scrollHeight);
        const buttons = Array.from(document.querySelectorAll('*')).filter(el => {
            const text = el.textContent || '';
            return (text.includes('加载更多') || text.includes('点击加载') || text.includes('展开')) && el.offsetParent !== null;
        });
        if (buttons.length > 0) buttons[0].click();
    }

    function switchSortOrder() {
        const sortButtons = Array.from(document.querySelectorAll('*')).filter(el => {
            const text = el.textContent || '';
            return text.includes('按时间') || text.includes('按热度');
        });
        if (sortButtons.length > 0) {
            for (const btn of sortButtons) {
                if (btn.textContent.includes('按时间')) {
                    btn.click();
                    console.log('Switched to sort by time');
                    return true;
                }
            }
        }
        return false;
    }

    // 开始爬取
    async function scrape() {
        console.log('Starting scraping process...');

        switchSortOrder();
        await new Promise(r => setTimeout(r, 2000));

        for (let i = 0; i < window.SCROLL_STATS.maxIterations; i++) {
            window.SCROLL_STATS.iterations = i + 1;
            const currentCount = extractCurrentComments();

            if (i % 10 === 0) {
                console.log('Progress [' + (i+1) + '/' + window.SCROLL_STATS.maxIterations + '] Loaded: ' + currentCount + ' comments');
            }

            if (currentCount >= 680) {
                console.log('Target reached: ' + currentCount + ' comments');
                break;
            }

            if (currentCount === window.SCROLL_STATS.lastCount) {
                window.SCROLL_STATS.noNewCount++;
                if (window.SCROLL_STATS.noNewCount >= 15) {
                    console.log('No new comments, stopping');
                    break;
                }
            } else {
                window.SCROLL_STATS.noNewCount = 0;
                window.SCROLL_STATS.lastCount = currentCount;
            }

            smartScroll();
            await new Promise(r => setTimeout(r, 1200));
        }

        const commentsArray = Array.from(window.ALL_COMMENTS.values());
        commentsArray.sort((a, b) => b.likes - a.likes);

        return {
            count: commentsArray.length,
            comments: commentsArray
        };
    }

    return scrape();
})();
"""


async def auto_scrape_weibo(url: str = "https://weibo.com/7985254173/QmWvGrm7G#comment"):
    """完全自动化爬取微博评论"""
    print("\n" + "="*70)
    print("Weibo Comment Auto Scraper SKILL")
    print("="*70)
    print(f"Target URL: {url}")
    print(f"Target Count: 680 comments")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")

    # 导入MCP工具
    try:
        from mcp__chrome_devtools import new_page, evaluate_js

        print("Step 1: Opening page...")
        page_info = await new_page(url=url)
        page_id = page_info.get("page_id") if isinstance(page_info, dict) else page_info
        print(f"   OK - Page opened (ID: {page_id})\n")

        # 等待页面加载
        print("Waiting for page to load...")
        await asyncio.sleep(5)
        print("   OK - Page loaded\n")

        print("Step 2: Injecting scraper script...")
        print("   Script is running, please wait (about 4-8 minutes)\n")

        # 执行爬取脚本
        result = await evaluate_js(
            page_id=page_id,
            script=WEIBO_SCRAPER_JS
        )

        print("\nStep 3: Extracting scraped data...")

        # 获取评论数据
        comments_data = await evaluate_js(
            page_id=page_id,
            script="""
            (function() {
                const comments = Array.from(window.ALL_COMMENTS || []).map(c => c[1]);
                return {
                    count: comments.length,
                    comments: comments
                };
            })();
            """
        )

        print(f"   OK - Extracted: {comments_data.get('count', 0)} comments\n")

        # 保存数据
        output_dir = Path.home() / 'comment-analysis-reports'
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f'weibo_auto_comments_{timestamp}.json'

        data = {
            'url': url,
            'target_count': 680,
            'actual_count': comments_data.get('count', 0),
            'completion_rate': f"{comments_data.get('count', 0) / 680 * 100:.1f}%",
            'extracted_at': datetime.now().isoformat(),
            'comments': comments_data.get('comments', [])
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print("="*70)
        print("Scraping Complete Statistics")
        print("="*70)
        print(f"Target Count: 680 comments")
        print(f"Actual Count: {data['actual_count']} comments")
        print(f"Completion Rate: {data['completion_rate']}")
        print(f"\nData File: {output_file}")
        print("="*70 + "\n")

        # 显示热门评论
        comments = comments_data.get('comments', [])
        comments.sort(key=lambda x: x.get('likes', 0), reverse=True)

        print("Top 5 Comments by Likes:")
        print("-"*70)
        for i, c in enumerate(comments[:5]):
            print(f"{i+1}. @{c.get('username', 'Unknown')} | Likes: {c.get('likes', 0)} | {c.get('time', '')}")
            content = c.get('content', '')[:60]
            print(f"   {content}...")
            print()

        print("="*70)
        print("Auto Scraping Complete!")
        print("="*70)

        return str(output_file)

    except ImportError as e:
        print(f"ERROR: MCP tools import failed: {e}")
        print("Please ensure MCP Chrome DevTools is installed")
        return None
    except Exception as e:
        print(f"ERROR: Execution failed: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = asyncio.run(auto_scrape_weibo())
    if result:
        print(f"\nOK - Data saved to: {result}")
    else:
        print("\nERROR - Scraping failed, please check error messages")
