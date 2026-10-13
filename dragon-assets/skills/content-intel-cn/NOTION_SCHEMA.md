# Notion 数据库结构（Content Intel CN）

用于内容运营闭环：选题 → 发布 → 复盘。
建议建立 3 个数据库，并通过 Relation 关联。

---

## 1) 选题池（Topic Backlog）

**数据库名建议：** `内容选题池`

字段：
- `标题` (Title)
- `平台` (Multi-select): `X`, `小红书`, `公众号`
- `主题关键词` (Rich text)
- `目标受众` (Select): `潜在客户`, `社群成员`, `同行`, `泛流量`
- `内容类型` (Select): `教程`, `观点`, `案例`, `清单`, `复盘`
- `优先级` (Select): `P0`, `P1`, `P2`
- `状态` (Select): `待写`, `草稿中`, `已排期`, `已发布`, `归档`
- `预估价值` (Number)
- `灵感来源` (URL)
- `创建时间` (Created time)
- `计划发布时间` (Date)
- `关联发布记录` (Relation -> 发布记录)

---

## 2) 发布记录（Publishing Log）

**数据库名建议：** `内容发布记录`

字段：
- `标题` (Title)
- `平台` (Select): `X`, `小红书`, `公众号`
- `发布时间` (Date)
- `正文` (Rich text)
- `链接` (URL)
- `标签` (Multi-select)
- `是否系列` (Checkbox)
- `系列名` (Rich text)
- `关联选题` (Relation -> 选题池)
- `关联复盘` (Relation -> 复盘库)

统计字段（可后补）：
- `曝光` (Number)
- `点赞` (Number)
- `评论` (Number)
- `收藏` (Number)
- `转发` (Number)
- `互动率` (Formula): `(点赞+评论+收藏+转发)/曝光`

---

## 3) 复盘库（Review Lab）

**数据库名建议：** `内容复盘`

字段：
- `标题` (Title) 例：`2026-W10 周复盘`
- `周期` (Select): `日`, `周`, `月`, `专题`
- `起止时间` (Date, end date)
- `平台范围` (Multi-select)
- `总发布数` (Rollup from 发布记录)
- `总互动` (Rollup/Number)
- `最佳内容` (Relation -> 发布记录)
- `失败样本` (Relation -> 发布记录)
- `有效模式` (Rich text)
- `无效模式` (Rich text)
- `下周动作` (Rich text)
- `负责人` (People)
- `创建时间` (Created time)

---

## 推荐视图

### 选题池
- `Kanban by 状态`
- `Calendar by 计划发布时间`
- `Table by 平台`

### 发布记录
- `本周发布`（filter: 发布时间在本周）
- `按平台分组`
- `Top互动`（sort: 互动率 desc）

### 复盘库
- `周复盘`
- `月复盘`

---

## 命名规范（建议）

- 周复盘：`YYYY-Www 内容复盘`
- 发布标题前缀：`[平台] 标题`
- 选题标题：`主题词 + 价值承诺`

例：
- `[X] AI 工作流里的 3 个降本坑`
- `地产设计协同：5 个跨部门推进模板`
