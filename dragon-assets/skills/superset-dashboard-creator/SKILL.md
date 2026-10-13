---
license: UNKNOWN
triggers: ["superset dashboard creator", "superset-dashboard-creator"]
---
# superset-dashboard-creator

## 元数据
- **版本**: 1.0.0
- **创建日期**: 2026-03-19
- **匹配岗位**: 17-01 数据分析师, 19-01 数据工程师, 60-01 投资总监, 64-01 量化研究员
- **依赖**: superset-auth-manager, superset-data-connector

## 概述
Apache Superset 仪表板创建器，支持 50+ 图表类型、自动图表选择、仪表板布局、嵌入配置。为天龙引擎提供一键式数据可视化能力。

## 支持的图表类型（50+）

### 基础图表
| 图表类型 | 用途 | 触发关键词 |
|---------|------|-----------|
| 折线图 Line | 趋势分析 | 趋势、时间序列、走势 |
| 柱状图 Bar | 分类对比 | 对比、排名、分布 |
| 饼图 Pie | 占比分析 | 占比、构成、比例 |
| 散点图 Scatter | 相关性分析 | 相关、分布、聚类 |
| 面积图 Area | 累积趋势 | 累积、趋势、总量 |

### 高级图表
| 图表类型 | 用途 | 触发关键词 |
|---------|------|-----------|
| 热力图 Heatmap | 密度分析 | 密度、分布、矩阵 |
| 树状图 Treemap | 层级占比 | 层级、占比、结构 |
| 桑基图 Sankey | 流向分析 | 流向、转化、迁移 |
| 漏斗图 Funnel | 转化分析 | 转化、漏斗、流失 |
| 仪表盘 Gauge | KPI展示 | KPI、指标、达成率 |

### 地理图表
| 图表类型 | 用途 | 触发关键词 |
|---------|------|-----------|
| 地图 Map | 地理分布 | 地图、区域、分布 |
| 热力地图 Heatmap | 地理密度 | 热力图、区域密度 |
| Deck.gl | 高级地理 | 轨迹、3D、地理分析 |

### 金融图表
| 图表类型 | 用途 | 触发关键词 |
|---------|------|-----------|
| K线图 Candlestick | 价格走势 | K线、股票、价格 |
| 瀑布图 Waterfall | 增减分析 | 增减、变化、贡献 |

## 核心能力

### 1. 自动图表选择
```python
from superset_dashboard_creator import ChartRecommender

# 根据数据和意图自动推荐图表
recommender = ChartRecommender()
recommendation = recommender.recommend(
    data={
        "columns": ["date", "region", "sales"],
        "types": ["DATE", "STRING", "FLOAT"],
        "row_count": 10000
    },
    intent="趋势分析"
)

# 返回推荐
{
    "chart_type": "line",
    "x_axis": "date",
    "y_axis": "sales",
    "groupby": "region",
    "confidence": 0.95
}
```

### 2. 仪表板创建
```python
from superset_dashboard_creator import DashboardCreator

# 创建仪表板
creator = DashboardCreator(auth)

dashboard = creator.create(
    title="销售分析仪表板",
    description="实时销售数据监控",
    charts=[
        {
            "type": "line",
            "title": "销售趋势",
            "dataset": 1,
            "x_axis": "date",
            "y_axis": "sales",
            "groupby": "region"
        },
        {
            "type": "pie",
            "title": "区域占比",
            "dataset": 1,
            "metric": "SUM(sales)",
            "groupby": "region"
        }
    ],
    layout="auto"  # 自动布局
)
```

### 3. 嵌入配置
```python
# 生成嵌入配置
embed_config = creator.get_embed_config(
    dashboard_id=dashboard.id,
    rls=[{"clause": "region = 'East'"}]  # 行级安全
)

# 返回
{
    "guest_token": "eyJ...",
    "embed_url": "https://superset.example.com/embed/dashboard/1",
    "iframe_html": "<iframe src='...' />"
}
```

## 命令接口

### CLI 命令
```bash
# 创建仪表板
/superset-dashboard create --title "销售分析" --dataset 1

# 添加图表
/superset-dashboard add-chart --dashboard 1 --type line --x date --y sales

# 自动推荐图表
/superset-dashboard recommend --dataset 1 --intent "趋势分析"

# 生成嵌入配置
/superset-dashboard embed --dashboard 1 --rls "region='East'"

# 导出仪表板
/superset-dashboard export --dashboard 1 --output dashboard.json

# 导入仪表板
/superset-dashboard import --file dashboard.json
```

### 自然语言触发
- "创建销售分析仪表板"
- "添加趋势图表"
- "推荐适合的图表类型"
- "生成嵌入配置"

## 使用示例

### 与天龙岗位集成

