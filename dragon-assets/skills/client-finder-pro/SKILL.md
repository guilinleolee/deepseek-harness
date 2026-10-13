---
license: UNKNOWN
name: client-finder-pro
version: 1.0.0
description: |
  Automatically search and compile customer information by industry keyword for Chinese market. Extracts company details and contact info from search engines, industry websites, and business directories. Outputs formatted Markdown tables and auto-saves CSV for CRM import.
author: 天龙引擎团队
created: 2026-02-26
category: development

triggers:
  - "用户提到「client-finder-pro 客户搜寻专家」时"
---

# Client Finder Pro

自动搜索并整理客户信息的智能助手，专为中国市场设计。

## When to Use This Skill

- 搜索行业相关的公司信息和联系方式
- 快速获取潜在客户列表
- 准备客户开发（BD）或销售线索
- 导入国产CRM系统（销售易、纷享销客、EC SCRM等）

## What This Skill Does

1. **智能搜索**: 根据行业关键词在搜索引擎查找相关公司
2. **信息提取**: 提取公司名称、网站、所在地、联系方式等信息
3. **数据验证**: 验证数据完整性和去重
4. **自动保存**: 自动保存为CSV格式，支持国产CRM导入
5. **进度显示**: 实时显示搜索进度

## How to Use

### Basic Usage

直接描述要搜索的行业：

```
帮我找一些SaaS公司
搜索北京的制造业客户
查找上海的餐饮企业，大概30家
```

### With Slash Command (推荐)

```bash
# 基础用法
/find-clients SaaS

# 指定地区
/find-clients 制造业 广东

# 指定数量
/find-clients 餐饮 北京 30
```

## Instructions

当用户请求客户信息搜索时，按以下步骤执行：

### Step 1: 理解需求

确认搜索参数：
- **行业关键词**（必需）：如"SaaS"、"制造业"、"餐饮"
- **目标地区**（可选）：如"北京"、"广东"、"全国"
- **公司数量**（可选）：默认50家，范围1-100

使用AskUserQuestion确认缺失信息。

### Step 2: 构建搜索策略

使用可用的搜索工具执行**多轮多源搜索**：

#### 2.0 搜索工具降级策略

**优先级顺序**（当主搜索工具不可用时自动降级）：

1. **WebSearch** - 主搜索工具
2. **Brave Search MCP** (`mcp__brave_search__*`) - 备用搜索，独立API配额
3. **Exa MCP** (`mcp__exa__*`) - 备用搜索，专注搜索质量
4. **mcp__fetch__fetch** - 直接获取网页内容
5. **mcp__web_reader__webReader** - 网页解析和提取

**降级检测逻辑**：
```
if WebSearch 返回 "monthly usage limit has been reached":
    尝试使用 Brave Search MCP
    if Brave Search 不可用:
        尝试使用 Exa MCP
        if Exa 不可用:
            使用 fetch + webReader 直接访问企业信息平台
```

**Brave Search 使用方法**（如可用）：
```
调用 brave search 工具，查询参数：
- query: "{行业} 公司 {地区}"
- count: 20
- textDecorations: false
- searchLang: "zh-CN"
```

#### 2.1 搜索引擎查询（百度/Google/Brave）

**基础查询模板**（每个都执行）：
```
{行业} 公司 {地区}
{行业} 企业 {地区}
{行业} 服务商 {地区}
{行业} 厂家 {地区}
{行业} 供应商 {地区}
{行业} 公司大全 {地区}
{行业} 企业名录 {地区}
{行业} 十强 {地区}
{行业} 龙头企业 {地区}
```

#### 2.2 深度数据源查询

**招聘网站**（获取HR联系方式）：
```
site:zhipin.com {行业} 公司 {地区}
site:lagou.com {行业} 公司 {地区}
site:51job.com {行业} 公司 {地区}
site:liepin.com {行业} {地区}
```

**企业信息平台**：
```
site:qcc.com {行业} 公司 {地区}
site:tianyancha.com {行业} {地区}
site:qichacha.com {行业} {地区}
```

**地图/黄页**（获取本地商家）：
```
site:amap.com {行业} {地区}
site:dianping.com {行业} {地区}
{行业} 黄页 {地区}
{行业} 电话 {地区}
```

