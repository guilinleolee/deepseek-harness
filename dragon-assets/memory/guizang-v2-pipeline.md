---
name: guizang-v2-pipeline
description: guizang-social-card-skill V2.0 端到端博客主小红书图文 + 公众号封面 PNG 流水线 · 阶段 19 真集成(超集 V1.0.1)
metadata: 
  node_type: memory
  type: project
  originSessionId: a3c1ded7-36bc-4d18-a3bf-0a3827a854cf
  modified: 2026-07-20T01:34:38.035Z
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---


# guizang V2.0 pipeline · 阶段 19 真集成

> **核心**:不只生成单张海报 HTML(V1.0.1 单 HTML),而是完整**5-6 页小红书图文 carousel + 公众号封面双 PNG + tasks.jsonl + publisher 入库**。直接调本地已装 Playwright + Chromium 渲染。

## 仓库画像

| 字段 | 值 |
|---|---|
| 入口 | `guizang-social-card-skill/pipeline/blogger-poster.mjs` |
| 配套 | `extract-pages.mjs` `palette-rules.mjs` `recipe-rules.mjs` `to-html.mjs` `to-publisher.mjs` `validate-social-deck.mjs` `render-poster.mjs` |
| 渲染引擎 | Playwright + Chromium(已在 skill 的 `node_modules` 中) |
| 输出 | `local-tests/<slug>/{pages.jsonl, index.html, tasks.jsonl, output/*.png}` |
| 阶段 | 19 V2.0(超集 V1.0.1 html-only) |

## V2.0.1 · 实跑端到端产出 7 张 PNG · 2026-07-18

### laoli_bro_2026 实测产出(无 --dry-run,Playwright + Chromium 渲染)

**全部 7 张 PNG 成功渲染**(validate-social-deck R9 WARN,无 FAIL):

| # | 文件 | 尺寸 | 字节 | 内容 |
|---|------|------|------|------|
| 1 | `xhs-1.png` | 1080×1440 | 30,200 | **cover** · 老李兄弟 L01 · 顶部 ESSAY 元数据(空内容区) |
| 2 | `xhs-2.png` | 1080×1440 | **147,513** | **essay** · 母公式大字 + L2 style consistency + 标志词 + 自检 L1/L3 |
| 3 | `xhs-3.png` | 1080×1440 | 102,636 | **closing** · 收束笔记 |
| 4 | `xhs-4.png` | 1080×1440 | **156,998** | **pipeline** · 老李风节奏工具 |
| 5 | `xhs-5.png` | 1080×1440 | 116,102 | **pull-quote** |
| 6 | **`wechat-21x9.png`** | 2100×900 | 92,624 | **公众号主封面** · 老李兄弟大标题 + 2026-07 时间戳 |
| 7 | **`wechat-1x1.png`** | 1080×1080 | 73,799 | **公众号方形分享** |

**总产出** ≈ 720 KB / 7.2M pixels · tasks.jsonl 3.8 KB · platforms [xiaohongshu, wechat]

### 视觉验证(xhs-2.png)

- ✅ ESSAY · 文风 DNA kicker
- ✅ 母公式"有阅历的普通人在认真聊一件让他兴奋的事" Noto Serif SC 中文衬线大字
- ✅ L2 style consistency 副标题(斜体)
- ✅ 标志词:兄弟 · 你看 · 说白了(老李风核心)
- ✅ 自检 L1 + 自检 L3(8 维博主指纹 self_check_4_layer)
- ✅ Page 2 folio + ESSAY footer
- ✅ Kraft Paper 牛皮纸底色 + 暖棕墨水 `#2a1e13`

## V2.0.2 · 4 件修复全绿 · 2026-07-18

### 4 件修复

