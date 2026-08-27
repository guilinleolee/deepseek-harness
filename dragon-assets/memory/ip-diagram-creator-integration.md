---
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---
# ip-diagram-creator 集成 · V1.0

> **触发源**：[haloshin/ip-diagram-creator](https://github.com/haloshin/ip-diagram-creator)（73 ⭐ · 2026-06-22 · MIT）
> **战略定位**：补齐天龙引擎「博主全息克隆」第 8 维 · IP 视觉指纹
> **阶段**：#11 · 升级 4 个 SKILL · 累计 **28/28 PASS**

---

## 一、为什么是它（⭐ 低但价值高）

| 维度 | 数据 | 评价 |
|------|------|------|
| GitHub ⭐ | 73 | ⚠️ 偏低（低于 200） |
| 创新密度 | 极高（4 大原创）| ⭐⭐⭐⭐⭐ |
| 与天龙契合度 | IP 视觉 + Agent 协作 + PPT 规划 + 4 类密度 | ⭐⭐⭐⭐⭐ |
| 触发源质量 | 同源 khazix-skills 9.9k ⭐ | ⭐⭐⭐ |
| 综合价值 | **战略必备**（8 维指纹关键缺角）| ⭐⭐⭐⭐⭐ |

**判断**：虽然 ⭐ 偏低，但解决天龙「视觉指纹」空白 > 通用借鉴门槛。

---

## 二、借鉴的 4 大原创（克制清单）

| # | 借鉴项 | 落地 SKILL | 不照搬（克制）|
|---|--------|-----------|--------------|
| ① | **IP 角色三件套**（anchor + spec + extensions）| smart-illustrator V2.2 / ppt-master V9.9 / qiaomu-mondo V1.1 / blogger-fingerprint-registry V2.0 | 完整 IP 生成链路（已分流到 smart-illustrator）|
| ② | **Agent 协作图解**（IP 主 + 2-6 执行 Agent）| smart-illustrator V2.2 / ppt-master V9.9 / qiaomu-mondo V1.1 | 完整 Agent 编排引擎（不在 skill 范畴）|
| ③ | **IP 导演规划卡 + 8 类页面节奏** | ppt-master V9.9（新增 `/ppt-master-ip` 入口）| 完整 8 类全部生成（保留 3 类核心，其余占位）|
| ④ | **4 类信息密度**（minimal/low/medium/high）| smart-illustrator V2.2 / qiaomu-mondo V1.1 / blogger-fingerprint-registry V2.0 | 密度感知渲染管线（保持 schema 标记）|

---

## 三、4 个 SKILL 升级摘要

### 1. smart-illustrator V2.1.0 → V2.2.0

- 新增 `--ip-profile` 参数（IP 角色三件套锚定）
- 新增 `--agent-count` 参数（Agent 协作图解）
- 新增 `--density` 参数（minimal/low/medium/high 4 类）
- 新增 ip-profile JSON 模板与示例
- **向后兼容**：未传 --ip-profile 时走 V2.1 默认流程

### 2. ppt-master V9.8.0 → V9.9.0

- 新增 `/ppt-master-ip` 入口（IP 演讲模式）
- 新增 **8 类页面节奏**：cover / big-judgment / module / standard / scene / timeline / method / closing
- 新增 **IP 导演规划卡**（强制输出，用户确认后再批量）
- 新增 **contact sheet 整套 QA**（8up gallery 检视一致性）
- 新增 4 段式工作流：规划 → 样张 → 批量 → QA

### 3. qiaomu-mondo-poster-design V1 → V1.1.0

- 新增 `--ip-profile` 参数（IP 角色锁）
- 新增 `--mode knowledge-card`（Agent 协作海报）
- 新增 `--density` 参数（minimal/symbolic/labeled/knowledge-card 4 类）

### 4. blogger-fingerprint-registry V1.0 → V2.0

- 6 维指纹 → **8 维指纹**（声纹 6 + 文风 1 + IP 视觉 1）
- 新增 `ip_profiles` SQLite 表（IP 视觉独立存储）
- 新增 CLI：`add-ip` / `search-ip` / `retire-ip`
- **双重 consent**：声纹 consent + IP 视觉 ip_consent（独立授权范围）
- **双重撤回**：可仅撤回 IP 视觉，声纹保留

---

## 四、关键 schema 协议（4 SKILL 互通）

### ip-profile JSON（统一格式）

```json
{
  "blogger_id": "tech_laowang_01",
  "ip_anchor": {
    "image_path": "./ip-profile/anchor.png",
    "description": "科技老王，35 岁，戴圆框眼镜，穿灰色连帽衫"
  },
  "ip_spec": {
    "image_path": "./ip-profile/spec.png",
    "style_keywords": ["极简线条", "扁平插画", "莫兰迪色"],
    "color_palette": ["#2C3E50", "#E74C3C", "#ECF0F1"],
    "line_thickness": "medium"
  },
  "ip_extensions": {
    "image_path": "./ip-profile/extensions.png",
    "actions": ["讲解时双手摊开", "强调时握拳", "思考时托腮"],
    "expressions": ["微笑", "惊讶", "沉思"]
  },
  "ip_consent_file": "./ip-profile/consent.txt"
}
```

### 4 SKILL 协同矩阵

```
用户 → 上传 ip-profile JSON
        ↓
   ┌────┴────────────────────────────┐
   ↓                                 ↓
smart-illustrator              ppt-master
(配图 V2.2)                    (演讲 V9.9 + IP 导演规划)
   ↓                                 ↓
qiaomu-mondo                   blogger-fingerprint-registry
(海报 V1.1)                    (入库第 8 维 + 双重 consent)
   └────┬────────────────────────────┘
        ↓
   35-06 博主全息克隆 V1.1
   (文 + 图 + 音 + IP + 文风 + … = 8 维全息)
```

---

## 五、伦理护栏（强化为三重）

| 护栏 | 强制 | 说明 |
|------|------|------|
| **声纹 consent** | ✅ | V1.0 已有 |
| **IP 视觉 consent**（新）| ✅ | V2.0 引入，独立授权书 |
| **授权范围 scope** | 个人/商用/全平台 | V2.0 新增 |
| **IP 撤回与声纹独立** | ✅ | 可仅撤回 IP，保留声纹 |
| **私有 ip-profile 不入库** | ✅ | 4 SKILL 全部对齐 |

---

## 六、累计验证 · 28/28 PASS

| 类别 | 测试数 | 通过 | 失败 |
|------|--------|------|------|
| smart-illustrator V2.2 | 7 | 7 | 0 |
| ppt-master V9.9 | 7 | 7 | 0 |
| qiaomu-mondo V1.1 | 5 | 5 | 0 |
| blogger-fingerprint-registry V2.0 | 9 | 9 | 0 |
| **合计** | **28** | **28** | **0** |

验证脚本：`scripts/ip_diagram_check.py`（退出码 0=PASS / 1=部分失败 / 2=配置错 / 3=系统错）

---

## 七、与历史阶段的协同

| 上游 | 协同方式 |
|------|---------|
| **template-tone-matcher** | 8 字段协议检索 PPT/海报风格 |
| **smart-illustrator V2.1** | V2.2 向后兼容，未传 --ip-profile 时走 V2.1 |
| **ppt-master V9.8** | V9.9 向后兼容，未触发 /ppt-master-ip 时走 V9.8 |
| **blogger-fingerprint-registry V1.0** | V2.0 向后兼容，未注册 ip-profile 时仅存声纹 |
| **35-06 博主蒸馏 V1.1** | 接收 8 维指纹（含 IP 视觉）做全息克隆 |
| **voxcpm-multi-speaker V1.0** | 旁白 + IP 角色 = 音画同步 |

| 下游 | 协同方式 |
|------|---------|
| **multi-platform-publisher V1.0** | 把 IP 演讲 PPT + 海报 + 旁白推 9 平台 |
| **x-publisher-v2** | X/Twitter 双路线保障（IP 形象首发）|
| **stage 14 baoyu-skills 全集 21/21** | baoyu-diagram / baoyu-comic / baoyu-slide-deck 与 IP 视觉三件套形成「通用 vs IP」双轨 |

---

## 八、关键文件路径（速查）

| 资产 | 路径 |
|------|------|
| smart-illustrator V2.2.0 | `C:\Users\li\.claude\projects\dragon-engine\skills\smart-illustrator\SKILL.md` |
| ppt-master V9.9.0 | `C:\Users\li\.claude\projects\dragon-engine\skills\ppt-master\SKILL.md` |
| qiaomu-mondo-poster-design V1.1.0 | `C:\Users\li\.claude\projects\dragon-engine\skills\qiaomu-mondo-poster-design\SKILL.md` |
| blogger-fingerprint-registry V2.0 | `C:\Users\li\.claude\skills\blogger-fingerprint-registry\SKILL.md` |
| 验证脚本 | `C:\Users\li\.claude\projects\dragon-engine\skills\ip-diagram-creator-integration\scripts\ip_diagram_check.py` |
| MEMORY 主索引 | `C:\Users\li\.claude\projects\c--Users-li--claude\memory\MEMORY.md` |

---

## 九、借鉴但不照搬（克制清单 · 复盘）

- ✅ **借鉴**：IP 三件套、8 类页面节奏、4 类密度、Agent 协作、contact sheet QA
- ❌ **不照搬**：完整 IP 生成管线（已分流 smart-illustrator）
- ❌ **不照搬**：完整 Agent 编排引擎（不在 skill 范畴）
- ⚠️ **观察**：⭐ 73 偏低，但解决了天龙「视觉指纹」关键缺角，**值得借鉴**

---

## 十、版本信息

- **Version**: 1.0
- **Date**: 2026-07-02
- **Author**: 天龙引擎集成
- **License**: MIT
- **累计验证**：**28/28 PASS**（V2.2 + V9.9 + V1.1 + V2.0 全部就位）
- **对 MEMORY.md 贡献**：累计 PASS 262 → 290 · 主题文件 8 → 9

---

## 十一、2026-07-17 澄清 · IP 视觉指纹 ≠ 地图

> **重要纠正**：原"ip-diagram-creator 与 guizang map-component 路径重叠（MapLibre + OSM 真实瓦片）"的描述是错误的。**ip-diagram-creator 从来不是地图技能**——它解决的是「博主 IP 视觉指纹 + Agent 协作图解」，跟地图没有任何交集。

### 实际重叠方
**真正与 guizang map-component 重叠的是 homegrown `dragon-engine/skills/map-component/`**（空壳规格），不是本主题文件里的 ip-diagram-creator。

### 详细决策记录
参见 [map-component-merge-decision.md](map-component-merge-decision.md)（主题文件 #13 · 2026-07-17）

### 红线
- 🔴 **不要**让 smart-illustrator / ppt-master / qiaomu-mondo 接管地图 POI
- ✅ **正确路由**："旅行/探店地图 + 小红书图文" → guizang map-component；"AI 工具关系图 / 博主 IP 知识卡 / Agent 协作图解" → smart-illustrator V2.2 或 ppt-master V9.9

---

## 十二、2026-07-17 路径修正

- 原记录：`dragon-engine/skills/ip-diagram-creator/SKILL.md`（**不存在**）
- 实际路径：`dragon-engine/skills/ip-diagram-creator-integration/SKILL.md`（integration 模块）
- 原仓库 haloshin/ip-diagram-creator 已退场，仅 4 个下游 skill 继承其设计哲学