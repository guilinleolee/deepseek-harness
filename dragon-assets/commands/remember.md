---
name: remember
description: remember - 天龙记忆检索命令
invokable: true
---
# /remember - 天龙记忆检索命令

搜索历史记忆，与 claude-mem 集成。

## 使用方式

```bash
/remember [查询内容]     # 搜索历史记忆
/remember --timeline ID  # 获取时间线上下文
/remember --stats        # 查看记忆统计
/remember --export       # 导出记忆数据
```

## 功能说明

### 1. 记忆搜索

当用户提供查询内容时，使用 claude-mem MCP 工具搜索历史记忆：

```
search(query="查询内容", limit=10)
```

### 2. 时间线上下文

获取特定观察记录周围的时间线上下文：

```
timeline(observation_id=ID)
```

### 3. 记忆统计

查看当前记忆系统状态：
- 总会话数
- 总观察记录数
- 存储大小
- 最早/最新记录时间

### 4. 记忆导出

导出记忆数据为 JSON 格式，用于备份或迁移。

## 3层工作流

遵循 claude-mem 的 Token 高效工作流：

1. **Layer 1: search()** - 获取紧凑索引（~50-100 tokens/result）
2. **Layer 2: timeline()** - 获取时间线上下文
3. **Layer 3: get_observations()** - 获取完整详情（~500-1000 tokens/result）

**收益**: ~10x Token 节省

## 与 lessons.md 协同

- `/remember` 搜索自动记忆（claude-mem）
- lessons.md 存储手动记录的高质量经验
- 两者同时加载，lessons.md 优先级更高

## 天龙岗位映射

| 岗位 | 用途 |
|------|------|
| 07记录师 | 自动记录检索 |
| 01调研师 | 历史调研参考 |
| 00分析师 | 相似问题参考 |
| 04验证师 | 历史Bug修复参考 |

## 配置

确保 claude-mem 插件已安装：

```bash
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem
```

Web Viewer UI: http://localhost:37777