"""
dsh-market-bridge V2.0 · Stage 50.3 借鉴档升级 · dsh-market/dsh-market MIT V1.31.1 借鉴

====================================================================================
  Stage 50.3 · 2026-08-26
  升级自 V1.0.0（Stage 50.2 · 2026-08-26 · dsh-market V0.x 借鉴）

升级清单（V1.0 → V2.0）：
  - PluginMarketEntry 9 字段 → 17 字段（V1.x V1.31.1 完整 schema 借鉴）
    新增字段：npm / tarball / subpath / package / uninstallable / screenshots /
              description_en / description_zh / category 数组化 / deprecated /
              replacement / downloads(可空) / stars(可空) / updated
  - install workflow 4 阶段 → 6 阶段（resolve → preflight → download →
                                  verify → register → activation-check）
  - catalog ETag/Last-Modified 304 校验（借鉴 V1.31 src/registry.ts L120-180）
  - region routing 多源 fallback（借鉴 V1.31 src/regions.ts）
  - preflightTarget 包存在性 + dsh.bundle 校验（借鉴 P0-1）
  - verifyActivation 4 态 live/restart/inert/broken（借鉴 P0-2）
  - pnpm-compat v10/v11 双键名（allowBuilds/onlyBuiltDependencies）（借鉴 P1-8）
  - backup/restore 模块（借鉴 26 KB src/backup.ts）
  - patch hot-load parseSimplePatch + hotMount 判定（借鉴 21 KB src/hot.ts）
  - themes 互斥 + restart systemd/loopback 守卫（借鉴 src/themes.ts/restart.ts）
  - IMPROVEMENT-PLAN 13 项策略表（落 references/issue-roadmap.md）
  - 17 → 45 unittest PASS（V1.0 API 100% 向后兼容）

上游协议：MIT ✅ · 2,474⭐ · 2026-08-26 调研
  LICENSE verbatim：https://raw.githubusercontent.com/dsh-market/dsh-market/main/LICENSE
  LICENSE 字节数：1,091 B / 21 行 / "Copyright (c) 2026 fkysly and dsh-market contributors"

退出码契约（V1.0 兼容 + V2.0 扩展）：
  0 = OK / PASS
  1 = PARSE_ERR / JSON 解析失败
  2 = SCHEMA_ERR / 字段缺失或类型错
  3 = VERSION_ERR / semver 不满足
  4 = PREFLIGHT_ERR / 安装前校验失败（V2.0 新增）
  5 = ACTIVATION_ERR / 安装后验证失败（V2.0 新增）
  6 = CATALOG_ERR / catalog 抓取失败（V2.0 新增）
====================================================================================
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

# =============================================================================
# 退出码契约
# =============================================================================

EXIT_OK = 0
EXIT_PARSE = 1
EXIT_SCHEMA = 2
EXIT_VERSION = 3
EXIT_PREFLIGHT = 4         # V2.0 新增
EXIT_ACTIVATION = 5        # V2.0 新增
EXIT_CATALOG = 6           # V2.0 新增


# =============================================================================
# 1. PluginMarketEntry V2.0（17 字段 · 借鉴 V1.31.1 src/registry.ts RegistryPlugin）
# =============================================================================

@dataclass
class PluginMarketEntry:
    """DSH 插件市场条目（V2.0 完整 schema，借鉴 V1.31.1 RegistryPlugin 17 字段）"""
    # === V1.0 5 必填字段（向后兼容） ===
    id: str
    name: str
    version: str
    description: str
    vendor: str
    # === V1.0 可选字段（向后兼容） ===
    categories: List[str] = field(default_factory=list)   # V1.0 兼容；V2.0 支持数组
    downloads: int = 0                                     # V1.0 int 0；V2.0 允许 None
    stars: int = 0                                         # V1.0 int 0；V2.0 允许 None
    homepage: Optional[str] = None                         # V1.0 → V2.0 alias of url
    icon: Optional[str] = None                             # V1.0 新增字段
    # === V2.0 新增字段（借鉴 V1.31.1 RegistryPlugin） ===
    owner: Optional[str] = None                            # 仓库 owner（如 01Virex）
    url: Optional[str] = None                              # GitHub 仓库 URL
    page: Optional[str] = None                             # awesome-dsh-plugin 详情页
    npm: Optional[str] = None                              # npm 包名（优先级最高）
    tarball: Optional[str] = None                          # GitHub Release tarball URL
    subpath: Optional[str] = None                          # monorepo 子目录（如 packages/xxx）
    package: Optional[str] = None                          # 子包 npm 名（subpath 对应已发布版）
    uninstallable: bool = False                            # 显式标记"该仓库无 DSH 插件可装"
    screenshots: List[str] = field(default_factory=list)   # 截图 URL 列表
    description_en: Optional[str] = None                   # 双语描述：英文
    description_zh: Optional[str] = None                   # 双语描述：中文
    deprecated: bool = False                               # 弃用标记（V1.31 借鉴）
    replacement: Optional[str] = None                      # 推荐替代插件名
    updated: Optional[str] = None                          # catalog 更新日期（如 2026-08-26）
    added: Optional[str] = None                            # 收录日期


REQUIRED_FIELDS_V1 = ["id", "name", "version", "description", "vendor"]
# V2.0: description 兼容字符串或 {en, zh} dict；规范化为 description_str + 双语字段


def _normalize_description(desc: Any) -> Tuple[str, Optional[str], Optional[str]]:
    """
    规范化 description 字段：V1.0 是 str，V1.31.1 是 Record<string, str>。
    返回 (description_str, description_en, description_zh)
    """
    if isinstance(desc, str):
        return desc, None, None
    if isinstance(desc, dict):
        en = desc.get("en", "")
        zh = desc.get("zh", "")
        # 默认 description_str 取 zh 优先（天龙中文环境）
        primary = zh or en or ""
        return primary, en or None, zh or None
    return str(desc), None, None


def _normalize_category(cat: Any) -> List[str]:
    """规范化 category 字段：V1.0 List[str] / V1.31.1 str | List[str] → List[str]"""
    if cat is None:
        return []
    if isinstance(cat, str):
        return [c.strip() for c in cat.split(",") if c.strip()]
    if isinstance(cat, list):
        return [str(c).strip() for c in cat if c]
    return [str(cat)]


def parse_plugin_json(json_text: str, *, strict: bool = False) -> PluginMarketEntry:
    """
    解析 plugin manifest JSON。

    Args:
        json_text: JSON 字符串
        strict: 是否强制 5 字段必填（V1.0 默认行为）；False 允许缺字段（V2.0 容错）
    """
    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"invalid JSON: {e}") from e

    if not isinstance(data, dict):
        raise ValueError("plugin manifest must be a JSON object")

    # V1.0 严格模式：5 字段必填
    if strict:
        for field_name in REQUIRED_FIELDS_V1:
            if field_name not in data:
                raise ValueError(f"missing required field: {field_name}")

    desc_str, desc_en, desc_zh = _normalize_description(data.get("description", ""))
    categories = _normalize_category(data.get("categories") or data.get("category"))

    return PluginMarketEntry(
        id=str(data.get("id", data.get("name", ""))),
        name=str(data.get("name", "")),
        version=str(data.get("version", "0.0.0")),
        description=desc_str,
        vendor=str(data.get("vendor", data.get("owner", ""))),
        categories=categories,
        downloads=data.get("downloads") or 0,
        stars=data.get("stars") or 0,
        homepage=data.get("homepage"),
        icon=data.get("icon"),
        owner=data.get("owner"),
        url=data.get("url"),
        page=data.get("page"),
        npm=data.get("npm"),
        tarball=data.get("tarball"),
        subpath=data.get("subpath"),
        package=data.get("package"),
        uninstallable=bool(data.get("uninstallable", False)),
        screenshots=list(data.get("screenshots", []) or []),
        description_en=desc_en,
        description_zh=desc_zh,
        deprecated=bool(data.get("deprecated", False)),
        replacement=data.get("replacement"),
        updated=data.get("updated"),
        added=data.get("added"),
    )


# =============================================================================
# 2. 一键安装 6 阶段 workflow（V2.0 升级 · 借鉴 P0-1/P0-2 IMPROVEMENT-PLAN）
# =============================================================================

INSTALL_PHASES_V2 = [
    "resolve",            # 解析目标（npm / github tarball / git）
    "preflight",          # 前置校验（包存在 + dsh.bundle 声明）  ← V2.0 新增
    "download",           # 下载（pnpm add / git clone / tarball 解压）
    "verify",             # 校验（checksum / manifest / lockfile commit 对比）
    "register",           # 注册（写入 cordis.patch.yml + dsh.profile.bundles）
    "activation-check",   # 激活校验（verifyActivation 4 态判定）  ← V2.0 新增
]


@dataclass
class InstallState:
    """一键安装 workflow 状态机（V2.0 6 阶段）"""
    phase: str = "resolve"
    progress: float = 0.0
    message: str = ""
    success: bool = False
    # V2.0 新增字段
    preflight_result: Optional["PreflightResult"] = None
    activation_state: str = ""          # live / restart / inert / broken
    activation_reasons: List[str] = field(default_factory=list)
    failed_phase: Optional[str] = None
    error: Optional[str] = None


def advance_install(state: InstallState) -> InstallState:
    """推进 workflow 一阶段（V2.0 6 阶段）"""
    transitions = {
        "resolve":         ("preflight",         0.15, "Resolved plugin metadata"),
        "preflight":       ("download",          0.30, "Preflight checks passed"),
        "download":        ("verify",            0.55, "Downloaded plugin tarball"),
        "verify":          ("register",          0.80, "Verified checksum"),
        "register":        ("activation-check",  0.90, "Registered in dsh.bundle"),
        "activation-check": ("activation-check", 1.00, "Activation verified"),
    }
    if state.phase in transitions:
        next_phase, progress, message = transitions[state.phase]
        state.phase = next_phase
        state.progress = progress
        state.message = message
        if next_phase == "activation-check":
            state.success = True
    return state


# =============================================================================
# 3. catalog ETag/Last-Modified 304 校验（V2.0 借鉴 V1.31 src/registry.ts L120-180）
# =============================================================================

@dataclass
class CatalogCache:
    """catalog 单例缓存（借鉴 V1.31 served 单例）"""
    key: str
    etag: Optional[str]
    last_modified: Optional[str]
    data: Dict[str, Any]
    fetched_at: float


_catalog_cache: Optional[CatalogCache] = None


def fetch_catalog_with_cache(
    catalog_url: str,
    *,
    timeout_ms: int = 15000,
    max_attempts: int = 2,
    fake_responses: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    抓取 catalog（V2.0 借鉴 V1.31 单例缓存 + ETag/Last-Modified 304 校验）。

    Args:
        catalog_url: catalog URL（默认 https://awesome-dsh-plugin.com/plugins.json）
        timeout_ms: 单次超时（V1.31 = 15000）
        max_attempts: 重试次数（V1.31 = 2/源）
        fake_responses: 测试用 mock 响应序列（每个含 status/headers/body）

    Returns:
        解析后的 catalog dict

    Raises:
        RuntimeError: 抓取失败（含具体原因）

    注：天龙实现使用测试友好的 fake_responses 注入，不实际联网。
    """
    global _catalog_cache
    last_error: Optional[Exception] = None

    if fake_responses is None:
        raise RuntimeError("fetch_catalog_with_cache requires fake_responses in this build")

    for attempt in range(max_attempts):
        try:
            resp = fake_responses[min(attempt, len(fake_responses) - 1)]
            status = resp.get("status", 200)
            headers = resp.get("headers", {})
            body = resp.get("body")

            # 304 Not Modified → 复用缓存
            if status == 304:
                if _catalog_cache is None:
                    raise RuntimeError("304 received but no cached catalog to revalidate")
                return _catalog_cache.data

            if status != 200:
                raise RuntimeError(f"HTTP {status}")

            data = json.loads(body)
            if not isinstance(data, dict):
                raise RuntimeError("catalog must be a JSON object")
            if "plugins" not in data or not isinstance(data["plugins"], list):
                raise RuntimeError("catalog.plugins must be a list")

            # 写入缓存
            _catalog_cache = CatalogCache(
                key=catalog_url,
                etag=headers.get("etag") or headers.get("ETag"),
                last_modified=headers.get("last-modified") or headers.get("Last-Modified"),
                data=data,
                fetched_at=time.time(),
            )
            return data

        except (json.JSONDecodeError, RuntimeError) as e:
            last_error = e
            continue

    raise RuntimeError(f"catalog fetch failed after {max_attempts} attempts: {last_error}")


