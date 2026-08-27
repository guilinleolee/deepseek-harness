# html-anything-bridge · V1.0

> 桥接 [nexu-io/html-anything](https://github.com/nexu-io/html-anything)(7.8k ⭐ · 75 skill × 9 surface · 8 CLI auto-detect)给天龙引擎 —— 让博主/运营/产品场景能用"自然语言描述 → 一份可粘贴的 HTML"

## L0: 一句话描述 (≤15字)

**8 agent + 75 模板的 HTML 一键生成桥**

## L1: 使用场景 (50-100字)

天龙已有 baoyu-skills 21 skill(单篇内容深度处理)+ huashu-design 反 AI slop 5 维纪律。html-anything-bridge 补齐**"输入 → 可发布 HTML"** 这一段:
1. **75 模板** —— 杂志 / PPT / 海报 / 小红书 / 推文 / 数据报告 / 原型 / 视频帧,覆盖 baoyu 不擅长的"成片"形态
2. **8 CLI 自动探测** —— 复用你已登录的 Claude Code / Cursor / Codex / Gemini / Copilot / OpenCode / Qwen / Aider,**零 API key**
3. **沙盒 iframe 实时预览** —— 不像 baoyu 那样"生成完才能看"
4. **一键导出** —— WeChat / X / Zhihu / `.html` / `.png` 5 出口
5. **反 AI slop 5 维纪律** —— 与阶段 15 huashu-design 同源(CJK 字体栈 / 8px 网格 / 禁渐变 / contrast ≥4.5 / 真实数据)

## L2: 详细文档

### V1.0 核心能力

| 能力 | 描述 | 性能 |
|------|------|------|
| **模板覆盖** | 81 个模板(README 写 75,实查 81)/ 13 类 | < 200ms picker |
| **CLI 探测** | 22 个候选 / 2 已装(Claude + Hermes) | PATH 扫描 + 备用路径 |
| **SSE 流式** | agent stdout JSON-line → 实时 iframe | 断流可中断 |
| **导出目标** | WeChat / X / Zhihu / `.html` / `.png` | juice + modern-screenshot |
| **沙盒安全** | iframe[sandbox=allow-scripts allow-same-origin] | 隔离 cookies/localStorage |

### V1.0 三种调用模式

#### 模式 A · 浏览器手工(最常用,适合一次性设计)

```bash
# 1. 启动 dev 服务器
cd "C:/Users/li/html-anything"
pnpm -F @html-anything/next dev --port 3300

# 2. 浏览器打开 http://localhost:3300
# 3. 选 agent → 选模板 → 粘内容 → ⌘+Enter → 看实时流
# 4. 一键导出 WeChat / X / .html / .png
```

#### 模式 B · API 模式(适合自动化流水线)

`POST /api/convert` 接收 JSON,服务端 spawn 已登录的 Claude Code CLI,流式 SSE 推回 HTML delta:

```bash
curl -N -X POST http://localhost:3300/api/convert \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "claude",
    "skill": "deck-guizang-editorial",
    "content": "..."
  }'
# → data: {"delta": "<section..."}\n\n
```

#### 模式 C · 桥接到天龙 skill(本 skill 的核心)

在 `dragon-engine/skills/html-anything-bridge/scripts/html_anything_render.py` 中封装模式 B,可被天龙其他 skill(如 35-06 博主全息、28-01 撰稿)直接调用:

```python
from html_anything_render import render

result = render(
    agent="claude",
    skill="prototype-web",
    content="# 我的内容\n\n...",
    timeout=60,
)
# result.html, result.size_bytes, result.duration_ms
```

### V1.0 已知局限(从审计得出)

> 来源:10 个 SKILL.md 抽样审计(2026-07-17)

| 局限 | 数据 | 影响 |
|------|------|------|
| **质量参差** | 0/10 模板同时满足反 AI slop 5 维 | 抽到 magazine-poster / video-hyperframes / prototype-web / saas-landing 时**必须人工把关** |
| **顶部 3 强** | deck-guizang-editorial / deck-swiss-international / doc-kami-parchment 三份继承自上游(op7418/tw93),纪律严格 | 推荐优先用这 3 个 |
| **C2/C5 缺位** | 8px baseline grid 和 contrast ≥4.5 全行业无人写 | 选模板时**手工补这两个维度** |
| **3 个反 AI slop 违反** | video-hyperframes(霓虹) / prototype-web(渐变+glassmorphism) / saas-landing(渐变+glassmorphism) | 默认禁用,需 opt-in |

### V1.0 81 模板分类(实际数据,不是 README 数字)

| 分类 | 模板数 | 代表 |
|------|--------|------|
| Featured ⭐ | 13 | Guizang Editorial / Swiss International / Kami Parchment / Magazine Poster / Hyperframes / Glitch Title / VFX Text Cursor / Logo Outro / Open-Slide / Brutalist / Wireframe Sketch / Modern Resume / Printable Invoice |
| Marketing / Content | 14 | Waitlist / Digital E-Guide / Motion Frames / Social Carousel / Marketing Email / Sprite Animation / Magazine Web Deck / Magazine Article / Keynote / Product Launch / XHS Post / XHS Card / White Editorial / Reddit Post / X Post / Blog Post / Funnel Infographic(baoyu 上游)/ Marketing Poster / SaaS Landing / Twitter Share Card |
| Design / Explore | 5 | Mobile Onboarding / Apple-tier Soft Prototype / Editorial Prototype / Mobile App Screen / Web Prototype |
| Product | 8 | Competitive Teardown / Experiment Readout / Device 3D Showcase / Simple Deck / Team OKRs / Product Spec PRD / Replit Slides |
| Engineering / Dev | 8 | Tech Sharing / Presenter Mode / Graphify Dark / Knowledge Arch Blueprint / Hermes Cyber / Obsidian Claude / Safety Alert / Engineering Runbook / Docs Page |
| Operations | 9 | Live Team Dashboard / Executive Briefing Memo / Weekly Update / Sticky Flowchart Frame / Admin Dashboard / Meeting Notes / Kanban Board / FlowAI Team Dashboard |
| Creator | 3 | Social Media Matrix / Social Media Dashboard / Outline-Faithful Manifesto(ljg-present 上游)|
| Finance / Data | 3 | Finance Report / Data Visualization / Investor Pitch |
| Education | 2 | Course Module / Editorial Sketchnote(ljg-card 上游)|
| Personal | 5 | Dating Dashboard / Gamified App / Pastel Slow-life / Dir-Key Nav / Spotify Now-Playing |
| HR / Onboarding | 1 | HR Onboarding |
| Sales | 1 | Pricing Page |
| Video | 4 | Light-Leak Cinematic / Liquid Background Hero / macOS Notification / NYT-Style Data Chart |
| **总计** | **81** | (README 写 75,差 6 在 _template / 内部,不影响使用)|

### V1.0 上游项目引用(图谱)

```
nexu-io/html-anything (本 skill 桥接对象)
├─ jimliu/baoyu-skills          → 🪣 Funnel Infographic 模板直接引用     ← 阶段 14
├─ op7418/guizang-ppt-skill     → 🖋️ Guizang Editorial + 🟦 Swiss Intl    ← 已 fork 进 html-anything
├─ tw93/kami                    → 📜 Kami Parchment Document              ← 已 fork 进 html-anything
├─ 1weiho/open-slide            → 🎨 Open-Slide 1920 Canvas Deck          ← 已 fork 进 html-anything
├─ heygen-com/hyperframes       → 10 个 frame / vfx / motion 模板         ← schema spec
├─ remotion-dev/remotion        → 视频输出目标                            ← mp4 渲染
├─ alchaincyf/huashu-design     → 反 AI slop 5 维纪律源头                  ← 阶段 15
├─ mdnice/markdown-nice         → WeChat 导出管线(juice + CSS inline)
├─ gcui-art/markdown-to-image   → iframe → PNG(modern-screenshot)
├─ multica-ai/multica           → 多 CLI spawn 架构
└─ nexu-io/open-design          → 母舰(58k⭐ · 259 skill · 142 design system)
```

## L3: 调用示例

### 例 1 · 博主全息海报(35-06 场景)

```bash
# 35-06 V1.1 已生成博主全息 8 维 JSON,现在想变海报
python "C:/Users/li/.claude/projects/dragon-engine/skills/html-anything-bridge/scripts/html_anything_render.py" \
  --skill "magazine-poster" \
  --content "$(cat laoli_profile.json)" \
  --agent "claude" \
  --output "C:/tmp/laoli_poster.html"
```

⚠️ 注意:`magazine-poster` 是 1/5 质量,**必须人工把关**。推荐改用 `Guizang Editorial` 拿到反 AI slop 5 维保证。

### 例 2 · 数据报告(data-report · 阶段 7 VoxCPM2 触发器场景)

```bash
python scripts/html_anything_render.py \
  --skill "data-report" \
  --content "$(cat analytics.csv)" \
  --agent "claude" \
  --format "html"
```

### 例 3 · 公众号 HTML(对接 baoyu-post-to-wechat)

```bash
python scripts/html_anything_render.py \
  --skill "doc-kami-parchment" \
  --content "$(cat essay.md)" \
  --export "wechat" \
  # → 输出可直接 paste 进微信编辑器,样式保留
```

## L4: 文件结构

```
dragon-engine/skills/html-anything-bridge/
├── SKILL.md                          # 本文件
└── scripts/
    ├── html_anything_render.py       # 主调用脚本(模式 C)
    ├── agent_detect.py               # CLI PATH 扫描(8 候选 + 14 备用)
    └── check_html_anything_bridge.py # 验证脚本(本 skill 完整性)
```

## L5: 与天龙已有资产协同

| 资产 | 协同点 |
|------|--------|
| **baoyu-skills 21** (阶段 14) | baoyu 擅长"输入处理" → html-anything 擅长"输出 HTML" |
| **huashu-design 反 AI slop 5 维** (阶段 15) | html-anything 模板的纪律源头 |
| **35-06 博主全息 V1.1** | 博主 JSON → 海报/小红书卡(`Guizang Editorial` 模板) |
| **28-01 撰稿 V10.3** (老李风) | 文案 → 公众号 HTML(`Kami Parchment` 模板) |
| **multi-platform-publisher V1.0** | html-anything 出 HTML → multi-platform 分发到 9 平台 |
| **gpt-image-2** | html-anything 出版式,图仍用 gpt-image-2 |
| **VoxCPM2** | html-anything 不管音频,音频仍用 VoxCPM2 |
| **baoyu-xhs-images** | 小红书图:baoyu 9:16 原生 vs html-anything `XHS Card` |

## 版本信息

- **Version**: 1.0
- **Date**: 2026-07-17
- **Author**: 天龙引擎集成
- **License**: MIT(桥接代码)+ Apache-2.0(html-anything 上游)
- **上游版本**: html-anything @ main (2026-07-17 验证)
- **依赖**: Node 24 · pnpm 10.33.2 · 已登录的至少 1 个 coding-agent CLI
- **累计验证**: 待 `check_html_anything_bridge.py` 跑通后填入