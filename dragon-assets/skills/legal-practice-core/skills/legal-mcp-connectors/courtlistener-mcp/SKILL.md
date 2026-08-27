# courtlistener-mcp - Free Law Project判例法连接器

## L0: 一句话描述 (≤15字)
Free Law Project判例法检索连接器

## L1: 使用场景 (50-100字)
并购法务工程师通过MCP协议连接Free Law Project数据库，检索判例法、分析引用链、提取法律摘要。支持美国联邦和各州判例法检索，适用于78-01法律总顾问的判例研究和73-02合规师的监管合规分析场景。

## L2: 详细文档

### 核心能力

1. **判例法检索**
   - 美国联邦法院判例（DISTRICT、APPEALS、SUPREME）
   - 各州判例法数据库
   - 按日期/法院/法官/律师筛选

2. **引用链分析**
   - 正向引用（cited by）
   - 反向引用（citing）
   - 引用深度追溯

3. **法律摘要生成**
   - 案件要点自动提取
   - 判决理由结构化
   - 相关法规关联

### 输出格式

```yaml
courtlistener_search:
  query: string
  jurisdiction: "federal|state"
  court: string
  date_range:
    start: date
    end: date

  results:
    - case_id: string
      case_name: string
      citation: string
      court: string
      date_filed: date
      docket_number: string
      precedential_status: "Published|Unpublished"
      judges: [string]
      attorneys: [string]
      parties: [string]
      summary: string
      holding: string
      cited_by:
        - citation
        - case_name
      citing:
        - citation
        - case_name
      relevance_score: number
```

### 使用命令

```bash
# 基本检索
/mcp courtlistener search "antitrust merger" --jurisdiction federal

# 按法院筛选
/mcp courtlistener search "antitrust" --court "cafc"

# 引用分析
/mcp courtlistener citations "338 U.S. 1" --depth 2

# 批量下载
/mcp courtlistener bulk --query "price-fixing" --format json --output ./cases/

# 法规关联
/mcp courtlistener statutes --us-code "15-1" --related-cases 10
```

### 判例检索报告模板

```markdown
# 判例法检索报告

## 检索条件
- 关键词：antitrust merger
- 管辖区：Federal
- 日期范围：2020-01-01 至 2026-05-14

## 高相关判例

| 案件 | 法院 | 日期 | 相关性 | 要点 |
|------|------|------|--------|------|
| United States v. AT&T | D.D.C. | 2018-08-21 | 🔴 极高 | 横向并购反垄断审查标准 |
| FTC v. Sysco | D.D.C. | 2015-07-14 | 🔴 极高 | 食品分销并购反垄断审查 |
| United States v. H&R Block | D.D.C. | 2011-11-17 | 🟠 高 | 税务服务并购竞争分析 |

## 引用链分析
- 正向引用：45个案件引用
- 反向引用：12个案件引用
- 核心判例：Sherman Act §1

## 关键法律原则
1. 实质性减少竞争标准（SSNIP测试）
2. 市场界定分析方法
3. 合规抗辩理由

## 建议
- 重点参考AT&T案并购协议条款
- 关注FTC审查关注的市场集中度指标（HHI）
```

### 与天龙引擎协同

```yaml
天龙岗位协同:
  78-01 法律总顾问: courtlistener-mcp主调用者
  78-02 投融资法务: 并购反垄断判例数据消费者
  73-02 合规师: 监管判例数据消费者

数据流:
  courtlistener-mcp → 判例检索 → ma-diligence-agent(issue-extraction)
  courtlistener-mcp → 引用分析 → 风险评估报告
  courtlistener-mcp → 法规关联 → 合规检查清单
```

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-14 | V11.12初始集成，基于Free Law Project API |
