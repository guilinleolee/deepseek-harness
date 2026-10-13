# 触发词速查（中文 + 英文）

> 与 `SKILL.md` §1 同步；本文件只列触发词与路由，便于 LLM 在意图识别阶段做决策。

## A. Sheet（工作簿 / 表格）

| 中文 | 英文 |
|---|---|
| 做个工作簿 | create workbook |
| 做个 Excel | make spreadsheet |
| 做个 xlsx | build xlsx |
| 做个表格 | create sheet |
| 做个财务模型 | build financial model |
| 做个预算 | build budget |
| 做个销售报表 | make sales report |
| 加个图表 | add a chart |
| 加个透视表 | add a pivot |
| 加个迷你图 | add sparkline |
| 加条件格式 | add conditional formatting |

→ 加载 `univer` + `univer-sheet`

## B. Doc（Word 文档）

| 中文 | 英文 |
|---|---|
| 做个 Word | create doc |
| 做个 docx | write docx |
| 写个研报 | draft report |
| 写个周报 | draft weekly report |
| 做个正式报告 | formal report |
| 写个项目周报 | project weekly report |
| 做个有页眉页脚的文档 | document with header/footer |

→ 加载 `univer` + `univer-doc`

## C. Slide（PPT 幻灯）

| 中文 | 英文 |
|---|---|
| 做个 PPT | create deck |
| 做个路演 | make pitch deck |
| 做个 deck | build deck |
| 做个课件 | make lessons |
| 做个幻灯 | create slides |
| 做个视觉提案 | visual proposal |
| 做个客户提案 | client proposal |
| 帮我重做这几页 | redesign these pages |

→ 加载 `univer` + `univer-slide`

## D. Base（轻量数据库）

| 中文 | 英文 |
|---|---|
| 做个客户表 | customer tracker |
| 做个 CRM | lightweight CRM |
| 做个客户追踪 | customer tracking |
| 做个字段化表 | field-based table |
| 做个库存表 | inventory table |

→ 加载 `univer` + `univer-base`

## E. Board（可编辑画布）

| 中文 | 英文 |
|---|---|
| 做个画布 | create canvas |
| 做个流程图 | draw flowchart |
| 做个示意图 | make diagram |
| 做个思维导图 | mind map |
| 做个组织架构图 | org chart |

→ 加载 `univer` + `univer-board`

## F. 导入 / 导出 / 审阅

| 中文 | 英文 |
|---|---|
| 把这个 xlsx 转过来 | import this xlsx |
| 打开这个 Excel | open this Excel |
| 导入这个 pptx | import this pptx |
| 导出 xlsx | export xlsx |
| 导出 PPT | export pptx |
| 导出 docx | export docx |
| 给我个 Excel | give me Excel |
| 给我个 PPT | give me slides |
| 审阅一下 | review changes |
| 在工作台预览 | preview in workbench |

→ 加载 `univer`（按产物类型再加载对应 Unit skill）

## G. 工作台与交互

| 中文 | 英文 |
|---|---|
| 工作台 | workbench |
| 浏览器预览 | browser preview |
| 实时预览 | live preview |
| worktree 隔离 | isolated worktree |
| 多轮修订 | multi-round revision |

→ 暗示 DSH 内置预览，应优先 bridge 路径
