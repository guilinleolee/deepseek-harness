---
name: design-pattern
description: 设计模式选择 - 根据场景推荐合适的代码架构模式
invokable: true
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
---
## Context

- 编程语言: !`git config --get user.language 2>/dev/null || echo "TypeScript"`
- 框架栈: !`echo "请说明使用的框架"`
- 问题场景: !`echo "请描述要解决的代码问题"`

## Your Task

执行设计模式分析：

### 步骤 1: 场景理解
- 分析代码结构和问题特征
- 识别需要解决的核心问题
- 确定模式应用的目标

### 步骤 2: 模式匹配
- 根据问题类型推荐合适模式：
  - **创建型**: Factory, Builder, Singleton, Prototype
  - **结构型**: Adapter, Bridge, Composite, Decorator, Facade, Proxy
  - **行为型**: Chain of Responsibility, Command, Iterator, Mediator, Observer, State, Strategy, Template Method, Visitor

### 步骤 3: 方案输出
- 提供模式选择的理由
- 给出代码示例
- 说明模式如何解决当前问题

### 步骤 4: 实现建议
- 给出重构步骤
- 提供完整的代码模板
- 说明测试注意事项

## 设计模式选择矩阵

| 问题场景 | 推荐模式 |
|---------|---------|
| 对象创建复杂 | Builder, Factory |
| 接口不兼容 | Adapter |
| 需要统一接口 | Facade |
| 对象需要装饰 | Decorator |
| 状态变化频繁 | State |
| 需要策略选择 | Strategy |
| 事件驱动 | Observer |
| 请求处理链 | Chain of Responsibility |

## 注意事项

- 避免过度设计
- 优先使用简单方案
- 确保模式符合团队熟悉度
