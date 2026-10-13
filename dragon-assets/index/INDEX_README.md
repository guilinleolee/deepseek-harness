# index/ · 天龙引擎五资产索引 · 自动生成

> **schema**: `dragon-index/1.0`  ·  生成时间：2026-08-24T03:34:48Z

> **用法**：每次大模型启动时只读 `CLAUDE.md`（hot 层）；命中触发词后查对应 `*.jsonl`（warm 层）；按 `id` 再读 `cold` 资产原文。


## 📊 全量统计

| kind | files | total_kb | active | deprecated | license breakdown |
|---|---|---|---|---|---|
| skill | 784 | 7159.8 | 783 | 0 | unknown:691 · MIT:67 · Apache-2.0:18 · AGPL-3.0:3 |
| agent | 187 | 2489.3 | 187 | 0 | unknown:178 · MIT:9 |
| hook | 90 | 792.1 | 90 | 0 | unknown:90 |
| command | 156 | 510.4 | 156 | 0 | unknown:152 · GPL-3.0:2 · MIT:2 |
| plugin | 7 | 11.0 | 7 | 0 | unknown:5 · MIT:2 |

## 📁 文件清单

| 文件 | 行数 | 用途 |
|---|---|---|
| `SKILLS.jsonl` | 784 | skill 一级目录（含 library/ 套件剔除） |
| `AGENTS.jsonl` | 187 | agent 角色定义 |
| `HOOKS.jsonl` | 90 | 钩子脚本（sh/js/py/json） |
| `COMMANDS.jsonl` | 156 | 命令文件（含中文乱码警告） |
| `PLUGINS.jsonl` | 7 | plugin 插件 |
| `INDEX_MASTER.json` | - | 总入口 + 元数据 + schema 版本 |
| `INDEX_README.md` | - | 本文件 |

## 🔥 Hot / Warm / Cold 三层模型

- **Hot**（每次必读 · ≤ 6 KB）→ `CLAUDE.md` §3 触发词路由表
- **Warm**（按需 lazy · 命中后整类加载）→ 5 个 `*.jsonl`
- **Cold**（按 ID 精确加载）→ 各资产原文件 SKILL.md / *.md

## 💡 检索样例

```bash
# 按 ID 查 skill
grep '"id": "nuwa-skill"' index/SKILLS.jsonl

# 按触发词查 agents
grep '"博主' index/AGENTS.jsonl | head -5

# 找所有 MIT license 的 skill
grep '"license": "MIT"' index/SKILLS.jsonl | wc -l
```

## 🔁 同步

```bash
# 全量重建
python scripts/build-index.py

# 仅统计
python scripts/build-index.py --stats
```
