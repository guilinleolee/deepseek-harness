# Hyperframes 8种视觉风格指南

## 1. Swiss Pulse（瑞士脉动）

**情绪**: 临床精准、现代高效

**适用场景**:
- SaaS 产品演示
- 数据仪表板
- 开发工具介绍
- 技术文档视频

**设计特征**:
- 简洁的几何形状
- 高对比度色彩
- 无衬线字体 (Inter, Roboto)
- 大量留白
- 网格布局

**GSAP Easing**:
```javascript
ease: "expo.out"      // 入场
ease: "power4.out"     // 强调
```

**Shader转场**: Cinematic Zoom
```html
<shader transition="cinematic-zoom" intensity="0.3" />
```

**示例模板**:
```html
<div style="background: #FFFFFF; font-family: Inter;">
  <h1 style="color: #1a1a1a; font-size: 72px; font-weight: 700;">
    简洁有力
  </h1>
</div>
```

---

## 2. Velvet Standard（丝绒经典）

**情绪**: 高端经典、优雅从容

**适用场景**:
- 奢侈品品牌
- 企业演讲
- 品牌故事
- 高端服务

**设计特征**:
- 深色背景 (深蓝、深紫)
- 金色/玫瑰金点缀
- 衬线字体 (Playfair, Cormorant)
- 渐变和阴影
- 微妙的光效

**GSAP Easing**:
```javascript
ease: "sine.inOut"     // 平滑
ease: "power1"          // 温和
```

**Shader转场**: Cross-Warp Morph
```html
<shader transition="cross-warp-morph" intensity="0.5" />
```

**示例模板**:
```html
<div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);">
  <h1 style="color: #d4af37; font-family: Playfair Display; font-size: 80px;">
    奢华质感
  </h1>
</div>
```

---

## 3. Deconstructed（解构主义）

**情绪**: 工业原始、打破常规

**适用场景**:
- 科技产品发布
- 安全/加密主题
- 前卫品牌
- 黑客文化

**设计特征**:
- 故障艺术 (Glitch Art)
- 像素化/马赛克效果
- 不对称布局
- 原始工业元素
- 高对比度闪烁

**GSAP Easing**:
```javascript
ease: "back.out(2.5)"  // 弹跳
ease: "steps(8)"        // 阶梯
```

**Shader转场**: Glitch
```html
<shader transition="glitch" intensity="0.7" rgb-shift="10" />
```

**示例模板**:
```html
<div style="background: #0a0a0a;">
  <h1 style="color: #00ff00; font-family: monospace; font-size: 64px;
             text-shadow: 2px 0 #ff0000, -2px 0 #00ffff;">
    解构_破坏
  </h1>
</div>
```

---

## 4. Maximalist Type（极致喧嚣）

**情绪**: 高能喧嚣、视觉冲击

**适用场景**:
- 大事件发布
- 音乐节/演唱会
- 体育赛事
- 产品促销

**设计特征**:
- 超大字体 (200px+)
- 鲜艳色彩
- 多层次叠加
- 动态模糊
- 爆炸性元素

**GSAP Easing**:
```javascript
ease: "expo.out"       // 爆发
ease: "back.out(1.8)"  // 回弹
```

**Shader转场**: Ridged Burn
```html
<shader transition="ridged-burn" intensity="0.6" />
```

**示例模板**:
```html
<div style="background: #ff0066;">
  <h1 style="color: #ffff00; font-size: 200px; font-weight: 900;
             transform: skewX(-5deg);">
    超大字体
  </h1>
</div>
```

---

## 5. Data Drift（数据漂流）

**情绪**: 未来沉浸、科技前沿

**适用场景**:
- AI/ML 产品
- 科技前沿
- 数据可视化
- 太空/科幻主题

**设计特征**:
- 深色背景 + 发光元素
- 网格/粒子背景
- 霓虹色彩 (青色、紫色)
- 流动/漂浮动画
- 3D 透视效果

**GSAP Easing**:
```javascript
ease: "sine.inOut"     // 流畅
ease: "power2.out"      // 自然
```

**Shader转场**: Gravitational Lens
```html
<shader transition="gravitational-lens" intensity="0.4" />
```

**示例模板**:
```html
<div style="background: #0a0a1a;">
  <h1 style="color: #00ffff; font-size: 72px;
             text-shadow: 0 0 20px #00ffff;">
    数据漂流
  </h1>
  <div class="grid-bg" style="background: linear-gradient(90deg, rgba(0,255,255,0.1) 1px, transparent 1px);"></div>
</div>
```

---

## 6. Soft Signal（柔和信号）

**情绪**: 温暖亲密、治愈人心

**适用场景**:
- 健康/医疗
- 个人故事
- 心理关怀
- 教育内容

**设计特征**:
- 柔和色彩 (粉色、淡蓝、奶油色)
- 圆润形状
- 轻柔阴影
- 手绘/插画元素
- 舒适的留白

**GSAP Easing**:
```javascript
ease: "sine.inOut"          // 柔和
ease: "power1.inOut"        // 平缓
```

**Shader转场**: Thermal Distortion
```html
<shader transition="thermal-distortion" intensity="0.3" />
```

**示例模板**:
```html
<div style="background: #fff5f5;">
  <h1 style="color: #e88b8b; font-family: Quicksand; font-size: 64px;
             font-weight: 500;">
    温暖柔和
  </h1>
</div>
```

---

## 7. Folk Frequency（民俗频率）

**情绪**: 文化鲜明、地域特色

**适用场景**:
- 消费应用
- 美食探店
- 社区内容
- 生活方式

**设计特征**:
- 鲜艳民俗色彩
- 传统图案纹理
- 手写字体
- 拼贴艺术
- 波普元素

**GSAP Easing**:
```javascript
ease: "back.out(1.6)"   // 活力
ease: "elastic.out"      // 弹性
```

**Shader转场**: Swirl Vortex
```html
<shader transition="swirl-vortex" intensity="0.5" />
```

**示例模板**:
```html
<div style="background: #f4e4bc;">
  <h1 style="color: #c45c26; font-family: Permanent Marker; font-size: 72px;">
    民俗风格
  </h1>
</div>
```

---

## 8. Shadow Cut（暗影切割）

**情绪**: 暗黑电影、戏剧揭示

**适用场景**:
- 戏剧性叙事
- 安全/监控主题
- 神秘/悬疑
- 电影预告

**设计特征**:
- 深黑背景
- 光影对比
- 聚光灯效果
- 电影感色调
- 缓慢推移

**GSAP Easing**:
```javascript
ease: "power4.in"      // 沉重入场
ease: "power3.out"      // 缓慢离场
```

**Shader转场**: Domain Warp
```html
<shader transition="domain-warp" intensity="0.6" />
```

**示例模板**:
```html
<div style="background: #000000;">
  <h1 style="color: #ffffff; font-size: 80px; font-family: Bebas Neue;
             letter-spacing: 0.1em;">
    暗影切割
  </h1>
  <div style="background: radial-gradient(ellipse at center, rgba(255,255,255,0.1) 0%, transparent 70%);"></div>
</div>
```

---

## 风格选择决策树

```
内容类型 → 推荐风格
├── 数据/开发工具 → Swiss Pulse
├── 高端/奢侈品 → Velvet Standard
├── 科技/安全 → Deconstructed
├── 大事件/促销 → Maximalist Type
├── AI/未来 → Data Drift
├── 健康/个人 → Soft Signal
├── 消费/美食 → Folk Frequency
└── 戏剧/神秘 → Shadow Cut
```
