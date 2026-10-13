# Client Finder Pro - 搜索备用方案指南

## 问题：WebSearch 达到月度限额

当您看到以下错误时：
> "the monthly usage limit has been reached. The quota will reset on February 1, 2026"

说明 WebSearch 工具已达到月度使用限额（约15-20次/月）。

## 解决方案

### 方案 1：激活 Brave Search MCP（推荐）

Brave Search 有独立的 API 配额，不受 WebSearch 限额影响。

**步骤**：

1. 确认 MCP 配置文件中已有 Brave Search 配置：
   ```bash
   cat ~/.claude/mcp_servers.json | grep -A 5 brave-search
   ```

2. 如果看到以下内容，说明已配置：
   ```json
   "brave-search": {
     "command": "npx",
     "args": ["-y", "@brave/brave-search-mcp-server"],
     "env": {
       "BRAVE_API_KEY": "BSAAXosKZM5x1_vIjBY3j2kBKOtI3Fx"
     }
   }
   ```

3. **重启 Claude Code** 让 MCP 服务器生效

4. 重新执行 `/find-clients` 命令

### 方案 2：手动搜索 + 数据整理

#### 2.1 使用企业信息平台搜索

**企查查** (qcc.com)
```
访问：https://www.qcc.com/web/search
搜索：桂林 制造业
```

**天眼查** (tianyancha.com)
```
访问：https://www.tianyancha.com/search
搜索：桂林 制造业
```

**阿里巴巴公司库**
```
访问：https://s.1688.com/company/
搜索：桂林 制造业公司
```

#### 2.2 使用招聘网站查找（获取HR联系方式）

**Boss直聘**
```
访问：https://www.zhipin.com/
搜索：桂林 制造业
查看：公司列表 + HR联系方式
```

**猎聘**
```
访问：https://www.liepin.com/
搜索：桂林 制造业
```

#### 2.3 使用 LinkedIn 查找（适合外向型企业）

```
访问：https://www.linkedin.com/search/results/companies/
Keywords: 制造业
Location: 桂林，广西，中国
```

#### 2.4 使用脉脉查找（中国企业）

```
访问：https://www.maimai.cn/
搜索：桂林 制造业
```

### 方案 3：使用通用搜索引擎

**百度**
```
https://www.baidu.com/s?wd=桂林+制造业+公司
```

**必应**
```
https://www.bing.com/search?q=Guilin+manufacturing+companies
```

**Google**（如可访问）
```
https://www.google.com/search?q=桂林+制造业+公司+名录
```

### 方案 4：使用地图/黄页应用

**高德地图**
```
搜索：桂林 制造业
筛选：企业/工厂
```

**大众点评**
```
搜索：桂林 企业服务
```

## 手动搜索后如何处理

1. **收集数据到 Excel/CSV**
   - 公司名称
   - 联系电话
   - 邮箱
   - 地址
   - 网址

2. **使用 content-research-writer SKILL 整理**
   ```
   帮我整理这些公司信息到 Markdown 表格格式
   ```

3. **手动保存为 CSV**（兼容国产CRM）
   ```csv
   公司名称,联系人,职位,手机,邮箱,公司网站,所在地区,公司规模,行业,备注
   ```

## 等待限额重置

WebSearch 限额将在 **2026年2月1日** 重置。

重置后即可正常使用 `/find-clients` 命令。

## 技术说明

### WebSearch 限额原因

WebSearch 使用第三方搜索 API，有月度调用限制：
- 限额：约 15-20 次/月
- 重置：每月1号
- 当前状态：已达到限额

### Brave Search MCP 优势

- 独立 API 配额（不受 WebSearch 限制）
- 搜索结果质量高
- 支持中文搜索
- 已配置 API Key

### MCP 激活检测

运行以下命令检测 MCP 是否激活：
```bash
# 检查配置
cat ~/.claude/mcp_servers.json

# 重启 Claude Code 后，在 Claude 中测试
# 输入：帮我搜索桂林制造业公司
# 如果使用 Brave Search，说明 MCP 已激活
```

## 总结

| 方案 | 难度 | 效果 | 推荐度 |
|-----|-----|-----|-------|
| 激活 Brave Search MCP | 低 | 高 | ⭐⭐⭐⭐⭐ |
| 企查查/天眼查 | 低 | 高 | ⭐⭐⭐⭐ |
| LinkedIn/脉脉 | 中 | 中 | ⭐⭐⭐ |
| 手动搜索引擎 | 低 | 中 | ⭐⭐⭐ |
| 等待重置 | 无 | 高 | ⭐⭐（需等待） |

**推荐操作顺序**：
1. 尝试激活 Brave Search MCP
2. 使用企查查/天眼查手动搜索
3. 使用招聘网站补充联系人信息
4. 等待2月1日限额重置
