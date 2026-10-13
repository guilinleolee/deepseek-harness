# Lessons Learned - 系统经验教训库

> **目的**: 集中存储AI Agent在执行过程中学到的经验教训，避免重复错误，持续优化性能
>
> **维护**: 自动由 `lessons-logger.js` Hook 维护，也可手动编辑
>
> **版本**: 1.0.0
>
> **创建**: 2026-08-07

---

## 📋 说明

此文件由 `lessons-logger.js` Hook 自动维护，记录：
- 用户纠正的问题
- 重复出现的错误
- 三次失败后的模式
- 验证有效的最佳实践

每个条目包含：
- 问题描述
- 解决方案
- 触发条件
- 相关上下文

---

## 📚 经验教训条目


### [TRIPLE-FAILURE] MVP-test 三次失败需要替代方案

**日期**: 2026-08-07
**Agent**: 03-builder
**优先级**: P0
**标签**: #systematic-debugging #alternative-approach #node

**问题**:
ENOENT: file not found at /tmp/test/path

**解决方案**:
改用 require.resolve 替代硬编码路径

**上下文**:
```
{
  "tool": "Bash",
  "command": "cat /tmp/test/path"
}
```

**记录方式**: triple-failure


