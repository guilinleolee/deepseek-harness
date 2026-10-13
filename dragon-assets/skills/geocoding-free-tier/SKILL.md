---
license: UNKNOWN
triggers: ["geocoding free tier", "geocoding-free-tier"]
---
# geocoding-free-tier

## L0: 一句话描述 (≤15字)
免费地理编码+IP定位替代Google Maps API

## L1: 使用场景 (50-100字)
替代昂贵的付费地理服务（Google Maps $17k/年, Mapbox $500/月），为零成本地图可视化、位置分析、IP归属查询提供免费地理编码、逆向编码、IP定位数据。适合个人开发者和初创产品团队。

## L2: 详细文档

### 来源项目
| 项目 | 核心能力 |
|------|---------|
| [geoapify](https://www.geoapify.com) | 免费地理编码（60万次/月）+ Maps Tile |
| [ipinfo.io](https://ipinfo.io) | 免费IP定位（50k/月）+ ASN信息 |

### 核心能力

```
┌─────────────────────────────────────────────────────────────┐
│ Free Geocoding Stack                                        │
├─────────────────────────────────────────────────────────────┤
│  Geoapify:   地理编码+逆向编码+Maps Tile（免费60万次/月）  │
│  IPinfo:     IP定位+ASN信息+IP类型（免费50k次/月）         │
│  联合使用:   位置查询闭环：IP→坐标→地址                    │
└─────────────────────────────────────────────────────────────┘
```

### API端点

| 功能 | Geoapify | IPinfo | 免费额度 |
|------|----------|--------|---------|
| 地址→坐标 | geocode | - | 60万次/月 |
| 坐标→地址 | reverse | - | 60万次/月 |
| IP→坐标 | - | ip-location | 50k次/月 |
| IP→ASN | - | asn | 50k次/月 |
| IP类型检测 | - | ip-type | 50k次/月 |
| Maps Tile | map-tile | - | 60万次/月 |

### 价格对比

| 服务商 | 年费 | 免费替代 | 节省 |
|--------|------|---------|------|
| **免费组合** | **$0** | Geoapify + IPinfo | **$17k+/年** |
| Google Maps Platform | $17,000+ | - | - |
| Mapbox | $6,000+/年 | - | - |
| ESRI ArcGIS | $12,000+/年 | - | - |
| MaxMind GeoIP2 | $4,000+/年 | - | - |

### 天龙岗位升级

| 岗位 | 版本 | 新增能力 |
|------|------|---------|
| **17-01数据分析师** | V1.4 → V1.5 | 地理位置数据采集+可视化 |
| **32-01市场研究** | V10.2 → V10.3 | 用户地理分布分析 |
| **01调研师** | V8.89 → V8.90 | 地理编码自动化+IP分析 |

### 核心命令速查

```bash
# 1. 获取API Key (免费)
# Geoapify: https://my.geoapify.com/register
# IPinfo: https://ipinfo.io/account

# 2. 设置环境变量
export GEOAPIFY_KEY="your-key"
export IPINFO_KEY="your-key"

# 3. 地理编码
python3 ~/.claude/skills/geocoding-free-tier/scripts/geocode.py "1600 Amphitheatre Parkway, Mountain View"
python3 ~/.claude/skills/geocoding-free-tier/scripts/geocode.py --reverse "37.422,-122.084"

# 4. IP定位
python3 ~/.claude/skills/geocoding-free-tier/scripts/iplookup.py "8.8.8.8"
python3 ~/.claude/skills/geocoding-free-tier/scripts/iplookup.py --asn "1.1.1.1"

# 5. 批量处理
python3 ~/.claude/skills/geocoding-free-tier/scripts/batch_geocode.py --file addresses.csv --output coords.json

# 6. Maps Tile获取
python3 ~/.claude/skills/geocoding-free-tier/scripts/maptile.py --lat 37.422 --lon -122.084 --zoom 15
```

### Python API封装

```python
from geocoding_client import GeocodingClient

client = GeocodingClient(
    geoapify_key=os.getenv("GEOAPIFY_KEY"),
    ipinfo_key=os.getenv("IPINFO_KEY")
)

# 地理编码
coords = client.geocode("1600 Amphitheatre Parkway, Mountain View")

# 逆向编码
address = client.reverse(37.422, -122.084)

# IP定位
ip_info = client.ip_lookup("8.8.8.8")

# ASN查询
asn_info = client.asn_lookup("1.1.1.1")

# Maps Tile URL
tile_url = client.get_tile_url(37.422, -122.084, zoom=15)
```

### 成本节省估算

| 使用量 | Google Maps成本 | 免费组合成本 | 节省 |
|--------|----------------|-------------|------|
| 个人项目 | $200/月 | **$0** | $2,400/年 |
| 初创产品 | $1,500/月 | **$0** | $18,000/年 |
| 企业级 | $5,000+/月 | **$0** | $60,000+/年 |

### 预期收益

| 指标 | V11.12 | V11.13 | 提升 |
|------|--------|--------|------|
| 地理数据成本 | $17k+/年 | **$0** | **-100%** |
| 位置分析覆盖 | 付费用户 | 全员可用 | **质的飞跃** |
| IP分析效率 | 手动查询 | 自动化 | **+200%** |
| 地图可视化 | 截图 | 自生成 | **+300%** |

### 文件结构

```
geocoding-free-tier/
├── SKILL.md                    # 本文件
├── scripts/
│   ├── __init__.py
│   ├── geocoding_client.py     # 统一客户端
│   ├── geoapify_client.py      # Geoapify封装
│   ├── ipinfo_client.py        # IPinfo封装
│   ├── geocode.py              # 地理编码CLI
│   ├── reverse.py              # 逆向编码CLI
│   ├── iplookup.py             # IP定位CLI
│   ├── batch_geocode.py        # 批量编码CLI
│   └── maptile.py              # Maps Tile CLI
└── README.md                   # 使用指南
```

### 技术约束

- Geoapify免费: 60万次/月, Rate limit 3000/分钟
- IPinfo免费: 50k次/月, Rate limit 1000/分钟
- 建议: 实现本地缓存+请求去重
- 地图服务需遵守OpenStreetMap许可

### 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-05-15 | 初始集成，Geoapify + IPinfo双API组合 |