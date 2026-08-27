---
name: profile
description: 性能分析 - 定位性能瓶颈和优化机会
invokable: true
allowed-tools: Read, Glob, Bash, Write, Edit
---
## Context

- Target endpoint: !`echo "请指定要分析的接口或页面"`
- Load test report: !`ls -la *.har *.apifront *.k6 2>/dev/null || echo "无负载测试报告"`

## Your Task

执行性能分析：

### 步骤 1: 收集指标
```bash
# 运行性能基准测试
npm run benchmark

# 生成火焰图
npm run profile

# 分析 Bundle
npm run analyze
```

### 步骤 2: 分析瓶颈
- **CPU瓶颈**: 密集计算、递归、大循环
- **内存瓶颈**: 泄漏、频繁GC、大数据结构
- **IO瓶颈**: 网络延迟、磁盘IO、数据库查询
- **渲染瓶颈**: DOM操作、布局抖动、重排重绘

### 步骤 3: 识别热点
```markdown
## 性能热点清单

| 热点 | 类型 | 影响 | 优化建议 |
|------|------|------|----------|
| functionX | CPU | 高 | 算法优化 |
| queryY | DB | 中 | 添加索引 |
```

### 步骤 4: 输出优化方案
```markdown
## 优化方案

### 1. 立即优化（低投入高回报）
- 缓存计算结果
- 懒加载非关键资源

### 2. 中期优化（中等投入）
- 算法优化
- 数据库索引

### 3. 长期优化（高投入）
- 架构重构
- 技术栈升级
```

## 性能指标目标

| 指标 | 目标值 | 警告阈值 |
|------|--------|---------|
| FCP | < 1.8s | > 3s |
| LCP | < 2.5s | > 4s |
| TTI | < 3.8s | > 7s |
| API响应 | < 200ms | > 500ms |

## 注意事项

- 优先优化高影响热点
- 权衡优化成本和收益
- 验证优化后的性能提升
- 持续监控避免退化
