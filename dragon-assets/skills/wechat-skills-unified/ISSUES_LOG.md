# 微信公众号SKILL统一重构 - 问题清单

## 报告信息

- **执行者**: 04验证师（Validator）
- **创建时间**: 2026-02-26
- **项目状态**: 🟡 需要修复

---

## 问题统计

| 严重程度 | 数量 | 状态 |
|---------|------|------|
| **P0** | 2 | ✅ 已修复 |
| **P1** | 3 | ⚠️ 待修复 |
| **P2** | 5 | 📋 待办 |

---

## P0级问题（已修复）

### Bug #1: SQL多语句执行失败 ✅

**ID**: BUG-001
**状态**: ✅ 已修复
**严重程度**: P0 - 阻塞所有SQLite测试

**描述**:
SQLiteCache初始化时尝试一次执行多个CREATE INDEX语句，但Python sqlite3模块的`execute()`默认只支持单语句。

**错误信息**:
```
sqlite3.Warning: You can only execute one statement at a time.
```

**复现步骤**:
1. 创建SQLiteCache实例
2. 触发`_init_db()`方法
3. 执行`conn.execute(self.CREATE_INDEX_SQL)`
4. 抛出Warning

**根本原因**:
```python
# core/cache.py:162
CREATE_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_fetch_time ON articles(fetch_time);
CREATE INDEX IF NOT EXISTS idx_source ON articles(source);
"""
conn.execute(self.CREATE_INDEX_SQL)  # ❌ 只支持单语句
```

**修复方案**:
```python
# 修复后
CREATE_INDEX_SQL_LIST = [
    "CREATE INDEX IF NOT EXISTS idx_fetch_time ON articles(fetch_time);",
    "CREATE INDEX IF NOT EXISTS idx_source ON articles(source);"
]
for index_sql in self.CREATE_INDEX_SQL_LIST:
    conn.execute(index_sql)
```

**验证**:
```bash
pytest tests/test_cache.py::TestSQLiteCache -v
# 结果: 3/3 通过 ✅
```

**影响范围**:
- core/cache.py
- 所有SQLite相关测试

**修复时间**: 10分钟
**修复者**: 04验证师

---

### Bug #2: 测试用例url_hash不匹配 ✅

**ID**: BUG-002
**状态**: ✅ 已修复
**严重程度**: P1 - 测试缺陷

**描述**:
测试用例手动指定了错误的`url_hash`值，导致缓存查询失败。

**错误信息**:
```
AssertionError: assert None is not None
```

**复现步骤**:
1. 创建Article对象，手动指定`url_hash="hash"`
2. 写入缓存
3. 尝试使用URL获取缓存
4. 断言失败：result为None

**根本原因**:
```python
# 测试代码
article = Article(
    url="https://example.com/test",
    url_hash="hash",  # ❌ 手动指定
    ...
)

# ArticleCache.get()计算哈希
url_hash = Article._hash_url(url)  # 返回SHA256
# "hash" != SHA256("https://example.com/test")
```

**修复方案**:
```python
# 修复后：不指定url_hash，让系统自动生成
article = Article(
    url="https://example.com/test",
    url_hash="",  # ✅ 空字符串触发自动生成
    ...
)
```

**验证**:
```bash
pytest tests/test_cache.py::TestArticleCache::test_l1_l2_interaction -v
# 结果: 通过 ✅
```

**影响范围**:
- tests/test_cache.py

**修复时间**: 5分钟
**修复者**: 04验证师

---

### Bug #3: 相对导入失败 ✅

**ID**: BUG-003
**状态**: ✅ 已修复
**严重程度**: P0 - 阻塞所有测试

**描述**:
pytest无法识别项目为包，导致相对导入失败。

**错误信息**:
```
ImportError: attempted relative import with no known parent package
```

**根本原因**:
1. 项目目录名包含连字符（`wechat-skills-unified`）
2. `__init__.py`使用相对导入（`from .core import ...`）
3. pytest无法识别为包结构

**修复方案**:
```python
# __init__.py
try:
    # 尝试相对导入（安装后）
    from .core import ...
except ImportError:
    # 回退到绝对导入（测试/开发环境）
    from core import ...
```

**验证**:
```bash
pytest tests/ -v
# 结果: 可以正常导入 ✅
```

**影响范围**:
- __init__.py
- 所有测试

**修复时间**: 15分钟
**修复者**: 04验证师

---

## P1级问题（待修复）

