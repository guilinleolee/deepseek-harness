# 审批演练日志 · 5 封草稿

> 演示 §三 §3.5 中设计的"哈希绑定"机制
> 这是离线模拟——真实情况由 `approval/asked` + `approval/decided` session 事件对支撑

## 一、初始审批（5 封全通过）

| # | 客户 | 原 hash | 审批人 | 审批时间 | 操作 |
|---|---|---|---|---|---|
| 004 | KL Living Essentials | sha256:5678ef90 | [你] | 2026-08-11 14:23 | ✅ 通过 |
| 008 | Saigon Tech Home | sha256:ef567890 | [你] | 2026-08-11 14:25 | ✅ 通过 |
| 013 | Vietnam Smart Kitchen | sha256:abcd1234 | [你] | 2026-08-11 14:28 | ✅ 通过 |
| 018 | Hanoi Living Hub | sha256:1234abcd | [你] | 2026-08-11 14:31 | ✅ 通过 |
| 026 | PT Mitra Home | sha256:90abcdef | [你] | 2026-08-11 14:34 | ✅ 通过 |

`approved_hashes.json`（演练版）：

```json
{
  "version": 1,
  "approvals": {
    "004": {
      "draftHash": "sha256:5678ef90",
      "approvedAt": "2026-08-11T14:23:00Z",
      "approvedBy": "manual",
      "expiresAt": "2026-09-10T14:23:00Z"
    },
    "008": {
      "draftHash": "sha256:ef567890",
      "approvedAt": "2026-08-11T14:25:00Z",
      "approvedBy": "manual",
      "expiresAt": "2026-09-10T14:25:00Z"
    },
    "013": {
      "draftHash": "sha256:abcd1234",
      "approvedAt": "2026-08-11T14:28:00Z",
      "approvedBy": "manual",
      "expiresAt": "2026-09-10T14:28:00Z"
    },
    "018": {
      "draftHash": "sha256:1234abcd",
      "approvedAt": "2026-08-11T14:31:00Z",
      "approvedBy": "manual",
      "expiresAt": "2026-09-10T14:31:00Z"
    },
    "026": {
      "draftHash": "sha256:90abcdef",
      "approvedAt": "2026-08-11T14:34:00Z",
      "approvedBy": "manual",
      "expiresAt": "2026-09-10T14:34:00Z"
    }
  }
}
```

## 二、改稿验证：013 Vietnam Smart Kitchen

### 触发

2026-08-12 上午，你发现 013 草稿里"PT Mitra Home"客户案例拿捏得不够准——该客户综合家居全平台，**不是双平台厨房小电**，案例匹配度偏低。改成 "Mekong Home Store"（双平台厨房小电）更精确。

### 操作

```bash
# 修改 drafts/013-vietnam-smart-kitchen.md（替换案例）
# 重新计算 hash
node tools/hash-draft.js drafts/013-vietnam-smart-kitchen.md
# 新 hash: sha256:newsha9876
```

### 系统响应（预期）

`lg_plan_followup` 在入口断言时检测：

```
批准记录 hash:  sha256:abcd1234   (旧)
当前草稿 hash:  sha256:newsha9876 (新)
匹配: false
→ 拒绝执行，返回错误：
  "draft 013 not approved: hash mismatch
   (was sha256:abcd1234, now sha256:newsha9876)
   re-run lg_review_drafts to approve the new version"
```

### 演练意义

这就是 §三 §3.5 中"哈希绑定"设计的**核心价值**：

1. **改稿透明**：人工改了哪封，对应批准自动失效，必须重新审
2. **审计可追**：每次 hash 变更都进入审计日志（`approval/decided` 事件记录 `previousHash` / `currentHash`）
3. **零绕过**：模型层无法跳过——`lg_plan_followup` 入口断言不看模型 prompt，看磁盘文件

## 三、改稿后的二次审批

| # | 客户 | 旧 hash | 新 hash | 审批时间 | 操作 |
|---|---|---|---|---|---|
| 013 | Vietnam Smart Kitchen | sha256:abcd1234 | sha256:newsha9876 | 2026-08-12 11:15 | ✅ 重新通过 |

`approved_hashes.json` v2（演练版）：

```json
{
  "version": 2,
  "approvals": {
    ...
    "013": {
      "draftHash": "sha256:newsha9876",
      "previousHash": "sha256:abcd1234",
      "approvedAt": "2026-08-12T11:15:00Z",
      "approvedBy": "manual",
      "expiresAt": "2026-09-11T11:15:00Z"
    }
  }
}
```

## 四、演练发现

### 发现 1：expiresAt 不应硬编码 30 天

不同客户跟进节奏不同：
- A 级融资客户：2 周内必须联系，否则错过窗口
- C 级观察客户：1 个月无妨

**改进**：expiresAt 由评分等级决定（A=14 天 / B=30 天 / C=60 天）。

### 发现 2：人工审批成本不低

5 封审批花了 11 分钟。L 套餐 30 客户 × A+B 级 = 12+10=22 封，**仅审批就需要 ~50 分钟**。

**改进**：
- 提供批量审批 UI（多选 + 一键通过）
- 允许"群发模板"绕过单封审批（C 级客户）
- 审计上不记录每封，只记录批量动作

### 发现 3：改稿后"重新审批"≠ "重新走 lg_review_drafts"

演练中假设审批是同 UI，但实际 DSH 中是 `ask_user_question` 调用——每次改稿都要触发一次提问，会让模型感觉"啰嗦"。

**改进**：
- 工具内部检测 hash 变更后**自动**问用户一次（"013 草稿改了，是否重新审批？"）
- 减少模型 prompt 长度

## 五、给 §三私有部署授权版的提示

| 项 | 必须 |
|---|---|
| `approved_hashes.json` 必须按租户隔离（不同客户的批准互不影响） | ✅ |
| hash 算法必须固定（演练用了 sha256，生产必须一致） | ✅ |
| 审批日志必须可导出（用于 §三 §6 的合规审计） | ✅ |
| UI 审批必须支持批量（22 封单审会劝退用户） | ✅ |
| hash mismatch 错误信息必须可定位到具体草稿 | ✅ |