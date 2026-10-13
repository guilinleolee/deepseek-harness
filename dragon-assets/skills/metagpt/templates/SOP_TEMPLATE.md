# MetaGPT × 天龙引擎 SOP 协作模板

> MetaGPT SOP驱动 × 天龙九部专业分工

## 一、角色映射

| MetaGPT 角色 | 天龙岗位 | 思维模型 | 核心能力 |
|-------------|---------|---------|---------|
| **Product Manager** | 00分析师 | 数学思维 | 问题分析、量化决策 |
| **Architect** | 02架构师 | 第一性原理 | 架构设计、本质约束 |
| **Project Manager** | 09-02编排 | 系统论 | 任务编排、进度管理 |
| **Engineer** | 03构建师 | 化学思维 | 代码实现、模块耦合 |
| **QA Engineer** | 04验证师 | 工程可靠性 | 测试验证、FMEA |
| **Reviewer** | 06审查师 | 认知科学 | 代码审查、安全审计 |

## 二、工作流程

### Phase 1: 需求解析 (00分析师 + MetaGPT PM)

```
输入: 自然语言需求
   ↓
00分析师 × MetaGPT PM:
   → 需求澄清问题
   → 量化分析 (KPI/指标)
   → 生成用户故事 (User Stories)
   → 输出: REQUIREMENTS.md
   ↓
天龙记录: CLAUDE.md → requirements
```

### Phase 2: 架构设计 (02架构师 + MetaGPT Architect)

```
输入: REQUIREMENTS.md
   ↓
02架构师 × MetaGPT Architect:
   → 技术选型决策
   → 系统架构设计 (MVC/Microservices/Serverless)
   → 数据模型设计
   → API接口设计
   → 输出: ARCHITECTURE.md + API.md + DATA_DICT.md
   ↓
天龙记录: 架构决策 → ADR (Architecture Decision Records)
```

### Phase 3: 任务分解 (09-02编排 + MetaGPT PM)

```
输入: ARCHITECTURE.md
   ↓
09-02编排协调师 × MetaGPT PM:
   → 任务拆分 (Task Decomposition)
   → 依赖关系梳理
   → 优先级排序 (RICE/MoSCoW)
   → 并行任务识别
   → 输出: TASKS.md + DEPENDENCIES.md
   ↓
天龙编排: 编排元 → 场景化模板匹配
```

### Phase 4: 代码实现 (03构建师 + MetaGPT Engineer)

```
输入: TASKS.md
   ↓
03构建师 × MetaGPT Engineer (并行):
   → 模块1开发
   → 模块2开发
   → 模块3开发
   → ...
   输出: 完整代码库 + DOCS.md
   ↓
天龙验证: TDD → 先写测试再写代码
```

### Phase 5: 测试验证 (04验证师 + MetaGPT QA)

```
输入: 代码库
   ↓
04验证师 × MetaGPT QA:
   → 单元测试生成
   → 集成测试设计
   → E2E测试设计
   → 测试执行与报告
   → 输出: TEST_REPORT.md + COVERAGE.md
   ↓
天龙审查: 验证 → 回归测试 + 边界测试
```

### Phase 6: 代码审查 (06审查师)

```
输入: 代码库 + TEST_REPORT.md
   ↓
06审查师:
   → 架构合理性审查
   → 代码质量审查 (SOLID/DRY/KISS)
   → 安全漏洞扫描
   → 性能审查
   → 输出: REVIEW.md + SECURITY_REPORT.md
   ↓
天龙发布: 08发布师 → 合并 + 部署
```

## 三、协作协议

### 3.1 通讯协议

```yaml
# 角色间通讯格式
Message:
  from: Role
  to: Role
  type: question/answer/action/report
  content: JSON/Text
  priority: high/normal/low
  deadline: ISO8601
```

### 3.2 状态同步

```yaml
# 任务状态
States:
  - PENDING      # 待处理
  - IN_PROGRESS   # 进行中
  - BLOCKED       # 阻塞
  - COMPLETED     # 完成
  - FAILED        # 失败

# 状态同步频率
Sync:
  - 高优先级任务: 每5分钟
  - 普通任务: 每30分钟
  - 低优先级任务: 每小时
```

### 3.3 冲突解决

