---
license: UNKNOWN
triggers: ["browserbase integration", "Browserbase Integration"]
---
# Browserbase Integration

## L0: 一句话描述 (≤15字)
浏览器自动化平台，抗爬克星

## L1: 使用场景 (50-100字)
适用于登录墙/验证码/反爬网站的抓取与交互、B2B销售线索挖掘、会议演讲嘉宾发现、受保护竞品网站监控、UI对抗性测试等场景。当天龙现有技能（Agent-Reach/web-access）遇到CAPTCHA或反爬阻断时，启用Browserbase作为降级方案。

## L2: 详细文档

### 来源项目

| 项目 | Stars | 核心能力 |
|------|-------|---------|
| [browserbase/skills](https://github.com/browserbase/skills) | 2,557 | Remote浏览器+Anti-Bot+CAPTCHA破解+住宅代理 |

### 核心价值
填补天龙引擎在**抗爬浏览器自动化、B2B销售线索挖掘、会议嘉宾发现**三大关键空白。

### 技能架构

```
browserbase-integration/
├── SKILL.md                    # 本文件
├── scripts/
│   ├── bb-setup.sh           # API Key配置 + CLI安装
│   ├── bb-remote-browser.sh  # Remote模式浏览器封装
│   ├── bb-detect-antibot.mjs # Anti-bot检测脚本
│   ├── bb-cookie-sync.sh    # Cookie同步脚本
│   └── bb-company-research.sh # B2B调研封装
└── skills/
    ├── bb-remote-browser/    # 抗爬浏览器技能
    ├── bb-company-research/   # B2B调研技能
    └── bb-event-prospecting/ # 会议线索技能
```

### 核心能力矩阵

| 能力 | 说明 | 天龙现有能力 |
|------|------|------------|
| **Remote Browser** | Anti-Bot stealth + 201国家住宅代理 | ❌ 无等价 |
| **CAPTCHA Solving** | reCAPTCHA/hCaptcha自动破解 | ❌ 无等价 |
| **Cookie Sync** | Chrome→Browserbase会话同步 | ❌ 无等价 |
| **Anti-bot Detection** | Cloudflare/Akamai/DataDome识别 | ❌ 无等价 |
| **UI Testing** | AI对抗性UI测试 | browser-qa(互补) |
| **Company Research** | ICP评分B2B线索发现 | lead-generation(互补) |
| **Event Prospecting** | 会议演讲嘉宾线索 | ❌ 无等价 |

### CLI命令

```bash
# 安装配置
bash ~/.claude/skills/browserbase-integration/scripts/bb-setup.sh

# Remote浏览器操作
bash ~/.claude/skills/browserbase-integration/scripts/bb-remote-browser.sh open "https://example.com"
bash ~/.claude/skills/browserbase-integration/scripts/bb-remote-browser.sh screenshot "https://example.com"
bash ~/.claude/skills/browserbase-integration/scripts/bb-remote-browser.sh extract "https://example.com" --selector ".content"

# Anti-bot检测
node ~/.claude/skills/browserbase-integration/scripts/bb-detect-antibot.mjs "https://example.com"

# Cookie同步
bash ~/.claude/skills/browserbase-integration/scripts/bb-cookie-sync.sh --chrome --browserbase

# B2B调研
bash ~/.claude/skills/browserbase-integration/scripts/bb-company-research.sh "目标公司关键词"

# 安装@browserbase/skills
npx @browserbase/skills
```

### 天龙岗位升级

| 岗位 | 版本 | 新增能力 |
|------|------|---------|
| **01调研师** | V8.85 → V8.87 | Anti-bot检测 + 受保护网站抓取 |
| **32-01市场研究** | V10.0 → V10.1 | ICP评分 + 会议线索挖掘 |
| **32-02竞品分析** | V1.1 → V1.2 | 受保护竞品网站监控 |
| **38-02销售管理** | - | B2B线索发现 + company-research |
| **04验证师** | V8.75 → V8.76 | UI对抗性测试 + CDP追踪 |

### 协同链路

```bash
# 受保护网站抓取链路
Agent-Reach/web-access 失败（CAPTCHA/反爬）
    ↓
bb-detect-antibot 检测防护类型
    ↓
bb-remote-browser 绕过反爬抓取
    ↓
天龙07记录师 归档知识

# B2B调研链路
bb-company-research ICP评分筛选
    ↓
bb-event-prospecting 会议嘉宾发现
    ↓
38-02销售管理 线索跟进
```

### 安装前置条件

```bash
# 1. 获取Browserbase API Key
#    https://browserbase.com → Dashboard → API Keys

# 2. 设置环境变量
export BROWSERBASE_API_KEY="sk-..."

# 3. 运行安装脚本
bash ~/.claude/skills/browserbase-integration/scripts/bb-setup.sh
```

### 注意事项

- Remote模式需要Browserbase账号（免费额度有限）
- CAPTCHA破解消耗额外积分
- 住宅代理按流量计费
- 与天龙现有web-access/gstack-browse形成互补而非替代

### 版本

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-07 | 初始集成，基于browserbase/skills 2,557 Stars |
