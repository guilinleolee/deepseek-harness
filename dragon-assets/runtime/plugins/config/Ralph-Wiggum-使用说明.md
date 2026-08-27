# Ralph Wiggum 插件使用说明

> **AI 循环技术** - 持久迭代的 AI 开发方法论

## 简介

Ralph Wiggum 是一种基于持续 AI 循环的开发方法论。用 Geoffrey Huntley 的话说：**"Ralph 就是一个 Bash 循环"** - 一个简单的 `while true` 循环，反复向 AI 代理发送相同的提示词，让它不断改进工作直到完成。

该技术以《辛普森一家》中的 Ralph Wiggum 命名，体现了"尽管遇到挫折也要持续迭代"的哲学。

---

## 核心原理

这个插件通过 **Stop Hook** 来实现 Ralph 循环：

```bash
# 你只需运行一次：
/ralph-loop "你的任务描述" --completion-promise "DONE"

# 然后 Claude Code 自动执行：
# 1. 处理任务
# 2. 尝试退出
# 3. Stop Hook 阻止退出
# 4. Stop Hook 将相同提示词反馈回去
# 5. 重复直到完成
```

循环发生在**当前会话内部**，不需要外部 bash 循环。Stop Hook 通过阻止正常的会话退出来创建自引用反馈循环。

这创建了一个**自引用反馈循环**：
- 提示词在迭代之间保持不变
- Claude 之前的工作保留在文件中
- 每次迭代都能看到修改过的文件和 git 历史
- Claude 通过阅读自己过去的工作来自主改进

---

## 快速开始

### 基础用法

```bash
/ralph-loop "构建一个 REST API 用于待办事项管理。要求：CRUD 操作、输入验证、测试。完成后输出 <promise>COMPLETE</promise>" --completion-promise "COMPLETE" --max-iterations 50
```

### 最小化用法

```bash
/ralph-loop "实现一个功能" --max-iterations 20
```

---

## 命令参考

### `/ralph-loop` - 启动循环

**语法：**
```bash
/ralph-loop "<prompt>" [选项]
```

**选项：**

| 选项 | 说明 |
|------|------|
| `--max-iterations <n>` | 最大迭代次数（推荐设置安全网） |
| `--completion-promise <text>` | 完成信号短语（精确匹配） |

**示例：**

```bash
# 设置迭代限制和完成承诺
/ralph-loop "实现用户认证功能" --max-iterations 30 --completion-promise "DONE"

# 仅设置迭代限制
/ralph-loop "修复所有测试失败" --max-iterations 50

# 无限循环（不推荐）
/ralph-loop "持续优化代码"
```

---

### `/cancel-ralph` - 取消循环

**语法：**
```bash
/cancel-ralph
```

取消当前活动的 Ralph 循环，并显示已进行的迭代次数。

---

## 提示词编写最佳实践

### 1. 清晰的完成标准

**错误示范：**
```
构建一个待办事项 API，做得好一点。
```

**正确示范：**
```markdown
构建一个待办事项 REST API。

完成后应满足：
- 所有 CRUD 端点正常工作
- 输入验证已就位
- 测试通过（覆盖率 > 80%）
- 包含 API 文档的 README
- 输出：<promise>COMPLETE</promise>
```

---

### 2. 渐进式目标

**错误示范：**
```
创建一个完整的电商平台。
```

**正确示范：**
```markdown
阶段 1：用户认证（JWT，测试）
阶段 2：商品目录（列表/搜索，测试）
阶段 3：购物车（添加/删除，测试）

所有阶段完成后输出 <promise>COMPLETE</promise>
```

---

### 3. 自修正模式

**错误示范：**
```
编写功能 X 的代码。
```

**正确示范：**
```markdown
使用 TDD 实现功能 X：
1. 编写失败的测试
2. 实现功能
3. 运行测试
4. 如果失败，调试并修复
5. 必要时重构
6. 重复直到所有测试通过
7. 输出：<promise>COMPLETE</promise>
```

---

### 4. 逃生机制

**始终使用 `--max-iterations` 作为安全网：**

```bash
# 推荐：始终设置合理的迭代限制
/ralph-loop "尝试实现功能 X" --max-iterations 20

# 在提示词中包含卡住时的处理方案：
# "经过 15 次迭代后，如果未完成：
#  - 记录阻碍进展的问题
#  - 列出已尝试的方法
#  - 建议替代方案"
```

**注意**：`--completion-promise` 使用精确字符串匹配，不能用于多个完成条件。始终依赖 `--max-iterations` 作为主要安全机制。

---

## 适用场景

### 适合使用 Ralph

- ✅ 有明确定义的任务，有明确的成功标准
- ✅ 需要迭代和改进的任务（如让测试通过）
- ✅ 绿地项目（全新项目），可以放手不管
- ✅ 有自动验证的任务（测试、linter）

### 不适合使用 Ralph

- ❌ 需要人类判断或设计决策的任务
- ❌ 一次性操作，需要立即结果
- ❌ 成功标准不明确的任务
- ❌ 生产环境调试（应使用针对性调试）
- ❌ 需要外部审批或人工干预的任务

---

## 工作原理详解

### Stop Hook 机制

