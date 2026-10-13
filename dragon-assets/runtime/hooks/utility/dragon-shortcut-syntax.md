# 🐉 天龙引擎简化调用语法规范 v1.0

> **灵感来源**：ai-agent-team (Sunnyeung369/ai-agent-team)
>
> **设计目标**：将复杂的Task调用简化为直观的语法糖

---

## 📝 语法规范

### 1. 数字编号语法

```
[<编号>] <任务描述>
```

**示例**：
```bash
# 完整语法
Task({ subagent_type: "00analyst", prompt: "分析这个问题" })

# 简化语法
[00] 分析这个问题
[0] 分析这个问题

# 其他Agent
[01] 调研这个代码库
[02] 设计系统架构
[03] 实现这个功能
[04] 测试这个模块
[05] 审查这段代码
[06] 编写文档
[07] 发布版本
[08] 审查安全性
```

**映射表**：
| 编号 | Agent | 名称 | 专精 |
|------|-------|------|------|
| 00 | 00analyst | 分析师 | 问题解构、需求分析 |
| 01 | 01investigator | 调研师 | 代码考古、技术调研 |
| 02 | 02architect | 架构师 | 系统设计、架构规划 |
| 03 | 03builder | 构建师 | 代码实现、功能开发 |
| 04 | 04validator | 验证师 | 质量保证、测试验证 |
| 05 | 05security-reviewer | 安全师 | 安全审查、漏洞检测 |
| 06 | 06code-reviewer | 审查师 | 代码审查、质量审计 |
| 07 | 07scribe | 记录师 | 文档编写、知识沉淀 |
| 08 | 08publisher | 发布师 | 版本发布、Git管理 |

---

### 2. 中文名称语法

```
[@<中文名称>] <任务描述>
```

**示例**：
```bash
[@分析师] 分析用户需求
[@调研师] 考古这个代码库
[@架构师] 设计系统架构
[@构建师] 实现这个功能
[@验证师] 测试这个模块
[@安全师] 审查安全性
[@审查师] 审查代码质量
[@记录师] 编写API文档
[@发布师] 发布新版本
```

**支持别名**：
- 分析师 → 00分析师、分析师
- 调研师 → 01调研师、调研员、考古师
- 架构师 → 02架构师、架构设计
- 构建师 → 03构建师、开发者、程序员
- 验证师 → 04验证师、测试员、QA
- 安全员 → 05安全师、安全审查
- 审查师 → 06审查师、代码审查
- 记录师 → 07记录师、文档师
- 发布师 → 08发布师、发布经理

---

### 3. 任务分类语法

```
[task:<category>] <任务描述>
```

**示例**：
```bash
[task:analyze] 分析这个问题
[task:research] 调研这个技术
[task:design] 设计这个功能
[task:build] 实现这个功能
[task:test] 测试这个模块
[task:review] 审查这段代码
[task:document] 编写文档
[task:publish] 发布版本
```

**分类映射**：
| Category | 目标Agent | 说明 |
|----------|-----------|------|
| analyze | 00analyst | 需求分析、问题解构 |
| research | 01investigator | 调研考古、信息收集 |
| design | 02architect | 架构设计、系统规划 |
| build | 03builder | 代码实现、功能开发 |
| test | 04validator | 测试验证、质量保证 |
| security | 05security-reviewer | 安全审查、漏洞检测 |
| review | 06code-reviewer | 代码审查、质量审计 |
| document | 07scribe | 文档编写、知识沉淀 |
| publish | 08publisher | 版本发布、Git管理 |

---

### 4. 组合语法（高级）

```
[<编号1>+<编号2>] <任务描述>
```

**示例**：
```bash
# 串行执行
[00+01] 先分析再调研

# 并行执行（未来支持）
[00&01] 同时分析和调研
```

---

## 🔧 Hook实现原理

### 拦截点

```javascript
// userPromptSubmit Hook
function parseShortcutSyntax(userPrompt) {
  // 匹配 [00], [@分析师], [task:research]
  const patterns = [
    /^\[(\d{2})\]\s*(.+)$/,                    // [00] 任务
    /^\[@([^\]]+)\]\s*(.+)$/,                  // [@名称] 任务
    /^\[task:(\w+)\]\s*(.+)$/                  // [task:cat] 任务
  ];

  // 解析并转换为Task调用
}
```

### 转换示例

```javascript
// 输入
"[01] 调研React Hooks"

// 转换为
{
  tool: "Task",
  subagent_type: "01investigator",
  prompt: "调研React Hooks"
}
```

---

## 📊 兼容性

### 保留现有语法

```bash
# 完整语法仍然支持
Task({ subagent_type: "00analyst", prompt: "..." })
/plan
/commit
```

### 混合使用

```bash
# 可以在同一会话中混合使用
[00] 分析需求
Task({ subagent_type: "03builder", prompt: "实现功能" })
[@测试] 验证功能
```

---

## 🎯 使用场景

### 场景1: 快速任务

```bash
[03] 修复这个bug
```

### 场景2: 复杂任务

```bash
[00] 分析这个GitHub仓库并生成报告
```

### 场景3: 团队协作

```bash
[@调研师] 收集需求
[@架构师] 设计方案
[@构建师] 实现功能
[@验证师] 测试验收
```

---

## 🚀 未来扩展

### v1.1计划

- [ ] 支持并行语法 `[00&01]`
- [ ] 支持自定义别名
- [ ] 支持参数传递 `[03] --model=sonnet 实现功能`

### v2.0计划

- [ ] 支持管道语法 `[00] | [03] | [04]`
- [ ] 支持条件语法 `[00] ? [03] : [04]`
- [ ] 支持循环语法 `[03]*3 重复测试`

---

## 📚 参考文献

- ai-agent-team: https://github.com/Sunnyeung369/ai-agent-team
-天龙引擎V7.1: C:\Users\li\.claude\CLAUDE.md
- Hooks文档: C:\Users\li\.claude\hooks\README.md

---

*版本: 1.0.0 | 更新: 2026-02-28*
