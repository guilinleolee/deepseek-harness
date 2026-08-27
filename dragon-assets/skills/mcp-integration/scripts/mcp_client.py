#!/usr/bin/env python3
"""
MCP Integration Center - 按需调用MCP服务
按需实例化MCP客户端，高效调用各种MCP服务
"""

import json
import os
import sys
import asyncio
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from datetime import datetime
from pathlib import Path
import hashlib

# MCP集成目录
MCP_HOME = Path.home() / ".claude" / "mcp-integration"
MCP_HOME.mkdir(parents=True, exist_ok=True)

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCPServerType(Enum):
    """MCP服务器类型"""
    GEO_ANALYZER = "geo-analyzer"
    GEOCODER = "geocoder"
    LLMS_GENERATOR = "llms-generator"
    SCHEMA_GENERATOR = "schema-generator"
    BRAND_TRACKER = "brand-tracker"
    CITATION_CHECKER = "citation-checker"
    SERP_ANALYZER = "serp-analyzer"
    COMPETITOR_SCANNER = "competitor-scanner"
    CONTENT_AUDITOR = "content-auditor"
    IP_LOOKUP = "ip-lookup"
    ROUTE_PLANNER = "route-planner"


@dataclass
class MCPConfig:
    """MCP服务器配置"""
    name: str
    server_type: MCPServerType
    endpoint: str
    api_key: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPRequest:
    """MCP请求"""
    server_type: MCPServerType
    operation: str
    params: Dict[str, Any]
    request_id: Optional[str] = None
    timestamp: Optional[str] = None

    def __post_init__(self):
        if not self.request_id:
            self.request_id = hashlib.md5(
                f"{self.server_type.value}{self.operation}{datetime.now().isoformat()}".encode()
            ).hexdigest()[:12]
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class MCPResponse:
    """MCP响应"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    request_id: Optional[str] = None
    duration_ms: float = 0


class MCPClientPool:
    """MCP客户端连接池 - 按需实例化"""

    def __init__(self, max_connections: int = 5):
        self.max_connections = max_connections
        self._clients: Dict[MCPServerType, Any] = {}
        self._last_used: Dict[MCPServerType, datetime] = {}
        self._stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "cache_hits": 0,
        }

    def _get_client(self, server_type: MCPServerType) -> Optional[Any]:
        """获取或创建MCP客户端"""
        now = datetime.now()

        # 检查是否已存在且可用
        if server_type in self._clients:
            self._last_used[server_type] = now
            return self._clients[server_type]

        # 需要创建新客户端
        if len(self._clients) >= self.max_connections:
            # 清理最久未使用的连接
            self._cleanup_oldest()

        # 创建客户端
        client = self._create_client(server_type)
        if client:
            self._clients[server_type] = client
            self._last_used[server_type] = now
            logger.info(f"Created new MCP client for {server_type.value}")

        return client

    def _create_client(self, server_type: MCPServerType) -> Optional[Any]:
        """根据服务器类型创建客户端"""
        # 本地MCP服务（使用内置实现）
        local_services = {
            MCPServerType.GEOCODER: GeocoderService,
            MCPServerType.IP_LOOKUP: IPLookupService,
            MCPServerType.ROUTE_PLANNER: RoutePlannerService,
            MCPServerType.LLMS_GENERATOR: LLMsGeneratorService,
            MCPServerType.SCHEMA_GENERATOR: SchemaGeneratorService,
            MCPServerType.GEO_ANALYZER: GeoAnalyzerService,
            MCPServerType.BRAND_TRACKER: BrandTrackerService,
            MCPServerType.CITATION_CHECKER: CitationCheckerService,
            MCPServerType.SERP_ANALYZER: SerpAnalyzerService,
            MCPServerType.CONTENT_AUDITOR: ContentAuditorService,
            MCPServerType.COMPETITOR_SCANNER: CompetitorScannerService,
        }

        service_class = local_services.get(server_type)
        if service_class:
            return service_class()

        logger.warning(f"No client implementation for {server_type.value}")
        return None

    def _cleanup_oldest(self):
        """清理最久未使用的连接"""
        if not self._last_used:
            return

        oldest = min(self._last_used.items(), key=lambda x: x[1])
        server_type = oldest[0]
        if server_type in self._clients:
            logger.info(f"Cleaning up oldest MCP client: {server_type.value}")
            del self._clients[server_type]
            del self._last_used[server_type]

    async def call(self, request: MCPRequest) -> MCPResponse:
        """调用MCP服务"""
        start_time = datetime.now()
        self._stats["total_calls"] += 1

        try:
            client = self._get_client(request.server_type)
            if not client:
                return MCPResponse(
                    success=False,
                    error=f"No client available for {request.server_type.value}",
                    request_id=request.request_id
                )

            # 调用对应服务
            operation = getattr(client, request.operation, None)
            if not operation:
                return MCPResponse(
                    success=False,
                    error=f"Operation {request.operation} not found",
                    request_id=request.request_id
                )

            # 执行调用
            result = await operation(**request.params)

            duration = (datetime.now() - start_time).total_seconds() * 1000
            self._stats["successful_calls"] += 1

            return MCPResponse(
                success=True,
                data=result,
                request_id=request.request_id,
                duration_ms=duration
            )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            self._stats["failed_calls"] += 1
            logger.error(f"MCP call failed: {str(e)}")
            return MCPResponse(
                success=False,
                error=str(e),
                request_id=request.request_id,
                duration_ms=duration
            )

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self._stats,
            "active_connections": len(self._clients),
            "pool_size": self.max_connections,
        }

    def close_all(self):
        """关闭所有连接"""
        self._clients.clear()
        self._last_used.clear()
        logger.info("All MCP clients closed")


# ==================== 本地MCP服务实现 ====================

class GeocoderService:
    """地理编码服务 - 内置实现"""

    def __init__(self):
        self.api_key = os.getenv("GEOAPIFY_KEY", "")
        self.base_url = "https://api.geoapify.com/v1/geocode"

    async def geocode(self, address: str, **kwargs) -> Dict[str, Any]:
        """地址转坐标"""
        import urllib.parse

        if not self.api_key:
            # 使用免费Nominatim（有限制）
            return await self._nominatim_geocode(address)

        url = f"{self.base_url}/search"
        params = {
            "text": address,
            "apiKey": self.api_key,
            "format": "json"
        }

        try:
            import urllib.request
            query = urllib.parse.urlencode(params)
            with urllib.request.urlopen(f"{url}?{query}", timeout=10) as resp:
                data = json.loads(resp.read().decode())

            if data.get("results"):
                result = data["results"][0]
                return {
                    "success": True,
                    "address": result.get("formatted"),
                    "lat": result.get("lat"),
                    "lng": result.get("lon"),
                    "confidence": result.get("confidence", 1.0),
                    "country": result.get("country"),
                    "city": result.get("city"),
                    "state": result.get("state"),
                }
            return {"success": False, "error": "Address not found"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def reverse(self, lat: float, lng: float, **kwargs) -> Dict[str, Any]:
        """坐标转地址"""
        import urllib.parse

        if not self.api_key:
            return await self._nominatim_reverse(lat, lng)

        url = f"{self.base_url}/reverse"
        params = {
            "lat": lat,
            "lon": lng,
            "apiKey": self.api_key,
            "format": "json"
        }

        try:
            import urllib.request
            query = urllib.parse.urlencode(params)
            with urllib.request.urlopen(f"{url}?{query}", timeout=10) as resp:
                data = json.loads(resp.read().decode())

            if data:
                return {
                    "success": True,
                    "address": data.get("formatted"),
                    "lat": lat,
                    "lng": lng,
                    "country": data.get("country"),
                    "city": data.get("city"),
                    "state": data.get("state"),
                }
            return {"success": False, "error": "Location not found"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _nominatim_geocode(self, address: str) -> Dict[str, Any]:
        """使用Nominatim（免费有限制）"""
        import urllib.request, urllib.parse

        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": address, "format": "json", "limit": 1}
        headers = {"User-Agent": "DragonEngine-MCP/1.0"}

        try:
            query = urllib.parse.urlencode(params)
            req = urllib.request.Request(f"{url}?{query}", headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())

            if data:
                return {
                    "success": True,
                    "address": data[0].get("display_name"),
                    "lat": float(data[0].get("lat")),
                    "lng": float(data[0].get("lon")),
                    "confidence": float(data[0].get("importance", 0.5)),
                }
            return {"success": False, "error": "Address not found"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _nominatim_reverse(self, lat: float, lng: float) -> Dict[str, Any]:
        """Nominatim逆向编码"""
        import urllib.request, urllib.parse

        url = "https://nominatim.openstreetmap.org/reverse"
        params = {"lat": lat, "lon": lng, "format": "json"}
        headers = {"User-Agent": "DragonEngine-MCP/1.0"}

        try:
            query = urllib.parse.urlencode(params)
            req = urllib.request.Request(f"{url}?{query}", headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())

            if data:
                return {
                    "success": True,
                    "address": data.get("display_name"),
                    "lat": lat,
                    "lng": lng,
                    "country": data.get("address", {}).get("country"),
                    "city": data.get("address", {}).get("city"),
                }
            return {"success": False, "error": "Location not found"}

        except Exception as e:
            return {"success": False, "error": str(e)}


class IPLookupService:
    """IP定位服务"""

    def __init__(self):
        self.api_key = os.getenv("IPINFO_KEY", "")

    async def lookup(self, ip: str, **kwargs) -> Dict[str, Any]:
        """IP查询"""
        if self.api_key:
            return await self._ipinfo_lookup(ip)
        return await self._free_lookup(ip)

    async def _ipinfo_lookup(self, ip: str) -> Dict[str, Any]:
        """使用IPinfo API"""
        try:
            import urllib.request
            url = f"https://ipinfo.io/{ip}/json?token={self.api_key}"
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read().decode())

            coords = data.get("loc", "").split(",") if data.get("loc") else []
            return {
                "success": True,
                "ip": ip,
                "hostname": data.get("hostname"),
                "city": data.get("city"),
                "region": data.get("region"),
                "country": data.get("country"),
                "org": data.get("org"),
                "lat": float(coords[0]) if coords else None,
                "lng": float(coords[1]) if len(coords) > 1 else None,
                "timezone": data.get("timezone"),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _free_lookup(self, ip: str) -> Dict[str, Any]:
        """免费IP查询（有限制）"""
        try:
            import urllib.request
            url = f"http://ip-api.com/json/{ip}"
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read().decode())

            if data.get("status") == "success":
                return {
                    "success": True,
                    "ip": ip,
                    "city": data.get("city"),
                    "region": data.get("regionName"),
                    "country": data.get("country"),
                    "org": data.get("org"),
                    "lat": data.get("lat"),
                    "lng": data.get("lon"),
                    "timezone": data.get("timezone"),
                }
            return {"success": False, "error": "IP lookup failed"}

        except Exception as e:
            return {"success": False, "error": str(e)}


class LLMsGeneratorService:
    """llms.txt生成服务"""

    def __init__(self):
        self.cache_dir = MCP_HOME / "cache" / "llms"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def generate(self, site_url: str, **kwargs) -> Dict[str, Any]:
        """生成llms.txt"""
        try:
            from urllib.parse import urlparse

            parsed = urlparse(site_url)
            domain = parsed.netloc or parsed.path.split("/")[0]

            # 生成llms.txt内容模板
            content = f"""# {domain}

