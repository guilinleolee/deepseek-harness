---
name: nine-dragons-ui2code
description: 九部天龙UI转代码 - 设计稿直接生成前端代码（三引擎联动）
invokable: true
argument-hint: [设计稿图片路径]
---
# 九部天龙UI转代码

> Gemini看图 + Claude规划 + Codex生成 + Gemini审查 = 设计稿直接转代码

你现在需要处理设计稿：**$ARGUMENTS**

## 🎯 三引擎联动流程

### 阶段1：09视觉师(Gemini) - 分析设计稿
1. 读取图片: `Read("$ARGUMENTS")`
2. 分析设计: 布局结构、组件树、样式规范
3. 输出: 组件树 + Tailwind配置

### 阶段2：02架构师(Sonnet) - 技术选型
1. 选择框架: React/Vue/Next.js
2. 选择样式: Tailwind CSS / CSS Modules
3. 输出: 技术方案

### 阶段3：03构建师(Codex) - 生成代码
1. 生成组件代码
2. 生成样式代码
3. 输出: 可运行的前端代码

### 阶段4：06审查师(Gemini) - UI审查
1. 对比设计稿和实现
2. 输出: 差异报告 + 改进建议

## 📋 执行步骤

请依次执行上述4个阶段，每步完成后再进入下一步。

## 📊 预期产出
- 完整的React组件代码
- Tailwind CSS样式
- 响应式布局代码
- 组件文档（07记录师生成）

## ⚠️ 注意事项
- 图片格式: PNG/JPG/WebP
- 分辨率要求: ≥1024x768
- Gemini免费额度: 1000次/天
