---
name: darwin-skill-integration
description: alchaincyf/darwin-skill (5.3k⭐ MIT) 天龙集成主题文件 · 阶段 35 · skill 自动进化器 · 10/10 PASS
metadata:
  type: integration
  originSessionId: stage-35-nuwa-darwin-cangjie
  modified: 2026-08-04T11:29:10.544Z
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---


# darwin-skill × 天龙引擎 · 阶段 35-C 集成主题文件

> **上游**：[alchaincyf/darwin-skill](https://github.com/alchaincyf/darwin-skill) · 5,321 ⭐ / 568 forks
> **License**：MIT ✅（上游未署名 ©）
> **集成阶段**：天龙 35 · 周 1-B
> **累计 PASS**：10/10（test_darwin_installation.py）
> **镜像路径**：`dragon-engine/skills/darwin-skill/`
> **作者**：alchaincyf（同 nuwa 作者）
> **论文基础**：SkillLens (arXiv 2605.23899) + SkillOpt (arXiv 2605.23904)

---

## 1. 实跑元数据

| 维度 | 值 |
|---|---|
| GitHub URL | https://github.com/alchaincyf/darwin-skill |
| Stars / Forks | 5,321 / 568 |
| License SPDX | MIT |
| 上游 LICENSE size | 1,076 B |
| 最近 push | 2026-06-10 (V2.1) |
| 主语言 | HTML / Node.js |
| darwin 版本 | V2.1 (keep/revert 棘轮 paired 比较) |
| 镜像文件数 | 43（含 assets + references + scripts + templates + test-prompts.json + 5 README + AGENT/HANDOFF/PRODUCT + l3-specs）|

---

## 2. 镜像拓扑

```
dragon-engine/skills/darwin-skill/
├── LICENSE                                              ← 上游 verbatim
├── SKILL.md                                             ← 加天龙 frontmatter
├── README.md / README_EN.md                             ← 上游 verbatim
├── AGENT.md / HANDOFF.md / PRODUCT.md                   ← 天龙扩展
├── assets/  (23 文件 · chart-loop/phases/ratchet · banner · aso-hero)  ← 上游 verbatim
├── references/  (runtime-neutrality.md · skilllens-evidence.md)  ← 上游 verbatim
├── scripts/  (screenshot.mjs)                           ← 上游 verbatim
├── templates/  (result-card.html · -dark · -white · .png)  ← 上游 verbatim
├── test-prompts.json                                    ← 上游 verbatim（darwin 自身测试样本）
├── showcase.html                                        ← 上游 verbatim
├── l3-specs/                                            ← MIT 子包装（天龙本地增强）
│   ├── README.md
│   └── darwin-neat-freak-bridge.md  ← Phase 0.5 neat-freak V1.1 红线 gate
├── scripts/darwin_check.py                              ← 天龙 check 脚本
├── tests/test_darwin_installation.py                    ← 10 项 pytest PASS
└── .gitignore                                           ← 天龙扩展
```

---

## 3. 能力矩阵（9 维 rubric · skill 进化器）

### 3.1 结构维度（59 分）— 静态分析

| # | 维度 | 权重 | 评分标准 |
|---|------|------|---------|
| 1 | Frontmatter 质量 | 7 | name / description / 触发词 / ≤1024 字符 |
| 2 | 工作流清晰度 | 12 | 步骤明确 / 有输入输出 |
| 3 | 失败模式编码 | 12 | **必须显式**「X 失败 → Y」分支 |
| 4 | 检查点设计 | 6 | 🔴/STOP/CHECKPOINT 显性标记 |
| 5 | 可执行具体性 | 18 | 禁软化措辞（建议/可以考虑）|
| 6 | 资源整合度 | 4 | references/scripts/assets 引用正确 |

### 3.2 效果维度（35 分）— 实测

| # | 维度 | 权重 | 评分标准 |
|---|------|------|---------|
| 7 | 整体架构 | 12 | 冗余/AI 腔扣分 |
| 8 | 实测表现 | 23 | 跑 2-3 个测试 prompt 对比 baseline |

### 3.3 Meta-skill 维度（6 分）— 反例与黑名单

| # | 维度 | 权重 | 评分标准 |
|---|------|------|---------|
| 9 | 反例与黑名单 | 6 | 「不要做什么」反例清单 |

### 3.4 v2.1 关键改进

- **keep/revert 棘轮**：从「绝对分数 delta」改为「**paired 同-judge 比较 + 奇数 N 多数决**」—— 消除 ±8 judge 噪音
- **绝对分数降级为 triage-only** —— 仅用于「哪支最弱、先改谁」，不进 keep/revert 决策

### 3.5 天龙 4 条额外红线（l3-specs/darwin-neat-freak-bridge.md）

| # | 红线 | 权重 |
|---|------|------|
| 10 | MIT 致谢段完整（5 模板 × 2 skill）| +3 |
| 11 | AGPL 红线规避（不传模板到 H5）| +3 |
| 12 | Apache NOTICE 完整（5 段）| +3 |
| 13 | neat-freak V1.1 gate 通过 | +3 |

---

## 4. 实施边界（MIT 红线 · 必须遵守）

| 维度 | 约束 |
|---|---|
| LICENSE 完整性 | 不可删上游 "MIT License" |
| 致谢强度 | 5 平台模板（小红书 / 公众号 / H5 / 视频号 / 微博）+ 8 致谢段 |
| 不得抹去上游作者 | 不能把 9 维 rubric 说成"博主原创评分法" |
| 可子包装 | MIT 允许 — `l3-specs/` 可写本地增强 |
| 可修改源码 | MIT 允许 — 派生自由 |
| 商业 / SaaS | MIT 允许 — 无传染 |
| **Phase 0.5 红线 gate** | darwin 优化前必跑 `neat_check.py --target <skill>` |

---

## 5. 与天龙既有 26 阶段的协同矩阵

| 维度 | 协同对象 | 协议 |
|---|---|---|
| **红线护栏** | neat-freak V1.1 | Phase 0.5 gate |
| **cangjie 衔接** | cangjie-skill (AGPL) | test-prompts.json → darwin Phase 1 |
| **nuwa 衔接** | nuwa-skill (MIT) | 同上 schema 7 字段 |
| **book-distiller 协同** | book-distiller V9.12 | DIGEST 质量门神 |
| **skill-updater 报告** | skill-updater V1.1.3 | 已知天龙集成版自动走 AUTO_HINTS |

---

## 6. 累计 PASS 增量（阶段 35-C 锁定）

| 测试项 | 状态 |
|---|---|
| T1 LICENSE verbatim | ✅ PASS |
| T2 SKILL.md frontmatter | ✅ PASS |
| T3 天龙扩展三件套 | ✅ PASS |
| T4 upstream scripts | ✅ PASS |
| T5 upstream references | ✅ PASS |
| T6 upstream templates | ✅ PASS |
| T7 l3-specs + neat-freak bridge | ✅ PASS |
| T8 darwin_check.py exit 0 | ✅ PASS |
| T9 test-prompts.json 格式 | ✅ PASS |
| T10 mit-attribution section | ✅ PASS |
| **累计** | **10/10 PASS** ✅ |

总累计 = 773（35-A 之后）+ 10 = **783 PASS**（天龙 35-C 锁定）

---

## 7. Phase 0.5 neat-freak 联动协议

```python
# darwin Phase 0.5 红线 gate
import subprocess
import sys

def neat_freak_gate(skill_slug: str) -> int:
    cmd = [sys.executable, "~/.claude/skills/neat-freak/scripts/neat_check.py",
           "--target", skill_slug]
    result = subprocess.run(cmd, capture_output=True, encoding="utf-8")
    return result.returncode

# darwin Phase 1 入口
gate_exit = neat_freak_gate("a-stock-data-bridge")
if gate_exit != 0:
    print(f"FAIL: neat-freak gate exit={gate_exit}")
    sys.exit(gate_exit)
print("OK: neat-freak gate 通过")
```

详见 [`l3-specs/darwin-neat-freak-bridge.md`](../dragon-engine/skills/darwin-skill/l3-specs/darwin-neat-freak-bridge.md)

---

## 8. 风险与未决项

| 风险 | 缓解 |
|---|---|
| judge 子 agent 不可用 | 降级到 dry_run |
| dry_run > 30% | 警告（dim8 实测失效）|
| paired delta 全为负 | 自动 break + 回滚 |
| Apache/AGPL/MIT 红线误触 | Phase 0.5 neat-freak gate |
| editor 后 SKILL.md 长度爆炸 | neat-freak size check |

---

## 9. 来源链接

- 上游仓库：https://github.com/alchaincyf/darwin-skill
- 上游 LICENSE：https://github.com/alchaincyf/darwin-skill/blob/master/LICENSE
- 上游 SKILL.md：https://github.com/alchaincyf/darwin-skill/blob/master/SKILL.md
- 论文 SkillLens：arXiv 2605.23899
- 论文 SkillOpt：arXiv 2605.23904
- 本地镜像：`dragon-engine/skills/darwin-skill/`
- 主题文件：`memory/darwin-skill-integration.md`（本文件）
- 致谢模板：`memory/mit-attribution-statements.md §十二`
- neat-freak 联动：`dragon-engine/skills/darwin-skill/l3-specs/darwin-neat-freak-bridge.md`

---

## 10. 实施计划（天龙阶段 35-C · 已完成）

| 任务 | 状态 |
|---|---|
| mkdir + tarball 镜像 | ✅ 2026-08-04 |
| SKILL.md frontmatter | ✅ |
| AGENT.md / HANDOFF.md / PRODUCT.md | ✅ |
| l3-specs/darwin-neat-freak-bridge.md | ✅ |
| scripts/darwin_check.py | ✅ |
| tests/test_darwin_installation.py (10/10) | ✅ |
| memory/darwin-skill-integration.md（本文件）| ✅ 2026-08-04 |
| mit-attribution §十二 | ✅ 2026-08-04 |

---

## 11. 协同矩阵

| darwin 调用 | 触发 |
|---|---|
| `neat-freak V1.1` | Phase 0.5 红线 gate |
| `cangjie-skill test-prompts.json` | 蒸馏产物直接消费 |
| `nuwa-skill test-prompts.json` | 蒸馏产物直接消费 |
| `book-distiller V9.12` | DIGEST 质量评估 |

| 天龙其他 skill 调用 darwin | 触发 |
|---|---|
| 主仓 38 skills | 「优化 XX skill」/「XX skill 怎么样」|
| `~/.claude/skills/*` | 用户级 skill 优化 |
| `dragon-engine/skills/<new-skill>` | 新 skill 上线前优化 |