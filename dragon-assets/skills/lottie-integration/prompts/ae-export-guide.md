# AE导出Bodymovin指南

## 设计师专用 · Bodymovin插件 · SVG/Canvas渲染优化

---

## 快速导出流程

```
AE项目 → Bodymovin面板 → 选择合成 → Render → 导出JSON
```

### 导出设置对照表

| AE设置 | Bodymovin设置 | 推荐值 | 原因 |
|--------|--------------|--------|------|
| **Renderer** | Renderer | **SVG** / Canvas | SVG可缩放、SEO友好；Canvas高性能 |
| **Guide** | Guides | ❌ 关闭 | 避免辅助线进入动画 |
| **Stretch** | Stretch | **0** | 避免帧拉伸变形 |
| **Optimize** | Optimize | ✅ 开启 | JSON体积优化20-40% |
| **ExtraSettings** | Hidden Layers | ❌ 关闭 | 减少冗余数据 |

---

## 推荐导出参数

### SVG渲染（推荐Logo/Icon/插画）

```
Renderer: SVG
Guide: Off
Stretch: 0
Optimize: On
ExtraSettings:
  - Guide: Off
  - Hidden Layers: Off
  - Text: On (转换为路径)
```

### Canvas渲染（推荐粒子/特效/高性能）

```
Renderer: Canvas
Guide: Off
Stretch: 0
Frame Rate: 30 (或60)
Optimize: On
```

---

## ✅ 完全支持的功能

| 功能 | AE操作 | lottie表现 | 注意事项 |
|------|--------|-----------|---------|
| **形状图层** | 矩形/椭圆/多边形/星形 | ✅ 完美 | 优先使用矢量形状 |
| **路径动画** | Position/Scale/Rotation | ✅ 完美 | BEZIER路径完全支持 |
| **预合成** | Pre-comp | ✅ 完美 | 嵌套动画独立播放 |
| **文字动画** | Basic/Per-character | ✅ 完美 | 需开启Text选项 |
| **固态层** | Solid | ✅ 完美 | 可做背景/色块 |
| **空对象** | Null Object | ✅ 完美 | 用于辅助控制 |
| **父子关系** | Parent | ✅ 完美 | 层级关系完整保留 |
| **蒙版** | Add/Subtract/Intersect | ✅ 完美 | 最常用Add模式 |
| **修边动画** | Trim Paths | ✅ 完美 | 描边动画首选 |
| **轨道遮罩** | Track Matte | ✅ 完美 | Alpha遮罩支持 |
| **描边动画** | Stroke-dashoffset | ✅ 完美 | SVG路径描边 |
| **颜色渐变** | Gradient Fill | ✅ 完美 | 线性/径向均支持 |
| **字符偏移** | Character Offset | ✅ 完美 | 打字机效果 |
| **字符轮转** | Character Rotation | ✅ 完美 | 文字旋转动画 |
| **透明度** | Opacity | ✅ 完美 | 淡入淡出 |
| **混合模式** | Normal/Add/Screen | ✅ 部分 | Add/Screen支持 |
| **位图图层** | Image Layers | ✅ 完美 | 需打包图片资产 |

---

## ⚠️ 部分支持的功能

| 功能 | AE操作 | lottie表现 | 替代方案 |
|------|--------|-----------|---------|
| **滑杆控制** | Slider Control | ⚠️ 需表达式 | 使用关键帧替代 |
| **遮罩混合** | Blend Modes | ⚠️ 部分 | 仅Normal/Add/Screen/Multiply |
| **渐变描边** | Gradient Stroke | ⚠️ 部分 | 使用纯色描边 |
| **3D相机** | Camera | ❌ 不支持 | 改用2D模拟视角 |
| **3D图层** | 3D Layer开关 | ❌ 不支持 | 全部2D化 |
| ** PSD导入** | Import PSD | ⚠️ 部分 | 导入后扁平化 |
| **段落文字** | Paragraph Text | ⚠️ 部分 | 使用点文字替代 |
| **音频** | Audio | ❌ 不支持 | 使用Audio-Driven timeline |
| **毛发烧灼** | Roughness | ❌ 不支持 | 使用粒子系统替代 |
| **碎片效果** | CC Scatterize | ❌ 不支持 | 使用Canvas粒子替代 |
| **发光** | Glow (效果) | ⚠️ 部分 | 使用模糊+叠加替代 |

---

## ❌ 完全不支持的功能

| 功能 | AE操作 | 原因 | 替代方案 |
|------|--------|------|---------|
| **表达式** | Expression | 部分支持 | 使用关键帧替代 |
| **某些混合模式** | Overlay/Soft Light等 | 浏览器不支持 | 改用支持模式 |
| **时间重映射** | Time Remap | 不支持 | 调整关键帧 |
| **音频频谱** | Audio Spectrum | 不支持 | 使用Canvas绘制 |
| **毛发效果** | Wiggle Expression | 不支持 | 简化动画 |
| **SDF文本** | SDF Rendering | 不支持 | 使用路径化文字 |
| **投影** | Drop Shadow (效果) | ⚠️ 部分 | 使用CSS投影 |

---

## 动画类型推荐

### 最佳场景（✅ 完全支持）

