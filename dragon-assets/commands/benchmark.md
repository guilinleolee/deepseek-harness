---
name: benchmark
description: 性能基准测试 - 测量关键代码路径性能
invokable: true
allowed-tools: Read, Glob, Bash, Write, Edit, TodoWrite
---
## Context

- Test files: !`find . -name "benchmark*.ts" -o -name "*benchmark*.test.ts" 2>/dev/null | head -5`
- Performance requirements: !`cat package.json 2>/dev/null | grep -A5 '"perf"' || echo "无性能要求"`

## Your Task

执行性能基准测试：

### 步骤 1: 安装基准测试工具
```bash
# Node.js
npm install --save-dev benchmark

# 或使用内置工具
npm install --save-dev vitest bench
```

### 步骤 2: 编写基准测试
```typescript
// benchmark/data-processing.test.ts
import { bench, describe } from 'vitest';
import { processData, parseRecords, aggregateStats } from '../src/data-processor';

describe('Data Processing Performance', () => {
  const testData = Array.from({ length: 10000 }, (_, i) => ({
    id: i,
    name: `Item ${i}`,
    value: Math.random() * 100,
    timestamp: Date.now() - i * 1000
  }));

  bench('processData - 10000 records', () => {
    processData(testData);
  });

  bench('parseRecords - JSON parsing', () => {
    const json = JSON.stringify(testData);
    parseRecords(json);
  });

  bench('aggregateStats - 计算统计', () => {
    aggregateStats(testData);
  });
});
```

### 步骤 3: 运行基准测试
```bash
# 运行基准测试
npm run bench

# 对比分支性能
git checkout main
npm run bench > baseline.txt

git checkout feature-branch
npm run bench > feature.txt

# 对比结果
diff baseline.txt feature.txt
```

### 步骤 4: 分析结果
```
Results:
  processData (10000 records)
    baseline:  245ms ± 3.2%
    feature:  189ms ± 2.8%  (-22.9% faster) ✓

  parseRecords (JSON)
    baseline:  89ms ± 1.5%
    feature:   92ms ± 1.8%  (+3.4% slower) ✗

Summary:
  ✓ Faster: 1 test
  ✗ Slower: 1 test
```

## 常见基准测试场景

| 场景 | 测量指标 | 目标 |
|------|---------|------|
| 数据库查询 | 响应时间 | < 100ms |
| API端点 | 吞吐量 | > 1000 req/s |
| 排序算法 | 操作次数 | O(n log n) |
| 内存使用 | 峰值内存 | < 512MB |
| 首屏加载 | FCP/LCP | < 1.5s |

## 性能回归检测

```yaml
# .github/workflows/benchmark.yml
name: Performance Regression
on: [pull_request]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run baseline benchmarks
        run: npm run bench -- --output baseline.json
        env:
          BENCHMARK_COMPARE: main

      - name: Run PR benchmarks
        run: npm run bench -- --output pr.json

      - name: Compare results
        run: |
          node scripts/compare-benchmarks.js baseline.json pr.json

      - name: Comment on PR
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              body: 'Performance comparison results...'
            })
```

## 注意事项

- 使用生产级数据量测试
- 多次运行取平均值
- 禁用开发工具和调试代码
- 记录环境信息（CPU/RAM/Node版本）
- 定期更新基准线
