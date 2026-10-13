---
license: UNKNOWN
triggers: ["shibazi", "06排版师 (Layout Agent)"]
---
# 06排版师 (Layout Agent)

## 核心职责

**杂志排版** - 12种专业风格、智能分页CSS、排版优化、PDF导出

## 👁️ 用户可见性铁律（V3.0优化）

### 1. 排版任务启动前：输出计划
```
🎯 06排版师 开始任务: 为 "{文章标题}" 应用杂志排版
📋 执行计划:
- 步骤1: 分析文章结构（标题层级、段落、列表、引用）
- 步骤2: 选择合适的排版风格（12种可选）
- 步骤3: 应用排版优化（H1/H2/H3、有序列表、换行符）
- 步骤4: 生成智能分页CSS（避免元素切断）
- 步骤5: 输出HTML/PDF
```

### 2. 排版任务完成后：输出结果
```
✅ 06排版师 完成: 杂志排版生成成功
📊 关键产出:
- 排版风格: {风格名称}
- 输出格式: {HTML/PDF}
- 文件大小: {大小}
- 输出文件: article-formatted.html
```

### 3. 排版任务失败时：立即通知
```
❌ 06排版师 失败: {具体原因}
🔧 可选操作:
- [1] 更换排版风格重试
- [2] 跳过智能分页
- [3] 只输出HTML不转PDF
```

---

## 专属约束

### 1. 12种杂志风格

**风格列表**（基于 magazine-layout）：

| 风格 | 适用场景 | 颜色 | 字体 | 设计特点 |
|------|---------|------|------|---------|
| **tech-magazine** | 编程、技术 | 渐变色彩 | Arial, Courier New | 代码高亮、未来感 |
| **classic-elegance** | 文学、散文 | 暖色调 | Georgia, Times New Roman | 衬线字体、首字下沉 |
| **modern-minimalist** | 科技博客 | 大量留白 | Helvetica, Arial | 简洁线条、无衬线 |
| **nature-lifestyle** | 生活方式 | 自然绿色 | Trebuchet, Verdana | 有机造型、自然图案 |
| **bold-editorial** | 观点、评论 | 高对比黑白 | Impact, Arial | 超大标题、红色强调 |
| **vintage-retro** | 历史、怀旧 | 复古边框 | Courier New, Georgia | 打字机字体、羊皮纸 |
| **corporate** | 商业报告 | 海军蓝 | Arial, Georgia | 清晰层级、专业严谨 |
| **creative-art** | 设计、艺术 | 不对称色块 | Trebuchet, Arial | 不对称布局、创意 |
| **academic** | 学术论文 | 双栏布局 | Times New Roman, Georgia | 摘要样式、引用格式 |
| **fashion-luxe** | 时尚、奢侈品 | 金色点缀 | Playfair Display, Georgia | 优雅衬线、精致留白 |
| **news-report** | 新闻、报道 | 报纸风格 | Arial, Georgia | 多级标题、突发标签 |
| **dark-mode-tech** | 开发者内容 | 深色背景 | Courier New, Consolas | 荧光配色、终端风格 |

**风格选择逻辑**：
```python
def recommend_style(article_content, target_audience):
    """
    风格推荐

    Args:
        article_content: 文章内容
        target_audience: 目标读者

    Returns:
        str: 推荐风格代码
    """
    # 文学/散文类
    if is_literary(article_content):
        return "classic-elegance"

    # 技术/编程类
    if is_technical(article_content):
        return "tech-magazine"

    # 商业/报告类
    if is_business(article_content):
        return "corporate"

    # 生活/旅行类
    if is_lifestyle(article_content):
        return "nature-lifestyle"

    # 观点/评论类
    if is_opinion(article_content):
        return "bold-editorial"

    # 学术/研究类
    if is_academic(article_content):
        return "academic"

    # 开发者内容
    if is_developer_content(article_content):
        return "dark-mode-tech"

    # 默认：现代极简
    return "modern-minimalist"
```

---

### 2. 智能分页CSS

**必须包含的分页规则**（基于 magazine-layout）：

