---
license: UNKNOWN
name: html-slides
version: 1.0.0
description: |
  零依赖HTML幻灯片生成器。支持从零创建或转换PPT文件，12种精心设计的主题风格，
  一键部署到Vercel或导出PDF。与ppt-generator形成互补的双引擎架构。
author: 天龙引擎团队 (整合 zarazhangrui/frontend-slides)
source: https://github.com/zarazhangrui/frontend-slides
stars: 11200
created: 2026-03-25
updated: 2026-03-25
category: content
dependencies: none
triggers:
  - "html-slides"
  - "web slides"
  - "zero dependency slides"
  - "convert pptx"
  - "PPT转Web"
  - "零依赖PPT"
  - "HTML演示文稿"
---

# HTML Slides - 零依赖演示文稿生成器

## 核心价值

> **与ppt-generator形成互补的双引擎架构**

| 特性 | html-slides | ppt-generator |
|------|-------------|---------------|
| **依赖** | ✅ 零依赖 | ⚠️ 需要API密钥 |
| **输出** | HTML（可编辑） | 图片+视频 |
| **长期可用** | ✅ 单文件HTML | ⚠️ API依赖 |
| **视频功能** | ❌ 无 | ✅ 转场视频 |
| **PPT转换** | ✅ 支持 | ❌ 无 |

## 智能路由规则

### 自动路由算法

使用 `slide_router.py` 智能分析用户需求，自动选择最佳引擎：

```python
# 运行智能路由
python ~/.claude/skills/html-slides/scripts/slide_router.py "用户需求描述"

# 输出示例
# 🎯 推荐引擎: html-slides
# 📝 推荐命令: /html-slides
# 💡 推荐原因: 场景【长期存档】更适合零依赖路线
```

### 场景权重矩阵

| 场景 | html-slides | ppt-generator | 推荐原因 |
|------|-------------|---------------|---------|
| 长期存档 | ⭐⭐⭐ | ⭐ | 零依赖，永久可用 |
| 在线分享 | ⭐⭐⭐ | ⭐ | Vercel一键部署 |
| 转换PPT | ⭐⭐⭐ | - | PPT解析支持 |
| 无API依赖 | ⭐⭐⭐ | - | 零依赖设计 |
| 可编辑修改 | ⭐⭐ | ⭐ | HTML格式友好 |
| 视频转场 | - | ⭐⭐⭐ | AI视频生成 |
| 高质量配图 | ⭐ | ⭐⭐⭐ | AI图片生成 |
| 动画效果 | ⭐ | ⭐⭐⭐ | 可灵AI转场 |
| 产品发布 | ⭐ | ⭐⭐ | 视觉冲击力 |
| 技术演讲 | ⭐⭐ | ⭐ | 代码友好 |

### 路由触发词

**html-slides 触发词：**
- 零依赖、长期存档、在线分享、部署、vercel
- 转换ppt、pptx转、可编辑、html演示
- 无api、没有api密钥、不需要api

**ppt-generator 触发词：**
- 视频转场、高质量配图、ai图片、动画效果
- 转场视频、kling、可灵、图片生成
- 自动生成、ai生成ppt

## 12种主题风格

### 暗色主题
| 主题 | 描述 | 适用场景 |
|------|------|---------|
| **Bold Signal** | 大胆信号风格 | 科技产品发布 |
| **Electric Studio** | 电子工作室 | 创意工作室 |
| **Creative Voltage** | 创意电压 | 设计提案 |
| **Dark Botanical** | 暗色植物 | 自然/环保主题 |

### 亮色主题
| 主题 | 描述 | 适用场景 |
|------|------|---------|
| **Notebook Tabs** | 笔记标签 | 教育/笔记 |
| **Pastel Geometry** | 柔和几何 | 轻松/生活化 |
| **Split Pastel** | 分割柔和 | 对比分析 |
| **Vintage Editorial** | 复古编辑 | 历史/文化 |

### 特殊主题
| 主题 | 描述 | 适用场景 |
|------|------|---------|
| **Neon Cyber** | 霓虹赛博 | 赛博朋克/游戏 |
| **Terminal Green** | 终端绿色 | 开发者/技术 |
| **Swiss Modern** | 瑞士现代 | 极简/商务 |
| **Paper & Ink** | 纸墨风格 | 文艺/出版物 |

## 执行流程

### Phase 1: 需求收集

#### 1.1 确认内容来源

**选项A：从零创建**
```
用户: 创建一个AI创业路演PPT
→ 询问主题、页数、目标受众
```

**选项B：转换PPT**
```
用户: 转换 presentation.pptx
→ 使用Python脚本解析PPT
```

**选项C：已有内容**
```
用户: 基于以下文档生成...
→ 直接使用文档内容
```

#### 1.2 选择主题风格

使用AskUserQuestion展示风格选项：

```markdown
问题: 选择演示风格
选项:
- Bold Signal (暗色/科技感)
- Swiss Modern (亮色/极简商务)
- Terminal Green (特殊/开发者)
- Notebook Tabs (亮色/教育)
- Pastel Geometry (亮色/轻松)
```

#### 1.3 确认输出选项