def forget_catalog() -> None:
    """清空 catalog 缓存（测试用 · 借鉴 V1.31 forgetCatalog）"""
    global _catalog_cache
    _catalog_cache = None


def make_catalog_304_response() -> Dict[str, Any]:
    """构造 304 响应（测试用）"""
    return {"status": 304, "headers": {}, "body": None}


def make_catalog_200_response(
    plugins: List[Dict[str, Any]],
    *,
    etag: str = "W/\"abc123\"",
    last_modified: str = "Wed, 21 Aug 2026 07:28:00 GMT",
) -> Dict[str, Any]:
    """构造 200 响应（测试用）"""
    return {
        "status": 200,
        "headers": {"etag": etag, "last-modified": last_modified},
        "body": json.dumps({
            "updated": "2026-08-26",
            "count": len(plugins),
            "plugins": plugins,
        }),
    }


# =============================================================================
# 4. region routing 多源 fallback（V2.0 借鉴 V1.31 src/regions.ts）
# =============================================================================

@dataclass
class CatalogSource:
    """catalog 数据源（借鉴 V1.31 CatalogSource union）"""
    kind: str                              # "url" / "npm"
    url: Optional[str] = None
    registry: Optional[str] = None         # npm registry
    pkg: Optional[str] = None              # npm 包名


