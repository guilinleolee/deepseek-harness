# MD-to-PPTX 快速入门

> 5分钟上手 Markdown 转 PPT

## 安装

### 方式一: pip 安装

```bash
pip install python-pptx markdown
```

### 方式二: 使用 ppt-master 集成

md-to-pptx 已经是天龙引擎的一部分，无需额外安装。

## 基本使用

### 1. 准备 Markdown 文件

创建 `presentation.md`:

```markdown
# 我的演示文稿

## 第一部分

- 要点一
- 要点二
- 要点三

## 第二部分

> 这是一个引用

---

## 结论

谢谢观看！
```

### 2. 执行转换

```bash
python md2pptx.py presentation.md
```

### 3. 查看结果

输出文件: `presentation_corporate.pptx`

---

## 进阶使用

### 指定风格

```bash
# 科技风格
python md2pptx.py presentation.md --style tech

# 暗色风格
python md2pptx.py presentation.md --style dark

# 极简风格
python md2pptx.py presentation.md --style minimal
```

### 指定输出路径

```bash
python md2pptx.py presentation.md --output my-slides.pptx
```

### 指定标题

```bash
python md2pptx.py presentation.md --title "2024年度报告"
```

---

## 完整示例

### 完整 Markdown 文件

```markdown
<!-- slide:layout:cover -->
# 产品发布会
## 创新科技，引领未来
### 2024年8月20日

---

## 目录

- 产品概述
- 核心功能
- 技术架构
- 定价方案
- 联系我们

---

## 产品概述

我们专注于为企业提供：

- 🚀 **高性能** - 毫秒级响应
- 🔒 **安全可靠** - 企业级安全保障
- 📊 **数据驱动** - 智能分析与洞察
- 🌐 **全球部署** - 多地域覆盖

---

## 核心功能

### 智能助手

> 基于大语言模型的智能助手，7x24小时为你服务

### 实时协作

- 多端同步
- 多人编辑
- 版本控制

### 数据可视化

| 指标 | 数值 |
|------|------|
| 日活用户 | 100万+ |
| 处理数据 | 10亿+ |
| 响应时间 | <100ms |

---

## 技术架构

```python
# 核心代码示例
class ProductAnalyzer:
    def __init__(self, config):
        self.config = config
        self.model = load_model(config.model_path)

    def analyze(self, data):
        return self.model.predict(data)
```

---

<!-- slide:layout:ending -->

# 谢谢观看

## 欢迎提问

📧 contact@company.com
🌐 www.company.com
```

---

## 命令行参数

| 参数 | 缩写 | 说明 | 默认值 |
|------|------|------|--------|
| `--input` | `-i` | 输入文件 | (必需) |
| `--output` | `-o` | 输出文件 | auto |
| `--style` | `-s` | 风格 | corporate |
| `--format` | `-f` | 比例 | ppt169 |
| `--title` | `-t` | 标题 | auto |
| `--verbose` | `-v` | 详细输出 | False |
| `--stats` | | 统计信息 | False |

---

## 常见问题

### Q: 输出是 SVG 而不是 PPTX?

A: 检查是否安装了 python-pptx:
```bash
pip install python-pptx
```

### Q: 中文显示为方块?

A: 确保系统安装了中文字体，或在 Markdown 中指定字体。

### Q: 如何添加演讲备注?

A: 使用注释指令:
```markdown
<!-- slide:notes:这是备注内容 -->
```

### Q: 幻灯片顺序如何调整?

A: 使用 `---` 分隔符手动调整页面顺序。

---

## 下一步

- 查看 [布局指南](layout-guide.md) 了解布局选项
- 查看 ppt-master 技能了解更多高级功能
- 使用 `/ppt-templates` 查看可用模板
