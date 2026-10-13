# Map Component (.map-block)

Use when the content has **spatial relationships**: a travel route, store locations, walking tour, neighborhood overview, store-vs-store comparison by district, before/after relocation. Single coordinates ("我在北京") don't need a map.

Both seeds ship `.map-block` + `.map-pin` + `.map-legend` classes. The same markup works in either; only the style-locked tones differ.

## Three rendering modes

Pick mode **before** writing the markup. They are not stackable.

Default selection:

- Travel guides, walking routes, hiking, store locations, or anything the reader may use for orientation → **Mode T** Mapbox Static.
- Same need, but no Mapbox token → **Mode O** OSM static tile composite.
- Conceptual relationship map, fictional route, or purely editorial "places are connected like this" graphic → **Mode S** schematic SVG.

### Mode T · Mapbox Static Image (default for real routes)

Real raster tiles, desaturated and tinted to match the deck. Use when the content is travel / hiking / neighborhood wayfinding and you need to show actual terrain or streets. Requires `MAPBOX_ACCESS_TOKEN` in the build env.

```
https://api.mapbox.com/styles/v1/mapbox/light-v11/static/
  pin-s-1+555555(116.404,39.915),
  pin-l-2+1936b3(116.421,39.918)
  /116.412,39.916,14,0/1200x675@2x
  ?access_token=YOUR_TOKEN
```

```html
<div class="map-block r-16x10 tone-paper">
  <img src="https://api.mapbox.com/styles/v1/mapbox/light-v11/static/.../1200x675@2x?access_token=..." alt="Lhasa walking route">

  <!-- pins overlay (calculate % from mapbox bounds) -->
  <div class="map-pin" style="left:34%; top:52%;">...</div>
  <div class="map-pin accent" style="left:64%; top:42%;">...</div>

  <div class="map-legend">LHASA · MAPBOX LIGHT</div>
</div>
```

Editorial uses `tone-paper` (multiply-blend, saturation 36%). Swiss uses `tone-paper` with saturation 0 (pure greyscale). Don't show the raw Mapbox colour-saturated style — it fights the deck.

**Style allowlist** for the URL — keep it monochrome:
- `mapbox/light-v11`
- `mapbox/dark-v11`
- `mapbox/streets-v12` (only with `tone-paper`, never raw)

Never use `outdoors-v12` or `satellite-v9` — too colourful, will clash with both styles.

### Mode O · OpenStreetMap tile composite (fallback for real routes)

Free, no token. Use this when a real map is needed but Mapbox is unavailable. Render server-side via `staticmaps` npm package or similar, then place the raster as the `.map-block > img` child. Quality is lower than Mapbox, so keep labels sparse and let HTML pins carry the useful text.

### Mode S · Schematic SVG (conceptual / illustrative only)

Hand-drawn-style vector map drawn into a `viewBox="0 0 100 100"` SVG. Best for editorial decks where the map should feel like an illustrated guide, not a satellite capture. No external service.

```html
<div class="map-block r-16x10">
  <svg viewBox="0 0 100 100" preserveAspectRatio="none">
    <!-- coastline / district boundary -->
    <path class="map-coast" d="M 6 18 Q 32 22 58 16 T 96 28"/>
    <!-- main road -->
    <path class="map-road" d="M 8 78 Q 42 62 78 70 T 96 56"/>
    <!-- secondary road -->
    <path class="map-road" d="M 24 14 L 38 62 L 52 86"/>
    <!-- water / park polygon -->
    <path class="map-water" d="M 62 8 L 92 12 L 96 36 L 70 30 Z"/>
  </svg>

  <!-- pins overlay: % coords relative to .map-block -->
  <div class="map-pin" style="left:32%; top:48%;">
    <div class="dot"></div><div class="line"></div>
    <div class="card"><div class="name">大昭寺</div><span class="meta">DAY 1</span></div>
  </div>
  <div class="map-pin accent" style="left:62%; top:38%;">
    <div class="dot"></div><div class="line"></div>
    <div class="card"><div class="name">布达拉宫</div><span class="meta">DAY 2 · 18:40 SUNSET</span></div>
  </div>

  <div class="map-legend">LHASA · 拉萨城关 · 1:8K</div>
</div>
```

