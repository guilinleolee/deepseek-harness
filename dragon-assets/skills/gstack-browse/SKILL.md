---
license: UNKNOWN
name: gstack-browse
description: |
github_repo: garrytan/gstack.git
github_hash: 6209163900beb7497391f8dfc35e2c7d362f23b8
last_updated: 2026-04-25
source_type: derived
version: 1.0.0
allowed-tools: 
triggers: ["gstack browse", "gstack-browse - 守护进程浏览器"]
---

# gstack-browse - 守护进程浏览器

## 🎯 核心价值

解决 AI Agent 浏览器操作的**性能**和**状态持久化**两大核心问题。

| 维度 | 传统方案 | gstack-browse | 提升 |
|------|---------|---------------|------|
| **启动延迟** | 3-5s | **100-200ms** | **-96%** |
| **状态持久化** | 无 | Cookies + Tabs + Session | **质的飞跃** |
| **元素选择** | CSS/XPath（不可靠） | **Ref 引用系统** | **生产可用** |
| **CSP 绑定** | 受限 | **绕过 CSP/Shadow DOM** | **突破限制** |

---

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code Session                       │
└────────────────────────┬────────────────────────────────────┘
                         │ CLI
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Server (Bun.serve)                        │
│                   端口: 37778                                │
│                   延迟: ~100-200ms                           │
└────────────────────────┬────────────────────────────────────┘
                         │ CDP
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Chromium (持久化 Headless)                      │
│              • Cookies 持久化                                │
│              • Tabs 持久化                                   │
│              • 30 分钟空闲超时                                │
│              • 用户数据目录: ~/.gstack-browser/              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 安装

```bash
# 克隆 gstack
git clone https://github.com/garrytan/gstack.git
cd gstack

# 安装依赖
bun install

# 构建
bun run build

# 安装到系统
bun link
```

### 基本使用

```bash
# 启动浏览器（首次启动约 3s）
gstack browse

# 后续命令（~100-200ms）
gstack browse --url "https://example.com"
gstack browse --snapshot
gstack browse --click "@e1"
gstack browse --type "@e2" "Hello World"
```

---

## 📋 核心命令

### 浏览器控制

| 命令 | 功能 | 示例 |
|------|------|------|
| `gstack browse` | 启动/连接浏览器 | `gstack browse` |
| `gstack browse --url <url>` | 导航到 URL | `gstack browse --url "https://github.com"` |
| `gstack browse --snapshot` | 获取页面快照 | `gstack browse --snapshot` |
| `gstack browse --screenshot` | 截图 | `gstack browse --screenshot` |

### 页面交互

| 命令 | 功能 | 示例 |
|------|------|------|
| `gstack browse --click <ref>` | 点击元素 | `gstack browse --click "@e1"` |
| `gstack browse --type <ref> <text>` | 输入文本 | `gstack browse --type "@e2" "Hello"` |
| `gstack browse --scroll <direction>` | 滚动页面 | `gstack browse --scroll down` |
| `gstack browse --wait <selector>` | 等待元素 | `gstack browse --wait "#content"` |

### Cookie 管理

| 命令 | 功能 | 示例 |
|------|------|------|
| `gstack browse --cookies-export` | 导出 Cookies | `gstack browse --cookies-export` |
| `gstack browse --cookies-import <file>` | 导入 Cookies | `gstack browse --cookies-import cookies.json` |
| `gstack setup-browser-cookies` | 从真实浏览器导入 | `gstack setup-browser-cookies` |

---

## 🔍 Ref 引用系统

### 核心原理

传统 CSS 选择器和 XPath 在生产环境中不可靠：
- DOM 突变导致选择器失效
- CSP 限制执行脚本
- React 水合破坏选择器
- Shadow DOM 隔离元素

**解决方案**：基于 ARIA 树的引用系统。

### 工作流程

```
1. Agent: gstack browse --snapshot -i
2. Server: page.accessibility.snapshot()
3. Parser: 分配 @e1, @e2, @e3... refs
4. Store: Map<string, RefEntry> (role + name + Locator)
5. Later: gstack browse --click @e3 → Locator.click()
```

### 快照示例

