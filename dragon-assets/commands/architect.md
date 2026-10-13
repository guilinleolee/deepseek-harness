---
name: architect
description: 架构设计主流程 - 从需求到架构方案的全流程
invokable: true
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, TodoWrite
---
## Context

- Current git status: !`git status`
- Current git diff: !`git diff HEAD`
- Current branch: !`git branch --show-current`

## Your Task

执行完整的架构设计流程：

### 步骤 1: 需求理解
- 理解业务需求和功能要求
- 识别非功能性需求（性能、安全、可扩展性）
- 确定技术约束和限制

### 步骤 2: 顶层设计
- 定义系统边界和模块划分
- 设计核心抽象和接口
- 确定技术栈选择

### 步骤 3: 详细设计
- 设计数据模型和存储方案
- 设计API接口和通信协议
- 设计部署架构和基础设施

### 步骤 4: 风险评估
- 识别技术风险和依赖风险
- 评估复杂度和工期
- 制定风险缓解策略

## 输出

生成 ARCHITECTURE.md 文档，包含：
- 系统概览
- 模块划分
- 数据模型
- API设计
- 部署架构
- 风险清单

## 注意事项

- 使用第一性原理思维，剥离类比找本质约束
- 遵循统筹兼顾原则，平衡各方需求
- 识别主要矛盾，聚焦核心问题
