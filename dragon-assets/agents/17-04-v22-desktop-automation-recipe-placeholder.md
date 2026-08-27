---
name: 17-04-v22-recipe-placeholder
description: 阶段 42.6 占位 · 17-04 V2.2 加 recipe 录制回放(借鉴 ghost-os) · 等用户拍板
version: 0.0.0 (placeholder)
integration_stage: 42.6
integration_date: 2026-08-24
status: pending_user_decision
depends_on: user_decision
base_version: 17-04 V2.1(2026-05-08 · 现有)
modified_by: dragon-engine (user老李)
---

# 阶段 42.6 · 17-04 V2.2 recipe 录制回放占位

> **TL;DR**:本文件是阶段 42.6 的**占位标记**。当前 17-04 V2.1 是 `agents/17-04-desktop-automation-engineer.md`(已存在,2026-05-08)。本占位等**用户拍板**"是否升级 V2.2 加 recipe 录制回放"(借鉴 ghost-os)。

---

## 1. 触发条件

- [ ] **用户决策**"17-04 V2.2 是否升级加 recipe 系统"
- 暂**无**外部依赖,可独立实施

---

## 2. 借鉴清单(ghost-os)

| ghost-os 概念 | 17-04 V2.2 借鉴方式 |
|--------------|---------------------|
| `ghost_learn_start` | `[@17-04] 学习:Gmail 发邮件` 任务模式 |
| `ghost_learn_stop` | 录制停止 → 提炼成 JSON recipe |
| `ghost_recipe_save` | 配方保存到天龙 SKILL 库 |
| `ghost_run recipe:xxx params:{}` | 用户说"用 Gmail 发邮件给 sarah@..." 时自动套用配方 |

---

## 3. 阶段 42.6 决策矩阵

详见 [`../skills/dsh-computer-use/docs/stage-42-4-7-roadmap.md`](../skills/dsh-computer-use/docs/stage-42-4-7-roadmap.md) § 阶段 42.6。

**当前建议**:**待用户决策**。这是一个功能增强而非必要升级。建议先跑 42.7(4 层智能路由),然后再决策是否加 recipe。

---

## 4. 当用户拍板后的实跑步骤

```sh
# 1. 备份 V2.1
cp agents/17-04-desktop-automation-engineer.md \
   agents/_archive/17-04-desktop-automation-engineer-V2.1.md

# 2. 创建 V2.2
# 路径: dragon-engine/agents/17-04-desktop-automation-engineer-V2.2.md

# 3. 在 V2.2 加 recipe 子模块
# - recipe format:JSON 或 YAML
# - recipe storage:天龙 SKILL 库
# - recipe invocation:`[@17-04] 用 recipe: gmail-send 给我发邮件给 sarah@company.com`
```

### 4.1 JSON recipe 格式(路径 A · ghost-os 风格)

```json
{
  "name": "gmail-send",
  "params": ["recipient", "subject", "body"],
  "steps": [
    {"action": "click", "target": {"role": "AXButton", "title": "Compose"}},
    {"action": "type", "target": {"role": "AXTextField"}, "text": "{{recipient}}"},
    {"action": "click", "target": {"role": "AXButton", "title": "Send"}}
  ]
}
```

### 4.2 YAML recipe 格式(路径 B · 易编辑)

```yaml
name: gmail-send
params: [recipient, subject, body]
steps:
  - action: click
    target: {role: AXButton, title: Compose}
  - action: type
    target: {role: AXTextField}
    text: "{{recipient}}"
  - action: click
    target: {role: AXButton, title: Send}
```

---

## 5. 关键参考

| 资源 | 路径 |
|------|------|
| 17-04 V2.1(现有) | `dragon-engine/agents/17-04-desktop-automation-engineer.md` |
| ghost-os | https://github.com/ghostwright/ghost-os |
| 阶段 42.4-42.7 决策矩阵 | `dragon-engine/skills/dsh-computer-use/docs/stage-42-4-7-roadmap.md` |

---

## 6. 风险与未决项

1. **17-04 V2.2 升级是产品级大改** — 需稳定 V2.1 再决策
2. **recipe 格式 JSON vs YAML** — 路径 A vs B
3. **recipe 存储位置** — 天龙 SKILL 库 vs 独立目录

---

## 版本信息

- **V0.0.0(占位)**(2026-08-24):天龙侧占位 · 等用户拍板
- **预计 V1.0.0**:用户拍板后落地 JSON/YAML recipe 格式

---

> **下次同步点**:用户拍板"升级 17-04 V2.2" → 启动阶段 42.6 实跑。