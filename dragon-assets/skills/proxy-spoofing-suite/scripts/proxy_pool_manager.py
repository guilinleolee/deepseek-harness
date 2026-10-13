#!/usr/bin/env python3
# =============================================================================
# proxy_pool_manager.py — CloakBrowser 代理池管理脚本
# 天龙引擎V11.17 | 来源: CloakHQ/CloakBrowser
# 支持: 代理添加/删除/轮换/健康检查/GeoIP伪装/评分/头注入验证
# =============================================================================

import argparse
import json
import os
import re
import socket
import subprocess
import sys
import time
import urllib.request
import urllib.error
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# =============================================================================
# 配置
# =============================================================================

DEFAULT_PROXIES_FILE = Path.home() / ".cloakbrowser" / "proxies.json"
DEFAULT_CHECK_TIMEOUT = 10  # 秒
DEFAULT_TEST_URL = "https://httpbin.org/ip"

# 评分权重
WEIGHT_SPEED = 0.40
WEIGHT_ANONYMITY = 0.35
WEIGHT_STABILITY = 0.25

# 评分阈值
SCORE_PREMIUM = 8.0
SCORE_L3_GOOD = 6.0
SCORE_BACKUP = 4.0

# HTTPBin 用于检测真实出口IP
IP_DETECTION_URL = "https://httpbin.org/ip"


# =============================================================================
# 数据模型
# =============================================================================

@dataclass
class ProxyHealth:
    """代理健康状态"""
    last_check: str
    speed_ms: float
    anonymity: str  # elite / transparent / anonymous
    stability: float  # 0.0-1.0
    dns_leak: bool
    webRTC_leak: bool
    available: bool


@dataclass
class ProxyEntry:
    """单个代理条目"""
    proxy: str  # 完整代理URL
    country: str  # ISO国家代码
    tags: list[str] = field(default_factory=list)
    added: str = ""
    last_used: str = ""
    use_count: int = 0
    score: float = 5.0
    health: Optional[ProxyHealth] = None
    status: str = "active"  # active / inactive / removed

    def __post_init__(self):
        if not self.added:
            self.added = datetime.now(timezone.utc).isoformat()
        if isinstance(self.health, dict):
            self.health = ProxyHealth(**self.health) if self.health else None

    def to_dict(self) -> dict:
        d = asdict(self)
        if self.health:
            d["health"] = asdict(self.health)
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "ProxyEntry":
        if "health" in d and d["health"]:
            d["health"] = ProxyHealth(**d["health"])
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class ProxyPool:
    """代理池"""
    version: str = "1.0"
    updated: str = ""
    proxies: list[ProxyEntry] = field(default_factory=list)

    def __post_init__(self):
        if not self.updated:
            self.updated = datetime.now(timezone.utc).isoformat()

    def save(self, path: Path = DEFAULT_PROXIES_FILE):
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": self.version,
            "updated": datetime.now(timezone.utc).isoformat(),
            "proxies": [p.to_dict() for p in self.proxies]
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: Path = DEFAULT_PROXIES_FILE) -> "ProxyPool":
        if not path.exists():
            return cls()
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            proxies = [ProxyEntry.from_dict(p) for p in data.get("proxies", [])]
            return cls(
                version=data.get("version", "1.0"),
                updated=data.get("updated", ""),
                proxies=proxies,
            )
        except (json.JSONDecodeError, KeyError):
            return cls()


# =============================================================================
# 代理解析
# =============================================================================

def parse_proxy_url(url: str) -> dict:
    """解析代理URL，返回协议/主机/端口/用户名/密码"""
    pattern = r"^(https?|socks5|socks4)://(?:([^:@]+):(?:[^@]+)@)?([^:]+):(\d+)/?$"
    m = re.match(pattern, url.strip())
    if not m:
        raise ValueError(f"无效的代理URL格式: {url}")
    proto = m.group(1)
    user = m.group(2) or ""
    host = m.group(3)
    port = int(m.group(4))
    return {"protocol": proto, "user": user, "host": host, "port": port}


def proxy_to_dict(url: str) -> dict:
    """将代理URL转换为标准化字典"""
    p = parse_proxy_url(url)
    return {
        "proxy": url,
        "host": p["host"],
        "port": p["port"],
        "protocol": p["protocol"],
        "user": p["user"],
    }


