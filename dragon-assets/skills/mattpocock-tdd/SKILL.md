---
license: UNKNOWN
triggers: ["mattpocock tdd", "MattPocock TDD - 测试驱动开发技能"]
---
# MattPocock TDD - 测试驱动开发技能

## L0: 一句话描述 (≤15字)
垂直切片TDD驱动开发

## L1: 使用场景 (50-100字)
适用于需要实现新功能或模块的场景。通过先写测试，从用户视角定义接口，再逐步实现功能。避免过度工程，专注于当前需求。

## L2: 详细文档

### 核心理念

> "不要过度工程。先让测试通过，然后重构。"

### 垂直切片 vs 水平切片

| 方法 | 描述 | 适用场景 |
|------|------|---------|
| **垂直切片 (Vertical Slices)** | 从头到尾实现一个用户故事 | 优先功能完整性 |
| **水平切片 (Horizontal Slices)** | 先实现所有层的一个模块 | 优先技术架构 |

### 三阶段循环

```
┌─────────────────────────────────────────────────────────────┐
│ 1. RED (写一个失败的测试)                                    │
│    - 从用户视角写测试                                       │
│    - 测试应该失败，证明功能不存在                           │
│    - 不要mock太多东西                                       │
├─────────────────────────────────────────────────────────────┤
│ 2. GREEN (快速让测试通过)                                   │
│    - 用最简单的方式让测试通过                               │
│    - 可以有重复代码                                        │
│    - 不要追求完美                                          │
├─────────────────────────────────────────────────────────────┤
│ 3. REFACTOR (重构)                                         │
│    - 消除重复代码                                          │
│    - 改善代码结构                                          │
│    - 确保测试仍然通过                                      │
└─────────────────────────────────────────────────────────────┘
```

### 追踪弹 (Tracer Bullet) 工作流

适用于新项目或需要建立信心的场景：

```bash
# 1. 写一个端到端测试
# 2. 运行测试，看到它失败
# 3. 逐步实现，从外到内
#    - Controller/Handler → Service → Repository
# 4. 每次只让一个断言通过
# 5. 重复直到功能完成
```

### 测试结构模板

```typescript
// 1. 导入被测模块
import { calculate } from './calculator';

// 2. 描述测试组
describe('calculator', () => {
  // 3. 描述具体行为
  describe('add', () => {
    // 4. 写一个会失败的测试
    it('adds two numbers', () => {
      const result = calculate('2 + 2');
      expect(result).toBe(4);
    });
  });
});
```

### 常见反模式

| 反模式 | 问题 | 解决 |
|--------|------|------|
| 过度Mock | 测试不反映真实使用 | 只mock外部依赖 |
| 测试实现细节 | 重构破坏测试 | 测试行为而非实现 |
| 一次性写太多测试 | 难以调试 | 每次只写一个测试 |

### 与天龙构建师协同

```bash
[@构建师] 使用 mattpocock-tdd 开发这个功能
[@构建师] 先实现一个垂直切片
```

### 核心命令

```bash
# 启动TDD循环
/mattpocock-tdd start "功能描述"

# 垂直切片实现
/mattpocock-tdd vertical-slice "用户故事"

# 追踪弹实现
/mattpocock-tdd tracer-bullet
```

## L3: 参考资源

- https://github.com/mattpocock/skills/tree/main/tdd
- Test-Driven Development (Kent Beck)
- Growing Object-Oriented Software (Freeman & Pryce)
