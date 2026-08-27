---
name: debug
description: 调试主流程 - 系统化问题定位和修复
invokable: true
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, TodoWrite
---
## Context

- Error message: !`echo "请提供完整的错误信息"`
- Error location: !`echo "请说明错误发生的文件和行号"`

## Your Task

执行系统化调试流程：

### 步骤 1: 复现问题
- 收集完整的错误信息
- 确定问题的可复现性
- 记录复现步骤

### 步骤 2: 定位根因
```bash
# 查看详细错误
npm run dev 2>&1 | head -50

# 查看日志
tail -100 logs/app.log

# 运行测试定位
npm test -- --grep "相关测试"
```

### 步骤 3: 分析调用链
- 使用日志追踪执行路径
- 检查数据流向
- 验证条件分支

### 步骤 4: 制定修复方案
- 确定最小修复点
- 编写或修改测试
- 实施修复

### 步骤 5: 验证修复
```bash
# 运行相关测试
npm test -- --grep "修复相关的测试"

# 手动复现验证
```

## 调试工具清单

| 工具 | 用途 |
|------|------|
| console.log | 快速打印 |
| debugger | 断点调试 |
| 日志系统 | 生产追踪 |
| 测试框架 | 自动化验证 |
| 静态分析 | 类型检查 |

## 注意事项

- 一次只改一个变量
- 记录假设和验证结果
- 修复后运行完整测试
- 更新相关文档
