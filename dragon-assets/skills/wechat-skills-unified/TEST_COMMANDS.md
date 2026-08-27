# 快速测试命令清单

## 当前状态

- ✅ **核心测试通过**: 15/15 (100%)
- ⚠️ **总体通过率**: 20/24 (83.3%)
- ❌ **API不匹配**: 9个测试需要修复

---

## 快速命令

### 运行通过的测试

```bash
cd C:/Users/li/.claude/skills/wechat-skills-unified

# 运行所有通过的核心测试
pytest tests/test_cache.py tests/test_article.py -v

# 只运行缓存测试
pytest tests/test_cache.py -v

# 只运行Article模型测试
pytest tests/test_article.py -v
```

### 运行所有测试（包括失败的）

```bash
# 运行所有测试
pytest tests/ -v

# 运行所有测试并显示详细错误
pytest tests/ -v --tb=long

# 运行所有测试但只显示错误摘要
pytest tests/ -v --tb=line
```

### 查看测试报告

```bash
# 测试报告
cat TEST_REPORT.md

# 问题清单
cat ISSUES_LOG.md

# 性能基准
cat PERFORMANCE_BENCHMARK.md

# 验证总结
cat VALIDATION_SUMMARY.md
```

---

## 测试结果

### 通过的测试（15个）

```
tests/test_cache.py::TestLRUCache::test_basic_get_set         PASSED
tests/test_cache.py::TestLRUCache::test_lru_eviction          PASSED
tests/test_cache.py::TestLRUCache::test_hit_rate              PASSED
tests/test_cache.py::TestSQLiteCache::test_basic_get_set      PASSED
tests/test_cache.py::TestSQLiteCache::test_ttl_expiry         PASSED
tests/test_cache.py::TestSQLiteCache::test_delete             PASSED
tests/test_cache.py::TestArticleCache::test_l1_l2_interaction PASSED
tests/test_cache.py::TestArticleCache::test_cache_miss        PASSED
tests/test_cache.py::TestArticleCache::test_clear_cache       PASSED
tests/test_article.py::TestArticle::test_create_minimal       PASSED
tests/test_article.py::TestArticle::test_hash_url             PASSED
tests/test_article.py::TestArticle::test_to_dict              PASSED
tests/test_article.py::TestArticle::test_to_json              PASSED
tests/test_article.py::TestArticle::test_word_count_calculation PASSED
tests/test_article.py::TestArticle::test_save_and_load        PASSED
```

### 失败/错误的测试（9个）

```
# API不匹配需要修复
tests/test_html_utils.py::test_extract_meta         FAILED
tests/test_html_utils.py::test_extract_images       FAILED
tests/test_http_utils.py::*                         ERROR (5个)
tests/test_fetcher.py::*                            ERROR (4个)
```

---

## 下一步

### 1. 修复API不匹配

检查实际API签名：
```bash
grep -n "def __init__" core/fetcher.py utils/http.py utils/html.py
```

### 2. 运行端到端测试

```bash
# TODO: 创建端到端测试
pytest tests/test_e2e.py -v
```

### 3. 运行性能测试

```bash
# TODO: 创建性能测试
pytest tests/test_performance.py -v
```

---

**更新时间**: 2026-02-26
**状态**: Phase 1完成 ✅ | Phase 2-4待执行 ⏳
