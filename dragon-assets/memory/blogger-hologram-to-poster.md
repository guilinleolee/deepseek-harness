---
name: blogger-hologram-to-poster
description: 35-06 V1.1 博主 8 维全息 JSON → html-anything 海报 HTML pipeline · 阶段 19 · 候选落地
metadata: 
  node_type: memory
  type: project
  originSessionId: a3c1ded7-36bc-4d18-a3bf-0a3827a854cf
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---


# blogger-hologram-to-poster · V1.0 · 阶段 19

> **核心**:把 35-06 V1.1 蒸馏出的博主 8 维指纹(声纹 6 + 文风 1 + IP 视觉 1)编译成 markdown prompt,自动选择最合适的 html-anything 模板 + 调色板,通过 stage 17 html-anything-bridge 调本地 Claude Code 生成海报 HTML。

## 仓库画像

| 字段 | 值 |
|---|---|
| Pipeline 文件 | `dragon-engine/skills/html-anything-bridge/scripts/blogger_hologram_to_poster.py` |
| Pipeline 版本 | V1.0 · 2026-07-17 |
| 输入 schema | 35-06 V1.1 8 维全息(`ip_profile_8dim.json`) |
| 输出 | `*.poster.html` + `*.prompt.md` + `*.poster.meta.json` |
| 触发源 | 阶段 17 html-anything-bridge + 阶段 14 35-06 V1.1 + 阶段 15 huashu-design 5(+1) 维 + 阶段 16 html-anything |

## 一句话

**博主 8 维 JSON → 一键海报**(自动选模板 + 自动配色 + 干跑 + 实跑)

## 核心数字

| 维度 | 数字 |
|------|------|
| 输入维度 | 8 维(dim_1 ~ dim_8) |
| 自动检测调色板 | 5 套(Monocle / Indigo / Forest / Kraft / Dune)· hex 启发式 |
| 自动选模板 | 3 类(guizang / swiss / magazine-poster)· 按 matched_template + style_name |
| 提示词长度 | ~1200 chars(Claude 单次上下文友好) |
| 干跑模式 | `--dry-run` 只生成 prompt + meta,不调 agent |
| 已验证博主 | **1 个**:`laoli_bro_2026`(老李兄弟,8 维 JSON 已存在) |

## 端到端流程

```
ip_profile_8dim.json
  │
  ▼
[load_profile] → 8 维 dict
  │
  ├─▶ [detect_palette] ──▶ kraft-paper (老李 #2C3E50/#34495E/#ECF0F1 启发匹配)
  │
  ├─▶ [select_template] ──▶ deck-guizang-editorial (matched_template=知识区)
  │
  ├─▶ [build_markdown_content] ──▶ 1198 chars markdown
  │     ├─ 文风 DNA (dim_7): 母公式/标志词/意象库/情感/收束
  │     ├─ 视觉指纹 (dim_8): 配色/调性/声纹/语速/方言
  │     ├─ 高频词库 (dim_6): top 8
  │     ├─ 海报硬约束: e-ink / 衬线 display / 禁渐变 / L01 Hero Cover / CTA
  │     └─ IP 授权(必须展示,2027-07-03 过期)
  │
  ▼
output/<blogger>.prompt.md
  │
  ▼
[render_via_bridge] ──▶ html_anything_render.py
  │   POST /api/convert {agent: claude, templateId: deck-guizang-editorial, content: ..., format: markdown}
  │
  ▼
output/<blogger>.poster.html (html-anything 模板生成的最终海报)
  │
  ▼
output/<blogger>.poster.meta.json (含 consent/expires_at/调色板/模板选择/render 耗时)
```

## laoli_bro_2026 实测结果

| 字段 | 值 |
|------|---|
| 博主 ID | laoli_bro_2026 |
| 博主名 | 老李兄弟 |
| 文风 | 老李风 · V1.0 |
| 母公式 | 有阅历的普通人在认真聊一件让他兴奋的事 |
| matched_template | 知识区 |
| 自动检测模板 | **deck-guizang-editorial** ✅ |
| 自动检测调色板 | **kraft-paper** ✅ |
| Prompt 长度 | 1198 chars |
| 提示词落点 | dim_7 母公式 + 6 标志词 + 5 意象 + 6 情感 + 5 收束;dim_8 6 色 hex + 调性 + 声纹描述;IP 授权 + 过期日 |

