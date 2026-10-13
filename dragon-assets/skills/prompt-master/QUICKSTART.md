# 提词师 - 快速入门指南

> 5分钟掌握专业提示词工程技能

## 🚀 3种使用方式

### 方式1: 直接调用模板（推荐新手）

最简单的方式，直接使用预定义模板：

```bash
# 使用Python脚本
python skills/prompt-master/scripts/render.py \
  --template problem-decomposition \
  --var task_description="设计一个用户认证系统"

# 查看所有模板
python skills/prompt-master/scripts/render.py --list

# 搜索模板
python skills/prompt-master/scripts/render.py --search "代码"
```

**输出**: 完整的优化提示词

### 方式2: 在Claude Code中使用（推荐）

在Claude Code对话中直接引用：

```
@prompt-master 问题解构 "设计一个微服务架构的电商平台"
```

系统会自动：
1. 识别模板类型
2. 渲染变量
3. 输出优化后的提示词

### 方式3: 深度优化（推荐复杂任务）

调用专业subagent：

```
@prompt-architect "优化数据库查询性能，目标是将响应时间从5s降至100ms"
```

Subagent会：
1. 深度分析需求
2. 选择最佳框架
3. 生成3个候选版本
4. 质量评估
5. 推荐最优方案

## 📋 10+核心模板速查

| 模板名 | 适用场景 | 一句话描述 | 评分 |
|--------|---------|-----------|------|
| **问题解构** | 复杂任务分解 | 将模糊任务拆解为可执行步骤 | 92/100 |
| **系统设计** | 架构设计 | 输出完整的系统设计文档 | 90/100 |
| **代码重构** | 代码优化 | 分析代码问题并给出重构方案 | 88/100 |
| **调试分析** | 问题诊断 | 系统化调试，定位根因 | 90/100 |
| **文档生成** | 技术文档 | 生成API文档、用户手册等 | 85/100 |
| **需求分析** | 产品需求 | 从模糊想法到详细PRD | 87/100 |
| **测试设计** | 测试用例 | 生成完整的测试方案 | 86/100 |
| **代码审查** | Code Review | 深度审查代码质量 | 89/100 |
| **技术选型** | 技术决策 | 数据驱动的技术选型报告 | 88/100 |
| **性能优化** | 性能调优 | 全栈性能优化方案 | 91/100 |

## 💡 使用技巧

### 技巧1: 选择合适的模板

```
你的任务 → 关键词匹配 → 推荐模板

"设计一个系统" → 系统设计
"代码太乱了" → 代码重构
"不知道哪里出问题" → 调试分析
"要写API文档" → 文档生成
"怎么选技术栈" → 技术选型
"系统太慢了" → 性能优化
```

### 技巧2: 提供充分的上下文

**❌ 差的输入**:
```
优化代码
```

**✅ 好的输入**:
```
优化这段Python代码，目标是将执行时间从5s降至1s。
代码用于处理用户订单数据，当前使用嵌套循环，
数据量约10万条，希望使用更高效的算法。
```

### 技巧3: 明确输出格式

```
请以以下格式输出:
1. 问题诊断 (表格)
2. 解决方案 (分步骤)
3. 代码示例 (可运行)
4. 测试用例 (3-5个)
```

### 技巧4: 利用Few-Shot示例

在提示词中添加示例：

```markdown
## 示例

**输入**: "优化登录接口"
**输出**:
[完整的优化提示词]

---

现在请处理:
**输入**: "优化数据库查询"
**输出**:
```

## 🎯 常见场景

### 场景1: 快速生成系统设计文档

```bash
# 使用system-design模板
python render.py \
  --template system-design \
  --var business_requirements="电商平台，支持100万用户，日订单1万" \
  --var qps="5000" \
  --var user_scale="100万"
```

### 场景2: 代码重构分析

```bash
# 使用code-refactor模板
python render.py \
  --template code-refactor \
  --var language="python" \
  --var code_snippet="[粘贴代码]" \
  --var context_description="订单处理逻辑，性能瓶颈"
```

### 场景3: 性能优化方案