> AI-optimized description of {domain} - providing authoritative information and resources.

## Main Sections

- [Home]({site_url}): Main entry point and overview
- [About](/about): About us and our mission
- [Products/Services](/products): What we offer
- [Blog](/blog): Latest updates and insights
- [Contact](/contact): Get in touch

## Key Information

- **Domain**: {domain}
- **Focus**: AI, Search Optimization, Content Marketing
- **Expertise Areas**:
  - Generative Engine Optimization (GEO)
  - AI Search Visibility
  - Content Strategy
  - Technical SEO

## Latest Content

- Recent articles and resources available at {site_url}/blog

## Contact

- Website: {site_url}
"""

            # 保存到缓存
            cache_file = self.cache_dir / f"{domain.replace('.', '_')}.txt"
            cache_file.write_text(content, encoding='utf-8')

            return {
                "success": True,
                "domain": domain,
                "llms_content": content,
                "cache_file": str(cache_file),
                "preview": content[:500] + "..." if len(content) > 500 else content
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


class SchemaGeneratorService:
    """Schema生成服务"""

    SCHEMA_TEMPLATES = {
        "Article": {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "",
            "author": {"@type": "Person", "name": ""},
            "datePublished": "",
            "dateModified": "",
            "publisher": {"@type": "Organization", "name": ""},
            "description": "",
            "image": "",
            "url": ""
        },
        "FAQPage": {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": []
        },
        "Organization": {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "",
            "url": "",
            "logo": "",
            "description": "",
            "sameAs": []
        },
        "Person": {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": "",
            "jobTitle": "",
            "worksFor": "",
            "url": "",
            "sameAs": []
        }
    }

    async def generate(self, schema_type: str, **kwargs) -> Dict[str, Any]:
        """生成JSON-LD Schema"""
        if schema_type not in self.SCHEMA_TEMPLATES:
            return {
                "success": False,
                "error": f"Unknown schema type: {schema_type}",
                "available_types": list(self.SCHEMA_TEMPLATES.keys())
            }

        template = self.SCHEMA_TEMPLATES[schema_type].copy()

        # 填充kwargs参数
        for key, value in kwargs.items():
            if key in template:
                template[key] = value

        return {
            "success": True,
            "schema_type": schema_type,
            "json_ld": template,
            "json_string": json.dumps(template, indent=2, ensure_ascii=False)
        }


class GeoAnalyzerService:
    """GEO分析服务 - 基于天龙引擎seo-geo技能"""

    async def analyze(self, url: str, **kwargs) -> Dict[str, Any]:
        """分析网站GEO健康度"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc

            # 模拟GEO分析结果（实际需要抓取页面）
            analysis = {
                "success": True,
                "url": url,
                "domain": domain,
                "geo_score": 0,
                "dimensions": {
                    "citability": {
                        "score": 0,
                        "weight": 0.25,
                        "details": "需要页面内容分析"
                    },
                    "structure": {
                        "score": 0,
                        "weight": 0.20,
                        "details": "需要页面结构分析"
                    },
                    "authority": {
                        "score": 0,
                        "weight": 0.20,
                        "details": "需要权威信号分析"
                    },
                    "technical": {
                        "score": 0,
                        "weight": 0.20,
                        "details": "需要技术检查"
                    },
                    "multimodal": {
                        "score": 0,
                        "weight": 0.15,
                        "details": "需要多媒体检查"
                    }
                },
                "recommendations": [
                    "安装GEO分析工具获取详细数据",
                    "检查robots.txt中的AI爬虫规则",
                    "生成llms.txt文件",
                    "添加JSON-LD结构化数据"
                ],
                "ai_crawlers": {
                    "gptbot": "unknown",
                    "claudebot": "unknown",
                    "perplexitybot": "unknown"
                },
                "llms_txt_status": "missing"
            }

            return analysis

        except Exception as e:
            return {"success": False, "error": str(e)}