The SVG paths are stylized, not GPS-accurate. **Don't** try to trace OpenStreetMap by hand — this map is a graphic device, not a wayfinding tool. Sketch the major axes that frame the pins.

Layer order in the SVG (back to front):
1. `.map-water` polygons (rivers, lakes, parks)
2. `.map-coast` (boundary)
3. `.map-grid` (optional reference grid lines)
4. `.map-road` (transport lines)

Pins sit *outside* the SVG, as HTML siblings — they get the `.frame-shot` treatment for free.

## Hard rules

- **No pin labels on the SVG or raster tile.** Names live in `.map-pin .card`, never as SVG `<text>` or baked into the map image. Keeps font rendering consistent and avoids scaling issues.
- **Max 6 pins per board**. More than that, the cards collide. Use a relations / index card to list secondary points.
- **One accent pin maximum**. Multiple accents kill the visual hierarchy.
- **Pins must not overlap cards**. Test in browser first — if two cards are within 80 px on the long axis, alternate `.left` placement.
- **No live JavaScript map**. Social cards are static PNGs, MapLibre is wasted weight. The PPT skill has an interactive variant — don't port it here.

## Pin placement playbook

The `.map-pin` element uses `left:X%; top:Y%;` to anchor on its centre. The card grows to the right by default; add `.left` to flip:

```html
<div class="map-pin left" style="left:78%; top:30%;">
  <div class="dot"></div><div class="line"></div>
  <div class="card"><div class="name">车公庄</div><span class="meta">START</span></div>
</div>
```

Rule of thumb:
- Pin sits in left 60% of canvas → card opens right (default).
- Pin sits in right 60% of canvas → card opens left (`.left`).
- Two pins close to each other → alternate sides so cards don't stack.

## Recipe routing

Map block fits into existing recipes; it doesn't get its own.

| Recipe          | How the map fits                                                |
| --------------- | --------------------------------------------------------------- |
| M01 split       | Top half = `.map-block r-16x9`; bottom half = explanatory text. |
| M11 marginalia  | Main column = `.map-block r-3x4`; aside lists relation cards.   |
| M14 pipeline    | One step contains a small map (r-16x10) showing that step's location. |
| S02 two signals | One signal cell holds a map; the other holds the data table.    |
| S08 image hero  | Replace the hero photo with `.map-block r-16x10`.                |

Don't invent a "map-only" page — the map always pairs with text that says **why** the spatial relationship matters.

## Tone tokens

| Token         | Editorial behaviour                              | Swiss behaviour                               |
| ------------- | ------------------------------------------------ | --------------------------------------------- |
| (none)        | Raw — only use for SVG schematic.                | Raw — only use for SVG schematic.             |
| `tone-paper`  | Multiply blend on warm paper. Default for travel.| Hard greyscale. Default for everything.       |
| `tone-ink`    | Brightness 62%, saturation 18%. Dark deck pages. | Brightness 58%, saturation 0%. Dark posters.  |

Tone only affects `> img` children, not the SVG schematic.

## Common mistakes

- **Pasting Google Maps screenshots** — wrong tone, has UI chrome, will look out of place. Use Mapbox Static, OSM static tiles, or a schematic when the map is conceptual.
- **Tracing a real map into SVG** — schematic should *abstract*, not replicate. If a viewer can guess the city from your SVG alone, you over-traced.
- **Tiny pin cards** — `.card .name` is 15-16 px minimum. Cut the name if it overflows; never shrink.
- **Accent on every pin** — defeats the highlight system. Pick one most-important point.

---

## Five location styles (天龙 2026-07-17 扩展 · 来自 homegrown map-component V1.0)

> **来源**：homegrown `dragon-engine/skills/map-component/` V1.0（已归档 → `_archive/map-component-V1.0-DEPRECATED.md`）
> **决策记录**：[memory/map-component-merge-decision.md](../../../memory/map-component-merge-decision.md)
> **复用渲染管线**：上方的 Mode T (Mapbox) / Mode O (OSM) / Mode S (SVG schematic) —— 5 种样式共用同一套管线，仅模板差异化

