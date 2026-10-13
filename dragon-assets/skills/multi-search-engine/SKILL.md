---
license: UNKNOWN
name: multi-search-engine
version: 2.0.1
description: 多搜索引擎集成，支持17个搜索引擎（8个国内+9个国际），高级搜索操作符、时间过滤、站内搜索、隐私引擎和WolframAlpha知识查询。无需API密钥。
allowed-tools: - WebFetch
- Bash
triggers: ["multi search engine", "Multi Search Engine v2.0.1"]
---

# Multi Search Engine v2.0.1

集成17个搜索引擎，无需API密钥即可进行网页抓取。

## 搜索引擎列表

### 国内搜索引擎 (8个)
| 引擎 | URL模板 | 特点 |
|------|---------|------|
| **百度** | `https://www.baidu.com/s?wd={keyword}` | 最大中文搜索引擎 |
| **Bing CN** | `https://cn.bing.com/search?q={keyword}&ensearch=0` | 中文版Bing |
| **Bing INT** | `https://cn.bing.com/search?q={keyword}&ensearch=1` | 国际版Bing |
| **360搜索** | `https://www.so.com/s?q={keyword}` | 360搜索 |
| **搜狗** | `https://sogou.com/web?query={keyword}` | 搜狗搜索 |
| **微信** | `https://wx.sogou.com/weixin?type=2&query={keyword}` | 微信公众号文章 |
| **头条** | `https://so.toutiao.com/search?keyword={keyword}` | 今日头条 |
| **集思录** | `https://www.jisilu.cn/explore/?keyword={keyword}` | 投资社区 |

### 国际搜索引擎 (9个)
| 引擎 | URL模板 | 特点 |
|------|---------|------|
| **Google** | `https://www.google.com/search?q={keyword}` | 全球最大搜索引擎 |
| **Google HK** | `https://www.google.com.hk/search?q={keyword}` | Google香港 |
| **DuckDuckGo** | `https://duckduckgo.com/html/?q={keyword}` | 隐私搜索 |
| **Yahoo** | `https://search.yahoo.com/search?p={keyword}` | Yahoo搜索 |
| **Startpage** | `https://www.startpage.com/sp/search?query={keyword}` | Google结果+隐私保护 |
| **Brave** | `https://search.brave.com/search?q={keyword}` | 独立索引 |
| **Ecosia** | `https://www.ecosia.org/search?q={keyword}` | 环保搜索引擎 |
| **Qwant** | `https://www.qwant.com/?q={keyword}` | 欧盟GDPR合规 |
| **WolframAlpha** | `https://www.wolframalpha.com/input?i={keyword}` | 知识计算引擎 |

## 快速示例

```javascript
// 基础搜索
web_fetch({"url": "https://www.google.com/search?q=python+tutorial"})

// 站内搜索
web_fetch({"url": "https://www.google.com/search?q=site:github.com+react"})

// 文件类型
web_fetch({"url": "https://www.google.com/search?q=machine+learning+filetype:pdf"})

// 时间过滤 (过去一周)
web_fetch({"url": "https://www.google.com/search?q=ai+news&tbs=qdr:w"})

// 隐私搜索
web_fetch({"url": "https://duckduckgo.com/html/?q=privacy+tools"})

// DuckDuckGo Bangs快捷搜索
web_fetch({"url": "https://duckduckgo.com/html/?q=!gh+tensorflow"})

// 知识计算
web_fetch({"url": "https://www.wolframalpha.com/input?i=100+USD+to+CNY"})
```

## 高级搜索操作符

| 操作符 | 示例 | 说明 |
|--------|------|------|
| `site:` | `site:github.com python` | 站内搜索 |
| `filetype:` | `filetype:pdf report` | 指定文件类型 |
| `""` | `"machine learning"` | 精确匹配 |
| `-` | `python -snake` | 排除关键词 |
| `OR` | `cat OR dog` | 或运算 |
| `inurl:` | `inurl:login admin` | URL包含 |
| `intitle:` | `intitle:"index of" mp3` | 标题包含 |
| `..` | `laptop $500..$1000` | 数字范围 |
| `*` | `machine * algorithms` | 通配符 |

## 时间过滤参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `tbs=qdr:h` | 过去1小时 | `?q=news&tbs=qdr:h` |
| `tbs=qdr:d` | 过去24小时 | `?q=news&tbs=qdr:d` |
| `tbs=qdr:w` | 过去1周 | `?q=news&tbs=qdr:w` |
| `tbs=qdr:m` | 过去1月 | `?q=news&tbs=qdr:m` |
| `tbs=qdr:y` | 过去1年 | `?q=news&tbs=qdr:y` |

## 隐私搜索引擎对比

