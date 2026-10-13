# PRODUCT.md · darwin-skill × 天龙引擎产品定位

> **与上游 darwin-skill 平级扩展，但**不修改** upstream 任何字节**

---

## 1. 一句话定位

**darwin 是天龙引擎「任意 skill」的进化器**——用 9 维 rubric 评估 → hill climbing 优化 → paired 比较 keep/revert → 自动产出 result-card.html。

---

## 2. 与天龙既有 26 阶段资产的边界

| 维度 | darwin-skill | 既有对照 | 边界 |
|---|---|---|---|
| 作用对象 | 任意 SKILL.md | neat-freak 整仓扫描 | darwin 单 skill 深入 |
| 评估维度 | 9 维 rubric + hill climbing | neat-freak Apache/MIT/AGPL 红线 8 项 | 互补 |
| 决策 | paired 同-judge 比较 | neat-freak 退出码 0/1/2/3 | 互补 |
| 触发 | "优化 skill" "达尔文" "skill 评分" | neat-freak 自动巡检 | 互补 |
| 产出 | result-card.html | conformance 报告 | 互补 |

---

## 3. 关键决策树

```
用户说「优化 XX skill」或「XX skill 怎么样」
    │
    ├─ Phase 0.5: neat_check.py --target XX
    │   └─ exit 0 → 进 Phase 1
    │
    ├─ Phase 1: 9 维 rubric 评估 + 3 judge 子 agent
    │   └─ results.tsv
    │
    ├─ Phase 2: hill climbing（每轮 1 维度编辑）
    │   └─ paired 比较 + 奇数 N 多数决
    │
    ├─ Phase 3: 生成 result-card.html
    │
    └─ 用户确认 → git commit (或 revert)
```

---

## 4. Stage 35 协同架构

```
nuwa (蒸馏人) ──┐
                ├──► SKILL.md + test-prompts.json
cangjie (蒸馏书)─┤      ↓
                ├──► darwin Phase 0.5 (neat-freak gate)
                │      ↓
                ├──► darwin Phase 1 (9 维 rubric + 3 judge)
                │      ↓
                ├──► darwin Phase 2 (hill climbing + paired 比较)
                │      ↓
                └──► darwin Phase 3 (result-card.html)
                            ↓
                ┌──► 反哺天龙 skill 库
                │    或回滚到原版本
```

---

## 5. 核心数字

| 维度 | 数字 |
|---|---|
| 默认 judge 数 | 3（奇数）|
| 默认优化轮数 | 5（auto break）|
| Rubric 总分 | 100（结构 59 + 效果 35 + meta 6）|
| paired delta 阈值 | > 0 keep，≤ 0 revert |
| neat-freak 集成 | Phase 0.5 gate |

---

## 6. 后续协同

- **36 候选**：darwin 优化天龙 38 个主仓 skill（按质量分排序）
- **37 候选**：darwin 自动 + neat-freak 自动双轨（每日 cron）
- **38 候选**：darwin 进化结果 → book-distiller V9.12 post_distill_vet