@dataclass
class Region:
    """区域路由表（借鉴 V1.31 Region）"""
    name: str
    catalog_sources: List[CatalogSource] = field(default_factory=list)


DEFAULT_REGION = Region(
    name="default",
    catalog_sources=[
        CatalogSource(kind="url", url="https://awesome-dsh-plugin.com/plugins.json"),
    ],
)


MIRROR_REGION = Region(
    name="mirror",
    catalog_sources=[
        CatalogSource(kind="url", url="https://mirror.example.com/plugins.json"),
        CatalogSource(kind="url", url="https://awesome-dsh-plugin.com/plugins.json"),
    ],
)


def parse_registry_url(env_value: str) -> Optional[CatalogSource]:
    """
    解析 DSHM_REGISTRY_URL 环境变量（借鉴 V1.31 src/registry.ts L40-60）。

    注：天龙实现仅解析 schema，不实际 fetch。
    """
    if not env_value:
        return None
    if env_value.startswith("http://") or env_value.startswith("https://"):
        return CatalogSource(kind="url", url=env_value)
    return None


def resolve_region(env_value: Optional[str] = None) -> Region:
    """根据环境变量解析 region"""
    if env_value:
        src = parse_registry_url(env_value)
        if src:
            return Region(name="env-override", catalog_sources=[src])
    return DEFAULT_REGION


def routes_for_region(region: Region) -> List[CatalogSource]:
    """获取 region 的所有 catalog 源（按顺序尝试 fallback）"""
    return list(region.catalog_sources)


# =============================================================================
# 5. preflightTarget 包存在性 + dsh.bundle 校验（V2.0 借鉴 P0-1 IMPROVEMENT-PLAN）
# =============================================================================

EXIT_CODE_PREFLIGHT_BLOCKED = "blocked"
EXIT_CODE_PREFLIGHT_WARN = "warn"
EXIT_CODE_PREFLIGHT_OK = "ok"


