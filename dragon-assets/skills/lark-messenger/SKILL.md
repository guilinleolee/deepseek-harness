---
license: UNKNOWN
triggers: ["lark messenger", "Lark Messenger Skill"]
---
# Lark Messenger Skill

> 飞书/Lark 消息操作能力 - 群/私聊消息读写、线程回复、文件下载

## 核心能力

| 能力 | 功能 | 使用场景 |
|------|------|---------|
| **消息读取** | 群聊/私聊/线程消息 | 信息收集、舆情监控 |
| **消息发送** | 发送/回复/搜索消息 | 自动通知、客服回复 |
| **文件操作** | 下载附件 | 文档收集 |
| **线程管理** | Thread回复 | 讨论追踪 |

## 安装要求

```bash
# 安装 OpenClaw CLI
npm install -g openclaw

# Node.js 版本要求
node --version  # >= 22
```

## 配置

### 1. 飞书开放平台配置

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 配置权限：
   - `im:message` - 消息读写
   - `im:message:send_as_bot` - 以应用身份发消息
   - `im:chat` - 群组信息
   - `drive:drive` - 文件下载

### 2. 环境变量

```bash
export LARK_APP_ID="your_app_id"
export LARK_APP_SECRET="your_app_secret"
```

## 命令参考

### 消息读取

```bash
# 读取群聊消息
/lark-messenger read --chat-id "oc_xxx" --limit 50

# 读取私聊消息
/lark-messenger read --chat-id "ou_xxx" --limit 20

# 读取线程消息
/lark-messenger read-thread --message-id "om_xxx"

# 搜索消息
/lark-messenger search --query "关键词" --chat-id "oc_xxx"
```

### 消息发送

```bash
# 发送文本消息
/lark-messenger send --chat-id "oc_xxx" --text "消息内容"

# 发送富文本消息
/lark-messenger send --chat-id "oc_xxx" --rich-text '{"title":"标题","content":[[{"tag":"text","text":"内容"}]]}'

# 回复消息
/lark-messenger reply --message-id "om_xxx" --text "回复内容"

# 线程回复
/lark-messenger reply-thread --message-id "om_xxx" --text "线程回复"
```

### 文件操作

```bash
# 下载附件
/lark-messenger download --file-key "file_xxx" --output "./downloads/"

# 批量下载
/lark-messenger download-batch --message-id "om_xxx" --output "./downloads/"
```

## Python API

```python
from lark_messenger import LarkMessenger

# 初始化
messenger = LarkMessenger(app_id, app_secret)

# 读取消息
messages = messenger.read_messages(chat_id="oc_xxx", limit=50)

# 发送消息
messenger.send_message(chat_id="oc_xxx", text="消息内容")

# 回复消息
messenger.reply_message(message_id="om_xxx", text="回复内容")

# 下载文件
messenger.download_file(file_key="file_xxx", output_path="./downloads/")
```

## 天龙岗位映射

| 岗位 | 使用场景 | 匹配度 |
|------|---------|--------|
| **35-02 社媒运营** | 飞书群运营、自动回复、消息监控 | ⭐⭐⭐⭐⭐ |
| **01 调研师** | 群聊信息收集、用户反馈分析 | ⭐⭐⭐⭐ |
| **07 记录师** | 消息归档、知识沉淀 | ⭐⭐⭐⭐ |
| **08 发布师** | 发布通知、变更公告 | ⭐⭐⭐⭐ |

## 使用示例

### 示例1：自动化群运营

```python
# 自动监控群聊关键词并回复
messenger.monitor_keywords(
    chat_id="oc_xxx",
    keywords=["帮助", "问题", "bug"],
    auto_reply="感谢反馈，我们已收到您的问题，会尽快处理。"
)
```

### 示例2：消息归档

```python
# 归档群聊消息到本地
messenger.archive_messages(
    chat_id="oc_xxx",
    output_dir="./archives/",
    format="markdown"  # 支持 json, markdown, txt
)
```

### 示例3：客服自动回复

```python
# 基于规则的自动回复
rules = {
    "价格": "我们的产品价格请查看：https://example.com/pricing",
    "功能": "功能介绍请查看：https://example.com/features",
    "联系": "请联系客服：support@example.com"
}
messenger.auto_reply_rules(chat_id="oc_xxx", rules=rules)
```

## 安全警告

⚠️ **AI幻觉风险**：AI可能误解意图，建议：
- 先在测试群验证
- 避免在生产群直接使用
- 设置人工审核机制

## 错误处理

| 错误码 | 说明 | 解决方案 |
|--------|------|---------|
| 99991663 | 权限不足 | 检查应用权限配置 |
| 99991664 | 消息不存在 | 检查消息ID是否正确 |
| 99991661 | 群组不存在 | 检查群组ID是否正确 |

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| 1.0.0 | 2026-03-14 | 初始版本，支持消息读写、文件下载 |