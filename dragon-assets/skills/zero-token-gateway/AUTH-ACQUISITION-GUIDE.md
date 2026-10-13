# ChatGPT & Gemini 认证获取指南

## 🎯 概述

本指南帮助你获取 ChatGPT 和 Gemini 的认证信息，用于 Zero Token Gateway 实现零成本AI访问。

---

## 1️⃣ ChatGPT AccessToken 获取

### 方法一：开发者工具获取（推荐）

#### 步骤：

1. **打开 Chrome**，访问 https://chatgpt.com/
2. **登录**你的 OpenAI 账户（Google/Microsoft/Email登录）
3. 按 **F12** 打开开发者工具
4. 切换到 **"Application"** (应用) 标签页
5. 左侧展开 **"Local Storage"** → 点击 **"https://chatgpt.com"**
6. 找到以下键名：
   - `__Secure-next-auth.session-token` ⭐ 最重要
   - `accessToken`
   - 或搜索包含 "token" 的键

7. **复制其值**

### 方法二：Network 请求获取

```
1. 登录 chatgpt.com
2. F12 → Network 标签
3. 刷新页面 (Ctrl+R)
4. 搜索 "session" 或 "backend-api"
5. 找到请求 Headers 中的：
   Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
6. Bearer 后面的 JWT token 就是 accessToken
```

### 方法三：Console 直接提取

在 ChatGPT 页面的 Console 中执行：

```javascript
// 方法1：从 localStorage 获取
for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key.includes('token') || key.includes('session')) {
        console.log(key, ':', localStorage.getItem(key));
    }
}

// 方法2：尝试获取 accessToken
console.log('Session Token:', localStorage.getItem('__Secure-next-auth.session-token'));
```

### ChatGPT 认证格式

```json
{
  "chatgpt": {
    "accessToken": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "cookie": "__Secure-next-auth.session-token=xxx; ..."
  }
}
```

---

## 2️⃣ Gemini 认证获取

Gemini 使用 Google 账户认证，主要是 Cookies。

### 方法一：开发者工具获取 Cookies

#### 步骤：

1. **打开 Chrome**，访问 https://gemini.google.com/
2. **登录**你的 Google 账户
3. 按 **F12** 打开开发者工具
4. 切换到 **"Application"** 标签页
5. 左侧 **"Cookies"** → **"https://gemini.google.com"**
6. 找到重要 Cookies：
   - `SID` ⭐ 最重要
   - `HSID`
   - `SSID`
   - `APISID`
   - `SAPISID`

### 方法二：Console 提取

在 Gemini 页面的 Console 中执行：

```javascript
// 获取所有相关 cookies
const cookies = document.cookie.split('; ').reduce((acc, cookie) => {
    const [key, value] = cookie.split('=');
    acc[key] = value;
    return acc;
}, {});

// 打印重要 cookies
['SID', 'HSID', 'SSID', 'APISID', 'SAPISID'].forEach(key => {
    console.log(key, ':', cookies[key]);
});

// 导出完整 cookie 字符串
console.log('Full Cookie String:', document.cookie);
```

### Gemini 认证格式

```json
{
  "gemini": {
    "cookie": "SID=xxx; HSID=xxx; SSID=xxx; APISID=xxx; SAPISID=xxx"
  }
}
```

---

## 3️⃣ 自动捕获（使用 Zero Token Gateway）

### 步骤：

1. **确保 Chrome 以调试模式运行**：
```bash
# Windows
chrome.exe --remote-debugging-port=9222 --user-data-dir=%USERPROFILE%\AppData\Local\Google\Chrome\User Data
```

2. **在 Chrome 中登录 AI 平台**

3. **运行认证捕获**：
```bash
# 捕获所有平台
node skills/zero-token-gateway/scripts/auth-capture.js --all

# 或单独捕获
node skills/zero-token-gateway/scripts/auth-capture.js --platform chatgpt
node skills/zero-token-gateway/scripts/auth-capture.js --platform gemini
```

---

## 4️⃣ 验证认证是否有效

### 检查已保存的认证：
```bash
# 查看认证文件
cat ~/.openclaw-zero-state/auth.json
```

### 通过 API 测试：
```bash
# 测试 ChatGPT
curl -X POST http://localhost:3002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hello"}]
  }'

# 测试 Gemini
curl -X POST http://localhost:3002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-pro",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

---

## 5️⃣ 常见问题

### Q: 为什么捕获不到 token？

**A:** 可能原因：
1. 未登录 AI 平台
2. Chrome 未以调试模式运行
3. 登录状态已过期

### Q: 认证多久过期？

**A:**
- ChatGPT: 约 7-30 天（取决于登录方式）
- Gemini: 与 Google 账户同步

### Q: 如何刷新认证？

**A:** 重新登录后运行捕获命令即可。

---

## 6️⃣ 安全提醒

⚠️ **重要安全提示：**

1. **不要分享**你的 accessToken 或 cookies
2. 认证文件 (`~/.openclaw-zero-state/auth.json`) 包含敏感信息
3. 仅用于**个人研究和学习**目的
4. 定期检查账户活动

---

## 快速参考

| 平台 | 认证类型 | 关键字段 | 获取位置 |
|------|---------|---------|---------|
| ChatGPT | accessToken + cookie | `__Secure-next-auth.session-token` | localStorage |
| Gemini | cookie | `SID`, `HSID`, `SSID` | Cookies |