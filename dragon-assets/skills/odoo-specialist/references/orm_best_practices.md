# Odoo 19.0 ORM & Performance (防御性参考)

## 1. 性能红旗 (Red Flags)
- ❌ 在 `for record in self` 循环内执行数据库查询。
- ❌ 使用 `len(recordset)` 代替 `search_count()`。
- ❌ 忽略 `api.depends` 导致计算字段缓存不一致。

## 2. 19.0 关键变动
- **Prefetching**: 19.0 增强了自动预取，手动 `with_prefetch()` 的优先级需谨慎处理。
- **Batching**: 复杂计算强制使用 `env.cr.execute` 的场景需配合 `env.cache.invalidate()`。

## 3. 防御性清单
- [ ] 是否所有计算字段都有对应的 `api.depends`？
- [ ] 循环体是否完全“只读”缓存数据？
- [ ] 大规模删除是否使用了 `unlink()` 的批量模式？
