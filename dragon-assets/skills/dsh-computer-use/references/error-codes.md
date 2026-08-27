# 4 类 host-enforced 错误码 · 完整映射

> **来源**:[Anionex/dsh-computer-use README § "Status and limitations"](https://github.com/Anionex/dsh-computer-use) · 实拉 2026-08-23

## 总览

| 错误码 | 类别 | 触发 | 模型能否改? | 处置路径 |
|--------|------|------|-------------|---------|
| `COMPUTER_UNSUPPORTED_PLATFORM` | 平台 | Windows / Linux 启动 | ❌ | DSH profile 正常启动 · Tools 不注册 · Web Settings 提示 |
| `COMPUTER_PERMISSION_REQUIRED` | 权限 | app 不在 grants + DSH policy 是 `never` | ❌ | Settings 加 exact bundle id 或换 `ask` preset |
| `COMPUTER_TARGET_AMBIGUOUS` | 解析 | `targetHandle` 0 或 >1 候选 | ❌ | resolver fail-closed · 不猜 |
| `COMPUTER_TARGET_LOW_CONFIDENCE` | 解析 | 语义匹配 confidence 不足 | ❌ | resolver fail-closed · 不猜 |
| `COMPUTER_TARGET_REBIND_REQUIRES_CONFIRMATION` | 安全 | 高风险目标 rebind | ❌ | one-use token 作废 · 重观测 + 重确认 |

## 1. COMPUTER_UNSUPPORTED_PLATFORM

**触发条件**:`darwin` 平台检查失败,非 arm64/x86_64 主机,或 macOS < 14。

**用户感知**:
- DSH Web / Headless Profile 正常启动,不 crash
- Tools 不注册(无 `computer_click` / `computer_observe` 等)
- Skill 静默加载(无 Tools 可调用)
- Web Settings 显示红字 `COMPUTER_UNSUPPORTED_PLATFORM`

**当前状态**(2026-08-23):主机是 Windows,**所有 Tool 调用预期都会走到这个分支**。

**对策**:不在 Windows 上调任何 `computer_*` Tool,改用 `agent-browser` / `dsh-vision-toolkit` / API / CLI。

## 2. COMPUTER_PERMISSION_REQUIRED

**触发条件**:
- 调用 Tool 时 bundle id 不在 `grants` 列表
- 且 DSH 当前 preset 的 `approval/policy` 是 `never`(典型:`danger-full-access`)

**关键设计**:`danger-full-access` **不是** Computer Use 的安全沙盒 —— 文档明确指出它"不能防止直接 native 调用"。Computer Use 的安全模型是双 lease + exact bundle-id + 用户决策,不是文件权限。

**对策**:
- 路径 A:Computer Use Settings → Grants → 加 exact bundle id
- 路径 B:换 DSH preset 为 `approval/policy: ask`(用户每次 Tool 调用都会弹审批)

**重要**:这个错误**不**记为 user rejection(只在 user 显式拒绝时才记)。

## 3. COMPUTER_TARGET_AMBIGUOUS / COMPUTER_TARGET_LOW_CONFIDENCE

**触发条件**:
- `targetHandle` 解析得到 0 或 >1 候选
- 或语义匹配(rebind) 的 `confidence` 低于阈值

**resolver 行为**:
1. 先试 **exact-locator**(原 index + targetHandle)
2. 失败 → 试 **native-identifier**(macOS `AXIdentifier`)
3. 再失败 → 试 **semantic-rebind**(role · accessible name · advertised actions · stable ancestor fingerprint)
4. 任一步骤 fail-closed,绝不"猜"

**对策**:
- 调 `computer_observe` 获取新观测
- 用新 observationId 重新尝试
- 缩小 `targetHandle` 范围(更具体 role / name)

## 4. COMPUTER_TARGET_REBIND_REQUIRES_CONFIRMATION

**触发条件**:
- 高风险目标(7 类清单)的解析路径越过 exact locator
- 走 native-identifier 或 semantic-rebind

**token 行为**:
- one-use token 自动作废
- 调用方必须 `computer_observe` + `computer_confirm` 重来
- 即使原 grants 不变也要重来

**重要**:**视觉坐标不能作为 targetHandle**,文档明说 "Visual coordinates are not target handles and never authorize sensitive rebinding"。

## 调试 tips

```sh
# 看 DSH 当前 preset 的 approval policy
dsh --profile web --dump-config | grep approval

# 看 Computer Use Bundle 配置
dsh --profile web --dump-config | grep -A 20 computer-use

# macOS 上手动验证 TCC 权限
tccutil reset Accessibility <bundle-id>
tccutil reset ScreenCapture <bundle-id>
```

## 相关链接

- [[../../SKILL.md]] · 主 SKILL.md(L2 节)
- [上游 Status and limitations](https://github.com/Anionex/dsh-computer-use#status-and-limitations)
- [上游 Observation, permissions, and sensitive actions](https://github.com/Anionex/dsh-computer-use#observation-permissions-and-sensitive-actions)