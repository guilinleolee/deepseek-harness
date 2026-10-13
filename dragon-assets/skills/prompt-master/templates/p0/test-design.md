---
name: 测试设计
framework: APE
priority: P0
tags: [测试, 质量保证, 测试用例]
rating: 86
author: 九部天龙
created: 2026-02-21
---

# Action (行动)

请为以下功能设计完整的测试方案：

**功能描述**: {{feature_description}}

**技术栈** (可选):
- 语言: {{language | default("未指定")}}
- 框架: {{framework | default("未指定")}}

**测试要求** (可选):
{{test_requirements | default("完整覆盖功能、性能、安全")}}

---

# Purpose (目的)

## 测试目标

1. **功能验证**: 确保功能符合需求规格
2. **缺陷发现**: 尽早发现Bug，降低修复成本
3. **风险控制**: 评估上线风险，保障质量
4. **回归保护**: 建立回归测试基线

## 测试原则

### 测试金字塔

```
        /\
       /E2E\      少量端到端测试
      /------\
     /  集成  \    适量集成测试
    /----------\
   /   单元测试  \  大量单元测试
  /--------------\
```

**比例建议**: 70% 单元测试 / 20% 集成测试 / 10% E2E测试

### 测试覆盖原则

- **正常场景**: 预期输入，预期输出
- **边界场景**: 最小值、最大值、空值
- **异常场景**: 错误输入、网络异常、服务异常
- **并发场景**: 多用户同时操作
- **兼容性**: 不同浏览器、设备、版本

---

# Expectation (期望输出)

## 请按以下结构输出测试方案

### 1. 测试概览

#### 1.1 功能分析

**功能模块**: {{feature_description}}

**核心功能点**:
- 功能1: [描述]
- 功能2: [描述]
- 功能3: [描述]

**测试范围**:
- ✅ 包含: [本次测试覆盖的内容]
- ❌ 不包含: [本次测试不覆盖的内容]

#### 1.2 测试策略

| 测试类型 | 测试工具 | 负责人 | 时间安排 |
|---------|---------|--------|----------|
| 单元测试 | Jest/PyTest | 开发 | 开发阶段 |
| 集成测试 | Supertest/Postman | 测试 | 提测阶段 |
| E2E测试 | Cypress/Selenium | 测试 | 上线前 |
| 性能测试 | JMeter/K6 | 测试 | 上线前 |
| 安全测试 | OWASP ZAP | 安全 | 上线前 |

### 2. 测试用例设计

#### 2.1 功能测试用例

使用表格格式：

| 用例ID | 场景 | 前置条件 | 测试步骤 | 测试数据 | 预期结果 | 优先级 |
|--------|------|---------|---------|---------|---------|--------|
| TC001 | 正常登录 | 用户已注册 | 1.输入账号<br>2.输入密码<br>3.点击登录 | 账号: test@example.com<br>密码: Pass123! | 登录成功，跳转首页 | P0 |
| TC002 | 密码错误 | 用户已注册 | 1.输入正确账号<br>2.输入错误密码 | 账号: test@example.com<br>密码: Wrong123! | 提示"密码错误" | P0 |
| TC003 | 账号为空 | - | 1.账号留空<br>2.点击登录 | 账号: 空<br>密码: Pass123! | 提示"账号不能为空" | P1 |

**优先级定义**:
- **P0**: 核心功能，必须测试
- **P1**: 重要功能，应该测试
- **P2**: 边缘功能，时间允许则测试

#### 2.2 边界值测试

针对有范围的输入，测试边界值：

| 字段 | 有效范围 | 测试值 | 预期结果 |
|------|---------|--------|---------|
| 用户名 | 3-20字符 | 2字符 | 提示"用户名至少3个字符" |
| 用户名 | 3-20字符 | 3字符 | ✅ 通过 |
| 用户名 | 3-20字符 | 20字符 | ✅ 通过 |
| 用户名 | 3-20字符 | 21字符 | 提示"用户名最多20个字符" |
| 用户名 | 3-20字符 | 空字符串 | 提示"用户名不能为空" |
| 用户名 | 3-20字符 | null | 提示"用户名不能为空" |

**边界值分析原则**: 最小值-1, 最小值, 正常值, 最大值, 最大值+1

