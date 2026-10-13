---
license: UNKNOWN
name: unified-search
description: 智能统一搜索 - 一个入口调用所有搜索能力。自动分析查询意图，智能路由到最优搜索源（本地代码/Web搜索/知识图谱/GitHub），聚合结果并排序。支持 MCP 懒加载，节省 84% TOKEN。
github_repo: modelcontextprotocol/servers
github_hash: 4503e2d12b799448cd05f789dd40f9643a8d1a6c
last_updated: 2026-04-25
source_type: derived
version: 2.0.0
display_name: 超能搜
author: 九部天龙
created: 2026-02-26
tools: 
- curl: HTTP 客户端
- jq: JSON 处理
- grep: 文本搜索
triggers: ["unified search", "超能搜 (unified-search) Skill"]
---

# 超能搜 (unified-search) Skill

## 技能定位

**超能搜** 是智能统一搜索入口，自动分析查询意图并路由到最优搜索源，聚合所有搜索结果。

**V2.0 新特性**: MCP 懒加载支持 - 仅在需要时启动 MCP 服务器，大幅减少 TOKEN 消耗。

### 核心优势

| 功能 | 传统方式 | 超能搜 V2.0 |
|------|---------|-------------|
| 搜索入口 | 多个工具分散 | ✅ 单一入口 |
| 源选择 | 手动选择 | ✅ 智能路由 |
| 结果展示 | 分散显示 | ✅ 聚合排序 |
| **MCP 管理** | 预加载所有 MCP | ✅ **按需懒加载** |
| **启动 TOKEN** | ~5000 tokens | ✅ **~800 tokens (84% ↓)** |
| **启动时间** | ~15s | ✅ **~3s (80% ↓)** |
| **内存占用** | ~500MB | ✅ **~80MB (84% ↓)** |

## 核心功能

### 1. 智能查询分析

```bash
# 自动识别查询类型
超能搜 "React useEffect 使用方法"        # → Web 技术搜索 (Exa)
超能搜 "TODO 注释在哪里"                # → 本地代码搜索 (mgrep)
超能搜 "我之前说过什么关于架构的"        # → 知识图谱 (memory)
超能搜 "九部天龙仓库地址"               # → GitHub 搜索
超能搜 "今天的 AI 新闻"                 # → Web 通用搜索 (Brave)
```

### 2. 多源聚合搜索

```bash
# 并行搜索所有源，聚合结果
超能搜 --all "Claude Code 教程"

# 输出格式:
## 🔍 搜索结果: Claude Code 教程

### 📚 知识图谱 (1 条)
- 你之前收藏过 Claude Code 最佳实践...

### 💻 本地代码 (2 条)
- docs/CLAUDE.md: 九部天龙核心引擎...
- skills/github-cli/: GitHub 操作 via gh CLI...

### 🌐 Web 搜索 (10 条)
- [Exa] Claude Code 官方文档...
- [Brave] Claude Code 使用教程...
...
```

### 3. 搜索源层级

```
第一层: 知识图谱 (memory/agentdb)
  ↓ 未命中
第二层: 本地代码 (mgrep/github-cli)
  ↓ 未命中
第三层: 搜索缓存
  ↓ 未命中
第四层: Web 搜索 (search-cli: Brave + Exa)
```

### 4. 智能缓存

```bash
# 首次搜索 - 调用 Web API
超能搜 "React Server Components"

# 二次搜索 - 直接返回缓存（秒级响应）
超能搜 "React Server Components"

# 缓存管理
超能搜 --cache-clear      # 清空缓存
超能搜 --cache-stats      # 缓存统计
```

### 5. MCP 懒加载 (V2.0 新特性)

**超能搜 V2.0** 引入 MCP 懒加载机制，仅在需要时启动 MCP 服务器，大幅减少 TOKEN 消耗。

#### 核心优势

