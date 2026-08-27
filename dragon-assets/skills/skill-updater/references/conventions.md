# 天龙资产登记规范（V1.1.1）

> **目的**：避免未来新加的 SKILL / agent / plugin 出现无 `source` / `repository` 字段，导致 skill-updater 无法比对上游版本。
>
> **核心原则**：**任何从外部（GitHub、镜像仓库、市场里下载）来的资产，必须登记上游来源**；**天龙自研的资产，登记天龙仓库自身位置**。

---

## 1. 三类资产的"上游来源"字段约定

### 1.1 SKILL.md（YAML frontmatter）

```yaml
---
name: my-skill
description: ...
version: 1.0.0
author: 天龙引擎集成
# ↓↓↓ 以下两个字段必须填 ↓↓↓
source: https://github.com/owner/repo (3.2k ⭐ · 借调 xxx 范式)   # 必填
license: MIT                                                      # 必填（与上游 SPDX 一致）
---
```

**字段语义**：

| 字段 | 必填 | 含义 | 示例 |
|------|------|------|------|
| `source` | ✅ | 上游 GitHub URL（含可选的 ⭐ + 描述）| `https://github.com/op7418/guizang-social-card-skill (5.1k ⭐ · 借调 28 版式)` |
| `license` | ✅ | SPDX 标准的 license ID（与上游一致）| `MIT` / `Apache-2.0` / `AGPL-3.0` |

**允许的 source 写法**：

| 形态 | 例子 | 是否推荐 |
|------|------|---------|
| `https://github.com/owner/repo` | 最简洁 | ✅ 推荐 |
| `https://github.com/owner/repo (3.2k ⭐ · 借调 X 范式)` | 带 ⭐ + 借调说明 | ✅✅ **天龙首选** |
| `https://github.com/owner/repo.git` | 带 `.git` 后缀 | ✅ 接受 |
| `./local-repo` 或本地路径 | 本地引用 | ⚠️ 仅限真正本地的 |
| 描述性文字（无 URL）| `反向抽取自 SamurAIGPT/...` | ❌ **禁止** — skill-updater 无法解析 |

### 1.2 agents/*.md（YAML frontmatter）

```yaml
---
name: 00analyst
description: ...
# ↓↓↓ 必须填（如果 agent 借调了上游范式）↓↓↓
repository: https://github.com/xxx/yyy-patterns (借调 X 范式)
license: MIT
---
```

> 注：天龙自研的 agent **不需要** repository 字段（因为是内部创作）。**只有从外部借调范式的 agent** 才需要。

### 1.3 .claude-plugin/marketplace.json（JSON 字段）

```json
{
  "name": "my-marketplace",
  "version": "1.0.0",
  "owner": {
    "name": "My Org",
    "email": "contact@example.com"
  },
  "metadata": {
    "repository": "https://github.com/my-org/my-marketplace",  ← 新增
    "description": "..."
  },
  "plugins": [...]
}
```

**天龙 V1.1.1 新约定**：在 `metadata.repository` 字段写明 marketplace 的 GitHub URL。skill-updater 会优先读这个字段（比从 owner.name 推断准 100%）。

---

## 2. 检查清单（每个新资产开工前）

- [ ] 我加的资产是 SKILL.md / agents/*.md / marketplace.json 中的哪种？
- [ ] 这个资产**有上游来源**吗？
  - 有 → `source: https://github.com/owner/repo (X ⭐ · 借调 X)` 必填
  - 没有（纯天龙自研）→ SKILL.md `source` 留空也行，但**要在 description 里写 "天龙自研"`*
- [ ] `license` 字段填了 SPDX 标准 ID 吗？（不是 "MIT License"，是 "MIT"）
- [ ] license 跟上游一致吗？（如果上游 AGPL，本地也得 AGPL-3.0）

---

## 3. 如何检查"我有没有 source 字段"？

跑 skill-updater（V1.1.1+ 默认带）：

```bash
bash scripts/scan.sh --no-network
```

报告末尾会有一段：

```
=== 缺 source 字段的资产清单（建议补）===
按目录分组,共 6956 个:

projects/dragon-engine/skills/                  (5 个)
  ├─ async-task-pattern                         ← SKILL.md
  ├─ guizang-social-card-skill                  ← SKILL.md (天龙自研,可写"天龙自研")
  └─ skill-updater                              ← SKILL.md (天龙自研)

projects/dragon-engine/.agents/skills/         (10+ 个)
  ├─ ...
```

**天龙自研的不需要 source**（只要在 description 写"天龙自研"即可）。**从外部借调/镜像的必须补**。

---

## 4. 一键补 source 字段

### 方式 A：交互式 helper（推荐）

```bash
python scripts/make_source.py
```

扫描所有缺 source 的资产，按目录逐个询问：
1. 这个资产是"天龙自研"吗？y/n
2. 如果是外部借调：填 GitHub URL
3. helper 自动写入 SKILL.md frontmatter（**必须 --yes 才真改**）

### 方式 B：手动编辑

打开对应的 SKILL.md，找到 frontmatter：

```yaml
---
name: my-skill
description: ...
version: 1.0.0
+ source: https://github.com/owner/repo (X ⭐ · 借调 X)
+ license: MIT
---
```

### 方式 C：批量模板（适合批量迁移）

如果某目录下多个 skill 都借调同一仓库：

```bash
# 给 dragon-engine/skills/guizang-* 全部加 source
for f in dragon-engine/skills/guizang-*/SKILL.md; do
  # 在 frontmatter 插入 source 行
  sed -i '/^name:/a source: https://github.com/op7418/guizang-social-card-skill (5.1k ⭐ · 借调 28 版式)' "$f"
