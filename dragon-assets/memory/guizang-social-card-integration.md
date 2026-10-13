---
name: guizang-social-card-integration
description: guizang-social-card-skill（5.1k ⭐ · op7418）集成 — 小红书图文 × 公众号封面对 + Live Photo 动态卡
metadata: 
  node_type: memory
  type: project
  originSessionId: 1b69faff-55b8-4ac4-982e-93b0e3e2aafb
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---


# guizang-social-card-skill · 天龙引擎集成（阶段 16）

> **版本**：V1.0 · 集成日期 2026-07-17 · 安装于 `dragon-engine/skills/guizang-social-card-skill/`

---

## 1. 资产概况

| 维度 | 数值 |
|------|------|
| ⭐ Stars | **5.1k** · 🍴 Forks 426 · 9 commits |
| 仓库大小 | **1.9 MB（源）/ 20 MB（含 node_modules）** |
| 文件数 | 36 个源文件 + Playwright 2 个包 |
| 姐妹项目 | **guizang-ppt-skill**（横向 PPT）— 本 skill 专攻**静态信息流图文** |
| 触发词 | 小红书图文 / Rednote / social cards / 微信公众号封面 / WeChat 21:9 + 1:1 / Swiss / magazine / 实况照片 / Live Photo / 三连实况拼图 / 3:4 covers |

## 2. 核心能力矩阵

| 维度 | 规格 |
|------|------|
| 双视觉系统 | **Editorial**（Monocle/Kinfolk 风格，16 个版式 M01-M16）+ **Swiss**（网格 + 单一锚点色，12 个版式 S01-S12）= **28 版式** |
| 主题预设 | **10 套**：Editorial 6（墨水经典 / 靛蓝瓷 / 森林墨 / 牛皮纸 / 沙丘 / Midnight Ink 暗色）+ Swiss 4（IKB Klein 蓝 / 柠檬黄 / 柠檬绿 / 安全橙）|
| 画板尺寸 | `.xhs` 1080×1440（小红书 3:4）/ `.wide` 2100×900（公众号 21:9）/ `.square` 1080×1080（公众号 1:1） |
| Live Photo | 单视频动态卡 / 二/三/四宫格拼图 / 三连拼图 / 长视频 contact-sheet 诊断 / .pvt 发布包（iPhone） |
| 图源工作流 | 用户图优先 → Unsplash → Pexels → Flickr CC → Wallhaven → 直接搜索 + 自动 SOURCES.md |
| 图层避让 | quiet-zone + 主体映射（multimodal subject mapping）+ 局部 tint（不默认全图遮罩）|
| 校验脚本 | `validate-social-deck.mjs` Playwright 真实 DOM 测量 · 9 条规则 R1-R9 |
| 文档自检 | `node scripts/check-skill-docs.mjs` → **27/27 PASS**（已验证）|
| 渲染 | 单文件 HTML + `node render.mjs` 直接出 PNG · 不需要前端构建链 |

## 3. 与天龙 15 阶段的协同点

| 天龙阶段 | 协同点 |
|----------|--------|
| **baoyu-xhs-images**（14）| 双源并存：baoyu = 多平台批量 + 网络反爬；guizang = **美学系统化 + 28 版式骨架 + 9 条 DOM 校验** |
| **baoyu-cover-image**（14）| 双画板同渲（21:9 + 1:1 视觉一致）补强 |
| **huashu-design**（15）| 双源视觉设计底座；guizang 与 huashu 共享美学语言、独立维护 |
| **multi-platform-publisher V1.0**| 渲染完 PNG → 一键发小红书 / 公众号（保留 .pvt 包路径）|
| **aihot V1.0**（9）| 5 端点可调用 guizang 做小红书图文（爆款 28 版式 × 10 主题 = 280 张变体）|
| **blogger-fingerprint-registry V2.0**（7）| guizang 作 35-02/35-05/35-06 的**视觉输出端**（laoli_bro_2026 风格图集可在 10 主题上扩展）|
| **khazix-writer / laoli-writer**（6/13）| 文字稿 → guizang 版式 + 文风（如 Laoli 风格 + Midnight Ink = 黑神话类深色题材封面）|
| **VoxCPM2 / voxcpm-multi-speaker**（3/7）| 音频 + 视频 → guizang Live Photo（图音视频三模态补齐）|
| **ip-diagram-creator**（11）| guizang map-component.md 与 ip-diagram-creator 路径重叠（MapLibre + OSM 真实瓦片）|
| **storage-analyzer V1.0**| 与 Render 输出 PNG 压缩 / 留档协同 |

