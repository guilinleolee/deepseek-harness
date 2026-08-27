---
name: 35-06-blogger-distiller
description: 35-06 博主蒸馏分析师 - 蒸馏博主风格 → Style Library 镜像 V1.0（基于 518 案例 + 21 工业模板反向工程）
version: 1.0
category: marketing-center
department: 营销中心-数字营销部
upgrade_trigger: 2026-06-23 freestylefly/awesome-gpt-image-2 + gpt-image-2-gallery-explorer
triggers:
  - "[@博主蒸馏分析师]"
  - "[@35-06]"
  - "博主风格蒸馏"
  - "博主风格镜像"
  - "风格提取"
  - "风格反向工程"
  - "博主模仿"
  - "blogger distiller"
---

# 35-06 博主蒸馏分析师 - V1.0（基于 518 案例反向工程）

## L0: 一句话描述 (≤15字)

**博主风格反向工程 → 工业化复制**

## L1: 使用场景 (50-100字)

**适用场景**：当用户需要**模仿某个博主/品牌/IP 的视觉风格**生成新内容时，使用本 skill：
1. 输入博主 5-20 张代表性图片
2. 从 518 案例中匹配最近模板（类目/风格/场景）
3. 蒸馏 6 维风格指纹（构图/色彩/字体/材质/光线/隐喻）
4. 输出可复用的 Style Library 镜像条目
5. 后续用 style-library 模板 + 博主风格变量，工业化复制

**触发关键词**：`[@博主蒸馏分析师]`、`[@35-06]`、博主风格蒸馏、博主镜像、风格反向工程、blogger distiller、视觉风格提取

## L2: 详细文档

### 核心能力矩阵

| 能力 | 版本 | 来源 | 说明 |
|------|------|------|------|
| **518 案例匹配** | V1.0 | gallery-explorer | 12 类目智能匹配 |
| **6 维风格指纹** | V1.0 | 自研 | 构图/色彩/字体/材质/光线/隐喻 |
| **Style Library 镜像** | V1.0 | style-library V2.0 | 输出镜像条目 |
| **工业化复用** | V1.0 | 21 模板 | 模板 + 博主变量 |
| **风格演化追踪** | V1.0 | 5 阶段 | 早期→成熟→巅峰→转型→式微 |
| **跨博主比较** | V1.0 | 多博主对照 | 异同点分析 |

### 6 维风格指纹（核心算法）

```
风格指纹 = {
  构图 (composition):     "居中对角三分法 / 9:16 竖屏 / 大量留白"
  色彩 (palette):         "#FF6B35 + #2C3E50 + #ECF0F1 暖橙主导"
  字体 (typography):      "无衬线 30% + 衬线 50% + 手写 20%"
  材质 (texture):         "纸质 60% + 金属 20% + 玻璃 20%"
  光线 (lighting):        "自然光 70% + 棚拍 20% + 戏剧 10%"
  隐喻 (metaphor):        "食物→生命力 / 城市→赛博朋克 / 人物→故事感"
}
```

### 5 阶段工作流

```
阶段 1: 输入采集（Input Gathering）
   输入：5-20 张博主代表性图片（用户上传 / 微博 / 抖音 / 小红书抓取）
   输出：图片清单 + 元数据（尺寸 / 拍摄时间 / 平台 / 互动数据）

阶段 2: 518 案例匹配（Case Matching）
   工具：gpt-image-2-gallery-explorer
   命令：query.py --keyword <博主风格关键词> --limit 20
   输出：候选案例集（20-50 个）

阶段 3: 6 维风格指纹提取（Fingerprint Extraction）
   - 用 GPT-Image-2 反向工程 prompt
   - 提取 6 维风格指纹
   - 标注差异（vs 主流模板）

阶段 4: Style Library 镜像（Library Mirroring）
   - 找到 21 套模板中最近的 3-5 套
   - 在 style-library.md 中追加镜像条目
   - 输出：distilled_<博主名>.yaml

阶段 5: 工业化复用（Industrial Replication）
   - 模板 + 博主变量 → 批量生成
   - 后端路由：APIMart（批量便宜）/ hiapi（4K）
   - 输出：N 张同风格新图
```

### 蒸馏流程示例

**用户请求**：
```
"我最近喜欢小红书博主 'xxx' 的风格，能不能蒸馏她的风格用于我的产品"
```

**天龙引擎响应**：

```bash
# Step 1: 输入采集
$ ls ./input/blogger_xxx/*.jpg
case-001.jpg case-002.jpg ... case-015.jpg  # 15 张代表性

# Step 2: 518 案例匹配
$ python ~/.claude/skills/gpt-image-2-gallery-explorer/scripts/query.py \
    --keyword "暖色 美食 居中" --limit 20

🔍 候选案例（20 条）：
  case-45 — 早餐盘平面摄影
  case-67 — 居中食物摆拍
  case-123 — 暖色调静物
  ...

# Step 3: 6 维风格指纹提取
$ python ~/.claude/skills/gpt-image-2-style-library/scripts/distill.py \
    --input ./input/blogger_xxx/ \
    --match-cases case-45,case-67,case-123

📊 风格指纹：
  构图: 居中俯拍（80%）/ 45度斜拍（20%）
  色彩: #F5E6D3 背景 + #D2691E 主食 + #556B2F 配菜
  字体: 不出现（纯图）
  材质: 木质桌面 70% / 大理石 20% / 棉麻 10%
  光线: 自然侧光 75% + 暖光 20% + 顶光 5%
  隐喻: 食物 = 慢生活 / 仪式感

# Step 4: Style Library 镜像
$ python ~/.claude/skills/gpt-image-2-style-library/scripts/mirror.py \
    --fingerprint ./blogger_xxx.yaml \
    --output ~/.claude/skills/gpt-image-2-style-library/references/distilled/blogger_xxx.yaml

✅ 已生成镜像条目（影响 style-library.md）

# Step 5: 工业化复用
$ python ~/.claude/skills/gpt-image-2-api-integration/scripts/template_generate.py \
    --template photography-realism \
    --distilled blogger_xxx \
    --vars '{"subject":"我的产品 X","context":"早餐场景"}' \
    --backend apimart \
    --count 10 --aspect 1:1

💰 成本：10 × $0.006 = $0.06
🎨 输出：10 张博主风格的产品图
```

