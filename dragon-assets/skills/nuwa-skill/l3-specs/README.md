# l3-specs/ · nuwa-skill × 天龙引擎本地增强

> **MIT 允许子包装**：nuwa 是 MIT 协议，可在天龙本地添加 `l3-specs/` 子目录写本地增强，**无需公开修改源码**（与 AGPL 不同）。

---

## 1. nuwa-laoli-bridge.md（占位）

nuwa 蒸馏 laoli_bro_2026 时，自动调用 `~/.claude/ip-profiles/laoli_bro_2026/ip_consent.txt`（必须在有效期内）+ 10 维指纹 (`blogger-fingerprint-registry` V3.0)。

---

## 2. nuwa-cangjie-test-prompts-schema.md（占位）

nuwa 输出的 `test-prompts.json` 严格遵循 cangjie 的 darwin 兼容 schema 7 字段：

```json
{
  "skill": "<person-slug>",
  "version": "0.1.0",
  "source": "<person> — <author>",
  "darwin_compatible": true,
  "test_cases": [
    {"id": "should-trigger-01", "type": "should_trigger", "prompt": "...", "expected_behavior": "...", "notes": "..."},
    ...,
    {"id": "should-not-trigger-01", "type": "should_not_trigger", "prompt": "...", "expected_behavior": "...", "notes": "..."},
    {"id": "edge-01", "type": "edge_case", "prompt": "...", "expected_behavior": "...", "notes": "..."}
  ],
  "minimum_pass_rate": 0.8,
  "notes": "至少 3 条 should_trigger + 2 条 should_not_trigger + 1 条 edge_case..."
}
```

darwin 可直接消费，无需 schema 转换。

---

## 3. nuwa-quality-check-v1.md（占位）

天龙对 nuwa 上游 `scripts/quality_check.py` 的扩展（5 维 + 4 条额外红线）：

| 校验项 | 阈值 | 失败动作 |
|---|---|---|
| 心智模型数 | 3-7 | 阻断 |
| 表达 DNA 特征 | ≥3 | 阻断 |
| 诚实边界 | ≥3 条 | 阻断 |
| 内在张力 | ≥2 对 | 阻断 |
| 一手来源占比 | >50% | 警告 |
| **天龙额外** | | |
| 个性化识别度 | ≥3 处「only X says」字样 | 警告 |
| 与既有 skill 差异化 | ≥1 处「vs Y」引述 | 警告 |
| MIT 致谢段（5 模板）| 完整 | 警告 |
| test-prompts.json 格式 | darwin 兼容 | 警告 |

---

## 4. 核心调用流程（nuwa × 天龙）

```
1. 用户：「蒸馏 laoli_bro_2026」
2. ↓
3. nuwa Phase 0A：确认聚焦方向 → 全面 + 决策参考 + 标 准档
4. ↓
5. nuwa Phase 1：6 维度自动调研（多 agent 并行）
6. ↓
7. nuwa Phase 2：生成 SKILL.md（5 维）+ test-prompts.json (darwin 兼容)
8. ↓
9. nuwa Phase 3：跑 quality_check.py（5 维 + 4 条额外 = 9 项）
10. ↓
11. 落 ~/.claude/ip-profiles/laoli_bro_2026/skills/laoli-perspective/
12. ↓
13. 喂 darwin Phase 1 评估 → 改进 → 保留或回滚
14. ↓
14. 反哺 35-02 / 35-06 博主全息
```

---

## 5. 已知局限

- 上游 `quality_check.py` 5 维硬编码，天龙额外 4 条需要重写为 `l3-specs/quality_check_v1.py`
- nuwa 角色扮演能力有限（与 `khazix-writer` 互补）
- 蒸馏成本高（确认档位前明示成本范围）