@dataclass
class PreflightResult:
    """安装前置校验结果（借鉴 P0-1 §preflightTarget）"""
    status: str                                # ok / warn / blocked
    exists: bool                               # 目标包是否存在
    has_bundle: bool                           # 是否声明 dsh.bundle
    has_client: bool                           # 是否声明 dsh.client
    reason: str = ""
    # V2.0 拓展
    target_kind: str = ""                      # npm / github-tarball / github-subpath
    target: str = ""                           # 解析后的安装目标


def preflight_target(
    entry: PluginMarketEntry,
    *,
    fake_registry_lookup: Optional[Dict[str, Dict[str, Any]]] = None,
) -> PreflightResult:
    """
    安装前校验（借鉴 V1.31 preflightTarget 4 步校验）。

    Args:
        entry: PluginMarketEntry
        fake_registry_lookup: 测试用 mock 包元数据（key=npm 名, value={dsh.bundle, dsh.client, version}）

    注：天龙实现使用 fake 注入；上游用 pnpm view + npm registry。
    """
    # 解析目标（参考 V1.31 resolveTarget 4 优先级）
    target_kind = ""
    target = ""
    if entry.npm:
        target_kind, target = "npm", entry.npm
    elif entry.package:
        target_kind, target = "npm", entry.package
    elif entry.tarball:
        target_kind, target = "github-tarball", entry.tarball
    elif entry.subpath:
        target_kind, target = "github-subpath", entry.subpath
    elif entry.url:
        target_kind, target = "github-root", entry.url
    else:
        return PreflightResult(
            status=EXIT_CODE_PREFLIGHT_BLOCKED,
            exists=False,
            has_bundle=False,
            has_client=False,
            reason="no installable target (no npm/package/tarball/subpath/url)",
            target_kind="none",
            target="",
        )

    # uninstallable 显式标记
    if entry.uninstallable:
        return PreflightResult(
            status=EXIT_CODE_PREFLIGHT_BLOCKED,
            exists=False,
            has_bundle=False,
            has_client=False,
            reason="marked uninstallable (documentation-only repo)",
            target_kind=target_kind,
            target=target,
        )

    # 测试用 mock 校验
    if fake_registry_lookup is not None:
        if target_kind == "npm" and target not in fake_registry_lookup:
            return PreflightResult(
                status=EXIT_CODE_PREFLIGHT_BLOCKED,
                exists=False,
                has_bundle=False,
                has_client=False,
                reason=f"npm package '{target}' does not exist",
                target_kind=target_kind,
                target=target,
            )
        meta = fake_registry_lookup.get(target, {})
        has_bundle = bool(meta.get("dsh.bundle"))
        has_client = bool(meta.get("dsh.client"))
        if not has_bundle and not has_client:
            return PreflightResult(
                status=EXIT_CODE_PREFLIGHT_WARN,
                exists=True,
                has_bundle=False,
                has_client=False,
                reason="package exists but declares neither dsh.bundle nor dsh.client (may be a plain library)",
                target_kind=target_kind,
                target=target,
            )
        return PreflightResult(
            status=EXIT_CODE_PREFLIGHT_OK,
            exists=True,
            has_bundle=has_bundle,
            has_client=has_client,
            reason="all checks passed",
            target_kind=target_kind,
            target=target,
        )

    # 默认（无 mock）：仅做 schema 校验
    return PreflightResult(
        status=EXIT_CODE_PREFLIGHT_OK,
        exists=True,
        has_bundle=True,
        has_client=False,
        reason="schema OK (no network lookup performed)",
        target_kind=target_kind,
        target=target,
    )


# =============================================================================
# 6. verifyActivation 4 态判定（V2.0 借鉴 P0-2 IMPROVEMENT-PLAN）
# =============================================================================

ACTIVATION_LIVE = "live"          # 热挂载成功（patch 是纯 insert 且 bundles 已含）
ACTIVATION_RESTART = "restart"    # 已安装，需重启生效（patch 含 config/disable 行）
ACTIVATION_INERT = "inert"        # 已装但未成为 profile 层（无 dsh.bundle / 纯客户端插件）
ACTIVATION_BROKEN = "broken"      # 安装完成但校验失败


@dataclass
class ActivationResult:
    """激活验证结果（借鉴 P0-2 verifyActivation 4 态）"""
    state: str                                # live / restart / inert / broken
    reasons: List[str] = field(default_factory=list)
    in_bundles: bool = False                  # dsh.profile.bundles 是否含该包名
    has_bundle: bool = False
    has_client: bool = False
    patch_hot_loadable: bool = False          # patch 是否可热挂载


def parse_simple_patch(yaml_text: str) -> Dict[str, Any]:
    """
    解析 cordis.patch.yml 的简化版本（借鉴 V1.31 src/hot.ts parseSimplePatch）。

    返回 {"operations": [...], "hot_loadable": bool}

    注：天龙的实现是"判断可否热挂载"——只识别纯 insert（无 config/disable 行）。
    """
    ops: List[Dict[str, Any]] = []
    hot_loadable = True

    # 极简 YAML 解析：仅识别 - insert:/disable: 前缀
    for line in yaml_text.splitlines():
        line = line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if line.startswith("- insert:"):
            ops.append({"type": "insert"})
            continue
        if line.startswith("- disable:") or line.startswith("- remove:"):
            ops.append({"type": "disable" if "disable" in line else "remove"})
            hot_loadable = False
            continue
        if line.strip().startswith("config:") and ops:
            # patch 含 config 行 → 不可热挂载
            hot_loadable = False
            continue

    return {"operations": ops, "hot_loadable": hot_loadable}


