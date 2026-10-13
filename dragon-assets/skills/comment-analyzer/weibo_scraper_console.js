/* ============================================================
   微博评论爬取工具 - 控制台版本
   使用方法：在微博页面按F12，切换到Console标签，粘贴此代码并按Enter
   ============================================================ */

(function() {
    console.clear();
    console.log('%c='.repeat(60), 'color: #667eea');
    console.log('%c微博评论爬取工具启动中...', 'color: #667eea; font-size: 16px; font-weight: bold');
    console.log('%c='.repeat(60), 'color: #667eea');

    // 检查是否在正确的页面
    if (!window.location.href.includes('weibo.com')) {
        console.error('❌ 错误：请在微博页面使用此工具');
        return;
    }

    // 全局变量
    window.ALL_COMMENTS = new Map();
    window.SCROLL_STATS = {
        iterations: 0,
        lastCount: 0,
        noNewCount: 0,
        maxIterations: 200
    };

    // 解析评论
    function parseComment(text) {
        const colonIndex = text.indexOf(':');
        if (colonIndex === -1) return null;

        const username = text.substring(0, colonIndex).trim();

        // 匹配时间格式: 26-1-14 13:32
        const timeMatch = text.match(/(\d{1,2}-\d{1,2}-\d{1,2})\s+(\d{1,2}:\d{2})/);
        if (!timeMatch) return null;

        const time = timeMatch[1] + ' ' + timeMatch[2];
        const timeStartIndex = text.indexOf(timeMatch[0]);

        let content = text.substring(colonIndex + 1, timeStartIndex).trim();

        // 清理内容
        content = content.replace(/@[\u4e00-\u9fa5a-zA-Z0-9_]+/g, '').trim();
        content = content.replace(/^:+/, '').trim();
        content = content.replace(/\s+/g, ' ');

        if (content.length < 2) return null;

        // 提取点赞数
        const likeMatch = text.match(/(\d+)$/);
        const likes = likeMatch ? parseInt(likeMatch[1]) : 0;

        const uniqueId = username + '_' + content + '_' + time;

        return {
            username: username,
            content: content,
            time: time,
            likes: likes,
            uniqueId: uniqueId
        };
    }

    // 提取当前页面评论
    function extractCurrentComments() {
        const commentList = document.querySelector('.wbpro-list');

        if (!commentList) {
            console.warn('⚠️ 未找到评论列表 .wbpro-list');
            return 0;
        }

        const nodes = commentList.children;
        let newCount = 0;

        for (let i = 0; i < nodes.length; i++) {
            const text = nodes[i].textContent || '';
            const comment = parseComment(text);

            if (comment && !window.ALL_COMMENTS.has(comment.uniqueId)) {
                window.ALL_COMMENTS.set(comment.uniqueId, comment);
                newCount++;
            }
        }

        return window.ALL_COMMENTS.size;
    }

    // 智能滚动
    function smartScroll() {
        // 滚动评论列表
        const commentList = document.querySelector('.wbpro-list');
        if (commentList) {
            commentList.scrollTop = commentList.scrollHeight;
        }

        // 滚动页面
        window.scrollTo(0, document.body.scrollHeight);

        // 查找并点击"加载更多"按钮
        const buttons = Array.from(document.querySelectorAll('*')).filter(el => {
            const text = el.textContent || '';
            return (text.includes('加载更多') ||
                   text.includes('点击加载') ||
                   text.includes('展开')) &&
                   el.offsetParent !== null;
        });

        if (buttons.length > 0) {
            console.log('📜 找到加载按钮，点击加载...');
            buttons[0].click();
        }
    }

    // 切换排序方式
    function switchSortOrder() {
        const sortButtons = Array.from(document.querySelectorAll('*')).filter(el => {
            const text = el.textContent || '';
            return text.includes('按时间') || text.includes('按热度');
        });

        if (sortButtons.length > 0) {
            for (const btn of sortButtons) {
                if (btn.textContent.includes('按时间')) {
                    console.log('🔄 切换到"按时间"排序');
                    btn.click();
                    return true;
                }
            }
        }
        return false;
    }

    // 主爬取函数
    async function scrape() {
        console.log('🚀 开始爬取...');

        // 切换排序
        switchSortOrder();
        await new Promise(r => setTimeout(r, 2000));

        // 检查初始评论数
        const initialCount = extractCurrentComments();
        console.log(`📊 初始评论数: ${initialCount}`);

        // 开始滚动循环
        for (let i = 0; i < window.SCROLL_STATS.maxIterations; i++) {
            window.SCROLL_STATS.iterations = i + 1;

            const currentCount = extractCurrentComments();

            // 每10次输出进度
            if (i % 10 === 0) {
                console.log(`[${i+1}/${window.SCROLL_STATS.maxIterations}] 已加载: ${currentCount} 条评论`);
            }

            // 检查是否达到目标
            if (currentCount >= 680) {
                console.log(`%c✅ 达到目标: ${currentCount} 条评论`, 'color: #28a745; font-weight: bold');
                break;
            }

            // 检查是否没有新评论
            if (currentCount === window.SCROLL_STATS.lastCount) {
                window.SCROLL_STATS.noNewCount++;
                if (window.SCROLL_STATS.noNewCount >= 15) {
                    console.log('%c⚠️ 连续15次无新评论，停止爬取', 'color: #ffc107; font-weight: bold');
                    break;
                }
            } else {
                window.SCROLL_STATS.noNewCount = 0;
                window.SCROLL_STATS.lastCount = currentCount;
            }

            smartScroll();
            await new Promise(r => setTimeout(r, 1200));
        }

        // 排序评论
        const commentsArray = Array.from(window.ALL_COMMENTS.values());
        commentsArray.sort((a, b) => b.likes - a.likes);

        console.log('%c='.repeat(60), 'color: #667eea');
        console.log('%c爬取完成！', 'color: #28a745; font-size: 18px; font-weight: bold');
        console.log(`%c总计: ${commentsArray.length} 条评论`, 'color: #28a745; font-size: 14px; font-weight: bold');
        console.log('%c='.repeat(60), 'color: #667eea');

        return commentsArray;
    }

    // 下载文件
    async function download(data) {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'weibo_comments_' + new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19) + '.json';
        a.click();
        URL.revokeObjectURL(url);
    }

    // 执行爬取
    scrape().then(comments => {
        const data = {
            url: window.location.href,
            target_count: 680,
            actual_count: comments.length,
            completion_rate: (comments.length / 680 * 100).toFixed(1) + '%',
            extracted_at: new Date().toISOString(),
            comments: comments
        };

        download(data);
        console.log('%c✅ 文件已下载！', 'color: #28a745; font-weight: bold');
        console.log('%c将下载的JSON文件路径发送给Claude即可生成报告', 'color: #17a2b8');
    }).catch(e => {
        console.error('❌ 错误:', e);
    });

})();
