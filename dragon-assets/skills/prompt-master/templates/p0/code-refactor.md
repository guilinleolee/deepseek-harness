---
name: 代码重构
framework: APE
priority: P0
tags: [代码, 优化, 重构]
rating: 88
author: 九部天龙
created: 2026-02-21
---

# Action (行动)

请对以下代码进行重构分析和优化：

**代码片段**:
```{{language | default('python')}}
{{code_snippet}}
```

**上下文说明**: {{context_description}}

**主要问题** (可选):
{{issues | default("未指定，请分析")}}

---

# Purpose (目的)

## 重构目标

1. **提升可读性**: 代码应该像文档一样清晰易懂
2. **降低复杂度**: 控制圈复杂度（Cyclomatic Complexity）<10
3. **消除重复**: DRY原则（Don't Repeat Yourself）
4. **增强可维护性**: 便于后续修改和扩展
5. **优化性能**: 在不牺牲可读性的前提下提升性能

## 重构原则

### SOLID原则
- **单一职责**: 一个类/函数只做一件事
- **开闭原则**: 对扩展开放，对修改封闭
- **里氏替换**: 子类可替换父类
- **接口隔离**: 接口小而专
- **依赖倒置**: 依赖抽象而非具体

### 代码整洁之道
- **有意义的命名**: 变量/函数名应解释"为什么"
- **函数短小**: 一个函数只做一件事，<20行
- **无重复**: 抽取重复逻辑
- **表达力强**: 代码应自解释

---

# Expectation (期望输出)

## 请按以下结构输出

### 1. 代码诊断

#### 1.1 问题清单

| 问题类型 | 严重程度 | 位置 | 描述 | 影响 |
|---------|---------|------|------|------|
| 命名不清 | 中 | Line 15 | `temp`变量名不明确 | 降低可读性 |
| 重复代码 | 高 | Line 20-30, 45-55 | 相同逻辑重复2次 | 维护成本x2 |
| 函数过长 | 高 | Line 10-50 | 40行，职责混乱 | 难以测试 |
| ... | ... | ... | ... | ... |

**严重程度**: 🔴高 / 🟡中 / 🟢低

#### 1.2 度量指标

```markdown
重构前:
- 圈复杂度: 15 (过高，建议<10)
- 代码行数: 200行
- 重复率: 15%
- 可读性评分: 6/10
```

### 2. 重构方案

#### 2.1 重构策略

按优先级排序：

1. **[高优先级] 提取函数**
   - 将`processData()`拆分为`validateInput()`, `transformData()`, `saveResult()`
   - 预期收益: 圈复杂度降至5，可测试性提升

2. **[中优先级] 引入策略模式**
   - 将`if-elseif`链替换为策略类
   - 预期收益: 扩展性提升，符合开闭原则

3. **[低优先级] 优化命名**
   - `temp` → `validatedUserData`
   - `data` → `userProfile`

#### 2.2 重构后代码

```{{language}}
// 重构后的完整代码
// 包含详细的注释说明改动点

{{refactored_code}}
```

**关键改动说明**:
- Line 10-15: 提取了`validateInput()`函数
- Line 20-30: 引入策略模式替代`if-elseif`
- Line 35: 优化变量命名

### 3. 测试建议

#### 3.1 单元测试

提供关键测试用例：

```{{language | default('python')}}
import unittest

class TestRefactoredCode(unittest.TestCase):
    def test_validate_input_with_valid_data(self):
        # Arrange
        input = {...}
        # Act
        result = validateInput(input)
        # Assert
        self.assertTrue(result)

    def test_validate_input_with_invalid_data(self):
        # 测试边界条件
        ...

[提供3-5个核心测试用例]
```

#### 3.2 回归测试清单

- [ ] 原有功能是否正常？
- [ ] 边界条件是否覆盖？
- [ ] 错误处理是否完善？
- [ ] 性能是否下降？

### 4. 性能分析

#### 4.1 性能对比

| 指标 | 重构前 | 重构后 | 变化 |
|------|--------|--------|------|
| 执行时间 | 100ms | 95ms | -5% |
| 内存占用 | 10MB | 8MB | -20% |
| CPU使用 | 15% | 12% | -3% |

#### 4.2 性能优化点

- **缓存**: 对频繁调用的函数添加缓存
- **懒加载**: 延迟初始化大对象
- **批量处理**: 合并多次数据库查询

### 5. 可维护性评估

#### 5.1 代码评分

```markdown
重构后:
- 圈复杂度: 5 (✅ 符合标准)
- 代码行数: 150行 (-25%)
- 重复率: 0% (✅ 无重复)
- 可读性评分: 9/10 (+50%)
```

#### 5.2 后续优化建议

1. **短期**: [1-2周内可做的优化]
2. **中期**: [1-2个月内可做的优化]
3. **长期**: [架构层面的演进]

