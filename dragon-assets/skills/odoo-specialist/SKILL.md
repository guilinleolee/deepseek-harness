---
license: UNKNOWN
name: odoo-specialist-odoo
version: 1.0.0
description: |
  Use when creating or extending Odoo modules, handling ORM data operations, designing XML views (Grid/Gantt), or implementing OWL components. Odoo 专家技能，用于创建/扩展模块、处理 ORM 数据操作、设计 XML 视图及实现 OWL 组件。
author: 天龙引擎团队
created: 2026-02-26
category: design

triggers:
  - "用户提到「odoo-specialist Odoo 专家」时"
---

# Odoo Specialist (Odoo 专家)

针对 Odoo 19.0 的防御性工程大脑，确保所有代码符合高性能与高安全性基准。

## 🚀 触发准则 (Trigger Guidelines)
**铁律 1：仅在涉及 Odoo 物理文件（.py, .xml, .js, .csv）或架构设计时激活。**
**铁律 2：[社区优先] 在任何代码修改前，必须调用 `/01调研师` 检索 OCA 与 GitHub 现有方案。**

## 🛡️ 防御性工作流 (Defensive Workflow)

### 0. 社区考古 (Community Archaeology)
- **搜寻路径**: `OCA GitHub` -> `Odoo Apps Store` -> `Odoo OCB`。
- **判定逻辑**: 若存在覆盖率 >80% 的开源模块，优先提供安装与配置方案，严禁盲目自研。

### 1. Rationalization Table (合理化陷阱表)
| AI 借口 (Rationalization) | 事实与铁律 (Reality) |
| --- | --- |
| “这次数据量小，循环内查询没关系” | 性能债会累积，严禁任何形式的循环内查询。 |
| “XPath 路径虽然长，但能精确定位” | 绝对路径极其脆弱，必须使用基于属性的相对定位。 |
| “sudo() 只是为了方便测试” | sudo() 是安全漏洞的温床，生产代码必须有明确的权限边界。 |

### 2. Red Flags (红旗警告 - 出现即停止)
- ❌ **语义模糊**：在描述逻辑时使用“大概”、“可能需要”、“通常”等词汇。
- ❌ **跳过步骤**：以“优化”为名省略 `api.depends` 的完整路径检查。
- ❌ **依赖缺失**：修改了其它模块模型但 `depends` 中未声明。

### 3. 性能先行 (ORM Performance)
- **禁止 N+1**: 严禁在循环内调用 `search()`、`browse()` 或触发未缓存的计算字段。
- **强制映射**: 复杂取值必须使用 `mapped()`。
- **细节参考**: [orm_19_0.md](references/orm_best_practices.md)

### 2. 架构约束 (Views & UI)
- **19.0 Grid/Gantt**: 必须核对 XML Schema，确保 `app`、`block` 与 `setting` 层级正确。
- **细节参考**: [views_19_0.md](references/xml_inheritance.md)

### 3. 安全哨位 (Security)
- **拒绝 Public API**: 所有 API 默认受限，必须显式定义权限。
- **细节参考**: [security_19_0.md](references/security.md)

## 🎼 核心指令
- **考古模式**: 调用 `/01investigator` 检查 `__manifest__.py`。
- **审计模式**: 调用 `/06审查师` 检查 SQL 注入与 `sudo()` 滥用。
- **发布模式**: 修改完成后，必须询问用户：“是否需要将更改上传至 GitHub 仓库？”并在确认后调用 `/08发布师` 自动化推送。

---
*业务影响：通过 19.0 防御性加固，消除 90% 的性能抖动与权限旁路风险；通过 GitHub 自动化闭环，确保代码版本资产的安全性。*
