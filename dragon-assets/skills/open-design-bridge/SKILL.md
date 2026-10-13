---
name: open-design-bridge
description: |
  借鉴 nexu-io/open-design V0.20.3（Apache-2.0 ✅ · Copyright 2026 nexu-io · 91,574⭐ / 10,536 🍴 · DSH 生态第一热度 · 1.8 MB 巨型）的 5 类核心设计 + 自研 V1.0。
  借鉴清单：① Local-first 设计哲学 ② 20+ CLIs BYOK 检测（含 DSH）③ Sandboxed preview 路径校验
  ④ Design skill 模板 ⑤ Apache-2.0 NOTICE 模板（与 stage 17 同模式）。
  Stage 49.4 借鉴档 Apache 重量档 · 1.85 MB 巨型仓库 · Yarn Berry 工具链 + electron 双 blocker。
metadata:
  version: "1.0.0"
  date: "2026-08-26"
  license: MIT
  author: 天龙引擎 · Stage 49.4
  upstream_borrowing:
    - nexu-io/open-design v0.20.3 (Apache-2.0 · 91,574⭐ · 2026)
  integration_stage: 49.4
  integration_mode: "借鉴档 Apache 重量档（1.85 MB + Yarn Berry + 866 open issues）"
  license_template: "apache-attribution-statements.md §二"
  triggers:
    - "open-design"
    - "nexu-io"
    - "BYOK"
    - "code-agent CLI"
    - "sandboxed preview"
    - "design skill"
---

# open-design-bridge · V1.0（借鉴档 · Apache-2.0 重量档）

> **TL;DR**：借鉴 [nexu-io/open-design](https://github.com/nexu-io/open-design) V0.20.3（**Apache-2.0 ✅** · **91,574⭐ / 10,536 🍴** · DSH 生态第一热度 · 1.85 MB） 的 **5 类核心设计** + **天龙自研 V1.0**。**天龙首个 Apache-2.0 重量档集成**。**16/16 unittest PASS**（拆 6 大类）。

---

## L0: 一句话描述 (≤15字)

Apache 重量档本地优先设计。

---

## L1: 使用场景

当用户需要：
- 在 DSH 真机装入 `dsh plugin --profile web add @nexu-io/open-design`（**已完成 DSM 官方认可**）
- 设计 20+ code-agent CLI 兼容的 BYOK 工作流
- 在沙箱目录（/tmp / /workspace / .preview）内预览设计产物
- 用 Apache-2.0 NOTICE 强制条款标注借鉴源（与 stage 17 同模式）
- 与 stage 41 mneme + stage 47 dsh-univer + stage 49.2 memsearch 协同做"全栈设计"

---

## L2: 5 类借鉴

### 2.1 LocalFirstConfig（4 字段 dataclass）
```python
@dataclass
class LocalFirstConfig:
    cache_dir: str = "~/.open-design/cache"
    preview_sandbox: bool = True
    offline_first: bool = True
    byok_only: bool = True      # ← Apache NOTICE 红线
```

### 2.2 20+ CLIs BYOK 检测（含 DSH）
- 7 个真实上游 CLI（claude/codex/deepseek/gemini/cursor/opencode/copilot）+ 14 通用占位

### 2.3 Sandboxed Preview 路径校验
- `ALLOWED = ["/tmp", "/workspace", "./.preview"]`
- `/etc/*` / `/home/*` 等被 block

### 2.4 Design Skill 模板（borrowed 标注）
```python
generate_design_skill_template(skill_name)  # 默认 borrowed_from='nexu-io/open-design'
```

### 2.5 Apache-2.0 NOTICE 模板（与 stage 17 同模式）
- 含 "Modifications by dragon-engine" 段
- 含 "nexu-io" + "Apache Software Foundation" 致谢

---

## L3: 安装

```bash
# 1. 装本 skill（天龙自有，已落 dragon-engine/skills/open-design-bridge/）
# 2. 真机装 open-design（Apache 重量档 · 不镜像）
pnpm add @nexu-io/open-design
# 或 DSH plugin:
dsh plugin --profile web add @nexu-io/open-design
# 3. 验证 16 unittest PASS
python -m unittest tests/test_open_design_bridge.py -v
```

---

## L4: 触发词

```
open-design, nexu-io, BYOK, code-agent CLI, sandboxed preview, design skill
Apache 重量档, 91,574⭐, DSH 生态第一
```

---

## L5: 下游协同

| 下游 | 协同 |
|---|---|
| **stage 41 mneme-heat-engine** | mneme heat 衰减 → open-design memory 入库 |
| **stage 45 dsh-eval-bridge** | benchmark result → design viz |
| **stage 47 dsh-univer-office** | 借鉴档 Apache 共用 Apache NOTICE 模板 |
| **stage 49.2 memsearch-bridge** | memsearch retrieval → open-design preview |
| **stage 48 dsh-TUI** | TUI 显示 open-design preview |
| **paperclip-cost-control V2.1** | BYOK cost 估算（20+ CLIs token 计费）|

---

## L6: DON'T 护栏（5 条 · Apache 红线）

- ❌ **不要**镜像真源（1.85 MB · Yarn Berry · 866 issues blocker）
- ❌ **不要**让 `byok_only=False`（Apache NOTICE 红线）
- ❌ **不要**让 preview path 越权（`/etc / /home` 等 block）
- ❌ **不要**省 NOTICE 模板里的 `Modifications by dragon-engine`（Apache §4(a)）
- ❌ **不要**默认 ONNX 模型（cost 不可控）

---

## L7: 验证矩阵

| # | 必检项 | 期望 | 状态 |
|---|---|---|---|
| 1 | LocalFirstConfig 校验（offline + byok）| 2/2 | ✅ |
| 2 | CLIs count ≥ 20 + DSH present | 2/2 | ✅ |
| 3 | Sandbox 校验（5 路径）| 5/5 | ✅ |
| 4 | Skill template（default + custom）| 2/2 | ✅ |
| 5 | Apache NOTICE 模板（含 `Modifications by dragon-engine`）| 2/2 | ✅ |
| 6 | 16/16 unittest PASS | 拆 6 大类 | ✅ |

---

## L8: 参考链接

- **借鉴源**：https://github.com/nexu-io/open-design V0.20.3 · Apache-2.0
- **LICENSE verbatim**：https://raw.githubusercontent.com/nexu-io/open-design/main/LICENSE（11,296 B / Apache 2.0 全文）
- **Apache 合规模板**：[`memory/apache-attribution-statements.md §二`](../../../memory/apache-attribution-statements.md)（已就绪）
- **DSH 协议治理基线**：[`docs/dsh-ecosystem-license-policy.md`](../../../docs/dsh-ecosystem-license-policy.md)
- **Stage 49.4 主题文件**：[`memory/stage-494-open-design.md`](../../../memory/stage-494-open-design.md)
