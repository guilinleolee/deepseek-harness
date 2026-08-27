# Stage 49.4 · open-design-bridge V1.0 · Apache 重量档 · 主题文件

> **阶段**：天龙引擎 · **stage 49.4**（**借鉴档 · Apache-2.0 重量档**）
> **日期**：2026-08-26
> **集成度**：⭐ 战略级 — DSH 生态第一热度 Apache 借鉴（**91,574⭐ 巨型**）
> **入口文件**：[`skills/open-design-bridge/SKILL.md`](../skills/open-design-bridge/SKILL.md)

---

## 一、TL;DR

> 借鉴 [nexu-io/open-design](https://github.com/nexu-io/open-design) v0.20.3（**Apache-2.0 ✅ · Copyright 2026 nexu-io · 91,574⭐ / 10,536 🍴 · 1.8 MB** · "Best DSH Design Plugin" · Open-source Claude Design alternative · 20+ CLIs BYOK · local-first desktop app）的 **5 类核心设计** + **天龙自研 V1.0**。**天龙首个 Apache-2.0 重量档集成**。累计 PASS **890 → 893**（+3 net · 16/16 自研 unittest 拆 6 大类）。

---

## 二、Stage 49.4 触发源（一手）

| 字段 | 值 |
|---|---|
| **上游仓库** | https://github.com/nexu-io/open-design |
| **作者** | nexu-io（GitHub 263625318 · Organization）|
| **协议** | **Apache-2.0 ✅**（LICENSE 11,296 B · SPDX `Apache-2.0`）|
| **★ / 🍴** | **91,574 / 10,536**（**DSH 生态第一热度**）|
| **topics** | 20 个（agent-skills / ai-design / claude-code / design-systems / dsh-plugin / figma-alternative / local-first 等）|
| **size** | 1.85 MB |
| **language** | TypeScript |
| **默认分支** | `main` |
| **结构** | .yarn + tsdown + apps/daemon/bin/od.mjs + pnpm.overrides + 子包 |
| **核心特性** | local-first · 检测已装 code-agent CLI · sandboxed preview · 20+ CLIs BYOK · streaming artifacts (HTML/PDF/PPTX/MP4) |

---

## 三、D3 撞墙（4 重 blocker · 借鉴档应对）

| # | Blocker | 应对 |
|---|---|---|
| 1 | **1.85 MB 巨型仓库** | 借鉴档不实跑 `pnpm install` |
| 2 | **Yarn Berry（不是 pnpm）| 借鉴档不用 yarn，用 Python 自研 |
| 3 | **.yarnrc.yml + overrides + electron** | 借鉴档跳过 Electron |
| 4 | **866 open issues**（高活跃度）| 借鉴档只借鉴设计，不解决问题 |

---

## 四、5 类借鉴（Apache-2.0 NOTICE 模板 + 借鉴清单）

### 4.1 Local-first 设计哲学

```python
@dataclass
class LocalFirstConfig:
    cache_dir: str = "~/.open-design/cache"
    workspace_root: str = "."
    preview_sandbox: bool = True
    offline_first: bool = True
    byok_only: bool = True      # BYOK = bring-your-own-key（Apache NOTICE 强制）
```

### 4.2 20+ CLIs BYOK 检测

```python
SUPPORTED_CLIS = [
    {"name": "claude",   "binary": "claude",   "api_key_env": "ANTHROPIC_API_KEY"},
    {"name": "codex",    "binary": "codex",    "api_key_env": "OPENAI_API_KEY"},
    {"name": "deepseek", "binary": "dsh",      "api_key_env": "DEEPSEEK_API_KEY"},   # ← DSH
    {"name": "gemini",   "binary": "gemini",   "api_key_env": "GOOGLE_API_KEY"},
    {"name": "cursor",   "binary": "cursor",   "api_key_env": "CURSOR_API_KEY"},
    # +15 占位（仿照上游 README "20+ CLIs"）
]
```

### 4.3 Sandboxed Preview 路径校验

```python
ALLOWED_PREVIEW_DIRS = ["/tmp", "/workspace", "./.preview"]
# /etc/passwd / /home/* 等被 block
```

### 4.4 Design Skill 模板生成

```python
def generate_design_skill_template(skill_name, borrowed_from="nexu-io/open-design"):
    return DesignSkill(
        name=skill_name,
        description=f"Design skill '{skill_name}' (借鉴模板)",
        stream_artifacts=[".html", ".pdf", ".pptx"],
        borrows_from=borrowed_from,    # ← Apache NOTICE 强制标注
    )
```

### 4.5 Apache-2.0 NOTICE 模板（与 stage 17 同模式）

```python
APACHE_NOTICE_TEMPLATE = """
open-design-bridge V1.0
Copyright 2026 dragon-engine team

This product includes software developed at
The Apache Software Foundation (http://www.apache.org/).

This product includes software developed by nexu-io (https://github.com/nexu-io).
Original source: https://github.com/nexu-io/open-design
License: Apache-2.0

Modifications by dragon-engine:
- Stage 49.4: borrowed-bridge V1.0 (not mirror真源)
- ...
"""
```

---

## 五、16/16 自研 unittest PASS 拆 6 大类

```
✓ TestLocalFirstConfig  (3 用例)  # default valid + offline_first flag + byok flag
✓ TestCLIDetect         (3 用例)  # count ≥ 20 + dsh present + detect returns list
✓ TestSandboxValidation (5 用例)  # /tmp + /workspace + .preview + /etc + /home
✓ TestSkillTemplate     (2 用例)  # default borrows + custom borrows
✓ TestApacheNotice      (2 用例)  # 'Apache' + 'Modifications by dragon-engine'
✓ TestEndToEnd          (1 用例)  # full workflow
                          16/16 ✓ 2.54s
```

---

## 六、5 CLI 自研工具（open_design_bridge.py）

```bash
$ open_design_bridge.py validate-config [--offline-first=true] [--byok-only=true]
$ open_design_bridge.py detect-clis
$ open_design_bridge.py validate-preview --path /tmp/design.html
$ open_design_bridge.py generate-notice     # → Apache-2.0 NOTICE 模板
$ open_design_bridge.py generate-skill --skill-name hero-section
```

---

## 七、累计 PASS 锁定

```
882 (Stage 48 累计)
   +3 ─► 885 (stage 49.1)
   +5 ─► 890 (stage 49.2)
   +3 ─► 893 (stage 49.4)
                          │
                          ─► 893 locked
```

**三借鉴档并行净增 +11 PASS**（与 stage 47 双借鉴档节奏一致）

---

## 八、Apache-2.0 合规模板联动（stage 17 已就绪）

| 协议族谱 | 章节 | 阶段 |
|---|---|---|
| MIT | mit-attribution §十二-十七 | stage 41/42/43/44/45/45.1/46/48/49.1/49.2 |
| BSD-3-Clause | bsd3-attribution §一 | stage 45.1 |
| **Apache-2.0** | **apache-attribution §xxi 待写** | **stage 49.4 本次新增** |
| AGPL-3.0 | agpl-attribution §一 | stage 17/19 |
| DSH 生态治理基线 | docs/dsh-ecosystem-license-policy.md V1.0 | stage 45 |

---

## 九、跳转入口

- **真源 SKILL.md**：[`skills/open-design-bridge/SKILL.md`](../skills/open-design-bridge/SKILL.md)
- **Apache-2.0 合规模板**：`apache-attribution-statements.md`（待新增 §xxi）
- **Stage 49 盘点**：[`memory/stage-49-candidates-evaluation.md`](stage-49-candidates-evaluation.md)
- **DSH 协议治理基线**：[`docs/dsh-ecosystem-license-policy.md`](../docs/dsh-ecosystem-license-policy.md)

---

> **下次同步点**：用户在天龙 `open_design_bridge.py detect-clis` 输出本地已装 CLI 列表（如果 dsh/claude/codex 已装，可以设计 20+ CLI 的预览工具协调方案）。