#### 17-01 数据分析师
```python
# 数据分析完成后自动创建仪表板
from superset_dashboard_creator import DashboardCreator

def create_analysis_dashboard(analysis_results):
    creator = DashboardCreator.from_env()

    # 自动创建仪表板
    dashboard = creator.create_from_analysis(
        title="用户行为分析",
        analysis=analysis_results,
        charts=[
            "user_growth_trend",      # 自动推荐为折线图
            "region_distribution",    # 自动推荐为饼图
            "behavior_heatmap"        # 自动推荐为热力图
        ]
    )

    # 返回嵌入链接
    return dashboard.get_embed_url()
```

#### 64-01 量化研究员
```python
# 创建策略监控仪表板
creator = DashboardCreator(auth)

strategy_dashboard = creator.create(
    title="多因子策略监控",
    charts=[
        {
            "type": "line",
            "title": "累计收益",
            "dataset": "backtest_results",
            "x_axis": "date",
            "y_axis": "cumulative_return"
        },
        {
            "type": "heatmap",
            "title": "因子IC矩阵",
            "dataset": "factor_ic",
            "x_axis": "factor",
            "y_axis": "date",
            "metric": "ic"
        },
        {
            "type": "gauge",
            "title": "策略夏普比率",
            "dataset": "strategy_metrics",
            "metric": "sharpe_ratio",
            "target": 2.0
        }
    ]
)
```

#### 60-01 投资总监
```python
# 创建投资组合仪表板
portfolio_dashboard = creator.create(
    title="投资组合监控",
    charts=[
        {
            "type": "pie",
            "title": "资产配置",
            "dataset": "portfolio_allocation",
            "metric": "weight",
            "groupby": "asset_class"
        },
        {
            "type": "treemap",
            "title": "持仓明细",
            "dataset": "holdings",
            "metric": "market_value",
            "groupby": ["sector", "ticker"]
        },
        {
            "type": "line",
            "title": "净值曲线",
            "dataset": "nav_history",
            "x_axis": "date",
            "y_axis": "nav"
        }
    ]
)
```

#### 19-01 数据工程师
```python
# 创建 ETL 监控仪表板
etl_dashboard = creator.create(
    title="ETL 监控看板",
    refresh_interval=60,  # 60秒刷新
    charts=[
        {
            "type": "gauge",
            "title": "今日 ETL 完成率",
            "dataset": "etl_status",
            "metric": "completion_rate",
            "target": 100
        },
        {
            "type": "bar",
            "title": "各任务耗时",
            "dataset": "etl_metrics",
            "x_axis": "task_name",
            "y_axis": "duration_seconds"
        },
        {
            "type": "line",
            "title": "数据量趋势",
            "dataset": "etl_volume",
            "x_axis": "date",
            "y_axis": "row_count"
        }
    ]
)
```

## 预置模板

### 1. 销售分析仪表板模板
```python
sales_template = {
    "title": "销售分析仪表板",
    "charts": [
        {"type": "line", "title": "销售趋势", "x": "date", "y": "sales"},
        {"type": "pie", "title": "区域占比", "groupby": "region"},
        {"type": "bar", "title": "产品排名", "groupby": "product"},
        {"type": "funnel", "title": "转化漏斗", "stages": ["访问", "注册", "购买"]}
    ]
}
```

### 2. 用户增长仪表板模板
```python
growth_template = {
    "title": "用户增长仪表板",
    "charts": [
        {"type": "line", "title": "用户增长趋势", "x": "date", "y": "users"},
        {"type": "heatmap", "title": "活跃度分布", "x": "hour", "y": "weekday"},
        {"type": "treemap", "title": "用户分层", "groupby": "segment"}
    ]
}
```

### 3. 投资仪表板模板
```python
investment_template = {
    "title": "投资组合仪表板",
    "charts": [
        {"type": "pie", "title": "资产配置", "groupby": "asset_class"},
        {"type": "line", "title": "净值曲线", "x": "date", "y": "nav"},
        {"type": "gauge", "title": "夏普比率", "metric": "sharpe"},
        {"type": "heatmap", "title": "相关性矩阵", "metric": "correlation"}
    ]
}
```

## API 端点映射

| Superset API | 本 Skill 方法 |
|--------------|---------------|
| POST /api/v1/dashboard/ | `create()` |
| GET /api/v1/dashboard/{id} | `get()` |
| PUT /api/v1/dashboard/{id} | `update()` |
| DELETE /api/v1/dashboard/{id} | `delete()` |
| POST /api/v1/chart/ | `create_chart()` |
| GET /api/v1/chart/data | `get_chart_data()` |
| POST /api/v1/dashboard/import/ | `import_dashboard()` |
| GET /api/v1/dashboard/export/{id} | `export_dashboard()` |

## 文件结构
```
skills/superset-dashboard-creator/
├── SKILL.md
├── scripts/
│   ├── dashboard_creator.py     # 核心创建类
│   ├── chart_recommender.py     # 图表推荐引擎
│   ├── templates/               # 预置模板
│   │   ├── sales.json
│   │   ├── growth.json
│   │   └── investment.json
│   └── cli.py                   # CLI 工具
└── docs/
    ├── chart-types.md
    └── templates-guide.md
```

## 版本历史
- **1.0.0** (2026-03-19): 初始版本，支持 50+ 图表、自动推荐、模板系统