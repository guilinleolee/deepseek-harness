#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微博评论自动化爬取SKILL
完全自动化 - 无需手动操作
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

# JavaScript爬取脚本
WEIBO_SCRAPER_JS = """
(function() {
    console.log("🚀 开始微博完整评论爬取");

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
                    console.log('✅ 已切换为"按时间"排序');
                    return true;
                }
            }
        }
        return false;
    }

    // 开始爬取
    async function scrape() {
        console.log('📍 开始爬取流程');

        switchSortOrder();
        await new Promise(r => setTimeout(r, 2000));

        for (let i = 0; i < window.SCROLL_STATS.maxIterations; i++) {
            window.SCROLL_STATS.iterations = i + 1;
            const currentCount = extractCurrentComments();

            if (i % 10 === 0) {
                console.log('📈 [' + (i+1) + '/' + window.SCROLL_STATS.maxIterations + '] 已加载: ' + currentCount + '条');
            }

            if (currentCount >= 680) {
                console.log('🎉 已达到目标: ' + currentCount + '条');
                break;
            }

            if (currentCount === window.SCROLL_STATS.lastCount) {
                window.SCROLL_STATS.noNewCount++;
                if (window.SCROLL_STATS.noNewCount >= 15) {
                    console.log('⚠️  连续无新评论，停止');
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
    print("🔥 微博评论自动化爬取SKILL")
    print("="*70)
    print(f"📍 目标URL: {url}")
    print(f"🎯 目标评论数: 680条")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")

    # 导入MCP工具
    try:
        from mcp__chrome_devtools import new_page, evaluate_js

        print("📖 步骤1: 打开页面...")
        page_info = await new_page(url=url)
        page_id = page_info.get("page_id") if isinstance(page_info, dict) else page_info
        print(f"   ✅ 页面已打开 (ID: {page_id})\n")

        # 等待页面加载
        print("⏳ 等待页面加载...")
        await asyncio.sleep(5)
        print("   ✅ 页面加载完成\n")

        print("📜 步骤2: 注入爬取脚本...")
        print("   ⏳ 脚本执行中，请耐心等待（约4-8分钟）\n")

        # 执行爬取脚本
        result = await evaluate_js(
            page_id=page_id,
            script=WEIBO_SCRAPER_JS
        )

        print("\n📊 步骤3: 提取爬取结果...")

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

        print(f"   ✅ 提取完成: {comments_data.get('count', 0)}条评论\n")

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
        print("📊 爬取完成统计")
        print("="*70)
        print(f"🎯 目标评论数: 680条")
        print(f"✅ 实际提取: {data['actual_count']}条")
        print(f"📈 完成率: {data['completion_rate']}")
        print(f"\n📁 数据文件: {output_file}")
        print("="*70 + "\n")

        # 显示热门评论
        comments = comments_data.get('comments', [])
        comments.sort(key=lambda x: x.get('likes', 0), reverse=True)

        print("💬 热门评论 TOP5:")
        print("-"*70)
        for i, c in enumerate(comments[:5]):
            print(f"{i+1}. @{c.get('username', 'Unknown')} | 👍 {c.get('likes', 0)} | {c.get('time', '')}")
            content = c.get('content', '')[:60]
            print(f"   {content}...")
            print()

        print("="*70)
        print("✅ 自动化爬取完成！")
        print("="*70)

        return str(output_file)

    except ImportError as e:
        print(f"❌ MCP工具导入失败: {e}")
        print("请确保已安装MCP Chrome DevTools")
        return None
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = asyncio.run(auto_scrape_weibo())
    if result:
        print(f"\n✅ 数据已保存到: {result}")
    else:
        print("\n❌ 爬取失败，请检查错误信息")
