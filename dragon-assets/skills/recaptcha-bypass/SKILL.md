---
license: UNKNOWN
triggers: ["recaptcha bypass", "recaptcha-bypass"]
---
# recaptcha-bypass
天龙引擎 V11.17 | 来源: CloakHQ/CloakBrowser

## L0: 一句话描述 (≤15字)
reCAPTCHA v3评分获取绕过套件

## L1: 使用场景 (50-100字)
当需要绕过Cloudflare/reCAPTCHA保护、获取人类级评分(≥0.9)时，通过2Captcha API或CloakBrowser本地模式获取reCAPTCHA v3评分，辅助隐身路由决策和自动化任务执行。

## L2: 详细文档

### 核心能力

| 能力 | 脚本 | 功能 |
|------|------|------|
| **评分获取** | `recaptcha_score.py` | reCAPTCHA v3评分获取，支持API/本地双模式 |
| **批量处理** | `recaptcha_score.py` | 多站点批量评分 + Markdown报告生成 |
| **阈值判断** | 内置 | ≥0.9高可信/≥0.7可信/≥0.5可疑/<0.5拒绝 |

### 双模式架构

```
┌─────────────────────────────────────────────────────────────┐
│                     reCAPTCHA评分获取                         │
├─────────────────────────────────────────────────────────────┤
│  模式1: 2Captcha API (默认)                                │
│  ├── 适用: 无CloakBrowser环境                              │
│  ├── 依赖: 2Captcha API Key ($0.0029/token)               │
│  └── 端点: https://2captcha.com/res.php                   │
│                                                             │
│  模式2: CloakBrowser本地 (备选)                            │
│  ├── 适用: 已部署CloakBrowser环境                         │
│  ├── 依赖: cloakbrowser Python包                          │
│  └── 优势: 零成本                                         │
└─────────────────────────────────────────────────────────────┘
```

### 评分阈值判定

| 分数范围 | 解释 | 行动建议 |
|----------|------|---------|
| **≥0.9** | 高可信用户，几乎确定是人类 | 允许操作 |
| **≥0.7** | 可信用户 | 建议允许 |
| **≥0.5** | 可疑用户 | 建议二次验证 |
| **<0.5** | 极低可信，极可能是机器人 | 拒绝或降级 |

### 使用场景

- **评分获取**: 获取目标站点reCAPTCHA评分用于路由决策
- **批量评估**: 评估多个站点的CAPTCHA风险等级
- **决策辅助**: 结合StealthRouter判断是否需要高级隐身配置

### 路由集成

```
reCAPTCHA评分 → StealthRouter → 隐身级别决策

score ≥ 0.7 → 正常流程
score < 0.7 → 考虑降级或使用CloakBrowser
score < 0.5 → 拒绝或强制L2+隐身配置
```

### 命令行使用

```bash
# 单个评分获取
python3 scripts/recaptcha_score.py \
  --site-key "6LeIxAcTAAAAAJcZVRqyHh71UMIEIGQ36IdbBzEd" \
  --page-url "https://example.com/recaptcha-demo" \
  --api-key "YOUR_2CAPTCHA_API_KEY"

# 批量评分获取
python3 scripts/recaptcha_score.py --batch sites.json --json

# JSON格式输出
python3 scripts/recaptcha_score.py --site-key "..." --page-url "..." --json
```

### 批量处理输入格式 (sites.json)

```json
[
  {
    "site_key": "6LeIxAcTAAAAAJcZVRqyHh71UMIEIGQ36IdbBzEd",
    "page_url": "https://example.com/page1",
    "name": "站点1"
  },
  {
    "site_key": "6LcjAsATAAAAA...",
    "page_url": "https://example.com/page2",
    "name": "站点2"
  }
]
```

### 天龙岗位协同

| 岗位 | 协同方式 |
|------|---------|
| **01调研师** | 调研前评估站点CAPTCHA风险 |
| **stealth-browser-orchestrator** | 评分数据 → 路由决策输入 |
| **17-04桌面自动化** | 评分辅助判断登录态需求 |

### 安装验证

```bash
# 验证脚本
python3 scripts/recaptcha_score.py --help

# 依赖检查
pip install httpx
python3 -c "import httpx; print('httpx OK')"
```

### 文件结构

```
recaptcha-bypass/
├── SKILL.md                     # 本文件
└── scripts/
    └── recaptcha_score.py        # reCAPTCHA评分获取脚本
```

### 依赖

- Python 3.8+
- `httpx` (用于API调用)

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-19 | 初始集成，基于 CloakHQ/CloakBrowser |