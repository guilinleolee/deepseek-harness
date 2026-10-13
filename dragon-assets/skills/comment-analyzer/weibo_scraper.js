// 微博完整评论爬取脚本 - JavaScript版本
// 在浏览器控制台直接执行

console.log("🚀 开始微博完整评论爬取");

// 全局存储
window.ALL_COMMENTS = new Map();
window.SCROLL_STATS = {
    iterations: 0,
    lastCount: 0,
    noNewCount: 0,
    maxIterations: 200
};

// 解析单条评论
function parseComment(text) {
    const colonIndex = text.indexOf(':');
    if (colonIndex === -1) return null;

    const username = text.substring(0, colonIndex).trim();

    // 匹配时间格式: 26-1-14 13:32
    const timeMatch = text.match(/(\d{1,2}-\d{1,2}-\d{1,2})\s+(\d{1,2}:\d{2})/);
    if (!timeMatch) return null;

    const time = `${timeMatch[1]} ${timeMatch[2]}`;
    const timeStartIndex = text.indexOf(timeMatch[0]);

    // 提取内容
    let content = text.substring(colonIndex + 1, timeStartIndex).trim();

    // 清理@提及
    content = content.replace(/@[\u4e00-\u9fa5a-zA-Z0-9_]+/g, '').trim();
    content = content.replace(/^:+/, '').trim();
    content = content.replace(/\s+/g, ' ');

    if (content.length < 2) return null;

    // 提取点赞数
    const likeMatch = text.match(/(\d+)$/);
    const likes = likeMatch ? parseInt(likeMatch[1]) : 0;

    const uniqueId = `${username}_${content}_${time}`;

    return { username, content, time, likes, uniqueId };
}

// 提取当前页面所有评论
function extractCurrentComments() {
    const commentList = document.querySelector('.wbpro-list');
    if (!commentList) {
        console.log('⚠️  未找到 .wbpro-list');
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
    // 滚动到评论容器底部
    const commentList = document.querySelector('.wbpro-list');
    if (commentList) {
        commentList.scrollTop = commentList.scrollHeight;
    }

    // 滚动到页面底部
    window.scrollTo(0, document.body.scrollHeight);

    // 查找并点击"加载更多"
    const buttons = Array.from(document.querySelectorAll('*')).filter(el => {
        const text = el.textContent || '';
        return (text.includes('加载更多') || text.includes('点击加载') || text.includes('展开'))
            && el.offsetParent !== null;
    });

    if (buttons.length > 0) {
        buttons[0].click();
        console.log('  ✅ 点击了"加载更多"按钮');
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
                btn.click();
                console.log('✅ 已切换为"按时间"排序');
                return true;
            }
        }
    }
    console.log('⚠️  未找到排序按钮');
    return false;
}

// 主爬取函数
async function scrapeAllComments(targetCount = 680) {
    console.log(`\n📍 目标评论数: ${targetCount}条`);
    console.log(`🔄 最大迭代次数: ${window.SCROLL_STATS.maxIterations}`);

    // 切换排序
    console.log('\n📋 步骤1: 切换排序方式');
    switchSortOrder();
    await new Promise(r => setTimeout(r, 2000));

    // 开始滚动加载
    console.log('\n📜 步骤2: 开始滚动加载');

    for (let i = 0; i < window.SCROLL_STATS.maxIterations; i++) {
        window.SCROLL_STATS.iterations = i + 1;

        // 提取评论
        const currentCount = extractCurrentComments();

        // 进度显示
        if (i % 5 === 0 || currentCount >= targetCount) {
            const progress = Math.min(100, (currentCount / targetCount * 100)).toFixed(1);
            console.log(`  📈 [${i+1:3d}/${window.SCROLL_STATS.maxIterations}] 已加载: ${currentCount:3d}条 (${progress}%)`);
        }

        // 检查是否达到目标
        if (currentCount >= targetCount) {
            console.log(`\n🎉 已达到目标评论数: ${currentCount}条`);
            break;
        }

        // 检查是否有新评论
        if (currentCount === window.SCROLL_STATS.lastCount) {
            window.SCROLL_STATS.noNewCount++;
            if (window.SCROLL_STATS.noNewCount >= 15) {
                console.log(`\n⚠️  连续15次无新评论，停止滚动`);
                break;
            }
        } else {
            window.SCROLL_STATS.noNewCount = 0;
            window.SCROLL_STATS.lastCount = currentCount;
        }

        // 执行滚动
        smartScroll();
        await new Promise(r => setTimeout(r, 1200)); // 等待1.2秒
    }

    // 最终提取
    console.log('\n📊 步骤3: 提取所有评论数据');
    const finalCount = extractCurrentComments();
    console.log(`  ✅ 最终提取: ${finalCount}条评论`);

    // 转换为数组并排序
    const commentsArray = Array.from(window.ALL_COMMENTS.values());
    commentsArray.sort((a, b) => b.likes - a.likes);

    return commentsArray;
}

// 导出数据
function exportData(comments, targetCount) {
    const data = {
        url: window.location.href,
        target_count: targetCount,
        actual_count: comments.length,
        completion_rate: (comments.length / targetCount * 100).toFixed(1) + '%',
        extracted_at: new Date().toISOString(),
        comments: comments
    };

    // 下载JSON文件
    const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `weibo_complete_comments_${new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)}.json`;
    a.click();
    URL.revokeObjectURL(url);

    console.log('\n💾 数据已导出');
    return data;
}

// 打印统计摘要
function printSummary(comments, targetCount) {
    console.log('\n' + '='.repeat(70));
    console.log('📊 爬取完成统计');
    console.log('='.repeat(70));
    console.log(`🎯 目标评论数: ${targetCount}条`);
    console.log(`✅ 实际提取: ${comments.length}条`);
    console.log(`📈 完成率: ${(comments.length / targetCount * 100).toFixed(1)}%`);

    if (comments.length >= targetCount) {
        console.log(`🎉 恭喜！已达到目标评论数！`);
    } else {
        const missing = targetCount - comments.length;
        console.log(`⚠️  差距: 还差 ${missing} 条评论`);
    }

    console.log('\n💬 热门评论 TOP5:');
    console.log('-'.repeat(70));
    for (let i = 0; i < Math.min(5, comments.length); i++) {
        const c = comments[i];
        console.log(`${i+1}. @${c.username} | 👍 ${c.likes} | ${c.time}`);
        console.log(`   ${c.content.substring(0, 60)}...`);
    }
    console.log('='.repeat(70));
}

// 执行爬取
console.log('\n⏳ 爬取进行中，请稍候...\n');

scrapeAllComments(680).then(comments => {
    printSummary(comments, 680);
    exportData(comments, 680);
    console.log('\n✅ 爬取完成！');
}).catch(err => {
    console.error('❌ 爬取失败:', err);
});