#### 2.3 异常场景测试

| 场景 | 触发方式 | 预期行为 |
|------|---------|---------|
| 网络超时 | 断网或模拟超时 | 提示"网络连接失败"，不崩溃 |
| 服务端500 | Mock服务器错误 | 提示"服务异常"，记录日志 |
| 并发修改 | 2个用户同时编辑 | 后提交覆盖前提交，提示冲突 |
| 数据库连接失败 | 停止数据库 | 优雅降级，返回缓存数据 |

#### 2.4 安全测试用例

| 测试项 | 测试方法 | 预期结果 |
|--------|---------|---------|
| SQL注入 | 输入: `' OR '1'='1` | 参数化查询，注入失败 |
| XSS攻击 | 输入: `<script>alert(1)</script>` | 转义为 `&lt;script&gt;` |
| CSRF攻击 | 跨域POST请求 | CSRF Token验证失败 |
| 越权访问 | 用户A访问用户B的数据 | 返回403 Forbidden |
| 敏感信息泄露 | 查看响应体 | 不包含密码、Token等 |

#### 2.5 性能测试用例

| 指标 | 测试场景 | 目标值 | 测试方法 |
|------|---------|--------|---------|
| 响应时间 | 单用户请求 | P95 < 200ms | JMeter压测 |
| 吞吐量 | 并发100用户 | > 500 TPS | 逐步加压 |
| 并发用户 | 同时在线 | 1000人 | K6持续压测10分钟 |
| 稳定性 | 长时间运行 | 24小时无异常 | 持续压测 |

### 3. 测试代码示例

#### 3.1 单元测试示例

**示例**: 登录功能单元测试

```python
import pytest

class TestLogin:
    """登录功能单元测试"""

    def test_login_with_valid_credentials(self, user_service):
        """测试: 有效账号密码登录"""
        # Given
        username = "test@example.com"
        password = "Pass123!"

        # When
        result = user_service.login(username, password)

        # Then
        assert result.success is True
        assert result.token is not None
        assert result.user.email == username

    def test_login_with_invalid_password(self, user_service):
        """测试: 密码错误"""
        # Given
        username = "test@example.com"
        password = "WrongPassword"

        # When
        result = user_service.login(username, password)

        # Then
        assert result.success is False
        assert result.error == "INVALID_PASSWORD"

    def test_login_with_nonexistent_user(self, user_service):
        """测试: 用户不存在"""
        # Given
        username = "nonexistent@example.com"
        password = "Pass123!"

        # When
        result = user_service.login(username, password)

        # Then
        assert result.success is False
        assert result.error == "USER_NOT_FOUND"

    @pytest.mark.parametrize("username,password,expected_error", [
        ("", "Pass123!", "USERNAME_EMPTY"),
        ("test@example.com", "", "PASSWORD_EMPTY"),
        ("ab", "Pass123!", "USERNAME_TOO_SHORT"),
    ])
    def test_login_validation(self, user_service, username, password, expected_error):
        """测试: 参数校验"""
        # When
        result = user_service.login(username, password)

        # Then
        assert result.success is False
        assert result.error == expected_error
```

#### 3.2 集成测试示例

```python
import pytest

class TestLoginAPI:
    """登录API集成测试"""

    def test_login_api_success(self, client):
        """测试: 登录API成功"""
        # Given
        payload = {
            "email": "test@example.com",
            "password": "Pass123!"
        }

        # When
        response = client.post("/api/auth/login", json=payload)

        # Then
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["user"]["email"] == "test@example.com"

    def test_login_api_failure(self, client):
        """测试: 登录API失败"""
        # Given
        payload = {
            "email": "test@example.com",
            "password": "WrongPassword"
        }

        # When
        response = client.post("/api/auth/login", json=payload)

        # Then
        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "INVALID_CREDENTIALS"
```

#### 3.3 E2E测试示例

