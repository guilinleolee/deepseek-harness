---
name: 代码审查
framework: APE
priority: P0
tags: [代码审查, 质量保证, 最佳实践]
rating: 89
author: 九部天龙
created: 2026-02-21
---

# Action (行动)

请对以下代码进行深度审查：

**代码片段**:
```{{language | default('python')}}
{{code_snippet}}
```

**上下文说明**: {{context_description}}

**审查重点** (可选):
{{review_focus | default("全面审查：功能、性能、安全、可维护性")}}

---

# Purpose (目的)

## 审查目标

1. **缺陷发现**: 找出潜在的Bug和逻辑错误
2. **质量提升**: 改进代码结构和可读性
3. **知识传递**: 通过审查分享最佳实践
4. **团队成长**: 帮助开发者提升编码能力

## 审查原则

### 建设性原则
- **对事不对人**: 评论代码而非评论人
- **解释原因**: 不仅说"怎么改"，更要说"为什么"
- **认可优点**: 先肯定做得好的地方
- **提供建议**: 给出具体的改进方案

### 审查层次
1. **正确性**: 代码是否实现了预期功能？
2. **可读性**: 代码是否易于理解？
3. **可维护性**: 代码是否易于修改和扩展？
4. **性能**: 代码是否存在性能问题？
5. **安全性**: 代码是否存在安全漏洞？

---

# Expectation (期望输出)

## 请按以下结构输出审查报告

### 1. 审查概览

#### 1.1 基本信息

```markdown
**代码位置**: [文件路径:行号]
**代码行数**: [总行数]
**审查时间**: [时间戳]
**审查人**: [你的名字]
**审查范围**: [功能描述]
```

#### 1.2 总体评价

| 维度 | 评分 (1-5) | 说明 |
|------|-----------|------|
| 功能正确性 | 4/5 | 核心逻辑正确，边界条件未覆盖 |
| 代码可读性 | 3/5 | 变量命名需改进，缺少注释 |
| 可维护性 | 3/5 | 函数过长，职责不清晰 |
| 性能 | 4/5 | 整体良好，有一处N+1查询 |
| 安全性 | 5/5 | 无明显安全问题 |
| 测试覆盖 | 2/5 | 缺少边界条件测试 |

**总体评分**: 3.5/5 (良好)

**一句话评价**: 代码实现了核心功能，但需要在可读性、可维护性和测试覆盖方面改进。

#### 1.3 亮点

**做得好的地方**:
- ✅ 使用了参数化查询，避免SQL注入
- ✅ 错误处理完善，所有异常都被捕获
- ✅ 遵循了项目命名规范

### 2. 功能审查

#### 2.1 逻辑正确性

| 问题 | 严重程度 | 位置 | 描述 | 建议 |
|------|---------|------|------|------|
| 除零风险 | 🔴高 | Line 25 | `result = total / count` 未检查count是否为0 | 添加 `if count == 0: return 0` |
| 类型错误 | 🟡中 | Line 30 | 字符串和数字直接相加 | 使用 `str()` 转换 |
| 边界条件 | 🟡中 | Line 40 | 数组越界风险 | 检查索引范围 |

**严重程度定义**:
- 🔴 **高**: 必须修复，否则会导致Bug
- 🟡 **中**: 建议修复，可能引发问题
- 🟢 **低**: 可选优化，改进代码质量

#### 2.2 业务逻辑

**问题**: [描述业务逻辑问题]

**示例**:
```python
# 原代码
if user.vip or user.amount > 100:
    discount = 0.1

# 问题: VIP用户无论金额多少都打折，可能不符合业务规则

# 建议
if user.vip and user.amount > 100:
    discount = 0.15
elif user.amount > 100:
    discount = 0.1
```

### 3. 代码质量审查

#### 3.1 命名规范

| 类型 | 当前命名 | 建议命名 | 理由 |
|------|---------|---------|------|
| 变量 | `temp` | `user_profile` | 表达实际含义 |
| 函数 | `process()` | `calculate_order_total()` | 清晰表达功能 |
| 常量 | `timeout` | `CONNECTION_TIMEOUT` | 常量应大写 |