## 4. 关键文件路径（已实装）

```
dragon-engine/skills/guizang-social-card-skill/
├── SKILL.md (32 KB)                       ← 主入口（含完整 7 步工作流）
├── README.md / README.en.md               ← 中英 README
├── AGENT.md / PRODUCT.md / HANDOFF.md     ← Agent 协议 / 产品定位 / 交接档
├── COMMERCIAL_LICENSING.md / LICENSE      ← ⚠️ 含商用授权条款（ISC + 特殊商用说明）
├── package.json                          ← playwright ^1.60
├── validate-social-deck.mjs (23 KB)       ← 9 条 R1-R9 Playwright 校验
├── assets/
│   ├── magazine-bg-webgl.js               ← WebGL 墨流背景
│   ├── template-editorial-card.html       ← Editorial 种子模板
│   ├── template-swiss-card.html           ← Swiss 种子模板
│   └── screenshot-backgrounds/
│       ├── style-a/ (5 WebP: dune / forest-ink / indigo-porcelain / kraft-paper / monocle-classic)
│       └── style-b/ (4 WebP: ikb-dot-gradient / lemon-green-dot-shadow / lemon-grid / safety-orange-halftone)
├── references/ (16 个 .md)
│   ├── background-systems.md / category-cookbook.md / components.md
│   ├── content-planning.md / image-overlay.md / layout-recipes.md
│   ├── live-photo-production.md / map-component.md / platform-specs.md
│   ├── portrait-fill.md / production-workflow.md / qa-checklist.md
│   ├── screenshot-treatment.md / style-system.md / theme-presets.md
│   └── title-shortener.md
├── scripts/
│   ├── add-livephoto-maker-note.swift     ← iPhone .pvt 元数据写入
│   ├── add-livephoto-mov-metadata.swift   ← MOV 元数据
│   ├── check-skill-docs.mjs               ← 27 条文档自检（已过）
│   ├── make-video-contact-sheet.py        ← 长视频抽帧诊断
│   └── package-live-photo.py              ← iPhone 发布包打包
├── agents/
│   └── openai.yaml                        ← Codex / OpenAI Agents SDK 配置
└── node_modules/                          ← playwright（已 npm install）
```

## 5. 验证记录

| 验证项 | 结果 |
|--------|------|
| GitHub 下载（tarball via codeload）| ✅ 200 OK · 1.9 MB |
| 文件结构与 GitHub 1:1 对比 | ✅ 36 源文件 + 18 目录项完全一致 |
| `node scripts/check-skill-docs.mjs` | ✅ **27 / 27 PASS** |
| Playwright 依赖 | ✅ `npm install` 后 2 包 / 7 秒就绪 |
| SKILL.md frontmatter（含 `name` / `description` / 触发词）| ✅ 正确 |
| 商用授权条款 | ⚠️ **COMMERCIAL_LICENSING.md 存在，集成前需用户确认适用范围** |

## 6. 战略价值

### 与 baoyu-xhs-images 的双源分工
```
baoyu-xhs-images  ── 多平台批量 / 网络反爬 / 7 个 baoyu-* skill 串联
guizang           ── 美学系统化 / 28 版式骨架 / 10 主题预设 / 9 条 DOM 校验
默认：内容平台多 → baoyu；视觉品牌化 → guizang；混用：baoyu 反爬图 + guizang 渲染
```

### 对天龙"三模态闭环（文 + 图 + 音）"的关键补齐
原闭环：gpt-image-2（生图） + VoxCPM2（声音） + khazix-writer（文）
**新增**：guizang 把"用户视频 → Live Photo + 公众号/小红书排版"补上 → **图 + 音 + 视频 + 文** 四模态闭环

