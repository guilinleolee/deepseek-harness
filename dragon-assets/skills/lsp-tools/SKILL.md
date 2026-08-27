---
license: UNKNOWN
github_repo: code-yeongyu/oh-my-openagent
github_hash: 48b0cfeaf54b19beca3c29d501c58c05d5515d2d
last_updated: 2026-04-25
source_type: derived
triggers: ["lsp tools", "LSP Tools - IDE级精度代码操作"]
---
# LSP Tools - IDE级精度代码操作

> 通过Language Server Protocol实现IDE级精度的代码操作

## 触发词

`/lsp-rename`, `/lsp-references`, `/lsp-definition`, `/lsp-diagnostics`, `/lsp-hover`, `/lsp-complete`, `LSP`, `重命名符号`

## 功能

### 1. 重命名符号 (rename)
```
/lsp-rename src/utils.ts "oldFunction" "newFunction"
```
一次性全局重命名，更新所有引用

### 2. 查找引用 (references)
```
/lsp-references src/app.ts "handleRequest"
```

### 3. 跳转定义 (definition)
```
/lsp-definition src/app.ts "express"
```

### 4. 获取诊断 (diagnostics)
```
/lsp-diagnostics src/app.ts
```

### 5. 悬停信息 (hover)
```
/lsp-hover src/app.ts 15 10
```

### 6. 代码补全 (complete)
```
/lsp-complete src/app.ts 20 15
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

## 天龙岗位映射

| 岗位 | LSP用途 |
|------|---------|
| **03构建师** | 精确重命名、引用查找、代码补全 |
| **06审查师** | 诊断分析、类型检查、引用追踪 |
| **04验证师** | 错误定位、类型验证 |
| **01调研师** | 定义跳转、引用分析 |

## 来源

> [oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent) - LSP集成