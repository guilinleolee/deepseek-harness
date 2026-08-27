---
license: UNKNOWN
triggers: ["lark base", "Lark Base Skill"]
---
# Lark Base Skill

> 飞书/Lark 多维表操作能力 - CRUD/批量操作/高级筛选

## 核心能力

| 能力 | 功能 | 使用场景 |
|------|------|---------|
| **库表管理** | 创建/删除/更新库表 | 数据建模 |
| **记录操作** | CRUD记录 | 数据管理 |
| **批量操作** | 批量导入/导出/更新 | 数据迁移 |
| **高级筛选** | 多条件筛选、视图 | 数据分析 |

## 安装要求

```bash
npm install -g openclaw
node --version  # >= 22
```

## 配置

### 飞书开放平台权限

- `bitable:bitable` - 多维表操作
- `bitable:bitable:readonly` - 多维表只读
- `bitable:record` - 记录操作

### 环境变量

```bash
export LARK_APP_ID="your_app_id"
export LARK_APP_SECRET="your_app_secret"
```

## 命令参考

### 库表管理

```bash
# 创建多维表
/lark-base create-app --name "项目管理表" --folder-id "fld_xxx"

# 创建数据表
/lark-base create-table --app-token "app_xxx" --name "任务表"

# 创建字段
/lark-base create-field --table-id "tbl_xxx" --name "负责人" --type "user"
```

### 记录操作

```bash
# 创建记录
/lark-base create-record --table-id "tbl_xxx" --fields '{"任务":"写文档","状态":"进行中"}'

# 读取记录
/lark-base read-records --table-id "tbl_xxx" --limit 100

# 更新记录
/lark-base update-record --record-id "rec_xxx" --fields '{"状态":"已完成"}'

# 删除记录
/lark-base delete-record --record-id "rec_xxx"
```

### 批量操作

```bash
# 批量导入
/lark-base import --table-id "tbl_xxx" --file "./data.csv"

# 批量更新
/lark-base batch-update --table-id "tbl_xxx" --file "./updates.json"

# 导出数据
/lark-base export --table-id "tbl_xxx" --format csv --output "./exports/"
```

### 高级筛选

```bash
# 条件筛选
/lark-base filter --table-id "tbl_xxx" --filter '{"条件":[{"field":"状态","op":"=","value":"进行中"}]}'

# 排序
/lark-base sort --table-id "tbl_xxx" --sort '{"field":"创建时间","order":"desc"}'

# 分组统计
/lark-base group --table-id "tbl_xxx" --group-by "负责人" --aggregate "count"
```

## Python API

```python
from lark_base import LarkBase

# 初始化
base = LarkBase(app_id, app_secret)

# 创建多维表
app_token = base.create_app(name="项目管理表", folder_id="fld_xxx")

# 创建数据表
table_id = base.create_table(app_token=app_token, name="任务表", fields=[
    {"name": "任务名称", "type": "text"},
    {"name": "负责人", "type": "user"},
    {"name": "状态", "type": "single_select", "options": ["进行中", "已完成", "已取消"]},
    {"name": "截止日期", "type": "date"}
])

# 创建记录
record_id = base.create_record(table_id=table_id, fields={
    "任务名称": "完成API文档",
    "负责人": "ou_xxx",
    "状态": "进行中",
    "截止日期": "2026-03-20"
})

# 查询记录
records = base.query(
    table_id=table_id,
    filter='{"条件":[{"field":"状态","op":"=","value":"进行中"}]}',
    sort='{"field":"截止日期","order":"asc"}'
)

# 批量导入
base.import_from_csv(table_id=table_id, csv_path="./tasks.csv")

# 导出数据
base.export_to_csv(table_id=table_id, output_path="./exports/tasks.csv")
```

## 天龙岗位映射

| 岗位 | 使用场景 | 匹配度 |
|------|---------|--------|
| **01 调研师** | 数据采集、竞品分析、用户调研 | ⭐⭐⭐⭐⭐ |
| **50-01 产品策划** | 需求管理、迭代追踪 | ⭐⭐⭐⭐⭐ |
| **07 记录师** | 知识库管理、数据归档 | ⭐⭐⭐⭐ |
| **17-01 数据分析师** | 数据分析、报表生成 | ⭐⭐⭐⭐⭐ |

## 使用示例

### 示例1：需求管理

```python
# 创建需求管理表
base.create_requirements_table(app_token="app_xxx")

# 添加需求
base.add_requirement(table_id=table_id, requirement={
    "标题": "用户登录功能",
    "优先级": "P0",
    "负责人": "张三",
    "状态": "开发中",
    "预计完成": "2026-03-20"
})

# 查询进行中的需求
requirements = base.query(table_id=table_id, filter={
    "状态": "开发中"
})
```

### 示例2：调研数据收集

```python
# 创建调研数据表
base.create_research_table(app_token="app_xxx", name="用户调研")

# 批量导入调研数据
base.import_from_csv(table_id=table_id, csv_path="./survey_data.csv")

# 生成统计报表
stats = base.analyze(table_id=table_id, group_by="满意度", aggregate="count")
```

### 示例3：任务追踪

```python
# 同步任务状态
base.sync_tasks(
    table_id=table_id,
    tasks=[
        {"id": "T001", "status": "已完成"},
        {"id": "T002", "status": "进行中"}
    ]
)

# 获取过期任务
overdue_tasks = base.get_overdue_tasks(table_id=table_id)
```

## 字段类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `text` | 文本 | 任务名称 |
| `number` | 数字 | 预算 |
| `single_select` | 单选 | 状态 |
| `multi_select` | 多选 | 标签 |
| `date` | 日期 | 截止日期 |
| `user` | 人员 | 负责人 |
| `attachment` | 附件 | 文档 |
| `link` | 超链接 | 相关链接 |

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| 1.0.0 | 2026-03-14 | 初始版本，支持CRUD/批量操作/高级筛选 |