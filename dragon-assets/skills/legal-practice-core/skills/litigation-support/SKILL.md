# litigation-support - 诉讼支持技能包

## L0: 一句话描述 (≤15字)
诉讼流程自动化支持套件

## L1: 使用场景 (50-100字)
诉讼支持工程师专用技能包，提供需求受理、诉讼图表构建、特权日志审查、取证准备四大核心能力，与73-05诉讼支持工程师深度集成，适用于73-03风控师的风险追踪场景。

## L2: 详细文档

### 技能包结构

```
litigation-support/
├── SKILL.md                        # 本文件
├── skills/
│   ├── demand-intake/             # 需求受理系统
│   ├── claim-chart-builder/       # 诉讼图表构建
│   ├── privilege-log-review/      # 特权日志审查
│   └── deposition-prep/           # 取证准备助手
└── prompts/
    ├── demand-template.md
    ├── chart-template.md
    └── privilege-review-template.md
```

### 核心能力矩阵

| 技能 | 功能 | 适用岗位 |
|------|------|---------|
| **demand-intake** | 案件信息收集+分类+路由 | 73-05诉讼支持工程师 |
| **claim-chart-builder** | 诉讼请求可视化+时间线 | 73-05诉讼支持工程师 |
| **privilege-log-review** | 特权日志AI审查+风险标注 | 73-05诉讼支持工程师 |
| **deposition-prep** | 取证问题生成+证人准备 | 73-05诉讼支持工程师 |

### 与天龙引擎协同

```yaml
天龙岗位协同:
  73-05 诉讼支持工程师: litigation-support主调用者
  73-03 风控师: litigation-support风险数据消费者

CLAUDE.md集成:
  V11.12 升级: litigation-support技能包集成
  来源: anthropics/claude-for-legal litigation-support
```

### 使用命令

```bash
# 需求受理
/demand-intake

# 诉讼图表
/claim-chart-builder

# 特权审查
/privilege-log-review

# 取证准备
/deposition-prep
```

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-14 | V11.12初始集成，基于Claude for Legal litigation-support |