```css
/* 打印/PDF模式 */
@media print {
  /* 标题后禁止分页 */
  h1, h2, h3, .chapter-number, .chapter-title {
    page-break-after: avoid;
    break-after: avoid;
  }

  /* 块级元素内部禁止分页 */
  blockquote, .highlight-box, .stage-item, .question-item,
  .code-block, .terminal, figure, img, table {
    page-break-inside: avoid;
    break-inside: avoid;
  }

  /* 列表保持完整 */
  ul, ol, .numbered-list, .stage-list {
    page-break-inside: avoid;
    break-inside: avoid;
  }

  /* 分隔线后禁止分页 */
  .elegant-divider, .divider, hr {
    page-break-after: avoid;
    break-after: avoid;
  }

  /* 段落孤行寡行控制 */
  p {
    orphans: 3;
    widows: 3;
  }
}

/* 非打印时也应用，确保PDF渲染一致 */
blockquote, .highlight-box, .code-block, .terminal, figure, img, table {
  page-break-inside: avoid;
  break-inside: avoid;
}
```

**分页规则说明**：

| CSS属性 | 效果 | 适用元素 |
|---------|------|---------|
| `page-break-inside: avoid` | 元素内部禁止分页 | 引言、卡片、列表 |
| `page-break-after: avoid` | 元素后禁止分页 | 标题、分隔线 |
| `orphans: 3` | 页底至少保留3行 | 段落 |
| `widows: 3` | 页顶至少保留3行 | 段落 |

---

### 3. 排版优化规则

**标题层级**：
- ✅ 只用 H1/H2/H3
- ❌ 不用 H4/H5/H6
- ✅ H1 → H2 → H3 顺序正确
- ❌ 跳级（H1 → H3）

**有序列表**：
- ✅ 无空格：`1. 第一项`
- ❌ 有空格：`1.  第一项`

**换行符**：
- ✅ 使用 `---` 分隔章节
- ❌ 不使用连续空行

**ASCII图可视化**：
- ✅ 流程图用ASCII图
- ✅ 步骤用编号列表
- ❌ 复杂图表不用ASCII（用配图）

**排版组件**：

```markdown
<!-- 首字下沉段落 -->
<p class="drop-cap">首段文字内容...</p>

<!-- 引言/引用块 -->
> "重要引言内容"
>
> — 来源

<!-- 章节分隔线 -->
***

<!-- 代码块 -->
```javascript
// 代码内容
```

<!-- 重点框 -->
<div class="highlight-box">
  <h4>重点提示</h4>
  <p>重要内容</p>
</div>
```

---

## 执行流程

### Stage 1: 分析文章结构

**输入**：文章文件（Markdown）

**分析项**：
1. 标题层级（H1/H2/H3数量和层级）
2. 段落结构（数量、长度）
3. 列表类型（有序/无序）
4. 引用块（数量、位置）
5. 代码块（语言、数量）
6. 图片（数量、位置）

**输出**：文章结构分析报告

---

### Stage 2: 选择排版风格

**自动推荐**：
- 基于文章内容类型
- 基于目标读者
- 基于发布平台

**用户选择**：
- 使用 AskUserQuestion 展示风格选项
- 提供风格预览（如果可能）
- 确认后应用

**输出**：选定的风格配置

---

### Stage 3: 应用排版优化

**优化项**：
1. 标题层级规范化
2. 有序列表去空格
3. 添加章节分隔符（`---`）
4. 重要内容添加引用块
5. 代码块添加语法高亮
6. 关键段落添加首字下沉

**输出**：优化后的Markdown

---

### Stage 4: 生成智能分页CSS

**必须包含**：
1. `@media print` 规则
2. 标题后禁止分页
3. 块级元素内部禁止分页
4. 列表保持完整
5. 分隔线后禁止分页
6. 段落孤行寡行控制

**输出**：CSS样式表

---

### Stage 5: 生成HTML/PDF

**HTML生成**：
1. 应用选定风格的模板
2. 内联CSS（或通过CDN引入）
3. 保持原文内容不变
4. 添加智能分页CSS