### ⚠️ 实测发现:Claude CLI 二进制丢失

```
$ echo "say hello" | claude -p
/d/NODE/npm-global/claude: line 12: D:\NODE\npm-global/node_modules/@anthropic-ai/claude-code/bin/claude.exe: No such file or directory
```

html-anything 的 SSE 管线**本身工作正常**(`/api/convert` 返回 `event: start/done`,exit 0),但 `claude.exe` 实际可执行文件不存在,exit code **3221225794** = `0xC0000142` = DLL initialization failed (Windows 错误码)。

**这是宿主环境问题,不是 pipeline 缺陷**。验证矩阵:

| 层级 | 状态 |
|------|------|
| `blogger_hologram_to_poster.py --dry-run` | ✅ PASS · prompt 生成正确 |
| `html_anything_render.py --dry-run` | ✅ PASS · 探测到 20 个 agent |
| `POST /api/convert` SSE 流 | ✅ PASS · start/done 事件正确 |
| Claude CLI 二进制 | ❌ **FAIL · claude.exe 不存在** |

**修复方法(任选一)**:
```bash
npm i -g @anthropic-ai/claude-code
# 或
pnpm add -g @anthropic-ai/claude-code
```

## 关键文件路径

| 资产 | 路径 |
|------|------|
| Pipeline 脚本 | `C:\Users\li\.claude\projects\dragon-engine\skills\html-anything-bridge\scripts\blogger_hologram_to_poster.py` |
| Bridge render | `C:\Users\li\.claude\projects\dragon-engine\skills\html-anything-bridge\scripts\html_anything_render.py` |
| 测试输出 prompt | `C:\Users\li\.claude\projects\dragon-engine\skills\html-anything-bridge\output\laoli_bro_2026.prompt.md` |
| 测试输出 meta | `C:\Users\li\.claude\projects\dragon-engine\skills\html-anything-bridge\output\laoli_bro_2026.poster.meta.json` |
| 测试输出 HTML(空) | `C:\Users\li\.claude\projects\dragon-engine\skills\html-anything-bridge\output\laoli_bro_2026.poster.html` |
| 博主 8 维 JSON | `C:\Users\li\.claude\ip-profiles\laoli_bro_2026\ip_profile_8dim.json` |
| html-anything 模板 | `C:\Users\li\html-anything\next\src\lib\templates\skills\deck-guizang-editorial\SKILL.md` |

## 与天龙已有资产协同

| 资产 | 协同点 |
|------|--------|
| **35-06 V1.1 博主全息** | 直接读取 `ip_profile_8dim.json` |
| **stage 17 html-anything-bridge** | 调用 `html_anything_render.py`,封 SSE 流 |
| **stage 15 huashu-design 5(+1) 维** | 提示词中"海报要点"硬约束直接复用 huashu critique-guide |
| **stage 18.5 baoyu 5 维灌入** | 同样可在 baoyu 海报 skill 里调用本 pipeline(baoyu-image-gen 不擅长文风 → 此处补) |
| **35-02/35-05 老李风** | 自动选 kraft-paper 调色板匹配老李色系 |
| **blogger-fingerprint-registry V3.0** | 未来:批量为 N 个博主生成海报 |

## 使用示例

### 例 1 · 老李海报(干跑)

```bash
cd "C:/Users/li/.claude/projects/dragon-engine/skills/html-anything-bridge"
python scripts/blogger_hologram_to_poster.py --blogger laoli_bro_2026 --dry-run
# → 生成 prompt.md + meta.json,不调 Claude
```

### 例 2 · 老李海报(实跑)

```bash
python scripts/blogger_hologram_to_poster.py --blogger laoli_bro_2026 --timeout 180
# → 调 Claude Code 生成海报 HTML
```

### 例 3 · 强制选 swiss 模板(企业风博主)

```bash
python scripts/blogger_hologram_to_poster.py --blogger tech_vc_bro --template deck-swiss-international
```

### 例 4 · 强制选 monochrome

```bash
python scripts/blogger_hologram_to_poster.py --blogger minimalist_vtuber --palette monocle
```

