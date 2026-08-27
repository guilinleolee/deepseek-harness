# FastGPT 配置说明

## 首次启动后手动操作

### 1. 访问管理后台

浏览器打开 http://localhost:3000

- 用户名: root
- 密码: 来自 .env 的 FASTGPT_ROOT_PASSWORD

### 2. 配置 LLM（OpenAI 兼容 · 指向 MiniMax）

进入 "系统设置" → "模型配置" → "新增模型":

| 字段 | 值 |
|------|-----|
| 模型类型 | LLM |
| 模型名称 | MiniMax-M3 |
| API Base URL | https://api.minimax.chat/v1 |
| API Key | 从 dragon-engine/.env 复制 OPENAI_API_KEY |
| 模型标识 | MiniMax-M3 |
| 温度 | 0.7 |
| Max Tokens | 2000 |

Embedding 模型同样配置。

### 3. 创建知识库

进入 "知识库" → "新建知识库"，上传：

- 产品手册（PDF / Markdown）
- 常见 Q&A（CSV / Excel）
- 退换货政策
- 服务条款

### 4. 创建机器人应用

进入 "应用" → "新建应用":

- 关联知识库: 上一步创建的知识库
- 系统提示词: 你是专业的客服助手...
- 关联模型: MiniMax-M3
- 温度: 0.5
- 引用上限: 5

### 5. 测试对话

"应用" → "调试"，发条消息验证。

---

## API 对接

客服后端通过 FastGPT 的 OpenAI 兼容 API:

```http
POST http://fastgpt:3000/api/v1/chat/completions
Authorization: Bearer ${FASTGPT_API_KEY}
Content-Type: application/json

{
  "messages": [{"role": "user", "content": "用户问题"}],
  "stream": false,
  "detail": true
}
```

响应里 detail.quoteList 是命中的知识库引用，存到消息表的 knowledge_refs 字段。
