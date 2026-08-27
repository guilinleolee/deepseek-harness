---
license: UNKNOWN
triggers: ["map component", "Map Component (地图/位置卡片渲染器)"]
---
# Map Component (地图/位置卡片渲染器)

> **L0 一句话**：渲染地图/位置卡片,适配 Editorial M13-M16 模板,支撑旅行/本地生活/美食探店类内容。

## L1 使用场景

当 11-category 路由匹配到「**旅行攻略**」「**家居生活**」「**美食菜谱**」三类时,调用本 Skill 渲染含地理信息的卡片。核心场景：

- **小红书旅行攻略**（3:4 配图 + 地图位置点）
- **本地生活探店**（1:1 推荐 + 区域热度图）
- **美食菜谱**（3:4 步骤 + 餐厅定位）
- **城市深度游**（9:16 竖屏路线图）
- **商圈/社区指南**（1:1 区域 + 兴趣点聚类）

## L2 详细文档

### 1. Context（背景）

归沧方法 28 套模板中,Editorial M13-M16 4 套专门为「**位置/地理**」维度设计：

- M13 = 单点地图
- M14 = 路线地图
- M15 = 区域地图
- M16 = 多点聚类

本 Skill 把这 4 套模板的渲染能力封装为可调用工具,补齐「**位置**」这一缺失的卡片维度。本 Skill 是归沧方法论二次创作,**不调用**任何第三方商业地图 API 的专有代码。**法律风险 = 0**。

### 2. Role（角色）

地图/位置卡片渲染器。同时承担：

- **5 种位置卡片样式**(pin / route / area / pin-cluster / heatmap)
- **适配 11-category 路由中的「旅行攻略」/「家居生活」/「美食菜谱」3 类**
- **地图源优先级**:高德 → 百度 → Google Maps → OpenStreetMap（国内优先高德/百度）
- **下游协同**:输出卡片直接对接 social-card-validator R1-R7 校验

### 3. Objective（目标）

- ✅ 补齐「位置/地理」维度的卡片组件
- ✅ 与 Editorial M13-M16 模板无缝对接
- ✅ 5 种位置卡片样式可由用户 / Agent 直接选择
- ✅ 地图数据源自动降级（高德不可用 → 百度 → Google → OSM）
- ✅ 法律风险 0（独立设计 + 公开 API 规范）

### 4. Actions（行动 — 5 种位置卡片样式）

#### 样式 1: Pin (单点定位)

- **适用**:单一地点推荐（餐厅 / 景点 / 酒店 / 咖啡店）
- **视觉**:1 个主 pin + 3-5 个辅助 POI 点
- **数据需求**:经纬度 + 名称 + 类别（餐饮 / 酒店 / 景点 / 娱乐）
- **模板**:Editorial M13
- **典型比例**:3:4 / 1:1

#### 样式 2: Route (路线规划)

- **适用**:多目的地路线（旅行 day-by-day / 探店路线 / 通勤）
- **视觉**:路径折线 + 起点终点 marker + 沿途 3-8 个 stop
- **数据需求**:多组经纬度 + 顺序 + 交通方式（步行 / 驾车 / 公交）
- **模板**:Editorial M14
- **典型比例**:9:16（竖屏路线） / 16:9（横屏全览）

#### 样式 3: Area (区域)

- **适用**:商圈 / 社区 / 景区概览
- **视觉**:多边形边界 + 区域内 5-10 个兴趣点
- **数据需求**:区域边界 (GeoJSON) + 兴趣点列表
- **模板**:Editorial M15
- **典型比例**:1:1

#### 样式 4: Pin Cluster (多点聚类)

- **适用**:同主题多地点（10+ 家咖啡店 / 20+ 家民宿 / 30+ 家书店）
- **视觉**:聚类气泡 + 缩放级别自适应
- **数据需求**:大量经纬度（10-100 个）+ 类别
- **模板**:Editorial M16
- **典型比例**:1:1 / 3:4

#### 样式 5: Heatmap (热力图)

- **适用**:某城市/区域数据密度（美食密度 / 房价热度 / 健身房密度）
- **视觉**:渐变色热力图 + 标注极值点（最高/最低 3 个）
- **数据需求**:网格化数据（lat/lng grid + weight）
- **模板**:Swiss S10 衍生（信息图风格）
- **典型比例**:1:1

### 5. Tactics（战术 — 地图源优先级与降级）

```
[Step 1] 数据准备
  → 11-category 路由 → 旅行/家居/美食 → 触发本 Skill
  → 提取经纬度 / 地名 / 类别 / 路线信息
  → 校验数据完整性（必填项：name, lat, lng, category）

[Step 2] 地图源选择（按优先级）
  Tier 1: 高德地图（国内首选,POI 数据最丰富,坐标系 GCJ-02）
  Tier 2: 百度地图（国内备选,坐标系 BD-09,需 GCJ-02 → BD-09 转换）
  Tier 3: Google Maps（海外/跨境,坐标系 WGS-84）
  Tier 4: OpenStreetMap（免费备选,数据较稀疏,无 Key 限制）

  → 自动检测当前网络区域 + 凭据可用性
  → 高德 API Key 存在 → Tier 1
  → 百度 API Key 存在 → Tier 2
  → 海外用户 → Tier 3
  → 全失败 → Tier 4 降级

[Step 3] 模板匹配
  → 5 种样式对应 5 套模板
  → pin → M13 / route → M14 / area → M15 / cluster → M16 / heatmap → S10 衍生

[Step 4] 渲染
  → 地图源 API 获取 tiles + markers
  → 套用模板样式（Editorial 杂志感 / Swiss 信息图感）
  → 主题色板适配（6 主题预设）
  → 输出:HTML / SVG / PNG（与 xhs-images 格式一致）

[Step 5] 校验
  → 调用 social-card-validator R1-R7 过审
  → 特别关注:
    - R6 截断保护（地名过长）
    - R2 色彩一致性（地图色与卡片主题色 ΔE）
    - R1 越大越细（路线 stop 数量 vs 视觉权重）

[Step 6] 发布
  → 通过校验后入 35-02 社媒运营 V13.2.0 队列
  → 位置元数据写入平台（小红书 POI tag / 公众号位置 tag）
```

