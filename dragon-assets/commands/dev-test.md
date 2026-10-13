---
name: dev-test
description: 开发测试 - TDD开发流程中的测试编写和运行
invokable: true
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, TodoWrite
---
## Context

- Test framework: !`ls -la jest.config.* vitest.config.* pytest.ini pyproject.toml 2>/dev/null | head -3`
- Test files: !`find . -name "*.test.*" -o -name "*_test.py" -o -name "*_spec.ts" 2>/dev/null | wc -l`

## Your Task

执行测试驱动开发流程：

### 步骤 1: RED - 写失败测试
```bash
# 先写一个会失败的测试
npm test -- --watch  # 或对应框架的测试命令
```

### 步骤 2: 分析测试
- 理解测试期望的行为
- 识别需要实现的功能
- 确认边界条件

### 步骤 3: GREEN - 实现代码
- 编写最少的代码让测试通过
- 保持实现简单直接
- 避免提前优化

### 步骤 4: REFACTOR - 重构
- 在测试保护下重构代码
- 提升代码质量
- 保持测试通过

### 步骤 5: 覆盖率验证
```bash
# 运行覆盖率报告
npm test -- --coverage
```

## 测试金字塔

```
         /\
        /E2E\       <- 少量，端到端
       /------\
      /集成测试\    <- 适量
     /----------\
    /  单元测试  \  <- 大量
   /--------------\
```

## 注意事项

- 测试文件与源文件同目录或相邻
- 测试命名清晰描述行为
- 每个测试只测一件事
- 保持测试快速运行
