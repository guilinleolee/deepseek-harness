---
license: UNKNOWN
name: excel-advanced
version: 1.0.0
description: |
  Excel高级功能：数据透视表原生支持、条件格式、动态图表绑定、高级函数(INDEX/MATCH/INDIRECT等)、动态数组函数(XLOOKUP/FILTER等)。支持Excel原生格式，与天龙xlsx技能颜色编码标准深度集成。
author: 天龙引擎团队
created: 2026-05-09
category: office
triggers:
  - "用户提到「数据透视表 pivot table」时"
  - "用户提到「条件格式 conditional formatting」时"
  - "用户提到「高级Excel函数」时"
  - "用户提到「动态数组函数 dynamic array」时"
---

# Excel Advanced - Excel高级功能

## Overview

Excel高级功能是数据分析师的核心工具。本技能提供数据透视表、条件格式、高级函数、动态图表等完整能力，与天龙xlsx技能深度集成。

## 数据透视表

### 创建透视表

```bash
# 创建数据透视表
excel-advanced pivot create --data "数据源" --rows "行字段" --columns "列字段" --values "值字段"

# 示例
excel-advanced pivot create --data "销售数据.xlsx" --rows "地区" --columns "产品" --values "销售额" --agg sum
```

### 透视表功能

```bash
# 聚合方式
# - sum: 求和
# - count: 计数
# - average: 平均值
# - max: 最大值
# - min: 最小值
# - product: 乘积
# - countNums: 数字计数
# - stdDev: 标准差
# - variance: 方差

# 高级功能
excel-advanced pivot options --data "透视表" --showFilter --enableDrill --groupDate "季度"
```

### 切片器和时间线

```bash
# 添加切片器
excel-advanced slicer add --pivot "透视表" --field "筛选字段"

# 添加时间线
excel-advanced timeline add --pivot "透视表" --dateField "日期字段"
```

## 条件格式

### 基础格式规则

```bash
# 数值条件格式
excel-advanced format number --range "A1:A10" --rule "大于" --value 100 --format "红色"

# 色阶条件格式
excel-advanced format colorScale --range "A1:A10" --type "三色" --min "绿色" --mid "黄色" --max "红色"

# 数据条条件格式
excel-advanced format dataBars --range "A1:A10" --direction "右到左"
```

### 高级格式规则

```bash
# 图标集条件格式
excel-advanced format iconSet --range "A1:A10" --icons "方向箭头" --rules "0-60-80-100"

# 公式条件格式
excel-advanced format formula --range "A1:A10" --formula "=A1>B1" --format "浅红填充"

# 重复值格式
excel-advanced format duplicate --range "A1:A10" --highlight "唯一值"
```

### 条件格式规则管理

```bash
# 列出所有规则
excel-advanced format list --sheet "工作表"

# 删除规则
excel-advanced format delete --rule-id "规则ID"

# 优先级调整
excel-advanced format priority --rule-id "规则ID" --move "up/down"
```

## 高级函数

### 查找引用函数

```bash
# INDEX/MATCH组合
excel-advanced function write --name "INDEX_MATCH" --formula "=INDEX(B:B,MATCH(A1,C:C,0))"

# XLOOKUP（动态数组）
excel-advanced function write --name "XLOOKUP" --formula "=XLOOKUP(A1,C:C,B:B,0,-1)"

# VLOOKUP/HLOOKUP
excel-advanced function write --name "VLOOKUP" --formula "=VLOOKUP(A1,D:E,2,FALSE)"
```

### 逻辑函数

```bash
# IFS函数
excel-advanced function write --name "IFS" --formula "=IFS(A1>=90,"优秀",A1>=80,"良好",A1>=60,"及格",TRUE,"不及格")"

# SWITCH函数
excel-advanced function write --name "SWITCH" --formula "=SWITCH(A1,"A",1,"B",2,"C",3,0)"
```

### 文本函数

```bash
# TEXTJOIN
excel-advanced function write --name "TEXTJOIN" --formula "=TEXTJOIN(\",\",TRUE,A1:A10)"

# CONCAT/TEXTJOIN
excel-advanced function write --name "CONCAT" --formula "=CONCAT(A1,\": \",B1)"
```

### 日期时间函数

```bash
# NETWORKDAYS.INTL
excel-advanced function write --name "WORKDAYS" --formula "=NETWORKDAYS.INTL(A1,B1,1,假期)"

# EOMONTH
excel-advanced function write --name "MONTHEND" --formula "=EOMONTH(TODAY(),0)"
```

