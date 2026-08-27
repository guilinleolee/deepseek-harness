---
license: UNKNOWN
github_repo: gsd-build/get-shit-done
github_hash: a72bebb3791f5c5d3294683223d35182deed9388
last_updated: 2026-04-25
source_type: derived
triggers: ["gsd dragon bridge", "GSD-Dragon Bridge 技能"]
---
# GSD-Dragon Bridge 技能

> 规范驱动开发 × 天龙引擎 = 上下文永不丢失

## 核心价值

将GSD（Get-Shit-Done，42.7k Stars）的规范驱动开发文件体系与天龙引擎深度融合，解决"上下文衰减"问题。

## 文件体系映射

```
GSD                      天龙引擎                  融合命令
────────────────────────────────────────────────────────────────
.planning/PROJECT.md   ↔ CLAUDE.md              → /gsd:sync-project
.planning/STATE.md     ↔ lessons.md             → /gsd:sync-state
.planning/ROADMAP.md   ↔ plans/                 → /gsd:sync-roadmap
.planning/REQUIREMENTS.md ↔ 需求分析输出         → /gsd:sync-requirements
phases/*-PLAN.md       ↔ Plan Mode输出          → /gsd:plan-to-dragon
phases/*-SUMMARY.md    ↔ 记录师输出             → /gsd:summary-to-dragon
phases/*-VERIFICATION.md ↔ 验证师输出           → /gsd:verify-to-dragon
```

## 核心命令

### 文件同步命令

```bash
# 双向同步
/gsd:sync-all                    # 同步所有文件

# 单向同步
/gsd:sync-project                # PROJECT.md → CLAUDE.md
/gsd:sync-state                  # STATE.md ↔ lessons.md（双向）
/gsd:sync-roadmap                # ROADMAP.md → plans/
/gsd:sync-requirements           # REQUIREMENTS.md → 需求分析
```

### 格式转换命令

```bash
# GSD → 天龙
/gsd:plan-to-dragon              # PLAN.md → 天龙Plan格式
/gsd:summary-to-dragon           # SUMMARY.md → 天龙总结格式
/gsd:verify-to-dragon            # VERIFICATION.md → 天龙验证格式

# 天龙 → GSD
/gsd:dragon-to-plan              # 天龙Plan → PLAN.md
/gsd:dragon-to-summary           # 天龙总结 → SUMMARY.md
/gsd:dragon-to-verify            # 天龙验证 → VERIFICATION.md
```

### 状态追踪命令

```bash
/gsd:status                      # 查看当前项目状态
/gsd:progress                    # 查看进度
/gsd:decisions                   # 查看决策历史
/gsd:blockers                    # 查看阻塞项
```

## 与天龙岗位协同

| 天龙岗位 | GSD协同 | 协同方式 |
|---------|---------|---------|
| **00分析师** | gsd-researcher | 使用GSD文件体系记录分析结果 |
| **01调研师** | gsd-codebase-mapper | 棕地项目映射 → PROJECT.md |
| **02架构师** | gsd-planner | 计划输出 → PLAN.md |
| **03构建师** | gsd-executor | 执行偏差 → STATE.md |
| **04验证师** | gsd-verifier | 验证结果 → VERIFICATION.md |
| **06审查师** | gsd-nyquist-auditor | 审查结果 → SUMMARY.md |
| **07记录师** | - | 总结输出 → SUMMARY.md |
| **08发布师** | - | 发布记录 → ROADMAP.md |

## 偏差处理规则集成

GSD的4条偏差规则已集成到天龙Hooks系统：

| 规则 | 触发条件 | 自动处理 | Hook实现 |
|------|---------|---------|---------|
| **Rule 1** | 代码不按预期工作 | 自动修复Bug | gsd-deviation-handler.js |
| **Rule 2** | 缺少关键功能 | 自动添加 | gsd-deviation-handler.js |
| **Rule 3** | 阻塞问题 | 自动修复 | gsd-deviation-handler.js |
| **Rule 4** | 架构变更需求 | 停止并询问用户 | gsd-deviation-handler.js |

