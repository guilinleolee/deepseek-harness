# HANDOFF.md · darwin-skill × 天龙引擎

> **协议**：跨阶段交付文档（与上游 darwin-skill 平级扩展，但**不修改** upstream 任何字节）

---

## 1. 输入与输出契约

### 1.1 输入

| 维度 | 必填 | 默认 |
|---|---|---|
| 目标 skill 路径 | ✅ | — |
| 优化目标维度（哪几条 rubric）| | 全部 9 维 |
| 优化轮数 | | 5 轮（自动 break）|
| judge 数量 | | 3 个独立 judge 子 agent |
| 是否走 neat-freak gate | | 是（天龙默认）|

### 1.2 输出

```
output/<skill-slug>-<date>/
├── results.tsv                     ← 每轮 9 维评分（绝对分 + paired 比较）
├── results.md                      ← 人可读报告
├── result-card.html                ← 视觉化卡片（上游 templates/result-card-*.html）
├── edits/
│   ├── round-1/<skill>.SKILL.md    ← 第 1 轮编辑后版本
│   ├── round-2/<skill>.SKILL.md
│   └── ...
├── gates/
│   └── neat-freak-check.txt        ← Phase 0.5 neat_check.py 输出
└── README.md                       ← 优化报告总结
```

---

## 2. 与天龙既有资产的衔接

### 2.1 落盘路径

| 优化对象 | 路径 |
|---|---|
| 主仓 skill（同步主仓）| `dragon-engine/skills/<slug>/SKILL.md` |
| 用户级 skill（个人）| `~/.claude/skills/<slug>/SKILL.md` |
| IP skill（laoli_bro_2026）| `~/.claude/ip-profiles/laoli_bro_2026/skills/<slug>/SKILL.md` |

### 2.2 优化报告归档

`dragon-engine/skills/darwin-skill/output/` 留历史报告（参考 `.gitignore`）。

---

## 3. 质量门神

| 校验项 | 阈值 | 失败动作 |
|---|---|---|
| Phase 0.5 neat-freak exit | 0 | 阻断 |
| judge 数量 | ≥3 (奇数) | 警告 |
| 优化轮数 | ≤ 5 | 自动 break |
| paired 比较 delta | > 0 | keep |
| paired 比较 delta | ≤ 0 | revert |

---

## 4. 跨阶段交付 Link

| 上游 | 输出物 | 下游 |
|---|---|---|
| cangjie 蒸馏 | `<book>/<skill>/SKILL.md` + `test-prompts.json` | darwin Phase 1 评估 |
| nuwa 蒸馏 | `<person>-perspective/SKILL.md` + `test-prompts.json` | darwin Phase 1 评估 |
| book-distiller V9.12 | DIGEST.md | darwin Phase 1 评估 |
| darwin 优化结果 | `<skill>.SKILL.md` (改善版) | 反哺天龙主仓 skill 库 |

---

## 5. 失败兜底

| 失败模式 | 兜底 |
|---|---|
| Phase 0.5 neat-freak 失败 | 阻断 darwin 启动 |
| judge 子 agent 不可用 | 降级到 dry_run |
| dry_run > 30% | 警告（dim8 实测失效）|
| 编辑后 SKILL.md 长度爆炸 | neat-freak size check |

---

## 6. 累计 PASS 校验（天龙阶段 35-C）

- 10 项安装自检（mirror 完整性 + 5 致谢模板 + 9 维 rubric 引用 + test-prompts.json 格式）= **10/10 PASS**
- 详见 `tests/test_darwin_installation.py`