### 6. Evaluation（评估标准）

| 维度 | 优秀 | 合格 | 不合格 |
|---|---|---|---|
| 地图源可用性 | Tier 1 成功 | Tier 2-3 降级 | Tier 4 仍失败 |
| 模板匹配 | 5 种样式 + 28 模板正确对应 | 1-2 处偏差 | 明显错配 |
| 视觉一致性 | 地图配色与主题色 ΔE < 10 | ΔE 10-20 | ΔE > 20 |
| POI 准确性 | 经纬度精确到小数点 6 位 | 4 位 | < 4 位（城市级） |
| 加载性能 | 首次渲染 < 2s | 2-5s | > 5s（Tiles 卡顿） |
| R1 越大越细 | 路线 stop 信息密度 ≥ 0.05 | 0.03-0.05 | < 0.03 |
| 坐标系一致性 | 单一坐标系（GCJ-02 或 WGS-84） | 跨源已转换 | 混用未转换 |

## 核心命令速查

```bash
# 渲染单点地图
@map-component pin --lat 30.27 --lng 120.15 --name "西湖" --category "景点"

# 渲染路线地图
@map-component route --stops "西湖,灵隐寺,龙井村" --transport "walking"

# 渲染区域地图
@map-component area --geojson ./area.geojson --pois ./pois.json

# 渲染多点聚类
@map-component cluster --points ./cafes.json --category "咖啡"

# 渲染热力图
@map-component heatmap --grid ./density.json --metric "美食密度"

# 与 35-02 协同
@35-02 旅行攻略自动调用 map-component pin + xhs-images

# 坐标系转换
@map-component convert --input coords.csv --from WGS84 --to GCJ02
```

## 5 种样式速查表

| 样式 | 模板 | POI 数 | 适用场景 | 典型比例 |
|---|---|---|---|---|
| pin | M13 | 1-5 | 单一推荐 | 3:4 / 1:1 |
| route | M14 | 3-8 | 路线规划 | 9:16 / 16:9 |
| area | M15 | 5-10 | 商圈/景区 | 1:1 |
| cluster | M16 | 10-100 | 同主题多地点 | 1:1 / 3:4 |
| heatmap | S10 衍生 | 100+ | 数据密度 | 1:1 |

## 地图源降级矩阵

| 场景 | Tier 1 高德 | Tier 2 百度 | Tier 3 Google | Tier 4 OSM |
|---|---|---|---|---|
| 国内 + 高德 Key | ✅ 首选 | 备选 | 不推荐 | 备选 |
| 国内 + 无 Key | 失败 | 备选 | 失败 | ✅ 免费 |
| 海外 | 失败 | 失败 | ✅ 首选 | 备选 |
| 跨境（国内数据） | ✅ | 备选 | 备选 | 备选 |

## 11-category 路由适配

| 类别 | 推荐样式 | 数据源 |
|---|---|---|
| 旅行攻略 | route + pin | 地名 → 高德 POI 搜索 |
| 家居生活 | area + pin | 楼盘/小区 → 高德 POI |
| 美食菜谱 | pin + cluster | 餐厅 → 高德 POI 搜索 |

## 协同链路

```
[01 调研师] 内容洞察（旅行/家居/美食）
    ↓
[35-02 社媒运营 V13.2.0] 11-category 路由
    ↓
[map-component] ← 本 Skill: 5 种位置样式渲染
    ↓
[social-card-validator] R1-R7 校验
    ↓
[xhs-images] → 小红书发布（含 POI tag）
```

## 法律声明

本 Skill 渲染逻辑独立设计，**不调用**任何第三方商业地图 API 的专有代码。地图源切换（高德/百度/Google/OSM）走各厂商公开 API 规范（REST + JSON）。所有 5 种位置样式 + 11-category 适配均根据 USER-GUIDE 第 7 章 + Phase 3 复盘独立设计。**法律风险 = 0**。

## 文件结构

```
map-component/
├── SKILL.md                       # 本文件
├── scripts/
│   ├── render_pin.py             # 单点地图
│   ├── render_route.py            # 路线地图
│   ├── render_area.py             # 区域地图
│   ├── render_cluster.py          # 聚类地图
│   ├── render_heatmap.py          # 热力图
│   ├── map_source_router.py       # 地图源降级路由
│   ├── coord_transform.py         # 坐标系转换（WGS84/GCJ02/BD09）
│   └── 5style_cli.py              # 统一 CLI 入口
├── templates/
│   ├── M13_pin.html               # Editorial M13
│   ├── M14_route.html             # Editorial M14
│   ├── M15_area.html              # Editorial M15
│   ├── M16_cluster.html           # Editorial M16
│   └── S10_heatmap.html           # Swiss S10 衍生
└── examples/
    ├── xhs_travel_pin.png         # 旅行 pin 样例
    ├── xhs_food_route.png         # 美食 route 样例
    └── map_validation_report.md   # 校验报告
```

## 版本历史

| 版本 | 日期 | 变更 |
|---|---|---|
| V1.0 | 2026-06-04 | 初始版本,5 种位置样式 + 11-category 适配（Phase 5.B） |
