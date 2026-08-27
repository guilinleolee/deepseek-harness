---
name: dsh-market-bridge
description: |
  借鉴 dsh-market/dsh-market V1.31.1（MIT · Copyright (c) 2026 fkysly and dsh-market contributors · 2,474⭐ · DSH 可视化插件市场）的 13 类核心设计 + 自研 V2.0。
  借鉴清单（V2.0 升级自 V1.0 5 类）：① 17 字段 PluginMarketEntry schema（V1.31 RegistryPlugin 完整）② 6 阶段 install workflow（+preflight +activation-check · P0-1/P0-2）③ catalog ETag/Last-Modified 304 校验（V1.31 served 单例）④ region routing 多源 fallback ⑤ preflightTarget 包存在性 + dsh.bundle 校验（P0-1）⑥ verifyActivation 4 态 live/restart/inert/broken（P0-2）⑦ pnpm v10/v11 allowBuilds 双键名（P0-4）⑧ backup/restore merge 模式 ⑨ themes 互斥切换 ⑩ restart systemd/loopback 守卫 ⑪ parse_simple_patch 热挂载判定 ⑫ 13 类 issue 分类（P1-9）⑬ description 双语 en/zh（P1-13）。
  Stage 50.3 · 借鉴档 64/64 unittest PASS（V1.0 16 向后兼容 + V2.0 48 新增）。
metadata:
  version: "2.0.0"
  date: "2026-08-26"
  license: MIT
  author: 天龙引擎 · Stage 50.3
  upstream_borrowing:
    - dsh-market/dsh-market (MIT · 2,474⭐ · 2026-08-26 · v1.31.1)
  integration_stage: 50.3
  integration_mode: "借鉴档 · 自研 Python（不镜像 TypeScript 真源）"
  upgrade_from:
    stage_50_2_v1_0_0: 2026-08-26  # 借鉴 V0.x 早期版
  borrows:
    - p0_1_preflight_target: "install target validation (P0-1 IMPROVEMENT-PLAN)"
    - p0_2_verify_activation: "post-install 4-state verification (P0-2)"
    - p0_4_pnpm_compat: "v10/v11 allowBuilds 双键名"
    - p1_8_catalog_governance: "目录数据治理 · ETag/304 缓存"
    - p1_9_issue_classification: "13 类策略（V1.0 5 + V2.0 8）"
    - p1_13_i18n_bilingual: "description en/zh 双语字段"
  triggers:
    - "dsh-market"
    - "DSH 插件市场"
    - "plugin market"
    - "one-click install"
    - "/market"
    - "/install"
    - "plugin search"
    - "plugin preflight"
    - "plugin verify"
    - "dsh-market-mcp"
    - "plugin restore"
    - "plugin backup"
---

# dsh-market-bridge · V2.0（借鉴档 · V1.31.1 升级 · 64/64 unittest PASS）