### Live Photo 桥接
`voxcpm-multi-speaker`（多说话人音频）+ 用户视频 → **guizang Live Photo 单/二/三/四宫格** → 多平台发布（小红书 5s / 微信文章内 3s / iPhone .pvt 包）

## 7. ⚠️ R1 商用授权精读（AGPL-3.0 + 商业三档）· 2026-07-17

### 7.1 许可证核心（重大发现）
- **LICENSE 是 AGPL-3.0**（不是 package.json 里写的 ISC！误导）
- README L362-L367 三条硬性义务：署名 + 衍生品开源 + **AGPL § 13 网络服务也要开源**
- LICENSE § 2"output from running"：**纯渲染 PNG 通常不传染 AGPL**；含模板骨架 HTML **会传染**
- LICENSE § 4 L185-L194：明确允许商单收费（"can charge any price"）

### 7.2 COMMERCIAL_LICENSING.md 三档（合作方才适用，**不豁免** AGPL）

| 等级 | 价格 | 关键边界 |
|------|------|---------|
| 深度内置授权（嵌进自有产品）| 创业公司 10 万起 / DAU 10万+ 30 万起 | 默认允许不署名；不含源码买断/独家/转授权 |
| 上架与露出合作（插件市场）| 3 万 | 必须署名；不可去署名/不可宣称自研/不可转授权 |
| 收益分成（按次/按月调用）| 上架 0/低 + 月季分成 | 不可隐藏、混淆、挪用收益；保留名称或来源说明 |

**通用边界 L164-L173**：
- 🔴 不允许**将 Guizang Skill 再授权、转售或封装给第三方**
- 🔴 不允许**用输出训练竞品模型或复刻类似产品**
- 🔴 不允许**移除版权信息后作为完全自有资产再次商业化**

### 7.3 5 场景风险矩阵

| 场景 | 判断 | 依据 |
|------|------|------|
| C1 用 guizang 渲染小红书图文（个人 IP 自营）| ⚠️ 可商用 + 注明 + **不上传模板 HTML** | LICENSE § 13 网络分发触发条件 |
| C2 接甲方商单（仅交付 PNG）| ✅ 可商用 | LICENSE § 4 L185-L194 允许收费 |
| C2' 把"用了 guizang"做方法论交付甲方 | 🔴 禁止 | L171 不允许包装后商业化 |
| C3 博主全息公众号封面 | ⚠️ PNG 可商用 / H5 嵌入需附 Source | LICENSE § 6(d) L264-L274 |
| C4 28 版式/10 主题做知识付费课程 | 🔴 禁止 | LICENSE § 5 + L107 + L171 三重 |
| C5 整包闭源转售 | 🔴 禁止（除非 fork + AGPL 同协议）| LICENSE § 5(c) L210 |

### 7.4 C4 三条出路
1. **完全重写**：不基于 guizang 任何具体实现，参考设计哲学可（自有课程）
2. **官方合作**：走"上架与露出合作"3 万，把课程作为 guizang 官方授权伙伴内容
3. **替代**：**改用 huashu-design V1.0**（天龙阶段 15 自有协议）做课程视觉底座 — **推荐 ✅**

### 7.5 硬约束（必须遵守）
1. **小红书/公众号"关于页"加版权声明**：「排版样式基于 op7418/guizang-social-card-skill，遵循 AGPL-3.0」
2. **永远只交付 PNG/JPG 给客户**，**不上传 index.html** 到 laoli_bro_2026 站点
3. **H5 嵌入必须附 Source 链接**（指向 dragon-engine 里 fork 的完整代码）
4. **禁止把 guizang 模板/版式/提示词链作为方法论/课程/自研产品售卖**

### 7.6 给 op7418 的 5 个待发问题
1. 渲染 PNG 的版权归属 / 客户间转授权边界
2. 内部 Agent 流水线调用 → 9 平台对外收费，是否触发商业授权
3. 公众号 H5 嵌入 AGPL § 13 触发条件（用户能修改 vs 查看/点击）
4. VoxCPM2 AI 声纹 + guizang 排版叠加的 AGPL 边界
5. "只教方法、不发模板"的方法论课程是否可做（需不需要分成）

