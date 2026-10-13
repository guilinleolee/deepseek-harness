# AGENT.md · nuwa-skill × 天龙引擎

> **协议**：Agent 工作约定（与上游 nuwa-skill 平级扩展，但**不修改** upstream 任何字节）

---

## 1. 何时使用本 skill

由 [SKILL.md `description`](SKILL.md) 的 trigger 词触发，主要场景：

| 触发词 | 路径 |
|---|---|
| 「蒸馏 XX」/「造 XX 的 skill」| Phase 0A → 直接路径 |
| 「我想提升 XX」/「我需要一个思维顾问」| Phase 0B → 诊断路径 |
| "distill [person]" / "how does [person] think" | 英文直接路径 |

---

## 2. 天龙引擎协同约定

### 2.1 与 35-02 / 35-06 博主全息协同

- 直接使用 `~/.claude/ip-profiles/laoli_bro_2026/` 作为本地语料（**先读 IP 授权** `ip_consent.txt` 必须在有效期内）
- nuwa 蒸馏产物（人/思维模式 skill）→ `[ip-profiles/<id>/skills/]` 落地
- 与 `skills/blogger-fingerprint-registry/` V3.0 共享 10 维指纹

### 2.2 与 cangjie + darwin 三件套协同

- nuwa 产出的"人物 skill" → 喂 darwin 进化 → 反哺天龙 skill 库
- nuwa 与 cangjie 输出格式对齐（均产出 `test-prompts.json` 供 darwin 评估）

### 2.3 与 28-01 / 28-04 (内容策划师) 协同

- 28-04 用 nuwa 蒸馏的"语料"作为 ip 描述 chapter 输入
- 28-01 (khazix-writer) 把 nuwa 蒸馏的"表达 DNA"注入到 khazix 文风

---

## 3. 蒸馏档位协议（成本控制）

天龙调用约定：

| 档位 | 调研规模 | 成本 | 触发条件 |
|---|---|---|---|
| **快速** | 3 维度，每维 5 来源 | ≈ 标准 1/3 | 冷门人物 / 预算敏感 / 试效果 |
| **标准**（默认）| 6 维完整 | 中等 | 默认 |
| **深度** | 6 维 + 全量一手素材 | 最高 | 打算开源发布精品 skill |

**默认不阻塞交付**：所有未明确问题先用默认值。

---

## 4. Agent 工作流要点

1. **永远先读 IP 授权**（如果用本地 IP 语料）
2. **永远先产出一个最小可启动阶段**（访谈提纲 / 执行计划），不把所有问题卡在确认前
3. **永远本地 quiz 模式 + 联网搜索双源**（`agent-reach` V1.5.0）
4. **永远输出 `test-prompts.json`**（cangjie / nuwa 协议对齐，darwin 可消费）

---

## 5. 不在天龙范围内的约束

- **不绕过 IP 授权**——`ip_consent.txt` 过期自动降级为公开人物模式
- **不重复蒸馏**——`~/.claude/skills/<person>-perspective/` 存在则优先更新而非新建
- **不在 nuwa 内重做 nuwa**——避免 meta 递归

---

## 6. 后续协同点

- **阶段 36 候选**：把 nuwa 蒸馏产物落双路径（`~/.claude/skills/` + `dragon-engine/skills/<person>-perspective/`）
- **阶段 37 候选**：nuwa 蒸馏时自动跑 `neat_freak_check.py` 防红线
- **阶段 38 候选**：nuwa 蒸馏成本统计 → dragon-engine 月度报告
