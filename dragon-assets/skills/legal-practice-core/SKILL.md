---
license: UNKNOWN
triggers: ["legal practice core", "legal-practice-core - 法律实践核心技能包"]
---
# legal-practice-core - 法律实践核心技能包

## L0: 一句话描述 (≤15字)
法律实践核心能力套件

## L1: 使用场景 (50-100字)
天龙引擎V11.12法律合规升级核心技能包，提供冷启动访谈、监管动态监控、合同续约监控、诉讼时间线监控四大能力，与73-02合规师V11.0/73-04法律合规工程师深度集成。

## L2: 详细文档

### 技能包结构

```
legal-practice-core/
├── SKILL.md                        # 本文件
├── skills/
│   ├── cold-start-interview/     # 冷启动访谈系统
│   ├── reg-feed-watcher/          # 监管动态监控
│   ├── contract-renewal-watcher/  # 合同续约监控
│   └── docket-watcher/            # 诉讼时间线监控
└── prompts/
    ├── cold-start-prompt.md
    ├── reg-feed-template.md
    └── practice-profile-template.md
```

### 核心能力矩阵

| 技能 | 功能 | 适用岗位 |
|------|------|---------|
| **cold-start-interview** | 实践档案(Practice Profile)初始化 | 73-04法律合规工程师 |
| **reg-feed-watcher** | NPRM追踪+政策差异分析+监管缺口评分 | 73-02合规师V11.0/73-04 |
| **contract-renewal-watcher** | 取消截止日扫描+延期提醒+自动处理 | 73-03风控师V2.0 |
| **docket-watcher** | 法院文件监控+截止日追踪+出庭提醒 | 73-05诉讼支持工程师 |

### MCP Server依赖

- `courtlistener-mcp` - 法院研究连接器
- `trellis-mcp` - 法院情报连接器

### 与天龙引擎协同

```yaml
天龙岗位协同:
  73-02 合规师: reg-feed-watcher 监管动态监控
  73-03 风控师: contract-renewal-watcher 合同续约监控
  73-04 法律合规工程师: cold-start-interview 冷启动访谈
  73-05 诉讼支持工程师: docket-watcher 诉讼时间线监控

CLAUDE.md集成:
  V11.12 升级: legal-practice-core 技能包集成
  来源: anthropics/claude-for-legal legal-practice-core
```

### 使用命令

```bash
# 冷启动访谈
/cold-start-interview

# 监管动态监控
/reg-feed-watcher

# 合同续约监控
/contract-renewal-watcher

# 诉讼时间线监控
/docket-watcher
```

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-14 | V11.12初始集成，基于Claude for Legal实践核心能力 |