当 Ralph 循环激活时，插件会在项目根目录创建 `.claude/ralph-loop.local.md` 状态文件：

```yaml
---
iteration: 1
max_iterations: 50
completion_promise: "COMPLETE"
---
你的提示词内容...
```

每次 Claude 尝试退出时：
1. Stop Hook 读取状态文件
2. 检查是否达到最大迭代次数
3. 检查输出中是否包含完成承诺
4. 如果未完成，更新迭代计数
5. 阻止退出，将相同提示词反馈给 Claude

### 完成检测

- **完成承诺**：在输出中使用 `<promise>TEXT</promise>` 标签
- **精确匹配**：只有当标签内容完全匹配时才认为完成
- **最大迭代**：达到迭代限制后自动停止

---

## 实际案例

### 案例 1：构建 API

```bash
/ralph-loop "
构建用户管理 REST API。

技术栈：Node.js + Express + PostgreSQL

功能要求：
1. 用户注册（邮箱验证）
2. 用户登录（JWT 认证）
3. 获取用户信息
4. 更新用户信息
5. 删除用户

测试要求：
- 所有端点有单元测试
- 集成测试覆盖主要流程
- 测试覆盖率 > 80%

文档要求：
- README 包含 API 文档
- 环境变量说明
- 部署指南

完成后输出 <promise>API_COMPLETE</promise>
" --completion-promise "API_COMPLETE" --max-iterations 50
```

### 案例 2：修复测试

```bash
/ralph-loop "
修复所有失败的测试。

执行流程：
1. 运行测试套件
2. 分析失败原因
3. 修复代码或测试
4. 重新运行测试
5. 重复直到所有测试通过

完成后输出 <promise>ALL_TESTS_PASSING</promise>
" --completion-promise "ALL_TESTS_PASSING" --max-iterations 30
```

### 案例 3：重构代码

```bash
/ralph-loop "
重构 src/utils.js 文件。

目标：
1. 提高代码可读性
2. 改善函数命名
3. 添加必要的注释
4. 保持所有现有测试通过
5. 不改变公共 API

执行流程：
1. 运行测试确认当前状态
2. 进行小步重构
3. 每次修改后运行测试
4. 如果测试失败，回滚或修复
5. 完成后输出 <promise>REFACTOR_COMPLETE</promise>
" --completion-promise "REFACTOR_COMPLETE" --max-iterations 25
```

---

## 核心哲学

### 1. 迭代 > 完美

不要第一次就追求完美。让循环来完善工作。

### 2. 失败即数据

"确定性地糟糕"意味着失败是可预测且信息丰富的。利用它们来调整提示词。

### 3. 操作者技能很重要

成功取决于编写好的提示词，而不仅仅是拥有好的模型。

### 4. 坚持就是胜利

持续尝试直到成功。循环会自动处理重试逻辑。

---

## 安全建议

### 始终设置迭代限制

```bash
# 推荐
/ralph-loop "任务" --max-iterations 30

# 不推荐（可能无限循环）
/ralph-loop "任务"
```

### 监控进度

- 检查控制台输出中的迭代计数
- 如果看起来卡住了，使用 `/cancel-ralph` 取消
- 查看 `.claude/ralph-loop.local.md` 了解当前状态

### 测试提示词

在长时间运行前，先用较小的 `--max-iterations` 测试提示词：

```bash
# 先测试
/ralph-loop "任务" --max-iterations 5

# 确认有效后，增加限制
/ralph-loop "任务" --max-iterations 50
```

---

## 故障排除

### 循环不停止

1. 检查完成承诺是否正确拼写
2. 使用 `/cancel-ralph` 手动取消
3. 检查 `.claude/ralph-loop.local.md` 确认状态

### 迭代数不增加

如果迭代计数器似乎没有增加，检查：
- Stop Hook 是否正确安装
- `.claude/ralph-loop.local.md` 文件权限
- 查看控制台错误信息

### 完成承诺不被识别

确保：
- 使用正确的标签格式：`<promise>TEXT</promise>`
- TEXT 与 `--completion-promise` 参数精确匹配
- TEXT 不包含额外的空格或换行

---

## 插件文件位置

```
C:\Users\li\.claude\plugins\ralph-wiggum\
├── commands/
│   ├── ralph-loop.md      # 循环命令
│   ├── cancel-ralph.md    # 取消命令
│   └── help.md            # 帮助命令
├── hooks/
│   ├── stop-hook.sh       # Stop Hook 脚本
│   └── hooks.json         # Hook 配置
├── scripts/
│   └── setup-ralph-loop.sh # 设置脚本
└── README.md              # 原始文档
```

---

## 相关资源

- 原始技术：https://ghuntley.com/ralph/
- Ralph Orchestrator：https://github.com/mikeyobrien/ralph-orchestrator
- Awesome Claude：https://awesomeclaude.ai/ralph-wiggum

---

## 实际成果

- 在 Y Combinator 黑客松测试中一夜之间成功生成 6 个仓库
- 一份价值 $50,000 的合同仅用 $297 的 API 成本完成
- 使用这种方法在 3 个月内创建了完整的编程语言（CURSED）

---

*最后更新：2026-01-15*
