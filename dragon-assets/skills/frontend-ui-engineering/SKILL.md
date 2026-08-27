---
license: UNKNOWN
triggers: ["frontend ui engineering", "frontend-ui-engineering"]
---
# frontend-ui-engineering

## L0: 一句话描述 (≤15字)
设计驱动前端工程，审美量化，组件体系。

## L1: 使用场景 (50-100字)
适用于需要从设计规范转化为可执行代码的前端开发场景。核心价值在于"审美量化"——将主观的设计感觉转化为可测量的参数（字体量级/色彩权重/动效曲线），确保设计与实现的一致性，避免设计走形。

## L2: 详细文档

# Frontend UI Engineering (前端UI工程)

> **核心理念**: "Design is not just what it looks like, design is how it works."
> 每个前端项目必须先有设计规范，否则代码实现就是无锚之舟。

## 审美量化体系

### 字体量级 (Typography Scale)
```
--font-size-xs: 0.75rem    /* 12px - 辅助文本 */
--font-size-sm: 0.875rem   /* 14px - 正文小字 */
--font-size-base: 1rem     /* 16px - 正文标准 */
--font-size-lg: 1.125rem    /* 18px - 强调文本 */
--font-size-xl: 1.25rem     /* 20px - 小标题 */
--font-size-2xl: 1.5rem    /* 24px - 中标题 */
--font-size-3xl: 1.875rem  /* 30px - 大标题 */
--font-size-4xl: 2.25rem    /* 36px - 页面标题 */
```

### 色彩权重 (Color Weight)
```
/* 主色系：按权重分层 */
--color-primary-50:  0.02   /* 极浅，hover背景 */
--color-primary-100: 0.05   /* 浅，选中态 */
--color-primary-200: 0.10   /* 次浅，disabled */
--color-primary-300: 0.15   /* 浅边框 */
--color-primary-400: 0.20   /* 浅色文字 */
--color-primary-500: 0.50   /* 标准（中性灰平衡）*/
--color-primary-600: 0.65   /* 深色文字 */
--color-primary-700: 0.75   /* 深色边框 */
--color-primary-800: 0.85   /* 深色背景 */
--color-primary-900: 0.92   /* 极深背景 */

/* 语义色 */
--color-success: hsl(142, 76%, 36%)
--color-warning: hsl(38, 92%, 50%)
--color-error:   hsl(0, 84%, 60%)
--color-info:    hsl(199, 89%, 48%)
```

### 动效曲线 (Motion Curves)
```
/* 默认曲线库 */
--ease-default:    cubic-bezier(0.4, 0, 0.2, 1)   /* 标准 */
--ease-in:         cubic-bezier(0.4, 0, 1, 1)       /* 进入 */
--ease-out:        cubic-bezier(0, 0, 0.2, 1)       /* 退出 */
--ease-bounce:     cubic-bezier(0.34, 1.56, 0.64, 1) /* 弹性 */

/* 持续时间标准化 */
--duration-instant:  75ms    /* 微交互 */
--duration-fast:    150ms   /* 小元素 */
--duration-normal:  250ms   /* 标准过渡 */
--duration-slow:     400ms   /* 页面级 */
--duration-slower:  600ms   /* 复杂动画 */
```

## 设计工程化四步法

### Step 1: 设计规范提取 (Design Token Extraction)
```bash
# 从设计文件提取颜色
grep -rE "#[0-9a-fA-F]{3,8}|hsl\(|rgb\(" --include="*.json" | \
  python3 scripts/extract_colors.py

# 从Figma/Sketch导出Design Token
python3 ~/.claude/skills/ui-design-system/scripts/design_token_generator.py \
  --input design.fig \
  --output tokens/

# 生成CSS变量
python3 scripts/generate_css_vars.py tokens/
```

### Step 2: 组件体系构建 (Component Architecture)
```
src/
├── components/
│   ├── primitives/        # 基础组件（Button/Input/Icon）
│   ├── composites/        # 复合组件（Card/Modal/Dropdown）
│   └── patterns/          # 业务模式（Form/Login/Table）
├── tokens/                # Design Token
│   ├── colors.css
│   ├── typography.css
│   ├── motion.css
│   └── spacing.css
└── hooks/
    ├── useDesignToken.ts
    ├── useResponsive.ts
    └── useMotion.ts
```

### Step 3: 一致性验证 (Consistency Validation)
```bash
# 检查组件尺寸一致性
python3 scripts/check_spacing.py src/components/

# 验证色彩对比度（WCAG AA）
python3 scripts/validate_contrast.py

# 动效一致性检查
grep -r "transition\|animation" src/ | python3 scripts/check_motion.py
```

### Step 4: 文档自动生成 (Documentation Auto-Generation)
```bash
# 从组件生成Storybook
python3 scripts/generate_stories.py src/components/ --output stories/

# 生成Design Token文档
python3 scripts/generate_token_docs.py tokens/
```

## 与天龙引擎协同

| 天龙组件 | 协同方式 |
|---------|---------|
| 13-01设计师 | 设计规范作为前端工程的输入 |
| 02架构师 | 组件体系架构设计 |
| 03构建师 | 按设计规范实现组件 |
| 06审查师 | 设计一致性审查 |
| frontend-design | 设计思维作为工程化的指导原则 |
| ui-design-system | Design Token生成作为组件规范化的输入 |

## 版本

- V1.0: 2026-04-30 初始集成，基于 addyosmani/agent-skills 前端UI工程方法论