### 6. 风险评估

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| 引入新Bug | 中 | 高 | 完善单元测试+代码审查 |
| 性能下降 | 低 | 中 | 性能基准测试 |
| 兼容性破坏 | 低 | 高 | 保留旧接口，标记Deprecated |

---

## 常见代码坏味道（Code Smells）

### 需要重构的信号

1. **重复代码** (Duplicated Code)
   - 相同逻辑出现2次以上
   - 解决: 抽取函数/类

2. **过长函数** (Long Method)
   - 函数>20行
   - 解决: 提取子函数

3. **过大类** (Large Class)
   - 类>300行
   - 解决: 拆分职责

4. **长参数列表** (Long Parameter List)
   - 参数>4个
   - 解决: 引入参数对象

5. **特性依恋** (Feature Envy)
   - 函数更关心其他类的数据
   - 解决: 移动函数到合适类

6. **数据泥团** (Data Clumps)
   - 总是一起出现的参数
   - 解决: 封装为对象

7. **基本类型偏执** (Primitive Obsession)
   - 过度使用基本类型
   - 解决: 引入值对象

8. **switch语句** (Switch Statements)
   - 大量switch/if-elseif
   - 解决: 多态/策略模式

9. **临时字段** (Temporary Field)
   - 某些字段仅在特定情况下使用
   - 解决: 提取子类

10. **被拒绝的遗赠** (Refused Bequest)
    - 子类不需要父类的某些方法
    - 解决: 委托而非继承

---

## 重构技巧

### 安全重构

1. **小步前进**: 每次只改一个点
2. **测试保护**: 重构前后都要跑测试
3. **版本控制**: 每个重构点提交一次
4. **代码审查**: 重构后请同事Review

### 常用重构手法

| 手法 | 说明 | 示例 |
|------|------|------|
| 提取函数 | 将代码段抽取为函数 | `processData()` → `validate() + transform() + save()` |
| 内联函数 | 函数逻辑简单，直接内联 | `add(a, b) { return a+b; }` → `a+b` |
| 提取变量 | 将表达式赋值给变量 | `if (date.getTime() < ...) ` → `const winterStartTime = date.getTime(); if (winterStartTime < ...)` |
| 引入参数对象 | 多参数封装为对象 | `function(x, y, z)` → `function(Point p)` |
| 函数改名 | 更清晰地表达意图 | `process()` → `calculateTotalPrice()` |

---

## 示例

### 重构前

```python
def process_order(order):
    if order['status'] == 'pending':
        if order['amount'] > 1000:
            discount = order['amount'] * 0.1
        else:
            discount = order['amount'] * 0.05
        total = order['amount'] - discount
        if total > 500:
            shipping = 0
        else:
            shipping = 10
        final = total + shipping
        # 保存到数据库...
    elif order['status'] == 'paid':
        # ...
    # ... 100 lines of nested logic
```

### 重构后

```python
def process_order(order: Order) -> Receipt:
    """处理订单并返回收据

    Args:
        order: 订单对象

    Returns:
        Receipt: 收据对象
    """
    if order.status == OrderStatus.PENDING:
        return _process_pending_order(order)
    elif order.status == OrderStatus.PAID:
        return _process_paid_order(order)
    else:
        raise InvalidOrderStatusError(order.status)


def _process_pending_order(order: Order) -> Receipt:
    """处理待支付订单"""
    discount = _calculate_discount(order.amount)
    total = order.amount - discount
    shipping = _calculate_shipping(total)
    final_amount = total + shipping

    receipt = Receipt(
        order_id=order.id,
        subtotal=order.amount,
        discount=discount,
        shipping=shipping,
        final_amount=final_amount
    )

    _save_receipt(receipt)
    return receipt


def _calculate_discount(amount: Decimal) -> Decimal:
    """计算折扣

    Args:
        amount: 订单金额

    Returns:
        折扣金额
    """
    if amount > 1000:
        return amount * Decimal('0.1')
    return amount * Decimal('0.05')


def _calculate_shipping(total: Decimal) -> Decimal:
    """计算运费

    Args:
        total: 订单总额（折扣后）

    Returns:
        运费，满500包邮
    """
    return Decimal('0') if total > 500 else Decimal('10')


def _save_receipt(receipt: Receipt) -> None:
    """保存收据到数据库"""
    # ...
```

**改进点**:
- ✅ 每个函数只做一件事
- ✅ 圈复杂度从15降至3
- ✅ 引入类型注解，类型安全
- ✅ 函数命名清晰
- ✅ 易于单元测试

---

## 注意事项

1. **不要过度重构**: 重构的目的是改进代码，不是展示技巧
2. **保持功能不变**: 重构≠重写，功能行为必须一致
3. **测试先行**: 没有测试的重构是自欺欺人
4. **团队沟通**: 重构涉及他人代码时，提前沟通
5. **留痕**: 提交信息清晰描述重构内容
