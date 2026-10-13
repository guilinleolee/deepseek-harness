# map-component V1.0 · DEPRECATED

> **归档日期**：2026-07-17
> **原位置**：`dragon-engine/skills/map-component/SKILL.md`
> **决策主题文件**：[memory/map-component-merge-decision.md](../map-component-merge-decision.md)
> **替代方案**：[dragon-engine/skills/guizang-social-card-skill/references/map-component.md](../skills/guizang-social-card-skill/references/map-component.md)

---

## 归档原因

天龙阶段 17 评估（R3 重叠评估 · 2026-07-17）发现：

1. **homegrown map-component 是「空壳规格」**：仅 SKILL.md，scripts/templates/examples 全部缺失
2. **guizang map-component 是「已完工产品」**：Playwright 渲染管线 + 9 条 DOM 校验 R1-R9 + 28 版式 + 10 主题
3. **两者在「真实地理瓦片 + 多 pin + 旅行/探店类小红书图文」功能上重叠**
4. **路线（route）/ 区域（area）/ 聚类（cluster）/ 热力图（heatmap）4 种模式是 homegrown 独有的设计规格**

## 决策

**方案 1**：归档 homegrown SKILL.md → 回流 4 种样式规格到 guizang map-component.md
- 拒绝方案 2（合并）= 强行合并 = guizang 重写全部 scripts（得不偿失）
- 拒绝方案 3（只留一个）= 删 guizang = 丢弃 9 条校验（亏）；删 homegrown = 丢失 4 种模式规格（亏）

## 回流清单

homegrown V1.0 的 5 种位置卡片样式将作为规格文档回流到 guizang map-component.md：

| mode | 描述 | 状态 |
|------|------|------|
| pin | 1-5 个标记 + 1 个 accent | ✅ guizang 已有（max 6/board）|
| route | 3-8 stops 路径折线 | ✅ 规格回流(2026-07-18)· 渲染待补 |
| area | 多边形 + 5-10 POI | ✅ 规格回流(2026-07-18)· 渲染待补 |
| cluster | 10-100 POI 聚类 | ✅ 规格回流(2026-07-18)· 渲染待补 |
| heatmap | 100+ 网格密度 | ✅ 规格回流(2026-07-18)· 渲染待补 |

> **回流进度(2026-07-18)**:5/5 模式的规格描述、数据契约(JSON schema)、渲染方案(Mode T/O/S)全部回流到 `dragon-engine/skills/guizang-social-card-skill/references/map-component.md` 的 §5 位置卡片样式 + §数据契约 章节。**渲染实现**(SVG Mode S 可立即实现)待触发条件:**有 travel/hiking/探店类博主入驻**。

附加回流：
- 中国地图源降级策略（高德→百度→Google→OSM）✅ 回流到 `references/map-component.md` §中国地图源降级策略(规格参考,不实际调用)
- 11-category 路由入口规格文档（旅行/职场/推荐/游戏/影视/...）✅ 回流到 `references/map-component.md` §11-category 路由适配

## 不要再用此 skill

任何 Agent 收到以下请求时，**绝对不要**调用本归档 skill：

```
❌ "做一张旅行地图 + 小红书图文"
❌ "画探店地图"
❌ "做北京三里屯美食地图（多 pin）"
❌ "做上海网红打卡路线图（路线模式）"
```

正确路由：

```
✅ guizang map-component（已合并 5 模式）
   dragon-engine/skills/guizang-social-card-skill/references/map-component.md
```

---

## 原 SKILL.md 内容备份

原文件已备份至本归档目录的子目录：

- `map-component-V1.0-homegrown-design-doc/SKILL.md.original`（主实例 · 241 行 · 9.6 KB）
- `map-component-V1.0-homegrown-design-doc/SKILL-2nd-instance.md`（`.claude/skills/` 下副本 · 完全一致）

两份原 SKILL.md 的完整内容（含 L0/L1/L2 全部章节）已保留，供将来查阅 V1.0 设计意图：

- 5 种位置卡片样式（pin/route/area/cluster/heatmap）设计规格
- 4 级地图源降级策略（高德→百度→Google→OSM）
- 11-category 路由入口（旅行/家居/美食/...）
- Editorial M13-M16 / Swiss S10 衍生版式映射
- WGS84 / GCJ02 / BD09 坐标系转换 spec
- social-card-validator R1-R7 协同链路
- 法律声明：「不调用任何第三方商业地图 API 专有代码」

> **注意**：原 SKILL.md 描述了未来的 `scripts/`（render_pin.py / render_route.py / render_area.py / render_cluster.py / render_heatmap.py / map_source_router.py / coord_transform.py）和 `templates/`（M13-M16 + S10 衍生 HTML）与 `examples/`，但**实际从未实装**。本次合并到 guizang 后由 guizang 渲染管线接管实现。

---

**相关决策**：见 `memory/map-component-merge-decision.md`（主题文件 #14）