```javascript
describe('Login E2E Test', () => {
  it('should login successfully with valid credentials', () => {
    // 访问登录页
    cy.visit('/login')

    // 输入账号密码
    cy.get('[data-testid="email-input"]').type('test@example.com')
    cy.get('[data-testid="password-input"]').type('Pass123!')

    // 点击登录
    cy.get('[data-testid="login-button"]').click()

    // 验证跳转到首页
    cy.url().should('include', '/dashboard')
    cy.get('[data-testid="welcome-message"]')
      .should('contain', 'Welcome, test@example.com')
  })

  it('should show error with invalid credentials', () => {
    cy.visit('/login')

    cy.get('[data-testid="email-input"]').type('test@example.com')
    cy.get('[data-testid="password-input"]').type('WrongPassword')
    cy.get('[data-testid="login-button"]').click()

    // 验证错误提示
    cy.get('[data-testid="error-message"]')
      .should('contain', '账号或密码错误')
      .and('be.visible')

    // 验证仍在登录页
    cy.url().should('include', '/login')
  })
})
```

### 4. 测试数据准备

#### 4.1 测试数据清单

| 数据类型 | 数据准备 | 用途 |
|---------|---------|------|
| 正常用户 | 10个有效账号 | 功能测试 |
| 边界用户 | 用户名长度=3, =20的账号 | 边界测试 |
| 异常数据 | 特殊字符、SQL注入字符串 | 安全测试 |
| 性能数据 | 10000条用户数据 | 性能测试 |

#### 4.2 数据清理策略

- **独立测试**: 每个测试用例独立数据，互不影响
- **事务回滚**: 测试后回滚数据库
- **Mock数据**: 使用Mock而非真实数据

### 5. 测试环境

#### 5.1 环境配置

| 环境 | 用途 | 数据 | 访问地址 |
|------|------|------|----------|
| 开发环境 | 开发自测 | Mock数据 | http://localhost:3000 |
| 测试环境 | QA测试 | 脱敏生产数据 | http://test.example.com |
| 预发环境 | 上线前演练 | 生产数据副本 | http://staging.example.com |
| 生产环境 | 真实环境 | 真实数据 | http://example.com |

#### 5.2 环境依赖

- 数据库: PostgreSQL 14
- 缓存: Redis 7
- 消息队列: RabbitMQ 3.12
- 第三方服务: 支付宝沙箱环境

### 6. 测试执行计划

#### 6.1 测试进度

| 阶段 | 测试类型 | 时间 | 负责人 | 通过标准 |
|------|---------|------|--------|----------|
| 第1周 | 单元测试 | 开发中 | 开发 | 覆盖率>80% |
| 第2周 | 集成测试 | 提测后 | QA | 用例通过率>95% |
| 第3周 | E2E测试 | 上线前 | QA | 核心流程100%通过 |
| 第3周 | 性能测试 | 上线前 | QA | 性能指标达标 |

#### 6.2 验收标准

- **功能**: 所有P0用例通过
- **性能**: P95响应时间<200ms
- **安全**: 无高危漏洞
- **覆盖率**: 单元测试>80%, 集成测试>60%

### 7. 风险与应对

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| 测试环境不稳定 | 中 | 中 | 提前验证环境，准备备用环境 |
| 测试数据不足 | 低 | 中 | 提前准备数据生成脚本 |
| 第三方服务不可用 | 低 | 高 | Mock第三方服务 |
| 时间不足 | 中 | 高 | 按优先级测试，P0必测 |

---

## 测试设计技巧

### 1. 等价类划分

将输入划分为有效等价类和无效等价类：

**示例**: 用户名长度3-20字符

| 等价类 | 测试值 | 预期 |
|--------|--------|------|
| 有效等价类 | 5字符 | ✅ 通过 |
| 有效等价类 | 15字符 | ✅ 通过 |
| 无效等价类（<3） | 2字符 | ❌ 失败 |
| 无效等价类（>20） | 25字符 | ❌ 失败 |

### 2. 边界值分析

在每个边界上测试：

**示例**: 折扣门槛满99包邮

| 测试值 | 预期 |
|--------|------|
| 98.00 | 不包邮 |
| 98.99 | 不包邮 |
| 99.00 | 包邮 |
| 99.01 | 包邮 |
| 100.00 | 包邮 |

### 3. 决策表测试

针对复杂业务规则：

