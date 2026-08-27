---
license: UNKNOWN
name: ai-regression-testing
description: Regression testing strategies for AI-assisted development. Sandbox-mode API testing without database dependencies, automated bug-check workflows, and patterns to catch AI blind spots where the same model writes and reviews code.
github_repo: affaan-m/everything-claude-code
github_hash: 4e66b2882da9afb9747468b08a253ca2f09c85f3
last_updated: 2026-04-25
source_type: derived
origin: ECC (everything-claude-code)
triggers: ["ai regression testing", "AI Regression Testing"]
---

# AI Regression Testing

> 来源: [affaan-m/everything-claude-code/skills/ai-regression-testing](https://github.com/affaan-m/everything-claude-code)

## 功能概述

专为AI辅助开发设计的回归测试策略。解决AI同一模型写代码和审查代码时产生的系统性盲点问题。

## 核心问题

当AI写代码然后审查自己的工作时，会将相同的假设带入两个步骤：

```
AI写修复 → AI审查修复 → AI说"看起来正确" → Bug仍然存在
```

## 核心问题：沙箱/生产路径不一致

这是AI引入的第一大回归模式：

```
Fix 1: 添加notification_settings到API响应
  → 忘记添加到SELECT查询
  → AI审查时没发现（相同的盲点）

Fix 2: 添加到SELECT查询
  → TypeScript构建错误（生成的类型中没有该列）
  → AI审查Fix 1但没发现SELECT问题

Fix 3: 改为SELECT *
  → 修复了生产路径，忘了沙箱路径
  → AI审查再次错过（第4次发生）

Fix 4: 测试首次运行立即发现 ✅
```

## 沙箱模式API测试

### 核心原则

**只对发现bug的代码写测试，不对正常工作的代码写测试。**

```typescript
// 测试助手
export function createTestRequest(
  url: string,
  options?: {
    method?: string;
    body?: Record<string, unknown>;
    headers?: Record<string, string>;
    sandboxUserId?: string;
  },
): NextRequest {
  // 强制沙箱模式
  const reqHeaders: Record<string, string> = { ...headers };
  if (sandboxUserId) {
    reqHeaders["x-sandbox-user-id"] = sandboxUserId;
  }
  return new NextRequest(`http://localhost:3000${url}`, {
    method: method || "GET",
    headers: reqHeaders,
    body: body ? JSON.stringify(body) : undefined,
  });
}
```

### 响应契约测试

```typescript
// 必须包含的字段 — 定义合同
const REQUIRED_FIELDS = [
  "id", "email", "full_name", "phone", "role",
  "created_at", "avatar_url",
  "notification_settings",  // ← 发现bug后添加
];

describe("GET /api/user/profile", () => {
  it("returns all required fields", async () => {
    const req = createTestRequest("/api/user/profile");
    const res = await GET(req);
    const { status, json } = await parseResponse(res);

    expect(status).toBe(200);
    for (const field of REQUIRED_FIELDS) {
      expect(json.data).toHaveProperty(field);
    }
  });
});
```

## AI回归模式

### 模式1: 沙箱/生产路径不匹配 (最常见)

```typescript
// ❌ AI只添加到生产路径
if (isSandboxMode()) {
  return { data: { id, email, name } };  // 缺少新字段
}
return { data: { id, email, name, notification_settings } };

// ✅ 两条路径必须返回相同形状
if (isSandboxMode()) {
  return { data: { id, email, name, notification_settings: null } };
}
return { data: { id, email, name, notification_settings } };
```

### 模式2: SELECT子句遗漏

```typescript
// ❌ 添加了新列但不在SELECT中
const { data } = await supabase
  .from("users")
  .select("id, email, name")  // notification_settings不在这里
  .single();

// ✅ 使用SELECT *或显式包含新列
const { data } = await supabase
  .from("users")
  .select("*")
  .single();
```

### 模式3: 错误状态泄露

```typescript
// ❌ 设置错误状态但没清除旧数据
catch (err) {
  setError("Failed to load");
  // reservations仍然显示上一个tab的数据！
}