**示例**:
```python
# ❌ 差: 命名不清晰
def calc(a, b, c):
    return a * b + c

# ✅ 好: 命名清晰
def calculate_total_price(quantity, unit_price, shipping_fee):
    return quantity * unit_price + shipping_fee
```

#### 3.2 函数设计

**问题**: 函数过长，职责混乱

**示例**:
```python
# ❌ 差: 50行，做太多事
def process_order(order_id):
    # 1. 验证订单 (10行)
    # 2. 计算金额 (15行)
    # 3. 扣减库存 (10行)
    # 4. 创建支付 (10行)
    # 5. 发送通知 (5行)

# ✅ 好: 拆分为多个函数
def process_order(order_id):
    order = validate_order(order_id)
    total = calculate_total(order)
    deduct_inventory(order)
    payment = create_payment(order, total)
    send_notification(order, payment)
    return payment
```

**函数设计原则**:
- **单一职责**: 一个函数只做一件事
- **短小精悍**: 函数<20行（特殊情况除外）
- **参数少**: 参数≤4个，多则封装为对象

#### 3.3 复杂度分析

**圈复杂度** (Cyclomatic Complexity):
```python
# 当前: 圈复杂度 = 8 (过高，建议<10)

def calculate_discount(user, order):
    if user.is_vip:  # +1
        if user.level == 1:  # +1
            if order.amount > 100:  # +1
                return 0.15
            else:  # +1
                return 0.1
        elif user.level == 2:  # +1
            if order.amount > 200:  # +1
                return 0.2
            else:  # +1
                return 0.15
    else:  # +1
        return 0

# 建议: 提前返回，降低嵌套

def calculate_discount(user, order):
    if not user.is_vip:
        return 0

    if user.level == 2 and order.amount > 200:
        return 0.2
    if user.level == 2:
        return 0.15
    if user.level == 1 and order.amount > 100:
        return 0.15
    if user.level == 1:
        return 0.1
```

#### 3.4 代码重复

**示例**:
```python
# ❌ 差: 相同逻辑重复3次
def process_user_a(data):
    if validate_email(data['email']):
        save_to_db(data)
        send_email(data['email'])
        log_action('user_a_created')

def process_user_b(data):
    if validate_email(data['email']):
        save_to_db(data)
        send_email(data['email'])
        log_action('user_b_created')

# ✅ 好: 提取公共逻辑
def create_user(data, user_type):
    if not validate_email(data['email']):
        return False
    save_to_db(data)
    send_email(data['email'])
    log_action(f'{user_type}_created')
    return True
```

### 4. 性能审查

#### 4.1 性能问题

| 问题 | 位置 | 影响 | 优化建议 |
|------|------|------|----------|
| N+1查询 | Line 45-50 | 数据库压力大 | 使用JOIN或批量查询 |
| 大循环 | Line 60-70 | O(n²)复杂度 | 优化为O(n) |
| 未缓存 | Line 80 | 重复计算 | 添加缓存 |

**示例**: N+1查询

```python
# ❌ 差: N+1查询
orders = db.query("SELECT * FROM orders")
for order in orders:
    user = db.query(f"SELECT * FROM users WHERE id = {order.user_id}")  # N次查询
    order.user = user

# ✅ 好: 批量查询
orders = db.query("SELECT * FROM orders")
user_ids = [o.user_id for o in orders]
users = db.query(f"SELECT * FROM users WHERE id IN ({','.join(user_ids)})")  # 1次查询
user_map = {u.id: u for u in users}
for order in orders:
    order.user = user_map[order.user_id]
```

#### 4.2 算法复杂度

| 当前实现 | 复杂度 | 优化后 | 复杂度 |
|---------|--------|--------|--------|
| 嵌套循环 | O(n²) | 使用哈希表 | O(n) |
| 递归调用 | O(2ⁿ) | 动态规划 | O(n²) |

### 5. 安全审查

