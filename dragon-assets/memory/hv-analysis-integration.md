---
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---
# hv-analysis V1.0 完整集成 · 详细记忆（hv-analysis-integration.md）

> **状态**：天龙引擎 10 阶段流水线 · **阶段 10**（2026-06-29 完成）
> **MEMORY.md 指针**：1 行 + 本文件
> **本文件目的**：抽离 MEMORY.md 详细记忆，让 MEMORY.md 压回 ≤200 行

---

## 触发源

[KKKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills) 同源（**9.9k ⭐**）— 阶段 6/8/9 之后，hv-analysis 作为同源姊妹 skill 接续。hv-analysis 是「横纵分析法深度研究 + 万字 PDF 报告」引擎，是 **35-07 横纵研究师新岗位** 的核心。

---

## 阶段 1：V0.0 基础（已存在）

| 文件 | 状态 | 内容 |
|------|------|------|
| `skills/hv-analysis/SKILL.md` V0.0 | ✅ 已存在（350 行）| 6 步工作流 + Python 封装 + 简单 PDF |
| `scripts/hv_research.py` V0.0 | ✅ 已存在（160 行）| `HVResearch class + argparse CLI` |

**V0.0 已具备**：6 步工作流（search/diachronic/synchronic/lateral/cross/pdf）；Python 封装 + CLI；4 岗位升级表（01/10-02/62-02/07）；禁词清单；与天龙协同。

**V0.0 关键缺失**（升级动机）：
1. 无 YAML frontmatter / 无 version 字段
2. **6 步 ≠ khazix 源版 5 步**（V0.0 多了 lateral 步骤，是凑步骤）
3. **缺方法论溯源**（索绪尔 / 社会科学 / 商学院 / 波特 4 大思想）
4. **缺并行子Agent 搜索策略**（khazix 源版核心）
5. **缺 arXiv 必查规则**（学术类研究对象）
6. **缺 4 类研究对象适配**（产品/公司/概念/人物 各自侧重点）
7. **缺竞品场景 A/B/C 判断**（不同场景对比方式不同）
8. **缺横纵交汇 5 核心问题 + 3 剧本**（khazix 源版核心）
9. **缺 14 项质检**（V0.0 完全无质检）
10. **缺 14 条 DON'T 护栏**（V0.0 只有禁词清单）
11. **缺 md_to_pdf.py 独立脚本**（V0.0 是 generate_pdf 内嵌方法）
12. **缺 hv_check.py 一键质检**（V0.0 无退出码契约）
13. **缺 35-07 横纵研究师新岗位**（V0.0 4 岗位已过时）
14. **缺 3 个新 reference**（method-trace/research-types/writing-style）
15. V 升级表写的老版本（V8.89/V8.69/V9.1/V9.07）已被超越

---

## 阶段 2：V1.0 升级（已完成）

### 2.1 SKILL.md V1.0 重写（~500 行）

**保留**：V0.0 全部工程骨架（6 步 → 5 步、Python 封装、CLI、禁词）

**新增 6 个方法论模块**（来自 khazix 源版 hv-analysis.md）：
1. **YAML frontmatter**（name / version: V1.0.0 / base_version: V0.0 / source khazix 9.9k ⭐ / triggers 11 类 / depends 2 / downstream 5 岗位）
2. **5 步工作流**（去掉 V0.0 的 lateral，与 khazix 源版对齐）
3. **方法论溯源**（索绪尔 + 社会科学 + 商学院 + 波特 4 大思想）
4. **并行子Agent 搜索策略**（3 个 Agent + arXiv 必查）
5. **4 类研究对象适配**（产品/公司/概念/人物 各自侧重点）
6. **14 项质检 + 14 条 DON'T 护栏**

**V 升级表现役版本**（V0.0 写的全部已超越）：
| 岗位 | V0.0 写的老版本 | V1.0 升级到现役 | 关键能力 |
|------|---------|---------|---------|
| 01 调研师 | V8.89 | **V9.0** | AI热点实时监控+每日快报（visual-code-tracer 集成）|
| 10-02 AI 研究员 | V8.69 | **V9.0** | 横纵双轨研究 + 5 步方法论 + 14 质检 + PDF 排版 |
| 62-02 行业研究员 | V9.1 | **V11.0** | TradingAgents 升级 + 横纵研究法 |
| 07 记录师 | V9.07 | **V12.1** | html-slides V2 集成 + 横纵 PDF 归档 |
| **35-07 横纵研究师** ⭐NEW | - | **V1.0** | 万字深度研究 + PDF 报告（hv-analysis 直管）|

### 2.2 references/ 目录（新建 3 个文件）

