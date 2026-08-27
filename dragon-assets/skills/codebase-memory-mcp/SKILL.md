---
license: UNKNOWN
name: codebase-memory-mcp
description: |
github_repo: DeusData/codebase-memory-mcp
github_hash: bebc6d8d571268f6ebe30f8bd1aca036e958b6ef
last_updated: 2026-04-25
source_type: derived
集成于 V8.66: 01调研师 V8.64, 03构建师 V8.63, 06审查师 V8.51, 02架构师 V8.63
triggers: ["codebase memory mcp", "Codebase Memory MCP - V8.66 核心技能"]
---

# Codebase Memory MCP - V8.66 核心技能

## 概述

**codebase-memory-mcp** 是天龙引擎 V8.66 集成的极速代码智能引擎，通过 tree-sitter AST 分析生成持久知识图谱。

### 核心指标

| 指标 | 性能 |
|------|------|
| Linux内核全索引 | 3分钟 (28M LOC, 75K文件) |
| Django全索引 | ~6秒 |
| Cypher查询 | <1ms |
| 名称搜索(regex) | <10ms |
| 死代码检测 | ~150ms |
| Token节省 | **120倍** |

### 66种编程语言支持

```
主流语言: Python, JavaScript, TypeScript, Go, Rust, Java, C, C++, C#
Web语言: HTML, CSS, SCSS, JSON, YAML, TOML, XML, Markdown
脚本语言: Bash, Shell, Ruby, PHP, Perl, Lua
数据语言: SQL, R, Julia, Scala, Kotlin, Swift
系统语言: Assembly, Rust, Zig, Nim, D, Odin
移动语言: Objective-C, Dart, Kotlin
科学语言: MATLAB, Fortran, COBOL, Pascal
配置语言: Dockerfile, Terraform, HCL, Nix, Cue
```

---

## 14个MCP工具

### 索引工具 (4个)

```javascript
// 全量/增量索引代码仓库
index_repository({ repo_path: "/path/to/repo", incremental: true })

// 列出已索引项目
list_projects()

// 删除项目及关联数据
delete_project({ project_name: "project-name" })

// 查看索引进度
index_status()
```

### 查询工具 (7个)

```javascript
// 图谱名称搜索(regex)
search_graph({
  name_pattern: ".*Handler.*",
  label: "Function",
  file_pattern: "*.ts"
})

// 追踪函数调用链(任意深度)
trace_call_path({
  function_name: "Search",
  direction: "both",  // "caller" | "callee" | "both"
  depth: 5
})

// Cypher查询(自定义图查询)
query_graph({
  query: "MATCH (f:Function) WHERE f.name =~ '.*parse.*' RETURN f.name LIMIT 10"
})

// 获取图谱Schema
get_graph_schema()

// 获取代码片段
get_code_snippet({
  node_id: "node-id",
  context_lines: 5
})

// 获取模块架构
get_architecture()

// 代码语义搜索
search_code({
  query: "user authentication flow",
  language: "typescript"
})
```

### 高级工具 (3个)

```javascript
// 检测代码变化及影响
detect_changes({
  changed_files: ["src/auth.ts"],
  include_dependents: true
})

// 管理架构决策记录(ADR)
manage_adr({
  action: "list"  // "list" | "create" | "get"
})

// 摄入性能追踪数据
ingest_traces({
  trace_file: "/path/to/traces.json"
})
```

---

## 图数据模型

### 节点标签

| 标签 | 说明 | 示例 |
|------|------|------|
| `Project` | 项目根节点 | - |
| `Package` | 包/模块 | npm, pip, cargo |
| `Folder` | 目录 | src/, lib/ |
| `File` | 源代码文件 | *.ts, *.py |
| `Module` | ES6模块 | export default |
| `Class` | 类定义 | class User |
| `Function` | 函数定义 | function login() |
| `Method` | 类方法 | user.getName() |
| `Interface` | 接口定义 | interface Config |
| `Enum` | 枚举 | enum Status |
| `Type` | 类型定义 | type ID = string |
| `Route` | HTTP路由 | GET /api/users |
| `Resource` | 资源 | API资源 |

### 边类型

| 边类型 | 说明 |
|--------|------|
| `CONTAINS_*` | 层级包含关系 |
| `DEFINES` | 定义关系 |
| `CALLS` | 函数调用 |
| `HTTP_CALLS` | HTTP请求 |
| `IMPORTS` | 导入关系 |
| `IMPLEMENTS` | 接口实现 |
| `HANDLES` | 路由处理 |
| `USAGE` | 使用关系 |
| `TESTS` | 测试关系 |
| `USES_TYPE` | 类型使用 |
| `MEMBER_OF` | 成员关系 |

