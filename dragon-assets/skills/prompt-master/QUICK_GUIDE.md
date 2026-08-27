# 提词师系统 - 快速使用指南

> **5分钟上手，让你的提示词质量提升10倍！**

---

## 🚀 3秒快速开始

```bash
# 查看所有可用模板
python scripts/render.py --list

# 渲染一个模板
python scripts/render.py -t problem-decomposition -v task_description="设计一个用户认证系统"
```

---

## 📋 模板清单

### P0 核心模板（10个）

| 模板 | 名称 | 评分 | 适用场景 |
|------|------|------|---------|
| problem-decomposition | 问题解构 | 92/100 | 复杂任务分解、需求分析 |
| performance-optimization | 性能优化 | 91/100 | 系统性能调优 |
| debugging-analysis | 调试分析 | 90/100 | 问题诊断、故障排查 |
| system-design | 系统设计 | 90/100 | 架构设计、技术方案 |
| code-review | 代码审查 | 89/100 | 代码质量审查 |
| code-refactor | 代码重构 | 88/100 | 代码优化、重构 |
| tech-selection | 技术选型 | 87/100 | 技术栈选择、方案对比 |
| requirement-analysis | 需求分析 | 86/100 | 需求梳理、分析 |
| test-design | 测试设计 | 85/100 | 测试用例设计 |
| documentation-generation | 文档生成 | 84/100 | 技术文档编写 |

---

## 💡 使用场景

### 场景1: 需求分析（00分析师）

```bash
python scripts/render.py -t problem-decomposition \
  -v task_description="设计一个电商推荐系统" \
  -v context="千万级商品，百万级用户"
```

**输出**: 结构化的任务分解报告，包含子任务、依赖关系、风险分析

---

### 场景2: 架构设计（02架构师）

```bash
python scripts/render.py -t system-design \
  -v qps="10000" \
  -v user_scale="百万级" \
  -v availability_requirement="99.9%"
```

**输出**: 完整的系统架构方案，包含服务拆分、技术栈、非功能需求

---

### 场景3: 代码审查（06审查师）

```bash
python scripts/render.py -t code-review \
  -v context_description="JWT认证模块" \
  -v language="python" \
  -v review_focus="安全性、性能"
```

**输出**: 全面的代码审查清单，涵盖安全性、性能、可维护性

---

### 场景4: 性能优化（03构建师）

```bash
python scripts/render.py -t performance-optimization \
  -v context="API响应慢，平均2秒" \
  -v language="python" \
  -v framework="Django"
```

**输出**: 系统化的性能优化方案，包含诊断、优化、验证

---

### 场景5: 调试分析（04验证师）

```bash
python scripts/render.py -t debugging-analysis \
  -v context_description="用户反馈登录失败" \
  -v error_logs="TokenExpiredError" \
  -v reproduction_steps="登录后等待1小时"
```

**输出**: 结构化的问题分析报告，包含根因分析、解决方案

---

## 🎯 九部天龙映射表

| 宗师 | 推荐模板 | 核心价值 |
|------|---------|---------|
| **00分析师** | problem-decomposition, requirement-analysis | 需求分析、任务分解 |
| **02架构师** | system-design, tech-selection | 架构设计、技术选型 |
| **03构建师** | code-refactor, performance-optimization | 代码实现、性能优化 |
| **04验证师** | test-design, debugging-analysis | 测试设计、问题诊断 |
| **06审查师** | code-review | 代码质量审查 |
| **07记录师** | documentation-generation | 技术文档编写 |

---

## 🛠️ 高级用法

### 交互式模式
```bash
python scripts/render.py --interactive
```

### 搜索模板
```bash
python scripts/render.py --search "代码"
```

### 查看模板详情
```bash
python scripts/render.py --info problem-decomposition
```

### 评估提示词质量
```bash
# 评估文件
python scripts/evaluate.py --prompt my_prompt.txt

# 评估文本
python scripts/evaluate.py --text "你的提示词内容"
```

---

## 📊 质量评估维度

评估脚本会从5个维度评分（100分制）：

1. **清晰度 (20%)**: 表达是否清晰无歧义
2. **完整性 (25%)**: 是否包含所有必要要素
3. **可操作性 (25%)**: 是否可直接执行
4. **一致性 (15%)**: 术语和风格是否统一
5. **效率 (15%)**: Token使用是否精简

**评分标准**:
- 90+分: 优秀 ✅
- 75-89分: 良好 🟢
- 60-74分: 及格 🟡
- <60分: 需改进 🔴

---

## ⚡ 性能数据

- **平均渲染时间**: 0.052秒
- **平均输出长度**: 5500字符
- **平均Token消耗**: ~1300 tokens
- **支持最大输入**: 无限制（取决于内存）

---

## 🔧 常见问题

### Q1: 中文乱码？
**A**: 已修复！使用最新版本的 `render.py` 和 `evaluate.py`

### Q2: 如何自定义变量？
**A**: 使用 `-v key=value` 格式，多个变量用空格分隔：
```bash
python scripts/render.py -t system-design \
  -v qps="10000" \
  -v user_scale="百万级"
```

### Q3: 如何保存输出？
**A**:
```bash
# 方法1: 重定向
python scripts/render.py -t problem-decomposition -v task="测试" > output.md

# 方法2: 交互式模式保存
python scripts/render.py --interactive
# 选择 "保存到文件"
```

### Q4: 如何创建自己的模板？
**A**: 在 `templates/p0/` 目录创建 `.md` 文件，格式：
```markdown
---
name: 模板名称
framework: CO-STAR
priority: P0
tags: [标签1, 标签2]
rating: 90
---

# Context (背景)
你的角色定位...

# Objective (目标)
{{task_description}}

...
```

---

## 📚 更多资源

- **详细测试报告**: `TEST_REPORT.md`
- **实战验证报告**: `VALIDATION_REPORT.md`
- **任务完成报告**: `COMPLETION_REPORT.md`
- **项目主页**: `README.md`

---

## 🎉 开始使用

现在就试试吧！

```bash
cd C:\Users\li\.claude\skills\prompt-master
python scripts/render.py --list
```

**让每一个提示词都成为专业级！** 🚀
