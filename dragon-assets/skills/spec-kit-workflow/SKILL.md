---
license: UNKNOWN
github_repo: github/spec-kit
github_hash: 232c19cb04f5ed26349295582a420fd0c71e0b21
last_updated: 2026-04-25
source_type: derived
triggers: ["spec kit workflow", "spec-kit-workflow Skill"]
---
# spec-kit-workflow Skill

> Spec-Driven Development (SDD) 工作流集成 - 天龙引擎V8.62新增

## 核心价值

封装 GitHub/spec-kit 6步SDD工作流，与天龙引擎现有能力形成互补：

| spec-kit优势 | 天龙现有能力 | 协同效果 |
|-------------|-------------|---------|
| 规范直接生成代码 | PM Skills PRD模板 | 质的飞跃 |
| 9条治理规则(Constitution) | 批判性思维 | 架构决策规范化 |
| 规范-实现漂移检测 | lessons.md | 一致性保障 |
| 33+扩展生态 | 400+ Skills | 生态互补 |

## 6步SDD工作流

```
┌─────────────────────────────────────────────────────────────┐
│                 Spec-Driven Development                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Step 1: Constitution (宪法) ⭐                            │
│  ├── 定义项目原则和约束                                     │
│  └── 9条治理规则（天龙新增）                               │
│                                                             │
│  Step 2: Specify (规范定义) ⭐                             │
│  ├── 用户场景和测试                                        │
│  ├── 功能需求 (FR-001, FR-002...)                         │
│  └── 边界条件                                              │
│                                                             │
│  Step 3: Plan (技术规划) ⭐                                │
│  ├── 技术架构设计                                          │
│  └── 技术选型理由                                          │
│                                                             │
│  Step 4: Tasks (任务分解)                                  │
│  ├── 可执行任务列表                                        │
│  └── 依赖关系管理                                          │
│                                                             │
│  Step 5: Implement (代码实现)                              │
│  └── Test-First: 先写测试                                 │
│                                                             │
│  Step 6: Refine (持续优化)                                 │
│  └── 生产指标更新规范                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 核心命令

### 1. Constitution (宪法创建)

```bash
# 创建项目宪法
python3 ~/.claude/skills/spec-kit-workflow/scripts/sync_checker.py constitution --name "项目名称" --output ./CONSTITUTION.md

# 使用自定义原则
python3 ~/.claude/skills/spec-kit-workflow/scripts/sync_checker.py constitution --name "项目名称" --principles "Library-First" "CLI Interface" "Test-First"
```

**天龙增强**: 02架构师自动生成9条治理规则

### 2. Specify (规范定义)

```bash
# 生成功能规范模板
python3 ~/.claude/skills/spec-kit-workflow/scripts/sync_checker.py specify --name "功能名称" --output ./SPEC.md

# 带用户故事
python3 ~/.claude/skills/spec-kit-workflow/scripts/sync_checker.py specify --name "登录功能" --user-story "用户需要安全登录系统" --output ./SPEC.md
```

**天龙增强**: 01调研师自动关联specify模板

### 3. Plan (技术规划)

```bash
# 生成技术规划
python3 ~/.claude/skills/spec-kit-workflow/scripts/sync_checker.py plan --name "项目名称" --output ./PLAN.md

# 关联规范文件
python3 ~/.claude/skills/spec-kit-workflow/scripts/sync_checker.py plan --name "项目名称" --spec ./SPEC.md --tech-stack "Python/React" --output ./PLAN.md
```

**天龙增强**: 02架构师自动关联第一性原理

### 4. Tasks (任务分解)

```bash
# 从规范文件生成任务列表
python3 ~/.claude/skills/spec-kit-workflow/scripts/sync_checker.py tasks --spec ./SPEC.md --output ./TASKS.md

# 设置并行度
python3 ~/.claude/skills/spec-kit-workflow/scripts/sync_checker.py tasks --spec ./SPEC.md --parallel 5 --output ./TASKS.md
```

### 5. Sync (规范-实现漂移检测)

```bash
# 检查规范-实现一致性
python3 ~/.claude/skills/spec-kit-workflow/scripts/sync_checker.py sync --spec ./SPEC.md --impl ./src
```

## 与天龙引擎岗位协同

### 02架构师 协同

```
天龙架构师 → spec-kit Constitution → 架构决策规范化
     ↓
