# 微博评论自动爬取 - PowerShell脚本
# 完全自动化版本

Write-Host "="*70
Write-Host "Weibo Comment Auto Scraper"
Write-Host "="*70
Write-Host ""

# 目标URL
$url = "https://weibo.com/7985254173/QmWvGrm7G#comment"

Write-Host "Target URL: $url"
Write-Host "Target Count: 680 comments"
Write-Host ""

# 爬取JavaScript代码
$scraperScript = @"
(function(){
    console.clear();
    console.log('Starting Weibo Comment Scraper...');

    window.ALL_COMMENTS = new Map();
    window.SCROLL_STATS = {iterations: 0, lastCount: 0, noNewCount: 0, maxIterations: 200};

    function parseComment(text) {
        const colonIndex = text.indexOf(':');
        if (colonIndex === -1) return null;
        const username = text.substring(0, colonIndex).trim();
        const timeMatch = text.match(/(\d{1,2}-\d{1,2}-\d{1,2})\s+(\d{1,2}:\d{2})/);
        if (!timeMatch) return null;
        const time = timeMatch[1] + ' ' + timeMatch[2];
        const timeStartIndex = text.indexOf(timeMatch[0]);
        let content = text.substring(colonIndex + 1, timeStartIndex).trim();
        content = content.replace(/@[\u4e00-\u9fa5a-zA-Z0-9_]+/g, '').trim();
        content = content.replace(/^:+/, '').trim();
        content = content.replace(/\s+/g, ' ');
        if (content.length < 2) return null;
        const likeMatch = text.match(/(\d+)$/);
        const likes = likeMatch ? parseInt(likeMatch[1]) : 0;
        const uniqueId = username + '_' + content + '_' + time;
        return {username, content, time, likes, uniqueId};
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

        console.log('='.repeat(60));
        console.log('Scraping Complete!');
        console.log('Total: ' + commentsArray.length + ' comments');
        console.log('='.repeat(60));

        return commentsArray;
    }

    return scrape();
})();
"@

# 创建HTML文件用于执行爬取
$htmlContent = @"
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Weibo Auto Scraper</title>
</head>
<body>
    <h1>Weibo Auto Scraper</h1>
    <p>Starting automatic scraping...</p>
    <div id="status"></div>
    <script>
        window.location.href = '$url';
        setTimeout(function() {
            console.log('Page loaded, injecting scraper...');
            $scraperScript
        }, 5000);
    </script>
</body>
</html>
"@

Write-Host "Step 1: Creating automation page..."
$outputPath = "$env:TEMP\weibo_auto_scraper.html"
$htmlContent | Out-File -FilePath $outputPath -Encoding UTF8

Write-Host "Step 2: Opening browser with automation..."
Start-Process $outputPath

Write-Host ""
Write-Host "="*70
Write-Host "Instructions:"
Write-Host "="*70
Write-Host "1. Wait for the browser to open the Weibo page"
Write-Host "2. Open Developer Tools (F12)"
Write-Host "3. Go to Console tab"
Write-Host "4. Copy and paste the scraper script below:"
Write-Host ""
Write-Host $scraperScript
Write-Host ""
Write-Host "="*70
Write-Host "Or use the bookmarklet tool (bookmarklet_installer.html)"
Write-Host "="*70