```markdown
问题: 输出方式
选项:
- 仅HTML文件（快速）
- HTML + 部署到Vercel（在线分享）
- HTML + 导出PDF（正式文档）
```

### Phase 2: 内容规划

#### 2.1 自动规划幻灯片结构

**5页结构（5分钟演讲）：**
1. 封面 - 标题 + 核心主题
2. 问题 - 痛点分析
3. 方案 - 解决方案
4. 价值 - 核心优势
5. 行动 - 下一步计划

**10页结构（15分钟演讲）：**
1. 封面
2-3. 引言/背景
4-6. 核心内容（3个关键点）
7-8. 案例/数据
9. 总结
10. 行动呼吁

**15页结构（30分钟演讲）：**
1. 封面
2. 目录
3-4. 引言和背景
5-7. 第一部分
8-10. 第二部分
11-13. 第三部分/案例
14. 数据可视化
15. 总结与致谢

#### 2.2 生成 slides-plan.json

```json
{
  "title": "AI创业路演",
  "theme": "bold-signal",
  "total_slides": 5,
  "output_options": {
    "deploy_vercel": true,
    "export_pdf": false
  },
  "slides": [
    {
      "number": 1,
      "type": "cover",
      "title": "AI驱动的智能客服",
      "subtitle": "重新定义客户体验"
    },
    {
      "number": 2,
      "type": "problem",
      "title": "当前痛点",
      "content": "传统客服成本高、响应慢、体验差"
    }
  ]
}
```

### Phase 3: HTML生成

#### 3.1 使用模板生成

```bash
# 主要生成逻辑（Claude Code执行）
python ~/.claude/skills/html-slides/scripts/generate_html.py \
  --plan slides-plan.json \
  --theme bold-signal \
  --output ./my-deck/
```

#### 3.2 生成的文件结构

```
my-deck/
├── index.html          # 主HTML文件（零依赖）
├── images/             # 图片资源（如果有）
│   ├── slide-01.png
│   └── ...
└── README.md           # 使用说明
```

### Phase 4: 部署/导出（可选）

#### 4.1 部署到Vercel

```bash
# 自动部署脚本
bash ~/.claude/skills/html-slides/scripts/deploy.sh ./my-deck/
```

输出：
```
✅ 部署成功！
🔗 分享链接: https://my-deck.vercel.app
```

#### 4.2 导出PDF

```bash
# 使用Playwright导出
bash ~/.claude/skills/html-slides/scripts/export-pdf.sh ./my-deck/index.html
```

输出：
```
✅ PDF导出成功！
📄 文件路径: ./my-deck/presentation.pdf
```

## 命令参考

### 基础命令

```bash
# 从零创建
/html-slides

# 指定主题
/html-slides --theme terminal-green

# 指定页数
/html-slides --slides 10

# 转换PPT
/html-slides --convert presentation.pptx
```

### 自然语言触发

```
创建一个零依赖的HTML演示文稿
转换这个PPT为Web版本
用Swiss Modern主题做一个产品发布会PPT
```

## 与天龙岗位协同

| 岗位 | 协同方式 | 收益 |
|------|---------|------|
| **07记录师** | 主要使用者 | 零依赖文档，长期可用 |
| **13-01设计师** | 风格参考 | 12种反模板化设计 |
| **35-02社媒运营** | 内容分享 | 一键部署，稳定URL |
| **50-01产品策划** | PRD演示 | 可编辑HTML，灵活修改 |
| **00分析师** | 分析报告 | PDF导出，正式文档 |

## 技术架构

### 零依赖设计

```html
<!-- 单文件HTML，所有CSS/JS内联 -->
<!DOCTYPE html>
<html>
<head>
  <style>
    /* 所有样式内联 */
  </style>
</head>
<body>
  <!-- 幻灯片内容 -->
  <script>
    /* 所有交互逻辑内联 */
  </script>
</body>
</html>
```

### 动画系统

- CSS Keyframes 动画
- Intersection Observer 触发
- 响应式设计（移动端友好）
- 键盘导航支持

## 对比决策矩阵

| 需求 | 推荐 | 原因 |
|------|------|------|
| 长期存档文档 | html-slides | 零依赖，永久可用 |
| 快速分享在线链接 | html-slides | Vercel一键部署 |
| 需要视频转场效果 | ppt-generator | AI视频生成 |
| 需要高质量配图 | ppt-generator | AI图片生成 |
| 转换现有PPT | html-slides | PPT解析支持 |
| 可编辑修改 | html-slides | HTML格式友好 |
| 正式商务报告 | 两者皆可 | html-slides+PDF / ppt-generator |

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| PPT解析失败 | 文件格式不支持 | 提示用户转换为PPTX格式 |
| Vercel部署失败 | 未安装CLI | 提供手动部署指南 |
| PDF导出失败 | Playwright未安装 | 安装指南：`npm install -g playwright` |

## 安装要求

### 必需
- 无（零依赖设计）

### 可选（部署/导出功能）
```bash
# Vercel部署
npm install -g vercel

# PDF导出
npm install -g playwright
npx playwright install chromium

# PPT转换
pip install python-pptx
```

## 版本历史

- **v1.0.0** (2026-03-25) - 初始集成到天龙引擎V8.52