### Issue #1: HTMLParser API不匹配 ⚠️

**ID**: ISSUE-001
**状态**: ❌ 待修复
**严重程度**: P1

**描述**:
测试期望的HTMLParser方法在实际代码中不存在。

**缺失方法**:
- `extract_meta()` - 元数据提取
- `extract_images()` - 图片提取

**影响**:
- 2个测试失败
- HTML解析功能验证不完整

**建议**:
1. 检查`utils/html.py`的实际实现
2. 调整测试以匹配实际API
3. 或在HTMLParser中添加缺失的方法

**估计修复时间**: 30分钟

---

### Issue #2: HTTPClient API不匹配 ⚠️

**ID**: ISSUE-002
**状态**: ❌ 待修复
**严重程度**: P1

**描述**:
测试期望的HTTPClient构造函数签名与实际不匹配。

**问题**:
```python
# 测试假设
HTTPClient(timeout=10, retry_times=2)

# 实际签名（需要确认）
HTTPClient(user_agents, timeout=10, retry_times=2)
```

**影响**:
- 5个测试错误
- HTTP客户端功能验证缺失

**建议**:
1. 确认HTTPClient的实际构造函数签名
2. 更新测试以匹配实际API
3. 或添加默认的user_agents参数

**估计修复时间**: 30分钟

---

### Issue #3: UnifiedFetcher API不匹配 ⚠️

**ID**: ISSUE-003
**状态**: ❌ 待修复
**严重程度**: P1

**描述**:
测试期望的UnifiedFetcher构造函数签名与实际不匹配。

**问题**:
```python
# 测试假设
UnifiedFetcher(cache=cache)

# 实际签名（需要确认）
```

**影响**:
- 4个测试错误
- 核心获取功能验证缺失

**建议**:
1. 检查`core/fetcher.py`中UnifiedFetcher的实际实现
2. 更新测试以匹配实际API

**估计修复时间**: 30分钟

---

## P2级问题（待办）

### Task #1: 端到端测试 📋

**ID**: TASK-001
**状态**: 📋 待办
**优先级**: P0

**描述**:
需要测试完整的fetch_article()流程。

**测试场景**:
1. 真实URL获取
2. 缓存命中/未命中
3. 降级机制
4. 批量获取

**估计时间**: 3-4小时

---

### Task #2: 性能基准测试 📋

**ID**: TASK-002
**状态**: 📋 待办
**优先级**: P1

**描述**:
需要量化性能指标。

**测试项**:
- 缓存命中率（目标≥85%）
- P50/P95/P99延迟
- 并发性能

**估计时间**: 2-3小时

---

### Task #3: 压力测试 📋

**ID**: TASK-003
**状态**: 📋 待办
**优先级**: P1

**描述**:
需要测试极端情况。

**测试场景**:
- 空URL、超长URL、特殊字符
- 网络超时、连接失败
- 并发压力（3/10/100）

**估计时间**: 2-3小时

---

### Task #4: 测试覆盖率提升 📋

**ID**: TASK-004
**状态**: 📋 待办
**优先级**: P0

**描述**:
当前覆盖率约35%，目标≥80%。

**未测试模块**:
- core/fallback.py
- core/config.py
- core/fetcher.py
- utils/http.py
- utils/html.py

**估计时间**: 4-5小时

---

### Task #5: 向后兼容验证 📋

**ID**: TASK-005
**状态**: 📋 待办
**优先级**: P1

**描述**:
需要验证旧版API兼容性。

**验证项**:
- 旧版Fetcher API
- 旧版Aggregator API
- 配置文件兼容

**估计时间**: 2小时

---

## 附录

### A. 修复优先级

```
P0 (立即修复):
├── Issue #3: UnifiedFetcher API不匹配
├── Issue #2: HTTPClient API不匹配
└── Task #4: 测试覆盖率提升

P1 (本周完成):
├── Issue #1: HTMLParser API不匹配
├── Task #1: 端到端测试
├── Task #2: 性能基准测试
├── Task #3: 压力测试
└── Task #5: 向后兼容验证
```

### B. 快速修复脚本

```bash
# 1. 检查实际API签名
grep -n "def __init__" core/fetcher.py utils/http.py

# 2. 更新测试文件
# 手动编辑测试以匹配实际API

# 3. 重新运行测试
pytest tests/ -v
```

---

**问题清单生成时间**: 2026-02-26
**验证师签名**: 04验证师（Validator）
**下一步**: 修复P1级API不匹配问题
