# 平台抓取策略

## 微博（Weibo）

### 特点
- 使用虚拟滚动技术，DOM只渲染可见评论（约10-15条）
- 支持API拦截，可直接获取完整评论数据
- 需要登录（扫码登录，45秒等待）
- 移动端：m.weibo.cn
- 短链接：t.cn

### API拦截策略（优先）
```javascript
// 监听response事件
page.on('response', async response => {
  const url = response.url();

  // 匹配评论API端点
  if (url.includes('/comments/buildComments')) {
    const json = await response.json();

    // 提取评论数据
    json.data.forEach(comment => {
      allComments.push({
        id: comment.id,
        author: comment.user?.screen_name,
        content: comment.text,
        likes: comment.like_counts,
        publish_time: comment.created_at
      });
    });
  }
});
```

### DOM选择器（备用）
```
.comment-item    # 评论容器
.comment-text    # 评论文本
.comment-user    # 用户信息
.comment-time    # 发布时间
.like-btn        # 点赞数
```

### 配置参数
```json
{
  "LOGIN_WAIT_TIME": 45,
  "MAX_SCROLL_COUNT": 100,
  "SCROLL_DELAY": 1500,
  "EXPAND_REPLIES": true
}
```

## 小红书（Xiaohongshu）

### 特点
- 动态SPA应用
- 需要登录
- 滚动加载评论
- 移动端：m.xiaohongshu.com

### DOM选择器
```
.comment-item      # 评论容器
.comment-text      # 评论文本
.user-name         # 用户信息
.publish-time      # 发布时间
```

### 抓取策略
1. 滚动加载所有评论
2. 提取可见评论数据
3. 重复直到无新内容

## 抖音（Douyin）

### 特点
- 动态SPA应用
- 需要登录
- 有加密参数
- 滚动加载评论

### DOM选择器
```
.comment-item      # 评论容器
.comment-content   # 评论文本
.user-name         # 用户信息
.time              # 发布时间
```

## B站（Bilibili）

### 特点
- 支持API调用
- 部分内容需要登录
- 分页加载评论
- 短链接：b23.tv

### API端点
```
/api/v1/reply  # 评论API
```

### DOM选择器（备用）
```
.reply-item       # 评论容器
.text-con         # 评论文本
.user-name        # 用户信息
.time             # 发布时间
```

## 知乎（Zhihu）

### 特点
- 混合页面（静态+动态）
- 需要登录
- 分页加载评论
- 有IP限制

### DOM选择器
```
.List-item-text     # 评论容器
.RichContent        # 评论文本
.User-name          # 用户信息
.time               # 发布时间
```

## 公众号（WeChat MP）

### 特点
- 静态HTML渲染
- 基本无反爬
- 无需登录
- 直接渲染所有评论

### DOM选择器
```
.comment_item        # 评论容器
.comment_content     # 评论文本
.comment_nickname    # 用户信息
.comment_time        # 发布时间
```

## 通用策略

### 滚动加载
```python
async def scroll_to_load(page):
    last_count = 0
    for i in range(MAX_SCROLL_COUNT):
        # 滚动到底部
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(SCROLL_DELAY)

        # 检查是否有新评论
        current_count = await get_comment_count(page)
        if current_count == last_count:
            no_new_count += 1
            if no_new_count >= NO_NEW_COMMENT_LIMIT:
                break
        else:
            no_new_count = 0
        last_count = current_count
```

### 数据提取
```python
async def extract_comments(page, selectors):
    comments = await page.evaluate(f"""
        () => {{
            return Array.from(document.querySelectorAll('{selectors["comment_item"]}'))
                .map(item => ({{
                    content: item.querySelector('{selectors["comment_text"]}')?.textContent,
                    author: item.querySelector('{selectors["comment_user"]}')?.textContent,
                    time: item.querySelector('{selectors["comment_time"]}')?.textContent,
                    likes: item.querySelector('.like-btn')?.textContent
                }}));
        }}
    """)
    return comments
```

### 登录检测
```python
async def check_login(page):
    # 检测是否需要登录
    login_required = await page.evaluate("""
        () => {
            return document.querySelector('.login-btn') !== null ||
                   document.querySelector('.unlogin') !== null;
        }
    """)

    if login_required:
        print("⚠️ 需要登录，请在45秒内扫码")
        await asyncio.sleep(LOGIN_WAIT_TIME)
```