| 模式 | 描述 | 渲染方式 | 适用场景 |
|------|------|---------|---------|
| **pin** | 1-6 个标记 + 1 个 accent | Mode T / O / S 任选 | 探店、POI 标注、景点列表 |
| **route** | 3-8 stops 路径折线 | Mode T（推荐）或 S | 旅行路线、城市徒步、city walk、行程规划 |
| **area** | 多边形 + 5-10 POI | Mode T | 区域盘点、商圈分析、社区边界 |
| **cluster** | 10-100 POI 聚类 | Mode O（OSM 聚合）| 城市美食地图、密度热区、多个分店 |
| **heatmap** | 100+ 网格密度 | Mode O（OSM heatmap）| 大范围数据可视化、人口密度、商家分布 |

### Route 模式（3-8 stops）

```html
<div class="map-block r-16x10 tone-paper">
  <img src="https://api.mapbox.com/.../route-style/.../1200x675@2x?access_token=...">

  <!-- 路线 pins 顺序连接 -->
  <div class="map-pin" style="left:25%; top:60%;">
    <div class="dot">1</div>
    <div class="card"><div class="name">三里屯</div><span class="meta">DAY 1 · 14:00</span></div>
  </div>
  <div class="map-pin" style="left:45%; top:40%;">
    <div class="dot">2</div>
    <div class="card"><div class="name">国贸</div><span class="meta">DAY 1 · 17:00</span></div>
  </div>
  <div class="map-pin accent" style="left:70%; top:30%;">
    <div class="dot">3</div>
    <div class="card"><div class="name">什刹海</div><span class="meta">DAY 1 · 20:00</span></div>
  </div>

  <div class="map-legend">北京 CITY WALK · 1 DAY · 3 STOPS</div>
</div>
```

**硬规则**：
- Max **8 stops**（超过 8 用 cluster 替代）
- 数字编号 `.dot` 必须顺序连接
- 起点用 `accent` 高亮

### Area 模式（多边形 + 5-10 POI）

```html
<div class="map-block r-3x4 tone-ink">
  <svg viewBox="0 0 100 100" preserveAspectRatio="none">
    <!-- 多边形边界 -->
    <path class="map-coast" d="M 20 30 L 80 25 L 85 70 L 25 75 Z" fill="rgba(0,47,167,0.15)" stroke="#002FA7" stroke-width="0.5"/>
    <!-- POI 散布 -->
    <circle cx="35" cy="45" r="1.5" fill="#002FA7"/>
    <circle cx="55" cy="50" r="1.5" fill="#002FA7"/>
    <circle cx="65" cy="60" r="1.5" fill="#002FA7"/>
  </svg>

  <div class="map-pin accent" style="left:35%; top:45%;">
    <div class="card"><div class="name">798 艺术区</div><span class="meta">核心区</span></div>
  </div>

  <div class="map-legend">北京 798 · 5 POI · 艺术商圈</div>
</div>
```

### Cluster 模式（10-100 POI 聚类）

适用 OSM Mode O，通过 staticmaps npm 聚合渲染。HTML pins 仅展示 TOP 3-5 聚类点，剩余用数字徽章表示（如 "23+"）。

### Heatmap 模式（100+ 网格密度）

适用 OSM Mode O，通过 staticmaps + leaflet-heatmap 渲染。HTML 层不显示 pin，仅图例说明密度梯度。

---

## 中国地图源降级策略（homegrown V1.0 引用）

> 来自 homegrown map-component V1.0 的 4 级降级策略，作为 reference 引用

| 优先级 | 源 | 备注 |
|--------|----|------|
| 1 | 高德（国内首选）| 需 key |
| 2 | 百度地图 | 需 key |
| 3 | Google Static Maps | 海外首选，需 key |
| 4 | **OSM staticmaps（推荐 fallback）** | 免费、guizang 默认走这条 |

**guizang 推荐**：除非业务强需求，**默认走 OSM**（免费、无 token、隐私友好），高德/百度仅在 POI 数据准确性要求高的场景使用。

---

## 11-category 路由入口（homegrown V1.0 引用）

