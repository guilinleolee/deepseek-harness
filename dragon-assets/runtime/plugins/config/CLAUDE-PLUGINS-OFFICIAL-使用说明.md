# Claude Code 官方插件使用说明

> 来源: [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)
> 更新时间: 2026-01-13

## 已安装插件列表 (25个)

| 插件名 | 类型 | 描述 |
|--------|------|------|
| agent-sdk-dev | 开发工具 | Claude Agent SDK 应用开发 |
| clangd-lsp | LSP | C/C++ 语言服务器 |
| code-review | 代码审查 | PR 自动代码审查 |
| code-simplifier | 代码质量 | 代码简化和重构 |
| commit-commands | Git 工具 | Git 提交/推送/PR 命令 |
| csharp-lsp | LSP | C# 语言服务器 |
| explanatory-output-style | 输出风格 | 教育性代码解释 |
| feature-dev | 开发工作流 | 7阶段功能开发流程 |
| frontend-design | 前端设计 | 前端界面设计 |
| gopls-lsp | LSP | Go 语言服务器 |
| hookify | Hook 工具 | 自定义 Hook 创建 |
| jdtls-lsp | LSP | Java 语言服务器 |
| kotlin-lsp | LSP | Kotlin 语言服务器 |
| learning-output-style | 输出风格 | 交互式学习模式 |
| lua-lsp | LSP | Lua 语言服务器 |
| php-lsp | LSP | PHP 语言服务器 |
| plugin-dev | 开发工具 | Claude Code 插件开发 |
| pr-review-toolkit | PR 审查 | 全面 PR 审查工具包 |
| pyright-lsp | LSP | Python 语言服务器 |
| ralph-loop | 开发方法论 | 迭代式 AI 开发循环 |
| rust-analyzer-lsp | LSP | Rust 语言服务器 |
| security-guidance | 安全 | 安全警告 Hook |
| swift-lsp | LSP | Swift 语言服务器 |
| typescript-lsp | LSP | TypeScript 语言服务器 |

---

## 一、开发工作流类

### 1. feature-dev - 功能开发工作流

**用途**: 系统化的 7 阶段功能开发流程，适用于复杂功能开发。

**命令**: `/feature-dev [功能描述]`

**7 个阶段**:
1. **Discovery** - 理解需求
2. **Codebase Exploration** - 探索现有代码
3. **Clarifying Questions** - 明确需求细节
4. **Architecture Design** - 设计架构方案
5. **Implementation** - 实现功能
6. **Quality Review** - 质量审查
7. **Summary** - 总结完成内容

**示例**:
```bash
/feature-dev 添加用户 OAuth 登录功能
```

**适用场景**:
- ✅ 涉及多个文件的新功能
- ✅ 需要架构决策的功能
- ✅ 复杂的现有代码集成
- ❌ 单行 bug 修复
- ❌ 简单的任务

---

### 2. commit-commands - Git 工作流

**用途**: 简化 Git 操作，一键提交、推送、创建 PR。

**命令**:

| 命令 | 功能 |
|------|------|
| `/commit` | 自动生成提交信息并提交 |
| `/commit-push-pr` | 提交 + 推送 + 创建 PR |
| `/clean_gone` | 清理已删除的远程分支 |

**示例**:
```bash
# 修改代码后
/commit

# 准备创建 PR
/commit-push-pr

# 清理分支
/clean_gone
```

**要求**:
- `gh` CLI 工具已安装并认证 (用于 `/commit-push-pr`)

---

### 3. ralph-loop - 迭代式开发循环

**用途**: 实现 "Ralph Wiggum" 技术 - 持续 AI 循环直到任务完成。

**命令**: `/ralph-loop "<任务描述>" --max-iterations <N> --completion-promise "<完成标记>"`

**示例**:
```bash
/ralph-loop "构建一个 Todo REST API，包含 CRUD 操作和测试。完成后输出 <promise>COMPLETE</promise>" --max-iterations 50 --completion-promise "COMPLETE"
```

**工作原理**:
1. Claude 执行任务
2. 尝试退出时被 Stop hook 拦截
3. 重新注入相同提示
4. 循环直到完成或达到迭代上限

**适用场景**:
- ✅ 有明确成功标准的任务
- ✅ 需要迭代的任务（如通过测试）
- ✅ 可自动验证的任务
- ❌ 需要人类判断的任务
- ❌ 一次性操作

---

## 二、代码审查类

### 4. code-review - PR 自动审查

**用途**: 使用多个专业代理并行审查 PR。