| 指标 | 预加载 MCP | 懒加载 MCP | 改善 |
|------|-----------|-----------|------|
| 启动 TOKEN | ~5000 | ~800 | **84% ↓** |
| 启动时间 | ~15s | ~3s | **80% ↓** |
| 内存占用 | ~500MB | ~80MB | **84% ↓** |
| 首次搜索 | 0s | +2-3s | 可接受 |

#### MCP 服务器支持

| MCP 服务器 | 触发关键词 | 空闲超时 | 用途 |
|-----------|-----------|----------|------|
| **Brave Search** | web, search, news, 通用 | 30 分钟 | 通用 Web 搜索 |
| **Exa** | tech, code, programming, API, React | 20 分钟 | 技术/代码搜索 |
| **Relace** | explore, 智能探索, 分析 | 15 分钟 | 智能代码探索 |
| **GitHub** | repo, pr, issue, 仓库 | 25 分钟 | GitHub 搜索 |
| **Elasticsearch** | enterprise, 企业, 大规模 | 30 分钟 | 企业级搜索 |
| **Filesystem** | file, local, 文件 | 20 分钟 | 文件系统访问 |

#### MCP 管理命令

```bash
# 查看所有 MCP 状态
~/.claude/skills/unified-search/bin/mcp_manager.sh status

# 智能启动（基于查询内容）
~/.claude/skills/unified-search/bin/mcp_manager.sh smart "React 教程"

# 手动管理
~/.claude/skills/unified-search/bin/mcp_manager.sh start exa
~/.claude/skills/unified-search/bin/mcp_manager.sh stop exa

# 统计信息
~/.claude/skills/unified-search/bin/mcp_manager.sh stats
```

#### 自动清理

```bash
# 查看活动状态
~/.claude/skills/unified-search/bin/mcp_auto_cleanup.sh stats

# 清理空闲 MCP
~/.claude/skills/unified-search/bin/mcp_auto_cleanup.sh cleanup

# 模拟运行
~/.claude/skills/unified-search/bin/mcp_auto_cleanup.sh dry-run

# 集成到 cron（每 10 分钟清理一次）
*/10 * * * * ~/.claude/skills/unified-search/bin/mcp_auto_cleanup.sh cleanup
```

#### 工作流程

```
用户搜索 "React 教程"
    ↓
unified-search 分析器
    ↓
识别为 tech_web 查询
    ↓
检查 Exa MCP 是否运行
    ├─ 已运行 → 直接调用
    └─ 未运行 → 启动 Exa MCP (2-3s) → 调用
    ↓
返回结果
    ↓
20 分钟后自动清理（如果未使用）
```

#### 降级策略

如果 MCP 启动失败或不可用，系统会自动降级到 API 备用方案：

```bash
# 尝试使用 Exa MCP
ensure_mcp "exa"
    ↓ 失败
# 降级到 Exa API
search_web_exa_api "$query"
```

## 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│              超能搜 V2.0 (unified-search)                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🧠 查询分析器 (bin/analyzer.sh)                            │
│     ├── 关键词提取                                           │
│     ├── 意图识别 (5 类查询)                                  │
│     └── 上下文理解                                           │
│                                                             │
│  🧭 智能路由器 (bin/router.sh)                              │
│     ├── 知识层: memory MCP → agentdb                        │
│     ├── 代码层: mgrep (优先) + grep (降级)                   │
│     ├── Web层: Exa MCP (技术) + Brave MCP (通用)            │
│     ├── GitHub层: GitHub MCP + Relace MCP (代码探索)        │
│     └── 企业层: Elasticsearch MCP (可选)                    │
│                                                             │
│  🔄 结果聚合器 (bin/aggregator.sh)                          │
│     ├── 去重 (URL + 文件路径)                                 │
│     ├── 相关性排序 (score + source weight)                  │
│     ├── 智能摘要 (AI-generated)                              │
│     └── Markdown 格式化                                      │
│                                                             │
│  💾 缓存管理器 (bin/cache.sh)                               │
│     ├── 多级缓存 (L1: 内存, L2: 磁盘)                        │
│     ├── 智能预热 (常用查询)                                  │
│     ├── 失效策略 (TTL + 主动失效)                            │
│     └── 命中率统计                                           │
│                                                             │
│  ⚙️  MCP 管理器 (bin/mcp_manager.sh) [V2.0 新增]            │
│     ├── 懒加载启动（按需）                                    │
│     ├── 状态监控                                            │
│     ├── 自动清理                                            │
│     └── 降级策略 (MCP → API)                                │
│                                                             │
│  🧹 自动清理 (bin/mcp_auto_cleanup.sh) [V2.0 新增]          │
│     ├── 空闲检测                                            │
│     ├── 定时清理 (cron 支持)                                 │
│     └── 资源释放                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 使用场景

