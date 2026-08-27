# 4 维推理 brief 模板 · nano-banana-brief V1.0

> **来源**：天龙自研 + 借调 gpt-image-2-prompt-library 21 模板 + freestylefly/awesome-gpt-image-2 reasoning brief 范式
> **触发**：nano-banana-brief `generate.sh` 选中后，按 4 维自动填 prompt

---

## 1. subject（主体）· 必填

**4 元素必填**：年龄 + 性别 + 服饰 + 神态

### 1.1 模板

```
{年龄段}{性别}{服饰描述}，{神态描述}，{特殊标记}
```

### 1.2 老李风典型 subject

| 模板 | 完整 subject |
|------|-------------|
| 默认老李 | "中年男性（约 40 岁），深棕色围裙 + 灰白衬衫，思考中带着确定的眼神，鬓角有白发" |
| 老李青年 | "青年男性（约 28 岁），白 T 恤 + 牛仔裤，专注低头阅读，手指轻敲书脊" |
| 老李演讲 | "中年男性（约 45 岁），立领衬衫 + 深蓝西装外套，双手打开演讲姿态，灯光从左上方 45°" |
| 老李收束 | "中年男性（约 50 岁），素色围裙 + 老花镜，微笑但眼神坚定，站在门口远眺" |

### 1.3 反 AI slop（来自 awesome-gpt-image-2）

- ❌ **不要**只写 "a man" / "a person" → 必须含年龄+服饰+神态
- ❌ **不要**加 emoji / 装饰物 → 老李风禁忌
- ❌ **不要**用 "beautiful" / "handsome" / "cute" 等空泛形容词
- ✅ **要**用"中年人"、"围裙"、"鬓角白发"等具体描述
- ✅ **要**写出"在做什么"（思考 / 阅读 / 演讲 / 远眺）

---

## 2. scene（场景）· 必填

**3 元素必填**：地点 + 陈设 + 质感

### 2.1 模板

```
{地点描述}，{陈设清单}，{质感描述}
```

### 2.2 老李风典型 scene

| 模板 | 完整 scene |
|------|----------|
| 牛皮纸咖啡馆 | "牛皮纸质感的小咖啡馆角落，木桌 + 老式台灯 + 半杯咖啡，桌上有牛皮纸笔记本" |
| 老书房 | "老式书房，藤编书架 + 老式台灯 + 散落书页，墙上挂中国书法横卷，午后阳光从百叶窗洒入" |
| 工厂车间 | "老式机械车间背景，金属车床 + 木质工具箱 + 半成品零件，暖色工业灯" |
| 山间小路 | "山间小路，碎石路面 + 路边野花 + 远处云海，午后斜阳从侧面 45° 照射" |
| 冬日小镇 | "北方小镇街道，积雪屋顶 + 木制电线杆 + 老式自行车，远景烟囱冒白烟" |

### 2.3 反 AI slop

- ❌ **不要**写 "in a beautiful place" → 必须具体地点
- ❌ **不要**写 "magical / fantasy / dreamy" → 老李风必须是现实主义
- ❌ **不要**纯 CG 风格场景 → 必须有真实质感
- ✅ **要**写出"具体陈设"（不是 "some furniture"）
- ✅ **要**写出"质感"（牛皮纸 / 金属 / 木质 / 积雪）

---

## 3. style（风格）· 选填（天龙 21 模板）

**默认**：kraft-paper editorial（老李风最常用）

### 3.1 天龙 21 模板速查（gpt-image-2-prompt-library 内置）

| 模板 ID | 名称 | 适用场景 |
|--------|------|---------|
| template_01 | kraft-paper editorial | 老李风默认 |
| template_02 | swiss-ikb | 信息图 / 数据 |
| template_03 | editorial-midnight | 公众号深度长文 |
| template_04 | new-york-magazine | 评测 / 观点 |
| template_05 | reuters-news | 资讯 / 快讯 |
| template_06 | bbc-documentary | 纪录片风格 |
| template_07 | national-geographic | 自然 / 探索 |
| template_08 | apple-keynote | 科技 / 产品 |
| template_09 | redbook-wellness | 健康 / 生活 |
| template_10 | tmagazine | 时装 / 设计 |
| ... | ... | ... |
| template_21 | ink-wash | 水墨风 |