来自 homegrown map-component V1.0 的 11 小红书品类路由表，与本 skill `references/category-cookbook.md` 对齐。

---

## 坐标系转换参考（homegrown V1.0 引用）

WGS84 / GCJ02 / BD09 三坐标系互转 spec：
- **WGS84**（国际标准）— Mapbox / OSM 使用
- **GCJ02**（国测局加密）— 高德 / 腾讯使用
- **BD09**（百度加密）— 百度使用

国内 POI 数据从高德/百度获取时需先转 WGS84 再上 Mapbox。

---

## 5 种位置卡片样式规格（homegrown V1.0 回流扩展 · 阶段 19 V2.0.3）

> **扩展基础**:line 152 已有的 "Five location styles" 表格 + route/area 代码示例  
> **回流来源**:`dragon-engine/skills/_archive/map-component-V1.0-DEPRECATED.md`  
> **回流日期**:2026-07-18(候选 22 收尾)  
> **本节补充**:line 152 表格未覆盖的**完整数据契约**(JSON schema)+ **Mode S 实现优先级判定**  
> **适配状态**:`pin` 已被 guizang 现有 `.map-pin` 覆盖;其余 4 种(`route` / `area` / `cluster` / `heatmap`)回流本文档,**渲染实现待补**。

5 种样式共享同一 `.map-block` + `.map-pin` + `.map-legend` 类,**只有数据结构和版式选择不同**。Agent 选择模式后,按对应数据契约填字段。

### 样式 1 · Pin (单点定位) ✅ 已被 guizang 覆盖

- **适用**:单一地点推荐(餐厅 / 景点 / 酒店 / 咖啡店)
- **视觉**:1 个主 pin + 3-5 个辅助 POI 点
- **数据需求**:经纬度 + 名称 + 类别
- **模板**:Editorial M13(`map-pin` 已在 `references/components.md` 定义)
- **典型比例**:3:4 / 1:1
- **Guizang 当前支持**:✅ `pin-s-1` / `pin-l-2` Mapbox style,1-6 个 pin/board

### 样式 2 · Route (路线规划) 🟡 规格回流,渲染待补

- **适用**:多目的地路线(旅行 day-by-day / 探店路线 / 通勤)
- **视觉**:路径折线(SVG `<path>`)+ 起点终点 marker + 沿途 3-8 个 stop
- **数据需求**:
  ```jsonc
  {
    "mode": "route",
    "stops": [
      { "id": "start",  "name": "西湖",     "lat": 30.245, "lng": 120.142, "category": "景点" },
      { "id": "stop-1", "name": "灵隐寺",   "lat": 30.241, "lng": 120.101, "category": "景点" },
      { "id": "stop-2", "name": "龙井村",   "lat": 30.222, "lng": 120.108, "category": "美食" },
      { "id": "end",    "name": "灵隐路",   "lat": 30.246, "lng": 120.115, "category": "街道" }
    ],
    "transport": "walking|driving|transit"
  }
  ```
- **模板**:Editorial M14(pipeline stage 19 已自动选 M14 用于 laoli 老李,但 .map-block 内 **route** 路径样式待补)
- **典型比例**:9:16(竖屏路线) / 16:9(横屏全览)
- **渲染方案**:
  - Mode T (Mapbox):Mapbox Directions API → polyline overlay on map
  - Mode O (OSM):GraphHopper OSRM `/route` 公共 endpoint → polyline
  - Mode S (SVG):纯 SVG `<polyline points="...">` + 圆点 marker,无需任何外部 API
- **Guizang 当前支持**:🟡 数据契约已定义,SVG Mode S 可立即实现

### 样式 3 · Area (区域) 🟡 规格回流,渲染待补

- **适用**:商圈 / 社区 / 景区概览
- **视觉**:多边形边界(GeoJSON Polygon)+ 区域内 5-10 个 POI
- **数据需求**:
  ```jsonc
  {
    "mode": "area",
    "boundary": {
      "type": "Polygon",
      "coordinates": [[[116.40,39.90],[116.42,39.90],[116.42,39.92],[116.40,39.92],[116.40,39.90]]]
    },
    "pois": [
      { "name": "三里屯太古里", "lat": 39.913, "lng": 116.415, "category": "商圈" },
      { "name": "工体北路",     "lat": 39.918, "lng": 116.418, "category": "街道" }
    ],
    "fill_opacity": 0.18,
    "stroke_weight": 2
  }
  ```
