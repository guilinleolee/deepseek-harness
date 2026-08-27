---
license: UNKNOWN
name: context-engineering
description: 上下文工程核心技能，整合压缩优化、渐进披露、多Agent模式、评估框架四大能力
github_repo: muratcankoylan/agent-skills-for-context-engineering
github_hash: 7a95d94c364e25c869a86896a45791dfda6db8bf
last_updated: 2026-04-25
source_type: derived
version: 1.0.0
source: https://github.com/muratcankoylan/agent-skills-for-context-engineering
triggers: ["context engineering", "Context Engineering for AI Agents"]
---

# Context Engineering for AI Agents

> 来源: [agent-skills-for-context-engineering](https://github.com/muratcankoylan/agent-skills-for-context-engineering) - 14.4k Stars

## 核心能力矩阵

```
┌─────────────────────────────────────────────────────────────┐
│ 上下文工程四大核心能力                                        │
├─────────────────────────────────────────────────────────────┤
│ 1. Context Compression    - 压缩优化，Token节省30-50%        │
│ 2. Progressive Disclosure - 渐进披露，上下文效率+40%         │
│ 3. Multi-Agent Patterns   - 多Agent模式，上下文隔离          │
│ 4. Evaluation Frameworks  - 评估框架，质量保证               │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Context Compression（上下文压缩）

### 核心概念

| 概念 | 说明 | Token节省 |
|------|------|----------|
| **损失无关压缩** | 移除不影响输出的冗余内容 | 20-30% |
| **损失有损压缩** | 通过摘要/抽象减少信息量 | 30-50% |
| **渐进式压缩** | 根据上下文压力动态调整压缩级别 | 可变 |

### 压缩策略优先级

```yaml
策略1 - 观察掩码（优先级最高）:
  操作: 替换verbose工具输出为紧凑引用
  示例: "工具输出已保存到 /tmp/output.txt，包含150行数据"
  效果: Token节省50-80%

策略2 - 摘要压缩:
  操作: 对累积上下文进行summarization
  示例: "前10轮对话已压缩为摘要：用户要求实现X功能，已讨论A、B、C方案"
  效果: Token节省60-70%

策略3 - 上下文分区:
  操作: 将工作分散到sub-agents
  示例: 拆分为独立子任务，每个sub-agent获得新鲜context window
  效果: 防止上下文降级
```

### 触发条件

```yaml
自动触发:
  - 上下文利用率 > 70%
  - 检测到注意力降级迹象（重复提问、遗漏中间信息）
  - 成本优化需求

手动触发:
  - /compress-context
  - "优化上下文"
  - "减少token"
```

### 压缩执行流程

```
1. 测量当前Token使用
   ↓
2. 识别可压缩内容（工具输出 > 文档 > 对话）
   ↓
3. 选择压缩策略（优先无损压缩）
   ↓
4. 执行压缩（保留关键决策点）
   ↓
5. 验证压缩效果（目标：50-70%减少，质量损失<5%）
```

### 最佳实践

```yaml
1. 压缩前先测量:
   - 记录当前token使用量
   - 识别token消耗大户（通常是工具输出）

2. 优先压缩工具输出:
   - 工具输出占tokens的80%+
   - 替换为摘要+文件引用

3. 保留系统提示:
   - 系统提示锚定模型行为
   - 不压缩核心指令

4. 边缘放置关键信息:
   - U型注意力曲线：开头和结尾召回率最高
   - 关键决策放在边缘位置

5. 目标设定:
   - Token减少: 50-70%
   - 质量损失: <5%
```

---

## 2. Progressive Disclosure（渐进式披露）

### 三级披露架构

```yaml
Level 1 - 技能选择级:
  启动时加载: 名称 + 描述
  按需加载: 完整技能内容
  示例:
    静态上下文: "database-optimization: Query tuning and indexing strategies"
    动态加载: read_file("skills/database-optimization/SKILL.md")

Level 2 - 文档加载级:
  首次加载: 摘要（前100字）
  任务需要时: 详情章节
  示例:
    摘要: "API设计最佳实践"
    详情: "RESTful命名规范、分页策略、错误处理..."

Level 3 - 工具结果保留级:
  保留: 最近3-5次结果（完整）
  压缩/驱逐: 较旧结果
  示例:
    完整保留: 最近一次文件读取
    压缩: 之前的读取结果 → 文件路径摘要
```

### 实现模式

```markdown
# 静态上下文（最小化启动负载）
Available skills (load with read_file when relevant):
- database-optimization: Query tuning and indexing strategies
- api-design: REST/GraphQL best practices
- testing-strategies: Unit, integration, and e2e testing patterns

# 动态加载（任务触发时）
当任务需要数据库优化 → read_file("skills/database-optimization/SKILL.md")
```

### 关键原则

```yaml
1. 边界清晰:
   技能激活时: 完全加载，而非部分加载
   避免: 激活但只加载一半内容

2. 严格激活阈值:
   触发条件: 任务明确匹配技能描述
   避免: "可能相关"就加载

3. 避免急切加载:
   错误: 启动时预加载所有技能
   正确: 零启动负载，按需加载
```

### 预期收益

| 指标 | 无渐进披露 | 有渐进披露 | 提升 |
|------|----------|----------|------|
| **启动Token** | 10000+ | 500-1000 | **-90%** |
| **平均上下文** | 8000 | 4000-5000 | **-40%** |
| **响应延迟** | 高 | 低 | **-30%** |

---

## 3. Multi-Agent Patterns（多Agent模式）

### 架构模式对比

| 模式 | 适用场景 | 上下文隔离 | 协调开销 | 推荐度 |
|------|---------|----------|---------|--------|
| **单Agent管道** | 默认选择，简单任务 | 无 | 无 | ⭐⭐⭐⭐⭐ |
| **Supervisor** | 复杂任务分解、动态分配 | 高 | 中 | ⭐⭐⭐⭐ |
| **Sequential** | 线性工作流、依赖任务 | 中 | 低 | ⭐⭐⭐⭐ |
| **Parallel** | 独立子任务、速度优先 | 高 | 中 | ⭐⭐⭐⭐ |

### 升级到多Agent的决策树

```
默认选择: 单Agent管道
    │
    ├─ 需要并行探索不同方面？ ──→ Parallel模式
    │
    ├─ 任务超过单个context window？ ──→ Sequential + 文件系统通信
    │
    ├─ 专业sub-agents在基准测试中证明有效？ ──→ Supervisor模式
    │
    └─ 否 ──→ 保持单Agent管道
```

### 核心设计原则

```yaml
原则1 - 上下文隔离 > 角色拟人化:
  正确理由: Sub-agents获得新鲜的context windows
  错误理由: 给Agent分配人类角色（如"产品经理Agent"）

原则2 - 文件系统通信 > 消息传递链:
  推荐: 每个agent写入独立目录 → 协调器直接读取
  避免: Agent1 → Agent2 → Agent3（每跳summarization丢失细节）

原则3 - 防止长时间运行任务的上下文降级:
  问题: 单Agent长时间运行 → 上下文降级
  解决: Checkpoint → 新鲜Agent → 结果汇总
```

### 信息传递模式

```yaml
推荐 - 文件系统工作空间:
  结构:
    /workspace/
      ├── agent1/
      │   └── output.json
      ├── agent2/
      │   └── output.json
      └── coordinator/
          └── merged_result.json

  优点:
    - 无信息衰减
    - 可追溯
    - 支持并行写入

避免 - 消息传递链:
  结构: Agent1 → summarize → Agent2 → summarize → Agent3

  问题:
    - "电话游戏"效应
    - 每跳丢失10-30%细节
    - 最终结果可能偏离原始意图
```

### 与天龙引擎协同

| 天龙组件 | Multi-Agent Pattern | 协同效果 |
|---------|---------------------|---------|
| **09-02 编排协调师** | Supervisor模式 | 端到端任务编排 |
| **Fresh Subagent** | Sequential模式 | 上下文隔离 |
| **Parallel Dispatch** | Parallel模式 | 并行加速 |
| **V7.4 魔鬼代言人** | 双线协作 | 质疑+主线并行 |

---

## 4. Evaluation Frameworks（评估框架）

### 评估维度矩阵

| 维度 | 指标 | 测量方法 | 权重 |
|------|------|---------|------|
| **任务完成** | 成功率、错误率 | 自动化测试 | 30% |
| **输出质量** | 准确性、相关性 | LLM-as-judge | 25% |
| **效率** | Token消耗、延迟 | 系统监控 | 20% |
| **鲁棒性** | 错误恢复率 | 故障注入 | 15% |
| **可维护性** | 代码质量、文档完整性 | 静态分析 | 10% |

### 评估技术栈

```yaml
生产评估:
  LLM-as-Judge:
    - 优点: 可扩展、一致性好
    - 缺点: 可能有偏见
    - 最佳实践: 使用多个judge模型
    - 推荐模型: Claude Haiku (快速), GPT-4o (高质量)

  人工评估:
    - 优点: 最高质量
    - 缺点: 成本高、不可扩展
    - 用途: 金标准建立、边界案例

  自动化评估:
    - 优点: 快速、可重复
    - 缺点: 覆盖有限
    - 用途: 回归测试、CI/CD
```

### 高级评估技术

```yaml
代码评估:
  - 单元测试覆盖率
  - 静态分析（ESLint, PyLint）
  - 安全扫描（Semgrep, CodeQL）
  - 复杂度分析（圈复杂度）

行为评估:
  - 轨迹分析（Agent决策路径）
  - 工具使用模式（频率、顺序、效果）
  - 决策质量（正确率、回退率）

上下文评估:
  - Token效率（输出/输入比）
  - 注意力分布（U型曲线验证）
  - 信息密度（有用信息/总token）
```

### 评估工作流

```
1. 定义评估目标
   ↓
2. 选择评估方法（LLM-as-Judge / 人工 / 自动化）
   ↓
3. 构建评估数据集（金标准 + 边界案例）
   ↓
4. 执行评估
   ↓
5. 分析结果（识别薄弱环节）
   ↓
6. 迭代改进
```

---

## 5. Context Degradation Detection（上下文降级检测）

### 五大降级模式

| 模式 | 症状 | 缓解策略 |
|------|------|---------|
| **Lost-in-Middle** | 忽略中间信息 | 边缘放置关键信息 |
| **Poisoning** | 错误信息传播 | 验证输入、截断恢复 |
| **Distraction** | 注意力稀释 | 相关性过滤 |
| **Confusion** | 任务交叉污染 | 任务隔离 |
| **Clash** | 矛盾信息冲突 | 优先级规则 |

### 检测方法

```yaml
1. Lost-in-Middle检测:
   方法: 在中间位置插入验证问题
   症状: Agent无法回答中间位置的信息
   缓解: 将关键信息移至开头或结尾

2. Poisoning检测:
   方法: 监控错误信息的传播路径
   症状: 错误信息被重复引用
   缓解: 输入验证、事实核查

3. Distraction检测:
   方法: 分析注意力分布
   症状: Agent关注无关信息
   缓解: 相关性过滤、压缩冗余

4. Confusion检测:
   方法: 检查任务切换频率
   症状: Agent频繁切换任务
   缓解: 任务隔离、清晰边界

5. Clash检测:
   方法: 识别矛盾信息对
   症状: Agent表现出不确定或矛盾输出
   缓解: 优先级规则、来源标记
```

---

## 6. 与天龙引擎集成

### 技能映射

| 天龙岗位 | Context Engineering能力 | 升级价值 |
|----------|------------------------|---------|
| **01 调研师** | Context Compression + Progressive Disclosure | ⭐⭐⭐⭐⭐ |
| **02 架构师** | Multi-Agent Patterns + Evaluation | ⭐⭐⭐⭐⭐ |
| **04 验证师** | Evaluation Frameworks | ⭐⭐⭐⭐⭐ |
| **09-02 编排协调师** | Multi-Agent Patterns | ⭐⭐⭐⭐⭐ |

### 命令集成

```bash
# 上下文压缩
/compress-context              # 手动触发压缩
/context-stats                 # 查看上下文统计

# 渐进式披露
/skill-list                    # 列出可用技能（名称+描述）
/skill-load <name>             # 加载完整技能内容

# 多Agent模式
/multi-agent --mode parallel   # 并行模式
/multi-agent --mode sequential # 顺序模式
/multi-agent --mode supervisor # 监督模式

# 评估框架
/evaluate-agent <agent-id>     # 评估Agent
/eval-report                   # 生成评估报告
```

---

## 7. 预期收益

| 指标 | 集成前 | 集成后 | 提升 |
|------|--------|--------|------|
| **Token效率** | 基准 | +50% | ⭐⭐⭐⭐⭐ |
| **上下文利用率** | 60% | 85% | +42% |
| **任务完成率** | 基准 | +15% | ⭐⭐⭐⭐ |
| **质量一致性** | 基准 | +25% | ⭐⭐⭐⭐ |

---

## 8. 参考资料

- [Context Fundamentals](https://github.com/muratcankoylan/agent-skills-for-context-engineering/blob/main/skills/context-fundamentals/SKILL.md)
- [Context Compression](https://github.com/muratcankoylan/agent-skills-for-context-engineering/blob/main/skills/context-compression/SKILL.md)
- [Multi-Agent Patterns](https://github.com/muratcankoylan/agent-skills-for-context-engineering/blob/main/skills/multi-agent-patterns/SKILL.md)
- [Evaluation Frameworks](https://github.com/muratcankoylan/agent-skills-for-context-engineering/blob/main/skills/evaluation/SKILL.md)