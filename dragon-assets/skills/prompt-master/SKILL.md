---
license: UNKNOWN
name: prompt-master
version: 1.0.0
description: |
专业提示词工程系统，提供结构化模板库、智能路由和深度优化能力。

基于顶级框架（CO-STAR, CREATE, APE）和质量标准，通过10+验证模板提升LLM输出质量。

## 核心功能
- 问题解构、系统设计、代码重构
- 文档生成、调试分析、需求分析
- 测试设计、代码审查、技术选型、性能优化

触发词：提词、prompt、提示词工程
author: 天龙引擎团队
created: 2026-02-26
category: ai

triggers:
  - "用户说「帮我写个prompt」时"
  - "用户说「优化提示词」时"
  - "需要结构化提示词时"
---

# 提词师 (Prompt Master) - 专业提示词工程技能

## 技能描述

专业级提示词工程系统，提供结构化模板库、智能路由和深度优化能力。基于顶级框架（CO-STAR, CREATE, APE）和质量标准，通过10+验证模板提升LLM输出质量。

## 核心功能

### P0 - 核心模板库（开箱即用）
- **问题解构**: 复杂任务结构化分解
- **系统设计**: 技术方案架构设计
- **代码重构**: 代码质量提升和优化
- **文档生成**: 技术文档标准化生成
- **调试分析**: 系统化问题诊断
- **需求分析**: 用户需求到技术规格
- **测试设计**: 测试用例生成
- **代码审查**: 代码质量审计
- **技术选型**: 技术栈决策
- **性能优化**: 系统性能提升

### P1 - 质量增强
- Few-Shot示例管理
- 5维度质量评估（清晰度、完整性、可操作性、一致性、效率）
- 结构化输出解析
- A/B测试建议

### P2 - 高级功能
- CoT（思维链）模板
- Chaining（链式调用）模板
- 效果追踪（指标记录）
- 团队协作（共享模板）

## 使用方法

### 方式1: 直接调用模板（推荐新手）

```bash
# 快速开始
/prompt-master 问题解构
/prompt-master 系统设计
/prompt-master 代码审查

# 查看所有模板
/prompt-master --list
```

### 方式2: 交互式选择（推荐专家）

```bash
/prompt-master
# → 交互式选择模板类型
# → 输入具体任务
# → 自动渲染优化后的提示词
```

### 方式3: 深度优化（推荐复杂任务）

```bash
/prompt-master --deep
# → 调用 prompt-architect subagent
# → 深度分析+优化+质量审计
```

## 技术原理

### 模板架构
- **YAML Frontmatter**: 元数据（框架、评分、标签）
- **Jinja2渲染**: 变量插值和逻辑控制
- **Markdown格式**: 可读性和版本控制友好

### 质量标准
- **清晰度**: 无歧义、无冗余
- **完整性**: 覆盖所有必要要素
- **可操作性**: 可直接执行
- **一致性**: 术语和风格统一
- **效率**: Token使用优化

### 路由策略
1. **明确模板名**: 直接调用（如"问题解构"）
2. **关键词匹配**: 自动推荐最相关模板
3. **默认兜底**: 使用通用框架（CO-STAR）

## 知识库

### 框架 (knowledge/frameworks/)
- CO-STAR框架详解
- CREATE框架详解
- APE框架详解
- 框架对比和选择指南

### 最佳实践 (knowledge/best-practices/)
- 提示词编写原则
- 常见错误和避坑指南
- Token优化策略
- 多轮对话技巧

### 模式 (knowledge/patterns/)
- Few-Shot Learning模式
- Chain-of-Thought模式
- Role Prompting模式
- Self-Consistency模式

### 高级模式 (knowledge/advanced-patterns/)
- ReAct (推理+行动)
- Tree-of-Thoughts (思维树)
- Multi-Agent Collaboration
- RAG增强提示词

## 评估体系

### 5维度评分
```python
{
  "clarity": 0-5,      # 清晰度
  "completeness": 0-5, # 完整性
  "actionability": 0-5, # 可操作性
  "consistency": 0-5,  # 一致性
  "efficiency": 0-5    # 效率
}
```

### 总分计算
```python
总分 = (clarity + completeness + actionability + consistency + efficiency) / 25 * 100
```

### 质量等级
- **90-100**: 优秀 (可直接使用)
- **75-89**: 良好 (微调后使用)
- **60-74**: 及格 (需要优化)
- **<60**: 不及格 (重新设计)

## 版本历史

- **v1.0** (2026-02-21): 初始版本，完成P0+P1+P2全部功能

## 贡献指南

欢迎提交新模板和改进建议！

### 模板提交规范
1. 放置在对应优先级目录 (templates/p0/, p1/, p2/)
2. 包含完整的YAML frontmatter
3. 通过质量评估（总分>75）
4. 添加Few-Shot示例（可选）

## 相关技能

- `/uc` - 统一搜索
- `systematic-debugging` - 系统化调试
- `testing-patterns` - 测试模式

## 许可证

MIT License