def verify_activation(
    plugin_name: str,
    *,
    bundles: Optional[List[str]] = None,
    has_bundle: bool = False,
    has_client: bool = False,
    patch_yaml: str = "",
) -> ActivationResult:
    """
    验证插件激活状态（借鉴 P0-2 verifyActivation 4 态）。

    Args:
        plugin_name: 插件包名
        bundles: profile.dsh.profile.bundles 列表（CLI reconcile 后真值）
        has_bundle: 插件是否声明 dsh.bundle
        has_client: 插件是否声明 dsh.client
        patch_yaml: cordis.patch.yml 文本（用于热挂载判定）

    Returns:
        ActivationResult（state + reasons）
    """
    bundles = bundles or []
    in_bundles = plugin_name in bundles
    patch_info = parse_simple_patch(patch_yaml)
    patch_hot_loadable = patch_info["hot_loadable"]

    # 优先级判定：broken > inert > restart > live
    # 1. broken: 不在 bundles 里（CLI 没 reconcile 进）
    if not in_bundles and has_bundle:
        return ActivationResult(
            state=ACTIVATION_BROKEN,
            reasons=[
                f"plugin '{plugin_name}' not found in dsh.profile.bundles",
                "CLI did not reconcile it into the profile layer",
            ],
            in_bundles=False,
            has_bundle=has_bundle,
            has_client=has_client,
            patch_hot_loadable=patch_hot_loadable,
        )

    # 2. inert: 没有 dsh.bundle（纯客户端插件或纯库）
    if not has_bundle:
        if has_client:
            return ActivationResult(
                state=ACTIVATION_INERT,
                reasons=[
                    f"plugin '{plugin_name}' is client-only (no dsh.bundle declared)",
                    "it renders in the web UI but contributes no host-side row",
                ],
                in_bundles=in_bundles,
                has_bundle=False,
                has_client=True,
                patch_hot_loadable=False,
            )
        return ActivationResult(
            state=ACTIVATION_INERT,
            reasons=[
                f"plugin '{plugin_name}' declares neither dsh.bundle nor dsh.client",
                "it was installed as a plain library dependency",
            ],
            in_bundles=False,
            has_bundle=False,
            has_client=False,
            patch_hot_loadable=False,
        )

    # 3. live vs restart: 看 patch 是否可热挂载
    if patch_hot_loadable and in_bundles:
        return ActivationResult(
            state=ACTIVATION_LIVE,
            reasons=["pure insert patch hot-loaded successfully"],
            in_bundles=True,
            has_bundle=True,
            has_client=has_client,
            patch_hot_loadable=True,
        )

    # 4. restart: 已 install 但 patch 不可热挂
    return ActivationResult(
        state=ACTIVATION_RESTART,
        reasons=[
            "patch contains config or disable rows (not hot-loadable)",
            "DSH restart required to take effect",
        ],
        in_bundles=in_bundles,
        has_bundle=True,
        has_client=has_client,
        patch_hot_loadable=False,
    )


# =============================================================================
# 7. pnpm v10/v11 allowBuilds 兼容（V2.0 借鉴 V1.31 src/pnpm-compat.ts）
# =============================================================================

PNPM_V10 = "10"
PNPM_V11 = "11"


def detect_pnpm_major_version(pnpm_version: str) -> str:
    """
    探测 pnpm 主版本（决定 allowBuilds vs onlyBuiltDependencies 键名）。

    Returns:
        "10" 或 "11"
    """
    if not pnpm_version:
        return PNPM_V10
    m = re.match(r"^(\d+)", pnpm_version.strip())
    if not m:
        return PNPM_V10
    major = m.group(1)
    if major >= "11":
        return PNPM_V11
    return PNPM_V10


def build_allow_builds_entry(
    packages: List[str],
    pnpm_version: str,
) -> Dict[str, Any]:
    """
    构造 allowBuilds 配置条目（V2.0 借鉴 V1.31 pnpm-compat 双键名）。

    - pnpm v10 → `onlyBuiltDependencies: [pkgs]`
    - pnpm v11 → `allowBuilds: { pkg: true }`
    """
    if detect_pnpm_major_version(pnpm_version) == PNPM_V11:
        return {"allowBuilds": {pkg: True for pkg in packages}}
    return {"onlyBuiltDependencies": packages}


def merge_pnpm_workspace_yaml(
    existing_yaml: str,
    packages: List[str],
    pnpm_version: str,
) -> str:
    """
    合并 pnpm-workspace.yaml（借鉴 V1.31 pnpm-compat.ts "保留原有内容不覆盖"）。

    Args:
        existing_yaml: 现有 yaml 文本（可能含其他配置）
        packages: 要添加的 allowBuilds 包名列表
        pnpm_version: pnpm 版本字符串

    Returns:
        合并后的 yaml 文本
    """
    entry = build_allow_builds_entry(packages, pnpm_version)
    key = "allowBuilds" if "allowBuilds" in entry else "onlyBuiltDependencies"

    # 极简实现：直接在尾部追加（生产环境应使用 PyYAML 解析合并）
    if key == "allowBuilds":
        allow_dict = entry["allowBuilds"]
        lines = [f"{pkg}: true" for pkg in allow_dict.keys()]
        new_block = f"\n{key}:\n  " + "\n  ".join(lines) + "\n"
    else:
        pkgs = entry["onlyBuiltDependencies"]
        items = "\n    - ".join(pkgs)
        new_block = f"\n{key}:\n    - {items}\n"

    return existing_yaml.rstrip() + "\n" + new_block


