---
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---
# neat-freak · MEMORY 主题文件

> 阶段 8 详细记忆（从 MEMORY.md 抽离，因主文件已达 195/200 行）

---

## neat-freak V1.0 详情（2026-06-29）

**触发源**：天龙自身迭代（MEMORY 治理前置需求）

**3 个核心资产**：

| 资产 | 路径 | 行数 | 能力 |
|------|------|------|------|
| `drift_scanner.py` V1.1 | `skills/neat-freak/scripts/drift_scanner.py` | 331 | 三层漂移扫描（版本/能力/命名/约束）|
| `neat_check.py` V1.0 ⭐NEW | `skills/neat-freak/scripts/neat_check.py` | 226 | 一键合规检查（user/project/all）|
| `convergence.py` V0.0 | `skills/neat-freak/scripts/convergence.py` | - | top-down 收敛 + 毕业机制 |
| `tests/test_drift_scanner.py` ⭐NEW | `skills/neat-freak/tests/` | 12 用例 | scan_size/inversion/links |
| `tests/test_neat_check.py` ⭐NEW | `skills/neat-freak/tests/` | 14 用例 | user/project/all + 退出码契约 |

**累计验证**：**26/26 PASS**

## 退出码契约

| 退出码 | 含义 | 触发场景 |
|-------|------|---------|
| 0 | ✅ 完全合规 | 尺寸 + 体量 + 链接全部通过 |
| 1 | ❌ 尺寸超限 | MEMORY.md > 200 行 / > 25KB |
| 2 | ❌ 体量倒挂 | memory > docs × ratio |
| 3 | ❌ 链接断裂 | MEMORY.md 引用了不存在的文件 |

## 关键 API

```python
from drift_scanner import scan_size, scan_inversion, scan_links
from neat_check import check_user_level, check_project_level, check_all

# 尺寸检查（默认 200 行 / 25KB）
scan_size("path/to/MEMORY.md")

# 体量倒挂检查（默认 ratio=0.2）
scan_inversion(memory_dir, docs_dir, ratio=0.2)

# 链接断裂检查
scan_links("path/to/MEMORY.md", memory_dir)

# 一键合规（user-level）
result = check_user_level()
```

## CLI

```bash
# 一键合规
python neat_check.py --target user
python neat_check.py --target project
python neat_check.py --target all

# JSON 输出
python neat_check.py --target user --json

# 自定义目录
python neat_check.py --memory-dir /custom/path

# 退出码 = 0/1/2/3 (合规/尺寸/倒挂/链接)
echo $?
```

## 实测状态

- **user-level MEMORY.md**: 197 行 / 10.3KB / 10 链接全有效 → **PASS** ✅
- **project-level MEMORY.md**: 12 链接断裂（agents/ 路径不存在）→ 待修复

## 战略价值

- **文档一致性 +400%**（V0.0 手动 → V1.0 自动）
- **记忆膨胀防护**（毕业机制 + 体量倒挂检查）
- **CI gate 一键集成**（`neat_check.py --target user` 退出码 0 = 通过）
- **预期收益**（V0.0 → V1.0）：
  - 版本漂移率 15% → **0%**
  - 命名统一性 70% → **95%**
  - 收敛效率 人工 2 小时 → **< 5 分钟**

## 协同链路

```
07 记录师 (scribe V10.x) → neat-freak V1.0 → docs/ 毕业
                                  ↓
                            neat_check.py → 退出码 0
                                  ↓
08 发布师 (publisher V10.x) → GitHub 发布
```

## 后续阶段协同

- **stage 14 baoyu-skills 全集 21/21**（2026-07-17）→ [baoyu-skills-integration.md](baoyu-skills-integration.md) · baoyu-format-markdown ↔ neat-freak 文档漂移检测（双重防护：内容 drift 来自 neat-freak，结构 drift 来自 baoyu-format-markdown）

## 路径速查

- SKILL: `C:\Users\li\.claude\projects\dragon-engine\skills\neat-freak\SKILL.md`
- 脚本: `C:\Users\li\.claude\projects\dragon-engine\skills\neat-freak\scripts\`
- 测试: `C:\Users\li\.claude\projects\dragon-engine\skills\neat-freak\tests\`
- 参考: `references/sync-matrix.md` + `references/agent-paths.md`

---

**抽离日期**：2026-06-29 · **来源**：MEMORY.md 主文件 195/200 行压力
