# Odoo 19.0 Security & Audit (安全审计)

## 1. 安全红旗 (Red Flags)
- ❌ 使用 `sudo()` 绕过权限且未附加逻辑说明。
- ❌ 创建 `type="object"` 的按钮方法但未在 `ir.model.access.csv` 中定义写权限。

## 2. 19.0 防御重点
- **Unsafe Public Methods**: 严禁在未经 `auth="user"` 校验的控制器中处理敏感数据。
- **SQL Injection**: 所有动态 SQL 必须使用占位符，严禁字符串拼接。

## 3. 审计核对
- [ ] 所有新模型是否有 `ir.model.access.csv` 记录？
- [ ] 敏感记录规则 (Record Rules) 是否覆盖了 `Multi-company` 场景？