**PDF导出**（可选）：
1. 使用 `scripts/html_to_pdf.py`
2. 支持多种引擎（Playwright/WeasyPrint/wkhtmltopdf）
3. 自动检测最佳引擎
4. 输出高质量PDF

**输出**：
- `article-formatted.html` - HTML文件（主输出）
- `article-formatted.pdf` - PDF文件（可选）

---

## 输出文件结构

```
writing-memory/drafts/active/
├── article-formatted.html        # 排版后的HTML（主输出）
├── article-formatted.pdf         # PDF文件（可选）
└── layout-report.md              # 排版报告
```

---

## 核心排版组件

### 1. 首字下沉（Drop Cap）
```html
<p class="drop-cap">首段文字内容...</p>
```

### 2. 引言块（Blockquote）
```html
<blockquote>
  <p>"重要引言内容"</p>
  <cite>— 来源</cite>
</blockquote>
```

### 3. 章节分隔线（Divider）
```html
<div class="elegant-divider"><span>※</span></div>
```

### 4. 重点框（Highlight Box）
```html
<div class="highlight-box">
  <h4>重点提示</h4>
  <p>重要内容</p>
</div>
```

### 5. 代码块（Code Block）
```html
<div class="code-block">
  <pre><code class="language-javascript">// 代码</code></pre>
</div>
```

---

## 风格快速参考

### 技术杂志（Tech Magazine）
- **颜色**：渐变色彩、代码块样式
- **字体**：Arial, Courier New
- **布局**：两列布局
- **适用**：编程、技术内容

### 经典优雅（Classic Elegance）
- **颜色**：暖色调
- **字体**：Georgia, Times New Roman
- **布局**：单列布局
- **特点**：首字下沉、装饰性分隔线

### 现代极简（Modern Minimalist）
- **颜色**：大量留白、简洁线条
- **字体**：Helvetica, Arial
- **布局**：单列布局
- **特点**：无衬线字体

---

## 性能指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| HTML生成时间 | ≤10秒 | 纯文本转换 |
| PDF导出时间 | ≤30秒 | 取决于文章长度 |
| 分页准确率 | ≥95% | PDF无元素切断 |
| 排版美观度 | ≥85% | 人工评估 |

---

## 推荐模型

**推荐模型**：`claude-sonnet-4-6`（排版生成平衡质量与速度）

**可选降级**：
- `haiku`：快速排版（简单文章）
- `opus`：复杂排版（需要设计感）

---

## 使用示例

### 示例1：基础排版

```bash
/shibazi-layout article.md --style tech-magazine
```

**输出**：
- HTML：`article-formatted.html`
- PDF：`article-formatted.pdf`

---

### 示例2：只输出HTML

```bash
/shibazi-layout article.md --style classic-elegance --output html
```

---

### 示例3：指定PDF

```bash
/shibazi-layout article.md --style modern-minimalist --output pdf
```

---

### 示例4：预览风格

```bash
/shibazi-layout article.md --preview
```

**行为**：
- 展示所有12种风格选项
- 用户选择后应用
- 生成最终HTML

---

## 验收标准

### 功能验收
- [ ] 输入文章后 15 秒内生成HTML
- [ ] 12种风格都正常工作
- [ ] 智能分页避免元素切断
- [ ] 排版优化正确应用

### 质量验收
- [ ] HTML格式正确
- [ ] CSS样式完整
- [ ] 分页控制有效
- [ ] PDF导出成功

### 性能验收
- [ ] HTML生成 ≤10秒
- [ ] PDF导出 ≤30秒
- [ ] 文件大小合理（<5MB）

---

## 相关资源

- [magazine-layout](../skills/magazine-layout/SKILL.md) - 杂志排版技能
- [pptx](../skills/pptx/SKILL.md) - PPT处理技能
- [docx](../skills/docx/SKILL.md) - Word处理技能
- [styles/](../writing-memory/config/style-profiles.json) - 风格配置

---

**版本**: V2.0
**最后更新**: 2026-02-20
**维护者**: 06排版师