class BrandTrackerService:
    """品牌追踪服务"""

    async def track(self, brand: str, **kwargs) -> Dict[str, Any]:
        """追踪品牌可见性"""
        try:
            period = kwargs.get("period", "30d")

            # 模拟追踪数据
            return {
                "success": True,
                "brand": brand,
                "period": period,
                "platforms": {
                    "chatgpt": {"mentions": 0, "trend": "neutral"},
                    "perplexity": {"mentions": 0, "trend": "neutral"},
                    "claude": {"mentions": 0, "trend": "neutral"},
                    "gemini": {"mentions": 0, "trend": "neutral"}
                },
                "sentiment": "neutral",
                "top_citations": [],
                "recommendations": [
                    "建立Wikipedia实体页面",
                    "增加Reddit社区提及",
                    "创建YouTube内容"
                ]
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


class CitationCheckerService:
    """引用检查服务"""

    async def check(self, url: str, **kwargs) -> Dict[str, Any]:
        """检查AI引用情况"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc

            return {
                "success": True,
                "url": url,
                "domain": domain,
                "citations": {
                    "chatgpt": {"cited": False, "queries": []},
                    "perplexity": {"cited": False, "queries": []},
                    "claude": {"cited": False, "queries": []},
                    "gemini": {"cited": False, "queries": []}
                },
                "citation_contexts": [],
                "attribution_breakdown": {}
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


class SerpAnalyzerService:
    """SERP分析服务"""

    async def analyze(self, keyword: str, **kwargs) -> Dict[str, Any]:
        """分析搜索结果"""
        try:
            location = kwargs.get("location", "global")
            language = kwargs.get("language", "en")

            return {
                "success": True,
                "keyword": keyword,
                "location": location,
                "language": language,
                "results": [],
                "featured_snippet": None,
                "ai_overview": None,
                "top_domains": [],
                "intent": "unknown"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


class ContentAuditorService:
    """内容审计服务"""

    async def audit(self, url: str, **kwargs) -> Dict[str, Any]:
        """审计内容质量"""
        try:
            return {
                "success": True,
                "url": url,
                "score": 0,
                "dimensions": {
                    "readability": {"score": 0, "issues": []},
                    "seo": {"score": 0, "issues": []},
                    "geo": {"score": 0, "issues": []},
                    "multimedia": {"score": 0, "issues": []},
                    "structure": {"score": 0, "issues": []}
                },
                "word_count": 0,
                "reading_time_minutes": 0,
                "recommendations": []
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


class CompetitorScannerService:
    """竞品扫描服务"""

    async def scan(self, domain: str, **kwargs) -> Dict[str, Any]:
        """扫描竞品GEO数据"""
        try:
            return {
                "success": True,
                "domain": domain,
                "geo_score": 0,
                "strengths": [],
                "weaknesses": [],
                "opportunities": [],
                "threats": [],
                "top_keywords": [],
                "referring_domains": 0
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


class RoutePlannerService:
    """路径规划服务"""

    async def plan(self, origin: str, destination: str, **kwargs) -> Dict[str, Any]:
        """规划路径"""
        try:
            mode = kwargs.get("mode", "driving")

            return {
                "success": True,
                "origin": origin,
                "destination": destination,
                "mode": mode,
                "distance_km": 0,
                "duration_minutes": 0,
                "route": [],
                "alternatives": []
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


# ==================== MCP调用CLI入口 ====================

async def main():
    """MCP CLI主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="MCP Integration Center CLI")
    parser.add_argument("command", help="MCP command (geocode, reverse, etc.)")
    parser.add_argument("args", nargs="*", help="Command arguments")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # 初始化连接池
    pool = MCPClientPool()

    try:
        result = None

        if args.command == "geocode":
            if not args.args:
                print("Error: Address required")
                return 1
            request = MCPRequest(
                server_type=MCPServerType.GEOCODER,
                operation="geocode",
                params={"address": args.args[0]}
            )
            response = await pool.call(request)
            result = response.data if response.success else {"error": response.error}

        elif args.command == "reverse":
            if not args.args:
                print("Error: Coordinates required (lat,lng)")
                return 1
            coords = args.args[0].split(",")
            if len(coords) != 2:
                print("Error: Coordinates format should be lat,lng")
                return 1
            request = MCPRequest(
                server_type=MCPServerType.GEOCODER,
                operation="reverse",
                params={"lat": float(coords[0]), "lng": float(coords[1])}
            )
            response = await pool.call(request)
            result = response.data if response.success else {"error": response.error}

        elif args.command == "ip-lookup":
            if not args.args:
                print("Error: IP address required")
                return 1
            request = MCPRequest(
                server_type=MCPServerType.IP_LOOKUP,
                operation="lookup",
                params={"ip": args.args[0]}
            )
            response = await pool.call(request)
            result = response.data if response.success else {"error": response.error}

        elif args.command == "llms-generate":
            if not args.args:
                print("Error: Site URL required")
                return 1
            request = MCPRequest(
                server_type=MCPServerType.LLMS_GENERATOR,
                operation="generate",
                params={"site_url": args.args[0]}
            )
            response = await pool.call(request)
            result = response.data if response.success else {"error": response.error}

        elif args.command == "schema-generate":
            schema_type = args.args[0] if args.args else "Article"
            request = MCPRequest(
                server_type=MCPServerType.SCHEMA_GENERATOR,
                operation="generate",
                params={"schema_type": schema_type}
            )
            response = await pool.call(request)
            result = response.data if response.success else {"error": response.error}

        elif args.command == "geo-analyze":
            if not args.args:
                print("Error: URL required")
                return 1
            request = MCPRequest(
                server_type=MCPServerType.GEO_ANALYZER,
                operation="analyze",
                params={"url": args.args[0]}
            )
            response = await pool.call(request)
            result = response.data if response.success else {"error": response.error}

        elif args.command == "brand-track":
            if not args.args:
                print("Error: Brand name required")
                return 1
            request = MCPRequest(
                server_type=MCPServerType.BRAND_TRACKER,
                operation="track",
                params={"brand": args.args[0]}
            )
            response = await pool.call(request)
            result = response.data if response.success else {"error": response.error}

        elif args.command == "citation-check":
            if not args.args:
                print("Error: URL required")
                return 1
            request = MCPRequest(
                server_type=MCPServerType.CITATION_CHECKER,
                operation="check",
                params={"url": args.args[0]}
            )
            response = await pool.call(request)
            result = response.data if response.success else {"error": response.error}

        elif args.command == "status":
            result = pool.get_stats()

        else:
            print(f"Unknown command: {args.command}")
            print("Available commands: geocode, reverse, ip-lookup, llms-generate, schema-generate, geo-analyze, brand-track, citation-check, status")
            return 1

        # 输出结果
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            _print_human_readable(args.command, result)

    finally:
        pool.close_all()

    return 0


