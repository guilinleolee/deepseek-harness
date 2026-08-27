# 视觉测试设计提示词

## 视觉回归测试设计指南

### 基础原则

1. **关键状态覆盖**：每个页面至少测试 3 个关键状态
2. **动态内容隔离**：对动态内容使用 `wait_for_timeout` 稳定
3. **视口多样性**：桌面 + 平板 + 移动端

### 测试场景设计模板

```markdown
## [页面名称] 视觉回归测试

### 测试目标
验证 [功能] 在各种条件下的视觉一致性。

### 关键状态
1. **初始状态**: 页面加载完成
2. **交互后**: [用户操作后]
3. **加载中**: 数据加载中
4. **空状态**: 无数据时

### 断言阈值
- 差异阈值: 0.1 (10%)
- 差异高亮: 开启
- 全页截图: 是

### 等待策略
- 动态内容等待: 500ms
- 动画等待: 1000ms
- 加载完成等待: wait_for_selector "body"
```

### 示例：聊天应用视觉测试

```json
{
  "name": "chat-visual-regression",
  "url": "http://localhost:3000/chat",
  "steps": [
    {
      "action": "wait_for_selector",
      "selector": "[data-testid='chat-input']",
      "timeout": 10000
    },
    {
      "action": "screenshot",
      "name": "chat-initial"
    },
    {
      "action": "fill",
      "selector": "[data-testid='chat-input']",
      "value": "Hello, what can you do?"
    },
    {
      "action": "screenshot",
      "name": "chat-input-filled"
    },
    {
      "action": "click",
      "selector": "[data-testid='send-button']"
    },
    {
      "action": "wait_for_selector",
      "selector": "[data-testid='response']",
      "timeout": 30000
    },
    {
      "action": "screenshot",
      "name": "chat-response-received"
    }
  ],
  "visual": {
    "enabled": true,
    "threshold": 0.1,
    "full_page": true,
    "animations_wait": 1000,
    "dynamic_content_wait": 500
  }
}
```

### 视觉差异分析

| 差异类型 | 原因 | 阈值建议 |
|----------|------|----------|
| 字体渲染 | 操作系统差异 | 0.15 |
| 抗锯齿 | 浏览器版本 | 0.12 |
| 图标 | CDN 加载 | 0.05 |
| 布局偏移 | CSS 渲染 | 0.08 |

### 常见问题排查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 全页高度变化 | 动态内容加载 | 使用固定视口高度 |
| 截图不一致 | 动画/过渡 | 添加 `animations_wait` |
| 字体差异 | 系统字体 | 注入 CSS 覆盖 |
| 闪烁内容 | 广告/通知 | 使用 headless 模式 |

### 响应式测试矩阵

| 视口 | 宽度 | 高度 | 典型场景 |
|------|------|------|----------|
| Desktop HD | 1920 | 1080 | 桌面浏览器 |
| Desktop | 1366 | 768 | 笔记本 |
| Tablet | 768 | 1024 | iPad 竖屏 |
| Mobile | 375 | 667 | iPhone SE |

### 批量视觉测试配置

```json
{
  "name": "batch-visual-test",
  "pages": [
    { "name": "home", "url": "/", "wait_for": "body" },
    { "name": "about", "url": "/about", "wait_for": "main" },
    { "name": "contact", "url": "/contact", "wait_for": "form" },
    { "name": "pricing", "url": "/pricing", "wait_for": ".pricing-table" },
    { "name": "features", "url": "/features", "wait_for": ".feature-grid" }
  ],
  "visual": {
    "enabled": true,
    "threshold": 0.1,
    "full_page": true,
    "animations_wait": 1000,
    "dynamic_content_wait": 500
  }
}
```

### 视觉测试 CI/CD 集成

```yaml
# GitHub Actions 示例
visual-test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Install dependencies
      run: npm install && npx playwright install
    - name: Run visual tests
      run: evalite visual --config visual-tests.json
    - name: Upload baseline
      if: github.ref == 'main'
      uses: actions/upload-artifact@v4
      with:
        name: baseline-screenshots
        path: baseline/
    - name: Download baseline
      if: github.ref != 'main'
      uses: actions/download-artifact@v4
      with:
        name: baseline-screenshots
        path: baseline/
    - name: Visual diff report
      uses: actions/upload-artifact@v4
      with:
        name: visual-diff-report
        path: reports/diffs/
```