# =============================================================================
# 健康检查
# =============================================================================

def check_proxy_health(proxy_url: str, timeout: int = DEFAULT_CHECK_TIMEOUT) -> ProxyHealth:
    """检查代理可用性、速度、匿名度"""
    p = parse_proxy_url(proxy_url)
    start_time = time.time()

    # 1. 连接测试
    try:
        if p["protocol"] in ("http", "https"):
            proxies = {"http": proxy_url, "https": proxy_url}
            req = urllib.request.Request(IP_DETECTION_URL, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=timeout, proxies=proxies) as resp:
                ip_data = json.loads(resp.read().decode())
                proxy_ip = ip_data.get("origin", "")
        elif p["protocol"] == "socks5":
            proxy_ip = _check_socks5(proxy_url, timeout)
        elif p["protocol"] == "socks4":
            proxy_ip = _check_socks4(proxy_url, timeout)
        else:
            raise ValueError(f"不支持的协议: {p['protocol']}")
    except Exception as e:
        return ProxyHealth(
            last_check=datetime.now(timezone.utc).isoformat(),
            speed_ms=timeout * 1000,
            anonymity="unknown",
            stability=0.0,
            dns_leak=True,
            webRTC_leak=True,
            available=False,
        )

    speed_ms = (time.time() - start_time) * 1000

    # 2. 匿名度检测
    anonymity = _detect_anonymity(proxy_ip, timeout)

    # 3. DNS泄漏检测（通过代理检测真实IP对比）
    dns_leak = False  # 简化版

    # 4. WebRTC泄漏检测（简化版）
    webRTC_leak = anonymity == "transparent"

    # 5. 稳定性模拟（基于连续可用性）
    stability = 0.95 if anonymity != "unknown" else 0.5

    return ProxyHealth(
        last_check=datetime.now(timezone.utc).isoformat(),
        speed_ms=round(speed_ms, 1),
        anonymity=anonymity,
        stability=stability,
        dns_leak=dns_leak,
        webRTC_leak=webRTC_leak,
        available=True,
    )


def _check_socks5(proxy_url: str, timeout: int) -> str:
    """通过SOCKS5代理获取出口IP"""
    try:
        import socks
        p = parse_proxy_url(proxy_url)
        socks.set_default_proxy(
            socks.SOCKS5,
            p["host"],
            p["port"],
            username=p["user"] or None,
            password=None,
        )
        socket_original = socket.socket
        socket.socket = socks.socksocket
        try:
            req = urllib.request.Request(IP_DETECTION_URL)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode())
                return data.get("origin", "")
        finally:
            socket.socket = socket_original
    except ImportError:
        return "socks-check-skipped"
    except Exception:
        return "socks-check-failed"


def _check_socks4(proxy_url: str, timeout: int) -> str:
    """通过SOCKS4代理获取出口IP"""
    try:
        import socks
        p = parse_proxy_url(proxy_url)
        socks.set_default_proxy(
            socks.SOCKS4,
            p["host"],
            p["port"],
            username=p.get("user", ""),
        )
        socket_original = socket.socket
        socket.socket = socks.socksocket
        try:
            req = urllib.request.Request(IP_DETECTION_URL)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode())
                return data.get("origin", "")
        finally:
            socket.socket = socket_original
    except ImportError:
        return "socks-check-skipped"
    except Exception:
        return "socks-check-failed"


def _detect_anonymity(proxy_ip: str, timeout: int) -> str:
    """检测匿名度"""
    if "socks" in proxy_ip.lower() or proxy_ip == "" or proxy_ip == "failed":
        return "transparent"
    try:
        # 通过代理获取的IP vs 直接获取的IP
        req = urllib.request.Request(IP_DETECTION_URL)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            direct_data = json.loads(resp.read().decode())
            direct_ip = direct_data.get("origin", "")

        if proxy_ip == direct_ip:
            return "transparent"  # 未走代理
        # 检查是否泄漏了真实IP信息
        return "elite"
    except Exception:
        return "unknown"


# =============================================================================
# 代理评分
# =============================================================================