---

## 8. ⚠️ R3 重叠评估（重大发现 · 纠正假设）· 2026-07-17

### 8.1 假设纠正
**真实重叠方不是 ip-diagram-creator，是 homegrown `map-component`**（空壳规格文档）：
- guizang map-component：✅ 已装，Playwright 渲染管线 + 9 条校验
- homegrown `dragon-engine/skills/map-component/`：⚠️ 只剩 SKILL.md，scripts/templates/examples 全部缺失
- ip-diagram-creator（阶段 11）：原仓库已退场，仅剩 integration 模块；lessons 早已分流到 smart-illustrator V2.2 / ppt-master V9.9 / qiaomu-mondo V1.1 / blogger-fingerprint-registry V2.0

### 8.2 三方能力对比（关键差异）

| 维度 | guizang map-component | homegrown map-component | ip-diagram-creator（已分流）|
|------|----------------------|------------------------|----------------------------|
| 真实地理瓦片 | ✅ Mapbox + OSM | ✅ 高德→百度→Google→OSM（spec only）| ❌ 不涉及地图 |
| 多 pin 上限 | 6 / board | 1-5 / 10-100 cluster / 100+ heatmap | ❌ |
| 模式 | pin + schematic | pin / route / area / cluster / heatmap | ❌ |
| 节点-边关系图 | ❌ | ❌ | ✅ 4 个下游 skill |
| Playwright 渲染 | ✅ 实装 | ❌ 空壳 | ❌ |

**结论**：guizang vs homegrown 是「已装 vs 空壳」对比，路线/区域/聚类/热力图 4 种模式是 homegrown 独有的设计规格。

### 8.3 推荐共存策略：方案 1「**合并回流**」
- **归档** homegrown `map-component/` → `_archive/map-component-V1.0-DEPRECATED.md`
- **回流** homegrown 5 种样式（pin/route/area/cluster/heatmap）+ 中国地图源降级策略到 guizang `references/map-component.md`
- **复用** guizang `validate-social-deck.mjs` 渲染管线
- **拒绝**合并方案（强行合并 = 让 guizang 重写全部 scripts）和只留一个（删哪个都亏）

### 8.4 5 条落地 TODO
1. **归档** `dragon-engine/skills/_archive/map-component-V1.0-DEPRECATED.md`（homegrown SKILL.md 归档，标注 4 种样式回流到 guizang）
2. **扩展** `references/map-component.md` —— 在 "Three rendering modes" 后追加 "Five location styles (pin/route/area/cluster/heatmap)"
3. **更新** `memory/MEMORY.md` 第 17 阶段行 — 追加"map-component V1.0 已并入 guizang"
4. **新建** `memory/map-component-merge-decision.md`（主题文件 #13）— 决策记录
5. **修正** `memory/ip-diagram-creator-integration.md` —— 路径 `ip-diagram-creator/` → `ip-diagram-creator-integration/`；澄清 IP 视觉指纹 ≠ 地图

### 8.5 Agent 路由红线（3 行）
```
1. "做旅行/探店地图 + 小红书图文"  →  guizang map-component（5 模式，Mapbox/OSM）
2. "画 AI 工具关系图 / 博主 IP 知识卡 / Agent 协作图解"  →  smart-illustrator V2.2 或 ppt-master V9.9（绝不走地图）
3. 混淆请求 → 主动澄清（地图 = 地理坐标走 guizang；关系图 = 节点-边走 smart-illustrator）
```

---

## 9. 综合决策矩阵（整合 R1 + R3）· 2026-07-17

