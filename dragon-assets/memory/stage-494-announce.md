---
name: stage-494-announce
description: Stage 49.4 总验收公告 — open-design-bridge V1.0（借鉴档 · Apache-2.0 重量档 · 91,574⭐ · DSH 生态第一热度）
metadata:
  node_type: memory
  originSessionId: stage-494-open-design-20260826
  modified: 2026-08-26T11:38:08.000Z
---

# 🚀 Stage 49.4 总验收公告 · 2026-08-26

> **TL;DR**：天龙引擎 Stage 49.4 借鉴 [nexu-io/open-design](https://github.com/nexu-io/open-design) V0.20.3（**Apache-2.0 ✅** · **91,574⭐ / 10,536 🍴** · DSH 生态第一热度 · 1.85 MB） 的 **5 类核心设计** + **天龙自研 V1.0**。**天龙首个 Apache-2.0 重量档集成**。累计 **PASS 890 → 893**（+3 net · 16/16 自研 unittest 拆 6 大类）。

---

## 一、本阶段交付

| W# | 任务 | 关键产物 | 验证 |
|---|---|---|---|
| **W1** | D1 R1 协议评估 | Apache-2.0 ✅ · LICENSE 11,296 B verbatim | ✅ |
| **W1** | open-design-bridge V1.0 + 5 类借鉴 + 5 CLI | `SKILL.md V1.0` + `open_design_bridge.py` + 16/16 unittest PASS | ✅ 自检通过 |
| **W1** | Apache-2.0 NOTICE 模板（与 stage 17 同模式）| `APACHE_NOTICE_TEMPLATE` 常量 · 含 'Modifications by dragon-engine' 段 | ✅ |
| **W1** | 主题文件 + MEMORY row + 本文件 | `memory/stage-494-open-design.md` (10 KB) + MEMORY 893 PASS | ✅ |

---

## 二、5 类借鉴

### 2.1 LocalFirstConfig
```python
@dataclass
class LocalFirstConfig:
    cache_dir: str = "~/.open-design/cache"
    preview_sandbox: bool = True
    offline_first: bool = True
    byok_only: bool = True      # ← Apache NOTICE 红线
```

### 2.2 20+ CLIs BYOK 检测
```python
SUPPORTED_CLIS = [
    {"name": "claude",   "binary": "claude",   "api_key_env": "ANTHROPIC_API_KEY"},
    {"name": "codex",    "binary": "codex",    "api_key_env": "OPENAI_API_KEY"},
    {"name": "deepseek", "binary": "dsh",      "api_key_env": "DEEPSEEK_API_KEY"},
    # +17
]
```

### 2.3 Sandboxed Preview
- `ALLOWED = ["/tmp", "/workspace", "./.preview"]`
- `/etc/*` / `/home/*` 被 block

### 2.4 Design Skill 模板
```python
generate_design_skill_template(name)  # borrowed_from 默认 'nexu-io/open-design'
```

### 2.5 Apache-2.0 NOTICE 模板
```python
APACHE_NOTICE_TEMPLATE = """
open-design-bridge V1.0
Copyright 2026 dragon-engine team
This product includes software developed at The Apache Software Foundation.
This product includes software developed by nexu-io.
Modifications by dragon-engine:
- Stage 49.4: borrowed-bridge V1.0 (not mirror真源)
- Stage 49.4: 自研 4 CLI 不实跑上游 1.8 MB 仓库
"""
```

---

## 三、16/16 自研 unittest PASS 拆 6 大类

```
✓ TestLocalFirstConfig  (3)  # default valid + offline + byok
✓ TestCLIDetect         (3)  # count + dsh + detect
✓ TestSandboxValidation (5)  # /tmp + /workspace + .preview + /etc + /home
✓ TestSkillTemplate     (2)  # default + custom
✓ TestApacheNotice      (2)  # 'Apache' + 'Modifications by'
✓ TestEndToEnd          (1)
                       16/16 ✓ 2.54s
```

---

## 四、累计 PASS 锁定

```
882 (Stage 48 累计)
   +3 ─► 885 (stage 49.1)
   +5 ─► 890 (stage 49.2)
   +3 ─► 893 (stage 49.4)
                          │
                          ─► 893 locked
```

**stage 49 三借鉴档并行净增 +11 PASS**（与 stage 47 双借鉴档节奏一致）

---

> **下次同步点**：用户在天龙 `open_design_bridge.py detect-clis` 输出本地已装 CLI 列表（如果 dsh/claude/codex 已装）。
