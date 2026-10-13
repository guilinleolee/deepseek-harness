---
name: nine-dragons-check
description: 九部天龙健康检查 - 检测agents/skills/commands配置完整性并提供修复建议
invokable: true
---
# 九部天龙健康检查

> V3.3环境诊断工具 - 一键检测九部天龙配置完整性

## 📋 检查清单

请依次执行以下检查项，并生成完整报告：

### 1. 核心配置文件检查

检查以下文件是否存在：

```bash
# 核心配置
✅ CLAUDE.md - 九部天龙核心引擎
✅ rules/comments.md - 代码注释规范

# Agents目录
✅ agents/00-analyst.md - 00分析师
✅ agents/01-investigator.md - 01调研师
✅ agents/02-architect.md - 02架构师
✅ agents/03-builder.md - 03构建师
✅ agents/04-validator.md - 04验证师
✅ agents/05-security-reviewer.md - 05安全师
✅ agents/06code-reviewer.md - 06审查师
✅ agents/07-scribe.md - 07记录师
✅ agents/08-publisher.md - 08发布师

# V3.3新增
⚠️  agents/09-vision-ai.md - 09视觉师（可选）

# Commands目录
✅ commands/nine-dragons-help.md - 智能助手
✅ commands/nine-dragons-check.md - 健康检查（本文件）
⚠️  commands/nine-dragons-cost-opt.md - 成本优化（P1任务）
⚠️  commands/nine-dragons-ui2code.md - UI转代码（P2任务）

# Docs目录
✅ docs/nine-dragons-optimization-summary.md - 优化路线图
✅ docs/agent-team-communication.md - 通信协议
✅ docs/skill-discovery-mechanism.md - Skill发现机制
```

### 2. Skills CLI检查

检查Skills CLI是否可用：

```bash
# 检查find-skills
npx skills --version 2>&1

# 预期输出：skills-cli version x.x.x
# 如果失败 → 提示用户安装：npm install -g @anthropic-ai/skills-cli
```

### 3. 文件持久化机制检查

检查三个核心文件是否存在：

```bash
# 检查持久化文件
ls -la task_plan.md findings.md progress.md 2>&1

# 如果不存在 → 提示用户执行 /planning-with-files
```

### 4. Agent配置完整性检查

读取每个agent文件，验证：
- ✅ 文件存在且可读
- ✅ 包含核心职责章节
- ✅ 包含专属约束
- ✅ 包含输出标准

### 5. Skill回退链检查

验证00分析师的Skill回退链配置：
- ✅ 本地Skill扫描步骤
- ✅ 外部Skill搜索步骤
- ✅ 通用Subagent回退步骤

## 📊 检查报告格式

请生成以下格式的报告：

```markdown
# 九部天龙健康检查报告

**检查时间**：2026-02-19 [当前时间]
**版本**：V3.3

---

## 📈 总体评分

- **配置完整性**：✅ 95% (19/20)
- **核心功能**：✅ 100% (9/9)
- **可选功能**：⚠️  50% (1/2)
- **建议优先级**：🟡 中等

---

## ✅ 正常项

### 核心配置文件
- ✅ CLAUDE.md 存在且完整
- ✅ rules/comments.md 存在
- ✅ 9个核心agent配置文件全部存在

### Agents配置
- ✅ 00分析师 - 包含成本感知机制（V3.3新增）
- ✅ 01调研师 - 配置完整
- ✅ 02架构师 - 配置完整
- ✅ 03构建师 - 配置完整
- ✅ 04验证师 - 配置完整
- ✅ 05安全师 - 配置完整
- ✅ 06审查师 - 配置完整
- ✅ 07记录师 - 配置完整
- ✅ 08发布师 - 配置完整

### Commands
- ✅ /nine-dragons-help - 智能助手命令可用
- ✅ /nine-dragons-check - 健康检查命令可用（本命令）

### 文档
- ✅ docs/nine-dragons-optimization-summary.md 存在
- ✅ docs/agent-team-communication.md 存在
- ✅ docs/skill-discovery-mechanism.md 存在

---

## ⚠️ 警告项

### V3.3新增功能（可选）

#### 1. 09视觉师未配置
**状态**：⚠️ 缺失（可选）
**影响**：无法使用UI转代码功能
**修复**：
```bash
# 执行P1-1任务创建09视觉师
# 或等待V3.3完整升级完成
```

#### 2. 成本优化命令未创建
**状态**：⚠️ 缺失（P1任务）
**影响**：无法使用成本优化模式
**修复**：
```bash
# 执行P1-3任务创建命令
# 或手动创建 commands/nine-dragons-cost-opt.md
```

#### 3. UI2Code命令未创建
**状态**：⚠️ 缺失（P2任务）
**影响**：无法使用设计稿转代码功能
**修复**：
```bash
# 执行P2-2任务创建命令
# 或手动创建 commands/nine-dragons-ui2code.md
```

---

## 🔧 修复建议

### 立即修复（影响核心功能）
无

### 建议修复（增强功能）
1. **完成P1任务**：创建09视觉师和成本优化命令
2. **完成P2任务**：创建UI2Code完整流程
3. **更新CLAUDE.md**：添加V3.3新特性说明

### 可选优化
1. 配置外部MCP Servers（Codex/Gemini）
2. 安装Skills CLI（find-skills功能）
3. 配置conversationId共享记忆机制

---

## 🚀 快速修复命令

根据检测结果，推荐执行以下命令：

| 需求 | 命令 | 说明 |
|------|------|------|
| 创建持久化文件 | Skill(skill="planning-with-files") | 初始化三大核心文件 |
| 查找Skill | npx skills search <关键词> | 搜索外部Skills |
| 安装Skills CLI | npm install -g @anthropic-ai/skills-cli | 安装Skill管理工具 |
| 升级到V3.3 | （等待P0-P2任务完成） | 完整升级流程 |

---

## 📋 检查详情

### 文件完整性
```
核心配置:       2/2   ✅
Agents配置:     9/9   ✅
Commands:       2/5   ⚠️  (缺3个V3.3新命令)
文档:           3/3   ✅
总计:          16/19  84%
```

### 功能完整性
```
场景路由:       ✅ 可用
成本感知:       ✅ 已配置（V3.3新增）
命令决策树:     ✅ 可用
健康检查:       ✅ 可用（本命令）
09视觉师:       ⚠️  未配置（可选）
成本优化:       ⚠️  未配置（P1）
UI2Code:        ⚠️  未配置（P2）
```

---

## 💡 下一步操作

1. **如果一切正常**：可以开始使用九部天龙
   - 推荐：先运行 `/nine-dragons-help "你的任务"` 了解执行路径

2. **如果有警告项**：根据优先级修复
   - 高优先级：影响核心功能的项
   - 中优先级：V3.3新功能（可选）
   - 低优先级：锦上添花的功能

3. **如果想完整升级**：继续执行P0-P2任务
   - P0已完成 ✅
   - P1进行中 🔄
   - P2待开始 ⏳

---

## 相关文档

- [CLAUDE.md](../CLAUDE.md) - 九部天龙核心引擎
- [task_plan.md](../task_plan.md) - 当前任务计划
- [docs/nine-dragons-optimization-summary.md](../docs/nine-dragons-optimization-summary.md) - 优化路线图
