---
license: UNKNOWN
triggers: ["taste 3dial", "taste-3dial"]
---
# taste-3dial

> **来源**: [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) (MIT License)
> **版本**: V1.0 | **集成**: 天龙引擎 V9.02

## L0: 一句话描述
3Dial参数控制系统 - 量化控制AI生成设计的三个核心维度

## L1: 使用场景

### 适用场景
- 需要精确控制设计输出的"风格强度"
- 希望在"极简"和"激进"之间找到平衡点
- 前端开发中需要快速切换设计风格

### 触发条件
```
用户请求高级UI设计，且需要明确风格参数时启用
```

## L2: 详细文档

---

# 3Dial Design Control System

## 核心参数

### 1. DESIGN_VARIANCE (布局实验性 1-10)

| 级别 | 描述 | CSS实现 |
|------|------|--------|
| **1-3** | 预测性/对称 | `justify-center`, 12列对称网格, 等间距 |
| **4-7** | 偏移/打破对称 | `margin-top: -2rem`重叠, 混合宽高比(4:3+16:9), 左对齐标题+居中数据 |
| **8-10** | 非对称/艺术 | Masonry布局, CSS Grid分数单位(如`2fr 1fr 1fr`), 大面积留白(`padding-left: 20vw`) |

**Mobile Override**: 当级别≥4时，`< md`断点必须强制回退到单列布局(`w-full`, `px-4`, `py-8`)，防止水平滚动和布局破坏。

### 2. MOTION_INTENSITY (动画强度 1-10)

| 级别 | 描述 | CSS实现 |
|------|------|--------|
| **1-3** | 静态/无动画 | 仅CSS `:hover` 和 `:active` 状态 |
| **4-7** | 流畅CSS动画 | `transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1)`, animation-delay级联, 聚焦`transform`和`opacity`, 谨慎使用`will-change: transform` |
| **8-10** | 高级编排 | 复杂滚动触发动画或视差, 使用Framer Motion hooks, **禁止使用** `window.addEventListener('scroll')` |

### 3. VISUAL_DENSITY (视觉密度 1-10)

| 级别 | 描述 | CSS实现 |
|------|------|--------|
| **1-3** | 艺术馆模式 | 大量留白, 大间距, 一切显得昂贵干净 |
| **4-7** | 日常App模式 | 标准间距 |
| **8-10** | 驾驶舱模式 | 极小内边距, 无卡片边框用1px分隔线, **必须**对所有数字使用`font-mono` |

---

## 默认配置 (Baseline)

```yaml
DESIGN_VARIANCE: 8    # 非对称/现代
MOTION_INTENSITY: 6   # 中等动画
VISUAL_DENSITY: 4     # 日常App密度
```

---

## 使用命令

### 启动3Dial控制系统
```
/taste-3dial <level> [variance] [motion] [density]
```

### 预设组合

| 预设 | VARIANCE | MOTION | DENSITY | 场景 |
|------|----------|--------|---------|------|
| `soft` | 3 | 4 | 3 | 柔和高端界面 |
| `minimal` | 2 | 2 | 4 | 极简编辑产品 |
| `brutalist` | 9 | 3 | 8 | 机械美学 |
| `dashboard` | 4 | 6 | 8 | 数据密集型 |
| `landing` | 7 | 5 | 3 | 落地页 |
| `mobile` | 5 | 7 | 5 | 移动优先 |

### 示例

```bash
# 使用预设
/taste-3dial soft        # 柔和风格
/taste-3dial brutalist   # 机械美学

# 自定义参数
/taste-3dial 8 6 4        # VARIANCE=8, MOTION=6, DENSITY=4

# 单独调整
/taste-3dial variance=9  # 仅调整布局实验性
```

---

## 与impeccable协同

`taste-3dial` 作为 **DESIGN_VARIANCE** 补充impeccable的 `/quieter` 和 `/bolder` 命令：

| 命令 | 功能 | taste-3dial协同 |
|------|------|-----------------|
| `/quieter` | 降低激进设计 | `DENSITY` 降低 |
| `/bolder` | 放大设计冲击力 | `VARIANCE` 提高 |
| `/taste-3dial` | 精确三维度控制 | 完整参数调节 |

---

## 天龙引擎集成

### 适用岗位
- **13-01 设计师** (V10.6+)
- **03 构建师** (V8.74+)
- **06 审查师** (V8.51+)

### 调用方式

```javascript
// 天龙引擎中调用
await ai.design("创建高端仪表板", {
  skills: ["taste-3dial", "frontend-design"],
  params: { variance: 8, motion: 6, density: 4 }
});
```

---

## 技术约束

1. **Mobile Override**: VARIANCE≥4时必须处理移动端回退
2. **Performance**: 动画级别≥8时使用Framer Motion，避免`window.addEventListener('scroll')`
3. **Density≥8**: 数字必须使用等宽字体

---

## 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-04-26 | 天龙引擎V9.02初始集成，基于Leonxlnx/taste-skill |