| 场景 | 已登录 | VIP | 库存充足 | 预期结果 |
|------|--------|-----|---------|---------|
| 1 | ✅ | ✅ | ✅ | 可购买，VIP价格 |
| 2 | ✅ | ❌ | ✅ | 可购买，原价 |
| 3 | ✅ | - | ❌ | 提示"库存不足" |
| 4 | ❌ | - | ✅ | 跳转登录页 |

### 4. 状态迁移测试

测试对象在不同状态间的迁移：

```
[待支付] → [已支付] → [已发货] → [已完成]
                ↓
             [已取消]
```

**测试路径**:
- 正常路径: 待支付 → 已支付 → 已发货 → 已完成
- 取消路径: 待支付 → 已取消
- 退货路径: 已完成 → 已退货

### 5. 错误猜测

基于经验猜测可能的错误：

- 用户输入全角字符
- 用户输入前后空格
- 用户输入emoji
- 用户输入RTL语言（阿拉伯语）
- 用户输入HTML标签

---

## 示例

### 输入
```
功能描述: 用户注册
技术要求:
- 支持邮箱注册
- 密码8-20字符，必须包含大小写字母和数字
- 邀请码可选
```

### 输出（简化版）

```markdown
# 用户注册功能测试方案

## 测试用例

| 用例ID | 场景 | 步骤 | 数据 | 预期 |
|--------|------|------|------|------|
| TC001 | 正常注册 | 1.输入邮箱<br>2.输入密码<br>3.点击注册 | 邮箱: test@example.com<br>密码: Pass123! | 注册成功，发送欢迎邮件 |
| TC002 | 邮箱已存在 | 1.输入已存在邮箱<br>2.点击注册 | 邮箱: existed@example.com | 提示"邮箱已注册" |
| TC003 | 密码太短 | 1.输入短密码 | 密码: Pass1! | 提示"密码至少8个字符" |
| TC004 | 密码无数字 | 1.输入无数字密码 | 密码: Password! | 提示"密码必须包含数字" |

## 边界测试

| 字段 | 测试值 | 预期 |
|------|--------|------|
| 密码 | 7字符 | 提示"密码至少8个字符" |
| 密码 | 8字符 | ✅ 通过 |
| 密码 | 20字符 | ✅ 通过 |
| 密码 | 21字符 | 提示"密码最多20个字符" |

## 安全测试

| 测试项 | 输入 | 预期 |
|--------|------|------|
| SQL注入 | `' OR '1'='1` | 转义处理 |
| XSS攻击 | `<script>alert(1)</script>` | 转义为 `&lt;script&gt;` |
| 邮箱轰炸 | 同一邮箱1分钟注册10次 | 限流，第4次提示"操作过于频繁" |

## 单元测试代码

```python
def test_register_with_valid_data():
    """测试: 正常注册"""
    service = UserService()
    result = service.register(
        email="test@example.com",
        password="Pass123!"
    )
    assert result.success is True
    assert result.user.email == "test@example.com"

def test_register_with_duplicate_email():
    """测试: 邮箱已存在"""
    service = UserService()
    service.register(email="test@example.com", password="Pass123!")
    result = service.register(email="test@example.com", password="Pass123!")
    assert result.success is False
    assert result.error == "EMAIL_ALREADY_EXISTS"

@pytest.mark.parametrize("password,expected_error", [
    ("Pass1!", "PASSWORD_TOO_SHORT"),  # 7字符
    ("password!", "PASSWORD_MISSING_UPPERCASE"),
    ("PASSWORD1!", "PASSWORD_MISSING_LOWERCASE"),
    ("Password!", "PASSWORD_MISSING_DIGIT"),
])
def test_password_validation(service, password, expected_error):
    """测试: 密码规则校验"""
    result = service.register(email="test@example.com", password=password)
    assert result.success is False
    assert result.error == expected_error
```

## 性能测试

- 并发注册: 100用户同时注册 → 成功率>95%
- 响应时间: P95 < 300ms
```

---

## 注意事项

1. **测试先行**: 测试用例应在开发前编写（TDD）
2. **测试独立性**: 每个测试用例独立，可单独运行
3. **测试可重复**: 多次运行结果一致
4. **测试可维护**: 代码变化时测试易于更新
5. **覆盖率陷阱**: 不要为了覆盖率而写无意义的测试