**LinkedIn**（获取企业决策人信息，适合国际企业和外向型企业）：
```
site:linkedin.com/company {行业} {地区}
site:linkedin.com {行业} 公司 {地区}
"{行业}" companies {地区} LinkedIn
```

**脉脉**（获取中国企业职场信息，作为LinkedIn的补充）：
```
site:maimai.cn {行业} 公司 {地区}
{行业} 公司 脉脉 {地区}
```

### Step 3: 执行搜索并显示进度

```
正在搜索 "{行业}" 的公司信息（目标：{数量}家）...

[进度 1/7] 搜索引擎查询中...
[进度 2/7] 招聘网站查询中...
[进度 3/7] 企业信息平台查询中...
[进度 4/7] LinkedIn/脉脉查询中...
[进度 5/7] 深度挖掘官网联系信息...
[进度 6/7] 验证和去重数据...
[进度 7/7] 生成CSV文件...

✓ 搜索完成！找到 {total_found} 家公司，{valid_count} 家数据有效
```

### Step 4: 深度挖掘官网联系信息

对每个找到的公司，执行以下深度挖掘：

#### 4.1 官网Contact页面挖掘

使用 `mcp__web_reader__webReader` 访问公司官网：

**目标页面**：
- `/contact` 或 `/contact-us` - 联系我们
- `/about` - 关于我们
- `/team` - 团队介绍
- `/join` - 加入我们/招聘

**提取信息**：
- 公司名称（验证）
- 联系电话
- 邮箱地址（通用邮箱如 info@, contact@, sales@）
- 公司地址
- 微信公众号/二维码
- 决策人信息（CEO/总经理/业务负责人）

#### 4.2 招聘信息挖掘

**从招聘网站提取**：
- 招聘HR联系方式
- 公司规模（从招聘岗位数量推断）
- 公司地址（从工作地点推断）
- 薪资范围（判断公司实力）
- 业务部门负责人（如技术总监、销售总监）

#### 4.3 企业信息平台

**从企查查/天眼查提取**：
- 注册资本（判断公司规模）
- 法人代表
- 注册地址
- 经营范围
- 联系电话（如公开）
- 邮箱（如公开）

#### 4.4 LinkedIn/脉脉信息提取

**从LinkedIn提取**（适合国际企业和外向型企业）：
- 公司LinkedIn页面URL
- 员工数量
- 行业分类
- 公司总部地址
- 关键决策人（CEO、CTO、VP等）
- 决策人LinkedIn个人资料链接

**从脉脉提取**（适合中国企业）：
- 公司认证信息
- 员工评价
- 招聘活跃度
- 业务口碑
- 联系方式（如公开）

### Step 5: 提取和验证数据

对每个搜索结果提取以下字段：

**必需字段**：
- 公司名称
- 所在地

**推荐字段**：
- 网站
- 联系人/决策人
- 邮箱
- 电话
- 公司规模
- 行业分类

**数据验证**：
- 去重检查（按公司名称）
- 网站格式验证
- 邮箱格式验证
- 丢弃无效数据

### Step 6: 格式化输出

**Markdown表格预览**：
```markdown
# 客户信息搜索结果

## 搜索概览
- **行业**: {industry}
- **地区**: {location}
- **搜索时间**: {timestamp}
- **找到公司**: {total_found}
- **有效数据**: {valid_count}

## 公司列表

| # | 公司名称 | 网站 | 所在地 | 规模 | 联系方式 | 备注 |
|---|---------|------|-------|------|----------|------|
```

**CSV自动保存**：
- 文件名：`客户信息_{行业}_{时间戳}.csv`
- 保存路径：`~/客户搜索结果/`
- 编码：UTF-8（兼容国产CRM）
- 字段：公司名称,联系人,职位,手机,邮箱,公司网站,所在地区,公司规模,行业,LinkedIn,脉脉,备注,数据来源

### Step 7: 提供后续操作建议