- **`references/method-trace.md`**（~180 行）— 4 大思想溯源 + 双轴原理 + 适用边界
- **`references/research-types.md`**（~200 行）— 4 类研究对象完整适配 + 混合类型处理
- **`references/writing-style.md`**（~220 行）— 6 借鉴 + 4 不借鉴 + 14 质检详解 + 失败症状

### 2.3 脚本 V1.1 升级（+3 脚本总计）

| 脚本 | V0.0 函数 | V1.1 新增函数/升级 |
|------|----------|------------------|
| `hv_research.py` | `HVResearch class + 6 步` | **5 步对齐** + 4 类研究对象 + 竞品场景 A/B/C + 5 核心问题 + 3 剧本 + CLI `--type`/`--scenario` |
| `md_to_pdf.py` ⭐NEW V1.0 | - | 完整 WeasyPrint 排版（A4/封面/配色/字体/页眉页脚/孤行寡行）|
| `hv_check.py` ⭐NEW V1.0 | - | 14 项质检（10 必检 + 4 推荐）+ 退出码契约 0/1/2/3 |

**V0.0 → V1.1 兼容性**：100% 向后兼容（V0.0 类名/方法名全保留，新增 `--type`/`--scenario` 参数有默认值）。

**新增 CLI 参数**：
- `hv_research.py` — `--type {product,company,concept,person}` / `--scenario {A,B,C}` / `--title` / `--author`
- `md_to_pdf.py` — `--title` / `--author` / `--css` / `--no-html`
- `hv_check.py` — `--json` / `--required-only`

### 2.4 35-07 横纵研究师新岗位 ⭐NEW V1.0

- `agents/35-07-hv-researcher-v10.md` ⭐NEW — 横纵研究师 V1.0（由 hv-analysis V1.0 直管）
- 5 步工作流 + 4 类研究对象 + 14 质检 + 14 DON'T + WeasyPrint PDF 排版
- 与 01/32-01/62-02/07/aihot V1.0 协同（接收输入 + 输出归档）

---

## 累计验证

| 验证项 | 命令 | 期望退出码 | 实际 |
|-------|------|----------|------|
| V0.0 兼容（HVResearch 类）| `python hv_research.py --help` | 0 | ✅ |
| V1.0 5 步（去掉 lateral）| 查看 step2_diachronic/step3_synchronic | N/A | ✅ |
| V1.0 4 类研究对象 | `--type product/company/concept/person` | 0 | ✅ |
| V1.0 竞品场景 A/B/C | `--scenario A/B/C` | 0 | ✅ |
| V1.0 5 核心问题 | step4_cross_convergence 模板 | N/A | ✅ |
| V1.0 3 剧本 | step4_cross_convergence 模板 | N/A | ✅ |
| md_to_pdf.py 单测 | `python md_to_pdf.py test.md test.pdf` | 0 | ✅ |
| hv_check.py 14 质检 | `python hv_check.py test.md` | 0/1/2/3 | ✅ |
| hv_check.py JSON | `python hv_check.py test.md --json` | 0/1/2/3 | ✅ |
| hv_check.py required-only | `python hv_check.py test.md --required-only` | 0/1/2 | ✅ |
| MEMORY.md 合规 | `neat_check.py --target=user` | 0 | ✅ |
| 35-07 岗位 V1.0 创建 | `agents/35-07-hv-researcher-v10.md` | 存在 | ✅ |
| 4 类研究对象 CLI | `--type concept "RAG" --scenario C` | 0 | ✅ |

**总计：13/13 PASS**

---

## 核心数字

- **3 个 Python 脚本**（V1.1 hv_research + V1.0 md_to_pdf + V1.0 hv_check）
- **5 步工作流**（与 khazix 源版对齐）
- **4 类研究对象**（产品/公司/概念/人物）
- **3 个竞品场景**（A 无竞品 / B 1-2 个 / C 3+ 个）
- **5 核心问题 + 3 剧本**（横纵交汇）
- **14 项质检**（10 必检 + 4 推荐）
- **14 条 DON'T 护栏**（含禁词 + 流程护栏）
- **3 个新 reference**（method-trace / research-types / writing-style）
- **1 个新岗位 35-07**（横纵研究师 V1.0）
- **退出码契约 0/1/2/3**（PASS/FAIL/WARN/ERROR）

---

## 战略价值

### 1. 双轴分析法（方法论母集对齐 khazix）

V0.0 是 6 步（凑步骤）→ V1.0 是 5 步（与 khazix 源版对齐）。**核心不变**：纵向追时间深度，横向追同期广度，交汇出判断。**侧重点灵活**：4 类研究对象各自适配。

### 2. 万字 PDF 报告（从模板到工业级）

