---
license: UNKNOWN
triggers: ["founder mcp", "Solo Founder MCP — 一人公司创始人工具集"]
---
# Solo Founder MCP — 一人公司创始人工具集

## L0: 一句话描述 (≤15字)
一人公司跑道守护：想法验证 + MVP边界 + 上线检查

## L1: 使用场景 (50-100字)
Solo Founder（一人公司创始人）专用MCP工具集，为天龙引擎Agent提供极简创业思维支持。适用场景包括：创业想法验证（6问压力测试）、MVP边界保护（防范围步）、20项上线检查、魔法时刻触发器设计、跑道计算（资金+时间）。与其他天龙工具互补——不替代市场调研或技术实现，专注"极简决策"本身。

## L2: 详细文档

### Overview

Solo Founder MCP 将一人公司创始人的5个核心命令封装为MCP工具，供天龙引擎Agent调用。核心哲学：**反规模主义**——每一个复杂性的添加，都必须用等量或更大的价值来证明。

### Server Information

- **Server Name**: `founder_mcp`
- **Transport**: stdio (local subprocess)
- **Language**: Python 3
- **Framework**: FastMCP
- **Dependencies**: `pydantic>=2.0`
- **Entry Point**: `scripts/founder_mcp.py`

### Tool Inventory

| Tool Name | 对应命令 | 功能 | Read-Only |
|-----------|---------|------|-----------|
| `founder_pressure_test` | `/founder-pressure-test` | 6问想法验证 | ✅ |
| `founder_mvp_scope_limit` | `/mvp-scope-limit` | MVP边界保护 | ✅ |
| `founder_launch_check` | `/founder-launch-check` | 20项上线检查 | ✅ |
| `founder_airstrip_one` | `/airstrip-one` | 魔法时刻触发器 | ✅ |
| `founder_runway_calculation` | `/founder-runway` | 跑道计算 | ✅ |

---

### Tool 1: `founder_pressure_test`

**命令**: `/founder-pressure-test`

**Description**: 在投入任何开发资源之前，用6问验证想法是否值得追求。

**Input Schema**:
```python
class PressureTestInput(BaseModel):
    problem_description: str = Field(
        description="要验证的商业想法或痛点描述（5-2000字符）",
        min_length=5, max_length=2000
    )
    format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="输出格式: markdown(默认) 或 json"
    )
```

**Output Schema**:
```python
class PressureTestOutput(BaseModel):
    result: str = Field(description="压力测试结果_markdown格式")
    json_result: Optional[dict] = Field(default=None, description="压力测试结果_json格式")
    pass_score: int = Field(description="通过分数(0-6)")
    verdict: str = Field(description="判定结果: 通过/部分通过/不通过")
```

**6问内容**:
1. 真实痛点：这个问题是你亲身经历的吗？还是道听途说？
2. 具体客户：你能说出这个人的名字、行业、职位吗？
3. 付费意愿：如果明天收他们$99/月，他们会掏钱吗？
4. 竞品缺口：为什么现有方案做不好？
5. 防御壁垒：6个月后会有10个竞争对手吗？
6. 时间窗口：你的优势会在12个月内消失吗？

**Pass Criteria**: 6问中至少4问有明确答案，且至少2问答案是"是"。

**Usage Example**:
```
# Markdown格式（默认）
founder_pressure_test(
    problem_description="中小企业主需要自动化的社交媒体日程管理工具，节省每天30分钟的发布操作时间"
)

# JSON格式
founder_pressure_test(
    problem_description="远程团队需要统一的文档知识库，减少知识流失",
    format="json"
)
```

**Annotations**: `readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False`

---

### Tool 2: `founder_mvp_scope_limit`

**命令**: `/mvp-scope-limit`

**Description**: MVP不是"缩小版产品"，而是"最小可验证实验"。保护MVP边界，防止范围蔓延。

**Input Schema**:
```python
class MvpScopeLimitInput(BaseModel):
    core_value_proposition: str = Field(
        description="核心价值主张描述（5-1000字符）",
        min_length=5, max_length=1000
    )
    proposed_features: list[str] = Field(
        description="候选功能列表",
        min_length=1, max_length=20
    )
    development_time_weeks: float = Field(
        description="计划开发时间（周）",
        ge=0.5, le=52
    )
    format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)
```

