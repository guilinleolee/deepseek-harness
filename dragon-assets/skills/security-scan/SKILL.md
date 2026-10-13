---
license: UNKNOWN
name: security-scan
github_repo: affaan-m/everything-claude-code
github_hash: 4e66b2882da9afb9747468b08a253ca2f09c85f3
last_updated: 2026-04-25
source_type: derived
github: 
repo: affaan-m/everything-claude-code
path: skills/security-scan
branch: main
date: 2026-03-30
note: Source repo unreachable; based on upstream ECC project
triggers: ["security scan", "Security Scan — Claude Code配置安全扫描"]
---

# Security Scan — Claude Code配置安全扫描

> 来源: [affaan-m/everything-claude-code/skills/security-scan](https://github.com/affaan-m/everything-claude-code)

## 功能概述

使用AgentShield审计Claude Code配置的安全问题，检测配置漏洞、注入风险和错误配置。覆盖CLAUDE.md、settings.json、MCP服务器、hooks和agent定义。

## 何时激活

- 设置新的Claude Code项目
- 修改`.claude/settings.json`、CLAUDE.md或MCP配置后
- 提交配置更改前
- 入职已有Claude Code配置的仓库时
- 定期安全检查

## 扫描范围

| 文件 | 检查项 |
|------|--------|
| `CLAUDE.md` | 硬编码密钥、自动运行指令、提示注入模式 |
| `settings.json` | 过度宽松的允许列表、缺失的拒绝列表、危险绕过标志 |
| `mcp.json` | 危险MCP服务器、硬编码env密钥、npx供应链风险 |
| `hooks/` | 通过插值的命令注入、数据泄露、静默错误抑制 |
| `agents/*.md` | 无限制的工具访问、提示注入面、缺失模型规格 |

## 前置条件

AgentShield必须已安装：

```bash
# 检查是否安装
npx ecc-agentshield --version

# 全局安装(推荐)
npm install -g ecc-agentshield

# 或直接通过npx运行
npx ecc-agentshield scan .
```

## 使用方法

### 基础扫描

```bash
# 扫描当前项目
npx ecc-agentshield scan

# 扫描指定路径
npx ecc-agentshield scan --path /path/to/.claude

# 设置最低严重性过滤
npx ecc-agentshield scan --min-severity medium
```

### 输出格式

```bash
# 终端输出(默认) — 带评分的彩色报告
npx ecc-agentshield scan

# JSON — 用于CI/CD集成
npx ecc-agentshield scan --format json

# Markdown — 用于文档
npx ecc-agentshield scan --format markdown

# HTML — 自包含深色主题报告
npx ecc-agentshield scan --format html > security-report.html
```

### 自动修复

```bash
npx ecc-agentshield scan --fix
```

自动修复包括:
- 用环境变量引用替换硬编码密钥
- 收紧通配符权限为范围替代方案
- 不修改手动建议

### Opus深度分析

运行对抗性三Agent管道进行深度分析：

```bash
export ANTHROPIC_API_KEY=your-key
npx ecc-agentshield scan --opus --stream
```

运行:
1. **攻击者(红队)** — 发现攻击向量
2. **防御者(蓝队)** — 推荐加固方案
3. **审计者(最终裁决)** — 综合双方观点

### GitHub Action

添加到CI管道：

```yaml
- uses: affaan-m/agentshield@v1
  with:
    path: '.'
    min-severity: 'medium'
    fail-on-findings: true
```

## 严重性等级

| 等级 | 分数 | 含义 |
|------|------|------|
| A | 90-100 | 安全配置 |
| B | 75-89 | 轻微问题 |
| C | 60-74 | 需要注意 |
| D | 40-59 | 重大风险 |
| F | 0-39 | 严重漏洞 |

## 天龙引擎集成

### 适用岗位

| 岗位 | 集成方式 | 增强能力 |
|------|---------|---------|
| **05安全师** | 安全扫描 | 配置审计 + AgentShield集成 |
| **08发布师** | CI/CD安全门控 | GitHub Action + 扫描报告 |
| **02架构师** | 安全架构设计 | 通配符权限收紧 |

### 天龙引擎增强

```
┌─────────────────────────────────────────────────────────────┐
│ 天龙引擎安全扫描体系                                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   AgentShield扫描:                                          │
│   ├── CLAUDE.md      → 硬编码密钥/提示注入                 │
│   ├── settings.json   → 权限配置                            │
│   ├── mcp.json       → MCP服务器安全                      │
│   ├── hooks/         → 命令注入/数据泄露                   │
│   └── agents/*.md    → Agent权限面                        │
│                                                             │
│   严重性分级:                                              │
│   🔴 CRITICAL → 立即修复                                   │
│   🟠 HIGH      → 生产前修复                               │
│   🟡 MEDIUM    → 推荐修复                                  │
│   🔵 INFO      → 知晓即可                                  │
│                                                             │
│   协同技能:                                                 │
│   ├── /deployment-patterns → CI/CD安全门控                │
│   ├── /docker-patterns    → 容器安全配置                  │
│   └── /ai-first-engineering → 安全假设审查               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 核心命令

```bash
# 安全扫描
[@05] 扫描项目配置安全问题
[@05] 使用AgentShield进行安全审计

# CI/CD集成
[@发布师] 在CI流水线中添加安全扫描步骤
[@发布师] 配置fail-on-findings自动阻止危险配置

# 定期检查
[@05] 每月执行一次配置安全扫描
```

## 关键发现解读

### 严重发现(立即修复)
- 配置文件中硬编码的API密钥或令牌
- 允许列表中的`Bash(*)`(无限制shell访问)
- hooks中通过`${file}`插值的命令注入
- 运行shell的MCP服务器

### 高风险发现(生产前修复)
- CLAUDE.md中的自动运行指令(提示注入向量)
- 缺失权限拒绝列表
- 具有不必要Bash访问的Agent

### 中等风险发现(推荐修复)
- hooks中的静默错误抑制(`2>/dev/null`, `|| true`)
- 缺失PreToolUse安全钩子
- MCP服务器配置中的`npx -y`自动安装

## 参考资料

- **GitHub**: [github.com/affaan-m/agentshield](https://github.com/affaan-m/agentshield)
- **npm**: [npmjs.com/package/ecc-agentshield](https://www.npmjs.com/package/ecc-agentshield)

---

**版本**: V1.0 | **兼容性**: 天龙引擎 V8.67+ | **来源**: ECC
