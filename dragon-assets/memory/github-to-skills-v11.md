---
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---
# github-to-skills V1.1 · 详细记忆（github-to-skills-v11.md）

> **状态**：天龙引擎 6 阶段第 3 阶段（2026-06-23 完成）
> **MEMORY.md 指针**：1 行 + 本文件
> **本文件目的**：抽离 MEMORY.md 详细记忆，让 MEMORY.md 压回 ≤200 行

---

## 触发源

天龙引擎自身的工程化需求：把 GitHub 上的优质仓库（任何有 README + 子目录结构的项目）自动转换为天龙标准的 SKILL.md 资产。

---

## 阶段 1：V1.0 基础能力（已完成）

| 能力 | 说明 |
|------|------|
| **GitHub 仓库解析** | tarball 增量拉取 → 子目录识别 → SKILL.md 候选检测 |
| **自动 SYNC** | 把上游 SKILL.md 同步到 `~/.claude/skills/<repo-name>/SKILL.md` |
| **天龙标准模板注入** | YAML frontmatter + L0/L1/L2 章节结构 |
| **post_distill_vet.py** | 5 类危险模式扫描（dangerous-code / exfiltration / credential-leak / path-traversal / prompt-injection）|

---

## 阶段 2：V1.1 升级（2026-06-23）

### 2.1 vet_whitelist V9.12（误报白名单）

| 维度 | V1.0 | V1.1 |
|------|------|------|
| 危险模式扫描 | 5 类硬拦截 | **5 类 + 3 级豁免** |
| 误报率 | 高（中文/教学反例被误判）| **低**（5 类历史误报自动解决）|
| 豁免机制 | 无 | **Path prefix / Context comment / Negation** 3 级 |

### 2.2 vet_whitelist V9.13（多语言白名单，2026-06-24）

- **5 语言 marker**：JA (9) / KO (9) / FR (9) / DE (9) / ES (9) = **45 multilingual markers**
- 3 级豁免机制不变
- 8/8 测试 PASS：
  1. ✅ JA path prefix + edu prefix (`agents/05-security-reviewer/ja.md`)
  2. ✅ CN context comment (`# 反例:`)
  3. ✅ EN negation (`DO NOT USE`)
  4. ✅ JA file marker (`攻撃例` / `危険` / `禁止`)
  5. ✅ KO file marker + negation (`위험` / `금지` / `사용 금지`)
  6. ✅ FR file marker (`dangereux` / `ne pas utiliser`)
  7. ✅ DE file marker (`gefährlich` / `verboten`)
  8. ✅ negative case（无 marker → 不豁免）

### 2.3 自动解决 5 类历史误报

| 误报源 | 豁免方式 |
|-------|---------|
| 05-security-reviewer | Path prefix `agents/05-` |
| 07-scribe | Path prefix `agents/07-` |
| 13-designer | Path prefix `agents/13-` |
| 47-03-im-operator | Path prefix `agents/47-03-` |
| vet 教学反例 | Context comment `# 反例:` |

---

## 累计验证

- V1.0 post_distill_vet：**5 类危险模式 100% 拦截**
- V9.12 vet_whitelist 集成测试：**7/7 PASS**
- V9.13 多语言白名单：**8/8 PASS**
- **总计：15/15 PASS / 0 FAIL**

---

## 战略价值

### 1. GitHub → 天龙资产转化流水线

- 上游仓库（GitHub）→ 自动 SYNC → 下游资产（`~/.claude/skills/`）
- 卡兹克 / VoxCPM2 / GPT-Image-2 等都是经这条流水线集成的

### 2. 安全护栏工业化

- 5 类危险模式扫描是"硬拦截"层
- 3 级豁免机制是"软豁免"层
- 多语言支持让国际开源项目也能走同一管线

### 3. 误报治理

- 5 类历史误报 + 多语言 marker 让 vet 系统的真实可用性大幅提升
- 从"宁可错杀"到"精准识别"

---

## 关键文件路径

| 路径 | 说明 |
|------|------|
| `C:\Users\li\.claude\skills\github-to-skills\scripts\sync.py` | 仓库解析 + SKILL.md 同步 |
| `C:\Users\li\.claude\skills\github-to-skills\scripts\vet_whitelist.py` | V9.13 / 5 语言 / 3 级豁免 |
| `C:\Users\li\.claude\skills\github-to-skills\tests\test_vet_whitelist.py` | 7+8 测试用例 |

---

## 关键参考（不重复）

| 资产 | 链接 |
|------|------|
| 上游 gpt-image-2 集成 | `gpt-image-2-integration.md` |
| 上游 VoxCPM2 集成 | `voxcpm-integration.md` |
| 上游 khazix 集成 | `khazix-integration.md` |
| 下游（暂无）| - |

---

## 后续阶段协同

- **stage 14 baoyu-skills 全集 21/21**（2026-07-17）→ [baoyu-skills-integration.md](baoyu-skills-integration.md)

## 版本信息

- **整合日期**: 2026-06-23
- **V1.0**: 基础仓库解析 + 5 类危险模式
- **V1.1 V9.12**: vet_whitelist 3 级豁免
- **V1.1 V9.13**: 多语言白名单（5 语言 / 45 markers）
- **累计验证**: 15/15 PASS
- **MEMORY.md 行数**: 治理前置阶段
- **战略价值**: GitHub 转化流水线 / 安全护栏工业化 / 误报治理
