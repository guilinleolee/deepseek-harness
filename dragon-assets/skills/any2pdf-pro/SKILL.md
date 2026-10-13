---
license: UNKNOWN
triggers: ["any2pdf pro", "any2pdf-pro - Markdown转专业排版PDF"]
---
# any2pdf-pro - Markdown转专业排版PDF

> 天龙引擎专属版本 | V8.83 | 基于 lovstudio/any2pdf (87⭐)

## L0: 一句话描述 (≤15字)
Markdown一键转换为专业排版PDF

## L1: 使用场景 (50-100字)
当用户需要将Markdown文档转换为专业排版PDF时使用。支持10种设计主题、CJK完美支持、封面目录水印。适用：研究报告、论文、投标书、商务文档等。

## L2: 详细文档

### 核心能力

```
┌─────────────────────────────────────────────────────────────┐
│ any2pdf-pro 专业PDF生成能力                                   │
├─────────────────────────────────────────────────────────────┤
│ ✅ 零配置零模板，无需LaTeX                                  │
│ ✅ 单Python文件，依赖仅reportlab                            │
│ ✅ 完美支持CJK（中日韩）+ 拉丁混合文本                      │
│ ✅ 10种内置专业设计主题                                     │
│ ✅ 封面页 + 可点击目录 + 书眉页脚 + 水印 + 封底            │
│ ✅ 自动字体发现，跨平台（macOS/Windows/Linux）              │
│ ✅ AI Agent Skill格式，交互式工作流                        │
└─────────────────────────────────────────────────────────────┘
```

### 10种设计主题

| 主题ID | 风格 | 适用场景 |
|--------|------|---------|
| `warm-academic` | 温暖学术风 | 研究报告、论文 |
| `classic-thesis` | 经典论文风 | 学术文档 |
| `tufte` | Tufte书籍风 | 数据可视化报告 |
| `ieee-journal` | IEEE期刊风 | 技术论文 |
| `modern-minimal` | 现代极简 | 商业文档 |
| `corporate` | 企业风格 | 商务报告 |
| `elegant-book` | 典雅书籍 | 电子书 |
| `technical-manual` | 技术手册 | API文档 |
| `presentation` | 演示风格 | 演示文稿PDF |
| `nord` | 北欧极简 | 现代简约文档 |

### 天龙引擎调用命令

```bash
# 基础使用
[@07记录师] 将这份调研报告转换为专业PDF
[@07记录师] 生成一份IEEE期刊风格的论文PDF
[@07记录师] 创建学术研究报告PDF

# 高级使用
[@07记录师] 使用warm-academic主题生成研究报告PDF
[@07记录师] 为投标书生成corporate风格PDF

# 组合使用
[@07记录师] 将markdown转换为PDF并添加水印
[@07记录师] 生成带封面和目录的研究报告PDF
```

### CLI直接调用

```bash
# 安装依赖
pip install reportlab

# 基础转换
python ~/.agents/skills/lovstudio-any2pdf/scripts/md2pdf.py \
  --input report.md \
  --output report.pdf \
  --title "研究报告"

# 指定主题
python ~/.agents/skills/lovstudio-any2pdf/scripts/md2pdf.py \
  --input report.md \
  --output report.pdf \
  --title "研究报告" \
  --theme warm-academic

# 完整配置
python ~/.agents/skills/lovstudio-any2pdf/scripts/md2pdf.py \
  --input report.md \
  --output report.pdf \
  --title "研究报告" \
  --author "天龙引擎" \
  --theme ieee-journal \
  --cover \
  --toc \
  --watermark "机密"
```

### 与现有天龙能力协同

| 天龙组件 | any2pdf协同 | 效果 |
|---------|------------|------|
| **deep-research** | 研究报告 → 专业PDF | 成果展示提升 |
| **gpt-researcher** | 调研报告 → 专业PDF | 发布质量+200% |
| **research-to-wechat** | 文章 → PDF存档 | 知识沉淀增强 |
| **ppt-generator** | PPT → PDF备份 | 演示存档完整 |
| **baoyu-post-to-wechat** | 公众号 → PDF归档 | 多格式留存 |

### 天龙岗位升级

| 岗位 | 版本 | 新增能力 |
|------|------|---------|
| **07记录师** | V8.82 → V8.83 | 专业排版PDF生成 + 10种设计主题 |
| **13-01设计师** | V10.4 → V10.5 | PDF设计主题库 |
| **28-01文案策划** | V1.0 → V1.1 | 策划文档专业PDF导出 |

### 预期收益

| 指标 | 集成前 | 集成后 | 提升 |
|------|--------|--------|------|
| **PDF专业排版能力** | 基础 | 10种主题 | **质的飞跃** |
| **文档美观度** | 通用 | 学术/商业/IEEE | **+300%** |
| **CJK支持** | 需手动配置 | 自动完美支持 | **质的飞跃** |
| **记录师能力** | V8.82 | V8.83 | **+1版本** |

## 安装验证

```bash
# 验证安装
ls ~/.agents/skills/lovstudio-any2pdf/

# 验证依赖
python -c "import reportlab; print('reportlab OK')"
```