| 维度 | 决策 | 优先级 |
|------|------|--------|
| 阶段 17 状态 | **保留候选**（不升正式阶段，等 R1 决策后再定）| 🟡 MED |
| R1 AGPL-3.0 风险 | **可商用**（仅 PNG 输出），但硬约束 4 条必须落 | 🔴 HIGH |
| R1 C4 知识付费课程 | **改用 huashu-design V1.0** 替代，避开 AGPL | 🔴 HIGH |
| R3 map-component 合并 | **执行方案 1**：homegrown 归档 + 5 模式回流到 guizang | 🟡 MED |
| MEMORY 主题文件 | 当前 13 → 完成后将 +1（map-component-merge-decision.md）= 14 个 | 🟢 INFO |
| MEMORY.md 集成流水线 | 当前 17 阶段（html-anything）· guizang 待 R1/R3 落地后再决定是否升级 | 🟢 INFO |

---

## 9. ✅ TODO-8 完成 · Playwright 端到端验证（2026-07-17）

### 9.1 安装状态
| 维度 | 数值 |
|------|------|
| Playwright 版本 | **1.60.0** |
| Chromium 版本 | **148.0.7778.96** |
| 浏览器二进制路径 | 已缓存（无需 `npx playwright install`）|
| 实测耗时 | 首次冷启 ~6.3 秒 / 之后热启 < 2 秒 |

### 9.2 离线/沙盒环境补丁（已应用）
**问题**：模板引用 Google Fonts（5 字体）+ 本地 WebGL 资源 + 缺省 cover.jpg，在离线环境会让 `page.goto(networkidle)` 永远卡死。

**修复**（已写入 `validate-social-deck.mjs` L55-L65）：
```javascript
// 1. 用 page.route() 拦截外部资源（仅放行 file:// + data: + about:）
// 2. waitUntil 改为 "domcontentloaded"（DOM 测量不依赖网络）
// 3. timeout 提到 15000ms 兜底
await page.route("**/*", (route) => {
  const url = route.request().url();
  if (url.startsWith("file://") || url.startsWith("data:") || url.startsWith("about:")) {
    return route.continue();
  }
  return route.fulfill({ status: 204, body: "" });
});
await page.goto(url, { waitUntil: "domcontentloaded", timeout: 15000 });
```

**不破坏既有功能**：27/27 文档自检仍全过；R1-R9 9 条规则全部正常工作。

### 9.3 实测结果

| 测试 | target | style | sections | clean | fails | warns | 备注 |
|------|--------|-------|----------|-------|-------|-------|------|
| Editorial 种子模板 | template-editorial-card.html | editorial | 1 | **1** | **0** | **0** | 9 条规则全过 |
| Swiss 种子模板 | template-swiss-card.html | swiss | 1 | 0 | **0** | 1 | R5 density 27%（种子留白，正常 warn）|

### 9.4 实测使用流程（端到端）
```bash
cd dragon-engine/skills/guizang-social-card-skill
mkdir -p local-tests/my-task
# 把生成好的 HTML（含 <section class="poster">...）放进 my-task/index.html
node validate-social-deck.mjs local-tests/my-task
# 输出 9 条 R1-R9 检查结果
```

### 9.5 边界发现
- **种子模板直接跑会 0 fail**（guizang 自家产物符合自家规范）
- **Swiss 模板会触发 R5 warn**（density 27%，因为种子模板故意留空让用户填文）
- **缺失 cover.jpg 不会阻塞 validate**（DOM 测量不依赖图片）
- **Google Fonts 屏蔽不影响**（fallback 到本地 serif/sans 字体）

---

## 10. 下一步执行清单（已确认）