### 风格演化追踪（5 阶段）

| 阶段 | 特征 | 检测方法 |
|------|------|----------|
| **早期（探索期）** | 风格不固定 / 模仿明显 | 风格相似度 < 0.4 |
| **成熟（定型期）** | 风格稳定 / 模板化 | 风格相似度 0.4-0.7 |
| **巅峰（爆发期）** | 风格独特 / 高互动 | 风格相似度 0.7-0.9 + 互动数据高 |
| **转型（突破期）** | 风格迭代 / 跨类目 | 风格相似度下降 + 新类目出现 |
| **式微（衰退期）** | 风格僵化 / 互动下降 | 风格相似度 > 0.95 + 互动持续低 |

### 与其他技能协同

| 技能 | 协同方式 |
|------|---------|
| **gpt-image-2-gallery-explorer** | 518 案例匹配 |
| **gpt-image-2-style-library** | 镜像条目写入 |
| **gpt-image-2-prompt-library** | 双源 prompt 复用 |
| **gpt-image-2-api-integration** | 后端批量生成 |
| **gpt-image-2-bridge** | 桥接到 Mondo/Baoyu/Smart-illustrator |
| **35-02 社媒运营** V13.1 | 蒸馏结果 → 社媒发布 |
| **35-05 短视频编导** V10.1 | 蒸馏风格 → 视频首帧 |
| **13-01 设计师** V11.11 | 蒸馏 → 模板资产化 |
| **28-01 文案策划** V10.1 | 蒸馏 → 文案视觉一致性 |

### 应用场景矩阵

| 场景 | 输入 | 输出 | 后端 |
|------|------|------|------|
| **产品种草** | 博主 15 张 + 产品 1 张 | 10 张同风格产品图 | APIMart（批量便宜）|
| **个人 IP 打造** | 创始人 10 张 + 品牌指南 | 50 张品牌风格图 | hiapi（4K + 永久）|
| **节日 Campaign** | 节日图 20 张 + 品牌指南 | 30 张 Campaign 图 | hiapi |
| **小红书矩阵号** | 博主 20 张 + 矩阵号定位 | 100 张批量图 | APIMart |
| **品牌 VI 升级** | 历史素材 30 张 | 新 VI 风格指南 + 样图 | hiapi |

### 蒸馏质量评分（10 分制）

| 维度 | 权重 | 评分 |
|------|------|------|
| **风格一致性**（vs 原作）| 30% | 1-10 |
| **构图还原度** | 15% | 1-10 |
| **色彩保真度** | 15% | 1-10 |
| **光线一致性** | 10% | 1-10 |
| **隐喻保留度** | 15% | 1-10 |
| **工业化可用性**（模板化）| 15% | 1-10 |
| **总分** | 100% | 蒸馏质量指数 DQI |

DQI ≥ 8：可直接工业化
DQI 6-8：需要人工微调
DQI < 6：重新蒸馏

### 与其他岗位的差异化

| 岗位 | 核心差异 |
|------|---------|
| **35-02 社媒运营** | 35-02 偏发布 / 35-06 偏风格提取 |
| **13-01 设计师** | 13-01 偏原创 / 35-06 偏反向工程 |
| **28-01 文案策划** | 28-01 偏文字 / 35-06 偏视觉风格 |
| **10-01 提示词架构师** | 10-01 偏构造 / 35-06 偏蒸馏 |

### 安装与验证

```bash
# 1. 验证依赖技能
ls ~/.claude/skills/gpt-image-2-{gallery-explorer,style-library,prompt-library,api-integration,bridge}

# 2. 准备输入
mkdir ./input/blogger_xxx
cp /path/to/representative/*.jpg ./input/blogger_xxx/

# 3. 运行蒸馏
python ~/.claude/skills/gpt-image-2-style-library/scripts/distill.py \
    --input ./input/blogger_xxx/ \
    --output ./output/blogger_xxx.yaml

# 4. 生成镜像
python ~/.claude/skills/gpt-image-2-style-library/scripts/mirror.py \
    --fingerprint ./output/blogger_xxx.yaml
```

### 注意事项

1. **版权风险**：蒸馏他人风格仅用于学习参考，不要完全复制 + 商标/水印
2. **数据隐私**：博主图片不上传到云端，本地处理
3. **风格可解释性**：6 维指纹必须可解释，不能是黑盒
4. **持续更新**：博主风格会演化，建议每 3 个月重新蒸馏

### 版本演进

| 版本 | 日期 | 关键变更 |
|------|------|---------|
| **V1.0** | **2026-06-23** | **初始版（基于 518 案例 + 21 模板 + 6 维指纹 + 5 阶段流程）** |

### 版本信息

- **Version**: 1.0
- **Author**: 天龙引擎集成
- **Last Updated**: 2026-06-23
- **Dependencies**: gpt-image-2-gallery-explorer / style-library / api-integration / bridge