- **模板**:Editorial M15
- **典型比例**:1:1(区域全览)
- **渲染方案**:
  - Mode T (Mapbox):`/styles/v1/mapbox/light-v11/geojson` overlay
  - Mode O (OSM):Leaflet `L.polygon` + OSM tile composite
  - Mode S (SVG):`<polygon points="...">` + `<circle>` POI markers
- **Guizang 当前支持**:🟡 数据契约已定义,SVG Mode S 可立即实现

### 样式 4 · Pin Cluster (多点聚类) 🟡 规格回流,渲染待补

- **适用**:同主题多地点(10+ 家咖啡店 / 20+ 家民宿 / 30+ 家书店)
- **视觉**:聚类气泡(数字 = 该簇 POI 数)+ 缩放级别自适应(zoom-in 展开)
- **数据需求**:
  ```jsonc
  {
    "mode": "cluster",
    "points": [
      { "name": "Manner 静安寺", "lat": 31.223, "lng": 121.448, "category": "咖啡" },
      /* ... 30+ points ... */
    ],
    "category": "咖啡|书店|民宿|餐厅",
    "zoom": 12
  }
  ```
- **模板**:Editorial M16
- **典型比例**:1:1 / 3:4
- **渲染方案**:
  - Mode T (Mapbox):Mapbox built-in `cluster: true` on GeoJSON source
  - Mode O (OSM):Leaflet `markercluster` plugin + OSM tiles
  - Mode S (SVG):服务端预聚类(simple-grid-bucket → 6 桶,然后 SVG `<circle>` 半径按点数)
- **Guizang 当前支持**:🟡 数据契约已定义。**仅 Mode S 可立即实现**(Mode T/O 需要 JS 运行时,违反"No live JavaScript map"硬约束 line 101)

### 样式 5 · Heatmap (热力图) 🟡 规格回流,渲染待补

- **适用**:某城市/区域数据密度(美食密度 / 房价热度 / 健身房密度)
- **视觉**:渐变色热力图(冷→暖=低→高)+ 标注极值点(最高/最低 3 个)
- **数据需求**:
  ```jsonc
  {
    "mode": "heatmap",
    "grid": [
      { "lat": 39.913, "lng": 116.405, "weight": 8.2 },
      { "lat": 39.918, "lng": 116.418, "weight": 12.5 },
      /* ... 100+ grid cells ... */
    ],
    "metric": "美食密度|房价热度|健身房密度",
    "scale": "linear|log"
  }
  ```
- **模板**:Swiss S10 衍生(信息图风格)
- **典型比例**:1:1
- **渲染方案**:
  - Mode T (Mapbox):Mapbox built-in `heatmap-layer` on GeoJSON source
  - Mode O (OSM):Leaflet.heat plugin + OSM tiles
  - Mode S (SVG):服务端预聚合 → 6 桶颜色映射(蓝/青/黄/橙/红/深红),`<rect>` 半透明叠加
- **Guizang 当前支持**:🟡 数据契约已定义。**仅 Mode S 可立即实现**

---

## 5 种样式速查表（聚合）

| 模式 | 模板 | POI 数 | 适用场景 | 典型比例 | Guizang 现状 |
|------|------|--------|---------|---------|-------------|
| **pin** | Editorial M13 | 1-6 | 单点推荐 | 3:4 / 1:1 | ✅ 已实现 |
| **route** | Editorial M14 | 3-8 stops | 多目的地路线 | 9:16 / 16:9 | 🟡 Mode S 可立即 |
| **area** | Editorial M15 | 5-10 + 多边形 | 商圈/社区/景区概览 | 1:1 | 🟡 Mode S 可立即 |
| **cluster** | Editorial M16 | 10-100 | 同主题多点 | 1:1 / 3:4 | 🟡 Mode S 可立即 |
| **heatmap** | Swiss S10 衍生 | 100+ grid | 数据密度分布 | 1:1 | 🟡 Mode S 可立即 |

