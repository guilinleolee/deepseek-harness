---
name: lsp
description: lsp - 天龙LSP工具命令
invokable: true
---
# /lsp - 天龙LSP工具命令

IDE级精度的代码操作，通过Language Server Protocol实现。

## 使用方式

```bash
/lsp-rename <file> <symbol> <new-name>   # 重命名符号
/lsp-references <file> <symbol>           # 查找所有引用
/lsp-definition <file> <symbol>           # 跳转到定义
/lsp-diagnostics <file>                   # 获取诊断信息
/lsp-hover <file> <line> <col>            # 获取悬停信息
/lsp-complete <file> <line> <col>         # 获取补全建议
```

## 功能说明

### 1. 重命名符号 (rename)

```bash
/lsp-rename src/utils.ts "oldFunction" "newFunction"
```

**效果**:
- 重命名函数定义
- 更新所有调用点
- 更新所有import引用
- 一次性全局重命名

**输出示例**:
```
✅ Renamed "oldFunction" → "newFunction"

Changed files:
  src/utils.ts (definition)
  src/app.ts (2 references)
  tests/utils.test.ts (3 references)

Total: 6 changes across 3 files
```

### 2. 查找引用 (references)

```bash
/lsp-references src/app.ts "handleRequest"
```

**输出示例**:
```
📍 References for "handleRequest"
==================================================

src/app.ts:
  15: const result = handleRequest(req);
  42: return handleRequest(processedReq);

src/handlers/index.ts:
  7: import { handleRequest } from './request';

tests/handlers.test.ts:
  23: const mock = handleRequest(mockReq);

==================================================
Total: 4 references across 3 files
```

### 3. 跳转定义 (definition)

```bash
/lsp-definition src/app.ts "express"
```

**输出示例**:
```
📍 Definition of "express"
==================================================

File: node_modules/@types/express/index.d.ts
Line: 17
Content: declare function e(): core.Express;

Type: function declaration
Module: express
```

### 4. 获取诊断 (diagnostics)

```bash
/lsp-diagnostics src/app.ts
```

**输出示例**:
```
🔍 Diagnostics for src/app.ts
==================================================

❌ Errors (2):
  15:5 - Cannot find name 'undefinedVar'
  28:12 - Type 'string' is not assignable to type 'number'

⚠️ Warnings (1):
  42:1 - Unused variable 'temp'

💡 Suggestions (2):
  7:1 - Consider using 'const' instead of 'let'
  55:10 - Missing return type on function

==================================================
Summary: 2 errors, 1 warning, 2 suggestions
```

### 5. 悬停信息 (hover)

```bash
/lsp-hover src/app.ts 15 10
```

**输出示例**:
```
📋 Hover at src/app.ts:15:10
==================================================

Symbol: handleRequest
Type: (req: Request) => Response
Documentation:
  Process incoming HTTP request and return response.
  @param req - Express Request object
  @returns Express Response object
```

### 6. 代码补全 (complete)

```bash
/lsp-complete src/app.ts 20 15
```

**输出示例**:
```
💡 Completions at src/app.ts:20:15
==================================================

  console.log()
  console.error()
  console.warn()
  console.info()
  const
  continue

==================================================
6 suggestions (filtered by context)
```

## 支持的语言

| 语言 | LSP服务器 | 状态 |
|------|----------|------|
| TypeScript | typescript-language-server | ✅ 默认支持 |
| JavaScript | typescript-language-server | ✅ 默认支持 |
| Python | pylsp / pyright | ✅ 需安装 |
| Rust | rust-analyzer | ✅ 需安装 |
| Go | gopls | ✅ 需安装 |
| Java | jdtls | ✅ 需安装 |
| C/C++ | clangd | ✅ 需安装 |
| Ruby | solargraph | ✅ 需安装 |

## 与Hash-Anchored协同

```bash
# 工作流示例

# 1. 读取文件获取锚点
/hash-read src/utils.ts

# 2. 查找所有引用
/lsp-references src/utils.ts "oldFunction"

# 3. 精确重命名（使用锚点确保安全）
/hash-edit src/utils.ts "15#K7" "function newFunction() {"

# 4. 验证修改
/lsp-diagnostics src/utils.ts
```

## 天龙岗位映射

| 岗位 | LSP用途 |
|------|---------|
| **03构建师** | 精确重命名、引用查找、代码补全 |
| **06审查师** | 诊断分析、类型检查、引用追踪 |
| **04验证师** | 错误定位、类型验证 |
| **01调研师** | 定义跳转、引用分析 |

## 配置

```json
// .claude/lsp-config.json
{
  "servers": {
    "typescript": {
      "command": "typescript-language-server",
      "args": ["--stdio"],
      "enabled": true
    },
    "python": {
      "command": "pylsp",
      "args": [],
      "enabled": true
    },
    "rust": {
      "command": "rust-analyzer",
      "args": [],
      "enabled": true
    }
  },
  "timeout": 5000,
  "diagnostics": {
    "enable": true,
    "maxItems": 100
  }
}
```

## 安装LSP服务器

```bash
# TypeScript/JavaScript
npm install -g typescript-language-server typescript

# Python
pip install python-lsp-server

# Rust
rustup component add rust-analyzer

# Go
go install golang.org/x/tools/gopls@latest
```

## 来源

> [oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent) - LSP集成
> 集成方案: [analysis/OH-MY-OPENAGENT-P1-INTEGRATION-PLAN.md](analysis/OH-MY-OPENAGENT-P1-INTEGRATION-PLAN.md)