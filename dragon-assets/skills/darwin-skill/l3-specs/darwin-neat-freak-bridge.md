# darwin-neat-freak-bridge.md · darwin × neat-freak V1.1 联动协议

> **天龙本地增强**（MIT 允许子包装，**不修改** upstream darwin-skill 任何字节）
> **目的**：darwin 在每个优化周期前，必须先跑 `neat-freak V1.1` Apache/MIT/AGPL 红线扫描，防止优化过程中触碰协议红线。

---

## 1. 协议概要

```
[darwin Phase 0.5: 红线 Gate]
    │
    ├─► $ python ~/.claude/skills/neat-freak/scripts/neat_check.py --target <skill-slug>
    │
    ├─► exit 0 (PASS) → 进 Phase 1 基线评估
    │
    ├─► exit 1 (尺寸超限) → 阻断 + 用户手动缩减 skill 文件
    │
    ├─► exit 2 (体量倒挂) → 阻断 + 重新组织子目录
    │
    └─► exit 3 (链接断裂) → 阻断 + 修复交叉引用
```

---

## 2. neat-freak 退出码契约

| Exit code | 含义 | darwin 动作 |
|---|---|---|
| 0 | PASS | 进 Phase 1 |
| 1 | 尺寸超限 | 阻断 + 报警 |
| 2 | 体量倒挂（子目录 > 父）| 阻断 + 报警 |
| 3 | 链接断裂 | 阻断 + 报警 |

---

## 3. Apache-2.0 红线（防止 darwin 误删）

darwin 优化 Apache-2.0 skill（如 a-stock-data-bridge）时，**绝不能**：

| ❌ 不能动 | ✅ 必须保留 |
|---|---|
| NOTICE 文件 | 完整 5 段结构 |
| LICENSE 文件 | 10-12 KB verbatim |
| ## Attribution 段 | SKILL.md frontmatter + body |
| runtime.conf | license=Apache-2.0 字段 |

`neat-freak V1.1` 7 层一致性检查会捕获这些。

---

## 4. AGPL-3.0 红线（防止 darwin 把方法论当课程）

darwin 优化 AGPL skill（如 guizang / cangjie）时，**绝不能**：

| ❌ 不能动 | ✅ 必须保留 |
|---|---|
| LICENSE AGPL-3.0 verbatim | 34.5 KB / 659 行 |
| COMMERCIAL_LICENSING.md | 三档商用合作 |
| README.md 末尾 AGPL 署名段 | 4 项强制条款 |

---

## 5. MIT 红线（防止 darwin 删版权声明）

darwin 优化 MIT skill（如 nuwa / darwin）时，**绝不能**：

| ❌ 不能动 | ✅ 必须保留 |
|---|---|
| LICENSE MIT verbatim | 含 "Copyright (c) ..." |
| 5 模板致谢段 | 小红书 / 公众号 / H5 / 视频号 / 微博 |
| mit-attribution-statements.md §十一 | 5 平台 × 2 skill = 10 致谢段 |

---

## 6. 累计 PASS 校验

- neat-freak V1.1 已有 763 PASS（基线）
- darwin Phase 0.5 gate 不计入 darwin 自身的 PASS，但阻断后必须更新 neat-freak 累计 PASS
- 详见 `~/.claude/skills/neat-freak/scripts/neat-freak-v11-conformance.py`

---

## 7. 实现伪代码

```python
import subprocess
import sys

def neat_freak_gate(skill_slug: str) -> int:
    """Phase 0.5 红线 gate"""
    cmd = [
        sys.executable,
        "~/.claude/skills/neat-freak/scripts/neat_check.py",
        "--target", skill_slug,
    ]
    result = subprocess.run(cmd, capture_output=True, encoding="utf-8")
    return result.returncode

# darwin Phase 1 入口
gate_exit = neat_freak_gate("a-stock-data-bridge")
if gate_exit != 0:
    print(f"❌ neat-freak 红线未通过 (exit {gate_exit})，darwin 优化阻断")
    sys.exit(gate_exit)
print(f"✅ neat-freak 红线通过，进 Phase 1 基线评估")
```
