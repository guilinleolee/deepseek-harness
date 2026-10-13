# DRAGON_SYNC_PLAN.md · 天龙引擎 → DSH 同步计划

> **生成日期**: 2026-08-27
> **天龙版本**: V2.5 (26 + 26.1 阶段)
> **DSH 版本**: 当前 main
> **目标**: 把天龙引擎 1157 资产同步进 DSH 的 `dragon-assets/`（顶层数据目录，非 Cordis 包）

---

## 0. 同步体量（Phase 0 实测）

| 维度 | 数字 |
|------|------|
| 总资产（顶层目录） | 213 skills / 325 agents / 160 commands / 70+ hooks / 49 scripts / 65 memory / 16 plugins / 3 ip-profiles |
| 总文件数（含嵌套）| **22,006** |
| 总大小 | **346 MB** |
| 同步后 jsonl 索引行数 | 784 + 187 + 90 + 156 + 7 = **1,224** 行（与天龙 INDEX_MASTER.json counts 对齐）|

---

## 1. 目标目录布局

```
D:\deepseek-harness\
├── dragon-assets/                          ← 新建顶层数据目录（非 Cordis 包）
│   ├── README.md                            ← 龙资产入口说明
│   ├── LICENSE-ATTRIBUTION.md               ← 三档 License 致谢模板（MIT/AGPL/Apache）
│   ├── .gitignore                           ← 排除 GBK 误码 / scratch / graph.json
│   │
│   ├── skills/        ← 天龙 skills/    （843 一级目录 · 20,626 文件 → 排除后 20,904 含子）
│   ├── agents/        ← 天龙 agents/    （182 .md + 3 子目录）
│   ├── commands/      ← 天龙 commands/  （139 .md + 12 .sh = 172 文件）
│   ├── runtime/       ← 天龙 hooks/ + scripts/ + plugins/
│   │   ├── hooks/        （121 文件）
│   │   ├── scripts/      （63 文件）
│   │   └── plugins/      （289 文件 · 不含子仓 node_modules）
│   ├── memory/        ← 天龙 memory/    （129 .md · 含 critical/ obsidian-mirror/ 子目录）
│   ├── ip-profiles/   ← 天龙 ip-profiles/（35 文件 · IP 授权）
│   ├── index/         ← 天龙 index/    （5 jsonl + INDEX_MASTER.json + INDEX_README.md）
│   ├── docs/          ← 天龙 docs/     （9 文件）
│   ├── prompts/       ← 天龙 prompts/  （7 文件）
│   ├── tests/         ← 天龙 tests/    （25 文件 · 适配为 DSH vitest）
│   ├── market/        ← 天龙 market/   （15 文件 · 市场复盘产物）
│   ├── output/        ← 天龙 output/   （6 文件 · 历史产物归档）
│   └── top-level/     ← 天龙 顶层 md   （6 文件：BIBLE/CLAUDE/MEMORY/MAINTENANCE/REFERENCE_INDEX/STATUS）
│
├── packages/                                ← 现有 DSH 仓不动
│   ├── skill-index/      ← 新建（Phase 2A）
│   ├── agent-roster/     ← 新建（Phase 2B）
│   ├── license-policy/   ← 新建（Phase 2C）
│   └── dragon-bridge/    ← 新建（Phase 3A · 必须 `@deepseek-ai/dsh-experimental-*` 前缀）
```

---

## 2. 排除清单

| 排除项 | 原因 | 大小 |
|--------|------|------|
| `.git/` | VCS 内部 | - |
| `.cache/` `.pytest_cache/` `.streamlit/` `.vscode/` `.claude/` | 天龙开发副产物 | < 5 MB |
| **`node_modules/`** （嵌套在 `tasks/stage-*-scratch/*/node_modules`）| 临时 scratch 子仓依赖 | ~50 MB+ |
| **`graphify-out/`** | 知识图谱巨型产物（含 `graph.json` 49MB） | ~55 MB |
| **`third-party/`** | 上游克隆，含 node_modules | ~30 MB+ |
| **`tasks/`** | scratch 临时工作区 | - |

---

## 3. CJK 文件名处理

天龙 commands/ 有 13 个含中文文件名（`00调研师.md` / `01架构师.md` 等核心九部）。处理策略：

