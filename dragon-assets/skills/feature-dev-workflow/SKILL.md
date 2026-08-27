---
license: UNKNOWN
---

# feature-dev-workflow

## L0: 一句话描述（≤15字）
七阶段结构化功能开发流程

## L1: 使用场景（50-100字）
当需要进行新功能开发时，触发此Skill。它遵循七阶段结构化流程（discover→plan→brief→reimagine→transform→harden→verify），每个阶段有明确的输入、输出和验收标准，确保功能开发的质量和可控性。

## L2: 详细文档

### 七阶段流程

```
┌─────────────────────────────────────────────────────────────┐
│                    feature-dev 七阶段流程                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Phase 1: DISCOVER (需求发现)                              │
│  输入: 原始需求描述                                         │
│  输出: 需求边界枚举、功能范围定义                           │
│  工具: 5Why分析、用户故事地图                              │
│                                                             │
│  Phase 2: PLAN (任务规划)                                  │
│  输入: 需求边界                                            │
│  输出: 任务分解WBS、依赖关系图、时间估算                    │
│  工具: 任务分解、依赖分析                                   │
│                                                             │
│  Phase 3: BRIEF (需求简报)                                │
│  输入: 任务分解                                            │
│  输出: 标准化需求简报文档                                  │
│  工具: 模板填充、技术约束                                   │
│                                                             │
│  Phase 4: REIMAGINE (方案重想)                            │
│  输入: 需求简报                                            │
│  输出: 可选方案对比、推荐方案                               │
│  工具: 批判性审查、矛盾分析法                              │
│                                                             │
│  Phase 5: TRANSFORM (代码实施)                             │
│  输入: 推荐方案                                            │
│  输出: 完整功能代码                                        │
│  工具: TDD驱动、MVP优先                                   │
│                                                             │
│  Phase 6: HARDEN (强化处理)                               │
│  输入: 功能代码                                            │
│  输出: 边界处理、错误处理、测试用例                        │
│  工具: 边界枚举、异常处理、Edge Case                      │
│                                                             │
│  Phase 7: VERIFY (验证通过)                               │
│  输入: 强化代码                                            │
│  输出: 测试报告、部署清单                                  │
│  工具: 自动化测试、代码审查                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Phase 1: DISCOVER

**目标**: 完整理解需求，枚举所有边界

**输入**: 原始需求描述（用户故事、问题描述、功能需求）

**输出**:
```yaml
discover_output:
  requirements:
    primary: "用户能够通过邮箱注册账号"
    secondary:
      - "注册需要邮箱验证"
      - "密码强度要求8位以上"
    implicit:
      - "邮箱格式验证"
      - "重复注册检测"

  boundaries:
    included:
      - "邮箱格式校验"
      - "密码强度校验"
      - "验证码发送"
      - "账号激活链接"
    excluded:
      - "第三方登录（OAuth）"
      - "社交分享功能"
      - "用户头像上传"

  edge_cases:
    - "邮箱格式错误"
    - "邮箱已被注册"
    - "密码强度不足"
    - "验证码过期"
    - "重复点击注册"
    - "网络超时"

  ambiguity_questions:
    - "密码需要包含特殊字符吗？"
    - "验证码有效期是多久？"
    - "注册失败后的重试策略？"
```

**方法**:
- 5Why追问法: 连续追问5个为什么挖掘根本需求
- 用户故事地图: 梳理用户旅程中的触点
- 边界枚举: 明确包含/排除项

### Phase 2: PLAN

**目标**: 任务分解，识别依赖，制定计划

**输入**: discover阶段输出

**输出**:
```yaml
plan_output:
  wbs:
    - id: 1.1
      name: "创建用户数据模型"
      estimate: "1h"
      dependencies: []
      owner: "backend"

    - id: 1.2
      name: "实现邮箱格式验证"
      estimate: "2h"
      dependencies: ["1.1"]
      owner: "backend"

    - id: 1.3
      name: "实现密码加密存储"
      estimate: "1h"
      dependencies: ["1.1"]
      owner: "backend"

    - id: 2.1
      name: "开发注册API接口"
      estimate: "3h"
      dependencies: ["1.1", "1.2", "1.3"]
      owner: "backend"

    - id: 3.1
      name: "开发注册页面前端"
      estimate: "2h"
      dependencies: []
      owner: "frontend"

    - id: 3.2
      name: "集成前后端注册流程"
      estimate: "1h"
      dependencies: ["2.1", "3.1"]
      owner: "frontend"

  critical_path:
    - "1.1 → 1.2 → 2.1 → 3.2"
    duration: "8h"

  risks:
    - name: "验证码服务依赖"
      probability: "medium"
      impact: "high"
      mitigation: "使用mock服务先完成开发"
```

### Phase 3: BRIEF

**目标**: 生成标准化需求简报

**输出**:
```markdown
# 功能简报: 用户注册

## 概述
允许新用户通过邮箱注册账号，需要邮箱验证激活。

## 功能范围
- 邮箱格式验证
- 密码强度校验（8位以上）
- 验证码发送（6位数字，有效期10分钟）
- 账号激活链接（有效期24小时）

## 技术约束
- 技术栈: Node.js + Express + MongoDB
- API风格: RESTful
- 认证方式: JWT

