---
license: UNKNOWN
name: agent-payment-x402
description: Add x402 payment execution to AI agents — per-task budgets, spending controls, and non-custodial wallets via MCP tools. Use when agents need to pay for APIs, services, or other agents.
github_repo: affaan-m/everything-claude-code
github_hash: 4e66b2882da9afb9747468b08a253ca2f09c85f3
last_updated: 2026-04-25
source_type: derived
origin: ECC (everything-claude-code)
triggers: ["agent payment x402", "Agent Payment Execution (x402)"]
---

# Agent Payment Execution (x402)

> 来源: [affaan-m/everything-claude-code/skills/agent-payment-x402](https://github.com/affaan-m/everything-claude-code)

## 功能概述

为AI Agent添加自主支付能力，使用x402 HTTP支付协议和MCP工具，实现内置支出控制。Agent可以支付API、服务或其他Agent，无托管风险。

## 何时使用

- Agent需要支付API调用
- 购买外部服务
- 与其他Agent结算
- 强制单任务支出限制
- 管理非托管钱包

## 工作原理

### x402协议
x402将HTTP 402 (Payment Required) 扩展为机器可协商的流程。当服务器返回`402`时，Agent的支付工具自动协商价格、检查预算、签署交易并重试 — 无需人工介入。

### 支出控制
每个支付工具调用强制执行`SpendingPolicy`：

| 控制类型 | 说明 |
|---------|------|
| **Per-task budget** | 单个Agent操作的最大支出 |
| **Per-session budget** | 整个会话的累计限制 |
| **Allowlisted recipients** | 限制Agent可以支付的地址/服务 |
| **Rate limits** | 每分钟/小时的交易上限 |

### 非托管钱包
Agent通过ERC-4337智能账户持有自己的密钥。编排器在委托前设置策略；Agent只能在限制内支出。无池化资金，无托管风险。

## MCP集成

支付层暴露标准MCP工具，可插入任何Claude Code或Agent框架设置。

```json
{
  "mcpServers": {
    "agentpay": {
      "command": "npx",
      "args": ["agentwallet-sdk@6.0.0"]
    }
  }
}
```

### 可用工具

| 工具 | 用途 |
|------|------|
| `get_balance` | 检查Agent钱包余额 |
| `send_payment` | 向地址或ENS发送支付 |
| `check_spending` | 查询剩余预算 |
| `list_transactions` | 审计所有支付记录 |

### 4路径预算检查

```typescript
async function preToolCheck(agentpay: Client, apiCost: number): Promise<void> {
  // Path 1: 无效输入 (NaN/Infinity bypass)
  if (!Number.isFinite(apiCost) || apiCost < 0) {
    throw new Error(`Invalid apiCost: ${apiCost} — action blocked`);
  }

  // Path 2: 传输/连接失败
  let result;
  try {
    result = await agentpay.callTool({ name: "check_spending" });
  } catch (err) {
    throw new Error(`Payment service unreachable — action blocked: ${err}`);
  }

  // Path 3: 工具返回错误 (e.g., auth failure)
  if (result.isError) {
    throw new Error(`check_spending failed — action blocked: ${JSON.stringify(result.content)}`);
  }

  // Path 4: 解析并验证响应格式
  let remaining: number;
  try {
    const parsed = JSON.parse((result.content as Array<{text: string}>)[0].text);
    if (!Number.isFinite(parsed?.remaining)) {
      throw new TypeError("missing or non-finite 'remaining' field");
    }
    remaining = parsed.remaining;
  } catch (err) {
    throw new Error(`check_spending returned unexpected format — action blocked: ${err}`);
  }

  // Path 5: 预算超支
  if (remaining < apiCost) {
    throw new Error(`Budget exceeded: need $${apiCost} but only $${remaining} remaining`);
  }
}
```

## 天龙引擎集成

### 适用岗位

| 岗位 | 集成方式 | 增强能力 |
|------|---------|---------|
| **09-02 编排协调师** | 支付编排 | 多Agent资源结算 |
| **03构建师** | API调用 | 付费API预算控制 |
| **17-01 数据分析师** | 数据采购 | API成本优化 |

### 安全原则

| 原则 | 说明 |
|------|------|
| **编排器设置策略** | 策略由编排层在委托前设置，不是Agent可调用的工具 |
| **失败关闭** | 支付工具不可达时，阻止付费操作 |
| **固定依赖** | 始终在MCP配置中指定精确版本 |
| **审计追踪** | 在post-task hooks中使用`list_transactions`记录支出 |
| **先测测试网** | 使用Base Sepolia开发；切换到Base主网进行生产 |

### MCP配置

```json
// claudecode.json 或 MCP配置
{
  "mcpServers": {
    "agentpay": {
      "command": "npx",
      "args": ["agentwallet-sdk@6.0.0"],
      "env": {
        "WALLET_PRIVATE_KEY": "${WALLET_PRIVATE_KEY}"
      }
    }
  }
}
```

### 编排器集成示例

```typescript
// 编排器: 委托前设置支出策略
const policyResult = await agentpay.callTool({
  name: "set_policy",
  arguments: {
    per_task_budget: 0.50,
    per_session_budget: 5.00,
    allowlisted_recipients: ["api.example.com"],
  },
});
if (policyResult.isError) {
  throw new Error(`Failed to set spending policy — do not delegate: ${JSON.stringify(policyResult.content)}`);
}
```

### 调用示例

```bash
# 检查余额
agentpay get_balance

# 发送支付
agentpay send_payment --to "0x..." --amount 0.01 --recipient "api.example.com"

# 查询预算
agentpay check_spending

# 审计追踪
agentpay list_transactions --limit 20

# 天龙引擎集成
[@编排协调师] 使用x402支付API调用费用
[@构建师] 为这个API调用设置0.05美元的预算上限
```

## 生产参考

- **npm**: [`agentwallet-sdk`](https://www.npmjs.com/package/agentwallet-sdk)
- **协议规范**: [x402.org](https://x402.org)
- **NVIDIA集成**: [PR #17](https://github.com/NVIDIA/NeMo-Agent-Toolkit-Examples/pull/17) — NVIDIA Agent示例中的x402支付工具

## 最佳实践

1. **委托前设置预算**：生成子Agent时，通过编排层附加SpendingPolicy
2. **固定依赖版本**：始终在MCP配置中指定精确版本
3. **审计追踪**：使用`list_transactions`记录每次支出
4. **失败关闭**：支付工具不可达时阻止操作，不fallback到无计量访问
5. **安全审查配合**：支付工具是高权限的，应用与shell访问相同的审查标准
6. **先测测试网**：使用Base Sepolia开发

## 参考资料

- [Everything Claude Code](https://github.com/affaan-m/everything-claude-code)
- [ECC agent-payment-x402](https://github.com/affaan-m/everything-claude-code/tree/main/skills/agent-payment-x402)

---

**版本**: V1.0 | **兼容性**: 天龙引擎 V8.65+ | **来源**: ECC