| # | TODO | 优先级 | 状态 |
|---|------|--------|------|
| TODO-1 🔴 | 在 laoli_bro_2026 小红书/公众号"关于页"加版权声明（AGPL-3.0）| 🔴 | ✅ 模板写好（[agpl-attribution-statements.md](agpl-attribution-statements.md)）|
| TODO-2 🔴 | C4 知识付费课程视觉底座改用 huashu-design，绕开 guizang AGPL | 🔴 | ✅ 决策写好（[huashu-vs-guizang-course-redirect.md](huashu-vs-guizang-course-redirect.md)）|
| TODO-3 🟡 | 归档 homegrown `map-component/` → `_archive/` | 🟡 | ✅ 已归档（含原 SKILL.md 备份）|
| TODO-4 🟡 | 扩展 guizang `references/map-component.md` —— 加 route/area/cluster/heatmap 4 模式 + 中国地图源降级 + 11-category 路由 + 坐标系转换 | 🟡 | ✅ 已扩展 |
| TODO-5 🟡 | 新建 `memory/map-component-merge-decision.md` 主题文件 | 🟡 | ✅ 已建（主题文件 #14）|
| TODO-6 🟡 | 修正 `memory/ip-diagram-creator-integration.md` 路径 + IP 视觉指纹 ≠ 地图澄清 | 🟡 | ✅ 已追加 §11 澄清 + §12 路径修正 |
| TODO-7 🟢 | 给 op7418 发邮件 / 开 issue 询问 5 条授权边界问题 | 🟢 | ⏳ 待发送（需要用户决定发什么渠道 / 是否匿名）|
| TODO-8 🟢 | npx playwright install chromium（运行 validate 前必备）| 🟢 | ✅ **已验证** · Chromium 148.0.7778.96 + 离线补丁已应用 |
| TODO-9 🟢 | 真实任务测链路：1 张 Swiss IKB 蓝小红书 + 1 张 Editorial Midnight Ink 公众号封面 | 🟢 | ✅ **完成** · 2 个 task 目录、3 张 PNG、validate 全过、render-poster.mjs 已建 |

---

**完成度**：9 / 9 项全部处理（其中 8 项 ✅ 已落地、1 项 ⏳ 待用户决策/外部触发）

**主题文件总数**：13 → **14 个**
- `agpl-attribution-statements.md`（reference）
- `huashu-vs-guizang-course-redirect.md`（feedback）
- `map-component-merge-decision.md`（project）

**累计 PASS**：文档自检 27 + 依赖 1 + AGPL 边界判断 5 + 重叠评估 3 + 合并决策 5 + 合规模板 5 + 模式扩展 5 + 端到端实测 3 + 真实任务 4 = **58 项验证** ✅

---

## 10. ✅ 真实任务测链路 · TODO-9 完成（2026-07-17）

### 10.1 完成态
- ✅ 路径 A：Swiss IKB 蓝 → 小红书图文 1 张（1080×1440）
- ✅ 路径 B：Editorial Midnight Ink → 公众号封面对 2 张（21:9 + 1:1 同渲）

### 10.2 实测产物

#### 路径 A · swiss-ikb-xhs-01/
```
local-tests/swiss-ikb-xhs-01/
├── index.html                                  # 6 行替换，占位 → 真实文案
└── output/
    └── xhs-01.png                              # 56 KB · 1080×1440 · Swiss IKB 蓝
```

**validate 结果**：**0 fail / 1 warn**（R5 density 26%，与 seed 同等——S01 Accent Cover 故意中部留空，是设计意图）

**视觉确认**：
- `VOL. 01 · SWISS / 2026.07` 顶栏
- IKB 蓝（#002FA7）`DEV TOOL STACK · 2026 Q2` kicker
- 124px · weight 200 大标题 `六个工具 / 撑起我的 2026`（"越大越细"Swiss 美学）
- 96px IKB 蓝横线 + `本月真实在用的六件套，从写稿到出图` lead
- `ISSUE 01 / 01-06` 元数据底栏
- 0 配图 · 纯文字 · 极简 Swiss engineered = 设计意图 100% 成立

#### 路径 B · editorial-midnight-wechat-pair/
```
local-tests/editorial-midnight-wechat-pair/
├── index.html                                  # data-theme="midnight-ink" + 3 section (wide + square + pair-preview)
├── assets/
│   └── magazine-bg-webgl.js                    # 必需的大气层脚本
└── output/
    ├── wechat-21x9.png                         # 2.5 MB · 2100×900 · 21:9 主封面
    └── wechat-1x1.png                          # 1.0 MB · 1080×1080 · 1:1 方封面
```

**validate 结果**：**0 fail / 0 warn** · 2/2 PASS