### 场景 1: 代码调研 (01调研师)

```bash
# 查询本地代码
超能搜 "认证流程在哪里实现"

# 输出:
## 💻 本地代码搜索结果

**src/auth/login.ts**
```typescript
export async function login(credentials) {
  // ...
}
```

**docs/auth-flow.md**
```markdown
# 认证流程设计
1. 用户登录
2. Token 验证
3. 会话管理
```
```

### 场景 2: 技术问题解决 (03构建师)

```bash
# 查询 Web 技术文档
超能搜 "Next.js 15 app router 最佳实践"

# 自动路由到 Exa (技术内容优先)
# 返回高质量教程和文档
```

### 场景 3: 知识回顾 (07记录师)

```bash
# 查询知识图谱
超能搜 "之前讨论过九部天龙什么"

# 从 memory/agentdb 检索相关概念和对话
```

### 场景 4: 综合搜索

```bash
# 搜索所有源
超能搜 --all "微服务架构设计"

# 聚合本地笔记 + Web 文档 + GitHub 仓库
```

## 搜索源配置

### 知识图谱搜索

```bash
# lib/search_memory.sh
# 优先级: 1

# Memory MCP (知识图谱)
memory_search() {
  mcp__memory__search_nodes "$1"
}

# AgentDB (向量数据库)
agentdb_search() {
  mcp__agentdb__search "$1"
}
```

### 本地代码搜索

```bash
# lib/search_local.sh
# 优先级: 2

# mgrep (语义代码搜索)
mgrep_search() {
  mgrep "$1" 2>/dev/null || \
    grep -r "$1" --include="*.ts" --include="*.md" . 2>/dev/null
}

# GitHub CLI (仓库搜索)
github_search() {
  gh repo list --limit 10 --search "$1"
}
```

### Web 搜索

```bash
# lib/search_web.sh
# 优先级: 4

# search-cli (Brave + Exa)
web_search() {
  # 技术内容用 Exa
  if is_tech_query "$1"; then
    search_exa "$1"
  # 通用内容用 Brave
  else
    search_brave "$1"
  fi
}
```

## 命令参数

```bash
超能搜 [选项] "查询内容"

选项:
  --all              搜索所有源（默认: 智能选择）
  --local            仅搜索本地代码
  --web              仅搜索 Web
  --memory           仅搜索知识图谱
  --github           仅搜索 GitHub
  --cache-stats      显示缓存统计
  --cache-clear      清空缓存
  --no-cache         禁用缓存
  --format json      输出 JSON 格式
  --verbose          显示详细过程

示例:
  超能搜 "React 最佳实践"
  超能搜 --all "微服务架构"
  超能搜 --local "TODO 注释"
  超能搜 --web "AI 新闻"
```

## 查询类型识别规则

```bash
# 本地代码关键词
本地代码 = 代码 | 函数 | 文件 | 项目 | 实现 | TODO | FIXME

# GitHub 关键词
GitHub = repo | 仓库 | github | pr | issue

# 知识图谱关键词
知识 = 记住 | 之前 | 历史 | 我们 | 讨论

# 技术内容关键词
技术 = 编程 | API | 教程 | github | 文档 | 框架

# 默认: Web 通用搜索
```

## 性能优化

### 缓存策略

