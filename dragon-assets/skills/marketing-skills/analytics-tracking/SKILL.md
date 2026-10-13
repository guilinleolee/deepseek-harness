---
name: analytics-tracking
description: "数据追踪与分析 - 埋点设计、数据采集、分析报告。"
trigger: "数据追踪、埋点、数据分析、GA、事件追踪"
metadata:
  version: 1.0.0
  source: https://github.com/coreyhaines31/marketingskills
---

# Analytics Tracking

> **核心价值**：没有数据就没有优化，追踪是所有决策的基础。

## Before Starting

1. 确认已完善 `product-marketing-context`
2. 明确需要追踪的关键业务目标

---

## 追踪架构

### 数据层级

```
┌─────────────────────────────────────────────────────┐
│                   分析工具层                         │
│   GA4 | Mixpanel | Amplitude | GrowingIO           │
└─────────────────────────────────────────────────────┘
                        ↑
┌─────────────────────────────────────────────────────┐
│                   数据采集层                         │
│   GTM | Segment | 自定义SDK                        │
└─────────────────────────────────────────────────────┘
                        ↑
┌─────────────────────────────────────────────────────┐
│                   事件追踪层                         │
│   页面浏览 | 用户行为 | 业务事件                     │
└─────────────────────────────────────────────────────┘
```

---

## 事件追踪清单

### 必埋点事件

#### 用户行为事件

| 事件名称 | 触发条件 | 参数 |
|----------|----------|------|
| `page_view` | 页面加载 | page_path, page_title |
| `button_click` | 按钮点击 | button_id, button_text |
| `form_submit` | 表单提交 | form_id, form_name |
| `file_download` | 文件下载 | file_name, file_type |
| `video_play` | 视频播放 | video_id, video_name |

#### 业务事件

| 事件名称 | 触发条件 | 参数 |
|----------|----------|------|
| `signup` | 注册成功 | user_id, method |
| `login` | 登录成功 | user_id, method |
| `trial_start` | 开始试用 | user_id, plan |
| `purchase` | 付费成功 | user_id, amount, plan |
| `upgrade` | 升级套餐 | user_id, from_plan, to_plan |
| `churn` | 流失/取消 | user_id, reason |

### 事件参数规范

```yaml
# 事件参数标准
event_name: signup
parameters:
  user_id: string, required
  method: enum, [email, google, github]
  plan: enum, [free, pro, enterprise]
  utm_source: string, optional
  utm_medium: string, optional
  utm_campaign: string, optional
```

---

## GTM配置指南

### 1. 基础配置

```yaml
# GTM基础变量
variables:
  - name: Page Path
    type: URL
    component: Path

  - name: Page Title
    type: Page Title

  - name: User ID
    type: Data Layer Variable
    variable_name: userId

# 基础触发器
triggers:
  - name: All Pages
    type: Page View

  - name: Form Submit
    type: Form Submission

  - name: Click - CTA
    type: Click
    condition: element classes contains 'cta-btn'
```

### 2. 代码模板

```html
<!-- Google Tag Manager -->
<script>
dataLayer = [{
  'userId': 'USER_ID',
  'userType': 'free/pro/enterprise',
  'pageCategory': 'home/pricing/blog'
}];
</script>
<!-- End Google Tag Manager -->
```

---

## 分析报告模板

### 用户获取报告

```markdown
## 用户获取分析

### 渠道表现
| 渠道 | 访问量 | 注册量 | 注册率 | CAC |
|------|--------|--------|--------|-----|
| [渠道] | [数量] | [数量] | [比率] | [金额] |

### 趋势分析
- WoW增长：[百分比]
- MoM增长：[百分比]

### 优化建议
1. [建议1]
2. [建议2]
```

### 转化漏斗报告

```markdown
## 转化漏斗分析

### 漏斗数据
| 步骤 | 用户数 | 转化率 | 流失率 |
|------|--------|--------|--------|
| 访问 | 10000 | 100% | - |
| 注册 | 500 | 5% | 95% |
| 激活 | 250 | 50% | 50% |
| 付费 | 50 | 20% | 80% |

### 瓶颈分析
- 最大流失点：[步骤]
- 流失原因：[原因]
- 优化建议：[建议]
```

---

## 关键指标仪表板

### 必看指标

| 指标 | 数据源 | 更新频率 |
|------|--------|----------|
| DAU/MAU | 产品分析工具 | 每日 |
| 注册转化率 | 产品分析工具 | 每日 |
| 付费转化率 | CRM + 支付 | 每日 |
| CAC | 广告平台 | 每周 |
| LTV | 订阅数据 | 每月 |
| NRR | 订阅数据 | 每月 |

---

## Output Format

```markdown
## 数据追踪方案

### 追踪架构
- 分析工具：[工具名称]
- 数据采集：[GTM/Segment/自定义]
- 事件数量：[数量]

### 事件清单
| 事件名称 | 触发条件 | 参数 |
|----------|----------|------|
| [事件] | [条件] | [参数列表] |

### 配置步骤
1. [步骤1]
2. [步骤2]
3. [步骤3]

### 验证清单
- [ ] 页面浏览追踪正常
- [ ] 用户行为追踪正常
- [ ] 业务事件追踪正常
- [ ] 数据在分析工具中可见
```

---

## Related Skills

- [revops](../revops/SKILL.md) - 收益运营
- [page-cro](../page-cro/SKILL.md) - 着陆页优化
- [paid-ads](../paid-ads/SKILL.md) - 付费广告