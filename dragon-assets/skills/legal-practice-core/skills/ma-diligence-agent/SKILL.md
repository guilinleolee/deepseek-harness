# ma-diligence-agent - 并购尽职调查套件

## L0: 一句话描述 (≤15字)
并购尽职调查AI工作流套件

## L1: 使用场景 (50-100字)
并购法务工程师通过AI辅助完成并购尽职调查全流程，包括交易结构审查、尽职调查清单生成、问题提取与追踪、交易文档检查清单、交割前准备。适用于78-02投融资法务和76-02知识产权师的专业尽职调查场景。

## L2: 详细文档

### 技能包结构

```
ma-diligence-agent/
├── SKILL.md                        # 本文件
└── skills/
    ├── tabular-review/           # 尽职调查表格审查
    ├── issue-extraction/          # 问题提取与追踪
    ├── closing-checklist/         # 交割检查清单
    └── integration-runbook/       # 整合运行手册
```

### 核心能力矩阵

| 技能 | 功能 | 适用岗位 |
|------|------|---------|
| **tabular-review** | 尽职调查表格AI审查+风险标注 | 78-02投融资法务 |
| **issue-extraction** | 问题提取+优先级+追踪管理 | 78-02投融资法务 |
| **closing-checklist** | 交割前条件检查清单 | 78-02投融资法务 |
| **integration-runbook** | 整合阶段运行手册 | 78-02投融资法务 |

### 与天龙引擎协同

```yaml
天龙岗位协同:
  78-02 投融资法务: ma-diligence-agent主调用者
  76-02 知识产权师: 知识产权尽职调查数据消费者
  73-02 合规师: 合规尽职调查数据消费者

数据流:
  demand-intake → 交易档案 → ma-diligence-agent
  ma-diligence-agent → 调查材料 → 路由至78-02
```

### 使用命令

```bash
# 尽职调查表格审查
/ma-diligence tabular-review --deal-id "MA-001" --file ./due-diligence.xlsx

# 问题提取与追踪
/ma-diligence issues --deal-id "MA-001" --extract --track

# 交割检查清单
/ma-diligence closing --deal-id "MA-001" --output ./closing-checklist.md

# 整合运行手册
/ma-diligence runbook --deal-id "MA-001" --integration-date "2024-06-01"
```

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-14 | V11.12初始集成，基于Claude for Legal ma-diligence-agent |
