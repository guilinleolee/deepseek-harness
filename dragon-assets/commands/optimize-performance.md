---
name: optimize-performance
description: 性能优化 - 针对具体性能问题的优化实施
invokable: true
allowed-tools: Read, Glob, Bash, Write, Edit, TodoWrite
---
## Context

- Performance report: !`ls -la *.html *.json 2>/dev/null | grep -i perf || echo "请提供性能报告"`
- Target metric: !`echo "请指定要优化的性能指标"`

## Your Task

执行性能优化：

### 步骤 1: 确定优化目标
- 明确当前性能数据
- 设定优化目标值
- 确定优化范围

### 步骤 2: 分析瓶颈根因
```bash
# 生成性能分析报告
npm run analyze:performance

# 分析 Bundle
npm run analyze:bundle

# 检查数据库查询
npm run log:slow-queries
```

### 步骤 3: 选择优化策略

#### 前端优化
| 策略 | 效果 | 成本 |
|------|------|------|
| 代码分割 | 高 | 中 |
| 懒加载 | 高 | 低 |
| 缓存 | 高 | 低 |
| Tree-shaking | 中 | 低 |
| 压缩 | 中 | 低 |

#### 后端优化
| 策略 | 效果 | 成本 |
|------|------|------|
| 数据库索引 | 高 | 中 |
| 查询优化 | 高 | 中 |
| 缓存 | 高 | 中 |
| 连接池 | 中 | 低 |
| 异步处理 | 中 | 高 |

### 步骤 4: 实施优化
```bash
# 应用优化
npm run build:prod

# 验证优化效果
npm run benchmark
```

### 步骤 5: 监控和验证
```bash
# 运行性能测试
npm run test:performance

# 部署并监控
npm run deploy:staging
```

## 优化优先级

1. **高价值低投入**: 立即执行
2. **高价值高投入**: 规划排期
3. **低价值低投入**: 低优先级
4. **低价值高投入**: 避免

## 注意事项

- 一次只做一个优化
- 记录优化前后的指标
- 确保优化不引入新问题
- 持续监控避免性能退化