## 使用示例

### 新项目初始化

```bash
# 使用GSD工作流初始化
/gsd:new-project

# 自动创建天龙兼容文件
# ├── .planning/
# │   ├── PROJECT.md → 同步到 CLAUDE.md
# │   ├── STATE.md → 同步到 lessons.md
# │   ├── ROADMAP.md → 同步到 plans/
# │   └── REQUIREMENTS.md
```

### 阶段执行

```bash
# GSD五阶段工作流
/gsd:discuss-phase    # 需求讨论 → 00分析师
/gsd:plan-phase       # 阶段规划 → 02架构师
/gsd:execute-phase    # 阶段执行 → 03构建师（偏差自动处理）
/gsd:verify-work      # 工作验证 → 04验证师
/gsd:ship            # 发布 → 08发布师
```

### 状态同步

```bash
# 查看当前状态
/gsd:status

# 输出示例：
# 📊 项目状态: 开发中
# 📍 当前位置: Phase 2 - Plan 3
# ✅ 已完成: 12/20 任务 (60%)
# ⚠️ 阻塞项: 2
# 📝 决策数: 8
```

## 文件模板

### STATE.md 模板

```markdown
# Project State

## Current Position
- **Phase**: 02-implementation
- **Plan**: 03-auth-system
- **Task**: 2/5

## Progress
```
[████████░░░░░░░░░░] 40%
```

## Decisions
| Date | Decision | Rationale | Impact |
|------|----------|-----------|--------|
| 2026-03-27 | 使用JWT认证 | 安全性要求高 | Phase 2 |

## Blockers
| ID | Description | Since | Status |
|----|-------------|-------|--------|
| B001 | 等待API密钥 | 2026-03-27 | pending |

## Session Info
- **Last Session**: 2026-03-27T14:30:00Z
- **Stopped At**: Task 2 - 实现登录组件
```

### PLAN.md 模板

```markdown
---
phase: "02"
plan: "03"
type: "implementation"
autonomous: true
wave: 2
depends_on: ["02-02"]
must_haves:
  truths:
    - "用户可以使用邮箱和密码登录"
  artifacts:
    - "登录组件"
    - "认证API"
  key_links:
    - "前端 → 后端API"
    - "后端 → 数据库"
---

# Phase 2 Plan 3: 用户认证系统

## Objective
实现完整的用户认证流程，包括登录、注册、密码重置。

## Context
@./CONTEXT.md
@./REQUIREMENTS.md

## Tasks

### Task 1: 创建认证API (type="auto", tdd="true")
<behavior>
POST /api/auth/login
- 接收 email, password
- 返回 JWT token
- 错误处理: 401, 429
</behavior>
<implementation>
使用 jose 库生成 JWT
实现 refresh token 机制
</implementation>

### Task 2: 实现登录组件 (type="auto")
...

## Verification
- [ ] 单元测试覆盖率 > 80%
- [ ] E2E测试通过
- [ ] 安全审计通过

## Success Criteria
- 用户可以登录
- JWT有效期为1小时
- Refresh token有效期为7天
```

## 预期收益

| 指标 | 集成前 | 集成后 | 提升 |
|------|--------|--------|------|
| **上下文持久化** | 部分 | 完整 | **+100%** |
| **跨会话可追溯** | 低 | 高 | **+200%** |
| **偏差自动处理** | 手动 | 自动 | **+300%** |
| **进度可视化** | 基础 | 完整 | **+150%** |

## 相关技能

- [systematic-debugging](../systematic-debugging/) - GSD调试方法融合
- [tdd-workflow](../tdd-workflow/) - TDD工作流融合
- [planning-with-files](../planning-with-files/) - 文件持久化

## 参考资料

- [GSD官方文档](https://github.com/gsd-build/get-shit-done)
- [分析报告](../../analysis/GSD_INTEGRATION_ANALYSIS_REPORT.md)