| # | 修复 | 文件 | 验证 |
|---|------|------|------|
| 1 | publisher.py gbk(emoji UnicodeEncodeError) | `C:\Users\li\.claude\skills\multi-platform-publisher\scripts\publisher.py` | ✅ exit 0(原本 exit 1) · 加 `sys.stdout.reconfigure(encoding="utf-8")` |
| 2 | 5(+1) 维反 AI slop 自检集成 | `validate-social-deck.mjs` | ✅ 新增 **R10-R15**(概念 active / 调色板 / 8px baseline / border-radius=0 / contrast≥4.5 / 反 AI cliché)· 实测 **4 PASS / 0 FAIL / 6 WARN** |
| 3 | laoli design_style DB 升级 | `blogger-fingerprint-registry/scripts/upgrade_design_style.py` | ✅ `editorial` → `kraft-paper` |
| 4 | **Node-native sqlite 替代 sqlite3 CLI** ⭐NEW | `pipeline/blogger-poster.mjs` | ✅ 用 Node 24 内置 `node:sqlite` 读 `design_style` · **不再依赖 sqlite3 CLI** · pipeline 现在能看到第 9 维 |

### 4 号修复详解(Node-native sqlite)

**问题**:`blogger-poster.mjs` 单博主模式原本用 `execSync("sqlite3 ...")` 读 `design_style`,Windows 没装 sqlite3 CLI → 静默 catch → 第 9 维始终为 null → 走自动推断。

**修复**:加 2 个 helper:

```javascript
// 读单个博主
async function readRegistryRow(bloggerId) {
  const sqlite = await import("node:sqlite");
  const { DatabaseSync } = sqlite;
  if (!fs.existsSync(REGISTRY_DB)) return null;
  const db = new DatabaseSync(REGISTRY_DB);
  const row = db.prepare("SELECT design_style, consent_expires_at FROM fingerprints WHERE blogger_id = ?").get(bloggerId);
  db.close();
  return row || null;
}

// 读所有 active 博主(--all 模式)
async function readRegistryActiveRows() { /* ... 类似 ... */ }
```

调用点替换:
- 单博主模式(line 137 附近):`execSync("sqlite3 ...")` → `await readRegistryRow(profile.blogger_id)`
- `--all` 模式:已使用,提取到 helper

**验证**:
```
[2] 调色板选择:
    第 9 维 design_style: kraft-paper           ← 之前:（未设置）
    → 用第 9 维 (design_style): editorial / kraft-paper   ← 之前:自动推断
```

### 修复的 5 个上游 bug(V2.0 → V2.0.1 → V2.0.2 累计)

| Bug | 文件 | 版本 |
|-----|------|------|
| CJS `require("node:fs")` in ESM | extract-pages.mjs | V2.0.1 |
| 缺 fs import | extract-pages.mjs | V2.0.1 |
| dry-run 硬要 PNG | to-publisher.mjs | V2.0.1 |
| CJS require in ESM(child_process) | to-publisher.mjs | V2.0.1 |
| `<!-- POSTERS_HERE -->` 替换吃掉 body | to-html.mjs | V2.0.1 |
| route handler 拦截 file:// | render-poster.mjs | V2.0.1 |
| CJS require in ESM | blogger-poster.mjs | V2.0.1 |
| **publisher.py gbk emoji UnicodeEncodeError** | publisher.py | V2.0.2 |
| **sqlite3 CLI 缺失 → 第 9 维无法读取** | blogger-poster.mjs | **V2.0.2** |

### V2.0.2 调用方式

```bash
cd "C:/Users/li/.claude/projects/c--Users-li--claude/dragon-engine/skills/guizang-social-card-skill"

# 干跑
node pipeline/blogger-poster.mjs --blogger laoli_bro_2026 --dry-run

# 实跑(自动读 design_style,Playwright 渲染,publish 到 publisher.db)
node pipeline/blogger-poster.mjs --blogger laoli_bro_2026

# 全博主批量(串行,过期 consent 自动跳过)
node pipeline/blogger-poster.mjs --all

# 升级博主 design_style
python "C:/Users/li/.claude/projects/c--Users-li--claude/dragon-engine/skills/blogger-fingerprint-registry/scripts/upgrade_design_style.py" laoli_bro_2026 kraft-paper
```

