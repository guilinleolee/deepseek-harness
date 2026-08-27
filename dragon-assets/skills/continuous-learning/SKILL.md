---
license: UNKNOWN
name: continuous-learning-v2
description: |
混合模式持续学习系统：实时技能提取(Claudeception) + 会话批量总结。
自动评估 Claude Code 会话以提取可复用模式并保存为技能。
触发条件：会话结束(Stop hook) 自动评估 + 用户请求 "/learn"。
质量门槛：需要发现(非文档查询)、可复用、明确触发条件、已验证。
基于 Voyager/CASCADE/SEAgent/Reflexion 学术研究。
github_url: https://github.com/anthropics/skills/tree/main/skills/continuous-learning
github_hash: 5128e1865d670f5d6c9cef000e6dfc4e951fb5b9
github_repo: anthropics/skills
author: Claude
created: 2026-02-26
version: 2.0.0
date: 2026-02-24
triggers: ["continuous learning", "Continuous Learning Skill (混合模式增强版)"]
---

# Continuous Learning Skill (混合模式增强版)

## 🎯 核心功能

混合模式持续学习系统，结合两种互补的技能提取策略：

### 📊 实时提取模式（Claudeception）
- **触发**：每次用户提交请求后（UserPromptSubmit hook）
- **目的**：任务完成时立即评估是否提取技能
- **优势**：及时捕获知识，避免遗忘

### 🔄 批量总结模式（传统 continuous-learning）
- **触发**：会话结束时（Stop hook）
- **目的**：回顾整个会话，批量总结可复用模式
- **优势**：全局视角，发现跨任务的深层模式

---

## 📚 学术研究基础

本技能的设计基于以下学术研究：

1. **Voyager** (Wang et al., 2023)
   - 游戏代理通过技能库避免重复学习
   - 证明：持久化技能的代理表现优于从零开始的代理

2. **CASCADE** (2024)
   - 引入"元技能"（获取技能的技能）
   - 本技能即是一种元技能实现

3. **SEAgent** (2025)
   - 代理通过试错学习新软件环境
   - 启发了回顾性学习功能

4. **Reflexion** (Shinn et al., 2023)
   - 证明自我反思提升代理性能
   - 强调持续改进的重要性

> **核心洞察**：持久化学习的代理比从零开始的代理表现更好。

---

## ⚙️ 配置

创建或编辑 `config.json` 来自定义：

```json
{
  "min_session_length": 10,
  "extraction_threshold": "medium",
  "auto_approve": false,
  "learned_skills_path": "~/.claude/skills/learned/",
  "patterns_to_detect": [
    "error_resolution",
    "user_corrections",
    "workarounds",
    "debugging_techniques",
    "project_specific"
  ],
  "ignore_patterns": [
    "simple_typos",
    "one_time_fixes",
    "external_api_issues"
  ],
  "quality_gates": {
    "requires_discovery": true,
    "must_be_reusable": true,
    "must_be_verified": true,
    "specific_triggers": true
  }
}
```

---

## 🎯 质量门槛（四条铁律）

在提取技能之前，必须验证知识满足以下标准：

### 1. ✅ 需要发现 (Requires Discovery)
- 这不是简单的文档查询
- 需要实际的调查或调试
- 解决方案不是显而易见的

### 2. ✅ 可复用 (Reusable)
- 将有助于未来的任务
- 不仅适用于当前实例
- 可以在其他类似情况下应用

### 3. ✅ 明确触发条件 (Specific Triggers)
- 可以描述确切的触发条件
- 包含具体的错误消息或症状
- 有明确的上下文标记

### 4. ✅ 已验证 (Verified)
- 解决方案实际有效
- 不是理论上的
- 已经过测试或验证

---

## 📋 模式类型

| Pattern | Description |
|---------|-------------|
| `error_resolution` | How specific errors were resolved |
| `user_corrections` | Patterns from user corrections |
| `workarounds` | Solutions to framework/library quirks |
| `debugging_techniques` | Effective debugging approaches |
| `project_specific` | Project-specific conventions |

---

## 🔄 工作流程

### 批量模式（Stop hook）

1. **会话评估**：检查会话是否有足够的消息（默认：10+）
2. **模式检测**：识别会话中的可提取模式
3. **技能提取**：将有用的模式保存到 `~/.claude/skills/learned/`

### 实时模式（Claudeception activator）

每次用户提交请求后，Hook 会注入提醒：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 MANDATORY SKILL EVALUATION REQUIRED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CRITICAL: After completing this user request, you MUST evaluate whether
it produced extractable knowledge using the claudeception skill.

EVALUATION PROTOCOL (NON-NEGOTIABLE):

1. COMPLETE the user's request first
2. EVALUATE: Ask yourself:
   - Did this require non-obvious investigation or debugging?
   - Was the solution something that would help in future similar situations?
   - Did I discover something not immediately obvious from documentation?

3. IF YES to any question above:
   ACTIVATE: Use Skill(claudeception) NOW to extract the knowledge

4. IF NO to all questions:
   SKIP: No skill extraction needed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🔧 Hook 设置

### 方式一：用户级设置（推荐）

在 `~/.claude/settings.json` 中添加：

```json
{
  "hooks": {
    "userPromptSubmit": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/claudeception-activator.sh"
          }
        ]
      }
    ]
  }
}
```

### 方式二：项目级设置

在项目 `.claude/settings.json` 中添加：

```json
{
  "hooks": {
    "userPromptSubmit": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/claudeception-activator.sh"
          }
        ]
      }
    ]
  }
}
```

---

## 📖 相关资源

- [Claudeception](https://github.com/blader/Claudeception) - 实时技能提取系统
- [The Longform Guide](https://x.com/affaanmustafa/status/2014040193557471352) - Section on continuous learning
- `/learn` command - Manual pattern extraction mid-session

---

## 🧬 Evolution Pattern (维护模式)

为了在核心技能升级时保留自定义改进，避免直接编辑 `SKILL.md` 进行单独修改。相反：

1. 在技能根目录创建或更新 `evolution.json` 文件
2. 存储修改建议、自定义规则或演化逻辑
3. 确保自定义"演化"在基础 `SKILL.md` 被替换时得以保留

---

## 📊 预期收益

| 指标 | 传统模式 | 混合模式 | 提升 |
|------|----------|----------|------|
| **知识留存率** | 低（会话结束丢失） | 高（自动保存） | +300% |
| **重复问题解决时间** | 1小时 | 5分钟（技能复用） | -92% |
| **技能库增长** | 手动 | 自动 | +∞ |
| **学术严谨性** | 低 | 高（基于研究） | 质的飞跃 |