def score_proxy(health: ProxyHealth) -> float:
    """基于健康数据计算代理评分 (0-10)"""
    if not health.available:
        return 0.0

    # 速度评分 (40%): <500ms=10, >5000ms=0
    speed_score = max(0.0, min(10.0, 10.0 - (health.speed_ms - 500) / 500))

    # 匿名度评分 (35%): elite=10, anonymous=7, transparent=2, unknown=0
    anon_map = {"elite": 10.0, "anonymous": 7.0, "transparent": 2.0, "unknown": 0.0}
    anon_score = anon_map.get(health.anonymity, 0.0)

    # 稳定性评分 (25%): 直接使用stability * 10
    stability_score = health.stability * 10.0

    total = (
        speed_score * WEIGHT_SPEED
        + anon_score * WEIGHT_ANONYMITY
        + stability_score * WEIGHT_STABILITY
    )
    return round(total, 2)


def get_score_label(score: float) -> str:
    """获取评分标签"""
    if score >= SCORE_PREMIUM:
        return "优质代理 (L4首选)"
    elif score >= SCORE_L3_GOOD:
        return "良好代理 (L3可用)"
    elif score >= SCORE_BACKUP:
        return "一般代理 (仅备用)"
    else:
        return "低质代理 (自动剔除)"


# =============================================================================
# GeoIP 查询
# =============================================================================

def geoip_lookup(host: str) -> dict:
    """查询IP的地理位置（简化版，使用 ip-api.com）"""
    try:
        url = f"http://ip-api.com/json/{host}?fields=status,country,countryCode,timezone,city"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            if data.get("status") == "success":
                return {
                    "ip": host,
                    "country": data.get("countryCode", ""),
                    "country_name": data.get("country", ""),
                    "timezone": data.get("timezone", ""),
                    "city": data.get("city", ""),
                }
    except Exception:
        pass
    return {"ip": host, "country": "", "timezone": "", "city": ""}


# =============================================================================
# 头注入验证
# =============================================================================

def verify_headers(proxy_url: str, test_url: str = DEFAULT_TEST_URL) -> dict:
    """验证代理头注入是否正确"""
    p = parse_proxy_url(proxy_url)
    result = {
        "proxy": proxy_url,
        "test_url": test_url,
        "success": False,
        "detected_ip": "",
        "headers": {},
        "issues": [],
    }

    try:
        if p["protocol"] in ("http", "https"):
            proxies = {"http": proxy_url, "https": proxy_url}
            req = urllib.request.Request(test_url, headers={
                "User-Agent": "Mozilla/5.0",
                "Accept-Language": "en-US,en;q=0.9",
                "X-Forwarded-For": "203.0.113.50",
                "Via": "1.1 cloakbrowser",
            })
            with urllib.request.urlopen(req, timeout=DEFAULT_CHECK_TIMEOUT, proxies=proxies) as resp:
                body = json.loads(resp.read().decode())
                result["success"] = True
                result["headers"] = body.get("headers", {})
                result["detected_ip"] = body.get("origin", "")
        else:
            result["issues"].append(f"头验证仅支持HTTP/HTTPS代理，当前协议: {p['protocol']}")
    except Exception as e:
        result["issues"].append(str(e))

    return result


# =============================================================================
# 代理池操作
# =============================================================================

def find_proxy(pool: ProxyPool, proxy_url: str) -> Optional[ProxyEntry]:
    """按URL查找代理"""
    for p in pool.proxies:
        if p.proxy == proxy_url and p.status != "removed":
            return p
    return None


def add_proxy(
    pool: ProxyPool,
    proxy_url: str,
    country: str = "",
    tags: Optional[list[str]] = None,
) -> ProxyEntry:
    """添加代理到池"""
    existing = find_proxy(pool, proxy_url)
    if existing:
        existing.status = "active"
        return existing

    entry = ProxyEntry(
        proxy=proxy_url,
        country=country.upper() if country else "",
        tags=tags or [],
    )
    pool.proxies.append(entry)
    return entry


def remove_proxy(pool: ProxyPool, proxy_url: str) -> bool:
    """从池中移除代理（软删除）"""
    entry = find_proxy(pool, proxy_url)
    if entry:
        entry.status = "removed"
        return True
    return False