## 验收标准
1. 有效邮箱格式可通过验证
2. 无效邮箱格式显示错误提示
3. 弱密码无法提交，显示强度提示
4. 验证码10分钟内有效
5. 激活链接24小时内有效
6. 重复邮箱注册返回友好错误

## 测试场景
- [ ] TC001: 有效邮箱注册成功
- [ ] TC002: 无效邮箱格式校验
- [ ] TC003: 弱密码校验
- [ ] TC004: 验证码正确验证
- [ ] TC005: 激活链接有效激活
- [ ] TC006: 重复邮箱注册错误
```

### Phase 4: REIMAGINE

**目标**: 批判性审查，设计可选方案

**输出**:
```yaml
reimagine_output:
  options:
    - id: A
      name: "传统邮箱验证"
      approach: "自建邮件服务+验证码"
      pros:
        - "完全可控"
        - "无需第三方依赖"
      cons:
        - "开发周期长"
        - "邮件送达率难以保证"
      estimated_days: 5

    - id: B
      name: "第三方邮件服务"
      approach: "SendGrid/SES API发送邮件"
      pros:
        - "快速集成"
        - "送达率高"
      cons:
        - "增加成本"
        - "第三方依赖"
      estimated_days: 2

  recommendation:
    option_id: B
    reason: "MVP阶段快速验证更重要，第三方服务成熟稳定"
    cost: "$20/月（SendGrid免费额度100/天）"

  alternatives_considered:
    - "短信验证码: 成本高，用户体验差"
    - "社交登录: 增加开发复杂度，不符合当前需求"
```

### Phase 5: TRANSFORM

**目标**: 代码实施，遵循MVP优先

**原则**:
1. MVP先行: 先实现核心路径
2. TDD驱动: 红→绿→重构
3. 持续集成: 每阶段可运行

**输出**:
```bash
# 代码结构
src/
├── auth/
│   ├── models/
│   │   └── User.ts          # 用户模型
│   ├── routes/
│   │   └── register.ts      # 注册路由
│   ├── services/
│   │   ├── emailService.ts  # 邮件服务
│   │   └── tokenService.ts # Token服务
│   └── validators/
│       └── registerValidator.ts
├── tests/
│   └── auth/
│       └── register.test.ts
└── config/
    └── email.ts
```

### Phase 6: HARDEN

**目标**: 边界处理、错误处理、测试补全

**输出**:
```yaml
harden_output:
  edge_cases_handled:
    - name: "并发注册同一邮箱"
      solution: "数据库唯一索引+乐观锁"
      test: "TC007: 并发注册测试"

    - name: "验证码暴力破解"
      solution: "限流（5次/分钟）+图形验证码"
      test: "TC008: 限流测试"

    - name: "邮件发送超时"
      solution: "异步队列+重试机制"
      test: "TC009: 超时重试测试"

    - name: "激活链接被截获"
      solution: "一次性Token+HTTPS"
      test: "TC010: 安全测试"

  error_handling:
    - scenario: "数据库连接失败"
      response: "503 Service Unavailable"
      log_level: "error"

    - scenario: "邮件服务不可用"
      response: "降级: 保存到队列稍后重试"
      log_level: "warning"

  test_coverage:
    line_coverage: 85
    branch_coverage: 80
    critical_paths_covered: true
```

### Phase 7: VERIFY

**目标**: 验证通过，交付部署

**输出**:
```yaml
verify_output:
  test_results:
    unit_tests: 45/45 passed
    integration_tests: 12/12 passed
    e2e_tests: 6/6 passed

  code_quality:
    lint: PASS
    type_check: PASS
    coverage: 85%

  security_scan:
    vulnerability_scan: PASS
    dependency_audit: PASS

  deployment_checklist:
    - [x] 代码审查通过
    - [x] 测试全部通过
    - [x] 安全扫描通过
    - [x] 文档更新完成
    - [x] 监控告警配置
    - [x] 回滚方案就绪

  deployment_package:
    artifact: "auth-service-v1.0.0.tar.gz"
    image: "registry.example.com/auth:v1.0.0"
    rollout_strategy: "canary"
    health_check: "/health"
```

### 使用命令

```bash
# 完整流程
/feature-dev "用户注册功能"
/feature-dev --name "用户注册" --template api

# 单阶段执行
/feature-dev --phase discover "用户注册功能"
/feature-dev --phase plan
/feature-dev --phase brief
/feature-dev --phase reimagine
/feature-dev --phase transform
/feature-dev --phase harden
/feature-dev --phase verify

# 快速模式（跳过部分阶段）
/feature-dev "简单功能" --fast

# 指定模板
/feature-dev --template api         # API开发
/feature-dev --template frontend    # 前端开发
/feature-dev --template fullstack   # 全栈开发
```

### 与TDD协同

```
Phase 5: TRANSFORM
   ↓
   ┌─ 红: 写一个失败的测试
   ↓
   ┌─ 绿: 写最少的代码让它通过
   ↓
   └─ 重构: 改善代码但不改变行为
   ↓
Phase 6: HARDEN
   ↓
   补充边界测试和错误处理测试
```

## 天龙引擎协同

- **协同岗位**: 03构建师
- **天龙版本**: V8.73 → V9.0
- **天龙命令**: `[@03] 使用feature-dev流程开发这个功能`
- **预期收益**: 开发流程标准化+40%，质量可控性+60%
- **协同Skill**: tdd-workflow（Phase 5 TDD驱动）、emil-design-eng（前端美学）