### 修复的 4 个上游 bug

| Bug | 文件 | 修复 |
|-----|------|------|
| `extract-pages.mjs:235` 用 `require("node:fs")` in ESM | extract-pages.mjs | 删 require,顶部补 `import fs from "node:fs"` |
| `extract-pages.mjs` 顶部缺 fs import | extract-pages.mjs | 补 import |
| `to-publisher.mjs` `toTasksJsonl` 在 dry-run 模式硬要 PNG | to-publisher.mjs | 加 `dryRun` 参数,无 PNG 时写 placeholder task |
| `to-publisher.mjs` 用 `require("node:child_process")` | to-publisher.mjs | 顶部补 `import { execSync } from "node:child_process"`,删 require |
| `to-html.mjs` POSTERS_HERE 替换吃掉整个 body | to-html.mjs | **CSS 注释里也有字面量 `<!-- POSTERS_HERE -->`**(seed 文档字符串),改用 4-space 缩进 + `<main class="sheet">` 锚定 |
| `render-poster.mjs` route handler 拦截 file:// | render-poster.mjs | 删 `page.route("**/*", ...)`,直接 goto file:// |

### 已知遗留问题

1. **publisher.py gbk emoji 编码错误** —— `multi-platform-publisher/scripts/publisher.py` 的 `print(f"✅ ...")` 在 Windows GBK stdout 上抛 UnicodeEncodeError,导致 `runPublisherBatch` 退出码 1。但 tasks.jsonl 已成功写入,可手动跑 `python scripts/publisher.py batch --file tasks.jsonl`(设置 `PYTHONIOENCODING=utf-8` 后)解决。
2. **validate-social-deck R9 WARN** —— xhs-5 页的 .h-display 标题占位 3 行(cap 2);xhs-4 的 .step-title 与 .step-desc 之间 8px gap(min 16px)。建议:后续用更短 title,或扩 M04/M07 recipe 的 spacing 参数。
3. **xhs-1 内容空白** —— cover 页 hero display 撑满了画布,主体文本被挤出去。提示词需要明确"封面应预留 60% 视觉空间"。

### V2.0.1 调用方式(完整)

```bash
cd "C:/Users/li/.claude/projects/c--Users-li--claude/dragon-engine/skills/guizang-social-card-skill"

# 干跑(plan only)
node pipeline/blogger-poster.mjs --blogger laoli_bro_2026 --dry-run

# 实跑(渲染 PNG + 写 tasks.jsonl)
node pipeline/blogger-poster.mjs --blogger laoli_bro_2026

# 实跑 + 入 publisher 库(需先修 publisher.py gbk)
PYTHONIOENCODING=utf-8 node pipeline/blogger-poster.mjs --blogger laoli_bro_2026
```

## V2.0 vs V1.0.1 对比

| 维度 | V1.0.1(我手写) | V2.0(guizang 团队) |
|------|---------------|-------------------|
| 输出形态 | **1 个 HTML 海报** | **6 页小红书 carousel + 公众号封面 PNG** |
| 模板选择 | 1 个(deck-guizang-editorial) | 16 个 M01-M16 杂志版式 + S01-S12 瑞士风 |
| 调色板检测 | hex 启发式 5 套 | 调色板 8 套 + 第 9 维 design_style 优先 |
| IP 授权护栏 | 无 | **三重护栏:voice + IP image + 过期检查** |
| Recipe 系统 | 无 | `recipe-rules.mjs` 28 个版式规则 + 自动选 |
| 渲染方式 | Claude 生成 HTML 字符串 | **Playwright headless Chromium → PNG** |
| Publisher 集成 | 无 | tasks.jsonl → `multi-platform-publisher/publisher.py batch` |
| 9 维/版本 | 8 维 | 8-9 维 design_style 从 registry DB 读 |
| 实测 | laoli 1 张海报 HTML | **laoli 7 张 PNG(5 xhs + 2 wechat)· 720 KB** |