#### 5.1 安全漏洞

| 漏洞类型 | 严重程度 | 位置 | 描述 | 修复建议 |
|---------|---------|------|------|----------|
| SQL注入 | 🔴高 | Line 20 | 字符串拼接SQL | 使用参数化查询 |
| XSS漏洞 | 🔴高 | Line 35 | 直接输出用户输入 | HTML转义 |
| 敏感信息泄露 | 🟡中 | Line 50 | 日志中打印密码 | 移除日志 |
| CSRF漏洞 | 🟡中 | Line 60 | POST无Token | 添加CSRF Token |

**示例**: SQL注入

```python
# ❌ 差: SQL注入漏洞
query = f"SELECT * FROM users WHERE id = {user_id}"
result = db.execute(query)

# ✅ 好: 参数化查询
query = "SELECT * FROM users WHERE id = ?"
result = db.execute(query, [user_id])
```

**示例**: XSS漏洞

```python
# ❌ 差: XSS漏洞
return f"<div>{user_input}</div>"

# ✅ 好: HTML转义
import html
return f"<div>{html.escape(user_input)}</div>"
```

#### 5.2 数据验证

**缺少的验证**:
- [ ] 用户输入长度限制
- [ ] 数据类型校验
- [ ] 范围校验（如年龄>0）

**示例**:
```python
# ❌ 差: 无验证
def set_age(age):
    self.age = age

# ✅ 好: 完整验证
def set_age(self, age):
    if not isinstance(age, int):
        raise TypeError("Age must be an integer")
    if age < 0 or age > 150:
        raise ValueError("Age must be between 0 and 150")
    self.age = age
```

### 6. 可维护性审查

#### 6.1 注释和文档

**缺失的注释**:
- Line 15: 复杂算法缺少解释
- Line 30: 正则表达式未说明用途

**注释原则**:
- **为什么**: 解释"为什么"而非"是什么"
- **复杂逻辑**: 复杂算法必须注释
- **TODO**: 标记待完成的代码

**示例**:
```python
# ❌ 差: 无意义的注释
# 将count加1
count += 1

# ✅ 好: 解释原因
# 使用round避免浮点数精度问题
count = round(count + 1, 2)

# ✅ 好: 复杂算法解释
# 使用动态规划计算斐波那契数列
# 时间复杂度: O(n), 空间复杂度: O(n)
def fibonacci(n):
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]
```

#### 6.2 错误处理

**缺失的错误处理**:
- Line 25: 除法未检查除数
- Line 40: 数组访问未检查索引

**示例**:
```python
# ❌ 差: 无错误处理
result = total / count

# ✅ 好: 完善错误处理
if count == 0:
    logger.warning("Count is zero, returning 0")
    return 0
result = total / count
```

#### 6.3 依赖耦合

**高耦合**: 直接依赖具体实现

```python
# ❌ 差: 高耦合
def send_notification(user):
    sender = EmailSender()  # 具体实现
    sender.send(user.email, "Welcome")

# ✅ 好: 依赖抽象
def send_notification(user, sender: NotificationSender):
    sender.send(user, "Welcome")
```

### 7. 测试覆盖

#### 7.1 缺失的测试

| 测试类型 | 覆盖率 | 缺失场景 |
|---------|--------|----------|
| 单元测试 | 60% | 边界条件、异常场景 |
| 集成测试 | 40% | 数据库异常、第三方服务失败 |

**建议添加的测试**:
```python
# 边界测试
def test_calculate_discount_with_zero_amount():
    assert calculate_discount(user, amount=0) == 0

def test_calculate_discount_with_negative_amount():
    with pytest.raises(ValueError):
        calculate_discount(user, amount=-1)

# 异常测试
def test_get_user_with_database_error():
    with patch('db.query') as mock_query:
        mock_query.side_effect = DatabaseError()
        with pytest.raises(ServiceUnavailableError):
            get_user(123)
```

### 8. 改进建议

#### 8.1 具体修改方案