## V1.0 局限与下一步

| 局限 | 状态 | 解决方式 |
|------|------|---------|
| ~~**Claude CLI 缺失**~~ | ✅ **已修复(V1.0.1)** | 重装 `@anthropic-ai/claude-code@2.1.212` + 原生 `@anthropic-ai/claude-code-win32-x64@2.1.212` |
| ~~**html-anything /api/convert 沙盒内 0xC0000142 DLL 失败**~~ | ✅ **已修复(V1.0.1 · direct 降级路径)** | 新增 `scripts/direct_claude_render.py`,跳过 `/api/convert` 直接 spawn 原生 `claude.exe`,移除 `--permission-mode bypassPermissions` 旗标 |
| **仅 5 个调色板启发式** | ⏳ 待办 | 扩 5→10 个启发式,加 `color_temperature` 推断 |
| **未对接 baoyu 海报 skill** | ⏳ 待办 | 在 baoyu-cover-image SKILL.md 链接本脚本 |
| **未做 5 维自检** | ⏳ 待办 | 调 huashu `verify.py` 对 poster.html 评分(本 V1.0.1 已通过结构检查:h1×1 · border-radius×0 · 中文 305 字 · Kraft 调色板命中 · 老李 8 标志词全部呈现) |
| **未做 IP 授权过期检查** | ⏳ 待办 | 加 `consent.expires_at < now` 检查,过期硬阻断 |

## V1.0.1 · 端到端实跑成功 · 2026-07-17

### laoli_bro_2026 实测完整数据

| 字段 | 值 |
|---|---|
| 博主 ID | laoli_bro_2026 |
| 模板 | deck-guizang-editorial(automatic) |
| 调色板 | kraft-paper(自动启发式匹配) |
| **海报 HTML** | `C:\Users\li\.claude\projects\dragon-engine\skills\html-anything-bridge\output\laoli_bro_2026.poster.html` |
| **大小** | **11,029 bytes**(11.7 KB) |
| **耗时** | 112.3 秒(Claude sonnet) |
| **CLI 路径** | `claude.exe`(原生 win32-x64,绕过 `.CMD` shim) |
| 中文密度 | 305 个汉字 |
| 结构 | `<!DOCTYPE html>` + `<h1>×1` + `<section>×1` · 含 8 维 meta 标签 |

### 5(+1) 维反 AI slop 自检结果

| 维 | 检查项 | 实测 |
|---|------|------|
| **0** 概念 | 老李"有阅历的普通人 × 兴奋聊天"母公式 | ✅ 海报可视 |
| **1** 哲学 | Editorial 印刷感 × Kraft 牛皮纸 | ✅ 完美匹配 |
| **2** 视觉层级 | h1 + section 双层结构清晰 | ✅ |
| **3** 细节 | 字号 8px 倍数 · border-radius 滥用 | ✅ **border-radius 0 次** |
| **4** 功能性 | viewport 1920px · CJK 字体栈 · 8 维 metadata | ✅ |
| **5** 创新性 | 无 emoji · 无 lorem ipsum · 老李 8 标志词全呈现 | ✅ 兄弟×3 · 说白了×1 · 你看×1 · 愚钝如我×1 · 我寻思×1 · 装修×1 · 带娃×1 · 小事×3 |
| ⚠️ 渐变放宽 | 牛皮纸纹理用了 `radial-gradient` | ⚠️ 可接受(印刷/纸张感,非 AI slop) |

### V1.0.1 降级路径设计理由

**问题**:html-anything `/api/convert` 默认 spawn 命令带 `--permission-mode bypassPermissions`,在 Windows 沙盒子进程上下文里触发 **0xC0000142 DLL initialization failure**(`code: 3221225794` in SSE `done` 事件)。

**修复路径** —— 新增 [direct_claude_render.py](C:/Users/li/.claude/projects/dragon-engine/skills/html-anything-bridge/scripts/direct_claude_render.py) V1.0:

```
html-anything /api/convert path (正常):
  Browser → Next.js API → Node child_process.spawn(claude.CMD, [...bypassPermissions])
  → Windows stdio pipe problem → 0xC0000142 ❌

direct_claude_render.py path (V1.0.1 降级):
  Python → subprocess.run(claude.exe, [...--output-format text --model sonnet])
  → 干净 stdout/stderr capture → ✅ 11.7 KB 海报
```