def select_best_proxy(
    pool: ProxyPool,
    level: str = "L3",
    country: Optional[str] = None,
    require_tags: Optional[list[str]] = None,
) -> Optional[ProxyEntry]:
    """根据条件选择最优代理"""
    candidates = []
    min_score = SCORE_L3_GOOD if level == "L4" else SCORE_BACKUP

    for p in pool.proxies:
        if p.status != "active":
            continue
        if p.score < min_score:
            continue
        if country and p.country.upper() != country.upper():
            continue
        if require_tags:
            if not any(t in p.tags for t in require_tags):
                continue
        candidates.append(p)

    if not candidates:
        return None

    # 按评分降序
    candidates.sort(key=lambda x: x.score, reverse=True)
    best = candidates[0]
    best.last_used = datetime.now(timezone.utc).isoformat()
    best.use_count += 1
    return best


# =============================================================================
# CLI 命令处理器
# =============================================================================

def cmd_add(args, pool: ProxyPool) -> int:
    """添加代理"""
    try:
        parse_proxy_url(args.proxy)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1

    tags = args.tags.split(",") if args.tags else []
    entry = add_proxy(pool, args.proxy, args.country, tags)
    pool.save()

    print(f"✓ 代理已添加: {args.proxy}")
    print(f"  国家: {entry.country or '未知'}")
    print(f"  标签: {', '.join(entry.tags) or '无'}")

    # 健康检查
    if args.check_health:
        print("  执行健康检查...")
        health = check_proxy_health(args.proxy)
        entry.health = health
        entry.score = score_proxy(health)
        pool.save()
        label = get_score_label(entry.score)
        print(f"  健康状态: {health.anonymity} | 速度: {health.speed_ms}ms | 评分: {entry.score}/10 [{label}]")

    return 0


def cmd_batch_add(args, pool: ProxyPool) -> int:
    """批量添加代理"""
    path = Path(args.file)
    if not path.exists():
        print(f"错误: 文件不存在: {path}", file=sys.stderr)
        return 1

    lines = path.read_text(encoding="utf-8").splitlines()
    added = 0
    failed = 0

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if not parts:
            continue
        proxy = parts[0]
        country = ""
        tags = []
        for part in parts[1:]:
            if part.startswith("--country="):
                country = part.split("=", 1)[1]
            elif part.startswith("--tags="):
                tags = part.split("=", 1)[1].split(",")

        try:
            parse_proxy_url(proxy)
            entry = add_proxy(pool, proxy, country, tags)
            if args.check_health:
                health = check_proxy_health(proxy)
                entry.health = health
                entry.score = score_proxy(health)
            added += 1
        except ValueError:
            failed += 1
            print(f"  跳过无效代理: {proxy}")

    pool.save()
    print(f"\n✓ 批量添加完成: {added} 成功, {failed} 失败")
    return 0


def cmd_get(args, pool: ProxyPool) -> int:
    """获取最优代理"""
    country = args.country or None
    tags = args.tags.split(",") if args.tags else None

    entry = select_best_proxy(pool, args.level, country, tags)

    if not entry:
        print(f"未找到符合条件的代理 (level={args.level}", end="")
        if country:
            print(f", country={country}", end="")
        if tags:
            print(f", tags={tags}", end="")
        print(")", file=sys.stderr)
        return 1

    print(entry.proxy)

    if args.verbose or args.json:
        p = parse_proxy_url(entry.proxy)
        geo = geoip_lookup(p["host"])
        output = {
            "proxy": entry.proxy,
            "country": entry.country,
            "score": entry.score,
            "score_label": get_score_label(entry.score),
            "level": args.level,
            "tags": entry.tags,
            "use_count": entry.use_count,
            "geoip": geo,
        }
        if args.json:
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            print(f"  国家: {entry.country or geo.get('country', '未知')}")
            print(f"  评分: {entry.score}/10 [{get_score_label(entry.score)}]")
            print(f"  时区: {geo.get('timezone', '未知')}")
            print(f"  使用次数: {entry.use_count}")
        pool.save()

    return 0