天龙架构师 → spec-kit Plan → 技术选型文档化
     ↓
天龙架构师 → spec-kit v-model → 测试追溯
```

### 01调研师 协同

```
天龙调研师 → spec-kit Specify → 需求清晰化
     ↓
天龙调研师 → spec-kit understanding → 31维度需求分析
     ↓
天龙调研师 → spec-kit clarify → 需求澄清
```

### 09-02编排协调师 协同

```
天龙编排师 → spec-kit fleet → 全流程编排
     ↓
天龙编排师 → spec-kit MAQA → Multi-Agent QA协调
     ↓
天龙编排师 → spec-kit iterate → 规范迭代
```

## 天龙增强点

### 1. Constitution增强：9条治理规则

```markdown
## 天龙架构师Constitution模板

1. **Library-First**: 每个功能先做独立库
2. **CLI Interface**: 所有功能必须有CLI接口
3. **Test-First**: 任何实现必须先有测试
4. **Single Source of Truth**: 规范是唯一的真相
5. **Drift Detection**: 规范-实现漂移必须检测
6. **Incremental Compliance**: 渐进式符合规范
7. **Human-in-the-Loop**: 关键决策必须人工确认
8. **Agent-Agnostic**: 支持26种AI Agent
9. **Observable**: 所有操作必须可观测
```

### 2. Specify增强：天龙调研模板

```markdown
## 天龙Specify扩展

### 用户场景
- 用户画像
- 使用环境
- 痛点分析

### 功能需求 (FR-XXX)
- 需求ID
- 需求描述
- 优先级
- 验收标准

### 天龙增强
- 关联deep-research调研报告
- 关联LightRAG知识库
- 关联Cat-Research来源验证
```

## 安装与配置

### 前置条件

```bash
# 安装specify CLI
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@v0.4.3

# 验证安装
specify --version
```

### 天龙引擎配置

在 `~/.claude/skills/spec-kit-workflow/config.yaml` 配置：

```yaml
specify_path: ~/.specify
default_ai: claude
constitution_template:天龙-constitution-template.md
extensions_enabled:
  - understanding
  - verify
  - onboard
```

## 与现有Skills协同

| 现有Skill | 协同方式 |
|---------|---------|
| **pm-skills** | PRD → Specify规范转换 |
| **deep-research** | 调研 → Specify用户场景 |
| **lightrag-knowledge-base** | 知识库 → Specify背景 |
| **cat-research** | 来源验证 → Specify置信度 |
| **crewai-orchestration** | 多Agent → spec-kit fleet |
| **langflow-workflow-designer** | 可视化 → spec-kit plan |

## 预期收益

| 指标 | V8.61 | V8.62 | 提升 |
|------|-------|-------|------|
| **架构决策规范化** | 部分 | 完整 | +60% |
| **需求清晰度** | 模糊 | 清晰 | +50% |
| **规范-实现一致性** | 无 | 漂移检测 | 质的飞跃 |
| **多Agent编排** | 基础 | fleet+MAQA | +40% |

## 文件结构

```
~/.claude/skills/spec-kit-workflow/
├── SKILL.md                           # 本文件
├── config.yaml                        # 配置文件
├── scripts/
│   ├── constitution_generator.py       # 宪法生成器
│   ├── specify_generator.py           # 规范生成器
│   ├── plan_generator.py              # 规划生成器
│   ├── tasks_generator.py             # 任务分解器
│   └── sync_checker.py                # 漂移检测器
└── templates/
    ├── 天龙-constitution-template.md   # 天龙增强宪法模板
    ├── 天龙-spec-template.md           # 天龙增强规范模板
    └── 天龙-plan-template.md           # 天龙增强规划模板
```

## 参考资料

- [spec-kit官方仓库](https://github.com/github/spec-kit)
- [SDD方法论文档](https://github.com/github/spec-kit/blob/main/spec-driven.md)
- [扩展目录](https://github.com/github/spec-kit/blob/main/extensions/catalog.community.json)
