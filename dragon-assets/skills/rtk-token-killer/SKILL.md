---
license: UNKNOWN
triggers: ["rtk token killer", "rtk-token-killer"]
---
# rtk-token-killer

## L0: 一句话描述 (≤15字)
LLM输出压缩60-90%

## L1: 使用场景 (50-100字)
RTK拦截CLI命令输出，过滤噪音、分组、截断、去重，适用于代码开发、测试验证、运维监控等场景的Token节省。零依赖，<10ms开销，100+命令自动覆盖。

## L2: 详细文档

### 核心能力

| 能力 | 说明 |
|------|------|
| **Smart Filtering** | 移除噪音、注释、样板代码 |
| **Grouping** | 聚合相似项（文件按目录、错误按类型） |
| **Truncation** | 保留相关上下文，截断冗余 |
| **Deduplication** | 折叠重复日志行并显示计数 |
| **Auto-Rewrite Hook** | 透明拦截Bash命令并重写为rtk等价命令 |

### 支持命令（100+）

| 类别 | 命令 |
|------|------|
| **文件** | ls, read, smart, find, grep, diff |
| **Git** | status, log, diff, add, commit, push, pull |
| **GitHub CLI** | pr list, pr view, issue list, run list |
| **测试** | jest, vitest, playwright test, pytest, go test, cargo test, rake test, rspec |
| **构建/检查** | cargo build, cargo clippy, ruff check, golangci-lint run, rubocop, tsc |
| **包管理** | pnpm list, pip list, pip outdated, bundle install, prisma generate |
| **云** | aws (sts/ec2/lambda/logs/s3), kubectl |
| **容器** | docker ps/images/logs, docker compose ps |

### 支持AI工具

Claude Code, GitHub Copilot, Cursor, Gemini CLI, Windsurf, Cline, Kilo Code, OpenCode

### 安装方式

```bash
# Homebrew (推荐)
brew install rtk

# 快速安装
curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh

# Cargo
cargo install --git https://github.com/rtk-ai/rtk

# 初始化AI工具
rtk init -g                    # Claude Code / Copilot
rtk init -g --gemini           # Gemini CLI
rtk init -g --agent cursor     # Cursor
rtk init --agent windsurf      # Windsurf
rtk init --agent cline         # Cline / Roo Code
rtk init --agent hermes        # Hermes
```

### 分析命令

```bash
rtk gain              # 节省统计摘要
rtk gain --graph       # ASCII图表（最近30天）
rtk gain --history     # 最近命令历史
rtk discover           # 发现未优化的节省机会
rtk session           # 跨会话的RTK采用情况
```

### 全局参数

```bash
-u, --ultra-compact   # ASCII图标、内联格式（额外Token节省）
-v, --verbose         # 增加详细程度 (-v, -vv, -vvv)
```

### Token节省示例

| 命令 | 节省比例 |
|------|---------|
| ls / tree | ~80% |
| cat / read | ~70% |
| git status | ~80% |
| cargo test / pytest | ~90% |
| cargo build / tsc | ~85% |

### 天龙岗位协同

| 岗位 | 协同命令 | 效果 |
|------|---------|------|
| 03构建师 | ls, grep, diff, cargo build, tsc | 开发效率+Token节省 |
| 04验证师 | pytest, jest, vitest, cargo test | 测试输出压缩 |
| 07记录师 | docker logs, kubectl logs | 日志分析压缩 |
| 08发布师 | ruff, golangci-lint, cargo clippy | CI/CD输出压缩 |
| 16-02监控运维师 | aws, docker, kubectl | 运维日志压缩 |

### 与现有天龙能力协同

| 天龙组件 | rtk-token-killer | 协同效果 |
|---------|-----------------|---------|
| token-optimizer (V8.35) | 输出层补充 | 60-90% vs 50-80%，+10% |
| gstack-browse (V8.44) | CLI输出专注 | 互补覆盖 |
| ai-regression-testing (V8.67) | 测试输出压缩 | 防止上下文污染 |

### 验证安装

```bash
rtk init -g --show
```

### 预期收益

| 指标 | 当前 | RTK集成后 | 提升 |
|------|------|-----------|------|
| Token节省 | 50-80% | 60-90% | +10% |
| 命令覆盖 | 部分（手动） | 100+自动 | +500% |
| 运维日志 | 无压缩 | 完整覆盖 | 新增能力 |
| 开销 | - | <10ms | 可忽略 |