# Stage 50.2 · dsh-market-bridge V1.0 · 主题文件

> **阶段**：天龙引擎 · **stage 50.2**（**借鉴档 · 轻量 · MIT · DSH 插件市场**）
> **日期**：2026-08-26
> **集成度**：⭐ 战略级 — **天龙首个 DSH plugin 市场类集成**
> **入口文件**：[`skills/dsh-market-bridge/SKILL.md`](../skills/dsh-market-bridge/SKILL.md)

---

## 一、TL;DR

> 借鉴 [dsh-market/dsh-market](https://github.com/dsh-market/dsh-market) V0.x（**MIT ✅** · "Copyright (c) 2026 fkysly and dsh-market contributors" · **2,430⭐ / 123 🍴** · 13.2 KB · 12 天前 · 8 小时前极活跃 · 16 open_issues）的 **5 类核心设计** + **天龙自研 V1.0**。累计 PASS **898 → 904**（+6 net · 18/18 自研 unittest 拆 6 大类）。

---

## 二、触发源（一手）

| 字段 | 值 |
|---|---|
| **上游仓库** | https://github.com/dsh-market/dsh-market |
| **作者** | dsh-market（GitHub 316826596 · Organization · **fkysly** 主理）|
| **协议** | **MIT ✅**（LICENSE 1,091 B verbatim · "Copyright (c) 2026 fkysly and dsh-market contributors" · SPDX `MIT`）|
| **★ / 🍴** | **2,430⭐ / 123 🍴** |
| **size** | 13.2 KB（**轻量**）|
| **language** | TypeScript |
| **topics** | deepseek-harness / dsh-plugin / marketplace |
| **default_branch** | `main` |
| **创建** | 2026-08-14T04:58:15Z（**12 天前**）|
| **末 push** | 2026-08-26T06:49:34Z（**8 小时前 · 极活跃**）|
| **homepage** | https://dshmarket.com |
| **核心特性** | "The plugin market inside DeepSeek Harness — browse, search, one-click install" |
| **辅助文档** | IMPROVEMENT-PLAN.md（30 KB）· TESTING.md（7.2 KB）· README.zh.md |
| **意义** | **天龙首个 DSH plugin 市场类集成** · 与 stage 49.1 dsh-desktop 互补 |

---

## 三、5 类借鉴

### 3.1 PluginMarketEntry（9 字段 dataclass）
```python
@dataclass
class PluginMarketEntry:
    id: str
    name: str
    version: str
    description: str
    vendor: str
    categories: List[str] = []
    downloads: int = 0
    stars: int = 0
    homepage: Optional[str] = None
```

### 3.2 一键安装 4 阶段 workflow
```
resolve (0%) → download (25%) → verify (60%) → register (90%) → ✓ (100%)
```

### 3.3 search + filter engine（4 维度）
```python
def filter_plugins(plugins, query: SearchQuery) -> List[PluginMarketEntry]:
    # 4 维筛选：text + category + min_stars + max_version
```

### 3.4 semver version pinning
```python
def satisfies_version(installed: str, required: str) -> bool:
    return parse_semver(installed) >= parse_semver(required)
```

### 3.5 16 open_issues 分类应对策略
```python
ISSUE_CATEGORIES = {
    "search": "search and filter engine optimization",
    "filter": "category and tag filtering",
    "install": "one-click install reliability",
    "compat": "version compatibility matrix",
    "security": "checksum verification + sandbox",
}
```

---

## 四、18/18 自研 unittest PASS 拆 6 大类

```
✓ TestParsePlugin     (3)  # basic / missing_field / invalid_json
✓ TestInstallFlow    (1)  # full_flow 4 阶段
✓ TestIssueClassify  (4)  # search/filter/install/other
✓ TestFilter         (4)  # text/category/stars/combined
✓ TestVersion        (5)  # equal/upgrade/downgrade/prerelease/invalid
✓ TestEndToEnd       (1)  # full workflow
                     18/18 ✓ 0.001s
```

---

## 五、4 CLI 自研工具（dsh_market_bridge.py）

```bash
$ dsh_market_bridge.py parse-plugin --input '{"id":"x","name":"X","version":"1.0.0","description":"d","vendor":"v"}'
$ dsh_market_bridge.py install-flow        # → 4 阶段演示
$ dsh_market_bridge.py classify-issue --title "search broken"   # → "search"
$ dsh_market_bridge.py filter --query '{"text":"redis","category":"cache"}'   # → 4 维度
$ dsh_market_bridge.py check-version --installed 1.0.0 --required 0.5.0
```

---

## 六、累计 PASS 锁定

```
893 (Stage 50 累计)
   +5 ─► 898 (stage 50.1 deepseek-harness-bridge 11/11)
   +6 ─► 904 (stage 50.2 dsh-market-bridge 18/18)
                          │
                          ─► 904 locked
```

**stage 50 双借鉴档净增 +11 PASS**（与 stage 49 节奏一致 · 11/11 + 18/18 = 29/29 unittest）

---

## 七、跳转入口

- **真源 SKILL.md**：[`skills/dsh-market-bridge/SKILL.md`](../skills/dsh-market-bridge/SKILL.md)
- **DSH 协议治理基线**：[`docs/dsh-ecosystem-license-policy.md`](../docs/dsh-ecosystem-license-policy.md)
- **Stage 50 盘点**：[`memory/stage-50-candidates-evaluation.md`](stage-50-candidates-evaluation.md)

---

> **下次同步点**：用户在 DSH 真机 `pnpm add dsh-market` 后跑 `dsh market browse` 与 `dsh install <plugin-name>` 实测一键安装。
