---
license: UNKNOWN
triggers: ["minimax xlsx", "MiniMax Excel/XLSX Skill"]
---
# MiniMax Excel/XLSX Skill

## Overview

Excel/spreadsheet file manipulation with formatting, formulas, charts, and data operations.

## Invocation

```
/minimax-xlsx create "创建数据表格"
/minimax-xlsx format "格式化工作表"
[@07记录师] 使用minimax-xlsx处理数据
```

## Core Capabilities

### Data Manipulation

```python
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

# Create workbook
wb = Workbook()
ws = wb.active
ws.title = "Data"

# Write data
ws['A1'] = "Name"
ws['B1'] = "Value"
ws['A2'] = "Item 1"
ws['B2'] = 100

# Formulas
ws['C2'] = "=B2*1.1"  # 10% increase

# Save
wb.save('output.xlsx')
```

### Formatting

```python
# Font styling
ws['A1'].font = Font(
    name='Arial',
    size=14,
    bold=True,
    color='FFFFFF'
)

# Cell fill
ws['A1'].fill = PatternFill(
    start_color='1a365d',
    end_color='1a365d',
    fill_type='solid'
)

# Alignment
ws['A1'].alignment = Alignment(
    horizontal='center',
    vertical='center'
)

# Column width
ws.column_dimensions['A'].width = 20
```

### Charts

```python
from openpyxl.chart import BarChart, Reference

# Create chart
chart = BarChart()
chart.type = "col"
chart.title = "Sales by Region"

# Data reference
data = Reference(ws, min_col=2, min_row=1, max_col=4, max_row=5)
cats = Reference(ws, min_col=1, min_row=2, max_row=5)

chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)

# Add to sheet
ws.add_chart(chart, "F2")
```

## Data Operations

| Operation | Command |
|-----------|---------|
| Read CSV | `pd.read_csv('data.csv')` |
| Write Excel | `df.to_excel('output.xlsx')` |
| Merge cells | `ws.merge_cells('A1:D1')` |
| Sort data | `df.sort_values('column')` |
| Filter | `df[df['column'] > value]` |
| Pivot table | `pd.pivot_table(df, values='x', index='y')` |

## Integration with 天龙引擎

**Upgrades:**
- 17-01数据分析师 V1.3 → V1.4: Excel manipulation

**Synergies:**
- xlsx: Base Excel capabilities
- database-migrations: Data pipeline
- ecommerce-monitor: Data collection