```bash
# 缓存位置
CACHE_DIR="$HOME/.cache/unified-search"
CACHE_TTL=3600  # 1小时

# 缓存 Key
CACHE_KEY=$(echo "$1" | md5sum | cut -d' ' -f1)

# 缓存命中
if [ -f "$CACHE_DIR/$CACHE_KEY.json" ]; then
  # 检查是否过期
  if [ $(find "$CACHE_DIR/$CACHE_KEY.json" -mmin -60 | wc -l) -gt 0 ]; then
    cat "$CACHE_DIR/$CACHE_KEY.json"
    return 0
  fi
fi
```

### 并行搜索

```bash
# 同时搜索多个源
parallel_search() {
  memory_search "$1" > /tmp/memory.json &
  mgrep_search "$1" > /tmp/mgrep.json &
  web_search "$1" > /tmp/web.json &

  wait  # 等待全部完成

  # 聚合结果
  jq -s '{memory: .[0], local: .[1], web: .[2]}' \
    /tmp/memory.json /tmp/mgrep.json /tmp/web.json
}
```

## 错误处理

```bash
# 优雅降级
fallback_search() {
  # 尝试主搜索源
  result=$(primary_search "$1")

  if [ -z "$result" ]; then
    echo "⚠️  主搜索源未命中，使用备用源..."
    result=$(fallback_search "$1")
  fi

  echo "$result"
}

# 超时处理
timeout_search() {
  timeout 30 search "$1" || {
    echo "❌ 搜索超时，请稍后重试"
    return 1
  }
}
```

## 配置文件

### config/weights.json

```json
{
  "sources": {
    "memory": {
      "priority": 1,
      "weight": 0.9,
      "enabled": true
    },
    "local": {
      "priority": 2,
      "weight": 0.8,
      "enabled": true
    },
    "github": {
      "priority": 2,
      "weight": 0.7,
      "enabled": true
    },
    "web_brave": {
      "priority": 4,
      "weight": 0.6,
      "enabled": true
    },
    "web_exa": {
      "priority": 4,
      "weight": 0.8,
      "enabled": true
    }
  }
}
```

### config/cache.conf

```bash
# 缓存配置
CACHE_ENABLED=true
CACHE_TTL=3600
CACHE_MAX_SIZE=1000
CACHE_DIR="$HOME/.cache/unified-search"
```

## 与现有工具对比

| 功能 | 传统方式 | 超能搜 |
|------|---------|--------|
| 本地代码 | `mgrep "..."` | `超能搜 "..."` (自动识别) |
| Web 搜索 | `/search-cli "..."` | `超能搜 "..."` (自动路由) |
| 知识检索 | 手动查询 memory | `超能搜 "..."` (自动调用) |
| GitHub | `gh repo search` | `超能搜 "..."` (智能选择) |
| 结果聚合 | 手动汇总多个源 | ✅ 自动聚合排序 |
| 缓存 | ❌ 无 | ✅ 智能缓存 |

## 依赖检查

```bash
# 检查依赖
check_dependencies() {
  # 必需工具
  command -v curl >/dev/null || echo "❌ 缺少 curl"
  command -v jq >/dev/null || echo "❌ 缺少 jq"
  command -v grep >/dev/null || echo "❌ 缺少 grep"

  # 可选工具
  command -v mgrep >/dev/null || echo "⚠️  建议安装 mgrep"
  command -v gh >/dev/null || echo "⚠️  建议安装 gh CLI"

  # MCP 服务
  # memory, agentdb 等由 Claude Code 管理
}
```

## 示例对话

**用户**: 找到所有 TODO 注释

**超能搜**:
```bash
# 识别为本地代码查询
# 调用 mgrep
mgrep "Find all TODO, FIXME, and HACK comments"
```

**用户**: React Server Components 怎么用？

**超能搜**:
```bash
# 识别为技术内容查询
# 调用 search-cli (Exa)
search_exa "React Server Components tutorial"
```

**用户**: 我之前说的九部天龙是什么？

**超能搜**:
```bash
# 识别为知识图谱查询
# 调用 memory MCP
mcp__memory__search_nodes "九部天龙"
```

**用户**: 搜索"微服务架构"的所有信息