```yaml
# 冲突类型
Conflicts:
  - 架构冲突: 02架构师仲裁
  - 任务冲突: 09-02编排协调
  - 质量冲突: 04验证师判定
  - 安全冲突: 05安全师裁定

# 解决流程
Resolution:
  1. 提出方说明理由
  2. 相关方回应
  3. 仲裁方决策
  4. 记录决策 → ADR
```

## 四、输出规范

### 4.1 文档格式

```markdown
# [文档名称]

## 元信息
- 创建日期: YYYY-MM-DD
- 创建者: [角色]
- 版本: X.Y.Z
- 状态: draft/review/approved

## 内容
...

## 变更历史
| 日期 | 修改人 | 变更内容 |
|------|--------|---------|
| ... | ... | ... |
```

### 4.2 代码格式

```python
# 模块级docstring
"""模块描述.

详细说明...

Attributes:
    attr1: 说明
    attr2: 说明
"""

class ClassName:
    """类描述."""
    pass

def function_name(param1: Type1, param2: Type2) -> ReturnType:
    """函数描述.

    Args:
        param1: 参数1说明
        param2: 参数2说明

    Returns:
        返回值说明

    Raises:
        ExceptionType: 异常说明
    """
    pass
```

## 五、质量门禁

### 5.1 门禁检查点

```yaml
Gates:
  - Gate1: 需求解析完成
      check: REQUIREMENTS.md 存在且完整
      owner: 00分析师

  - Gate2: 架构设计完成
      check: ARCHITECTURE.md 通过审查
      owner: 02架构师

  - Gate3: 代码实现完成
      check: 单元测试覆盖率 > 80%
      owner: 04验证师

  - Gate4: 集成测试完成
      check: 集成测试通过率 100%
      owner: 04验证师

  - Gate5: 代码审查完成
      check: 无阻塞问题
      owner: 06审查师

  - Gate6: 安全审查完成
      check: 无高危漏洞
      owner: 05安全师
```

### 5.2 质量指标

```yaml
Metrics:
  code:
    coverage: "> 80%"
    complexity: "< 15"
    duplication: "< 3%"

  test:
    unit_pass_rate: "100%"
    integration_pass_rate: "100%"
    e2e_pass_rate: "> 95%"

  security:
    critical_vulnerabilities: 0
    high_vulnerabilities: 0
    medium_vulnerabilities: "< 3"

  performance:
    response_time_p95: "< 200ms"
    throughput: "> 1000 req/s"
```

## 六、天龙引擎增强

### 6.1 SOP标准化

```python
# 天龙SOP标准化接口
class DragonSOP:
    def __init__(self, requirement: str):
        self.requirement = requirement
        self.roles = self.define_roles()
        self.workflow = self.define_workflow()

    def define_roles(self):
        return [
            DragonRole("00", "分析师", MathThinking()),
            DragonRole("02", "架构师", FirstPrinciples()),
            DragonRole("09-02", "编排", SystemThinking()),
            DragonRole("03", "构建师", ChemistryThinking()),
            DragonRole("04", "验证师", ReliabilityThinking()),
            DragonRole("06", "审查师", CognitiveThinking()),
        ]

    def execute(self):
        # 1. 需求解析
        requirements = self.roles["00"].parse(self.requirement)

        # 2. 架构设计
        architecture = self.roles["02"].design(requirements)

        # 3. 任务编排
        tasks = self.roles["09-02"].decompose(architecture)

        # 4. 并行开发
        code = self.roles["03"].implement(tasks)

        # 5. 测试验证
        tests = self.roles["04"].verify(code)

        # 6. 代码审查
        review = self.roles["06"].review(code, tests)

        return SoftwareProduct(
            requirements=requirements,
            architecture=architecture,
            code=code,
            tests=tests,
            review=review
        )
```

### 6.2 与MetaGPT集成

```python
# MetaGPT × 天龙引擎 集成
class MetaGPTDragonIntegration:
    def __init__(self):
        self.metagpt = MetaGPT()
        self.dragon = DragonSOP()

    def run(self, requirement: str):
        # MetaGPT生成基础产物
        metagpt_output = self.metagpt.run(requirement)

        # 天龙增强
        dragon_output = self.dragon.enhance(metagpt_output)

        # 质量门禁检查
        gates_passed = self.check_gates(dragon_output)

        return dragon_output if gates_passed else None
```

---

*Version: 1.0.0 | Updated: 2026-03-30*