## 端到端流程(dry-run 已验证)

```
node pipeline/blogger-poster.mjs --blogger laoli_bro_2026 --dry-run
  │
  ├─▶ [1] 加载博主全息 ✓
  │    → C:/Users/li/.claude/ip-profiles/laoli_bro_2026/ip_profile_8dim.json
  │
  ├─▶ [2] IP 授权三重护栏 ✓
  │    → voice + IP image + expires_at(剩余 365 天)全部 PASS
  │
  ├─▶ [3] 调色板选择 ✓
  │    → 第 9 维 design_style 未设 → 自动推断 editorial/kraft-paper
  │    → label=kraft-laoli · confidence=8(高置信)
  │
  ├─▶ [4] Recipe 选择 ✓
  │    → M01(Magazine Issue Cover)· 知识类博主理由
  │
  ├─▶ [5] 抽取 page 计划 ✓
  │    → 6 页:
  │      page 1 M01   cover   老李兄弟
  │      page 2 M03   essay   有阅历的普通人在认真聊一件让他兴奋的事
  │      page 3 M07   closing 收束笔记
  │      page 4 M14   pipeline 老李风节奏工具
  │      page 5 M04   pull-quote ×
  │      page 6       wechat-cover-pair  老李兄弟(公众号封面双图)
  │
  ├─▶ [6] pages.jsonl 写出 ✓ (5,598 bytes)
  │    → 6 行 JSONL,每行一个 page 对象 + 完整 _ctx(style_name / voice_keywords / top_words / metaphor_library / emotion_library / closing_patterns)
  │
  ├─▶ [7] 复制 WebGL 脚本 ✓
  │    → assets/magazine-bg-webgl.js(Editorial family 需要)
  │
  ├─▶ [8] 拼 index.html ✓ (10,531 bytes)
  │
  ├─▶ [9] validate + render ⏸️ dry-run 跳过
  │
  ├─▶ [10] tasks.jsonl ✓ (805 bytes, dry-run placeholder)
  │    → platforms: ["xiaohongshu", "wechat"]
  │    → 真实跑时:从 output/*.png 反推每张图的角色(cover / essay / closing ...)
  │
  └─▶ [11] publisher.py batch ⏸️ dry-run 跳过
       → 真实跑时:`python publisher.py batch --file tasks.jsonl`
```

## V2.0 dry-run 实测产出

