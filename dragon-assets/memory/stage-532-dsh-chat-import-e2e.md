# Stage 53.2 · Nwflower/dsh-chat-import 真机 e2e · 主题文件

> **阶段**：天龙引擎 · **stage 53.2**（**真机 e2e 验证 · 维护档 0 PASS**）
> **日期**：2026-08-26
> **关联**：stage 53.1 借鉴档（19/19 unittest 已过）+ DSH 真机 import_chat 调用

---

## 一、TL;DR

> Nwflower/dsh-chat-import 借鉴档（stage 53.1）已落 19/19 unittest。**本阶段 53.2 仅记录真机 e2e 验证状态 + 维护档角色（0 PASS）**。累计 PASS 939 → **939 锁定**（stage 54.1 借鉴档 +4 PASS 已合并入 54 row）。

---

## 二、stage 53.2 真机 e2e 状态

| 项 | 状态 |
|---|---|
| npm `dsh-chat-import` 已发布 | ✅ |
| stage 53.1 bridge 19/19 unittest PASS | ✅ |
| DSH Desktop 安装 `dsh plugin --profile web add dsh-chat-import` | ⏳ 用户真机执行 |
| `import_chat({format:"claude", path:"~/.claude/projects/"})` 实证 | ⏳ 用户真机执行 |
| `import_chat({format:"codex", path:"~/.codex/sessions/"})` 实证 | ⏳ 用户真机执行 |
| `export_chat({format:"claude"})` 反向 export 实证 | ⏳ 用户真机执行 |

> 维护档角色：作为 stage 53 完整性的"e2e 待验证"标记。**0 PASS 是设计目标**（借鉴档 + e2e 验证是 stage 53.1 + 53.2 共同完成，53.1 已 +5）。

---

## 三、stage 53.2 维护档配套动作清单

- [x] stage 53.1 dsh-chat-import-bridge 借鉴档（19/19 unittest + 5 CLI + SKILL.md）
- [x] stage 53.2 主题文件（**本文件** · 维护档角色）
- [ ] 用户在 DSH 真机 `dsh plugin --profile web add dsh-chat-import`
- [ ] 实测 17+ Agent 来源（**任选 1-2 个**）：claude / codex / dsh
- [ ] 反向 export 验证（claude / codex / kimi 3 格式）
- [ ] 30 天后 stage 56 recheck（看 Nwflower 上游是否新增 format）

---

## 四、累计 PASS 锁定

```
939 (Stage 54 累计 · 另一个会话合并后)
   +0 (stage 53.2 真机 e2e · 维护档 · 不新增 pytest)
                          │
                          ─► 939 locked
```

---

## 五、跳转入口

- **stage 53.1 主题文件**：[`memory/stage-531-dsh-chat-import.md`](stage-531-dsh-chat-import.md)
- **stage 53.1 借鉴档 SKILL.md**：[`skills/dsh-chat-import-bridge/SKILL.md`](../skills/dsh-chat-import-bridge/SKILL.md)
- **上游 npm 包**：[dsh-chat-import](https://www.npmjs.com/package/dsh-chat-import)
- **DSH 协议治理基线**：[`docs/dsh-ecosystem-license-policy.md`](../docs/dsh-ecosystem-license-policy.md)

---

> **下次同步点**：用户在 DSH 真机装入 dsh-chat-import + 实测 import_chat / export_chat 至少 1 个 format 后，回填本主题文件"真机 e2e 状态"。