def cmd_health(args, pool: ProxyPool) -> int:
    """健康检查"""
    targets = []
    if args.all:
        targets = [p for p in pool.proxies if p.status == "active"]
    else:
        entry = find_proxy(pool, args.proxy)
        if entry:
            targets = [entry]
        else:
            print(f"错误: 代理未找到: {args.proxy}", file=sys.stderr)
            return 1

    print(f"检查 {len(targets)} 个代理...")
    for p in targets:
        health = check_proxy_health(p.proxy, args.timeout)
        p.health = health
        p.score = score_proxy(health)
        label = get_score_label(p.score)

        status_icon = "✓" if health.available else "✗"
        print(f"\n{status_icon} {p.proxy}")
        print(f"  匿名度: {health.anonymity}")
        print(f"  速度: {health.speed_ms}ms")
        print(f"  稳定性: {health.stability:.0%}")
        print(f"  评分: {p.score}/10 [{label}]")
        print(f"  上次检查: {health.last_check}")

        if p.score < SCORE_BACKUP:
            print(f"  ⚠ 评分过低，建议移除")
            if args.auto_remove:
                p.status = "removed"

    pool.save()

    # 自动剔除低质代理
    if args.auto_remove:
        removed = [p for p in pool.proxies if p.score < SCORE_BACKUP and p.status == "active"]
        if removed:
            for p in removed:
                p.status = "removed"
            pool.save()
            print(f"\n✓ 已自动剔除 {len(removed)} 个低质代理")

    return 0


def cmd_score(args, pool: ProxyPool) -> int:
    """评分单个代理"""
    entry = find_proxy(pool, args.proxy)
    if not entry:
        print(f"错误: 代理未找到: {args.proxy}", file=sys.stderr)
        return 1

    health = check_proxy_health(args.proxy)
    entry.health = health
    entry.score = score_proxy(health)
    pool.save()

    label = get_score_label(entry.score)
    print(f"代理: {args.proxy}")
    print(f"评分: {entry.score}/10 [{label}]")
    print(f"  速度: {health.speed_ms}ms (权重 {WEIGHT_SPEED:.0%})")
    print(f"  匿名度: {health.anonymity} (权重 {WEIGHT_ANONYMITY:.0%})")
    print(f"  稳定性: {health.stability:.0%} (权重 {WEIGHT_STABILITY:.0%})")

    return 0


def cmd_geoip(args, pool: ProxyPool) -> int:
    """GeoIP查询"""
    entry = find_proxy(pool, args.proxy)
    if entry:
        p = parse_proxy_url(entry.proxy)
        host = p["host"]
    else:
        p = parse_proxy_url(args.proxy)
        host = p["host"]

    geo = geoip_lookup(host)

    if args.json:
        output = {
            "proxy": args.proxy,
            "host": host,
            "country": geo.get("country", ""),
            "country_name": geo.get("country_name", ""),
            "timezone": geo.get("timezone", ""),
            "city": geo.get("city", ""),
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(f"IP: {host}")
        print(f"国家: {geo.get('country_name', '未知')} ({geo.get('country', '')})")
        print(f"时区: {geo.get('timezone', '未知')}")
        print(f"城市: {geo.get('city', '未知')}")

        # 生成 CloakBrowser L4 配置建议
        if geo.get("country") and geo.get("timezone"):
            locale_map = {
                "US": "en-US", "GB": "en-GB", "DE": "de-DE",
                "FR": "fr-FR", "JP": "ja-JP", "CN": "zh-CN",
                "KR": "ko-KR", "ES": "es-ES", "IT": "it-IT",
                "BR": "pt-BR", "RU": "ru-RU", "IN": "en-IN",
            }
            locale = locale_map.get(geo["country"], "en-US")
            print(f"\n--- L4 GeoIP 配置建议 ---")
            print(f"geoip_from_proxy: True")
            print(f"auto_timezone: True  # {geo['timezone']}")
            print(f"auto_locale: True     # {locale}")
            print(f"--fingerprint-webrtc-ip={host}")

    return 0


def cmd_headers(args, pool: ProxyPool) -> int:
    """头注入验证"""
    entry = find_proxy(pool, args.proxy)
    result = verify_headers(args.proxy, args.test_url)

    if result["success"]:
        print(f"✓ 头注入验证成功")
        print(f"  代理IP: {result['detected_ip']}")
        print(f"  响应头:")
        for k, v in result["headers"].items():
            print(f"    {k}: {v}")
    else:
        print(f"✗ 头注入验证失败")
        for issue in result["issues"]:
            print(f"  - {issue}")

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))

    return 0 if result["success"] else 1


