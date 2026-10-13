---
name: html-anything-integration
description: nexu-io/html-anything V1.0 — Agentic HTML editor（75 skill × 9 surface · 8 CLI auto-detect · SSE streaming）· 阶段 16
metadata: 
  node_type: memory
  type: project
  originSessionId: a3c1ded7-36bc-4d18-a3bf-0a3827a854cf
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---


# html-anything · nexu-io/html-anything · V1.0

## 仓库画像

| 字段 | 值 |
|---|---|
| GitHub | https://github.com/nexu-io/html-anything |
| ⭐ Stars | **7,808** · 762 forks |
| 创建 / 更新 | 2026-05-11 · 2026-07-17 |
| 语言 | HTML（Next.js 16.2.6 + Turbopack）|
| 许可证 | Apache-2.0 |
| 团队 | [nexu-io/open-design](https://github.com/nexu-io/open-design)（40k⭐ · 200+ contributors）|
| 尺寸 | 33 MB（clone 33M · 528 行 README）|

## 一句话

**Agentic HTML editor** —— 你写 Markdown,本地 CLI agent 生成 HTML,**沙盒 iframe 实时预览**,**一键导出 WeChat / X / Zhihu / `.html` / `.png`**。零 API key,复用你已有的 `claude login` / `cursor login` / `gemini auth` 会话。

## 核心数字

| 维度 | 数字 |
|------|------|
| Skill 模板 | **75 个**（prototype 21 / deck 20 / frame 12 / social 6 / office 14 / doc 2）|
| 输出形态 (surface) | **9 种** · magazine / deck / résumé / poster / XHS card / tweet card / web prototype / data report / Hyperframes video |
| Coding-agent CLI | **8 个** · Claude Code · Cursor Agent · OpenAI Codex · Gemini CLI · GitHub Copilot CLI · OpenCode · Qwen Coder · Aider |
| 上游灵感引用 | 12 个项目（baoyu-skills / open-design / multica / huashu-design / guizang-ppt-skill / kami / open-slide / hyperframes / remotion / mdnice / markdown-to-image）|
| 架构层 | Next.js 16 App Router + Turbopack · React 19 · Tailwind v4 · zustand · child_process.spawn SSE |

## 关键硬约束（每份 SKILL.md 强制）

- **CJK-first 字体栈**：`Noto Sans/Serif SC` / source-han / Inter / Manrope
- **8px baseline grid**：所有 spacing / line-height / font-size 都是 8 的倍数
- **反 AI slop**：圆角 + soft shadow + 不用纯黑/纯白 + contrast ≥ 4.5 + 不许渐变/SVG 库/装饰 emoji
- **不许 lorem ipsum / 占位 URL**：必须用真实数据
- 视觉纪律从 [alchaincyf/huashu-design](https://github.com/alchaincyf/huashu-design) Junior-Designer 模式 → **阶段 15** huashu-design 已集成,这是 HTML Anything 的源头

## 架构闭环

```
Browser (Next.js 16)
  ├─ Editor / upload / 模板 picker / iframe preview
  └─ GET  /api/agents  → 扫 PATH（含 ~/.local/bin / ~/.bun/bin / /opt/homebrew/bin）
                         返回已安装 CLI 列表（json-line wire protocol）
     POST /api/convert → SSE,spawn CLI pipe stdin/stdout
                         stdout JSON-line → text deltas → SSE event
                         → iframe srcdoc append（实时看到 AI 在"画"）
     ├─ 沙盒 iframe[sandbox="allow-scripts allow-same-origin"]
     ├─ 导出：juice(CSS inline,WeChat) · modern-screenshot(PNG) · ClipboardItem
     └─ 安全：Host header allowlist(防 DNS rebinding 攻击 127.0.0.1)
```

## 与天龙引擎的关系

| 关系 | 项目 |
|------|------|
| **上游参考目录**(已被 html-anything 引用) | [JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills) ← 阶段 14 |
| **反 AI slop 源头**(HTML Anything 引用其纪律) | [alchaincyf/huashu-design](https://github.com/alchaincyf/huashu-design) ← 阶段 15 |
| **Agent-detect 灵感**(同架构) | [nexu-io/open-design](https://github.com/nexu-io/open-design)(40k⭐) |
| **多 CLI spawn 借鉴** | [multica-ai/multica](https://github.com/multica-ai/multica) |
| **WeChat 导出管线** | [mdnice/markdown-nice](https://github.com/mdnice/markdown-nice) |
| **iframe → PNG** | [gcui-art/markdown-to-image](https://github.com/gcui-art/markdown-to-image) |

**关键判断**:html-anything **不是天龙的协同项**,而是 **baoyu-skills + huashu-design 的"上游参照系"**。它本身是 15 MB Web 应用,而非可分发的 skill。

## 本地安装验证 ✅

| 步骤 | 结果 |
|------|------|
| 1. `git clone --depth 1` | ✅ C:\Users\li\html-anything\ · 33 MB |
| 2. `corepack prepare pnpm@10.33.2 --activate` | ✅ pnpm 10.33.2 |
| 3. `pnpm install --frozen-lockfile` | ✅ 166 packages · 3m25s · esbuild postinstall ✅ |
| 4. `pnpm exec tsx scripts/guard.ts` | ✅ Guard passed(形状守卫) |
| 5. `pnpm -F @html-anything/next dev --port 3300` | ✅ Ready in 2.3s · HTTP 200 · 20.2s 首屏编译 |
| 6. `curl /api/agents` | ✅ 检测到 **Claude Code**(D:\NODE\npm-global\claude.CMD · available:true)+ Hermes |
| 7. 浏览器实拍 | ✅ "Pick a local code agent" 模态弹出 · 2 已装 / 18 未装 · Claude Code SELECTED |

## 修改记录(对原仓库)

`package.json` 增加 `"pnpm.onlyBuiltDependencies": ["esbuild"]` 字段 — 跳过 pnpm 10 的交互式 `pnpm approve-builds`(TUI 不可用),自动化 esbuild postinstall。

## 验证命令速查

```bash
cd "C:\Users\li\html-anything"
pnpm install --frozen-lockfile
pnpm exec tsx scripts/guard.ts                  # 形状守卫
pnpm -F @html-anything/next dev --port 3300     # → http://localhost:3300
pnpm -F @html-anything/next typecheck
pnpm -F @html-anything/e2e typecheck
pnpm -F @html-anything/e2e test                # Playwright
```

## 未来候选(阶段 17+)

- 把 huashu-design 的 **5 维自我批判**协议反向灌入 baoyu-skills 21 个 skill 的 SKILL.md frontmatter(强化反 AI slop)
- 把 html-anything 的 **75 个 SKILL.md 调色板 + 硬约束**做横向对比报告,识别可复用到天龙的 N 个模式
- 下一批博主 IP 入驻时,直接用 html-anything 的 prototype-web / magazine-poster 做"个人主页 / 海报"一键生成
- 跟进 open-design(40k⭐)主项目 —— 那是 html-anything 的"母舰"

**Why:** html-anything 是 baoyu-skills + huashu-design 的上游参照项目,但**本身不是 skill**(是 33 MB Next.js Web 应用)。理解它的设计纪律(SKILL.md 硬约束 / 75 模板分类 / 反 AI slop 5 维)和它引用的上游(baoyu / huashu / open-design / multica),能让天龙阶段 14-15 的价值更清晰。

**How to apply:** 当用户问"baoyu-skills 是不是从某个上游借鉴的 / 反 AI slop 5 维是哪 5 维 / 75 个 skill 模板怎么分类",优先引用本主题文件 + 阶段 14-15 的 baoyu-skills / huashu-design 主题。

相关：[[baoyu-skills-integration]] · [[huashu-design-integration]]