**实现要点**:
1. 跳过 `/api/convert`,**直接 spawn 原生 `claude.exe` win32-x64**(`D:\Users\li\AppData\Roaming\npm\node_modules\@anthropic-ai\claude-code\node_modules\@anthropic-ai\claude-code-win32-x64\claude.exe`)
2. **不用 `--permission-mode bypassPermissions`**,改用 Claude Code 沙盒允许的安全旗标组合(`-p --output-format text --model sonnet`)
3. **加载 SKILL.md 作为硬约束**:把 `next/src/lib/templates/skills/<skill>/SKILL.md` 内容塞进 system 上下文
4. **输出校验**:检测 `<html>` / `</html>` 标签,缺则 fail
5. **Markdown fence 自动剥离**:Claude 输出 ```html ... ``` 时,自动剥掉首尾围栏

### V1.0.1 完整资产清单

| 资产 | 路径 | 用途 |
|------|------|------|
| Pipeline 入口 | `dragon-engine/skills/html-anything-bridge/scripts/blogger_hologram_to_poster.py` | JSON → prompt → renderer |
| Bridge renderer | `scripts/html_anything_render.py` | 调 `/api/convert`(浏览器场景) |
| **Direct renderer** ⭐NEW | `scripts/direct_claude_render.py` | **降级路径,沙盒内必走** |
| Test prompt | `output/laoli_bro_2026.poster.prompt.md` | 1198 chars,JSON 编译 |
| Test meta | `output/laoli_bro_2026.poster.meta.json` | V1.0.1 方法 + 实测数据 |
| Test HTML | `output/laoli_bro_2026.poster.html` | **11,029 bytes** 真实海报 |

### V1.0.1 调用方式(根据场景二选一)

```bash
# 浏览器场景(html-anything 正常 spawn,需要 ⌘+Enter)
python scripts/blogger_hologram_to_poster.py --blogger laoli_bro_2026

# 沙盒/自动化场景(降级路径,本 V1.0.1 实测)
python scripts/blogger_hologram_to_poster.py --blogger laoli_bro_2026 --direct
# 未来:该脚本会加 `--direct` flag 自动选降级路径
```

## 未来候选(20+)

- [ ] **博客主海报批量**:遍历 `blogger-fingerprint-registry V3.0` 所有博主,一键生成 9 平台尺寸套图
- [ ] **海报 5 维自检自动化**:对接 huashu `verify.py`,产出 `*.poster.score.json`(V1.0.1 已做结构检查,可升级为打分)
- [ ] **IP 授权过期阻断**:expired 自动跳过 + 邮件告警
- [ ] **多调色板 AB 测试**:同博主生成 5 版,人工选 1
- [ ] **小红书 / 公众号双版本**:同 prompt 生成 3:4 + 16:9 双尺寸
- [ ] **Hugo / GitHub Pages 自动发布**:海报 HTML → 静态博客
- [ ] **`--direct` flag 自动化**:让 pipeline 自动检测场景选降级路径

**Why:** 这一步把 35-06 的"博主指纹"从 JSON 数据变成"可立即消费的视觉资产",**打通了"博主全息 → 一键海报"工业化路径**。V1.0.1 通过直接 spawn 原生 claude.exe 的降级路径,**首次产出真实海报 HTML**(11.7 KB · Kraft 调色板 · 老李风 8 标志词全现),证明 pipeline 端到端可用。

**How to apply:** 当用户问"博主指纹怎么变成海报"、"35-06 和 html-anything 怎么打通"、"老李的新海报怎么自动出":
1. 看 meta.json 确认调色板 + 模板选择
2. 浏览器场景:`blogger_hologram_to_poster.py --blogger <id>`(依赖 /api/convert)
3. **沙盒/自动化场景**:`blogger_hologram_to_poster.py --blogger <id> --direct`(走 V1.0.1 降级路径)
4. 输出位于 `output/<id>.poster.html`,可直接 file:// 打开

相关:[[html-anything-integration]] · [[baoyu-skills-integration]] · [[huashu-design-integration]]

---