---
name: gpt-researcher
description: GPT-Researcher 命令
invokable: true
---
# GPT-Researcher 命令

> 基于 assafelovic/gpt-researcher (42k+ Stars) 的深度研究Agent

## 安装状态

✅ **已安装**: `/tmp/gpt-researcher` 虚拟环境

## 命令列表

### 基本研究

```bash
# 基本研究
/tmp/gpt-researcher/Scripts/python ~/.claude/skills/gpt-researcher/scripts/gpt_researcher_wrapper.py research "研究主题"
```

### 深度研究

```bash
# 深度探索（推荐）
/tmp/gpt-researcher/Scripts/python ~/.claude/skills/gpt-researcher/scripts/gpt_researcher_wrapper.py deep "大型语言模型技术演进"

# 自定义深度和广度
/tmp/gpt-researcher/Scripts/python ~/.claude/skills/gpt-researcher/scripts/gpt_researcher_wrapper.py deep "AI Agent发展趋势" --depth 3 --breadth 5
```

### 本地文档研究

```bash
# 分析本地文档
/tmp/gpt-researcher/Scripts/python ~/.claude/skills/gpt-researcher/scripts/gpt_researcher_wrapper.py local "分析文档" --docs ./report.pdf
```

## 天龙引擎调用

### 01调研师

```bash
[@01调研师] 使用GPT-Researcher深度研究"AI Agent 2025发展趋势"
[@01调研师] 对比分析Claude/GPT/Gemini的技术路线差异
```

### 62-02行业研究员

```bash
[@行业研究员] 使用Deep Research分析新能源汽车行业竞争格局
[@行业研究员] 研究AI芯片行业技术演进路线
```

## 环境变量

```bash
export OPENAI_API_KEY="sk-..."
export TAVILY_API_KEY="tvly-..."  # 可选，增强搜索
```

## 重新安装（如需要）

```bash
cd /tmp
rm -rf gpt-researcher
uv venv gpt-researcher
source gpt-researcher/Scripts/activate
uv pip install gpt-researcher
```