done
```

---

## 5. 不遵守规范的代价

| 不填 source 的代价 | 后果 |
|--------------------|------|
| skill-updater 扫不到上游 | 🟣 本地定制（不算 bug，但失去上游状态追踪能力） |
| 上游 license 变化 | 🔴 合规告警永远发不出来（因为没有"参考对象"） |
| 升级天龙时 | ❓ 无法判断"本地是否落后上游"|
| 新成员接手 | ❌ 看不懂这个 skill 从哪里来、是不是天龙原创 |

**填 source 是一次性成本，长期受益**。

---

## 6. 模板（直接复制）

### SKILL.md 模板

```markdown
---
name: <kebab-case>
description: >
  <一句话描述> · <可选:含借调说明>
version: 1.0.0
author: 天龙引擎集成
source: https://github.com/<owner>/<repo> (<Xk ⭐ · 借调 <具体内容>)
license: <SPDX-ID>
last_updated: YYYY-MM-DD
depends: []
upstream: []
downstream: []
references:
  - references/<file>.md
---

# <skill 名> · V1.0

## L0: 一句话描述
...

## L1: 使用场景
...

## L2: 详细文档
...
```

### agents/*.md 模板

```markdown
---
name: <agent 名>
description: <一句话描述>
tools: <工具列表>
model: <sonnet|opus|haiku>
# ↓ 天龙自研:留空即可;借调外部范式:↓
# repository: https://github.com/<owner>/<repo> (<Xk ⭐ · 借调 <范式>)
# license: <SPDX-ID>
---

# Role: <中文角色名>

...
```

### marketplace.json 模板

```json
{
  "name": "<kebab-slug>",
  "version": "0.1.0",
  "owner": {
    "name": "<Owner Name>",
    "email": "<contact@example.com>"
  },
  "metadata": {
    "repository": "https://github.com/<owner>/<repo>",   ← V1.1.1 新增
    "description": "<一句话描述>"
  },
  "plugins": []
}
```

---

## 7. 长期演化路线

| 版本 | 时间 | 关键变更 |
|------|------|---------|
| V1.1.1 | 2026-07-21 | 本规范文档 + make_source.py + 报告"缺 source 清单" |
| V1.2   | 待定 | templates/SKILL.md.template 等模板体系，新资产必须从模板派生 |
| V1.3   | 待定 | CI / git hook 接入：commit 含无 source 资产时警告 |
| V2.0   | 待定 | metadata.json 副文件方案（替代 frontmatter） |

---

## 8. FAQ

### Q: 如果一个 skill **部分**借调了上游怎么办？
A: 仍然填 source，description 里写"借调 XXX 的 YYY 部分"。

### Q: 如果上游仓库被删了，source 字段还要保留吗？
A: 保留。skill-updater 会把这种标记为 🔴 "上游 404"，**正是你想看到的告警**。

### Q: 我不想每次新加 skill 都想 source URL 怎么办？
A: 用 `make_source.py` helper —— 它会问"是自研还是外部借调？"，**自研就一键跳过**。

### Q: 旧的 6000+ 资产怎么批量补？
A: **不补**！它们是历史资产，scan.sh 会自动标 🟣 本地。**只对未来新加的资产强制**。

### Q: agents/*.md 的 source/repository 字段天龙官方支持吗？
A: V1.1.1 起天龙规范要求。skill-updater V1.1.1 会读这个字段做上游比对。

---

**Last Updated**: 2026-07-21 (V1.1.1)
**Owner**: skill-updater
**变更追踪**: 任何新加资产后，跑 `bash scripts/scan.sh --no-network | grep -A100 "缺 source"` 自检