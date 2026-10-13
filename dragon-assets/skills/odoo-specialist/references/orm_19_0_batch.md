# Odoo 19.0 ORM Batch & Prefetching Logic

## 核心原则
- **Batch Processing**: 始终使用 Recordset 的集合操作，严禁在循环中进行单条记录操作。
- **Prefetching**: Odoo 19.0 增强了上下文感知的预取。在访问字段前，通过 `prefetch_ids` 显式或隐式加载。

## 关键指令
- `search_fetch(domain, fields, limit=None)`: 19.0 推荐写法，一次性完成搜索与指定字段加载。
- `browse(ids).with_prefetch(prefetch_ids)`: 手动注入预取上下文。

## 防御性清单
1. [ ] 循环外执行 `search`。
2. [ ] 避免在 `computed fields` 中调用 `search`。
3. [ ] 使用 `filtered_domain` 代替 Python 层面的 `if` 过滤。
