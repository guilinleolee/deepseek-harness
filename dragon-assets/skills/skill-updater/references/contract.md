# references/contract.md — frontmatter 字段契约（天龙 SKILL.md 子集）

本文件描述 `parse_skill.py` 在解析天龙 SKILL.md 时**期望看到**的 frontmatter 字段。如果你的 SKILL.md 写法与本文件不符，解析可能退化为 `None`。

---

## 必填字段（影响报告完整性）

| 字段 | 类型 | 说明 | 缺失时报告行为 |
|------|------|------|---------------|
| `name` | string | skill 主键，kebab-case | 用目录名 fallback |
| `version` | string | 语义化版本号（推荐 semver） | 列显示 `-` |
| `last_updated` | YYYY-MM-DD | 本地最后维护日期 | 跳过"长期未维护"判定 |
| `source` | string | 上游 GitHub URL 或本地路径 | 标 🟣 本地定制 |

## 推荐字段（提升报告质量）

| 字段 | 类型 | 说明 |
|------|------|------|
| `license` | SPDX ID | 用于 License 红线比对（必须与上游 SPDX 一致） |
| `upstream` | list | 描述性，借调的子模块清单（不参与比对） |

---

## 已知的"非标"写法（解析器容错）

天龙 22 阶段历史中，frontmatter 有以下 4 种变体已被解析器接受：

### 1. 单引号 / 双引号包值
```yaml
description: "这是一个 skill"
license: 'MIT'
```
✅ 双引号 / 单引号都会被去掉。

### 2. 多行 description 用 `>` 折行
```yaml
description: >
  这是多行
  描述。
```
⚠️ **V1.0 不展开 `>` / `|` 块**。整段会被读到 `description` 字段（包含换行符）。不影响主流程。

### 3. 列表两种写法
```yaml
# 内联
depends: ["a", "b"]

# 块
depends:
  - a
  - b
```
✅ 都支持。

### 4. source 字段带 ⭐ + 描述
```yaml
source: https://github.com/foo/bar (3.2k ⭐ · 借调 baz)
```
✅ regex 会从开头匹配 `https://github.com/owner/repo`，忽略括号内描述。

---

## 不被解析的字段（V1.0）

- `triggers:` —— 触发词列表（仅给 agent 看的运行时配置）
- `references:` —— 相对路径列表
- 多级嵌套对象 —— V1.0 暂不展开

---

## License SPDX 命名约定

请使用 [SPDX License List](https://spdx.org/licenses/) 中的标准 ID：

| 期望 | 不要写 |
|------|--------|
| `MIT` | `MIT License` |
| `Apache-2.0` | `Apache License 2.0` |
| `AGPL-3.0` | `AGPL v3` |
| `GPL-3.0` | `GPL3` |

如果你的写法不在 SPDX 列表中，会触发 **license 变化 → 🟡/🔴**，即使语义上一致。这是**已知限制**，V1.1 引入别名表后修复。