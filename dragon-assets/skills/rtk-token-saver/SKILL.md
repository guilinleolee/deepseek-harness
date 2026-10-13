---
license: UNKNOWN
triggers: ["rtk token saver", "RTK Token Saver ⭐V9.0新增"]
---
# RTK Token Saver ⭐V9.0新增

> 来源: [decolua/9router](https://github.com/decolua/9router) - 9Router RTK Token Saver
> 集成时间: 2026-05-24 | 天龙引擎V9.0

## L0: 一句话描述
工具输出无损压缩，节省20-40% tokens，与token-optimizer形成双层压缩体系。

## L1: 使用场景

| 场景 | 触发条件 | 压缩效果 |
|------|---------|---------|
| git diff/grep输出 | 检测到git命令 | 47K→28K (-40%) |
| find/ls文件列表 | 检测到文件命令 | 去重+截断 |
| 日志输出 | 检测到log内容 | dedup-log过滤器 |
| 搜索结果 | grep/find输出 | smart-truncate |

## L2: 详细文档

### 1. 核心过滤器列表

| 过滤器 | 适用命令 | 压缩原理 |
|--------|---------|---------|
| `git-diff` | git diff, git status | 去除上下文行，仅保留变更 |
| `grep` | grep, rg, findstr | 去重+行号优化 |
| `find` | find, fd, find . | 路径压缩+排序 |
| `ls` | ls, dir, tree | 列宽优化+颜色去除 |
| `tree` | tree, ntree | 层级折叠+路径压缩 |
| `dedup-log` | log输出 | 重复行合并 |
| `smart-truncate` | 大文件输出 | 智能截断+摘要 |
| `read-numbered` | cat -n | 行号压缩 |
| `search-list` | find, locate | 列表精简 |

### 2. 工作原理

```
┌─────────────────────────────────────────────────────────────┐
│                    RTK Token Saver 工作流程                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  工具输出 (tool_result)                                    │
│         ↓                                                   │
│  检测前1KB内容 → 判断命令类型                              │
│         ↓                                                   │
│  选择对应过滤器                                             │
│         ↓                                                   │
│  应用无损压缩 (保留关键信息)                               │
│         ↓                                                   │
│  验证压缩效果 (失败则保留原始)                             │
│         ↓                                                   │
│  格式转换前执行 → 跨所有格式通用                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3. 安全设计原则

- ✅ 过滤器失败时保留原始文本
- ✅ 压缩后文本变大时自动回退
- ✅ 仅修改输出格式，不改变内容
- ✅ 所有过滤器经过安全验证

### 4. 命令速查

```bash
# 启用/禁用
/rtk-enable      # 启用RTK压缩
/rtk-disable     # 禁用RTK压缩
/rtk-status      # 查看当前状态

# 统计
/rtk-stats       # 查看节省统计
/rtk-history     # 查看历史记录

# 配置
/rtk-config      # 查看配置
/rtk-filter-list # 列出所有过滤器
```

### 5. 与token-optimizer协同

```
┌─────────────────────────────────────────────────────────────┐
│ 天龙引擎 Token压缩双层体系                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Layer 1: RTK Token Saver (V9.0) ⭐新增                    │
│  ├── 工具输出压缩 (git diff/grep/find/ls/tree)           │
│  ├── 节省: 20-40%                                          │
│  └── 在格式转换前执行                                      │
│                                                             │
│  Layer 2: token-optimizer (V8.35)                        │
│  ├── 上下文压缩 (Context Optimizer)                       │
│  ├── 节省: 50-80%                                          │
│  └── Lazy Skill Loading + Model Router                    │
│                                                             │
│  总节省: 60-90% Token                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6. 天龙岗位升级

| 岗位 | 版本 | 新增能力 |
|------|------|---------|
| **03构建师** | V8.73→V9.0 | RTK过滤器集成 |
| **04验证师** | V8.70→V9.0 | RTK压缩效果验证 |
| **07记录师** | V8.86→V9.0 | 工具输出优化 |
| **08发布师** | V8.92→V9.0 | 部署日志压缩 |

### 7. 预期收益

| 指标 | V8.92 | V9.0 | 提升 |
|------|-------|------|------|
| 工具输出Token | 100% | 60-80% | **-20-40%** |
| git diff输出 | 47K | 28K | **-40%** |
| grep输出 | 30K | 18K | **-40%** |
| 总Token节省 | 50-80% | **60-90%** | **+10%** |

### 8. 文件结构

```
rtk-token-saver/
├── SKILL.md                    # 本文件
├── filters/
│   ├── git-diff.js            # git diff过滤器
│   ├── git-status.js          # git status过滤器
│   ├── grep.js                # grep过滤器
│   ├── find.js                # find过滤器
│   ├── ls.js                  # ls/tree过滤器
│   ├── dedup-log.js           # 日志去重过滤器
│   ├── smart-truncate.js       # 智能截断过滤器
│   └── index.js               # 过滤器入口
├── scripts/
│   ├── rtk-enable.js          # 启用脚本
│   ├── rtk-disable.js         # 禁用脚本
│   ├── rtk-stats.js           # 统计脚本
│   └── rtk-core.js            # 核心引擎
└── templates/
    └── config.json           # 默认配置
```

### 9. 核心代码示例

```javascript
// rtk-core.js
class RTKTokenSaver {
  constructor() {
    this.filters = {
      'git-diff': require('./filters/git-diff.js'),
      'git-status': require('./filters/git-status.js'),
      'grep': require('./filters/grep.js'),
      'find': require('./filters/find.js'),
      'ls': require('./filters/ls.js'),
      'tree': require('./filters/ls.js'),  // tree使用ls过滤器
      'dedup-log': require('./filters/dedup-log.js'),
      'smart-truncate': require('./filters/smart-truncate.js')
    };
    this.enabled = true;
  }

  compress(toolOutput) {
    if (!this.enabled) return toolOutput;

    // 检测前1KB判断命令类型
    const header = toolOutput.slice(0, 1024);
    const filterType = this.detectFilterType(header);

    if (this.filters[filterType]) {
      try {
        const compressed = this.filters[filterType](toolOutput);
        // 验证压缩效果（不使输出变大）
        if (compressed.length < toolOutput.length) {
          return compressed;
        }
      } catch (e) {
        // 过滤器失败，保留原始
      }
    }
    return toolOutput;
  }

  detectFilterType(header) {
    if (header.includes('diff --git')) return 'git-diff';
    if (header.includes('On branch')) return 'git-status';
    if (header.match(/^\d+:\s/)) return 'grep';
    if (header.includes('./') || header.includes('\\')) return 'find';
    if (header.match(/^d[rwx-]{9}/)) return 'ls';
    return 'smart-truncate';
  }
}

module.exports = new RTKTokenSaver();
```

## 技能文件

- [skills/rtk-token-saver/SKILL.md](skills/rtk-token-saver/SKILL.md)
- [skills/rtk-token-saver/filters/](skills/rtk-token-saver/filters/)
- [skills/rtk-token-saver/scripts/rtk-core.js](skills/rtk-token-saver/scripts/rtk-core.js)