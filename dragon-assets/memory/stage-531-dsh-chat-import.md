# Stage 53.1 · dsh-chat-import-bridge V1.0 · 主题文件

> **阶段**：天龙引擎 · **stage 53.1**（**借鉴档 · 轻量 · MIT · 17+ Agent 集成**）
> **日期**：2026-08-26
> **集成度**：⭐ 战略级 — 跨 Agent 数据迁移 · 与 stage 41 mneme-heat-engine 协同
> **入口文件**：[`skills/dsh-chat-import-bridge/SKILL.md`](../skills/dsh-chat-import-bridge/SKILL.md)

---

## 一、TL;DR

> 借鉴 [Nwflower/dsh-chat-import](https://github.com/Nwflower/dsh-chat-import)（**MIT ✅** · "Copyright (c) 2026 Nwflower, Copyright (c) 2026 Scarlett" · npm `dsh-chat-import` · **17+ agent 来源格式** · **import + export + sync + bundle**）的 **5 类核心设计** + **天龙自研 V1.0**。累计 PASS **924 → 929**（+5 net · 19/19 自研 unittest 拆 7 大类）。

---

## 二、触发源（一手）

| 字段 | 值 |
|---|---|
| **上游** | https://github.com/Nwflower/dsh-chat-import |
| **作者** | Nwflower（GitHub 105714958）|
| **协议** | **MIT ✅**（LICENSE 1,093 B · 21 行 · SPDX `MIT`）|
| **★ / 🍴** | 待查（搜索响应未含）|
| **language** | TypeScript |
| **Node.js** | ≥ 22.13 |
| **npm** | `dsh-chat-import` 已发布 |
| **创建** | 2026-08-13T14:21:58Z（**13 天前**）|
| **dsh 兼容** | 0.1.x（tested 0.1.0-rc.6 / 0.1.0-rc.7）|
| **收录** | ✅ Listed in 0xsline/awesome-deepseek-harness |
| **核心特性** | "Import 17+ external agent conversation histories into DeepSeek Harness as full-fidelity, resumable sessions — and export / sync back" |

---

## 三、5 类借鉴

### 3.1 17+ Agent 来源格式
| format | display | storage |
|---|---|---|
| `claude` | Claude Code | `~/.claude/projects/<slug>/<sessionId>.jsonl` |
| `codex` | Codex / ChatGPT CLI | `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` |
| `chatgpt` | ChatGPT (web export) | `conversations.json` |
| `cursor` | Cursor | `~/.cursor/projects/<slug>/agent-transcripts/<id>/<id>.jsonl` |
| `gemini` | Gemini CLI | `~/.gemini/history/<slot>/chats/session-*.json` |
| `reasonix` | Reasonix | `~/.reasonix/sessions/desktop-*.jsonl` |
| `opencode` | opencode | `~/.local/share/opencode/opencode.db` |
| `mimocode` | MiMo Code | `~/.local/share/mimocode/mimocode.db` |
| `zcode` | ZCode | `~/.zcode/cli/db/db.sqlite` |
| `grokbuild` | Grok Build | `~/.grok/sessions/<project>/<session_id>/` |
| `openclaw` | OpenClaw | `~/.openclaw/agents/<agent>/sessions/*.jsonl` |
| `pi` | Pi Coding Agent | `~/.pi/agent/sessions/--<cwd>--/<timestamp>_<uuid>.jsonl` |
| `hermes` | Hermes | `~/.hermes/` |
| `kimi` | Kimi CLI / Kimi Code | `~/.kimi/sessions/<workdir-md5>/<sessionId>/wire.jsonl` |
| `qoder` | Qoder CLI | `~/.qoder/projects/<encoded-project>/<sessionId>.jsonl` |
| `workbuddy` | WorkBuddy (Tencent) | `~/.workbuddy/projects/<project-hash>/<session-uuid>.jsonl` |
| `dsh` | DSH session logs | `~/.dsh/sessions/<encoded-workspace>/<sessionId>/session.jsonl(.zstd)` |
| `local-jsonl` | Any local JSONL | auto-detected |

### 3.2 import_chat 工具协议
```python
ImportChatRequest(format, path, preview, force, session_id, expected_hash)
```

### 3.3 matrix export 3 格式
```python
EXPORT_FORMATS = ["claude", "codex", "kimi"]
```

### 3.4 SHA-256 dedup + idempotency
```python
def check_idempotency(current_sha, stored_sha) -> str:
    # "skip" | "import" | "append"
```

### 3.5 portable interchange bundle
- dual SHA-256 fingerprint（primary + secondary）
- export_bundle / restore_bundle 跨机器

---

## 四、19/19 自研 unittest PASS 拆 7 大类

```
✓ TestSupportedFormats   (4)  # 17+ 来源格式 + claude/dsh 必含 + storage 字段
✓ TestValidateImport     (5)  # 5 字段 schema 校验 + valid_hash
✓ TestExportFormats       (1)  # 3 format
✓ TestSHA256Dedup         (3)  # consistent + different + length 16
✓ TestIdempotency         (3)  # skip / import / append
✓ TestInterchangeBundle   (2)  # integrity match + mismatch
✓ TestEndToEnd            (1)  # full workflow
                          19/19 ✓ 0.001s
```

---

## 五、5 CLI 自研工具（dsh_chat_import_bridge.py）

```bash
$ dsh_chat_import_bridge.py list-formats                       # 17+ agent 来源
$ dsh_chat_import_bridge.py validate-import --format dsh --path ~/.dsh/
$ dsh_chat_import_bridge.py check-idempotency --current c3d4 --stored a1b2
$ dsh_chat_import_bridge.py sha256-dedup --input "test content"
$ dsh_chat_import_bridge.py list-export-formats               # claude/codex/kimi
```

---

## 六、累计 PASS 锁定

```
924 (Stage 53 累计)
   +5 ─► 929   dsh_chat_import_bridge.py 19/19 自研 unittest PASS
                  (上游 npm `dsh-chat-import` 100+ 测试计入上游库不双计)
                          │
                          ─► 929 locked
```

---

## 七、跳转入口

- **真源 SKILL.md**：[`skills/dsh-chat-import-bridge/SKILL.md`](../skills/dsh-chat-import-bridge/SKILL.md)
- **DSH 协议治理基线**：[`docs/dsh-ecosystem-license-policy.md`](../docs/dsh-ecosystem-license-policy.md)
- **Stage 53 盘点**：[`memory/stage-53-candidates-evaluation.md`](stage-53-candidates-evaluation.md)
- **上游 npm**：[dsh-chat-import](https://www.npmjs.com/package/dsh-chat-import)

---

> **下次同步点**：用户在 DSH 真机 `dsh plugin --profile web add dsh-chat-import` 后跑 `import_chat({format:"dsh",path:"~/.dsh/"})` + export 到 Claude 格式。
