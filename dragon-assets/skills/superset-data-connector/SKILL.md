---
license: UNKNOWN
triggers: ["superset data connector", "superset-data-connector"]
---
# superset-data-connector

## 元数据
- **版本**: 1.0.0
- **创建日期**: 2026-03-19
- **匹配岗位**: 19-01 数据工程师, 17-01 数据分析师, 64-01 量化研究员
- **依赖**: sqlalchemy, psycopg2, pymysql, clickhouse-driver

## 概述
Apache Superset 数据连接器，支持 30+ 数据库连接管理、Schema 发现、数据集创建、SQL 查询执行。为天龙引擎提供统一的数据访问层。

## 支持的数据源（30+）

### 云数据仓库
| 数据库 | 连接器 | 用途 |
|--------|--------|------|
| BigQuery | sqlalchemy-bigquery | Google 云数仓 |
| Snowflake | snowflake-sqlalchemy | 企业数仓 |
| Databricks | databricks-sql-connector | 湖仓一体 |
| Amazon Redshift | sqlalchemy-redshift | AWS 数仓 |

### 开源 OLAP
| 数据库 | 连接器 | 用途 |
|--------|--------|------|
| ClickHouse | clickhouse-sqlalchemy | 高性能 OLAP |
| Apache Druid | pydruid | 实时分析 |
| Apache Doris | pydoris | MPP 数仓 |
| DuckDB | duckdb-engine | 本地分析 |

### 关系数据库
| 数据库 | 连接器 | 用途 |
|--------|--------|------|
| PostgreSQL | psycopg2 | 主流关系库 |
| MySQL | pymysql | Web 应用首选 |
| SQLite | sqlite3 | 本地数据库 |
| SQL Server | pymssql | 企业应用 |

### 大数据引擎
| 数据库 | 连接器 | 用途 |
|--------|--------|------|
| Apache Hive | pyhive | Hadoop 查询 |
| Spark SQL | pyspark | 大数据处理 |
| Presto/Trino | trino | 联邦查询 |

## 核心能力

### 1. 数据库连接管理
```python
from superset_data_connector import DatabaseManager

# 连接 PostgreSQL
db_manager = DatabaseManager(auth)
db = db_manager.create_database(
    database_name="production_db",
    sqlalchemy_uri="postgresql://user:pass@host:5432/db",
    expose_in_sqllab=True
)
```

### 2. Schema 发现
```python
# 获取所有表
tables = db_manager.get_tables(database_id=1)

# 获取表结构
columns = db_manager.get_table_columns(
    database_id=1,
    table_name="users"
)

# 获取样本数据
sample = db_manager.get_table_sample(
    database_id=1,
    table_name="users",
    limit=100
)
```

### 3. 数据集创建
```python
# 创建数据集
dataset = db_manager.create_dataset(
    database_id=1,
    table_name="sales",
    schema="public",
    columns=[
        {"column_name": "date", "type": "DATE"},
        {"column_name": "amount", "type": "FLOAT"},
        {"column_name": "region", "type": "STRING"}
    ]
)
```

### 4. SQL 查询执行
```python
# 执行 SQL
result = db_manager.execute_sql(
    database_id=1,
    sql="SELECT region, SUM(amount) FROM sales GROUP BY region"
)
```

## 命令接口

### CLI 命令
```bash
# 添加数据库连接
/superset-db add --name "production" --uri "postgresql://..."

# 列出所有数据库
/superset-db list

# 查看数据库表
/superset-db tables --database production

# 查看表结构
/superset-db schema --database production --table sales

# 执行 SQL
/superset-db query --database production --sql "SELECT * FROM sales LIMIT 10"

# 创建数据集
/superset-db create-dataset --database production --table sales
```

### 自然语言触发
- "连接 PostgreSQL 数据库"
- "查看 production 数据库的表"
- "创建 sales 数据集"
- "执行 SQL 查询"

## 使用示例

### 与天龙岗位集成

#### 19-01 数据工程师
```python
# ETL 完成后自动创建数据集
from superset_data_connector import DatabaseManager

def after_etl_complete():
    db_manager = DatabaseManager.from_env()

    # 创建数据集
    dataset = db_manager.create_dataset(
        database_id=1,
        table_name=f"etl_output_{date.today()}",
        schema="analytics"
    )

    # 创建监控仪表板
    dashboard_id = create_monitoring_dashboard(dataset.id)

    return dashboard_id
```

#### 64-01 量化研究员
```python
# 连接量化数据库
db_manager = DatabaseManager()

# 创建因子数据集
factor_dataset = db_manager.create_dataset(
    database_name="quant_db",
    table_name="factor_returns",
    sql_filter="WHERE date >= '2024-01-01'"
)

# 创建回测结果数据集
backtest_dataset = db_manager.create_dataset(
    database_name="quant_db",
    table_name="backtest_results"
)
```

#### 17-01 数据分析师
```python
# 连接业务数据库
db = db_manager.connect(
    name="business_db",
    uri="postgresql://user:pass@db.company.com:5432/business"
)

# 发现数据结构
tables = db.discover_tables()
for table in tables:
    print(f"{table.name}: {table.row_count} rows")

# 创建分析数据集
analysis_dataset = db.create_dataset(
    table_name="user_behavior",
    columns=["user_id", "action", "timestamp", "page"]
)
```

## API 端点映射

| Superset API | 本 Skill 方法 |
|--------------|---------------|
| GET /api/v1/database/ | `list_databases()` |
| POST /api/v1/database/ | `create_database()` |
| GET /api/v1/database/{id}/tables/ | `get_tables()` |
| GET /api/v1/database/{id}/table/{table}/column/ | `get_table_columns()` |
| POST /api/v1/dataset/ | `create_dataset()` |
| POST /api/v1/database/{id}/query/ | `execute_sql()` |

## 配置

### 数据库连接模板
```yaml
# ~/.superset/databases.yaml
databases:
  production:
    driver: postgresql
    host: db.company.com
    port: 5432
    database: production
    username_env: DB_USER
    password_env: DB_PASSWORD

  analytics:
    driver: clickhouse
    host: clickhouse.company.com
    port: 9000
    database: analytics

  quant:
    driver: mysql
    host: quant-db.company.com
    port: 3306
    database: quant_research
```

## 文件结构
```
skills/superset-data-connector/
├── SKILL.md
├── scripts/
│   ├── database_manager.py    # 核心管理类
│   ├── connectors/            # 各数据库连接器
│   │   ├── postgresql.py
│   │   ├── mysql.py
│   │   ├── clickhouse.py
│   │   └── bigquery.py
│   ├── schema_discovery.py    # Schema 发现
│   └── cli.py                 # CLI 工具
└── docs/
    ├── supported-databases.md
    └── connection-strings.md
```

## 依赖安装
```bash
# 核心依赖
pip install sqlalchemy psycopg2-binary pymysql

# 可选依赖（按需安装）
pip install clickhouse-driver sqlalchemy-bigquery snowflake-sqlalchemy
pip install pyhive trino databricks-sql-connector
```

## 安全考虑

1. **连接字符串加密**: 密码存储使用 AES-256 加密
2. **环境变量注入**: 敏感信息从环境变量读取
3. **SQL 注入防护**: 参数化查询，禁止字符串拼接
4. **行级安全**: 支持通过 RLS 规则限制数据访问

## 版本历史
- **1.0.0** (2026-03-19): 初始版本，支持 30+ 数据库连接、Schema 发现、数据集创建