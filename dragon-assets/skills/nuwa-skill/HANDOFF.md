# HANDOFF.md · nuwa-skill × 天龙引擎

> **协议**：跨阶段交付文档（与上游 nuwa-skill 平级扩展，但**不修改** upstream 任何字节）

---

## 1. 输入与输出契约

### 1.1 输入

| 维度 | 必填 | 默认 |
|---|---|---|
| 人物名 / 主题 | ✅ | — |
| 用途（思维顾问 / 决策参考 / 角色扮演）| | 思维顾问 |
| 聚焦方向（全面 / 聚焦某维度）| | 全面 |
| 新建 vs 更新 | | 自动检测 |
| 本地语料（PDF / transcript / 字幕）| | 无（走网络搜索）|
| 蒸馏档位（快速 / 标准 / 深度）| | 标准 |

### 1.2 输出

```
output/
├── <person>-perspective/
│   ├── SKILL.md              ← 主人物 skill（5 维：心智模型/决策/表达/反模式/诚实边界）
│   ├── test-prompts.json     ← darwin 兼容测试集（≥3 should_trigger + 2 should_not_trigger + 1 edge）
│   ├── quality_check_result.json  ← 跑 quality_check.py 的输出
│   └── README.md
└── index.md                  ← 蒸馏元数据（档位/成本/时长）
```

---

## 2. 与天龙既有资产的衔接

### 2.1 落盘路径

| 用途 | 路径 |
|---|---|
| 公开发布（任何人都能用）| `~/.claude/skills/<person>-perspective/` |
| 博主全息（与 laoli_bro_2026 协同）| `~/.claude/ip-profiles/laoli_bro_2026/skills/<person>-perspective/` |
| 主题研究（与 28-04 内容策划协同）| `dragon-engine/skills/<person>-perspective/` |

### 2.2 与 cangjie (AGPL) 共存

- **nuwa 蒸馏人**（产物是 `<person>-perspective/SKILL.md`）
- **cangjie 蒸馏书**（产物是 `<book-slug>/<skill-slug>/SKILL.md`）
- 两者不冲突，但产物的 `test-prompts.json` 要对齐 schema（darwin 可同时消费）

### 2.3 与 darwin 衔接

- nuwa 产出 → darwin 评估 → 改进 → 保留或回滚
- 自动产物：`<person>-perspective/test-prompts.json` → `darwin-skill/results.tsv`

---

## 3. 质量门神（天龙额外约束）

| 校验项 | 阈值 | 失败动作 |
|---|---|---|
| 心智模型数 | 3-7 | 阻断 |
| 表达 DNA 特征 | ≥3 | 阻断 |
| 诚实边界 | ≥3 条 | 阻断 |
| 内在张力 | ≥2 对 | 阻断 |
| 一手来源占比 | >50% | 警告 |
| 三重验证（V1 跨域 / V2 预测力 / V3 独特性）| 全过 | 阻断 |
| MIT 致谢段（5 模板）| 完整 | 警告 |

`scripts/quality_check.py` 跑全部 7 项。

---

## 4. 跨阶段交付 Link

| 上游 | 输出物 | 下游 |
|---|---|---|
| 公开人物 distill | `<person>-perspective/SKILL.md` | `dragon-engine/skills/` 或 `~/.claude/skills/` |
| IP 授权人物 distill | `<person>-perspective/SKILL.md` | `~/.claude/ip-profiles/<id>/skills/` |
| nuwa 蒸馏产物 | `test-prompts.json` | darwin-skill Phase 1 评估 |

---

## 5. 失败兜底

| 失败模式 | 兜底 |
|---|---|
| 一手语料缺失 | 全部走网络搜索（`agent-reach` V1.5.0）|
| 蒸馏档位超预算 | 半自动降级（用户确认）|
| 既有同名 skill 冲突 | 提示用户「更新 vs 新建」|
| IP 授权过期 | 自动降级为公开人物模式 |

---

## 6. 累计 PASS 校验（天龙阶段 35-A）

- 10 项安装自检（mirror 完整性 + 5 致谢模板 + frontmatter 字段 + references 引用 + scripts 可执行）= **10/10 PASS**
- 详见 `tests/test_nuwa_installation.py`