```bash
# 使用performance-optimization模板
python render.py \
  --template performance-optimization \
  --var system_description="Web应用，响应时间5s，目标<200ms" \
  --var performance_goal="提升25倍性能"
```

## 📊 质量评估

生成的提示词会自动进行5维度评分：

| 维度 | 权重 | 说明 |
|------|------|------|
| 清晰度 | 20% | 无歧义，表达清晰 |
| 完整性 | 25% | 覆盖所有要素 |
| 可操作性 | 25% | 可直接执行 |
| 一致性 | 15% | 术语风格统一 |
| 效率 | 15% | Token使用精简 |

**质量等级**:
- 90-100: 优秀 ✅ (可直接使用)
- 75-89: 良好 🟡 (微调后使用)
- 60-74: 及格 🟠 (需要优化)
- <60: 不及格 🔴 (重新设计)

## 🔧 高级功能

### 1. 自定义模板

在 `templates/p0/` 创建新模板：

```markdown
---
name: 我的模板
framework: CO-STAR
priority: P0
tags: [自定义]
rating: 85
---

# Context (背景)
[你的背景描述]

# Objective (目标)
请{{action}}以下内容：

**任务**: {{task_description}}

...

# Response Format
[输出格式说明]
```

### 2. Few-Shot示例库

在 `examples/few-shot/` 添加示例：

```
examples/few-shot/
├── system-design/
│   ├── ecommerce.md
│   └── im-system.md
└── code-refactor/
    ├── python-optimization.md
    └── java-refactoring.md
```

### 3. A/B测试

对比两个提示词版本的效果：

```bash
python scripts/ab-test.py \
  --prompt-a v1_prompt.txt \
  --prompt-b v2_prompt.txt \
  --test-cases test_cases.json
```

## 📚 学习路径

### Level 1: 新手（1小时）
1. 阅读本快速入门
2. 尝试3个不同模板
3. 理解3大框架（CO-STAR, CREATE, APE）

### Level 2: 熟练（1天）
1. 掌握10+核心模板
2. 学习提示词设计原则
3. 尝试自定义模板

### Level 3: 专家（1周）
1. 深入理解质量评估体系
2. 掌握Few-Shot和CoT技巧
3. 贡献模板到社区

## ❓ 常见问题

### Q1: 如何选择合适的模板？

**A**: 根据任务类型：
- 分析类 → 问题解构、调试分析
- 设计类 → 系统设计、需求分析
- 代码类 → 代码重构、代码审查
- 测试类 → 测试设计
- 优化类 → 性能优化、技术选型

或使用关键词搜索：

```bash
python render.py --search "关键词"
```

### Q2: 提示词太长怎么办？

**A**:
1. 使用更精简的框架（APE > CO-STAR > CREATE）
2. 删除不必要的示例
3. 使用"展开阅读"折叠进阶内容
4. 分步骤执行（每次只关注一个子任务）

### Q3: 如何评估提示词质量？

**A**: 使用质量评估脚本：

```bash
python scripts/evaluate.py --prompt my_prompt.txt
```

会输出5维度评分和改进建议。

### Q4: 可以在团队中共享模板吗？

**A**: 可以！模板是Markdown文件，可以通过Git共享：

```bash
# 提交到团队仓库
git add templates/p0/my-template.md
git commit -m "添加: XXX场景模板"
git push
```

### Q5: 如何贡献新模板？

**A**:
1. 在 `templates/p0/` 或 `p1/` 或 `p2/` 创建新模板
2. 包含完整的YAML frontmatter
3. 添加Few-Shot示例（可选）
4. 通过质量评估（总分>75）
5. 提交PR到GitHub仓库

## 🚀 下一步

- [ ] 尝试第一个模板
- [ ] 阅读完整的 [SKILL.md](SKILL.md)
- [ ] 浏览 [README.md](README.md)
- [ ] 查看 [10+核心模板](templates/p0/)
- [ ] 学习 [提示词设计原则](knowledge/best-practices/writing-principles.md)

---

**需要帮助?**
- 查看文档: `docs/`
- 提交Issue: [GitHub Issues](https://github.com/your-repo/issues)
- 加入社区: [Discord](https://discord.gg/your-server)

**享受提示词工程之旅！** 🎉