```
✅ Logo动画
   - 品牌开场动画
   - 企业Logo演绎
   - 产品Logo展示

✅ Icon动画
   - 功能演示动画
   - 交互反馈动画
   - 加载状态动画

✅ 插画动画
   - 故事叙述动画
   - 背景装饰动画
   - 人物角色动画

✅ 进度指示
   - 加载动画
   - 进度条
   - 数据可视化

✅ 描边动画
   - 路径绘制动画
   - 笔画书写效果
   - 地图流动效果
```

### 可行但需注意（⚠️ 部分支持）

```
⚠️ 表情动画
   - 简单表情变化
   - 建议：使用关键帧而非滑杆

⚠️ 数据图表动画
   - 柱状图/折线图动画
   - 建议：配合hyperframes chart组件

⚠️ 复杂渐变
   - 多层渐变叠加
   - 建议：减少渐变层数
```

---

## 性能优化技巧

### ✅ 推荐做法

```
1. 扁平化设计
   - 避免过深的图层嵌套
   - 减少预合成层级
   - 建议：最多3层嵌套

2. 简化路径
   - 使用Path Simplify插件
   - 减少贝塞尔曲线点数
   - 目标：每路径<100点

3. 统一帧率
   - 建议：30fps或60fps
   - 避免混用帧率

4. 合理尺寸
   - Logo建议：512x512
   - Icon建议：128x128或256x256
   - 全屏建议：1920x1080

5. 使用预合成
   - 重复使用的动画组
   - 独立播放的动画片段

6. 颜色优化
   - 使用设计系统色板
   - 减少渐变使用
```

### ❌ 避免做法

```
1. 过深嵌套
   - 超过5层预合成
   - 嵌套预合成中有遮罩

2. 复杂蒙版
   - 多个蒙版叠加
   - 不规则复杂路径

3. 大尺寸动画
   - 超过1MB的JSON
   - 4K以上分辨率

4. 逐帧动画
   - 序列图片导出的动画
   - 改用关键帧动画

5. 毛发/碎片
   - 消耗大量性能
   - 改用hyperframes粒子替代
```

---

## Bodymovin插件使用

### 安装BodBodymovin

```
1. 在AE中：Window → Extensions → Bodymovin
2. 如果没有Extensions菜单：
   - 打开ESR (ExtendScript Toolkit)
   - 运行BodBodymovin安装脚本
3. 重启AE
```

### 导出步骤

```
1. 打开BodBodymovin面板
   Window → Extensions → Bodymovin

2. 选择要导出的合成
   - 点击合成名称
   - 或拖拽合成到面板

3. 设置导出路径
   - 点击"Select Path"
   - 选择保存位置

4. 配置导出设置
   - Renderer: SVG (推荐)
   - Guide: Off
   - Optimize: On

5. 点击"Render"
   - 等待导出完成
   - 查看导出报告

6. 验证JSON
   - 使用 lottie_bridge.py validate
   - 确认无错误
```

### 批量导出

```
1. 在合成上右键
2. 选择 "Pre-compose"
3. 创建独立的合成
4. 在Bodymovin面板中
   - 勾选多个合成
   - 点击"Render Selected"
```

---

## 常见问题排查

### JSON导出为空或错误

```
问题：导出的JSON文件很小或为空
原因：合成包含不支持的元素
解决：
1. 检查合成是否有红色感叹号警告
2. 移除不支持的效果（如毛发、碎片）
3. 将3D图层转换为2D
```

### 动画播放异常

```
问题：动画在浏览器中表现与AE不一致
原因：渲染器或设置不匹配
解决：
1. 确认导出时使用的Renderer
2. 检查是否有表达式未转关键帧
3. 查看Bodymovin控制台警告信息
```

### 文件体积过大

```
问题：导出的JSON超过500KB
原因：路径点数过多或包含图片资产
解决：
1. 使用Optimize选项
2. 简化路径点数
3. 将图片压缩后再导入
4. 考虑使用dotLottie压缩
```

### 文字显示异常

```
问题：文字在浏览器中显示不正确
原因：字体或文字属性不支持
解决：
1. 在导出设置中开启Text选项
2. 将文字转换为路径（Outlines）
3. 避免使用特殊字体
```

---

## 设计师 × 开发者协作

### 交付清单

```
设计师交付给开发者：
□ .aep源文件（可选）
□ Bodymovin导出的.json文件
□ .json尺寸说明（宽x高）
□ 动画时长说明（秒数）
□ 循环/非循环说明
□ 包含的图片资产文件夹（如有）
□ Bodymovin导出设置截图
```

### 沟通要点

```
1. 动画类型
   - 入场动画/循环动画/结束动画
   - 触发方式（自动/点击/滚动）

2. 时间控制
   - 总时长
   - 关键时间点
   - 是否需要GSAP timeline同步

3. 交互需求
   - 是否有交互（hover/click）
   - 是否需要响应式

4. 性能要求
   - 目标帧率
   - 最大文件体积
```

---

## 快速检查清单

```
导出前检查：
□ 所有图层都是2D（无3D图层）
□ 无不支持的效果
□ 无表达式（已转关键帧）
□ 帧率统一（30或60）
□ 路径点数合理（<100/路径）
□ 图片资产已压缩
□ 动画时长合理（<30秒）

导出后验证：
□ JSON文件不为空
□ lottie_bridge.py validate通过
□ 浏览器中播放正常
□ 性能符合要求
```