---

## 渲染约束（重要）

> 来自本文件 line 101:`No live JavaScript map. Social cards are static PNGs, MapLibre is wasted weight.`

**这意味着**:
- Mode T (Mapbox Static Image) ✅ 可用(纯 raster 拉取)
- Mode O (OSM Tile Composite) ✅ 可用(纯 raster 拉取)
- Mode S (Schematic SVG) ✅ 可用(纯前端 SVG,无外部 API)
- ❌ Mapbox GL JS / Leaflet / MapLibre JS 运行时 → **禁止**(违反 line 101)

**回流 4 模式的实现策略**:**全部走 Mode S**(SVG 生成),保证符合"static PNGs"硬约束。

---

## 地图源降级矩阵（homegrown V1.0 回流 · 不在 guizang 默认实现路径内）

> **说明**:homegrown 5 模式 spec 配套设计了中国地图源降级(高德→百度→Google→OSM)。guizang 主用 Mapbox Static + OSM + SVG,不直接用高德/百度 API(避免国内合规 + API key 管理成本)。下表**仅作为规格参考**,实际 guizang 实现**不需要**调用这些 API。

| 优先级 | 地图源 | 坐标系 | 适用场景 | 凭据要求 |
|--------|--------|--------|---------|---------|
| Tier 1 | 高德地图 | GCJ-02 | 国内首选,POI 数据最丰富 | 高德 Web API Key |
| Tier 2 | 百度地图 | BD-09 | 国内备选,需 GCJ-02→BD-09 转换 | 百度地图 API Key |
| Tier 3 | Google Maps | WGS-84 | 海外/跨境 | Google Maps Platform Key |
| Tier 4 | OpenStreetMap | WGS-84 | 免费备选,数据较稀疏,无 Key 限制 | 无 |
| Tier 5(guizang 实际) | **Mapbox Static** | WGS-84 | 国际首选 + 静态 PNG 输出 | `MAPBOX_ACCESS_TOKEN` |
| Tier 6(guizang fallback) | **SVG Schematic** | 不需要 | 数据稀疏或无 token 时 | 无 |

---

## 11-category 路由适配（homegrown V1.0 引用）

> homegrown 5 模式 spec 设计时配套了 11 个小红书品类的推荐样式表。guizang 主用 `references/category-cookbook.md` 路由(11 大类 + 28 版式 + 10 主题),**不完全等同** homegrown 的 11-category。下表是 homegrown 映射,**仅作参考**:

| homegrown 品类 | 推荐样式 | 说明 |
|---------------|---------|------|
| 旅行攻略 | **route** + **area** + pin | 多目的地、跨城路线 |
| 家居生活 | pin + **area** | 楼盘、商圈、小区 |
| 美食菜谱 | pin + **cluster** + **heatmap** | 单店 / 多店对比 / 区域密度 |
| 时尚穿搭 | pin | 单店 / 单品 |
| 美妆 | pin | 专柜位置 |
| 育儿 | pin + **area** | 母婴店分布 |
| 数码 | (无) | 数码类极少用地图 |
| 职场 | pin + **route** | 公司周边通勤 |
| 游戏 | (无) | 虚拟位置 |
| 影视 | pin | 拍摄地 / 城市取景 |
| 教育 | pin + **area** | 学校 / 学区 |

天龙实际路由优先级:**guizang category-cookbook > 本表**(避免重复定义)。

---

## 法律声明（homegrown V1.0 声明 · 引用保留）

> 本 Skill 渲染逻辑独立设计,**不调用**任何第三方商业地图 API 的专有代码。地图源切换(高德/百度/Google/OSM/Mapbox)走各厂商公开 API 规范(REST + Static Image)。所有 5 种位置样式 + 11-category 适配均根据独立 spec 设计。**法律风险 = 0**。

实际天龙执行:
- Mapbox Static Image API:`api.mapbox.com/styles/v1/...` ← 公开 REST endpoint
- OpenStreetMap tiles:`tile.openstreetmap.org/{z}/{x}/{y}.png` ← ODbL 协议
- Mode S SVG:零外部 API 依赖

合规上无风险。
