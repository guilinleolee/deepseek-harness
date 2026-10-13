# 超能搜 (unified-search) - 智能统一搜索

> 🔍 **一个入口，调用所有搜索能力**

超能搜是智能统一搜索工具，自动分析查询意图并路由到最优搜索源，聚合所有搜索结果。

## ✨ 核心特性

- 🤖 **智能路由**: 自动识别查询类型，选择最优搜索源
- 📊 **多源聚合**: 并行搜索知识图谱、本地代码、Web、GitHub
- ⚡ **智能缓存**: 秒级响应，节省 API 调用
- 🎯 **精准排序**: 按相关性智能排序结果

## 🚀 快速开始

### 安装

```bash
# 克隆到技能目录
cd ~/.claude/skills/
git clone <repo-url> unified-search

# 添加执行权限
chmod +x unified-search/bin/*.sh
chmod +x unified-search/lib/*.sh
```

### 基本使用

```bash
# 智能搜索（自动选择源）
./unified-search/bin/unified-search.sh "React 最佳实践"

# 搜索所有源
./unified-search/bin/unified-search.sh --all "微服务架构"

# 仅搜索本地
./unified-search/bin/unified-search.sh --local "TODO 注释"

# 仅搜索 Web
./unified-search/bin/unified-search.sh --web "AI 新闻"

# 查看缓存统计
./unified-search/bin/unified-search.sh --cache-stats

# 清空缓存
./unified-search/bin/unified-search.sh --cache-clear
```

## 📖 搜索源

| 源 | 优先级 | 说明 |
|----|--------|------|
| 📚 知识图谱 | 1 | Memory MCP + AgentDB |
| 💻 本地代码 | 2 | mgrep + grep |
| 🐙 GitHub | 2 | gh CLI |
| 🌐 Web (Brave) | 4 | 通用内容搜索 |
| 🤖 Web (Exa) | 4 | 技术内容搜索 |

## 🧪 测试

```bash
# 运行测试套件
bash unified-search/tests/test_unified_search.sh
```

## ⚙️ 配置

编辑 `config/weights.json` 自定义搜索源权重和优先级。

## 📝 许可证

MIT License - 九部天龙
