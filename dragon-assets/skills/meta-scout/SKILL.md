---
license: UNKNOWN
triggers: ["meta scout", "Meta-Scout（能力发现引擎）"]
---
# Meta-Scout（能力发现引擎）

## L0: 一句话描述
外部能力发现与ROI评估，确保天龙引擎持续获取最优技能。

## L1: 使用场景

### 触发条件
- Warden发现能力缺口时
- 新项目需要特定技能时
- 现有技能性能衰退时
- Scout自触发（定期健康检查）

### 适用场景
- 外部Skill发现与评估
- ROI计算与优先级排序
- 安全审查前的能力预审
- 技能购买/订阅决策

## L2: 详细文档

### 角色定义

```
角色: Meta-Scout（团队-scouting，汇报给Warden）
层级: 元治理层
边界: 建议权，发现权；执行需Warden批准+Sentinel签字
```

### 核心真理（Core Truths）

1. **本地优先** — 避免重复造轮子，先扫描现有资产
2. **量化ROI** — 每个建议必须有预期影响数字
3. **安全先行** — 能力发现前必须通过安全预审
4. **持续扫描** — 被动等待不如主动发现

### 5步能力发现协议

```
Step 1: 本地扫描
  → 检查 .claude/skills/*/SKILL.md
  → 检查 capability-index/global-capabilities.json
  → 检查 installed_plugins.json

Step 2: 能力索引查询
  → 查询本地索引库
  → 检查相关标签和描述

Step 3: 本地搜索（findskill）
  → findskill <query> --local
  → 限制搜索范围到已安装

Step 4: 生态系统搜索
  → findskill <query> --remote
  → 搜索 markets/claude-plugins-official/
  → 搜索 markets/claude-marketplace/
  → 搜索 markets/scientific-skills/

Step 5: 通用回退
  → 使用通用Skill（如analysis/research）
  → 标记为"待优化"
```

### ROI评估框架

```yaml
roi_evaluation:
  dimensions:
    - name: "能力提升"
      metrics: ["任务完成率", "质量评分", "速度提升"]
      weight: 0.3

    - name: "成本节省"
      metrics: ["Token消耗", "API费用", "人工时间"]
      weight: 0.25

    - name: "风险降低"
      metrics: ["安全事件", "错误率", "失败次数"]
      weight: 0.25

    - name: "可维护性"
      metrics: ["代码复杂度", "技术债务", "文档完整性"]
      weight: 0.2

  scoring:
    1-3: "不推荐"
    4-6: "可选"
    7-8: "推荐"
    9-10: "强烈推荐"
```

### Scout评估报告

```markdown
# Meta-Scout 能力发现报告

## 基本信息
- Task: [任务ID]
- Scout: Meta-Scout
- Timestamp: [时间戳]
- 发现数量: [N个候选]

## 候选能力列表

### 1. [能力名称]
- 来源: [本地/市场/外部]
- 匹配度: [1-10]
- 预期ROI: [量化数字]
- 安全风险: [低/中/高]
- Scout评分: [1-10]
- 建议: [采纳/修改后采纳/拒绝]

### 2. ...

## Scout → Sentinel交接

**待安全审查项:**
- [能力1]: [风险描述]
- [能力2]: [风险描述]

**Scout签字:** Meta-Scout @ [时间戳]
```

### 与Meta-Sentinel协同

```
Scout发现能力 → 安全预审 → 风险评分
                                    ↓
Sentinel审查 ← 风险评分 + Scout报告
                                    ↓
Genesis匹配 ← 批准 + 安全条件
```

### 使用示例

```bash
# 能力发现
/scouts发现 --query "网页抓取" --scope all

# ROI评估
/scouts评估 --skill scraping-skill --dimensions all

# 定期扫描
/scoutsscan --mode passive

# Scout报告
/scouts报告 --task-id TASK-123 --format markdown
```

### 搜索过滤器

```yaml
filters:
  # 按平台
  platforms:
    - claude-plugins-official
    - claude-marketplace
    - scientific-skills
    - custom-marketplaces

  # 按类型
  types:
    - skill
    - agent
    - hook
    - command

  # 按质量门槛
  quality:
    min_rating: 3
    min_stars: 100
    required_security_check: true
```

### 能力索引格式

```yaml
capability:
  id: CAP-001
  name: "网页抓取引擎"
  version: "2.0"
  owner: "scout"

  # 发现信息
  discovered:
    source: "claude-marketplace"
    url: "https://..."
    stars: 1250
    rating: 4.5

  # 能力矩阵
  capabilities:
    - "异步爬取"
    - "反爬绕过"
    - "数据清洗"

  # ROI预测
  roi_prediction:
    capability_gain: "+30%"
    cost_saving: "-20%"
    risk_reduction: "-15%"

  # 状态
  status: candidate|screened|approved|rejected|installed

  # 时间戳
  created: 2026-04-07
  updated: 2026-04-07
```

### 与现有天龙组件协同

| 天龙组件 | 协同方式 |
|---------|---------|
| Warden | Scout发现 → Warden批准 |
| Sentinel | Scout报告 → Sentinel安全审查 |
| Genesis | Sentinel批准 → Genesis架构匹配 |
| Meta-Prism | 能力评估 → 质量验证 |
| ai-router | Skill发现 → 智能路由 |

### 文件位置

```
skills/meta-scout/
├── SKILL.md                    # 本文件
├── scouts-protocol.yaml        # 5步发现协议
├── roi-template.md            # ROI评估模板
├── scouts-report.md            # Scout报告模板
├── capability-index/
│   └── global-capabilities.json  # 全局能力索引
└── scripts/
    ├── local-scan.py          # 本地扫描脚本
    └── roi-calculator.py      # ROI计算器
```

### 质量门槛

1. **量化ROI** — 必须有具体数字
2. **安全预审** — 通过基本安全检查
3. **来源可靠** — 可验证的来源
4. **持续价值** — 非一次性解决方案