| 引擎 | 追踪 | 特点 | 推荐场景 |
|------|------|------|---------|
| **DuckDuckGo** | 无追踪 | 独立索引，Bangs快捷搜索 | 日常隐私搜索 |
| **Startpage** | 无追踪 | 使用Google结果 | 需要Google质量+隐私 |
| **Brave** | 无追踪 | 独立索引，快速 | 开源用户首选 |
| **Qwant** | 无追踪 | 欧盟GDPR合规 | 欧洲用户 |

### DuckDuckGo Bangs快捷搜索

| Bang | 目标 | 示例 |
|------|------|------|
| `!g` | Google | `!g python tutorial` |
| `!gh` | GitHub | `!gh tensorflow` |
| `!so` | Stack Overflow | `!so python error` |
| `!w` | Wikipedia | `!w machine learning` |
| `!yt` | YouTube | `!yt tutorial` |
| `!r` | Reddit | `!r programming` |

## WolframAlpha知识计算

### 数学计算
```
https://www.wolframalpha.com/input?i=integrate+x^2+dx
https://www.wolframalpha.com/input?i=solve+x^2+2x+1=0
https://www.wolframalpha.com/input?i=derivative+of+sin(x)
```

### 单位转换
```
https://www.wolframalpha.com/input?i=100+USD+to+CNY
https://www.wolframalpha.com/input?i=100+km+to+miles
https://www.wolframalpha.com/input?i=1+cup+to+ml
```

### 股票查询
```
https://www.wolframalpha.com/input?i=AAPL+stock
https://www.wolframalpha.com/input?i=苹果股价
```

### 天气查询
```
https://www.wolframalpha.com/input?i=weather+in+Beijing
https://www.wolframalpha.com/input?i=北京天气
```

### 科学计算
```
https://www.wolframalpha.com/input?i=mass+of+earth
https://www.wolframalpha.com/input?i=speed+of+light+in+km/h
https://www.wolframalpha.com/input?i=population+of+China
```

## 与天龙引擎集成

### 受益岗位

| 岗位 | 新增能力 |
|------|---------|
| **01调研师** | 隐私搜索 + 知识计算 |
| **32-01市场研究** | 多引擎对比搜索 |
| **62-02行业研究员** | WolframAlpha行业数据 |
| **64-01量化研究员** | WolframAlpha数学计算 |

### 与现有技能协同

| 天龙技能 | multi-search-engine | 协同效果 |
|---------|---------------------|---------|
| agent-reach | 隐私引擎+知识计算 | 能力互补 |
| search-cli | WolframAlpha | 计算能力补充 |
| deep-research | 多引擎验证 | 研究深度增强 |

## 使用建议

### 何时使用隐私搜索引擎
- 敏感话题研究
- 需要避免搜索历史记录
- 进行竞争情报收集

### 何时使用WolframAlpha
- 数学和科学计算
- 单位和货币转换
- 实时数据查询（股票、天气）
- 知识图谱查询

### 何时使用国内引擎
- 中文内容搜索
- 微信公众号文章
- 今日头条内容
- 国内网站

## 许可证

MIT

---

## 协同：与 dsh-web-search-pro（阶段 40.2 · 2026-08-24）

> **TL;DR**：本 skill 在 DSH 环境下应**降级为兜底通路**。`dsh-web-search-pro@0.1.8` 已经把 9 个引擎（seam/exa/ddg/bing/jina/github/bilibili/v2ex/youtube）封进 DSH bundle plugin + SQLite 持久化。

### 何时仍用本 skill（不降级）

1. **非 DSH 环境**（纯 Claude Code / 纯 IDE）：本 skill 是天龙零 key 兜底通路
2. **DSH 没装 web-search-pro bundle**：`python skills/dsh-web-search-pro-bridge/scripts/dsh_web_search_pro_check.py` exit=1 时
3. **需要零依赖 17 个零 key 引擎**（百度 / 360 / 搜狗 / 头条 / 微信 / 集思录 / Google / Yahoo / Startpage / Brave / Ecosia / Qwant / WolframAlpha）：这些 dsh-web-search-pro 没覆盖
4. **DSH 用户**显式要求"用 multi-search-engine"（罕见）

### 何时不再用本 skill（降级）

- DSH GUI 用户 + 装好 `dsh-web-search-pro@0.1.8` → 走 web_search_pro（持久化 + 引擎回退 + 凭证安全）

### 关联

- `dragon-engine/skills/dsh-web-search-pro-bridge/SKILL.md` — 天龙侧桥 V1.0
- `dragon-engine/skills/anysearch/SKILL.md` V3.1 — DSH bridge 探测
- `memory/stage-40-announce.md` — 阶段 40 总验收
