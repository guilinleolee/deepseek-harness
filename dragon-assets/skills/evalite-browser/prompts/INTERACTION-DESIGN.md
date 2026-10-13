# 交互测试设计提示词

## UI 交互验证测试指南

### 支持的交互动作

| 动作 | 说明 | 典型场景 |
|------|------|----------|
| `click` | 点击元素 | 按钮、链接、选项卡 |
| `dblclick` | 双击元素 | 编辑、展开 |
| `fill` | 填充输入框 | 文本输入、邮箱、密码 |
| `select` | 选择下拉选项 | 国家、语言、分类 |
| `hover` | 悬停元素 | 下拉菜单、工具提示 |
| `drag` | 拖拽元素 | 排序、重新排列 |
| `scroll` | 滚动页面/元素 | 加载更多、分页 |
| `press` | 按键 | Enter、Tab、Escape |
| `check` | 勾选复选框 | 表单同意、开关 |
| `uncheck` | 取消勾选 | 复选框取消 |

### 测试模板

```markdown
## [功能名称] 交互测试

### 测试目标
验证 [功能] 的用户交互行为符合预期。

### 测试场景

1. **正向流程**: 用户成功完成操作
2. **边界条件**: 空输入、特殊字符、最大长度
3. **错误处理**: 无效输入、服务器错误

### 断言类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `visible` | 元素可见 | 按钮、消息 |
| `hidden` | 元素隐藏 | 加载中、成功提示消失 |
| `contains_text` | 元素包含文本 | 错误消息、响应内容 |
| `has_value` | 输入框有值 | 表单填充 |
| `has_attribute` | 元素有属性 | aria-disabled |
| `has_count` | 元素数量 | 列表项数量 |
| `enabled` | 元素可交互 | 按钮可用 |
| `disabled` | 元素不可交互 | 禁用按钮 |
| `checked` | 复选框已勾选 | 同意条款 |
| `url_matches` | URL 匹配正则 | 导航成功 |
| `title_matches` | 标题匹配 | 页面标题 |

### 示例：表单提交测试

```json
{
  "name": "form-submission-test",
  "url": "http://localhost:3000/form",
  "steps": [
    {
      "action": "wait_for_selector",
      "selector": "form",
      "timeout": 5000
    },
    {
      "action": "fill",
      "selector": "[name='email']",
      "value": "user@example.com"
    },
    {
      "action": "fill",
      "selector": "[name='password']",
      "value": "SecurePass123!"
    },
    {
      "action": "fill",
      "selector": "[name='name']",
      "value": "Test User"
    },
    {
      "action": "click",
      "selector": "[type='submit']"
    },
    {
      "action": "wait_for_navigation",
      "timeout": 10000
    }
  ],
  "assertions": [
    {
      "type": "visible",
      "selector": ".success-message",
      "description": "成功消息可见"
    },
    {
      "type": "contains_text",
      "selector": ".success-message",
      "expected": "Thank you",
      "description": "成功消息包含感谢语"
    },
    {
      "type": "url_matches",
      "expected": ".*success.*",
      "description": "URL 包含 success"
    }
  ],
  "visual": {
    "enabled": true,
    "name": "form-submitted"
  }
}
```

### 示例：多页导航测试

```json
{
  "name": "navigation-flow-test",
  "url": "http://localhost:3000/",
  "steps": [
    {
      "action": "wait_for_selector",
      "selector": "nav"
    },
    {
      "action": "screenshot",
      "name": "home-page"
    },
    {
      "action": "click",
      "selector": "nav a[href='/about']"
    },
    {
      "action": "wait_for_navigation"
    },
    {
      "action": "screenshot",
      "name": "about-page"
    },
    {
      "action": "assertion",
      "type": "title_matches",
      "expected": "About"
    },
    {
      "action": "click",
      "selector": "nav a[href='/contact']"
    },
    {
      "action": "wait_for_navigation"
    },
    {
      "action": "screenshot",
      "name": "contact-page"
    },
    {
      "action": "hover",
      "selector": "footer a:first-child"
    },
    {
      "action": "scroll",
      "value": 300
    }
  ],
  "assertions": [
    {
      "type": "visible",
      "selector": "nav a[href='/about']",
      "description": "About 链接可见"
    },
    {
      "type": "visible",
      "selector": "nav a[href='/contact']",
      "description": "Contact 链接可见"
    },
    {
      "type": "url_matches",
      "expected": ".*contact.*",
      "description": "当前在 contact 页面"
    }
  ]
}
```

### 边界条件测试

```json
{
  "name": "form-boundary-tests",
  "url": "http://localhost:3000/form",
  "steps": [
    {
      "action": "fill",
      "selector": "[name='email']",
      "value": ""
    },
    {
      "action": "click",
      "selector": "[type='submit']"
    },
    {
      "action": "assertion",
      "type": "contains_text",
      "selector": ".error-message",
      "expected": "required",
      "description": "显示必填错误"
    }
  ]
}
```

### 等待策略

| 场景 | 策略 | 超时 |
|------|------|------|
| 页面导航 | `wait_for_navigation` | 30000ms |
| 元素出现 | `wait_for_selector` | 5000ms |
| 元素消失 | `wait_for_selector(hidden=True)` | 5000ms |
| 网络请求 | `wait_for_response` | 10000ms |
| 动画完成 | `wait_for_timeout` | 1000ms |
| 数据加载 | `wait_for_function` | 30000ms |

### 错误处理

```python
class RetryConfig:
    """重试配置"""
    max_attempts: int = 3      # 最大重试次数
    base_delay_ms: int = 1000  # 基础延迟
    max_delay_ms: int = 5000   # 最大延迟
    exponential_base: float = 2  # 指数退避基数

def calculate_delay(attempt: int, config: RetryConfig) -> int:
    """计算重试延迟"""
    delay = min(
        config.base_delay_ms * (config.exponential_base ** attempt),
        config.max_delay_ms
    )
    # 添加抖动 ±20%
    import random
    jitter = delay * random.uniform(-0.2, 0.2)
    return int(delay + jitter)
```

### CI/CD 集成

```yaml
interaction-test:
  runs-on: ubuntu-latest
  services:
    app:
      image: my-app:latest
      ports:
        - "3000:3000"
  steps:
    - name: Wait for app
      run: |
        for i in {1..30}; do
          curl -f http://localhost:3000 && break
          sleep 1
        done
    - name: Run interaction tests
      run: |
        evalite run \
          --config interaction-tests.json \
          --reporter json,html \
          --output reports/
    - name: Upload reports
      uses: actions/upload-artifact@v4
      with:
        name: test-reports
        path: reports/
```