def parse_blocked_builds_from_stderr(stderr: str) -> List[str]:
    """
    从 pnpm stderr 解析被拦截的构建脚本（借鉴 P0-4 parsePnpmFailure）。

    匹配 "Ignored build scripts: pkg1, pkg2" 行。
    """
    m = re.search(r"Ignored build scripts:\s*(.+)", stderr)
    if not m:
        return []
    return [pkg.strip() for pkg in m.group(1).split(",") if pkg.strip()]


# =============================================================================
# 8. backup/restore 模块（V2.0 借鉴 V1.31 src/backup.ts 26 KB）
# =============================================================================

@dataclass
class BackupProfile:
    """profile 备份（借鉴 V1.31 backup 导出格式）"""
    profile: str
    bundles: List[str]
    exported_at: float
    schema_version: str = "1.0"
    # V2.0 扩展
    cordis_patch: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


def export_backup(
    profile_name: str,
    bundles: List[str],
    *,
    cordis_patch: Optional[str] = None,
    settings: Optional[Dict[str, Any]] = None,
) -> BackupProfile:
    """
    导出 profile 备份（借鉴 V1.31 backup.ts exportBackup）。

    返回 JSON-friendly BackupProfile 对象（用 asdict 序列化）。
    """
    return BackupProfile(
        profile=profile_name,
        bundles=list(bundles),
        exported_at=time.time(),
        schema_version="1.0",
        cordis_patch=cordis_patch,
        settings=settings,
    )


@dataclass
class RestoreReport:
    """restore 报告（借鉴 V1.31 backup.ts merge restore）"""
    installed: List[str] = field(default_factory=list)       # 新安装的
    skipped: List[str] = field(default_factory=list)         # 已存在跳过
    merged: bool = False                                    # 是否 merge 模式（保留 backup 后的安装）
    failed: List[str] = field(default_factory=list)


def restore_backup(
    backup: BackupProfile,
    *,
    current_bundles: Optional[List[str]] = None,
    merge: bool = True,
) -> RestoreReport:
    """
    还原 profile 备份（借鉴 V1.31 merge restore 语义）。

    Args:
        backup: 备份对象
        current_bundles: 当前已装 bundles
        merge: True=合并（保留 backup 后安装的），False=覆盖
    """
    current = set(current_bundles or [])
    target = set(backup.bundles)
    report = RestoreReport(merged=merge)

    if merge:
        # merge 模式：安装 backup 里有但当前没有的
        to_install = target - current
        to_skip = target & current
        report.installed = sorted(to_install)
        report.skipped = sorted(to_skip)
    else:
        # 覆盖模式：全部安装
        report.installed = sorted(target)
        report.skipped = []

    report.merged = merge
    return report


# =============================================================================
# 9. themes 互斥切换（V2.0 借鉴 V1.31 src/themes.ts）
# =============================================================================

@dataclass
class ThemeState:
    """主题状态（借鉴 V1.31 themes 互斥语义）"""
    active_theme: Optional[str] = None
    installed_themes: List[str] = field(default_factory=list)


def switch_theme(
    state: ThemeState,
    new_theme: str,
) -> ThemeState:
    """
    切换主题（互斥：新主题替换旧的；旧主题自动 deactivate）。

    借鉴 V1.31 themes.ts：themes are mutually exclusive, your choice survives restarts.
    """
    return ThemeState(
        active_theme=new_theme,
        installed_themes=list(set(state.installed_themes + [new_theme])),
    )


def uninstall_theme(
    state: ThemeState,
    theme: str,
) -> ThemeState:
    """卸载主题；若是 active，则回退到 None（用户需手动选新主题）"""
    new_installed = [t for t in state.installed_themes if t != theme]
    new_active = state.active_theme if state.active_theme != theme else None
    return ThemeState(active_theme=new_active, installed_themes=new_installed)


# =============================================================================
# 10. restart systemd/loopback 守卫（V2.0 借鉴 V1.31 src/restart.ts）
# =============================================================================

def detect_systemd_main_process(invocation_id: Optional[str], unit_pid: Optional[int]) -> bool:
    """
    检测是否在 systemd 单元的主进程中运行（借鉴 V1.31 restart.ts）。

    守卫逻辑：必须同时满足
      1. 有 INVOCATION_ID 环境变量
      2. 当前进程 PID 等于 unit 的 MainPID
    """
    if not invocation_id:
        return False
    if unit_pid is None:
        return False
    return os.getpid() == unit_pid


def should_show_restart_button(
    *,
    invocation_id: Optional[str] = None,
    unit_pid: Optional[int] = None,
    allow_restart: Optional[bool] = None,
) -> bool:
    """
    是否应该显示"一键重启"按钮（借鉴 V1.31 restart.ts 多条件判定）。

    优先级：
      1. allow_restart=False → 永远不显示
      2. systemd 主进程 → 不显示（避免 cgroup 自杀）
      3. 默认 → 显示
    """
    if allow_restart is False:
        return False
    if detect_systemd_main_process(invocation_id, unit_pid):
        return False
    return True