```markdown
## 后续操作建议

1. **导入CRM系统**
   - CSV文件已保存到：{file_path}
   - 支持销售易、纷享销客、EC SCRM等系统

2. **深度分析**
   - 可使用 lead-research-assistant SKILL 对客户进行优先级排序
   - 获取个性化联系策略

3. **数据验证**
   - 建议访问官网确认联系方式
   - 关注公司近期动态
```

## Output Format

### Markdown格式
```markdown
# 客户信息搜索结果

## 搜索概览
- **行业**: SaaS
- **地区**: 北京
- **找到公司**: 22
- **有效数据**: 20

## 公司列表

| # | 公司名称 | 网站 | 所在地 | 规模 | 联系方式 | 备注 |
|---|---------|------|-------|------|----------|------|
| 1 | XX科技 | https://xx.com | 北京 | 100-500人 | contact@xx.com | - |
| 2 | YY软件 | https://yy.cn | 北京 | 50-100人 | info@yy.cn | - |

## CSV文件
已保存到：`~/客户搜索结果/客户信息_SaaS_20250113103000.csv`
```

### CSV格式
```csv
公司名称,联系人,职位,手机,邮箱,公司网站,所在地区,公司规模,行业,LinkedIn,脉脉,备注,数据来源
"XX科技","张三","CEO","13800138000","zhangsan@xx.com","https://xx.com","北京","100-500人","SaaS","https://linkedin.com/company/xx-tech","","有海外业务","搜索引擎"
```

## Examples

### Example 1: Basic Search
**User**: `/find-clients SaaS`

**Output**: 搜索全国SaaS公司，返回20家，自动保存CSV

### Example 2: Location-Specific
**User**: `/find-clients 制造业 广东`

**Output**: 搜索广东制造业公司

### Example 3: With Quantity
**User**: `/find-clients 餐饮 北京 30`

**Output**: 搜索北京餐饮企业，目标30家

## Technical Notes

### WebSearch 限额备用方案

当 WebSearch 达到月度限额时，SKILL 会自动切换到备用搜索方案：

**方案 A：直接访问企业信息平台**

使用以下平台的公开搜索功能（无需搜索引擎）：

1. **企查查** (qcc.com)
   - 直接搜索 URL: `https://www.qcc.com/web/search?key={关键词}`
   - 使用 webReader 提取结果

2. **天眼查** (tianyancha.com)
   - 搜索 URL: `https://www.tianyancha.com/search?key={关键词}`

3. **阿里巴巴**
   - 公司黄页: `https://s.1688.com/company/{关键词}.html`

**方案 B：使用 MCP 备用搜索**

如果 Brave Search MCP 或 Exa MCP 已激活：
- 这些服务有独立的 API 配额
- 不受 WebSearch 限额影响
- 配置文件：`~/.claude/mcp_servers.json`

**方案 C：手动搜索指南**

引导用户访问以下网站进行手动搜索：
- 百度: `https://www.baidu.com/s?wd={行业}+公司+{地区}`
- 必应: `https://www.bing.com/search?q={行业}+companies+{地区}`
- LinkedIn: `https://www.linkedin.com/search/results/companies/?keywords={行业}&location={地区}`

### API Constraints

- 所有WebSearch调用设置 `timeout=30`
- 如遇网络错误，自动重试1次
- 避免短时间内大量请求（防止限流）
- **WebSearch 月度限额**: 约 15-20 次/月（2026年2月1日重置）

### CSV Encoding

使用UTF-8编码（无BOM），确保国产CRM正确显示中文。

## Related Skills

- **lead-research-assistant**: 深度分析和优先级排序
- **content-creator**: 生成客户开发邮件模板

## Tips for Best Results

- **使用具体行业词**：如"SaaS"而非"软件"
- **限定地区范围**：提高数据相关性
- **合理设置数量**：20-30家为宜
- **验证关键信息**：重要客户建议人工核实

#### Evolution Pattern (Maintenance)

To preserve custom improvements when a core skill is upgraded, avoid editing `SKILL.md` directly for individual modifications. Instead:

1. Create or update an `evolution.json` file in the skill's root directory.
2. Store modification suggestions, custom rules, or evolved logic there.
3. This ensures that your custom "evolutions" are preserved even if the base `SKILL.md` is replaced during an upgrade.