V0.0 是简陋 HTML 生成 → V1.0 是 WeasyPrint 专业级排版：
- A4 页面 + 25mm/20mm 边距
- 4 色标题配色（H1 深蓝 / H2 绿 / H3 浅蓝 / H4 紫）
- 字体 fallback 链（自动处理中英混排）
- 孤行寡行控制 + 表格斑马纹 + 引用块 + 页眉页脚

### 3. 35-07 横纵研究师新岗位（天龙研究中枢）

**填补天龙研究能力空白**：
- 01 调研师 V9.0 — AI 热点监控
- 10-02 AI 研究员 V9.0 — 学术研究流程
- 62-02 行业研究员 V11.0 — 行业动态
- 07 记录师 V12.1 — 记录归档
- **35-07 横纵研究师 V1.0** ⭐NEW — **深度研究**（系统化方法论 + PDF 排版）

### 4. 14 项质检 + 14 条 DON'T 护栏（工业化安全）

V0.0 是无质检 → V1.0 是 14 项必检 + 推荐 + 退出码契约：
- 10 必检项必须全过才能交付
- 4 推荐项可触发 WARN
- hv_check.py 可进 CI gate

### 5. 跨平台兼容

- 纯 Python 3 + weasyprint + markdown
- CLI + 库两种使用方式
- 100% V0.0 向后兼容

---

## 关键文件路径

| 资产 | 路径 | 状态 |
|------|------|------|
| SKILL.md V1.0 | `C:\Users\li\.claude\projects\dragon-engine\skills\hv-analysis\SKILL.md` | 重写 |
| method-trace.md | `C:\Users\li\.claude\projects\dragon-engine\skills\hv-analysis\references\method-trace.md` | 新建 |
| research-types.md | `C:\Users\li\.claude\projects\dragon-engine\skills\hv-analysis\references\research-types.md` | 新建 |
| writing-style.md | `C:\Users\li\.claude\projects\dragon-engine\skills\hv-analysis\references\writing-style.md` | 新建 |
| hv_research.py V1.1 | `C:\Users\li\.claude\projects\dragon-engine\skills\hv-analysis\scripts\hv_research.py` | 升级 |
| md_to_pdf.py V1.0 | `C:\Users\li\.claude\projects\dragon-engine\skills\hv-analysis\scripts\md_to_pdf.py` | 新建 |
| hv_check.py V1.0 | `C:\Users\li\.claude\projects\dragon-engine\skills\hv-analysis\scripts\hv_check.py` | 新建 |
| 35-07 横纵研究师 V1.0 | `C:\Users\li\.claude\projects\dragon-engine\agents\35-07-hv-researcher-v10.md` | 新建 |
| 用户级 MEMORY.md | `C:\Users\li\.claude\projects\c--Users-li--claude\memory\MEMORY.md` | 联动更新（加阶段 10 行）|
| hv-analysis-integration.md | `C:\Users\li\.claude\projects\c--Users-li--claude\memory\hv-analysis-integration.md` | 新建（本文）|

---

## 关键参考（不重复）

| 资产 | 链接 |
|------|------|
| 上游阶段 9 aihot | `aihot-integration.md` |
| 上游阶段 8 neat-freak | `neat-freak-integration.md` |
| 上游阶段 6 khazix | `khazix-integration.md` |
| 上游阶段 5 book-distiller | `book-distiller-v908-12.md` |
| 上游阶段 4 github-to-skills | `github-to-skills-v11.md` |
| 上游阶段 3 VoxCPM2 | `voxcpm-integration.md` |
| 上游阶段 2 gpt-image-2 | `gpt-image-2-integration.md` |
| 下游（暂无）| - |

---

## 未来候选（已留指针，未实施）

| 优先级 | 资产 | 预期收益 |
|--------|------|---------|
| ⚪ 低 | 35-02 V13.3 / 35-05 V10.3 | 老李风作为内容素材源 + aihot 协同（V13.3/V10.3 留指针）|
| ⚪ 低 | 28-01 V10.4 | neat-freak 协同点：老李风生成内容自动存进 MEMORY 主题文件 |
| ⚪ 低 | khazix-skills 下一源版（content_methodology / storage-analyzer / style_examples）| 持续集成 |

---

## 后续阶段协同

- **stage 14 baoyu-skills 全集 21/21**（2026-07-17）→ [baoyu-skills-integration.md](baoyu-skills-integration.md)

## 版本信息

- **V0.0**：基础 6 步 + 简单 Python 封装
- **V1.0**（2026-06-29）：5 步对齐 khazix + YAML + 14 质检 + 14 DON'T + 35-07 新岗位 + md_to_pdf + hv_check
- **累计验证**：13/13 PASS
- **MEMORY.md 行数**：治理前置（用户级 ~200 行 ✅）
- **战略价值**：双轴分析法 / 万字 PDF 报告 / 35-07 新岗位 / 14 质检 / 跨平台兼容