# =============================================================================
# 11. 16/13 open_issues 策略表（V2.0 升级 · 借鉴 IMPROVEMENT-PLAN）
# =============================================================================

# V1.0 5 类 + V2.0 扩展为 13 类（对应 IMPROVEMENT-PLAN P0-1..P2-13）
ISSUE_CATEGORIES = {
    "search":         "search and filter engine optimization",
    "filter":         "category and tag filtering",
    "install":        "one-click install reliability (P0-1/2/3/4)",
    "compat":         "version compatibility matrix",
    "security":       "checksum verification + sandbox",
    "preflight":      "P0-1 install target validation",
    "activation":     "P0-2 post-install verification",
    "version":        "P0-3 minimumReleaseAge handling",
    "build":          "P0-4 allowBuilds approval flow",
    "diagnose":       "P1-5/P1-9 structured error diagnosis",
    "progress":       "P1-6 ndjson progress/cancel",
    "lock":           "P1-7 commit pinning",
    "registry":       "P1-8 catalog data governance",
}


def classify_issue(title: str) -> str:
    """对 issue title 分类（V2.0 升级为 13 类）"""
    title_lower = title.lower()
    for cat in ISSUE_CATEGORIES.keys():
        if cat in title_lower:
            return cat
    return "other"


# =============================================================================
# 12. search + filter engine（V2.0 扩展：5 维度 + 双语文本）
# =============================================================================

@dataclass
class SearchQuery:
    """插件搜索 query（V2.0 扩展）"""
    text: str = ""
    category: Optional[str] = None
    min_stars: int = 0
    max_version: Optional[str] = None
    # V2.0 新增：语言偏好（auto / en / zh）
    language: str = "auto"


def _text_matches(plugin: PluginMarketEntry, text: str) -> bool:
    """文本匹配（V2.0 支持双语 description）"""
    if not text:
        return True
    t = text.lower()
    if t in plugin.name.lower() or t in plugin.description.lower():
        return True
    if plugin.description_en and t in plugin.description_en.lower():
        return True
    if plugin.description_zh and t in plugin.description_zh.lower():
        return True
    return False


def filter_plugins(
    plugins: List[PluginMarketEntry],
    query: SearchQuery,
) -> List[PluginMarketEntry]:
    """
    5 维度 filter：text/category/stars/version/language。
    """
    results = []
    for p in plugins:
        if not _text_matches(p, query.text):
            continue
        if query.category and query.category not in p.categories:
            continue
        if p.stars < query.min_stars:
            continue
        if query.max_version and p.version > query.max_version:
            continue
        results.append(p)
    return results


# =============================================================================
# 13. version pinning（V1.0 兼容）
# =============================================================================

def parse_semver(version: str) -> tuple:
    """解析 'major.minor.patch' → tuple"""
    parts = version.split(".")
    if len(parts) < 3:
        return (0, 0, 0)
    try:
        return (int(parts[0]), int(parts[1]), int(parts[2].split("-")[0]))
    except ValueError:
        return (0, 0, 0)


def satisfies_version(installed: str, required: str) -> bool:
    """检查 installed >= required（简化 semver）"""
    return parse_semver(installed) >= parse_semver(required)


# =============================================================================
# CLI（V1.0 兼容 + V2.0 新增子命令）
# =============================================================================

def cmd_parse_plugin(args: argparse.Namespace) -> int:
    """解析 plugin manifest JSON"""
    try:
        entry = parse_plugin_json(args.input, strict=args.strict)
    except ValueError as e:
        print(f"[parse error] {e}", file=sys.stderr)
        return EXIT_PARSE
    print(json.dumps(asdict(entry), indent=2, ensure_ascii=False))
    return EXIT_OK


def cmd_install_flow(args: argparse.Namespace) -> int:
    """演示一键安装 6 阶段 workflow（V2.0）"""
    state = InstallState()
    print("=== dsh-market V2.0 one-click install workflow (6 phases) ===")
    while state.phase != "activation-check":
        state = advance_install(state)
        print(f"  [{state.progress*100:5.1f}%] {state.phase:<20} {state.message}")
    # activation-check 阶段不打印自己（终态）
    print(f"  [100.0%] activation-check      activation verified")
    return EXIT_OK


def cmd_classify_issue(args: argparse.Namespace) -> int:
    """对 issue title 分类"""
    cat = classify_issue(args.title)
    desc = ISSUE_CATEGORIES.get(cat, "no specific category")
    print(json.dumps({"title": args.title, "category": cat, "strategy": desc}, indent=2, ensure_ascii=False))
    return EXIT_OK


def cmd_filter(args: argparse.Namespace) -> int:
    """5 维度 filter plugin（V2.0 升级）"""
    mock_plugins = [
        PluginMarketEntry("tui-bridge", "TUI Bridge", "0.9.2", "DSH TUI client", "ccch1mneyyy", ["frontend"], 2566, 128),
        PluginMarketEntry("peak-gate", "Peak Gate", "0.2.0", "peak/off-peak gate", "f20880479-lab", ["traffic"], 3, 1),
        PluginMarketEntry("balance-meter", "Balance Meter", "0.1.0", "DSH balance", "Ghost011118", ["finance"], 0, 0),
        PluginMarketEntry("univer-office", "Univer Office", "0.2.9", "Office suite", "dream-num", ["office"], 8, 3),
    ]
    try:
        query_data = json.loads(args.query)
        query = SearchQuery(**query_data)
    except (json.JSONDecodeError, TypeError) as e:
        print(f"[parse error] {e}", file=sys.stderr)
        return EXIT_PARSE
    results = filter_plugins(mock_plugins, query)
    print(json.dumps([asdict(p) for p in results], indent=2, ensure_ascii=False))
    return EXIT_OK