**超能搜**:
```bash
# 使用 --all 参数
# 并行搜索所有源并聚合
超能搜 --all "微服务架构设计"
```

## 最佳实践

### 1. 查询优化

```bash
# ✅ 好的查询（具体、有上下文）
超能搜 "React useEffect 依赖数组为空时的行为"
超能搜 "九部天龙中的02架构师职责"

# ❌ 差的查询（模糊）
超能搜 "useEffect"
超能搜 "架构师"
```

### 2. 结果验证

```bash
# 查看搜索来源
超能搜 --verbose "查询内容"

# 输出会显示每个搜索源的结果数量
```

### 3. 缓存管理

```bash
# 定期清理缓存
超能搜 --cache-clear

# 查看缓存命中率
超能搜 --cache-stats
```

## 扩展性

### 添加新搜索源

```bash
# 1. 在 lib/ 创建新搜索函数
# lib/search_custom.sh
custom_search() {
  # 你的搜索逻辑
}

# 2. 在 router.sh 添加路由
route_search() {
  # ...
  case $query_type in
    "custom")
      custom_search "$query"
      ;;
  esac
}

# 3. 在 config/weights.json 添加配置
"custom": {
  "priority": 3,
  "weight": 0.7,
  "enabled": true
}
```

## 参考资源

- [mgrep 文档](../mgrep/SKILL.md)
- [search-cli 文档](../search-cli/SKILL.md)
- [web-fetch 文档](../web-fetch/SKILL.md)
- [github-cli 文档](../github-cli/SKILL.md)
- [Memory MCP](https://github.com/modelcontextprotocol/servers)

---

**版本**: v2.0.0
**维护者**: 九部天龙
**最后更新**: 2026-02-21

## V2.0 更新日志

- ✅ 新增 MCP 懒加载支持（节省 84% TOKEN）
- ✅ 新增 MCP 管理器 (`mcp_manager.sh`)
- ✅ 新增自动清理脚本 (`mcp_auto_cleanup.sh`)
- ✅ 更新搜索脚本集成 MCP 懒加载

---

## 协同：与 dsh-web-search-pro（阶段 40.2 · 2026-08-24）

> **TL;DR**：本 skill 的"智能路由"层应**优先指向 dsh-web-search-pro（DSH 用户）/ anysearch V3.1（天龙用户）**，而不是自带的 Exa + Brave + mgrep + memory + GitHub 五源。

### 路由优先级升级（推荐路径）

```
用户当前在哪跑?
├── DSH GUI + dsh-web-search-pro@0.1.8 已装 ──► 走 dsh-web-search-pro（11 工具）
│                                              └─ 不需要 MCP 懒加载（web-search-pro 自带持久化）
├── DSH GUI + 未装 web-search-pro ──► 走 anysearch V3.1（DSH bridge probe exit=1 时）
├── 纯天龙 / Claude Code ──► 走 anysearch V3.1（4 镜像 CLI）
└── 本 skill 自带的 Exa / Brave / mgrep / memory / GitHub ──► 仍作为"无任何 search skill 时的最后兜底"
```

### 性能对比（DSH 用户场景）

| 维度 | unified-search 自带 Exa | dsh-web-search-pro |
|------|-------------------------|---------------------|
| 启动 TOKEN | ~800 (懒加载后) | 0（DSH 已加载）|
| 单次 search 耗时 | 1-3s | 0.5-2s（含缓存命中时 <100ms）|
| 持久化 | ❌ | ✅ SQLite + LRU |
| 中文社区 | ❌ | ✅ 小红书/知乎/微博/豆瓣/贴吧/抖音/快手 |
| 凭证安全 | 用户手工 | DSH Credentials 服务 |

### 关联

- `dragon-engine/skills/dsh-web-search-pro-bridge/SKILL.md` — 天龙侧桥 V1.0
- `dragon-engine/skills/anysearch/SKILL.md` V3.1 — DSH bridge 探测
- `memory/stage-40-announce.md` — 阶段 40 总验收

- ✅ 改进架构设计文档