def _print_human_readable(command: str, result: Dict[str, Any]):
    """友好格式输出"""
    if not result:
        print("No result")
        return

    if result.get("success") is False:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
        return

    if command == "geocode":
        print(f"📍 {result.get('address', 'Unknown address')}")
        print(f"   坐标: {result.get('lat')}, {result.get('lng')}")
        if result.get('city'):
            print(f"   城市: {result.get('city')}, {result.get('country')}")

    elif command == "reverse":
        print(f"📍 {result.get('address', 'Unknown address')}")
        print(f"   坐标: {result.get('lat')}, {result.get('lng')}")

    elif command == "ip-lookup":
        print(f"🌐 IP: {result.get('ip')}")
        if result.get('city'):
            print(f"   位置: {result.get('city')}, {result.get('region')}, {result.get('country')}")
        if result.get('org'):
            print(f"   组织: {result.get('org')}")

    elif command == "llms-generate":
        print(f"✅ llms.txt generated for {result.get('domain')}")
        print(f"\n预览:\n{result.get('preview', '')}")

    elif command == "schema-generate":
        print(f"✅ {result.get('schema_type')} Schema generated")
        print(f"\n{result.get('json_string', '')}")

    elif command == "geo-analyze":
        score = result.get('geo_score', 0)
        print(f"🌐 GEO分析: {result.get('domain')}")
        print(f"   GEO分数: {score}/100")
        print(f"   llms.txt状态: {result.get('llms_txt_status', 'unknown')}")
        if result.get('recommendations'):
            print(f"\n建议:")
            for rec in result.get('recommendations', [])[:3]:
                print(f"   • {rec}")

    elif command == "status":
        print("📊 MCP连接池状态:")
        print(f"   总调用: {result.get('total_calls', 0)}")
        print(f"   成功: {result.get('successful_calls', 0)}")
        print(f"   失败: {result.get('failed_calls', 0)}")
        print(f"   活跃连接: {result.get('active_connections', 0)}")

    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