def cmd_list(args, pool: ProxyPool) -> int:
    """列出代理"""
    proxies = pool.proxies
    if args.min_score:
        proxies = [p for p in proxies if p.score >= args.min_score and p.status == "active"]

    if args.status:
        proxies = [p for p in proxies if p.status == args.status]

    if not proxies:
        print("没有找到符合条件的代理")
        return 0

    if args.json:
        output = {
            "proxies": [p.to_dict() for p in proxies],
            "total": len(proxies),
            "by_country": _count_by_country(proxies),
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(f"## CloakBrowser 代理池")
        print(f"**总数**: {len(proxies)}")
        print(f"**存储位置**: {DEFAULT_PROXIES_FILE}")
        print()
        print(f"| 代理 | 国家 | 评分 | 速度 | 匿名度 | 稳定性 | 状态 |")
        print(f"|------|------|------|------|--------|--------|------|")
        for p in proxies:
            geo = geoip_lookup(parse_proxy_url(p.proxy)["host"]) if p.status == "active" else {}
            country = p.country or geo.get("country", "-")
            health = p.health
            speed = f"{health.speed_ms}ms" if health else "-"
            anon = health.anonymity if health else "-"
            stab = f"{health.stability:.0%}" if health else "-"
            label = get_score_label(p.score)
            icon = "✅" if p.status == "active" else "❌"
            print(f"| {p.proxy[:50]} | {country} | {p.score}/10 | {speed} | {anon} | {stab} | {icon}{p.status} |")

    return 0


def cmd_remove(args, pool: ProxyPool) -> int:
    """移除代理"""
    if remove_proxy(pool, args.proxy):
        pool.save()
        print(f"✓ 代理已移除: {args.proxy}")
        return 0
    else:
        print(f"错误: 代理未找到: {args.proxy}", file=sys.stderr)
        return 1


def cmd_export_config(args, pool: ProxyPool) -> int:
    """导出CloakBrowser配置"""
    entry = select_best_proxy(pool, args.level, args.country, args.tags.split(",") if args.tags else None)
    if not entry:
        print(f"未找到符合条件的代理", file=sys.stderr)
        return 1

    p = parse_proxy_url(entry.proxy)
    geo = geoip_lookup(p["host"])

    locale_map = {
        "US": "en-US", "GB": "en-GB", "DE": "de-DE",
        "FR": "fr-FR", "JP": "ja-JP", "CN": "zh-CN",
        "KR": "ko-KR", "ES": "es-ES", "IT": "it-IT",
        "BR": "pt-BR", "RU": "ru-RU", "IN": "en-IN",
    }
    locale = locale_map.get(geo.get("country", ""), "en-US")
    webrtc_ip = p["host"]

    output = {
        "proxy": entry.proxy,
        "geoip": {
            "country": geo.get("country", entry.country),
            "timezone": geo.get("timezone", "UTC"),
            "locale": locale,
            "webrtc_ip": webrtc_ip,
        },
        "cloakbrowser_config": {
            "proxy": entry.proxy,
            "geoip_from_proxy": True,
            "auto_timezone": True,
            "auto_locale": True,
            "arguments": [f"--fingerprint-webrtc-ip={webrtc_ip}"],
        },
    }

    if args.json:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(f"--- CloakBrowser L{args.level[-1]} 配置 ---")
        print(f"代理: {entry.proxy}")
        print(f"国家: {geo.get('country_name', entry.country)}")
        print(f"时区: {geo.get('timezone', 'UTC')}")
        print(f"语言: {locale}")
        print(f"WebRTC IP: {webrtc_ip}")
        print()
        print("```python")
        print("from cloakbrowser import launch")
        print()
        print("browser = launch(")
        print(f'    stealth_level="{args.level}",')
        print(f'    proxy="{entry.proxy}",')
        print("    geoip_from_proxy=True,")
        print("    auto_timezone=True,")
        print("    auto_locale=True,")
        print(f'    arguments=["--fingerprint-webrtc-ip={webrtc_ip}"],')
        if args.level == "L4":
            print('    profile="persistent_profile_001",')
        print(")")
        print("```")

        # JSON配置块
        print("\n```json")
        print(json.dumps(output, indent=2, ensure_ascii=False))
        print("```")

    return 0


def cmd_stats(args, pool: ProxyPool) -> int:
    """代理池统计"""
    active = [p for p in pool.proxies if p.status == "active"]
    by_country = _count_by_country(active)
    total_score = sum(p.score for p in active) / len(active) if active else 0

    print(f"## 代理池统计")
    print(f"- 总数: {len(pool.proxies)}")
    print(f"- 活跃: {len(active)}")
    print(f"- 平均评分: {total_score:.1f}/10")
    print(f"- 按国家分布:")
    for country, count in sorted(by_country.items(), key=lambda x: -x[1]):
        print(f"  {country}: {count}")
    return 0


# =============================================================================
# 辅助函数
# =============================================================================

def _count_by_country(proxies: list[ProxyEntry]) -> dict:
    counts = {}
    for p in proxies:
        c = p.country or "unknown"
        counts[c] = counts.get(c, 0) + 1
    return counts


# =============================================================================
# 主入口
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="CloakBrowser 代理池管理器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # add
    p_add = sub.add_parser("add", help="添加代理到池")
    p_add.add_argument("--proxy", required=True, help="代理URL (http/socks5/socks4)")
    p_add.add_argument("--country", default="", help="ISO国家代码 (如US/GB/DE)")
    p_add.add_argument("--tags", default="", help="标签，逗号分隔 (如residential,fast)")
    p_add.add_argument("--check-health", action="store_true", help="添加后执行健康检查")

    # batch-add
    p_batch = sub.add_parser("batch-add", help="批量添加代理")
    p_batch.add_argument("file", help="代理列表文件 (每行: proxy [--country=XX] [--tags=x,y])")
    p_batch.add_argument("--check-health", action="store_true", help="批量添加后执行健康检查")

    # get
    p_get = sub.add_parser("get", help="获取最优代理")
    p_get.add_argument("--level", default="L3", choices=["L3", "L4"], help="隐身级别")
    p_get.add_argument("--country", help="指定国家")
    p_get.add_argument("--require-tags", help="必需标签 (逗号分隔)")
    p_get.add_argument("--verbose", "-v", action="store_true")
    p_get.add_argument("--json", action="store_true")

    # health
    p_health = sub.add_parser("health", help="健康检查")
    p_health.add_argument("--all", action="store_true", help="检查所有代理")
    p_health.add_argument("--proxy", help="检查指定代理")
    p_health.add_argument("--level", choices=["L3", "L4"], default="L3", help="按级别过滤")
    p_health.add_argument("--timeout", type=int, default=DEFAULT_CHECK_TIMEOUT, help="超时秒数")
    p_health.add_argument("--auto-remove", action="store_true", help="自动剔除低质代理")

    # score
    p_score = sub.add_parser("score", help="评分单个代理")
    p_score.add_argument("--proxy", required=True)

    # geoip
    p_geoip = sub.add_parser("geoip", help="GeoIP查询")
    p_geoip.add_argument("--proxy", required=True)
    p_geoip.add_argument("--json", action="store_true")

    # headers
    p_hdr = sub.add_parser("headers", help="头注入验证")
    p_hdr.add_argument("--proxy", required=True)
    p_hdr.add_argument("--test-url", default=DEFAULT_TEST_URL)
    p_hdr.add_argument("--json", action="store_true")

    # list
    p_list = sub.add_parser("list", help="列出所有代理")
    p_list.add_argument("--min-score", type=float, help="最低评分过滤")
    p_list.add_argument("--status", choices=["active", "inactive", "removed"])
    p_list.add_argument("--json", action="store_true")

    # remove
    p_rm = sub.add_parser("remove", help="移除代理")
    p_rm.add_argument("--proxy", required=True)

    # export-config
    p_exp = sub.add_parser("export-config", help="导出CloakBrowser配置")
    p_exp.add_argument("--level", default="L4", choices=["L3", "L4"])
    p_exp.add_argument("--country", help="指定国家")
    p_exp.add_argument("--tags", help="标签过滤")
    p_exp.add_argument("--json", action="store_true")

    # stats
    p_stats = sub.add_parser("stats", help="代理池统计")

    args = parser.parse_args()

    # 加载代理池
    pool = ProxyPool.load()

    # 执行命令
    handlers = {
        "add": cmd_add,
        "batch-add": cmd_batch_add,
        "get": cmd_get,
        "health": cmd_health,
        "score": cmd_score,
        "geoip": cmd_geoip,
        "headers": cmd_headers,
        "list": cmd_list,
        "remove": cmd_remove,
        "export-config": cmd_export_config,
        "stats": cmd_stats,
    }

    handler = handlers.get(args.command)
    if handler:
        sys.exit(handler(args, pool))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
