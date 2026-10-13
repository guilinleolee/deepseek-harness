# l3-specs/ · darwin-skill × 天龙引擎本地增强

> **MIT 允许子包装**：darwin 是 MIT 协议，可在天龙本地添加 `l3-specs/` 子目录写本地增强，**无需公开修改源码**。

---

## 1. 文件清单

| 文件 | 用途 |
|---|---|
| `darwin-neat-freak-bridge.md` | darwin Phase 0.5 neat-freak V1.1 红线 gate（防止 Apache/AGPL/MIT 红线误触）|
| `darwin-test-prompts-schema.md`（占位）| darwin 兼容 test-prompts.json 协议（与 cangjie / nuwa 共享）|
| `darwin-rubric-extension.md`（占位）| 天龙 9 维 rubric + 4 条额外红线（MIT 致谢 / AGPL 红线 / Apache NOTICE / neat-freak）|

---

## 2. 与 cangjie + nuwa 共享的 test-prompts.json schema

darwin 可同时消费 cangjie 和 nuwa 产出的 test-prompts.json：

```json
{
  "skill": "<slug>",
  "version": "0.1.0",
  "source": "<book-or-person> — <author>",
  "darwin_compatible": true,
  "test_cases": [
    {"id": "should-trigger-01", "type": "should_trigger", "prompt": "...", "expected_behavior": "...", "notes": "..."},
    ...,
    {"id": "should-not-trigger-01", "type": "should_not_trigger", "prompt": "...", "expected_behavior": "...", "notes": "..."},
    {"id": "edge-01", "type": "edge_case", "prompt": "...", "expected_behavior": "...", "notes": "..."}
  ],
  "minimum_pass_rate": 0.8
}
```

7 字段 schema，darwin 直接消费。

---

## 3. 累计 PASS 增量（天龙阶段 35-C）

- 10 项 darwin 安装自检 = **+10 PASS**
- 详见 `tests/test_darwin_installation.py`

---

## 4. 失败兜底

| 失败模式 | 兜底 |
|---|---|
| Phase 0.5 neat-freak 失败 | 阻断 darwin |
| judge 子 agent 不可用 | 降级到 dry_run |
| paired delta 全为负 | 自动 break + 回滚 |