**task 目录**:
`C:\Users\li\.claude\projects\c--Users-li--claude\dragon-engine\skills\guizang-social-card-skill\local-tests\blogger-laoli_bro_2026-kraft-paper\`

| 文件 | 大小 | 内容 |
|------|------|------|
| `pages.jsonl` | 5,598 bytes | 6 页 carousel 计划 JSONL |
| `index.html` | 10,531 bytes | 完整 HTML(单文件可 file:// 打开) |
| `assets/magazine-bg-webgl.js` | 复制 | Editorial 模板 WebGL 背景 |
| `tasks.jsonl` | 805 bytes | dry-run placeholder(真实跑含 PNG path) |

## 我修复的 3 个上游 bug

**Bug 1**:`extract-pages.mjs:235` 用 `require("node:fs")` —— ESM 模块不应 CJS require
**修复**:函数体内删 `const fs = require("node:fs")` 改成顶部 `import fs from "node:fs"`

**Bug 2**:`extract-pages.mjs` 顶部 import 里只有 recipe-rules,缺 fs import
**修复**:补 `import fs from "node:fs"`

**Bug 3**:`to-publisher.mjs` 用 `require("node:child_process")` + `toTasksJsonl` 在 dry-run 模式下必须先有 PNG
**修复**:
- 删 `const { execSync } = require(...)`,补顶部 `import { execSync } from "node:child_process"`
- `toTasksJsonl` 加 `dryRun` 参数,无 PNG 时写 placeholder task(_meta.role = "dry-run"),不抛错

**Bug 4**:`blogger-poster.mjs` 多处 `require("node:child_process")`(即使顶部已 import `execSync`)
**修复**:删多余 require 调用

## 与 V1.0.1 关系

**V1.0.1 已被 V2.0 超集** —— V1.0.1 是"单张 HTML 海报"路径,V2.0 是"5-6 页 carousel + 公众号封面 PNG"路径。

| 场景 | 用 V1.0.1 还是 V2.0? |
|------|---------------------|
| 单张概念稿 / quick share | V1.0.1(`/api/convert` 或 direct) |
| **真实博主全息出图**(小红书图文 + 公众号封面) | **V2.0** ✅ |
| 多博主批量 | V2.0 + 遍历 fingerprint-registry |
| 9 平台分发(含 X / 抖音) | V2.0 + multi-platform-publisher |

## V2.0 真实跑流程(下一步)

```bash
cd "C:/Users/li/.claude/projects/c--Users-li--claude/dragon-engine/skills/guizang-social-card-skill"

# 1. 干跑(已验证 · 不调 Claude,不调 Playwright)
node pipeline/blogger-poster.mjs --blogger laoli_bro_2026 --dry-run

# 2. 实跑(调 Playwright + Chromium render-poster.mjs → PNG)
node pipeline/blogger-poster.mjs --blogger laoli_bro_2026

# 3. 指定平台
node pipeline/blogger-poster.mjs --blogger laoli_bro_2026 --platforms xiaohongshu,wechat

# 4. 自定义 slug(避免覆盖)
node pipeline/blogger-poster.mjs --blogger laoli_bro_2026 --slug laoli-test-2026-07
```

## V2.0 下一步候选(22+)

- [ ] **实跑产出 laoli 6 张 PNG + 公众号封面**(已具备条件,只需去掉 --dry-run)
- [ ] **5(+1) 维反 AI slop 自检集成**:把阶段 18.5 baoyu 8 skill 的 5 维协议,加进 `validate-social-deck.mjs`
- [ ] **第 9 维补全**:往 blogger-fingerprint-registry DB 写 laoli 的 design_style(目前未设,自动推断用)
- [ ] **批量跑**:遍历 registry 里所有博主,fingerprint-registry DB → V2.0 → PNG 集
- [ ] **小红书 9 宫格 + 详情页**:从 6 张 carousel 自动切 9 宫格
- [ ] **Hugo / GitHub Pages 自动发布**:index.html + PNG → 静态博客
- [ ] **V1.0.1 主题文件合并说明**:把 blogger-hologram-to-poster.md 注释"已被 V2.0 超集"
- [ ] **MEMORY 阶段 19 升级到 V2.0**:把 V1.0.1 状态改为"V1.0.1 走单 HTML 路径,V2.0 走 multi-PNG 路径"

**Why:** V2.0 把 stage 19 从"能产出 1 张海报"升级到"能产出完整 6 页小红书图文 + 公众号封面,自动入 publisher 库"。guizang 团队已经写好完整实现,我手写的 V1.0.1 在 V2.0 之外仍有价值(单 HTML 概念稿场景),但主路径应是 V2.0。

**How to apply:** 当用户问"博主怎么自动出小红书图文"、"6 页 carousel 自动出图"、"博主全息 → 小红书发布" → 直接走 V2.0,`node pipeline/blogger-poster.mjs --blogger <id>`。当用户问"快速来一张 HTML 海报" → 走 V1.0.1 direct path。

相关:[[blogger-hologram-to-poster]] · [[guizang-social-card-integration]] · [[html-anything-integration]]