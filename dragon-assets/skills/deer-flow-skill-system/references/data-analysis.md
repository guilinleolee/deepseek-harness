# DeerFlow Data Analysis Skill

## Overview

数据分析技能 - 使用DuckDB进行SQL分析。

## Core Capabilities

- 检验Excel/CSV文件结构
- 执行任意SQL查询
- 生成统计摘要
- 支持多Sheet Excel
- 导出CSV/JSON/Markdown
- 自动缓存机制

## Workflow

### Step 1: 检验文件结构

```bash
python scripts/analyze.py \
  --files /path/to/data.xlsx \
  --action inspect
```

返回：
- Sheet名称（Excel）或文件名（CSV）
- 列名、数据类型、非空计数
- 行数
- 示例数据（前5行）

### Step 2: 执行SQL查询

```bash
python scripts/analyze.py \
  --files /path/to/data.xlsx \
  --action query \
  --sql "SELECT category, COUNT(*) as cnt FROM Sheet1 GROUP BY category"
```

### Step 3: 生成统计摘要

```bash
python scripts/analyze.py \
  --files /path/to/data.xlsx \
  --action summary \
  --table Sheet1
```

返回：count, mean, std, min, 25%, 50%, 75%, max, null_count

### Step 4: 导出结果

```bash
python scripts/analyze.py \
  --files /path/to/data.xlsx \
  --action query \
  --sql "SELECT * FROM Sheet1 WHERE amount > 1000" \
  --output-file /path/to/output.csv
```

## Table Naming Rules

- **Excel**: 每个sheet成为表，名称为sheet名
- **CSV**: 文件名去掉扩展名作为表名
- **多文件**: 所有表可在同一查询中关联
- **特殊字符**: 自动清理（空格→下划线）

## Analysis Patterns

### 基础探索
```sql
-- 行数
SELECT COUNT(*) FROM Sheet1

-- 去重值
SELECT DISTINCT category FROM Sheet1

-- 分布
SELECT category, COUNT(*) as cnt FROM Sheet1 GROUP BY category
```

### 聚合与分组
```sql
-- 按月收入
SELECT DATE_TRUNC('month', order_date) as month,
       SUM(revenue) as total_revenue
FROM Sales
GROUP BY month
```

### 跨文件关联
```sql
-- 关联销售和客户信息
SELECT s.order_id, c.customer_name, c.region
FROM sales s
JOIN customers c ON s.customer_id = c.id
```

## Caching

脚本自动缓存加载的数据：
- 首次加载后存储在持久化DuckDB数据库
- 缓存键为所有输入文件内容的SHA256哈希
- 相同文件的再次调用直接使用缓存

## Complete Example

```bash
# 1. 检验文件
python scripts/analyze.py --files sales.xlsx --action inspect

# 2. 按收入Top10产品
python scripts/analyze.py --files sales.xlsx --action query \
  --sql "SELECT product, SUM(revenue) as total FROM Sales GROUP BY product ORDER BY total DESC LIMIT 10"

# 3. 月度趋势
python scripts/analyze.py --files sales.xlsx --action query \
  --sql "SELECT DATE_TRUNC('month', order_date) as month, SUM(revenue) as revenue FROM Sales GROUP BY month" \
  --output-file monthly-trends.csv
```