// ✅ 错误时清除相关状态
catch (err) {
  setReservations([]);  // 清除陈旧数据
  setError("Failed to load");
}
```

### 模式4: 乐观更新没有正确回滚

```typescript
// ❌ 失败时没有回滚
const handleRemove = async (id: string) => {
  setItems(prev => prev.filter(i => i.id !== id));
  await fetch(`/api/items/${id}`, { method: "DELETE" });
  // 如果API失败，item从UI消失但DB中仍存在
};

// ✅ 捕获之前状态并在失败时回滚
const handleRemove = async (id: string) => {
  const prevItems = [...items];
  setItems(prev => prev.filter(i => i.id !== id));
  try {
    const res = await fetch(`/api/items/${id}`, { method: "DELETE" });
    if (!res.ok) throw new Error("API error");
  } catch {
    setItems(prevItems);  // 回滚
  }
};
```

## Bug检查工作流

### 步骤

```
User: "检查bug" (或 "/bug-check")
  │
  ├─ Step 1: npm run test (强制)
  │   ├─ FAIL → 机械发现bug（无需AI判断）
  │   └─ PASS → 继续
  │
  ├─ Step 2: npm run build
  │   ├─ FAIL → 类型错误
  │   └─ PASS → 继续
  │
  ├─ Step 3: AI代码审查（已知盲点）
  │   └─ 发现问题报告
  │
  └─ Step 4: 每个修复都写回归测试
      └─ 下次bug检查时捕获
```

## 天龙引擎集成

### 适用岗位

| 岗位 | 集成方式 | 增强能力 |
|------|---------|---------|
| **04验证师** | 沙箱回归测试 | AI盲点检测 + 路径一致性 |
| **06审查师** | 代码审查增强 | SELECT完整性 + 错误处理 |
| **03构建师** | AI安全编码 | 乐观更新回滚 + 状态清理 |

### 天龙引擎增强

```
┌─────────────────────────────────────────────────────────────┐
│ 天龙引擎 AI回归测试体系                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   AI开发盲点:                                              │
│   AI写代码 + AI审查代码 = 相同假设 = 系统性盲点              │
│                                                             │
│   天龙引擎协同:                                             │
│   ├── 04验证师  → 强制测试优先 + 沙箱/生产一致性            │
│   ├── 06审查师  → SELECT完整性 + 错误状态审查               │
│   └── 03构建师  → 安全编码模式 + 回滚机制                   │
│                                                             │
│   核心策略:                                                 │
│   ├── Bug发现处写测试 → 不对正常代码写测试                   │
│   ├── 沙箱/生产路径 → 必须返回相同字段                       │
│   └── 自动化优先 → 测试捕获而非AI判断                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 快速参考

| AI回归模式 | 测试策略 | 优先级 |
|-----------|---------|--------|
| 沙箱/生产不匹配 | 断言沙箱模式返回相同形状 | 🔴 高 |
| SELECT子句遗漏 | 断言响应包含所有必需字段 | 🔴 高 |
| 错误状态泄露 | 断言错误时状态清理 | 🟡 中 |
| 缺少回滚 | 断言API失败时状态恢复 | 🟡 中 |
| 类型转换掩盖null | 断言字段不是undefined | 🟡 中 |

## 最佳实践

1. **立即写测试**: 在修复bug后立即写测试（如果可能，修复前写）
2. **测试响应形状**: 测试API响应形状，而非实现
3. **测试第一**: 每次bug检查首先运行测试
4. **快速测试**: 保持测试快速（沙箱模式<1秒）
5. **命名bug测试**: 用bug编号命名测试（如"BUG-R1回归"）

## 参考资料

- [Everything Claude Code](https://github.com/affaan-m/everything-claude-code)
- [ECC ai-regression-testing](https://github.com/affaan-m/everything-claude-code/tree/main/skills/ai-regression-testing)

---

**版本**: V1.0 | **兼容性**: 天龙引擎 V8.67+ | **来源**: ECC