- **保留原文件名**（UTF-8，PowerShell/Node 22 都正常处理）
- **同步后** 在 `dragon-assets/commands/.cjk-rename-manifest.md` 记录每个 CJK 文件的 ASCII 别名（`00调研师.md` → `00-investigator.md`）方便检索
- 不主动改名（避免破坏天龙主仓引用一致性）

---

## 4. License 红线（来自 `packages/experimental/AGENTS.md` + DSH 主仓治理）

**虽然 `dragon-assets/` 不是 Cordis 包**（不会触发 `@deepseek-ai/dsh-experimental-*` 命名约束），但仍要遵守 DSH 主仓 License 治理：

| License | 同步策略 | 标记 |
|---------|---------|------|
| **MIT ✅** | 全部同步 | 无限制 |
| **Apache-2.0 ✅** | 全部同步 | dragon-assets/LICENSE-ATTRIBUTION.md 加 NOTICE 模板 |
| **BSD-3-Clause ✅** | 全部同步 | 同上 |
| **AGPL-3.0 ⚠️** | 全部同步但加 `LICENSE-WARNING-AGPL.md` 红头文件 | 禁止 SaaS 化、禁止修改后闭源 |
| **NOASSERTION ❌** | 跳过（天龙里几乎没有） | 记录跳过原因 |

---

## 5. 同步阶段执行顺序

| Phase | 内容 | 命令 | 预计耗时 |
|-------|------|------|---------|
| **Phase 0** | 资产盘点 + 风险扫描 | （已完） | - |
| **Phase 1A** | skills/ → dragon-assets/skills/ | `robocopy` 排除 node_modules | 10-15 min |
| **Phase 1B** | agents/ → dragon-assets/agents/ | `robocopy` | < 1 min |
| **Phase 1C** | commands/ → dragon-assets/commands/ | `robocopy` | < 1 min |
| **Phase 1D** | hooks/ + scripts/ + plugins/ → dragon-assets/runtime/ | `robocopy` ×3 | < 2 min |
| **Phase 1E** | memory/ + 顶层 md + index/ → dragon-assets/{memory,top-level,index}/ | `robocopy` ×3 | < 2 min |
| **Phase 1F** | 补充目录：docs/ prompts/ tests/ market/ output/ ip-profiles/ | `robocopy` ×6 | < 2 min |
| **Phase 1G** | 创建 dragon-assets/{README.md, .gitignore, LICENSE-ATTRIBUTION.md} | `write` | < 5 min |
| **Phase 2A-C** | 新建 packages/skill-index, agent-roster, license-policy | Cordis 包规范 | 2-3 天 |
| **Phase 3A** | 新建 packages/dragon-bridge/ | Cordis 包规范 | 1 天 |
| **Phase 3B** | `pnpm typecheck + test + lint + hygiene` | 必跑 | 5-10 min |
| **Phase 3C** | 写 `DRAGON_INTEGRATION.md` | `write` | < 30 min |

---

## 6. 验证清单（Phase 1 完）

- [ ] `dragon-assets/` 文件数 = **20,000+**（±与 Phase 0 计数一致）
- [ ] `dragon-assets/` 总大小 ≤ **400 MB**
- [ ] 5 个 jsonl 行数 = 天龙 INDEX_MASTER.json counts 一致
- [ ] 顶层 md 6 个全到位（BIBLE/CLAUDE/MEMORY/MAINTENANCE/REFERENCE_INDEX/STATUS）
- [ ] 不含 `node_modules/` `graph.json` `graphify-out/` `tasks/` `third-party/`
- [ ] `.gitignore` 正确（关键二进制大文件不跟踪）
- [ ] `LICENSE-ATTRIBUTION.md` 三档致谢模板就位

---

## 7. 不做清单（避免范围蔓延）

- ❌ 不重写天龙 skill 为 Cordis plugin（5-10x 工作量）
- ❌ 不把天龙 `docs/workflow/` 等迁移到 DSH `docs/`
- ❌ 不动天龙主仓任何文件
- ❌ 不创建 git commit（让你审过再说）
- ❌ 不跑 DSH 全套质量门（只在 Phase 3B 跑一次）
- ❌ 不引入天龙 `index/` 之外的二进制（图片/PDF 仅同步 metadata）