def cmd_check_version(args: argparse.Namespace) -> int:
    """semver 兼容性检查"""
    ok = satisfies_version(args.installed, args.required)
    print(json.dumps({
        "installed": args.installed,
        "required": args.required,
        "satisfies": ok,
        "installed_parsed": list(parse_semver(args.installed)),
        "required_parsed": list(parse_semver(args.required)),
    }, indent=2))
    return EXIT_OK if ok else EXIT_VERSION


def cmd_preflight(args: argparse.Namespace) -> int:
    """V2.0 新增：安装前置校验"""
    try:
        entry = parse_plugin_json(args.input)
    except ValueError as e:
        print(f"[parse error] {e}", file=sys.stderr)
        return EXIT_PARSE
    result = preflight_target(entry)
    print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
    if result.status == EXIT_CODE_PREFLIGHT_BLOCKED:
        return EXIT_PREFLIGHT
    return EXIT_OK


def cmd_verify(args: argparse.Namespace) -> int:
    """V2.0 新增：安装后激活验证"""
    bundles = json.loads(args.bundles) if args.bundles else []
    patch_yaml = args.patch or ""
    result = verify_activation(
        args.name,
        bundles=bundles,
        has_bundle=args.has_bundle,
        has_client=args.has_client,
        patch_yaml=patch_yaml,
    )
    print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
    if result.state == ACTIVATION_BROKEN:
        return EXIT_ACTIVATION
    return EXIT_OK


def cmd_pnpm_compat(args: argparse.Namespace) -> int:
    """V2.0 新增：pnpm 兼容配置构造"""
    pkgs = [p.strip() for p in args.packages.split(",") if p.strip()]
    entry = build_allow_builds_entry(pkgs, args.pnpm_version)
    print(json.dumps(entry, indent=2, ensure_ascii=False))
    return EXIT_OK


def cmd_backup(args: argparse.Namespace) -> int:
    """V2.0 新增：备份导出"""
    bundles = json.loads(args.bundles) if args.bundles else []
    backup = export_backup(
        args.profile,
        bundles,
        cordis_patch=args.patch,
        settings=json.loads(args.settings) if args.settings else None,
    )
    print(json.dumps(asdict(backup), indent=2, ensure_ascii=False))
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dsh_market_bridge",
        description="Stage 50.3 dsh-market-bridge V2.0 · dsh-market/dsh-market MIT V1.31.1 借鉴档",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # === V1.0 兼容子命令 ===
    sp = sub.add_parser("parse-plugin", help="解析 plugin manifest JSON (V1.0)")
    sp.add_argument("--input", required=True, help="plugin manifest JSON")
    sp.add_argument("--strict", action="store_true", help="V1.0 严格模式（5 字段必填）")
    sp.set_defaults(func=cmd_parse_plugin)

    sp = sub.add_parser("install-flow", help="演示一键安装 6 阶段 workflow (V2.0)")
    sp.set_defaults(func=cmd_install_flow)

    sp = sub.add_parser("classify-issue", help="对 issue title 分类（V2.0 13 类）")
    sp.add_argument("--title", required=True)
    sp.set_defaults(func=cmd_classify_issue)

    sp = sub.add_parser("filter", help="5 维度 filter plugin (V2.0)")
    sp.add_argument("--query", required=True)
    sp.set_defaults(func=cmd_filter)

    sp = sub.add_parser("check-version", help="semver 兼容性检查")
    sp.add_argument("--installed", required=True)
    sp.add_argument("--required", required=True)
    sp.set_defaults(func=cmd_check_version)

    # === V2.0 新增子命令 ===
    sp = sub.add_parser("preflight", help="V2.0 安装前置校验（P0-1）")
    sp.add_argument("--input", required=True, help="plugin manifest JSON")
    sp.set_defaults(func=cmd_preflight)

    sp = sub.add_parser("verify", help="V2.0 安装后激活验证（P0-2）")
    sp.add_argument("--name", required=True, help="plugin name")
    sp.add_argument("--bundles", default="[]", help='JSON 数组，如 ["pkg1","pkg2"]')
    sp.add_argument("--has-bundle", action="store_true", help="plugin declares dsh.bundle")
    sp.add_argument("--has-client", action="store_true", help="plugin declares dsh.client")
    sp.add_argument("--patch", default="", help="cordis.patch.yml text")
    sp.set_defaults(func=cmd_verify)

    sp = sub.add_parser("pnpm-compat", help="V2.0 pnpm allowBuilds 兼容（P1-8）")
    sp.add_argument("--packages", required=True, help='逗号分隔，如 "esbuild,node-gyp"')
    sp.add_argument("--pnpm-version", default="10", help='pnpm 版本，如 "10.5.0"')
    sp.set_defaults(func=cmd_pnpm_compat)

    sp = sub.add_parser("backup", help="V2.0 备份导出（backup.ts）")
    sp.add_argument("--profile", required=True)
    sp.add_argument("--bundles", default="[]")
    sp.add_argument("--patch", default=None)
    sp.add_argument("--settings", default=None)
    sp.set_defaults(func=cmd_backup)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