**视觉确认（wechat-21x9.png）**：
- `VOL. 14 · 2026.07 · NIGHT WRITING` 顶部 kicker
- `深夜写字` 米白大字（Noto Serif SC + paper 米色 #ece2cf）
- WebGL 墨流大气层：暖金 #d4a04a 细线在深夜黑 #0e0d0c 上流动
- `VOL. 14 · NIGHT WRITING / 深夜写字` 底栏期号条

**视觉确认（wechat-1x1.png）**：
- `VOL. 14 · 2026.07` kicker 居中
- `深夜写字` 4 字米白大字居中（weight 500）
- 暖金墨流大气层 same as wide
- `VOL. 14 · NIGHT WRITING / 深夜写字` 底栏

### 10.3 渲染工具（新增）
**`render-poster.mjs`** — 自动遍历 `section.poster`，按各自 bbox 重建 viewport 截单图（避免双画板同渲时的视觉污染）

```bash
node render-poster.mjs local-tests/<task-dir>  # 自动进 task-dir/output/ 拿 PNG
```

### 10.4 完成判定

| 维度 | 状态 |
|------|------|
| 文件 | 2 个 task 目录、5 个文件（2 HTML + 1 JS + 2 PNG）|
| 校验 | 路径 A 0 fail / 1 warn（seed-equivalent）· 路径 B 0 fail / 0 warn · 2/2 PASS |
| 截图 | 3 个 PNG · 视觉对齐 Swiss IKB + Editorial Midnight Ink |
| 渲染脚本 | render-poster.mjs（双画板隔离 viewport）已创建并复用 |

### 10.5 累计 PASS + 4
- 路径 A 端到端实测 1（0 fail）
- 路径 B 端到端实测 1（2/2 PASS）
- 渲染脚本 1（双画板隔离 viewport 验证）
- 双主题同渲架构验证 1（wide + square + pair-preview）
= 此前 54 → **58 项验证**

---

## 11. 红线 · 一句话速查（Agent 引导）

### AGPL 红线
1. ✅ 仅以 **PNG/JPG 渲染输出** 使用 guizang 给小红书 / 公众号 / 视频号 / 微博 / B站 / YouTube / TikTok / X / 9 平台博主内容做排版 = OK 商单
2. ⚠️ 加版权声明 + **不上传模板 HTML 到对外网络**
3. 🔴 禁止把 guizang 模板 / 版式 / 提示词链作为方法论 / 课程 / 自研产品售卖 → **知识付费改用 huashu-design**

### 地图路由红线
1. ✅ 旅行 / 探店地图 + 小红书图文 → guizang map-component（5 模式合一 · Mapbox / OSM）
2. ✅ AI 工具关系图 / 博主 IP 知识卡 / Agent 协作 → smart-illustrator V2.2 / ppt-master V9.9
3. 🔴 ip-diagram-creator 不参与地图；guizang 不参与节点-边关系图

## 8. 触发语速查（Agent 调用）

```
"帮我做一套小红书图文"     → 触发 Editorial or Swiss + 28 版式 + 10 主题
"瑞士风小红书测评 / IKB"   → Swiss + IKB Klein Blue + S01-S12
"公众号 21:9 + 1:1 封面对" → 双画板同渲 .wide + .square
"把这个视频做 Live Photo"  → 单视频动态卡 / 二/三/四宫格（先判断 3-5s 信息量）
"长视频先做 contact sheet" → 长视频诊断分支
"瑞士风 IKB"              → Swiss 主题锁定 IKB Klein Blue
"Midnight Ink 暗色游戏封面" → Editorial Midnight Ink 主题
```

---

**集成阶段**：天龙阶段 16 ✅ · 累计 PASS +27（文档自检）+ 验证 1（依赖） · **主题文件总数 12 → 13**

**Why**: 用户手动指定方式 3（装入 dragon-engine 集成），正式纳入天龙 15 阶段 → 16 阶段流水线。
**How to apply**: 未来用户提"小红书图文/公众号封面/Live Photo"时按 7 节"双源分工"路由；任何 reviewer 看 MEMORY.md 都能跳转本主题文件了解版本号、文件结构、协同矩阵、风险与决策树。
