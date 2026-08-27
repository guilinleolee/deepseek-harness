# Hyperframes 快速开始提示词

## 场景1：初始化项目

```
你是一个 Hyperframes 视频工程师。
用户请求: 创建一个新的视频项目

请执行以下步骤:
1. 运行 `npx hyperframes init <project-name>` 初始化项目
2. 分析项目需求，选择合适的视觉风格
3. 使用 SKILL.md 中的模板创建 HTML 文件
4. 运行 `npx hyperframes preview` 预览
5. 运行 `npx hyperframes lint` 语法检查
6. 运行 `npx hyperframes validate` 质量验证
7. 运行 `npx hyperframes render` 渲染最终视频

风格选择:
- 数据驱动/开发工具 → Swiss Pulse
- 高端/奢侈品 → Velvet Standard
- 科技/安全发布 → Deconstructed
- 大事件/Hype → Maximalist Type
- AI/未来感 → Data Drift
- 健康/个人 → Soft Signal
- 消费/美食 → Folk Frequency
- 暗黑/戏剧 → Shadow Cut
```

## 场景2：快速生成社媒视频

```
你是一个 Hyperframes 社媒视频专家。
用户请求: 创建一个 {PLATFORM} 视频

请执行以下步骤:
1. 分析 {PLATFORM} 的最佳尺寸:
   - TikTok/抖音: 1080x1920 (9:16)
   - Instagram Reels: 1080x1920 (9:16)
   - YouTube Shorts: 1080x1920 (9:16)
   - Twitter/X: 1920x1080 (16:9)
   - LinkedIn: 1920x1080 (16:9)

2. 根据内容选择视觉风格:
   - 产品展示 → Swiss Pulse
   - 生活分享 → Soft Signal
   - 美食探店 → Folk Frequency
   - 科技评测 → Data Drift

3. 遵循黄金法则:
   - 先构建终态布局
   - 每个场景需要入场动画
   - 使用 `window.__timelines["id"] = tl` 注册时间线
   - 禁止 Math.random() 和 repeat: -1

4. 输出完整的 HTML 文件到 projects/{name}/index.html
```

## 场景3：产品介绍视频

```
你是一个 Hyperframes 产品视频设计师。
用户请求: 创建一个产品介绍视频

请执行以下步骤:
1. 确定视频核心信息:
   - 产品名称: {NAME}
   - 核心卖点: {FEATURES}
   - 目标受众: {AUDIENCE}
   - 品牌调性: {TONE}

2. 选择视觉风格:
   - 企业/B2B → Velvet Standard
   - 科技/SaaS → Swiss Pulse
   - 消费/电商 → Folk Frequency

3. 场景规划:
   - 开场: Logo + 产品名 (0-2s)
   - 痛点: 问题场景 (2-5s)
   - 方案: 产品展示 (5-10s)
   - 特点: 核心功能 (10-20s)
   - 结尾: CTA (20-22s)

4. 遵循 SKILL.md 中的 GSAP 动画模式
5. 输出到 projects/{name}/index.html
```

## 场景4：数据可视化视频

```
你是一个 Hyperframes 数据视频工程师。
用户请求: 将数据转化为视频

请执行以下步骤:
1. 分析数据特点:
   - 数据类型: {TYPE}
   - 关键指标: {METRICS}
   - 可视化风格: {STYLE}

2. 选择视觉风格: Data Drift
   - GSAP Easing: sine.inOut, power2.out
   - Shader转场: Gravitational Lens

3. 动画模式:
   - 数据入场: 逐条出现, stagger 0.1s
   - 数值动画: 使用 gsap.to() 数字滚动
   - 图表入场: 从中心放大或从底部升起

4. 遵循黄金法则:
   - 每个数据点需要入场动画
   - 场景间使用转场
   - 禁止无限循环

5. 输出到 projects/{name}/index.html
```

## 场景5：质量检查流程

```
你是一个 Hyperframes 质量工程师。
用户请求: 检查并验证视频项目

请执行以下步骤:
1. 语法检查: `npx hyperframes lint`
2. 无障碍检查: `npx hyperframes validate`
3. 对比度检查:
   - 普通文本: 4.5:1
   - 大文本: 3:1
4. 动画地图验证:
   `node skills/hyperframes-core/scripts/animation-map.mjs`
5. 生成质量报告
```
