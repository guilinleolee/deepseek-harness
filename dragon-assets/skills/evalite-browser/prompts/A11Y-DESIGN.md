# 无障碍测试设计提示词

## WCAG 2.1 AA 合规性测试指南

### 测试范围

| 类别 | 规则数 | 关键规则 |
|------|--------|----------|
| 感知性 | 4 | 替代文本、适应性、区分性、可辨识性 |
| 可操作性 | 5 | 键盘可访问、可输入、时间充足、规避 |
| 可理解性 | 3 | 可读性、可预测性、输入协助 |
| 健壮性 | 1 | 兼容性 |

### 默认规则集

```python
DEFAULT_A11Y_RULES = [
    # 感知性
    "color-contrast",           # 颜色对比度 ≥ 4.5:1
    "image-alt",                 # 图片必须有 alt 文本
    "video-caption",            # 视频必须有字幕
    "marquee",                  # 禁止使用滚动字幕

    # 可操作性
    "keyboard",                 # 所有功能可通过键盘操作
    "no-autoplay-audio",       # 禁止自动播放音频
    "accesskeys",              # 避免重复快捷键
    "tabindex",                # 避免正数 tabindex
    "focus-order",             # 焦点顺序逻辑正确

    # 可理解性
    "label",                   # 表单元素必须有标签
    "link-name",               # 链接必须有可识别名称
    "language",                # 页面必须声明语言

    # 健壮性
    "aria-required-attr",      # ARIA 属性完整性
    "aria-valid-attr",        # ARIA 属性值有效
    "button-name",             # 按钮必须有名称
    "region",                  # 区域应有标题
]
```

### 测试模板

```markdown
## [页面名称] 无障碍审计

### 测试目标
确保 [功能] 符合 WCAG 2.1 AA 标准。

### 审计范围
- [ ] 颜色对比度
- [ ] 键盘导航
- [ ] 表单标签
- [ ] 图片替代文本
- [ ] ARIA 属性
- [ ] 焦点管理

### 执行步骤

1. **初始加载审计**
   ```python
   auditor = A11yAuditor(standard="WCAG2AA")
   report = auditor.audit(page, url=current_url)
   ```

2. **交互后审计**
   对每个用户交互后重新审计

3. **特定区域审计**
   ```python
   # 审计模态框
   modal = page.locator("[role='dialog']")
   modal_report = auditor.audit_element(modal, url=current_url)
   ```

### 断言配置

| 严重程度 | 违规数阈值 | 说明 |
|----------|------------|------|
| Critical | 0 | 必须修复 |
| Serious | 0 | 必须修复 |
| Moderate | ≤ 2 | 建议修复 |
| Minor | ≤ 5 | 可接受 |

### 常见违规修复

| 违规类型 | 原因 | 修复方案 |
|----------|------|----------|
| color-contrast | 前景/背景对比不足 | 提高对比度至 4.5:1+ |
| label | 缺少表单标签 | 添加 `<label for="">` |
| button-name | 按钮无文本 | 添加 `aria-label` 或文本内容 |
| image-alt | 图片缺少 alt | 添加描述性 alt 文本 |
| link-name | 链接无描述 | 添加 aria-label |

### 颜色对比度计算

```python
def calculate_contrast_ratio(foreground: str, background: str) -> float:
    """
    计算 WCAG 对比度
    返回值 >= 4.5 为 AA 标准
    """
    def luminance(hex_color: str) -> float:
        def channel(c):
            c = int(c, 16) / 255
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        r, g, b = channel(hex_color[1:3]), channel(hex_color[3:5]), channel(hex_color[5:7])
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    l1 = luminance(foreground)
    l2 = luminance(background)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

# 示例
ratio = calculate_contrast_ratio("#333333", "#ffffff")
# 返回 12.6，满足 AA 标准
```

### 键盘导航测试用例

```json
{
  "name": "keyboard-navigation-test",
  "url": "http://localhost:3000/form",
  "a11y": {
    "enabled": true,
    "standard": "WCAG2AA",
    "rules": ["keyboard", "focus-order", "button-name"]
  },
  "steps": [
    {
      "action": "press",
      "key": "Tab",
      "description": "第一个焦点应落在第一个输入框"
    },
    {
      "action": "assertion",
      "type": "focused",
      "selector": "[name='email']"
    },
    {
      "action": "fill",
      "selector": "[name='email']",
      "value": "user@example.com"
    },
    {
      "action": "press",
      "key": "Tab",
      "description": "焦点应移到密码输入框"
    },
    {
      "action": "assertion",
      "type": "focused",
      "selector": "[name='password']"
    },
    {
      "action": "press",
      "key": "Enter",
      "description": "Enter 键应提交表单"
    },
    {
      "action": "wait_for_navigation"
    }
  ],
  "assertions": [
    {
      "type": "visible",
      "selector": ".success-message",
      "description": "成功消息可见"
    }
  ]
}
```

### 报告生成

```python
# 生成 HTML 报告
report = auditor.audit(page)
html_report = auditor.generate_html_report(report, output_path="a11y-report.html")

# 报告内容
{
    "url": "http://localhost:3000/form",
    "timestamp": "2026-05-07T12:00:00Z",
    "violations": [
        {
            "id": "color-contrast",
            "impact": "serious",
            "description": "前景色与背景色对比度不足",
            "help": "确保文本与背景有足够对比度",
            "help_url": "https://dequeuniversity.com/rules/axe/color-contrast",
            "nodes": [
                {
                    "html": "<span class='muted'>灰色文字</span>",
                    "target": [".muted"],
                    "failure_summary": "前景色 #999999 与背景色 #ffffff 对比度为 2.85:1"
                }
            ]
        }
    ],
    "summary": {
        "total_violations": 1,
        "critical": 0,
        "serious": 1,
        "moderate": 0,
        "minor": 0
    }
}
```

### CI/CD 集成

```yaml
a11y-test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Install
      run: npm install && npx playwright install
    - name: Run a11y audit
      run: |
        evalite audit \
          --url http://localhost:3000 \
          --standard WCAG2AA \
          --report a11y-report.html
    - name: Check violations
      run: |
        VIOLATIONS=$(cat a11y-report.json | jq '.summary.total_violations')
        if [ $VIOLATIONS -gt 0 ]; then
          echo "Found $VIOLATIONS violations"
          exit 1
        fi
```
