# legal-mcp-connectors - 法律MCP连接器套件

## L0: 一句话描述 (≤15字)
法律MCP连接器四合一套件

## L1: 使用场景 (50-100字)
并购法务工程师通过MCP协议连接四大法律数据平台，实时获取判例法分析、诉讼进度追踪、电子发现数据和合同智能审查。适用于78-02投融资法务的跨境并购尽职调查和73-02合规师的监管合规分析场景。

## L2: 详细文档

### 技能包结构

```
legal-mcp-connectors/
├── SKILL.md                        # 本文件
├── courtlistener-mcp/             # 判例法分析
├── trellis-mcp/                   # 诉讼进度追踪
├── everlaw-mcp/                  # 电子发现
└── ironclad-mcp/                 # 合同智能审查
```

### 核心能力矩阵

| 连接器 | 功能 | 适用岗位 |
|--------|------|---------|
| **courtlistener-mcp** | 判例法检索+引用分析 | 78-01/78-03 |
| **trellis-mcp** | 诉讼进度追踪+案件状态 | 78-01/73-03 |
| **everlaw-mcp** | 电子发现+文档审查 | 78-01/78-03 |
| **ironclad-mcp** | 合同智能审查+条款分析 | 78-02/76-02 |

### 与天龙引擎协同

```yaml
天龙岗位协同:
  78-01 法律总顾问: courtlistener-mcp + trellis-mcp主调用者
  78-02 投融资法务: ironclad-mcp + everlaw-mcp
  73-02 合规师: courtlistener-mcp监管数据消费者
  73-03 风控师: trellis-mcp案件数据消费者

数据流:
  courtlistener-mcp → 判例数据 → ma-diligence-agent
  trellis-mcp → 诉讼数据 → demand-intake
  everlaw-mcp → 发现数据 → tabular-review
  ironclad-mcp → 合同数据 → issue-extraction
```

### 使用命令

```bash
# 判例法检索
/mcp courtlistener search "precedent:antitrust" --jurisdiction federal

# 诉讼进度追踪
/mcp trellis track --case-id "CASE-001" --monitor daily

# 电子发现
/mcp everlaw export --matter "MA-001" --format structured --output ./discovery/

# 合同审查
/mcp ironclad review --document ./contracts/SPA.pdf --clauses all
```

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-14 | V11.12初始集成，基于Claude for Legal MCP Connectors |