---

## 工作流集成

### 01调研师工作流

```
1. index_repository()  → 索引代码库
2. get_architecture()   → 获取模块架构
3. search_graph()       → 搜索关键函数/类
4. trace_call_path()    → 追踪调用链
5. query_graph()        → Cypher深度查询
```

### 03构建师工作流

```
1. search_graph()       → 定位目标函数
2. get_code_snippet()  → 获取实现细节
3. trace_call_path()    → 理解调用上下文
4. detect_changes()     → 修改前影响分析
5. search_code()        → 相似代码参考
```

### 06审查师工作流

```
1. search_graph()       → 发现所有函数/类
2. query_graph()        → 死代码检测查询
3. get_architecture()  → 架构合规检查
4. trace_call_path()    → 未使用函数识别
5. manage_adr()         → 架构决策审查
```

---

## CLI命令

```bash
# 版本
codebase-memory-mcp --version

# 索引仓库
codebase-memory-mcp cli index_repository '{"repo_path": "/path/to/repo"}'

# 搜索图谱
codebase-memory-mcp cli search_graph '{"name_pattern": ".*Handler.*", "label": "Function"}'

# 追踪调用
codebase-memory-mcp cli trace_call_path '{"function_name": "Search", "direction": "both"}'

# Cypher查询
codebase-memory-mcp cli query_graph '{"query": "MATCH (f:Function) RETURN f.name LIMIT 5"}'

# 列出项目
codebase-memory-mcp cli list_projects

# 查看状态
codebase-memory-mcp cli index_status

# 获取架构
codebase-memory-mcp cli get_architecture

# 获取Schema
codebase-memory-mcp cli get_graph_schema

# 3D可视化UI
codebase-memory-mcp ui
# 访问 http://localhost:9749

# 自动索引配置
codebase-memory-mcp config set auto_index true
```

---

## Cypher查询示例

```cypher
// 查找所有未调用的函数
MATCH (f:Function)
WHERE NOT EXISTS((f)-[:CALLS]->())
AND NOT f.name =~ '.*test.*'
AND NOT f.name =~ '.*Test.*'
RETURN f.name, f.file_path

// 查找深层调用链
MATCH path = (caller:Function)-[:CALLS*1..5]->(callee:Function)
WHERE caller.name = 'main'
RETURN path

// 查找路由处理函数
MATCH (r:Route)-[:HANDLES]->(f:Function)
RETURN r.path, r.method, f.name

// 查找接口实现
MATCH (i:Interface)-[:IMPLEMENTS]->(c:Class)
WHERE i.name = 'IDatabase'
RETURN c.name

// 查找测试覆盖
MATCH (t:Function)-[:TESTS]->(u:Function)
RETURN t.name as test, u.name as under_test
```

---

## 配置

### MCP配置 (~/.claude/.mcp.json)

```json
{
  "mcpServers": {
    "codebase-memory-mcp": {
      "command": "C:/Users/li/.local/bin/codebase-memory-mcp",
      "args": ["mcp", "run"]
    }
  }
}
```

### Claude Code Hook集成

安装脚本自动配置了 PreToolUse hook，会在 grep/file search 工具调用时提醒使用 codebase-memory-mcp。

---

## 与现有系统协同

| 天龙组件 | 协同效果 |
|---------|---------|
| **LSP Tools** | 图谱增强LSP，语义级理解 |
| **gstack-browse** | 架构可视化，互补 |
| **LightRAG** | 代码知识图谱，向量+结构双检索 |
| **advanced-memory-sync** | 索引知识沉淀，长期积累 |
| **claude-mem** | 会话记忆 + 代码图谱双记忆 |

---

## 性能对比

| 操作 | 传统方式 | codebase-memory-mcp | 提升 |
|------|---------|---------------------|------|
| 查找函数 | Grep 5-30s | <10ms | **500-3000x** |
| 追踪调用链 | 手动递归 | <10ms | **质的飞跃** |
| 架构理解 | 阅读大量文件 | get_architecture() | **100x** |
| Token消耗 | 412K | 3.4K | **120x** |
| 死代码发现 | 静态分析工具 | Cypher查询 | **一体化** |

---

**版本**: V8.66 (2026-03-30)
**来源**: [DeusData/codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp)
**Star**: 1k+ (推测)
