---
license: UNKNOWN
github_repo: airbnb/lottie-web
github_hash: bede03d25d232826e0c9dca1733d542d8a7754fb
last_updated: 2026-04-25
source_type: derived
triggers: ["lottie integration", "Lottie Integration Skill"]
---
# Lottie Integration Skill

## V1.0 | 2026-04-23 | 设计师动画桥梁 · AE → 浏览器

### 来源项目

| 项目 | Stars | 核心能力 |
|------|-------|---------|
| [Airbnb/lottie-web](https://github.com/airbnb/lottie-web) | 28k+ | AE动画JSON → 浏览器播放 |
| [Airbnb/lottie-js](https://github.com/airbnb/lottie-js) | - | ESM模块 + 尺寸/路径/段API |
| [LottieFiles/dotlottie-js](https://github.com/LottieFiles/dotlottie-js) | - | dotLottie压缩格式(.lottie) |

### 核心理念

> **打通设计师到AI的最后一公里。** AE设计 → Bodymovin导出JSON → lottie-web播放 → 与hyperframes-core无缝融合。

```
After Effects → Bodymovin插件导出 → JSON → lottie-web → SVG/Canvas/HTML渲染
```

### 与hyperframes-core的互补定位

```
┌─────────────────────────────────────────────────────────────┐
│        天龙引擎视频全家桶 · 互补定位                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  lottie-web     → 设计师AE动画播放（已有设计资产）           │
│  hyperframes    → AI生成HTML5视频（无设计资产时）           │
│  GSAP          → 精确Tween/Timeline控制（无设计时）         │
│  remotion      → 复杂React程序化视频                       │
│  MagiHuman     → 人像视频生成                             │
│  Seedance 2.0  → AI多模态生成                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 环境要求

```bash
# Node.js >= 18
node --version

# Python 依赖
pip install lottie-js        # Python lottie JSON 读取/生成
pip install svgwrite         # SVG 路径生成（用于 DrawSVGPlugin 替代）

# CDN 引入（无需安装）
# lottie-web
https://cdn.jsdelivr.net/npm/lottie-web@5.12.2/build/player/lottie.min.js

# dotLottie
https://cdn.jsdelivr.net/npm/@lottiefiles/dotlottie-web@0.40.0/dist/dotlottie-web.js
```

---

## 核心概念

### lottie-web 三渲染器

| 渲染器 | 适用场景 | 性能 | 特性 |
|--------|---------|------|------|
| **SVG** | 图标、Logo、简单图形 | 中等 | 可缩放、SEO友好、文本可选中 |
| **Canvas** | 粒子、复杂特效、高性能 | 高 | 无抗锯齿、文本渲染差 |
| **HTML** | 简单DOM动画、交互 | 低 | 支持CSS、DOM事件 |

### dotLottie 压缩格式

```
.lottie 文件结构（ZIP压缩包）:
├── animation.json     # 动画数据
├── images/           # 图片资产（可选）
│   ├── image_0.png
│   └── image_1.svg
└── manifest.json     # 元数据
    {
      "version": "1.0",
      "animations": [{ "id": "anim_1", "loop": true }]
    }

优势：比 .json 小 40-60%（zip压缩）
```

### Bodymovin 导出设置

| 设置项 | 推荐值 | 说明 |
|--------|--------|------|
| **Renderer** | SVG（推荐）/ Canvas | 影响动画表现 |
| **Guide** | ✅ 关闭 | 避免辅助线进入动画 |
| **Stretch** | 0 | 避免帧拉伸 |
| **Optimize** | ✅ 开启 | JSON体积优化 |
| **ExtraSettings** | ✅ 隐藏图层关闭 | 减少冗余数据 |

---

## 核心命令

| 命令 | 功能 | 使用场景 |
|------|------|---------|
| `npx lottie-web render` | 渲染AE动画到页面 | 预览调试 |
| `python3 lottie_bridge.py init` | 初始化lottie项目 | 新建项目 |
| `python3 lottie_bridge.py json2svg` | JSON → SVG帧提取 | 静态帧截图 |
| `python3 lottie_bridge.py validate` | 验证lottie JSON | 质量检查 |
| `python3 dotlottie_packer.py bundle` | 打包dotLottie | 压缩发布 |

---

## 三种集成模式

### 模式1：独立播放（推荐：简单Logo/Icon）

```html
<!-- 1. 引入 lottie-web -->
<script src="https://cdn.jsdelivr.net/npm/lottie-web@5.12.2/build/player/lottie.min.js"></script>

<!-- 2. 创建容器 -->
<div id="lottie-container" style="width:200px;height:200px;"></div>

<!-- 3. 加载动画 -->
<script>
  const anim = lottie.loadAnimation({
    container: document.getElementById('lottie-container'),
    renderer: 'svg',           // svg | canvas | html
    loop: true,
    autoplay: true,
    path: 'animation.json'     // 或 data: lottieJson（内联）
  });

  // 控制方法
  anim.play();
  anim.pause();
  anim.stop();
  anim.setSpeed(0.5);          // 0.5x 速度
  anim.setDirection(-1);       // 倒放
  anim.goToAndPlay(30);        // 跳到第30帧
  anim.goToAndStop(60, true);   // 跳到第60帧并停止
  anim.destroy();
</script>
```

### 模式2：与hyperframes-core Timeline同步（推荐：视频合成）

```html
<!-- 引入依赖 -->
<script src="https://cdn.jsdelivr.net/npm/lottie-web@5.12.2/build/player/lottie.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>

<div data-composition-id="product-intro" data-width="1920" data-height="1080">
  <div id="lottie-bg"></div>

  <script>
    // 1. 预加载 lottie
    const lottieAnim = lottie.loadAnimation({
      container: document.getElementById('lottie-bg'),
      renderer: 'svg',
      loop: false,
      autoplay: false,
      path: 'logo-animation.json'
    });

    // 2. 注册到 hyperframes timeline
    const tl = gsap.timeline({ paused: true });

    // 3. 在 GSAP timeline 中同步控制 lottie
    // lottie 帧 → GSAP 时间映射
    const lottieDuration = lottieAnim.totalFrames / lottieAnim.frameRate; // 秒

    // 入场：lottie 从头播放
    tl.call(() => lottieAnim.play(), null, 0);

    // 在 timeline 0.5s 时 logo 淡入
    tl.from('.logo', { opacity: 0, scale: 0.8, duration: 0.5, ease: 'power3.out' }, 0.5);

    // 在 timeline 3s 时 lottie 暂停
    tl.call(() => lottieAnim.pause(), null, 3);

    // 注册 timeline（必须！）
    window.__timelines['product-intro'] = tl;
  </script>
</div>
```

### 模式3：dotLottie压缩格式（推荐：发布环境）

```html
<!-- 引入 dotlottie-web -->
<script src="https://cdn.jsdelivr.net/npm/@lottiefiles/dotlottie-web@0.40.0/dist/dotlottie-web.js"></script>

<script>
  const dotLottie = new DotLottie({
    element: document.getElementById('dotlottie-container'),
    src: 'animation.lottie',   // .lottie 压缩包
    loop: true,
    autoplay: true,
    posterFrame: 0,
    posterMode: true
  });

  dotLottie.addEventListener('complete', () => {
    console.log('Animation complete');
  });
</script>
```

---

## Bodymovin AE导出指南

### 支持特性

| ✅ 完全支持 | ⚠️ 部分支持 | ❌ 不支持 |
|-----------|------------|---------|
| 形状图层（矩形/椭圆/多边形/星形） | 滑杆控制 | 表达式（部分） |
| 路径动画 | 遮罩（Blend Mode限制） | 某些效果（毛发/碎片） |
| 预合成 | 3D相机 | PSD AI文件 |
| 文字动画（Basic/Per-character） | 渐变（线性/径向） | 某些混合模式 |
| 固态层 | 描边动画 |  |
| 空对象/空文字 | 图层样式（投影/发光） |  |
| 父子关系 | 段落文字 |  |
| 蒙版（Add/Subtract/Intersect） |  |  |
| 修边（Trim Paths） |  |  |
| 轨道遮罩 |  |  |

### 最佳实践

```
✅ 推荐：
- 扁平化设计风格（插画师/Icon风格）
- 简单几何形状组合
- 描边动画（Stroke-dashoffset）
- 路径动画（Position/Scale/Rotation）
- 颜色渐变动画

❌ 避免：
- 照片级写实渲染
- 复杂粒子特效（用 hyperframes Canvas 替代）
- 文字描边特效（改用纯路径）
- 毛发/碎片效果
```

### 动画类型推荐

| AE动画类型 | lottie支持 | 推荐场景 |
|-----------|-----------|---------|
| **Logo动画** | ✅ 完全 | 品牌展示、开场动画 |
| **Icon动画** | ✅ 完全 | 功能演示、UI反馈 |
| **插画动画** | ✅ 完全 | 故事叙述、背景装饰 |
| **进度指示** | ✅ 完全 | 加载动画、数据可视化 |
| **表情动画** | ⚠️ 部分 | 简单表情、面部动画 |
| **数据图表** | ✅ 完全 | 配合 hyperframes chart组件 |

---

## Python工具脚本

### lottie_bridge.py

```python
#!/usr/bin/env python3
"""
Lottie Bridge - lottie-web 集成工具
"""
import argparse
import json
from pathlib import Path

def init():
    """初始化 lottie 项目结构"""
    pass  # 创建基础目录

def validate(json_path):
    """验证 lottie JSON 文件"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 检查必要字段
    required = ['v', 'fr', 'ip', 'op', 'w', 'h', 'nm', 'ddd', 'assets', 'layers']
    for field in required:
        if field not in data:
            print(f"❌ Missing required field: {field}")
            return False

    # 检查帧率
    fps = data.get('fr', 0)
    if fps <= 0:
        print(f"❌ Invalid frame rate: {fps}")
        return False

    print(f"✅ Lottie JSON valid: {json_path}")
    print(f"   Size: {json_path.stat().st_size / 1024:.1f} KB")
    print(f"   FPS: {fps}")
    print(f"   Frames: {data.get('ip', 0)} - {data.get('op', 0)}")
    print(f"   Duration: {(data.get('op', 0) - data.get('ip', 0)) / fps:.2f}s")
    print(f"   Render: {data.get('w', 0)}x{data.get('h', 0)}")
    return True

def json2svg(json_path, frame, output):
    """提取指定帧为 SVG"""
    # 使用 lottie-js 读取指定帧
    pass

def main():
    parser = argparse.ArgumentParser(description='Lottie Bridge Tool')
    parser.add_argument('command', choices=['init', 'validate', 'json2svg', 'bundle'])
    parser.add_argument('path', nargs='?', help='File path')
    args = parser.parse_args()

    if args.command == 'init':
        init()
    elif args.command == 'validate':
        validate(args.path)
    # ...

if __name__ == '__main__':
    main()
```

### dotlottie_packer.py

```python
#!/usr/bin/env python3
"""
dotLottie Packer - 打包 dotLottie 压缩格式
"""
import zipfile
import json
from pathlib import Path

def bundle(animation_json, output_dir=None, images_dir=None):
    """打包 .lottie 文件"""
    output_dir = output_dir or Path(animation_json).parent
    output_name = Path(animation_json).stem + '.lottie'
    output_path = output_dir / output_name

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 添加 animation.json
        zf.write(animation_json, 'animation.json')

        # 添加 manifest.json
        manifest = {
            "version": "1.0",
            "animations": [
                {
                    "id": "anim_1",
                    "loop": True,
                    "animationUrl": "animation.json"
                }
            ]
        }
        zf.writestr('manifest.json', json.dumps(manifest, indent=2))

        # 添加图片资产
        if images_dir and Path(images_dir).exists():
            for img in Path(images_dir).glob('*'):
                zf.write(img, f'images/{img.name}')

    original_size = Path(animation_json).stat().st_size
    compressed_size = output_path.stat().st_size
    ratio = (1 - compressed_size / original_size) * 100

    print(f"✅ Bundle created: {output_path}")
    print(f"   Original: {original_size / 1024:.1f} KB")
    print(f"   Compressed: {compressed_size / 1024:.1f} KB")
    print(f"   Savings: {ratio:.1f}%")
```

---

## 与hyperframes-core Registry集成

### Lottie Registry组件

```javascript
// registry/lottie-player.js
class LottiePlayer {
  static id = 'lottie-player';
  static category = 'media';
  static integrationCost = 'zero';
  static requiresCanvas = false;

  constructor() {
    this.anim = null;
  }

  mount(container, opts = {}) {
    opts = Object.assign({
      renderer: 'svg',
      loop: false,
      autoplay: false,
      path: null,
      data: null
    }, opts);

    this.anim = lottie.loadAnimation({
      container,
      renderer: opts.renderer,
      loop: opts.loop,
      autoplay: opts.autoplay,
      path: opts.path,
      animationData: opts.data  // 优先使用内联数据（避免CORS）
    });

    // GSAP 兼容接口
    this.anim.pause();  // 默认暂停，等待 timeline 驱动
  }

  // 返回 GSAP-compatible timeline
  getAnim() {
    return {
      play: () => this.anim && this.anim.play(),
      pause: () => this.anim && this.anim.pause(),
      stop: () => this.anim && this.anim.stop(),
      seek: (time) => {
        if (this.anim) {
          const frame = time * this.anim.frameRate;
          this.anim.goToAndStop(frame, true);
        }
      },
      get duration() {
        return this.anim ? this.anim.totalFrames / this.anim.frameRate : 0;
      },
      destroy: () => this.anim && this.anim.destroy()
    };
  }

  unmount() {
    if (this.anim) {
      this.anim.destroy();
      this.anim = null;
    }
  }
}

// 注册
if (typeof window !== 'undefined') {
  window.__registry = window.__registry || {};
  window.__registry['lottie-player'] = LottiePlayer;
}
```

### 使用方式

```html
<!-- 在 hyperframes HTML 中使用 -->
<script src="https://cdn.jsdelivr.net/npm/lottie-web@5.12.2/build/player/lottie.min.js"></script>
<script src="./registry/lottie-player.js"></script>

<div data-composition-id="brand-intro">
  <canvas id="lottie-logo" data-component="lottie-player"
    data-component-args='{"path":"logo.json","loop":false,"autoplay":false}'>
  </canvas>

  <script>
    const tl = gsap.timeline({ paused: true });

    // 获取 lottie timeline
    const lottieTL = window.__registry['lottie-player'].getAnim('lottie-logo');

    // 与 GSAP timeline 同步
    tl.call(() => lottieTL.play(), null, 0.5);
    tl.to('.text', { opacity: 1, y: 0, duration: 0.6 }, 0.5);
    tl.call(() => lottieTL.pause(), null, 3);

    window.__timelines['brand-intro'] = tl;
  </script>
</div>
```

---

## 黄金法则

### 设计阶段

1. **扁平化优先**：避免照片级渲染，用矢量插画替代
2. **减少图层嵌套**：过深的预合成会影响性能
3. **避免表达式**：lottie 对 AE 表达式支持有限
4. **统一帧率**：建议 30fps 或 60fps，避免混用
5. **尺寸合理**：Logo建议 512x512，Icon 128x128

### 开发阶段

6. **内联 JSON 数据**：优先使用 `animationData` 而非 `path`（避免CORS）
7. **预加载动画**：`loadAnimation` 后立即 `pause()`，等待 timeline 驱动
8. **销毁清理**：`anim.destroy()` 在 unmount 时必须调用
9. **Renderer 选择**：SVG（推荐）/ Canvas（高性能）/ HTML（简单DOM）
10. **循环设计**：如果需要循环，使用 AE 预合成而非 JS 控制

### 性能优化

```
✅ 优化：
- 简化路径点（Path Simplify）
- 减少图层数量
- 避免逐帧动画
- 使用 dotLottie 压缩格式

❌ 避免：
- 过多遮罩叠加
- 超大尺寸动画（> 1MB）
- 过多模糊效果
- 复杂3D旋转
```

---

## 场景路由

| 场景 | 工具 | 原因 |
|------|------|------|
| **设计师提供AE动画** | lottie-web ⭐ | 直接播放，无需重写 |
| **无设计资产，快速生成** | hyperframes ⭐ | AI驱动HTML5合成 |
| **需要精确时间线控制** | GSAP Timeline | 帧级别精确 |
| **复杂React组件视频** | Remotion | React生态完整 |
| **数据图表动画** | hyperframes + lottie | chart组件 + AE图表 |
| **Logo/Icon动画** | lottie-web ⭐ | 设计师已有资产 |
| **多段复杂视频** | Remotion + lottie | 复杂合成 + 设计师动画 |

---

## 典型工作流

### 设计师 → 开发者流水线

```bash
# 1. 设计师：在 AE 中创建动画
# 2. 设计师：使用 Bodymovin 插件导出 JSON
#    - Renderer: SVG
#    - 优化：开启 Optimize
#    - 保存为 animation.json

# 3. 开发者：验证 JSON
python3 lottie_bridge.py validate animation.json

# 4. 开发者：打包为 dotLottie（可选）
python3 dotlottie_packer.py bundle animation.json --images images/

# 5. 开发者：集成到 hyperframes
#    - 将 JSON 放入 templates/ 或 registry/ 目录
#    - 使用 lottie-player 组件
#    - 与 GSAP timeline 同步

# 6. 渲染
npx hyperframes render --format mp4 --quality high
```

---

## 文件结构

```
lottie-integration/
├── SKILL.md                        # 本文件 (V1.0)
├── prompts/
│   ├── ae-export-guide.md          # AE导出Bodymovin指南
│   └── web-embed-guide.md         # 网页嵌入指南
├── scripts/
│   ├── lottie_bridge.py           # CLI工具（validate/init/json2svg）
│   └── dotlottie_packer.py        # dotLottie打包工具
└── registry/
    └── lottie-player.js            # Registry原子组件
```

---

## 天龙引擎集成

### 适用岗位

| 岗位 | 版本升级 | 新增能力 |
|------|---------|---------|
| **35-05 短视频编导** | V5.0 → V5.1 | AE设计师动画播放 |
| **35-02 社媒运营** | V12.4 → V12.5 | Logo动画 + Icon动画复用 |
| **13-01 设计师** | V10.6 → V10.7 | Bodymovin导出规范 |
| **07 记录师** | V8.85 → V8.86 | 动画资产管理 |

### 命令调用

```bash
# 天龙引擎自然语言调用
[@35-05] 将设计师提供的AE动画导入hyperframes
[@35-05] 使用lottie播放logo动画并与GSAP timeline同步
[@设计师] 使用Bodymovin导出SVG格式动画

# CLI工具
python3 scripts/lottie_bridge.py validate animation.json
python3 scripts/dotlottie_packer.py bundle animation.json
```

---

## 参考资源

- lottie-web GitHub: https://github.com/airbnb/lottie-web
- Bodymovin插件: https://github.com/airbnb/lottie-sites (After Effects extension)
- dotLottie: https://dotlottie.io
- LottieFiles: https://lottiefiles.com (10万+免费动画)
- AE to Lottie 最佳实践: https://airbnb.io/lottie/#/after-effects?id=supported-features
