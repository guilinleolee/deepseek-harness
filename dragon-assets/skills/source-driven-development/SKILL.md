---
license: UNKNOWN
triggers: ["source driven development", "source-driven-development"]
---
# source-driven-development

## L0: 一句话描述 (≤15字)
源码优先开发，考古摸底，顺藤摸瓜。

## L1: 使用场景 (50-100字)
适用于接手陌生代码库或需要深度理解现有系统架构的场景。核心价值在于"考古摸底"——通过源码阅读、依赖分析、演进历史追踪，还原系统的真实设计意图，而非依赖过时文档或二手解读。

## L2: 详细文档

# Source-Driven Development (源码驱动开发)

> **核心理念**: "Code is the ground truth. Documentation is a lie." (源码即地面实况，文档只是二手解读)
> 每个复杂系统必须先从源码考古，否则基于文档的决策都是空中楼阁。

## 源码考古四步法

### Step 1: 拓扑扫描 (Topology Scan)
```bash
# 目录结构鸟瞰
find . -type f -name "*.py" -o -name "*.js" -o -name "*.ts" | head -50
ls -la

# 依赖关系图
grep -r "import\|require\|from" --include="*.py" --include="*.js" --include="*.ts" | \
  sed 's/:.*//' | sort | uniq -c | sort -rn | head -20

# 包管理文件
cat package.json 2>/dev/null || cat pyproject.toml 2>/dev/null || cat requirements.txt 2>/dev/null
```

### Step 2: 入口追踪 (Entry Trace)
```bash
# 找出main/entrypoint
grep -r "def main\|if __name__\|async def main\|app = \|new App\|createApp" \
  --include="*.py" --include="*.js" --include="*.ts" -l

# API路由入口
grep -r "@app\|@router\|@bp\|@route\|app\.\|Router\|Blueprint" \
  --include="*.py" --include="*.js" --include="*.ts" -l | head -10
```

### Step 3: 核心模块识别 (Core Module ID)
```bash
# 高频导入模块
grep -rh "import\|from.*import" --include="*.py" | \
  awk -F'import|from' '{print $2}' | awk '{print $1}' | \
  sort | uniq -c | sort -rn | head -20

# 核心数据流
grep -rn "class.*Repository\|class.*Service\|class.*Controller" \
  --include="*.py" --include="*.js" --include="*.ts"
```

### Step 4: 演进历史考古 (Git Archaeology)
```bash
# 关键文件提交历史
git log --oneline -20 -- <critical_file>

# 架构变更节点
git log --oneline --all | grep -i "refactor\|architecture\|restructure\|rewrite" | head -10

# Blame可疑代码
git blame <suspicious_file> | head -30
```

## SDD-CACHE Hook (跨会话HTTP缓存)

源码驱动开发阶段需要频繁查阅官方文档，SDD-CACHE Hook提供304缓存机制：

### 工作原理
```
PreToolUse (WebFetch):
  1. 计算URL的sha256作为key (截取前32位)
  2. 检查 ~/.claude/sdd-cache/<key>.json 是否存在
  3. 发送HEAD请求 + If-Modified-Since / If-None-Match 验证
  4. 如果304 Not Modified → 使用缓存内容
  5. 如果有新内容 → 获取并更新缓存

PostToolUse (WebFetch):
  1. 捕获响应内容
  2. 记录validators (lastModified, etag, contentLength)
  3. 存储到 ~/.claude/sdd-cache/<key>.json
```

### 调试模式
```bash
SDD_CACHE_DEBUG=1 claude  # 启用调试输出
```

## 与天龙引擎协同

| 天龙组件 | 协同方式 |
|---------|---------|
| 01调研师 | 考古摸底 = 源码优先开发的执行层 |
| 02架构师 | 拓扑扫描作为架构分析的输入 |
| 03构建师 | 核心模块识别作为修改前的必要步骤 |
| 06审查师 | git blame作为Code Review的辅助工具 |
| spec-driven-development | 考古结论作为SPEC格式化的输入 |

## 版本

- V1.0: 2026-04-30 初始集成，基于天龙引擎源码考古方法论
