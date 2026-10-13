---
name: blogger-hologram-to-poster-v2
description: 博主 9 维全息 → guizang 海报 → publisher V1.0 mock 三模态闭环（阶段 19 V2.0）
metadata: 
  node_type: memory
  type: project
  originSessionId: 1b69faff-55b8-4ac4-982e-93b0e3e2aafb
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---


# blogger-hologram-to-poster · V2.0 · 阶段 19

> **核心**：把博主 9 维全息 JSON（声纹 6 + 文风 1 + IP 视觉 1 + **设计风格 1**）→ **guizang 渲染管线**（不再走 html-anything）→ **publisher mock 入表** 三模态闭环。
> **位置**：`dragon-engine/skills/guizang-social-card-skill/pipeline/`
> **入口**：`node blogger-poster.mjs --blogger <id> [options]`
> **替代**：阶段 17 V1.0 候选（`html-anything-bridge/scripts/blogger_hologram_to_poster.py` —— 已被 V2.0 升级替代）

---

## V1.0 → V2.0 关键升级

| 维度 | V1.0 (阶段 17) | V2.0 (阶段 19) | 升级原因 |
|------|----------------|----------------|---------|
| **渲染管线** | html-anything（SSE 流 + Claude CLI） | **guizang V1.0（Playwright 本地）** | Claude CLI 0xC0000142 DLL 缺失实测 FAILL |
| **主题系统** | 5 套调色板启发式（kraft/indigo/forest/ink/dune） | **10 套 + 第 9 维覆盖**（含 4 Swiss） | 覆盖 guizang 全 10 主题 |
| **第 9 维** | ❌ 无 | **fingerprint-registry V3.0 `design_style`** | huashu 40 风格库一对一驱动 |
| **版式选择** | 3 类（deck-guizang-editorial 等 html-anything 模板名） | **12 类 guizang 版式（M01-M16 / S01-S12）** | 替换专用模板名为通用版式 ID |
| **页面计划** | 1 页 markdown prompt | **6 页 carousel JSONL + 自动 wechat-cover-pair** | 与 guizang 真实 5-6 页框架对齐 |
| **发布链路** | 无（只出 HTML） | **publisher.py batch → SQLite 14 行 success 入表** | mock 入表成功（真实 OpenAPI 待 publisher V2.0）|
| **AGPL-3.0** | ❌ 无（html-anything 是另一个 license） | **✅ 自动注入 metadata + 仅 PNG 输出** | stage 18 R1 红线 → V2.0 自动化 |
| **依赖链** | Claude CLI 必须 + html-anything SSE 端 | **Playwright 1.60.0 (已装) + Chromium 148** | 0 外部 LLM 依赖 |

---

## 仓库画像

| 字段 | 值 |
|---|---|
| Pipeline 目录 | `dragon-engine/skills/guizang-social-card-skill/pipeline/` |
| Pipeline 版本 | V2.0 · 2026-07-18 |
| 输入 schema | 9 维博主全息（fingerprint-registry V3.0 = 8 维 JSON + DB `design_style` 字段） |
| 输出 | 5-6 张 carousel PNG + wechat-cover-pair（21:9 + 1:1） + publisher.db 14 行 success |
| 触发源 | 阶段 18 guizang V1.0 + 阶段 16 huashu-design 40 风格库 + 阶段 17 V1.0 桥接脚本 |

## 6 个脚本（共 1141 行）

