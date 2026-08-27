#!/usr/bin/env python3
"""
Geocoding Free Tier Client - Geoapify + IPinfo 双冗余客户端
来源: 天龙引擎 V11.13 免费API替代方案
文档: skills/geocoding-free-tier/SKILL.md
"""

import os
import json
import time
import ipaddress
from typing import Optional, Literal
from dataclasses import dataclass
from urllib.parse import urlencode

try:
    import requests
except ImportError:
    print("请安装 requests: pip install requests")
    exit(1)


@dataclass
class GeoLocation:
    """地理位置数据结构"""
    lat: float
    lon: float
    formatted: str
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    postcode: Optional[str] = None
    confidence: Optional[float] = None
    source: str = "unknown"

    def to_dict(self) -> dict:
        return {
            "lat": self.lat,
            "lon": self.lon,
            "formatted": self.formatted,
            "address_line1": self.address_line1,
            "address_line2": self.address_line2,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "country_code": self.country_code,
            "postcode": self.postcode,
            "confidence": self.confidence,
            "source": self.source
        }


@dataclass
class IPLocation:
    """IP位置数据结构"""
    ip: str
    city: Optional[str]
    region: Optional[str]
    country: Optional[str]
    country_code: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    timezone: Optional[str]
    asn: Optional[str] = None
    org: Optional[str] = None
    isp: Optional[str] = None
    is_mobile: bool = False
    is_proxy: bool = False
    is_vpn: bool = False
    is_tor: bool = False
    is_hosting: bool = False

    def to_dict(self) -> dict:
        return {
            "ip": self.ip,
            "city": self.city,
            "region": self.region,
            "country": self.country,
            "country_code": self.country_code,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timezone": self.timezone,
            "asn": self.asn,
            "org": self.org,
            "isp": self.isp,
            "is_mobile": self.is_mobile,
            "is_proxy": self.is_proxy,
            "is_vpn": self.is_vpn,
            "is_tor": self.is_tor,
            "is_hosting": self.is_hosting
        }


@dataclass
class ASNInfo:
    """ASN信息数据结构"""
    asn: str
    name: str
    domain: Optional[str]
    route: str
    type: str
    description: Optional[str]
    source: str = "ipinfo"

    def to_dict(self) -> dict:
        return {
            "asn": self.asn,
            "name": self.name,
            "domain": self.domain,
            "route": self.route,
            "type": self.type,
            "description": self.description,
            "source": self.source
        }


class GeocodingError(Exception):
    """地理编码API异常"""
    pass