**Output Schema**:
```python
class MvpScopeLimitOutput(BaseModel):
    result: str = Field(description="MVP边界分析结果_markdown格式")
    json_result: Optional[dict] = Field(default=None)
    recommended_features: list[str] = Field(description="建议保留功能")
    excluded_features: list[str] = Field(description="建议排除功能（及原因）")
    scope_verdict: str = Field(description="范围判定")
```

**Decision Rules**:
- 功能数 = `max(3, 核心价值主张所需的最小功能数)`
- 开发时间 = `max(1周, 能在1周内完成的时间)`
- 每加一个功能，必须回答：**去掉这个功能MVP还能工作吗？**

**边界保护（永远不加）**:
- ❌ 用户反馈系统（手动收集即可）
- ❌ 多用户/权限系统（先单用户）
- ❌ 高级分析（先Excel）
- ✅ 必须：支付系统（没有它就没收入）

**Annotations**: `readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False`

---

### Tool 3: `founder_launch_check`

**命令**: `/founder-launch-check`

**Description**: 上线前20项检查清单，覆盖核心价值、商业闭环、技术底线、获客准备、法律合规五大维度。

**Input Schema**:
```python
class LaunchCheckInput(BaseModel):
    product_name: str = Field(description="产品名称")
    has_payment: bool = Field(description="是否已接通支付（Stripe/支付宝等）")
    target_customer: str = Field(description="目标客户描述")
    format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)
```

**Output Schema**:
```python
class LaunchCheckOutput(BaseModel):
    result: str = Field(description="检查结果_markdown格式")
    json_result: Optional[dict] = Field(default=None)
    total_items: int = Field(description="总检查项数(固定20)")
    passed_items: int = Field(description="通过项数")
    failed_items: list[str] = Field(description="未通过项列表")
    launch_ready: bool = Field(description="是否可以上线")
    risk_level: str = Field(description="风险等级: 高/中/低")
```

**20项检查清单**:

| 维度 | # | 检查项 |
|------|---|--------|
| **核心价值** | 1 | 客户能在3分钟内理解产品是什么 |
| | 2 | 客户能在5分钟内完成注册 |
| | 3 | 客户能在10分钟内体验到核心价值 |
| | 4 | 客户愿意向朋友推荐你的产品 |
| **商业闭环** | 5 | 支付已接通Stripe/支付宝 |
| | 6 | 退款政策已写明 |
| | 7 | 服务条款和隐私政策已发布 |
| | 8 | 客户能联系到真人（你） |
| **技术底线** | 9 | 核心页面加载<3秒 |
| | 10 | 注册/登录流程无bug |
| | 11 | 移动端可正常使用 |
| | 12 | 关键数据有备份 |
| **获客准备** | 13 | 有1条让人想分享的内容 |
| | 14 | 有1个收集邮箱的入口 |
| | 15 | 知道前10个客户在哪里 |
| | 16 | 定价经过竞品对比 |
| **法律/合规** | 17 | 明确的数据存储政策 |
| | 18 | 明确的服务限制（如有） |
| | 19 | 有紧急情况联系信息 |
| | 20 | 准备好客户支持时间 |

**Annotations**: `readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False`

---

### Tool 4: `founder_airstrip_one`

**命令**: `/airstrip-one`

**Description**: Airstrip One = 跑道一号 = 你的钱烧完前的最后期限。找到"魔法时刻"并加速到达。

**Input Schema**:
```python
class AirstripOneInput(BaseModel):
    user_journey_description: str = Field(
        description="用户旅程描述（5-2000字符）",
        min_length=5, max_length=2000
    )
    format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)
```

**Output Schema**:
```python
class AirstripOneOutput(BaseModel):
    result: str = Field(description="魔法时刻分析结果_markdown格式")
    json_result: Optional[dict] = Field(default=None)
    magic_moments: list[dict] = Field(description="发现的魔法时刻列表")
    recommended_triggers: list[dict] = Field(description="建议的触发器")
```

**Magic Moment Definition**:
- 用户第一次说出"哇！"是什么时候？
- 用户第一次主动向别人提起你是什么时候？
- 用户第一次愿意付钱是什么时候？

**4-Step Framework**:
1. 找到"魔法时刻" — 识别上述3个关键时刻
2. 加速到达魔法时刻 — 删除到达前的所有摩擦
3. 设计触发器 — Push触发/行为触发/时间触发
4. 测量魔法时刻到达率 — <20%则onboarding有问题

**Magic Moment Rate Benchmark**:
| 到达率 | 判定 |
|--------|------|
| <20% | on boarding有问题 |
| 20-50% | 需优化 |
| >50% | 找到增长杠杆 |

