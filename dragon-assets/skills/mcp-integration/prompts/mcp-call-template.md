# MCP调用提示词模板

## 概述

本模板用于在需要调用MCP服务时生成标准化的提示词。

## MCP调用标准格式

```
[角色]: MCP服务调用请求
[任务]: <具体任务描述>
[输入]: <用户提供的参数>
[输出要求]: <期望的返回格式>
[约束条件]: <技术约束和限制>
```

## MCP调用场景

### 场景1：地理编码

```
[角色]: MCP地理编码服务调用
[任务]: 将地址转换为地理坐标
[输入]:
  - 地址: {address}
[输出要求]:
  - 返回JSON格式的坐标数据
  - 包含: lat, lng, formatted_address, confidence
[约束条件]:
  - 使用免费Nominatim API（无API key时）
  - 优先使用Geoapify（有API key时）
  - 限速: 1请求/秒
```

### 场景2：GEO分析

```
[角色]: MCP GEO分析服务调用
[任务]: 分析网站的GEO健康度
[输入]:
  - URL: {url}
[输出要求]:
  - 返回五维评分
  - 包含可执行建议
  - 生成GEO分析报告
[约束条件]:
  - 遵循天龙引擎seo-geo技能标准
  - 使用MCP连接池优化性能
```

### 场景3：Schema生成

```
[角色]: MCP Schema生成服务调用
[任务]: 生成JSON-LD结构化数据
[输入]:
  - Schema类型: {schema_type}
  - 内容数据: {content_data}
[输出要求]:
  - 返回合规的JSON-LD
  - 包含所有必需字段
  - 支持Schema验证
[约束条件]:
  - 遵循schema.org标准
  - 支持类型: Article, FAQPage, Organization, Person, Product
```

### 场景4：llms.txt生成

```
[角色]: MCP llms.txt生成服务调用
[任务]: 生成网站AI可读文件
[输入]:
  - 网站URL: {site_url}
  - 页面列表: {pages}
[输出要求]:
  - 生成标准的llms.txt格式
  - 包含关键页面描述
  - 优化AI引用友好度
[约束条件]:
  - 遵循llms.txt规范
  - 限制文件大小
```

## MCP响应处理

### 成功响应

```json
{
  "success": true,
  "data": {
    "result_key": "result_value"
  },
  "metadata": {
    "server": "mcp-server-name",
    "duration_ms": 150,
    "cached": false
  }
}
```

### 错误响应

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {}
  },
  "metadata": {
    "server": "mcp-server-name",
    "duration_ms": 50
  }
}
```

## MCP调用最佳实践

1. **连接池复用**: 使用MCPClientPool减少连接开销
2. **请求去重**: 相同请求在短时间内返回缓存结果
3. **超时处理**: 设置合理的超时时间
4. **错误重试**: 对临时性错误进行重试
5. **日志记录**: 记录所有MCP调用用于调试

## MCP调用流程

```
1. 识别需求 → 确定需要调用的MCP服务
       ↓
2. 检查缓存 → 查看是否有缓存的响应
       ↓
3. 获取连接 → 从连接池获取MCP客户端
       ↓
4. 执行调用 → 调用MCP服务
       ↓
5. 处理结果 → 解析响应并格式化
       ↓
6. 更新缓存 → 缓存可复用的结果
       ↓
7. 释放连接 → 归还到连接池
```

## 与天龙引擎集成

MCP服务可以与天龙引擎的以下组件集成：

| 天龙组件 | MCP服务 | 集成方式 |
|---------|---------|---------|
| seo-geo | geo-analyzer | 获取GEO分析数据 |
| geo-optimizer | schema-generator | 生成结构化数据 |
| geo-content-generator | llms-generator | 生成llms.txt |
| 35-04 GEO内容优化师 | brand-tracker | 追踪品牌可见性 |
| 01调研师 | competitor-mcp | 竞品分析 |
| 04验证师 | citation-mcp | 引用检查 |