```yaml
# gstack browse --snapshot -i

Page: https://github.com/login

Interactive Elements:
  @e1 [textbox] "Username or email address"
  @e2 [textbox] "Password"
  @e3 [button] "Sign in"
  @e4 [link] "Forgot password?"
  @e5 [link] "Create an account"

Cursor Pointer Elements:
  @c1 [img] "GitHub Logo"
  @c2 [div] "Terms of Service"
```

### 分离命名空间

| 前缀 | 含义 | 使用场景 |
|------|------|---------|
| `@e` | 交互元素 | 可点击、可输入、可聚焦 |
| `@c` | cursor:pointer 元素 | 视觉提示、装饰性交互 |

---

## 🛡️ 安全模型

### Cookie 安全

```
1. Keychain 访问需要用户批准
2. 解密在进程内存中进行（PBKDF2 + AES-128-CBC）
3. 数据库只读访问（复制到临时文件）
4. 密钥缓存仅限会话生命周期
5. 日志中无 Cookie 值
```

### 危险命令保护

```bash
# /careful 技能集成
# 自动检测危险命令并警告

gstack browse --eval "rm -rf /"  # ⚠️ 警告：危险命令
```

---

## 🔄 与天龙引擎集成

### 升级岗位

| 岗位 | 升级内容 | 收益 |
|------|---------|------|
| **01 调研师** | 守护进程浏览器采集 | 浏览器操作延迟 -96% |
| **04 验证师** | 持久化 E2E 测试 | 测试环境状态保持 |
| **35-02 社媒运营** | 登录状态持久化 | 无需重复登录 |

### 与现有 Skill 协同

| 天龙 Skill | gstack-browse | 协同效果 |
|-----------|--------------|---------|
| **Chrome CDP** | 替换方案 | 更高效的守护进程模式 |
| **Playwright** | 补充方案 | 简单交互用 gstack，复杂用 Playwright |
| **dragon-scraper** | 底层支撑 | 更稳定的浏览器操作 |

---

## 📊 性能基准

| 操作 | 传统方案 | gstack-browse | 提升 |
|------|---------|---------------|------|
| **首次启动** | 3-5s | **~3s** | 持久化启动 |
| **后续命令** | 3-5s | **100-200ms** | **-96%** |
| **页面快照** | 1-2s | **~300ms** | **-70%** |
| **元素交互** | 1-2s | **~200ms** | **-80%** |
| **Cookie 导入** | 手动 | **自动** | **质的飞跃** |

---

## 🔧 配置

### 环境变量

```bash
# 浏览器端口（默认 37778）
export GBROWSE_PORT=37778

# 用户数据目录（默认 ~/.gstack-browser/）
export GBROWSE_DATA_DIR=~/.gstack-browser/

# 空闲超时（默认 30 分钟）
export GBROWSE_IDLE_TIMEOUT=1800000
```

### 配置文件

```yaml
# ~/.gstack-browser/config.yaml

server:
  port: 37778
  host: localhost

browser:
  headless: true
  idle_timeout: 1800000  # 30 分钟
  user_data_dir: ~/.gstack-browser/

security:
  keychain_access: true
  cookie_encryption: true
```

---

## 📚 相关文档

- [gstack 官方仓库](https://github.com/garrytan/gstack)
- [ARCHITECTURE.md](https://github.com/garrytan/gstack/blob/main/ARCHITECTURE.md) - 架构设计
- [browse/src/server.ts](https://github.com/garrytan/gstack/blob/main/browse/src/server.ts) - 服务器实现
- [browse/src/snapshot.ts](https://github.com/garrytan/gstack/blob/main/browse/src/snapshot.ts) - 快照系统

---

## 🚀 下一步

1. **安装 gstack CLI**: `git clone https://github.com/garrytan/gstack.git && cd gstack && bun install && bun run build && bun link`
2. **测试浏览器**: `gstack browse --url "https://github.com"`
3. **导入 Cookies**: `gstack setup-browser-cookies`
4. **集成到工作流**: 在天龙 Agent 中使用 `gstack browse` 替代传统浏览器操作

---

**版本**: v1.0.0
**来源**: garrytan/gstack (36k+ Stars)
**作者**: Garry Tan (Y Combinator CEO)