**命令**: `/code-review`

**审查流程**:
1. 检查 PR 状态（跳过已关闭/草稿/已审查）
2. 收集 CLAUDE.md 指导文件
3. 启动 4 个并行审查代理：
   - 代理 #1-2: CLAUDE.md 合规性
   - 代理 #3: 明显 bug 检测
   - 代理 #4: Git 历史分析
4. 对每个问题评分 0-100
5. 过滤低于 80 分的问题
6. 发布高置信度问题评论

**置信度评分**:
- **0**: 不是问题，误报
- **25**: 有点可能是问题
- **50**: 确实是问题，但次要
- **75**: 高度置信，真实且重要
- **100**: 绝对确定，确实是问题

---

### 5. pr-review-toolkit - PR 审查工具包

**用途**: 6 个专业审查代理，涵盖评论、测试、错误处理、类型设计等。

**代理列表**:

| 代理 | 功能 | 触发方式 |
|------|------|----------|
| comment-analyzer | 代码评论准确性 | "检查评论是否准确" |
| pr-test-analyzer | 测试覆盖率 | "检查测试覆盖" |
| silent-failure-hunter | 错误处理 | "检查静默失败" |
| type-design-analyzer | 类型设计质量 | "审查类型设计" |
| code-reviewer | 通用代码审查 | "审查我的更改" |
| code-simplifier | 代码简化 | "简化这段代码" |

**示例**:
```bash
# 综合审查
"请检查：1. 测试覆盖 2. 错误处理 3. 评论准确性"

# 单个审查
"检查是否有静默失败"
```

---

## 三、开发工具类

### 6. plugin-dev - 插件开发工具包

**用途**: 开发 Claude Code 插件的完整工具包。

**命令**: `/plugin-dev:create-plugin [插件描述]`

**8 阶段流程**:
1. Discovery - 理解插件用途
2. Component Planning - 确定所需组件
3. Detailed Design - 详细设计
4. Structure Creation - 创建目录结构
5. Component Implementation - 实现组件
6. Validation - 验证插件
7. Testing - 测试插件
8. Documentation - 完成文档

**7 个技能领域**:
1. **Hook Development** - Hook API 和事件驱动自动化
2. **MCP Integration** - Model Context Protocol 集成
3. **Plugin Structure** - 插件组织和清单配置
4. **Plugin Settings** - 配置模式
5. **Command Development** - 创建斜杠命令
6. **Agent Development** - 创建自主代理
7. **Skill Development** - 创建技能

---

### 7. agent-sdk-dev - Agent SDK 开发

**用途**: 创建和验证 Python/TypeScript Agent SDK 应用。

**命令**: `/new-sdk-app [项目名]`

**交互式问题**:
1. 语言选择
2. 项目名称
3. 代理类型
4. 起始模板
5. 工具偏好

**自动执行**:
- 检查并安装最新 SDK 版本
- 创建项目文件和配置
- 设置环境文件
- 提供工作示例
- 运行类型检查/语法验证
- 自动验证设置

**验证代理**:
- `agent-sdk-verifier-py` - Python 应用验证
- `agent-sdk-verifier-ts` - TypeScript 应用验证

---

### 8. code-simplifier - 代码简化器

**用途**: 简化代码以提高清晰度、一致性和可维护性。

**触发方式**:
```
"简化这段代码"
"让这个更清晰"
"优化这个实现"
```

**分析内容**:
- 代码清晰度和可读性
- 不必要的复杂性和嵌套
- 冗余代码和抽象
- 与项目标准的一致性
- 过于紧凑或聪明的代码

---

## 四、Hook 工具类

### 9. hookify - 自定义 Hook 创建

**用途**: 通过简单的 Markdown 配置文件创建 Hook，无需编辑复杂的 JSON。

**命令**:

| 命令 | 功能 |
|------|------|
| `/hookify [描述]` | 从描述创建规则 |
| `/hookify` | 分析对话找问题模式 |
| `/hookify:list` | 列出所有规则 |
| `/hookify:configure` | 交互式配置 |
| `/hookify:help` | 帮助 |

**规则格式** (`.claude/hookify.xxx.local.md`):
```markdown
---
name: block-dangerous-rm
enabled: true
event: bash
pattern: rm\s+-rf
action: block
---

⚠️ **检测到危险的 rm 命令！**

此命令可能删除重要文件。请验证路径正确。
```

**事件类型**:
- `bash` - Bash 工具命令
- `file` - 文件编辑操作
- `stop` - 停止事件
- `prompt` - 用户提交
- `all` - 所有事件