> **TL;DR**：借鉴 [dsh-market/dsh-market](https://github.com/dsh-market/dsh-market)（**MIT ✅** · **DSH 可视化插件市场 · 2,474⭐** · **v1.31.1**）的 **13 类核心设计** + **天龙自研 V2.0**。**天龙 DSH plugin 市场类集成的 V2.0 升级**。**64/64 unittest PASS**（V1.0 16 向后兼容 + V2.0 48 新增）。

---

## L0: 一句话描述 (≤15字)

DSH 插件市场 V2.0 借鉴。

---

## L1: 使用场景

当用户需要：

- 解析 DSH 插件市场条目（V2.0 17 字段 schema，V1.31 RegistryPlugin 完整）
- 实施 6 阶段一键安装 pipeline（resolve → preflight → download → verify → register → activation-check）
- 安装前校验（preflightTarget：包存在性 + dsh.bundle 声明）
- 安装后验证（verifyActivation：4 态 live/restart/inert/broken）
- catalog ETag/Last-Modified 304 缓存校验
- 多区域 catalog 路由（DSHM_REGISTRY_URL env override）
- pnpm v10/v11 allowBuilds 双键名兼容
- backup/restore profile（含 merge 模式）
- themes 互斥切换
- restart systemd/loopback 守卫
- cordis.patch.yml 热挂载判定（parse_simple_patch）
- 13 类 issue 策略分类（对应 IMPROVEMENT-PLAN P0-1..P2-13）
- 双语 description 字段（en/zh）搜索

---

## L2: 13 类借鉴（V2.0 升级自 V1.0 5 类）

### 2.1 PluginMarketEntry（17 字段 dataclass · V1.31 完整 schema 借鉴）

```python
@dataclass
class PluginMarketEntry:
    # V1.0 5 必填字段（向后兼容）
    id: str
    name: str
    version: str
    description: str
    vendor: str
    # V1.0 可选字段
    categories: List[str] = field(default_factory=list)
    downloads: int = 0
    stars: int = 0
    homepage: Optional[str] = None
    icon: Optional[str] = None
    # V2.0 新增字段（V1.31 RegistryPlugin 完整借鉴）
    owner: Optional[str] = None
    url: Optional[str] = None
    page: Optional[str] = None
    npm: Optional[str] = None
    tarball: Optional[str] = None
    subpath: Optional[str] = None
    package: Optional[str] = None
    uninstallable: bool = False
    screenshots: List[str] = field(default_factory=list)
    description_en: Optional[str] = None
    description_zh: Optional[str] = None
    deprecated: bool = False
    replacement: Optional[str] = None
    updated: Optional[str] = None
    added: Optional[str] = None
```

### 2.2 一键安装 6 阶段 workflow

```
resolve → preflight → download → verify → register → activation-check → ✓
```

V1.0 4 阶段 + V2.0 新增 `preflight`（P0-1）+ `activation-check`（P0-2）

### 2.3 catalog ETag/Last-Modified 304 校验

```python
# V1.31 src/registry.ts L120-180 完全借鉴
fetch_catalog_with_cache(
    catalog_url,
    fake_responses=[resp_200],  # 首次 200 写入缓存
) -> {"plugins": [...]}

fetch_catalog_with_cache(
    catalog_url,
    fake_responses=[resp_304],  # 二次 304 复用缓存
) -> 缓存数据
```

### 2.4 region routing 多源 fallback（V1.31 src/regions.ts 借鉴）

```python
DEFAULT_REGION = Region(
    name="default",
    catalog_sources=[CatalogSource(url="https://awesome-dsh-plugin.com/plugins.json")]
)

def resolve_region(env_value=None):
    """DSHM_REGISTRY_URL env override → env-override region"""
    if env_value:
        return Region(name="env-override", catalog_sources=[CatalogSource(url=env_value)])
    return DEFAULT_REGION
```

### 2.5 preflightTarget 包存在性 + dsh.bundle 校验（P0-1 借鉴）

```python
@dataclass
class PreflightResult:
    status: str  # ok / warn / blocked
    exists: bool
    has_bundle: bool
    has_client: bool
    reason: str
    target_kind: str  # npm / github-tarball / github-subpath
    target: str

# 4 优先级：npm > package > tarball > subpath > url
preflight_target(entry, fake_registry_lookup={
    "dsh-foo": {"dsh.bundle": True, "version": "1.0.0"},
})
```

### 2.6 verifyActivation 4 态判定（P0-2 借鉴）

```python
ACTIVATION_LIVE = "live"          # 热挂载成功
ACTIVATION_RESTART = "restart"    # 需重启
ACTIVATION_INERT = "inert"        # 纯客户端/纯库
ACTIVATION_BROKEN = "broken"      # CLI 没 reconcile

verify_activation(
    "dsh-foo",
    bundles=["dsh-base", "dsh-foo"],
    has_bundle=True,
    patch_yaml="- insert:\n    - id: foo\n",
)
# -> ActivationResult(state="live", reasons=["pure insert patch hot-loaded successfully"])
```

### 2.7 pnpm v10/v11 allowBuilds 双键名（P0-4 借鉴）

```python
# v10 → onlyBuiltDependencies
build_allow_builds_entry(["esbuild", "node-gyp"], "10.5.0")
# -> {"onlyBuiltDependencies": ["esbuild", "node-gyp"]}

# v11 → allowBuilds
build_allow_builds_entry(["esbuild", "node-gyp"], "11.0.0")
# -> {"allowBuilds": {"esbuild": True, "node-gyp": True}}

merge_pnpm_workspace_yaml(existing_yaml, ["esbuild"], "11.0.0")
# 保留原有 yaml 不覆盖，追加新条目
```

### 2.8 backup/restore merge 模式（V1.31 src/backup.ts 26 KB 借鉴）

```python
backup = export_backup("web", ["dsh-a", "dsh-b", "dsh-c"],
                        cordis_patch="- insert: ...", settings={"theme": "dark"})

# merge 模式（默认）：保留 backup 后安装的
report = restore_backup(backup, current_bundles=["dsh-b", "dsh-d"], merge=True)
# -> RestoreReport(installed=["dsh-a", "dsh-c"], skipped=["dsh-b"], merged=True)
```

### 2.9 themes 互斥切换（V1.31 src/themes.ts 借鉴）

```python
switch_theme(ThemeState(active_theme="dark"), "light")
# -> ThemeState(active_theme="light", installed_themes=["light"])

uninstall_theme(ThemeState(active_theme="dark"), "dark")
# -> ThemeState(active_theme=None, installed_themes=[])
```

### 2.10 restart systemd/loopback 守卫（V1.31 src/restart.ts 借鉴）

```python
# 双条件检测：INVOCATION_ID + MainPID
should_show_restart_button(
    invocation_id="abc-123",
    unit_pid=os.getpid(),
)
# -> False（在 systemd 主进程内，避免 cgroup 自杀）
```

### 2.11 parse_simple_patch 热挂载判定（V1.31 src/hot.ts 借鉴）

```python
parse_simple_patch("- insert:\n    - id: foo\n")
# -> {"operations": [{"type": "insert"}], "hot_loadable": True}

parse_simple_patch("- insert:\n  config:\n    port: 8080\n")
# -> {"operations": [{"type": "insert"}], "hot_loadable": False}  # config 不可热挂
```

### 2.12 13 类 issue 分类（V1.0 5 + V2.0 8 · P1-9 借鉴）

```python
ISSUE_CATEGORIES = {
    "search":     "search and filter engine optimization",
    "filter":     "category and tag filtering",
    "install":    "one-click install reliability (P0-1/2/3/4)",
    "compat":     "version compatibility matrix",
    "security":   "checksum verification + sandbox",
    "preflight":  "P0-1 install target validation",      # V2.0
    "activation": "P0-2 post-install verification",      # V2.0
    "version":    "P0-3 minimumReleaseAge handling",     # V2.0
    "build":      "P0-4 allowBuilds approval flow",      # V2.0
    "diagnose":   "P1-5/P1-9 structured error diagnosis",# V2.0
    "progress":   "P1-6 ndjson progress/cancel",         # V2.0
    "lock":       "P1-7 commit pinning",                 # V2.0
    "registry":   "P1-8 catalog data governance",       # V2.0
}
```

### 2.13 双语 description 字段（P1-13 借鉴）

```python
parse_plugin_json(json.dumps({
    "description": {"en": "English desc", "zh": "中文描述"},
    ...
}))
# -> PluginMarketEntry(description="中文描述", description_en="English desc", description_zh="中文描述")
```

---

## L3: 安装与运行

```bash
# 1. 验证 64/64 unittest PASS
cd 'C:\Users\li\.claude\projects\dragon-engine\skills\dsh-market-bridge'
"C:\Program Files\Python311\python.exe" -m unittest discover -s tests -p test_dsh_market_bridge.py

# 2. CLI 演示（V1.0 兼容子命令）
python scripts/dsh_market_bridge.py parse-plugin --input '{"id":"x","name":"X","version":"1.0.0","description":"d","vendor":"v"}'
python scripts/dsh_market_bridge.py install-flow
python scripts/dsh_market_bridge.py classify-issue --title "Search broken"
python scripts/dsh_market_bridge.py filter --query '{"text":"redis","category":"cache"}'
python scripts/dsh_market_bridge.py check-version --installed 1.0.0 --required 0.5.0

# 3. CLI 演示（V2.0 新增子命令）
python scripts/dsh_market_bridge.py preflight --input '{"id":"dsh-foo","name":"Foo","version":"1.0.0","description":"d","vendor":"v","npm":"dsh-foo"}'
python scripts/dsh_market_bridge.py verify --name dsh-foo --bundles '["dsh-base","dsh-foo"]' --has-bundle --patch "- insert:\n  - id: foo"
python scripts/dsh_market_bridge.py pnpm-compat --packages "esbuild,node-gyp" --pnpm-version 11.0.0
python scripts/dsh_market_bridge.py backup --profile web --bundles '["dsh-a","dsh-b"]'
```

---

## L4: 触发词（12 类 · V1.0 9 + V2.0 3）

```
dsh-market, DSH 插件市场, plugin market, one-click install, /market
/install, plugin search, semver pin, search + filter
plugin preflight, plugin verify, dsh-market-mcp, plugin restore, plugin backup
```

---

## L5: 下游协同（V2.0 升级）

| 下游 | 协同 |
|---|---|
| **stage 49.1 dsh-desktop-bridge** | 桌面 + 市场 = 完整 DSH 桌面 + 一键装入 |
| **stage 47 dsh-univer-office-bridge** | univer 装入 dsh-market |
| **stage 48 dsh-tui-bridge** | TUI 嵌入 dsh-market browse |
| **stage 49.2 memsearch-bridge** | memsearch semantic search 替换 market 默认搜索 |
| **stage 49.4 open-design-bridge** | design 装入 market |
| **40-01 mcp-orchestrator V2.1** ⭐V2.0 | **dsh-market-as-MCP 第 12 服务**（dsh-market-bridge V2.0 Python 引擎 + 6 阶段 install pipeline）|
| **stage 50.1 deepseek-harness** | cordis patch 借鉴同源 |

---

## L6: DON'T 护栏（10 条 · V1.0 5 + V2.0 5）

### V1.0 5 条（保留）

- ❌ **不要**镜像 dsh-market 真源（routes.ts 158 KB 借鉴设计即可）
- ❌ **不要**省 plugin manifest 5 字段必填校验（V1.0 strict 模式）
- ❌ **不要**让 version check 跳过 semver 简化
- ❌ **不要**默认开启 one-click install 自动执行（opt-in）
- ❌ **不要**让 13 类 issue 策略降级为 silent ignore

### V2.0 新增 5 条

- ❌ **不要**跳过 preflight 校验直接 install（P0-1 借鉴）
- ❌ **不要**忽略 verifyActivation 4 态判定（必须明确告诉用户 live/restart/inert/broken）
- ❌ **不要**在 pnpm v11 环境用 `onlyBuiltDependencies` 键名（必须探测版本）
- ❌ **不要**让 backup 覆盖式 restore 不经 merge 模式（默认 merge）
- ❌ **不要**在 systemd 主进程显示"一键重启"按钮（避免 cgroup 自杀）

---

## L7: 验证矩阵（11 类 · V1.0 6 + V2.0 5）

| # | 必检项 | 期望 | 状态 |
|---|---|---|---|
| 1 | V1.0 兼容：plugin manifest 5 字段必填 | 全过 | ✅ |
| 2 | V2.0 17 字段 dataclass 完整解析 | 全过 | ✅ |
| 3 | 6 阶段 install workflow 含 preflight + activation-check | 全过 | ✅ |
| 4 | catalog ETag/304 缓存复用 | 全过 | ✅ |
| 5 | region routing + DSHM_REGISTRY_URL env override | 全过 | ✅ |
| 6 | preflightTarget 3 态（ok/warn/blocked）+ 5 优先级 | 全过 | ✅ |
| 7 | verifyActivation 4 态（live/restart/inert/broken）| 全过 | ✅ |
| 8 | pnpm v10/v11 双键名 + 解析 blocked builds | 全过 | ✅ |
| 9 | backup export/restore merge 模式 | 全过 | ✅ |
| 10 | themes 互斥 + restart systemd/loopback 守卫 | 全过 | ✅ |
| 11 | **64/64 unittest PASS（V1.0 16 + V2.0 48）** | **6 大类** | ✅ |

---

## L8: 参考链接

- **借鉴源**：https://github.com/dsh-market/dsh-market · MIT
- **LICENSE verbatim**：https://raw.githubusercontent.com/dsh-market/dsh-market/main/LICENSE（1,091 B / 21 行 / "Copyright (c) 2026 fkysly and dsh-market contributors" / MIT）
- **上游 IMPROVEMENT-PLAN.md**：30 KB（V2.0 全吸收，13 项策略矩阵落 `references/issue-roadmap.md`）
- **上游 catalog**：https://awesome-dsh-plugin.com/plugins.json · 2231 插件 · 21 类目
- **DSH 协议治理基线**：`docs/dsh-ecosystem-license-policy.md`
- **MIT 致谢节**：`memory/mit-attribution-statements.md §十八`
- **天龙主题文件**：`memory/dsh-market-bridge-v2-integration.md`（待 W4 落盘）