**优先级1 (必须修复)**:
```python
# 修改位置: Line 25
# 原代码
result = total / count

# 修改为
if count == 0:
    return 0
result = total / count
```

**优先级2 (强烈建议)**:
```python
# 修改位置: Line 10-30
# 原代码: 50行函数
def process_order(order_id):
    # 50 lines...

# 修改为: 拆分函数
def process_order(order_id):
    order = _validate_order(order_id)
    total = _calculate_total(order)
    # ...
```

**优先级3 (可选优化)**:
```python
# 修改位置: Line 45
# 原代码
for order in orders:
    user = db.query(f"SELECT * FROM users WHERE id = {order.user_id}")

# 修改为: 批量查询
user_ids = [o.user_id for o in orders]
users = db.query(f"SELECT * FROM users WHERE id IN ({','.join(map(str, user_ids))})")
```

#### 8.2 学习资源

**相关阅读**:
- [Python代码风格指南 (PEP 8)](https://www.python.org/dev/peps/pep-0008/)
- [Clean Code 读书笔记](https://example.com/clean-code)
- [团队内部: 代码审查最佳实践](https://internal.example.com/code-review)

### 9. 总结

#### 9.1 优点
- ✅ 功能实现正确
- ✅ 安全性良好（无SQL注入、XSS）
- ✅ 错误处理基本完善

#### 9.2 待改进
- 🔴 **必须修复**: 除零风险 (Line 25)
- 🟡 **强烈建议**: 拆分函数，降低复杂度 (Line 10-30)
- 🟢 **可选优化**: 批量查询，提升性能 (Line 45)

#### 9.3 下一步行动

1. 开发者修复优先级1和2的问题
2. 更新单元测试，覆盖边界条件
3. 提交修改后，再次审查

---

## 审查技巧

### 1. 审查清单

使用标准清单避免遗漏：

```markdown
## 功能正确性
- [ ] 逻辑是否正确？
- [ ] 边界条件是否覆盖？
- [ ] 错误处理是否完善？

## 代码质量
- [ ] 命名是否清晰？
- [ ] 函数是否短小？
- [ ] 是否有重复代码？
- [ ] 注释是否充分？

## 性能
- [ ] 是否有N+1查询？
- [ ] 算法复杂度是否合理？
- [ ] 是否需要缓存？

## 安全
- [ ] SQL注入？
- [ ] XSS漏洞？
- [ ] CSRF漏洞？
- [ ] 敏感信息泄露？

## 测试
- [ ] 单元测试覆盖率？
- [ ] 是否有边界测试？
- [ ] 是否有异常测试？
```

### 2. 说话的艺术

**❌ 差的评论**:
```
"你这代码写得太烂了"
"为什么要这样写？"
"重构"
```

**✅ 好的评论**:
```
"这里可能存在除零风险，建议添加count==0的检查"
"我理解这里是为了XXX，但用YYY方式会更清晰，因为..."
"建议提取为独立函数，提高可测试性和复用性"
```

### 3. 优先级判断

不是所有问题都需要立即修复：

| 优先级 | 标准 | 示例 |
|--------|------|------|
| P0 | 必须修复，否则无法合并 | 除零错误、安全漏洞 |
| P1 | 强烈建议，应该尽快修复 | 性能问题、复杂度过高 |
| P2 | 可选优化，时间允许再改 | 命名不够清晰、缺少注释 |
| P3 | 风格差异，可讨论 | 缩进风格、空行数量 |

### 4. 工具辅助

使用自动化工具提高审查效率：

- **静态分析**: ESLint, Pylint, SonarQube
- **安全扫描**: Snyk, OWASP Dependency-Check
- **格式检查**: Black, Prettier
- **复杂度分析**: Lizard, radon

---

## 注意事项

1. **及时审查**: PR提交后24小时内完成审查
2. **小步提交**: 避免大PR（<400行），难以审查
3. **自我审查**: 提交前自己先审查一遍
4. **讨论学习**: 审查是双向学习，不是单方面批评
5. **感谢贡献**: 认可开发者的付出，建立信任