**操作类型**:
- `warn` - 显示警告但允许
- `block` - 阻止操作

---

### 10. security-guidance - 安全警告

**用途**: 编辑文件时警告潜在安全问题。

**警告内容**:
- 命令注入 (Command Injection)
- 跨站脚本攻击 (XSS)
- SQL 注入
- 不安全的代码模式
- 硬编码凭证

**自动触发**: 编辑文件时自动检查

---

## 五、输出风格类

### 11. explanatory-output-style - 教育性输出

**用途**: 在代码前后提供实现选择的教育性见解。

**输出格式**:
```
★ Insight ─────────────────────────────────────
[2-3 个关于代码库或实现的关键教育点]
─────────────────────────────────────────────────
```

**自动激活**: 安装后每个会话自动启用

---

### 12. learning-output-style - 交互式学习

**用途**: 结合交互式学习和教育性见解。

**功能**:
1. **学习模式**: 在决策点请求你编写有意义的代码
2. **解释模式**: 提供实现选择的教育性见解

**何时请求贡献**:
- 有多种有效方法的业务逻辑
- 错误处理策略
- 算法实现选择
- 数据结构决策
- 用户体验决策

**何时直接实现**:
- 样板代码
- 明显的实现
- 配置或设置代码
- 简单 CRUD 操作

---

## 六、前端设计类

### 13. frontend-design - 前端设计

**用途**: 生成独特、生产级的前端界面，避免通用 AI 美学。

**特点**:
- 大胆的美学选择
- 独特的排版和调色板
- 高冲击力动画和视觉细节
- 上下文感知实现

**示例**:
```
"创建一个音乐流媒体应用的仪表板"
"为 AI 安全初创公司构建着陆页"
```

---

## 七、LSP 语言服务器类

### LSP 插件列表

| 插件 | 语言 | 支持扩展 | 安装方式 |
|------|------|----------|----------|
| clangd-lsp | C/C++ | `.c`, `.h`, `.cpp`, `.cc`, `.cxx`, `.hpp`, `.hxx` | `brew install llvm` 或 `apt install clangd` |
| csharp-lsp | C# | - | - |
| gopls-lsp | Go | - | `go install golang.org/x/tools/gopls@latest` |
| jdtls-lsp | Java | - | - |
| kotlin-lsp | Kotlin | - | - |
| lua-lsp | Lua | - | - |
| php-lsp | PHP | - | - |
| pyright-lsp | Python | `.py`, `.pyi` | `npm install -g pyright` 或 `pip install pyright` |
| rust-analyzer-lsp | Rust | - | `rustup component add rust-analyzer` |
| swift-lsp | Swift | - | - |
| typescript-lsp | TypeScript | `.ts`, `.tsx`, `.js`, `.jsx` | `npm install -g typescript typescript-language-server` |

**注意**: LSP 插件需要先安装相应的语言服务器，插件才能提供代码智能功能。

---

## 插件管理命令

```bash
# 查看已安装的插件
claude plugin marketplace list

# 安装插件
claude plugin install <插件名>@claude-plugins-official

# 卸载插件
claude plugin uninstall <插件名>

# 禁用插件
claude plugin disable <插件名>

# 启用插件
claude plugin enable <插件名>

# 更新插件
claude plugin update <插件名>

# 更新市场
claude plugin marketplace update
```

---

## 常见问题

### Q: 插件安装后没有生效？
A: 需要重启 Claude Code 才能加载新插件。

### Q: 如何查看某个插件的详细信息？
A: 查看插件目录下的 README.md 文件：
```
c:\Users\li\.claude\plugins\marketplaces\claude-plugins-official\plugins\<插件名>\README.md
```

### Q: LSP 插件不工作？
A: LSP 插件需要先安装对应语言的服务器。参考上表中的安装方式。

### Q: 如何禁用某个插件？
A: 使用 `claude plugin disable <插件名>` 或删除插件。

### Q: 插件会消耗额外的 token 吗？
A: 是的，某些插件（如 learning-output-style）会在每个会话添加额外指令，会增加 token 消耗。

---

## 相关资源

- [Claude Code 官方文档](https://docs.claude.com/en/docs/claude-code)
- [Claude Code GitHub](https://github.com/anthropics/claude-code)
- [插件开发指南](https://docs.claude.com/en/docs/claude-code/plugins)
- [Agent SDK 文档](https://docs.claude.com/en/api/agent-sdk/overview)

---

*文档生成时间: 2026-01-13*