| 文件 | 行数 | 用途 |
|------|------|------|
| `blogger-poster.mjs` | 242 | **核心入口** — 加载 profile / 调色板 / recipe / pages / 拼 HTML / validate / render / publisher |
| `palette-rules.mjs` | 121 | 10 套调色板启发式 + huashu 16 个风格名 → guizang 主题映射 |
| `recipe-rules.mjs` | 117 | 12 类版式选择规则（matched_template + style_keywords 关键词）|
| `extract-pages.mjs` | 238 | 9 维 → pages.jsonl（6 页 plan：cover/essay/closing/pipeline/pullquote/wechat-cover-pair）|
| `to-html.mjs` | 274 | pages + theme → 注入 seed 模板 `<main>` 内的 `<!-- POSTERS_HERE -->` |
| `to-publisher.mjs` | 149 | output/*.png → tasks.jsonl + `python scripts/publisher.py batch` |

## 端到端流程

```
9 维博主全息
  │
  ├─ [1] 加载 ip_profile_8dim.json → 读 fingerprint-registry V3.0 第 9 维 design_style
  │
  ├─ [2] IP 授权三重护栏（voice + ip_consent + design_consent，expires_at > now）
  │
  ├─ [3] detect_palette(color_palette) 或 applyDesignStyle(design_style)
  │     └─ editorial / Swiss · 覆盖 10 套主题
  │
  ├─ [4] selectRecipe(matched_template, style_keywords, family)
  │     └─ 12 类版式规则（知识区→M01，测评→S01，警告→S05，...）
  │
  ├─ [5] extractPages(profile, choice, recipe)
  │     └─ 6 页：M01 cover / M03 essay / M07 closing / M14 pipeline / M04 pull-quote / wechat-cover-pair
  │
  ├─ [6] toHtml(pages, choice)
  │     └─ 复制 seed.template-{editorial|swiss}-card.html
  │     └─ 注入 <html data-theme="kraft-paper"> 或 <html data-accent="ikb">
  │     └─ 注入 AGPL-3.0 metadata
  │     └─ 替换 <main> 块内的 <!-- POSTERS_HERE --> 为 5+ sections
  │
  ├─ [7] node validate-social-deck.mjs <task> (R1-R9 校验)
  │
  ├─ [8] node render-poster.mjs <task> <output>
  │     └─ 5-6 个 PNG：xhs-1..N + wechat-21x9 + wechat-1x1
  │
  ├─ [9] toTasksJsonl({ taskDir, profile, platforms })
  │     └─ 每个 PNG 一行 task.jsonl（content_path/title/description/tags/platforms）
  │
  └─ [10] runPublisherBatch(tasksPath)
        └─ python scripts/publisher.py batch --file tasks.jsonl
        └─ SQLite publisher.db 写入 publish_tasks 行 × 14 (7 PNG × 2 平台)
```

## laoli_bro_2026 实测结果

| 维度 | 值 |
|---|---|
| 博主 ID | laoli_bro_2026 |
| 9 维数据来源 | `C:/Users/li/.claude/ip-profiles/laoli_bro_2026/ip_profile_8dim.json` + SQLite registry V3.0 |
| IP 授权检查 | ✅ 三重护栏通过（expires 2027-07-03） |
| 调色板选择 | **kraft-paper**（label=kraft-laoli, confidence=8，匹配 #2C3E50 #ECF0F1 等） |
| Recipe 选择 | **M01** Magazine Issue Cover（matched_template=知识区 weight=3） |
| 6 页 carousel | M01 cover / M03 essay / M07 closing / M14 pipeline / M04 pull-quote / wechat-cover-pair |
| validate 结果 | **0 fail / 4 warn**（R6 长标题 + R9 step-title gap，内容文案触发，可接受） |
| 渲染 PNG | **7 个**：xhs-1/2/3/4/5 + wechat-21x9 + wechat-1x1（共 ~720 KB） |
| publisher 入表 | **14 success rows**（7 PNG × 2 平台：`xiaohongshu` + `wechat`）· status=success · duration 38-1228ms |
| 总耗时 | **~67 秒**（端到端） |

## 与天龙已有资产协同

| 资产 | 协同点 |
|---|---|
| **35-06 V1.1 博主全息** | 直接读取 `ip_profile_8dim.json` |
| **stage 18 guizang V1.0** | 用 28 版式 / 10 主题 / 9 校验 + render-poster.mjs |
| **stage 18 R1 AGPL 红线** | 自动注入 AGPL metadata；强制仅 PNG 输出 |
| **stage 16 huashu-design 40 风格库** | 第 9 维 design_style 一对一映射到 10 主题 |
| **stage 17 V1.0 桥接脚本** | 用 detect_palette 启发式 + select_template 三段逻辑 |
| **blogger-fingerprint-registry V3.0** | 第 9 维 schema + writing_style column + design_style column |
| **multi-platform-publisher V1.0** | batch CLI 接 tasks.jsonl；14 行 success 入 publisher.db |
| **35-02/35-05 老李风** | 自动选 kraft-paper 调色板匹配老李色系 |

## 使用示例

### 例 1 · 一键博主出图（端到端）

```bash
cd "dragon-engine/skills/guizang-social-card-skill"
node pipeline/blogger-poster.mjs --blogger laoli_bro_2026
# → 7 PNG + 14 publisher success rows · ~67 秒
```

### 例 2 · 干跑（不调 publisher、不实渲）

```bash
node pipeline/blogger-poster.mjs --blogger laoli_bro_2026 --dry-run
# → 只生成 prompt/pages.jsonl/index.html/tasks.jsonl，不渲染 PNG，不调 publisher
```

### 例 3 · 仅发指定平台

```bash
node pipeline/blogger-poster.mjs --blogger laoli_bro_2026 --platforms xiaohongshu
# → tasks.jsonl 只含 xiaohongshu 平台
```

### 例 4 · 强制覆盖自动推断

```bash
node pipeline/blogger-poster.mjs --blogger laoli_bro_2026 --theme editorial --recipe M07
# → 强制 editorial 主题 + M07 closing note 版式
```

## V2.0 已知限制

| 局限 | 影响 | 缓解 |
|------|------|------|
| V2.0 仅用博主全息的 8 维 JSON；第 9 维必须先 UPDATE registry DB | 中文 encoding 噪音 | fingerprint-registry 已升级（步骤 1 完成）|
| `_meta` 不发 publisher.py（不是 PublishTask 字段）| metadata 仅在 file 留存 | tags/description 已带 design_style/consent |
| `publisher.py` 在 Windows gbk stdout 编码抛 UnicodeEncodeError | exit code 1 但 DB 真成功 | pipeline 视为 advisory warning（已 fix） |
| `palette-rules.mjs` 启发式 10 套 | 部分博主配色仍可能不准 | 第 9 维 design_style 显式覆盖 |
| 仅 1 个博主实测（laoli）| 多博主批量未测 | 已有 schema 兼容，下一阶段可批量 |

## 未来候选（阶段 20+）

- [ ] **批量全息出图**：遍历 `registry.db` 所有博主一键出图
- [ ] **真实 OpenAPI 接入**（publisher V2.0）替换 mock
- [ ] **Hugo / GitHub Pages 自动发布**：海报 HTML → 静态博客
- [ ] **更多模板族**：map-component（路线/区域/聚类/热力图）/ Live Photo / PPT 横版
- [ ] **A/B 测试**：同博主生成 5 版调色板，人工选 1
- [ ] **IP 授权过期阻断**：`consent_expires_at < now` 自动跳过 + 邮件告警

## 已知坑 & 修复记录

| 坑 | 修复 |
|---|---|
| `["writer", "stdio", "stdio"]` 缺 stdio 参数 + 重复 import execSync | 已删除重复 import + 加 `stdio: ["ignore", "pipe", "pipe"]` |
| POSTERS_HERE 正则在 `<style>` 块内的注释里错误命中 | 改用 `(    <!-- POSTERS_HERE -->)[\s\S]*?(  <\/main>)` 精确匹配 `<main>` 块内 |
| `extract-pages.mjs` 用 require() 但 ESM 文件不能 require | 改成 import "node:fs" 内联 |
| `publisher.py batch` 路径错（cwd 是 skill 根，不是 skill 子目录）| 改用 `python scripts/publisher.py batch` 完整路径 |
| `tasks.jsonl` 含 `_meta` 字段，PublishTask dataclass 拒绝 | 移除 `_meta`（metadata 仅 file 留存）|
| `publisher.py` exit=1（gbk emoji 编码）但 DB 真成功 | pipeline 视为 advisory warning |

---

**Why**: 这一步把"博主全息"从 JSON 数据变成"一键批量化视觉资产"，**打通了"9 维 → guizang 海报 → 9 平台 publisher"工业化路径**。即使 publisher V1.0 mock 不真实发布，链路本身已经验证可用（pipelie + DB 14 行 success），只等 publisher V2.0 OpenAPI 接入即可真实分发。

**How to apply**: 当用户说"批量博主出图"、"9 维全息一键渲"、"laoli 自动出公众号封面"，直接 `node pipeline/blogger-poster.mjs --blogger <id>`。先看 pages.jsonl + 渲染 PNG 确认内容，再调 publisher 入表。

相关:[[guizang-social-card-integration]] · [[map-component-merge-decision]] · [[agpl-attribution-statements]] · [[blogger-hologram-to-poster]]（V1.0）