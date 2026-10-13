# everlaw-mcp - 电子发现平台连接器

## L0: 一句话描述 (≤15字)
Everlaw电子发现平台连接器

## L1: 使用场景 (50-100字)
并购法务工程师通过MCP协议连接Everlaw电子发现平台，自动导入文档、分析元数据、生成审查报告。适用于78-01法律总顾问的大规模诉讼文档审查和78-03国际法师的跨境合规调查场景。

## L2: 详细文档

### 核心能力

1. **文档导入**
   - 自动从源系统导入文档
   - 元数据提取与标准化
   - 重复文档检测

2. **智能审查**
   - 文档编码与分类
   - 敏感信息标记
   - 相关性评分

3. **分析报告**
   - 文档量统计
   - 审阅进度追踪
   - privilege分析

### 输出格式

```yaml
everlaw_matter:
  matter_id: string
  matter_name: string
  client: string
  created_date: date
  status: "Active|Closed|OnHold"

  document_stats:
    total_documents: number
    total_pages: number
    total_size_gb: number
    custodians: number
    date_range:
      start: date
      end: date

  document_types:
    - type: string
      count: number
      percentage: number

  review_progress:
    total_assigned: number
    reviewed: number
    pending: number
    reviewed_percentage: number

  privilege_analysis:
    total_privileged: number
    with_holdings: number
    pending_review: number

  top_custodians:
    - name: string
      document_count: number
      review_status: string

  alerts:
    - type: string
      description: string
      urgency: string
```

### 使用命令

```bash
# 连接案件
/mcp everlaw connect --matter-id "MATTER-001" --api-key $EVERLAW_KEY

# 导入文档
/mcp everlaw import --source "file-server" --path /data/docs --format native

# 查看统计
/mcp everlaw stats --matter-id "MATTER-001" --format table

# 审查进度
/mcp everlaw progress --matter-id "MATTER-001"

# 生成报告
/mcp everlaw report --matter-id "MATTER-001" --format markdown --output ./report.md

# Privilege审查
/mcp everlaw privilege-review --matter-id "MATTER-001" --status pending

# 导出文档
/mcp everlaw export --matter-id "MATTER-001" --tag "responsive" --format production-set
```

### 电子发现报告模板

```markdown
# 电子发现Matter报告

## Matter概览
- Matter编号：MATTER-2026-001
- Matter名称：XYZ并购反垄断诉讼
- 客户：XYZ公司
- 创建日期：2026-01-15
- 当前状态：🟢 活跃

## 文档统计

| 指标 | 数值 |
|------|------|
| 文档总数 | 125,000 |
| 总页数 | 1,250,000 |
| 数据量 | 450 GB |
| 保管人数量 | 15 |
| 时间范围 | 2024-01-01 至 2026-05-14 |

## 文档类型分布
| 类型 | 数量 | 占比 |
|------|------|------|
| Email | 85,000 | 68% |
| Word文档 | 18,000 | 14.4% |
| Excel表格 | 12,000 | 9.6% |
| PDF | 7,500 | 6% |
| 其他 | 2,500 | 2% |

## 审阅进度

| 阶段 | 已分配 | 已审阅 | 待审阅 | 完成率 |
|------|--------|--------|--------|--------|
| 第一轮审阅 | 125,000 | 95,000 | 30,000 | 76% |
| 质量控制 | 95,000 | 28,500 | 66,500 | 30% |
| 律师审阅 | 40,000 | 35,000 | 5,000 | 87.5% |

## Privilege分析
| 类别 | 数量 | 状态 |
|------|------|------|
| 主张特权 | 8,500 | 审核中 |
|  withholding待审阅 | 3,200 | 待处理 |
|  放弃特权 | 1,100 | 已确认 |

## Top 5保管人
| 姓名 | 部门 | 文档数 | 审阅进度 |
|------|------|--------|---------|
| 张三 | 管理层 | 25,000 | 95% |
| 李四 | 法务部 | 18,000 | 88% |
| 王五 | 财务部 | 15,000 | 72% |
| 赵六 | 销售部 | 12,000 | 65% |
| 钱七 | 市场部 | 10,000 | 58% |

## 预警提醒
### 🔴 紧急
- 证据开示截止：2026-06-30（47天）
- 需完成剩余30,000文档审阅

### 🟠 高优先级
- QC完成率需提升至50%
- 专家报告截止：2026-07-15

## 建议行动
1. 增加审阅团队资源以赶上截止日
2. 优先完成管理层文档审阅
3. 启动privilege日志审阅
```

### 与天龙引擎协同

```yaml
天龙岗位协同:
  78-01 法律总顾问: everlaw-mcp主调用者
  78-03 国际法师: 跨境合规调查数据消费者

数据流:
  everlaw-mcp → 文档数据 → tabular-review
  everlaw-mcp → 审阅进度 → demand-intake
  everlaw-mcp → privilege分析 → privilege-log-review
```

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-14 | V11.12初始集成，基于Everlaw API |
