---
license: UNKNOWN
triggers: ["mattpocock design an interface", "MattPocock Design An Interface - 接口设计技能"]
---
# MattPocock Design An Interface - 接口设计技能

## L0: 一句话描述 (≤15字)
Design It Twice接口设计法

## L1: 使用场景 (50-100字)
适用于需要设计新接口/API/模块的场景。通过并行生成多个设计方案，从5个维度对比分析，避免先入为主的设计偏见，找到最优解。

## L2: 详细文档

### 核心理念

> "如果你只有一个设计方案，你就没有设计方案。" — Matt Pocock

### Design It Twice 工作流

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: 独立设计 (并行)                                    │
│                                                             │
│   设计方案A ──▶ 优点/缺点 ──┐                              │
│                                ├──▶ 最终推荐方案             │
│   设计方案B ──▶ 优点/缺点 ──┤                              │
│                                │                             │
│   设计方案C ──▶ 优点/缺点 ──┘                              │
├─────────────────────────────────────────────────────────────┤
│ Phase 2: 五维度对比                                         │
├─────────────────────────────────────────────────────────────┤
│ Phase 3: 推荐决策                                           │
└─────────────────────────────────────────────────────────────┘
```

### 五维度对比矩阵

| 维度 | 设计A | 设计B | 设计C |
|------|-------|-------|-------|
| **1. 简单性** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **2. 可扩展性** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **3. 类型安全** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **4. 可测试性** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **5. 开发者体验** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

### 设计方案模板

```typescript
// 设计方案A: 命令式API
interface Calculator {
  add(a: number, b: number): number;
  subtract(a: number, b: number): number;
}

// 设计方案B: 表达式API
type Operation = 'add' | 'subtract';
interface Calculator {
  calculate(op: Operation, a: number, b: number): number;
}

// 设计方案C: 链式API
interface Calculator {
  add(a: number): { subtract: (b: number) => number };
}
```

### 设计问题清单

在开始设计前，先问自己：

- [ ] 这个接口的调用者是谁？
- [ ] 最常见的调用模式是什么？
- [ ] 未来可能有哪些扩展需求？
- [ ] 当前系统的约束是什么？
- [ ] 如何处理错误情况？

### 常见设计模式

| 模式 | 适用场景 | 示例 |
|------|---------|------|
| **Builder** | 可选参数多 | `createUser({ name, email, role? })` |
| **Chain** | 连续操作 | `query.where().orderBy().limit()` |
| **Command** | 操作封装 | `execute('add', 2, 3)` |
| **Strategy** | 算法切换 | `sort((a, b) => a - b)` |

### 接口设计检查清单

```typescript
// ✅ 类型安全
interface User {
  id: string;
  email: Email; // 专用类型
}

// ❌ 避免any
function processUser(user: any) { }

// ✅ 必填/可选清晰
interface Config {
  host: string;      // 必填
  port?: number;    // 可选，有默认值
  timeout?: number;  // 可选
}

// ❌ 避免混合
interface Config {
  host: string;
  port: number | undefined;
}
```

### 与天龙架构师协同

```bash
[@架构师] 使用 design-an-interface 设计这个API
[@架构师] 用 Design It Twice 对比三个方案
```

### 核心命令

```bash
# 启动接口设计
/design-an-interface "设计一个用户服务API"

# 五维度对比
/design-an-interface compare "方案A" "方案B"

# 设计审查
/design-an-interface review "当前接口"
```

## L3: 参考资源

- https://github.com/mattpocock/skills/tree/main/design-an-interface
- Domain-Driven Design (Eric Evans)
- Designing Data-Intensive Applications (Martin Kleppmann)