## 动态数组函数

### FILTER函数

```bash
# FILTER筛选
excel-advanced function write --name "FILTER" --formula "=FILTER(A:C,B:B>\">100\",\"无数据\")"

# 多条件FILTER
excel-advanced function write --name "FILTER_MULTI" --formula "=FILTER(A:C,(B:B>\">100\")*(C:C<\"2026-12-31\"),\"无数据\")"
```

### 其他动态数组

```bash
# SORT排序
excel-advanced function write --name "SORT" --formula "=SORT(A:C,2,-1)"

# UNIQUE去重
excel-advanced function write --name "UNIQUE" --formula "=UNIQUE(A:A)"

# SEQUENCE序列
excel-advanced function write --name "SEQUENCE" --formula "=SEQUENCE(10,1,1,1)"

# RANDARRAY随机
excel-advanced function write --name "RANDARRAY" --formula "=RANDARRAY(5,3)"
```

### 组合动态数组

```bash
# UNIQUE+FILTER+SORT
excel-advanced function write --name "DYNAMIC_REPORT" --formula "=SORT(UNIQUE(FILTER(A:A,B:B>\">100\")),1,-1)"
```

## 图表绑定

### 创建图表

```bash
# 创建图表
excel-advanced chart create --type "柱形图" --data "A1:D10" --title "销售报表"

# 图表类型
# - 柱形图/条形图
# - 折线图
# - 饼图/环形图
# - 散点图
# - 面积图
# - 组合图
```

### 动态图表

```bash
# 创建动态图表（数据透视表绑定）
excel-advanced chart dynamic --pivot "透视表" --chart "柱形图"

# 定义命名范围
excel-advanced namedRange define --name "销售数据" --ref "Sheet1!$A$1:$D$100"

# 图表引用命名范围
excel-advanced chart bind --name "销售数据"
```

### 图表格式

```bash
# 设置图表样式
excel-advanced chart style --id "图表1" --template "企业蓝"

# 设置数据标签
excel-advanced chart labels --id "图表1" --show "值" --position "外侧"

# 设置坐标轴
excel-advanced chart axis --id "图表1" --y-min 0 --y-max 100 --y-unit 20
```

## VBA自动化

### 录制宏

```bash
# 开始录制
excel-advanced vba record --name "格式化报表"

# 停止录制
excel-advanced vba stop

# 查看代码
excel-advanced vba code --name "格式化报表"
```

### 编写VBA

```bash
# 生成VBA代码
excel-advanced vba generate --template "透视表刷新"

# 导入VBA模块
excel-advanced vba import --file "module.bas"
```

## 颜色编码标准

遵循天龙xlsx技能标准：

| 颜色 | 含义 | 示例 |
|------|------|------|
| **蓝色** (RGB:0,0,255) | 硬编码输入 | 阈值、判断条件 |
| **黑色** (RGB:0,0,0) | 公式计算 | =SUM(A:A) |
| **绿色** (RGB:0,128,0) | 同文件跨表引用 | =透视表!B10 |
| **红色** (RGB:255,0,0) | 外部文件引用 | ='[外部.xlsx]Sheet1'!A1 |
| **黄色背景** | 需关注假设 | 关键参数 |

## 命令速查

```bash
# 数据透视表
excel-advanced pivot create --data "数据.xlsx" --rows "行" --values "值"
excel-advanced slicer add --pivot "透视表" --field "字段"

# 条件格式
excel-advanced format number --range "A1:A10" --rule "大于" --value 100
excel-advanced format colorScale --range "A1:A10" --type "三色"

# 高级函数
excel-advanced function write --name "INDEX_MATCH" --formula "=INDEX(B:B,MATCH(A1,C:C,0))"

# 动态数组
excel-advanced function write --name "FILTER" --formula "=FILTER(A:C,B:B>\">100\")"

# 图表
excel-advanced chart create --type "柱形图" --data "A1:D10"
excel-advanced chart dynamic --pivot "透视表"

# VBA
excel-advanced vba record --name "宏名"
```

## 天龙引擎协同

| 天龙岗位 | 协同方式 |
|---------|---------|
| **17-01数据分析师** | 数据透视表+动态图表 |
| **60-01投资总监** | 财务模型+数据联动 |
| **64-01量化研究员** | 数据处理+指标计算 |
| **financial-model** | 三表联动+财务预测 |

## 依赖要求

- openpyxl (Excel操作)
- xlsxwriter (图表生成)
- pandas (数据处理)
- pywin32 (VBA自动化，Windows)
