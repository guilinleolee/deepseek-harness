---
name: critical-evidence
description: critical-evidence - 验证知识证据
invokable: true
---
# /critical-evidence - 验证知识证据

**天龙引擎 V7.4批判性思维 Layer 1 - 知识验证命令**

## 功能

验证指定知识条目的证据质量，包括：
- 证据来源检查
- 证据类型评分
- 置信度评估
- 过期状态检查

## 用法

```bash
/critical-evidence [fact-id]
```

### 参数

- `fact-id`: 知识条目ID（可选，不提供则显示所有待验证条目）

## 示例

### 验证指定条目
```bash
/critical-evidence fact-20260228-001
```

### 显示所有待验证条目
```bash
/critical-evidence
```

## 输出格式

```
## 🔍 知识证据验证

### 📋 条目信息
- **ID**: fact-20260228-001
- **知识**: React Query比Redux更适合数据获取
- **状态**: active
- **创建于**: 2026-02-28

### 📚 证据信息
- **来源**: https://react-query.tanstack.com/comparison
- **类型**: 官方文档 (official-docs)
- **置信度**: 🟢 极高可信 (1.0)
- **最后验证**: 2026-02-28

### ⚠️ 隐含假设
1. 项目使用React 18+
2. 主要关注服务端数据获取

### 🔄 反例/反对意见
1. **[强]** Redux仍然更适合复杂客户端状态管理
   - 来源: Redux官方文档
   - 有效性: strong

### 🔬 可证伪性声明
- **证伪方法**: 构建一个纯客户端状态管理场景，对比Redux和React Query的性能
- **测试标准**: React Query在客户端状态管理场景下性能显著低于Redux

### ✅ 验证结果
- **证据有效性**: 有效
- **是否需要重新验证**: 否
- **建议操作**: 无

### 📊 质量评分
- **证据质量**: 1.0/1.0
- **假设透明度**: 高 (2个显式假设)
- **反例覆盖率**: 中等 (1个强反例)
- **可证伪性**: 高 (明确测试方法)
```

## 实现细节

该命令调用 `critical-thinking-memory-layer.js` 中的验证逻辑，执行以下步骤：

1. 加载指定知识条目
2. 检查证据来源的可访问性（如果可能）
3. 根据证据类型计算置信度
4. 检查是否过期
5. 生成验证报告

## Hook集成

该命令与以下Hook集成：
- `critical-thinking-memory-layer.js` (SessionStart加载)
- 自动在SessionStart时显示待验证条目提醒

---

**命令版本**: 1.0.0
**最后更新**: 2026-02-28