class GeocodingClient:
    """
    地理编码免费客户端 - Geoapify + IPinfo

    使用方式:
        client = GeocodingClient()  # 使用环境变量
        client = GeocodingClient(geoapify_key="xxx", ipinfo_key="xxx")  # 显式指定

    环境变量:
        GEOAPIFY_API_KEY: Geoapify API密钥 (https://myprojects.geoapify.com)
        IPINFO_API_KEY: IPinfo API密钥 (https://ipinfo.io)

    免费额度:
        Geoapify: 3000请求/天, 10000请求/月
        IPinfo: 50000请求/月 (基础), 200000请求/月 (高级)
    """

    GEOAPIFY_GEOCODING_URL = "https://api.geoapify.com/v1/geocode"
    GEOAPIFY_PLACES_URL = "https://api.geoapify.com/v2/places"
    IPINFO_URL = "https://ipinfo.io"

    def __init__(
        self,
        geoapify_key: Optional[str] = None,
        ipinfo_key: Optional[str] = None,
        use_cache: bool = True,
        cache_ttl: int = 3600  # 地理位置缓存1小时
    ):
        self.geoapify_key = geoapify_key or os.getenv("GEOAPIFY_API_KEY")
        self.ipinfo_key = ipinfo_key or os.getenv("IPINFO_API_KEY")
        self.use_cache = use_cache
        self.cache_ttl = cache_ttl
        self._cache = {}

        if not self.geoapify_key and not self.ipinfo_key:
            raise GeocodingError(
                "需要设置以下环境变量之一:\n"
                "  GEOAPIFY_API_KEY: Geoapify地理编码\n"
                "  IPINFO_API_KEY: IPinfo IP查询\n\n"
                "获取地址:\n"
                "  Geoapify: https://myprojects.geoapify.com/register\n"
                "  IPinfo: https://ipinfo.io/signup"
            )

    def _check_cache(self, key: str) -> Optional[dict]:
        """检查缓存"""
        if not self.use_cache:
            return None
        if key in self._cache:
            cached, timestamp = self._cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return cached
        return None

    def _set_cache(self, key: str, data: dict):
        """设置缓存"""
        if self.use_cache:
            self._cache[key] = (data, time.time())

    def geocode(
        self,
        address: str,
        country: Optional[str] = None,
        city: Optional[str] = None,
        limit: int = 1
    ) -> list[GeoLocation]:
        """
        地址转坐标 (Geoapify)

        参数:
            address: 地址字符串
            country: 限定国家 (如 "us", "cn", "gb")
            city: 限定城市
            limit: 返回结果数量

        返回:
            GeoLocation列表
        """
        if not self.geoapify_key:
            raise GeocodingError("需要GEOAPIFY_API_KEY来使用地理编码")

        cache_key = f"geocode_{address}_{country}_{city}_{limit}"
        cached = self._check_cache(cache_key)
        if cached:
            return [GeoLocation(**c) if isinstance(c, dict) else c for c in cached]

        params = {
            "text": address,
            "apiKey": self.geoapify_key,
            "limit": limit,
            "format": "json"
        }

        if country:
            params["filter"] = f"countrycode:{country}"
        if city:
            params["filter"] = f"city:{city}"

        try:
            resp = requests.get(
                self.GEOAPIFY_GEOCODING_URL,
                params=params,
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()

            results = []
            for item in data.get("results", []):
                results.append(GeoLocation(
                    lat=item.get("lat", 0),
                    lon=item.get("lon", 0),
                    formatted=item.get("formatted", ""),
                    address_line1=item.get("address_line1"),
                    address_line2=item.get("address_line2"),
                    city=item.get("city"),
                    state=item.get("state"),
                    country=item.get("country"),
                    country_code=item.get("country_code"),
                    postcode=item.get("postcode"),
                    confidence=item.get("rank", {}).get("confidence", 0) if isinstance(item.get("rank"), dict) else None,
                    source="geoapify"
                ))

            self._set_cache(cache_key, [r.to_dict() for r in results])
            return results

        except requests.RequestException as e:
            raise GeocodingError(f"Geoapify地理编码失败: {e}")

    def reverse_geocode(
        self,
        lat: float,
        lon: float,
        limit: int = 1
    ) -> list[GeoLocation]:
        """
        坐标转地址 (Geoapify)

        参数:
            lat: 纬度
            lon: 经度
            limit: 返回结果数量

        返回:
            GeoLocation列表
        """
        if not self.geoapify_key:
            raise GeocodingError("需要GEOAPIFY_API_KEY来使用地理编码")

        cache_key = f"reverse_{lat}_{lon}_{limit}"
        cached = self._check_cache(cache_key)
        if cached:
            return [GeoLocation(**c) if isinstance(c, dict) else c for c in cached]

        params = {
            "lat": lat,
            "lon": lon,
            "apiKey": self.geoapify_key,
            "limit": limit,
            "format": "json"
        }

        try:
            resp = requests.get(
                f"{self.GEOAPIFY_GEOCODING_URL}/reverse",
                params=params,
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()

            results = []
            for item in data.get("results", []):
                results.append(GeoLocation(
                    lat=item.get("lat", lat),
                    lon=item.get("lon", lon),
                    formatted=item.get("formatted", ""),
                    address_line1=item.get("address_line1"),
                    address_line2=item.get("address_line2"),
                    city=item.get("city"),
                    state=item.get("state"),
                    country=item.get("country"),
                    country_code=item.get("country_code"),
                    postcode=item.get("postcode"),
                    confidence=item.get("rank", {}).get("confidence", 0) if isinstance(item.get("rank"), dict) else None,
                    source="geoapify"
                ))

            self._set_cache(cache_key, [r.to_dict() for r in results])
            return results

        except requests.RequestException as e:
            raise GeocodingError(f"Geoapify逆地理编码失败: {e}")

    def search_places(
        self,
        query: str,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        radius: int = 5000,
        categories: Optional[list[str]] = None,
        limit: int = 20
    ) -> list[dict]:
        """
        搜索地点 (Geoapify Places)

        参数:
            query: 搜索查询
            lat, lon: 中心点坐标 (可选)
            radius: 搜索半径 (米)
            categories: 地点类别筛选 (如 ["catering.restaurant", "commercial.supermarket"])
            limit: 返回数量

        返回:
            地点列表
        """
        if not self.geoapify_key:
            raise GeocodingError("需要GEOAPIFY_API_KEY来搜索地点")

        cache_key = f"places_{query}_{lat}_{lon}_{radius}_{'-'.join(categories or []}_{limit}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached

        params = {
            "text": query,
            "apiKey": self.geoapify_key,
            "limit": limit
        }

        if lat is not None and lon is not None:
            params["filter"] = f"circle:{lon},{lat},{radius}"
            params["bias"] = f"proximity:{lon},{lat}"

        if categories:
            params["categories"] = ",".join(categories)

        try:
            resp = requests.get(
                self.GEOAPIFY_PLACES_URL,
                params=params,
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()

            results = []
            for feature in data.get("results", []):
                props = feature.get("properties", {})
                results.append({
                    "name": props.get("name"),
                    "address": props.get("formatted"),
                    "lat": feature.get("geometry", {}).get("coordinates", [None, None])[1],
                    "lon": feature.get("geometry", {}).get("coordinates", [None, None])[0],
                    "categories": props.get("categories"),
                    "distance": props.get("distance"),
                    "source": "geoapify"
                })

            self._set_cache(cache_key, results)
            return results

        except requests.RequestException as e:
            raise GeocodingError(f"Geoapify地点搜索失败: {e}")

    def ip_lookup(self, ip_address: Optional[str] = None) -> IPLocation:
        """
        IP位置查询 (IPinfo)

        参数:
            ip_address: IP地址 (空则查询本机IP)

        返回:
            IPLocation对象
        """
        if not self.ipinfo_key:
            raise GeocodingError("需要IPINFO_API_KEY来查询IP位置")

        cache_key = f"ip_{ip_address or 'self'}"
        cached = self._check_cache(cache_key)
        if cached:
            return IPLocation(**cached) if isinstance(cached, dict) else cached

        # 验证IP地址格式
        target_ip = ip_address
        if target_ip:
            try:
                ipaddress.ip_address(target_ip)
            except ValueError:
                raise GeocodingError(f"无效的IP地址: {target_ip}")

        url = f"{self.IPINFO_URL}/json"
        if target_ip:
            url = f"{self.IPINFO_URL}/{target_ip}"

        headers = {}
        if self.ipinfo_key:
            headers["Authorization"] = f"Bearer {self.ipinfo_key}"

        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            # 解析坐标
            loc = data.get("loc", "")
            lat, lon = None, None
            if loc:
                try:
                    lat, lon = map(float, loc.split(","))
                except (ValueError, AttributeError):
                    pass

            # 解析ASN数据
            asn_data = data.get("asn", {}) if isinstance(data.get("asn"), dict) else {}

            # 解析托管/VPN标识
            hostname = data.get("hostname", "")
            privacy = data.get("privacy", {}) if isinstance(data.get("privacy"), dict) else {}
            hosting = data.get("hosting", {}) if isinstance(data.get("hosting"), dict) else {}
            proxy = data.get("proxy", {}) if isinstance(data.get("proxy"), dict) else {}
            tor = data.get("tor", {}) if isinstance(data.get("tor"), dict) else {}
            isp_data = data.get("isp", "") if isinstance(data.get("isp"), str) else ""
            org_data = data.get("org", "") if isinstance(data.get("org"), str) else ""

            location = IPLocation(
                ip=data.get("ip", ip_address or ""),
                city=data.get("city"),
                region=data.get("region"),
                country=data.get("country"),
                country_code=data.get("country_code"),
                latitude=lat,
                longitude=lon,
                timezone=data.get("timezone"),
                asn=asn_data.get("asn") if asn_data else None,
                org=org_data,
                isp=isp_data,
                is_mobile=bool(data.get("mobile", False)),
                is_proxy=bool(proxy.get("proxy", False)),
                is_vpn=bool(privacy.get("vpn", False)),
                is_tor=bool(tor.get("tor", False)),
                is_hosting=bool(hosting.get("hosting", False) or privacy.get("hosting", False))
            )

            # IPinfo免费版可能缺少ASN和隐私数据
            if not location.asn:
                location.asn = data.get("asn", "")

            self._set_cache(cache_key, location.to_dict())
            return location

        except requests.RequestException as e:
            raise GeocodingError(f"IPinfo查询失败: {e}")

    def ip_lookup_full(self, ip_address: str) -> dict:
        """
        IP完整信息查询 (IPinfo, 需要token)

        返回完整的ASN、隐私、托管等信息
        """
        if not self.ipinfo_key:
            raise GeocodingError("需要IPINFO_API_KEY来获取完整IP信息")

        cache_key = f"ip_full_{ip_address}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached

        headers = {"Authorization"] = f"Bearer {self.ipinfo_key}"}

        try:
            # 并行请求多个API
            base_url = f"{self.IPINFO_URL}/{ip_address}"
            batch_url = f"{self.IPINFO_URL}/batch"

            # 主信息
            resp = requests.get(base_url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            results = data

            # 尝试获取ASN信息
            try:
                asn_resp = requests.get(f"{base_url}/asn", headers=headers, timeout=10)
                if asn_resp.ok:
                    results["asn_details"] = asn_resp.json()
            except requests.RequestException:
                pass

            # 尝试获取隐私信息
            try:
                privacy_resp = requests.get(f"{base_url}/privacy", headers=headers, timeout=10)
                if privacy_resp.ok:
                    results["privacy_details"] = privacy_resp.json()
            except requests.RequestException:
                pass

            # 尝试获取Hostname信息
            try:
                hostname_resp = requests.get(f"{base_url}/hostname", headers=headers, timeout=10)
                if hostname_resp.ok:
                    results["hostname_details"] = hostname_resp.json()
            except requests.RequestException:
                pass

            self._set_cache(cache_key, results)
            return results

        except requests.RequestException as e:
            raise GeocodingError(f"IPinfo完整查询失败: {e}")

    def asn_lookup(self, asn: str) -> ASNInfo:
        """
        ASN信息查询 (IPinfo)

        参数:
            asn: ASN编号 (如 "AS15169", "15169", "AS1")

        返回:
            ASNInfo对象
        """
        if not self.ipinfo_key:
            raise GeocodingError("需要IPINFO_API_KEY来查询ASN信息")

        # 标准化ASN格式
        if not asn.upper().startswith("AS"):
            asn = f"AS{asn}"

        cache_key = f"asn_{asn}"
        cached = self._check_cache(cache_key)
        if cached:
            return ASNInfo(**cached) if isinstance(cached, dict) else cached

        headers = {"Authorization"] = f"Bearer {self.ipinfo_key}"}

        try:
            resp = requests.get(
                f"{self.IPINFO_URL}/asn/{asn}",
                headers=headers,
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()

            asn_info = ASNInfo(
                asn=data.get("asn", asn),
                name=data.get("name", ""),
                domain=data.get("domain"),
                route=data.get("route", ""),
                type=data.get("type", ""),
                description=data.get("description"),
                source="ipinfo"
            )

            self._set_cache(cache_key, asn_info.to_dict())
            return asn_info

        except requests.RequestException as e:
            raise GeocodingError(f"ASN查询失败: {e}")

    def distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        计算两点间距离 (Haversine公式)

        参数:
            lat1, lon1: 第一个点坐标
            lat2, lon2: 第二个点坐标

        返回:
            距离(公里)
        """
        import math

        R = 6371  # 地球半径(公里)

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def to_json(self, data) -> str:
        """转换为JSON格式"""
        if isinstance(data, list):
            return json.dumps([item.to_dict() for item in data], ensure_ascii=False, indent=2)
        return json.dumps(data.to_dict() if hasattr(data, 'to_dict') else data, ensure_ascii=False, indent=2)


def main():
    """CLI入口"""
    import argparse

    parser = argparse.ArgumentParser(description="地理编码客户端 - Geoapify + IPinfo")
    parser.add_argument("--geocode", "-g", help="地址转坐标")
    parser.add_argument("--reverse", "-r", help="坐标转地址 (lat,lon)")
    parser.add_argument("--ip", "-i", help="IP查询 (空则查询本机)")
    parser.add_argument("--asn", help="ASN查询 (AS号)")
    parser.add_argument("--search-places", "-p", help="搜索地点")
    parser.add_argument("--country", "-c", help="限定国家")
    parser.add_argument("--city", help="限定城市")
    parser.add_argument("--lat", type=float, help="纬度 (搜索中心)")
    parser.add_argument("--lon", type=float, help="经度 (搜索中心)")
    parser.add_argument("--radius", type=int, default=5000, help="搜索半径(米)")
    parser.add_argument("--limit", type=int, default=5, help="返回数量")
    parser.add_argument("--format", "-f", choices=["json", "text"], default="text", help="输出格式")
    parser.add_argument("--no-cache", action="store_true", help="禁用缓存")

    args = parser.parse_args()

    try:
        client = GeocodingClient(use_cache=not args.no_cache)

        if args.geocode:
            locations = client.geocode(
                args.geocode,
                country=args.country,
                city=args.city,
                limit=args.limit
            )

            if args.format == "json":
                print(client.to_json(locations))
            else:
                print(f"📍 地址转坐标: {args.geocode}")
                for loc in locations:
                    print(f"\n  坐标: {loc.lat}, {loc.lon}")
                    print(f"  地址: {loc.formatted}")
                    if loc.city and loc.country:
                        print(f"  位置: {loc.city}, {loc.country}")
                    if loc.confidence:
                        print(f"  可信度: {loc.confidence:.0%}")

        elif args.reverse:
            try:
                lat, lon = map(float, args.reverse.split(","))
            except ValueError:
                print("❌ 坐标格式错误, 应为: lat,lon (如: 40.7128,-74.0060)")
                return

            locations = client.reverse_geocode(lat, lon, limit=args.limit)

            if args.format == "json":
                print(client.to_json(locations))
            else:
                print(f"📍 坐标转地址: {lat}, {lon}")
                for loc in locations:
                    print(f"\n  地址: {loc.formatted}")
                    print(f"  城市: {loc.city or 'N/A'}")
                    print(f"  州/省: {loc.state or 'N/A'}")
                    print(f"  国家: {loc.country or 'N/A'} ({loc.country_code or 'N/A'})")

        elif args.ip:
            location = client.ip_lookup(args.ip)

            if args.format == "json":
                print(client.to_json(location))
            else:
                print(f"🌐 IP: {location.ip}")
                print(f"  位置: {location.city or 'N/A'}, {location.region or 'N/A'}, {location.country or 'N/A'}")
                print(f"  坐标: {location.latitude}, {location.longitude}")
                print(f"  时区: {location.timezone}")
                if location.isp:
                    print(f"  ISP: {location.isp}")
                if location.asn:
                    print(f"  ASN: {location.asn}")

                flags = []
                if location.is_vpn: flags.append("VPN")
                if location.is_tor: flags.append("Tor")
                if location.is_proxy: flags.append("代理")
                if location.is_hosting: flags.append("托管")
                if location.is_mobile: flags.append("移动")
                if flags:
                    print(f"  标记: {', '.join(flags)}")

        elif args.asn:
            asn_info = client.asn_lookup(args.asn)

            if args.format == "json":
                print(client.to_json(asn_info))
            else:
                print(f"🔗 ASN: {asn_info.asn}")
                print(f"  名称: {asn_info.name}")
                print(f"  域名: {asn_info.domain or 'N/A'}")
                print(f"  路由: {asn_info.route}")
                print(f"  类型: {asn_info.type}")
                if asn_info.description:
                    print(f"  描述: {asn_info.description}")

        elif args.search_places:
            places = client.search_places(
                args.search_places,
                lat=args.lat,
                lon=args.lon,
                radius=args.radius,
                limit=args.limit
            )

            if args.format == "json":
                print(json.dumps(places, ensure_ascii=False, indent=2))
            else:
                print(f"🏪 地点搜索: {args.search_places}")
                if args.lat and args.lon:
                    print(f"  中心: {args.lat}, {args.lon}, 半径: {args.radius}m")
                for place in places:
                    name = place.get("name", "未知地点")
                    addr = place.get("address", "")
                    dist = place.get("distance")
                    print(f"\n  📍 {name}")
                    print(f"     地址: {addr}")
                    if dist:
                        print(f"     距离: {dist}m")

        else:
            parser.print_help()

    except GeocodingError as e:
        print(f"❌ 错误: {e}")
        exit(1)


if __name__ == "__main__":
    main()