### 3.2 反 AI slop

- ❌ **不要**用 "cinematic / 8k / ultra-realistic" 等空泛词
- ❌ **不要**混搭多种风格（kraft-paper + cyberpunk）
- ✅ **要**从天龙 21 模板中选一个
- ✅ **要**在 prompt 中写明风格名（让 gpt-image-2 准确匹配）

---

## 4. light（光线）· 选填

**默认**：warm-ink-45deg（老李风最常用）

### 4.1 天龙内置光线

| 光线 ID | 描述 |
|--------|------|
| warm-ink-45deg | 暖棕色光从右上方 45° 入射（老李风默认）|
| cool-ikb-overhead | 冷蓝色顶光 |
| golden-hour-side | 黄昏侧光（金色）|
| midday-top | 正午顶光（中性）|
| indoor-warm-soft | 室内暖柔光 |
| candlelight-low | 烛光低位（暖红）|
| moonlight-cool-side | 月光冷侧光 |
| backlit-rim | 逆光轮廓 |
| studio-key-fill | 棚拍 key+fill |
| natural-diffuse | 自然漫射（阴天）|

### 4.2 反 AI slop

- ❌ **不要**只写 "soft light" / "natural light"
- ✅ **要**写明方向（45° / 顶光 / 侧光 / 逆光）+ 色温（暖 / 冷 / 中性）+ 强度（soft / hard）

---

## 5. 完整 prompt 模板

```markdown
# 推理 brief 输出

subject: {subject 4 元素}
scene: {scene 3 元素}
style: {style ID}
light: {light ID}

camera: 50mm prime, f/2.8, eye-level
lens: 35mm cinematic
post: subtle grain, warm ink shadow
mood: ordinary person thinking clearly
ratio: 3:4 (xhs) / 21:9 (wechat cover) / 1:1 (square)
```

**老李风完整 prompt 例子**：

```
A middle-aged man (~40 years old) wearing a dark brown apron over a 
gray-white shirt, eyes showing thoughtful certainty with some gray 
hair at the temples, sitting in a kraft-paper texture coffee shop 
corner with a wooden table and old-style desk lamp, half cup of 
coffee, kraft paper notebook on the table. Style: kraft-paper 
editorial. Light: warm-ink-45deg (warm brown light from upper-right 
at 45 degrees). Camera: 50mm prime f/2.8 eye-level. Lens: 35mm 
cinematic. Post: subtle grain, warm ink shadow. Mood: ordinary 
person thinking clearly.
```

---

## 6. 协同矩阵

| 维度 | 输入 | 输出 |
|------|------|------|
| subject | 关键词 → 4 元素 | "中年男性 ... 围裙 ..." |
| scene | 关键词 → 3 元素 | "牛皮纸咖啡馆 ... 木桌 ..." |
| style | 天龙 21 模板 ID | "kraft-paper editorial" |
| light | 天龙光线 ID | "warm-ink-45deg" |
| camera + lens + post | 默认值 | "50mm f/2.8 ... 35mm cinematic" |
| **完整 prompt** | 4 维 + camera | 直接喂 gpt-image-2 |

---

## 7. 反 AI slop 总览（11 条）

1. ❌ "a man" / "a person" → ✅ 含年龄+性别+服饰+神态
2. ❌ "beautiful place" → ✅ 具体地点
3. ❌ "cinematic / 8k / ultra-realistic" → ✅ 天龙 21 模板
4. ❌ "soft light" → ✅ 方向+色温+强度
5. ❌ emoji / sticker / AR 特效 → ✅ 现实主义
6. ❌ 纯 CG 场景 → ✅ 真实质感
7. ❌ "magical / fantasy / dreamy" → ✅ 老李风=现实主义
8. ❌ 混搭多种风格 → ✅ 一种风格
9. ❌ "in a beautiful place" → ✅ "牛皮纸咖啡馆"
10. ❌ 空泛形容词（beautiful / handsome / cute） → ✅ 具体描述
11. ❌ "some furniture" → ✅ 具体陈设清单

---

**How to apply**：nano-banana-brief 的 `generate.sh` 会按本模板自动补全 4 维，本文件是设计参考。