**Annotations**: `readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False`

---

### Tool 5: `founder_runway_calculation`

**命令**: `/founder-runway`

**Description**: 计算剩余跑道（时间和资金），判断当前阶段，给出优先级建议。

**Input Schema**:
```python
class RunwayCalculationInput(BaseModel):
    monthly_burn: float = Field(
        description="每月烧钱金额（人民币元）",
        ge=0
    )
    monthly_revenue: float = Field(
        description="每月收入（人民币元）",
        ge=0
    )
    current_cash: float = Field(
        description="当前现金储备（人民币元）",
        ge=0
    )
    monthly_expenses: dict[str, float] = Field(
        description="每月支出明细",
        default_factory=dict
    )
    format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)
```

**Output Schema**:
```python
class RunwayCalculationOutput(BaseModel):
    result: str = Field(description="跑道分析结果_markdown格式")
    json_result: Optional[dict] = Field(default=None)
    net_monthly_burn: float = Field(description="净月烧钱额")
    runway_months: float = Field(description="剩余跑道（月数）")
    current_phase: str = Field(description="当前阶段")
    phase_priority: str = Field(description="阶段优先级建议")
    alerts: list[str] = Field(description="警告信息")
```

**Phase Determination**:
| 阶段 | MRR范围 | 核心问题 | 唯一目标 |
|------|---------|---------|---------|
| **生存期** | $0-$500 | 有人愿意付钱吗？ | 找到第一个付费客户 |
| **验证期** | $500-$5k | 能重复卖吗？ | 3个付费客户以上 |
| **增长期** | $5k-$50k | 如何更快增长？ | 月复合增长>10% |
| **自由期** | $50k+ | 要规模化吗？ | 保持一人还是扩张 |

**Runway Alert Thresholds**:
| 跑道剩余 | 警告等级 | 行动 |
|---------|---------|------|
| <2个月 | 🔴 CRITICAL | 立即止血，或找融资 |
| 2-4个月 | 🟠 HIGH | 加速验证，全力获客 |
| 4-6个月 | 🟡 MEDIUM | 优化unit economics |
| >6个月 | 🟢 HEALTHY | 保持当前节奏 |

**Annotations**: `readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False`

---

### Installation & Configuration

**MCP Settings** (add to `~/.claude/settings.json` or project `.mcp.json`):

```json
{
  "mcpServers": {
    "founder_mcp": {
      "command": "python",
      "args": ["-m", "skills.founder_mcp.scripts.founder_mcp"],
      "env": {}
    }
  }
}
```

**Alternative — Direct Path**:
```json
{
  "mcpServers": {
    "founder_mcp": {
      "command": "python",
      "args": ["C:/Users/li/.claude/skills/founder-mcp/scripts/founder_mcp.py"],
      "env": {}
    }
  }
}
```

**Dependency Installation**:
```bash
pip install pydantic>=2.0
```

---

### 天龙引擎协同矩阵

| 天龙岗位 | 协同方式 | 使用Tool |
|---------|---------|---------|
| **00分析师** | 问题消解前，用Pressure Test验证想法 | `founder_pressure_test` |
| **03构建师** | 开发前，用MVP Scope Limiter锁定边界 | `founder_mvp_scope_limit` |
| **08发布师** | 上线前，用Launch Check走完20项检查 | `founder_launch_check` |
| **00分析师** | 跑道守护：每月运行Runway Calculation | `founder_runway_calculation` |
| **00分析师** | 增长瓶颈诊断：找魔法时刻触发器 | `founder_airstrip_one` |
| **25-02精益创业导师** | Lean Startup方法论支撑 | 全部工具 |

**典型工作流**:
```
[00分析师] 验证想法 → founder_pressure_test
    ↓
[03构建师] 锁定MVP边界 → founder_mvp_scope_limit
    ↓
[08发布师] 上线前检查 → founder_launch_check
    ↓
[00分析师] 跑道守护 → founder_runway_calculation (每月)
```

---

## Version History

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-20 | 初始版本，5个MCP工具 |

## Metadata

- **Skill Name**: founder-mcp
- **Category**: ai
- **Created**: 2026-05-20
- **Source**: 一人公司创始人框架 (99-01-solopreneur-founder.md)
- **Framework**: FastMCP + Pydantic v2
- **Triggers**: 用户提到「Solo Founder」「一人公司」「跑道守护」「创业想法验证」「MVP边界」「上线检查」时
