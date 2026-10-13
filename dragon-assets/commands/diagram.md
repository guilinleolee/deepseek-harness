---
name: diagram
description: diagram slash command
invokable: true
---
# diagram slash command

## description
Generate editorial-quality HTML+SVG diagrams using diagram-design skill

## 触发条件
用户需要生成流程图、时序图、象限图、时间线、泳道图等专业化图表时触发

## 工作流程
1. 识别图表类型（14种之一）
2. 确定变体（minimal-light / minimal-dark / full-editorial）
3. 使用diagram-design skill生成HTML+SVG
4. 如需品牌适配，执行60秒Onboarding

## 示例
/diagram flow "用户下单流程"
/diagram sequence "API调用时序"
/diagram quadrant "SWOT分析" --data "S:优势,W:劣势,O:机会,T:威胁"
/diagram timeline "产品路线图"
/diagram swimlane "电商流程"
