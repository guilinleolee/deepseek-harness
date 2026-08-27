# GLM Vision EXTEND.md

## 默认配置

---

## 自定义模型选择

### 免费模式
```json
{
  "model": "glm-4v-flash",
  "maxTokens": 1024
}
```

### 高质量模式
```json
{
  "model": "glm-4v",
  "maxTokens": 2048,
  "temperature": 0.7
}
```

---

## 自定义提示词模板

### 图像描述
```json
{
  "promptTemplate": "请详细描述这张图片的内容，包括：主体、背景、颜色、氛围等。"
}
```

### 文字提取
```json
{
  "promptTemplate": "请识别并提取图片中的所有文字内容，保持原有格式。"
}
```

### 图表分析
```json
{
  "promptTemplate": "请分析这张图表，提取数据并总结关键信息。"
}
```

### 代码识别
```json
{
  "promptTemplate": "请识别图片中的代码，并按原格式输出。"
}
```

---

## 自定义路由策略

### 成本优先
```json
{
  "routingStrategy": "costPriority",
  "fallbackModel": "glm-4v-flash"
}
```

### 质量优先
```json
{
  "routingStrategy": "qualityPriority",
  "preferredModel": "glm-4v"
}
```

---

## 配置优先级

CLI参数 > 项目级EXTEND.md > 用户级EXTEND.md > 默认配置

---

## 使用示例

### 项目级配置
```json
{
  "model": "glm-4v-flash",
  "maxTokens": 1024,
  "routingStrategy": "costPriority"
}
```

### 用户级配置
```json
{
  "model": "glm-4v",
  "maxTokens": 2048,
  "temperature": 0.7,
  "routingStrategy": "qualityPriority"
}
```