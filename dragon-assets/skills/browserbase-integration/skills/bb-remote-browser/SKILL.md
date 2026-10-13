# Browserbase Remote Browser

## L0: 一句话描述 (≤15字)
抗爬浏览器Stealth自动化

## L1: 使用场景 (50-100字)
适用于登录墙/CAPTCHA/反爬网站的抓取与交互。当 Agent-Reach/web-access 遇到 Cloudflare/Akamai/DataDome 等 Anti-Bot 阻断时，使用 Browserbase Remote Browser 作为降级方案。201国家住宅代理 + 自动CAPTCHA破解 + Stealth模式绕过检测。

## L2: 详细文档

### 来源项目
| 项目 | Stars | 核心能力 |
|------|-------|---------|
| [browserbase/skills](https://github.com/browserbase/skills) | 2,557 | Remote浏览器+Anti-Bot+CAPTCHA破解+住宅代理 |

### 核心能力矩阵

| 能力 | 说明 | 天龙现有能力 |
|------|------|------------|
| **Stealth模式** | 绕过Cloudflare/Akamai/DataDome/Imperva检测 | ❌ 无等价 |
| **住宅代理** | 201个国家IP轮换 | ❌ 无等价 |
| **CAPTCHA破解** | reCAPTCHA/hCaptcha自动求解 | ❌ 无等价 |
| **会话持久化** | Chrome Cookie同步到Remote Browser | ❌ 无等价 |

### Anti-Bot Detection

```javascript
const PROTECTION_PATTERNS = {
  cloudflare: {
    headers: ['cf-ray', 'cf-cache-status', '__cfduid'],
    body: ['Checking your browser', 'Cloudflare', 'ray id']
  },
  akamai: {
    headers: ['akamai-origin-hop', 'akamai-x-get-ids-json'],
    body: ['Reference', 'Akamai', 'aka']
  },
  datadome: {
    headers: ['datadome', 'x-datadome'],
    body: ['datadome', 'DDZ', 'datadome-']
  },
  imperva: {
    headers: ['x-cdn', 'x-iinfo'],
    body: ['Incapsula', 'imperva', 'x-cdn']
  }
};
```

### CLI命令

```bash
# Remote浏览器操作
bash ~/.claude/skills/browserbase-integration/scripts/bb-remote-browser.sh open "https://example.com"
bash ~/.claude/skills/browserbase-integration/scripts/bb-remote-browser.sh screenshot "https://example.com"
bash ~/.claude/skills/browserbase-integration/scripts/bb-remote-browser.sh extract "https://example.com" --selector ".content"

# Anti-bot检测
node ~/.claude/skills/browserbase-integration/scripts/bb-detect-antibot.mjs "https://example.com"

# Cookie同步
bash ~/.claude/skills/browserbase-integration/scripts/bb-cookie-sync.sh --chrome --browserbase
```

### 与现有能力协同

```bash
# 受保护网站抓取链路
Agent-Reach/web-access 失败（CAPTCHA/反爬）
    ↓
bb-detect-antibot 检测防护类型
    ↓
bb-remote-browser 绕过反爬抓取
    ↓
天龙07记录师 归档知识
```

### 天龙岗位升级

| 岗位 | 版本 | 新增能力 |
|------|------|---------|
| **01调研师** | V8.85 → V8.87 | Anti-bot检测 + 受保护网站抓取 |
| **04验证师** | V8.75 → V8.76 | UI对抗性测试 + CDP追踪 |

### 版本

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-07 | 初始集成，基于browserbase/skills |