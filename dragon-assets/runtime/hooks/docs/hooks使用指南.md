# Claude Code Hooks 使用指南

> 快速参考：在 Claude Code 中使用事件钩子自定义行为

---

## 📌 Hooks 配置位置

```json
// ~/.claude/settings-with-hooks.json 或 ~/.claude/settings.json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "可选正则匹配",
        "hooks": [
          {
            "type": "command",
            "command": "python /path/to/hook.py",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

---

## 🔗 可用的 Hook 事件

| 事件 | 触发时机 | 用途 |
|------|----------|------|
| `SessionStart` | 打开 Claude Code | 注入历史上下文、初始化 |
| `UserPromptSubmit` | 用户提交提示 | 保存提示、初始化会话 |
| `PreToolUse` | 工具执行前 | 验证、拦截危险操作 |
| `PostToolUse` | 工具执行后 | 记录日志、安全检查 |
| `Stop` | 用户停止提问 | 生成摘要、保存状态 |
| `SessionEnd` | 会话关闭 | 清理资源、标记完成 |
| `SubagentStop` | 子代理停止 | 通知 |
| `PreCompact` | 上下文压缩前 | 准备压缩 |
| `Notification` | 通知事件 | 显示通知 |

---

## 📝 Hook 脚本模板

### Python 模板

```python
#!/usr/bin/env python3
import json
import sys

# 从 stdin 读取输入（JSON 格式）
input_data = json.loads(sys.stdin.read())

session_id = input_data.get("session_id", "")
cwd = input_data.get("cwd", "")

# 你的处理逻辑
result = process(input_data)

# 输出结果
print(json.dumps({
    "continue": True,           # 是否继续
    "suppressOutput": True,     # 是否抑制输出
    "hookSpecificOutput": {
        "additionalContext": "注入给Claude的上下文"
    }
}))
```

### Shell 模板

```bash
#!/bin/bash
# 从 stdin 读取输入
input=$(cat)
session_id=$(echo "$input" | jq -r '.session_id')
cwd=$(echo "$input" | jq -r '.cwd')

# 你的处理逻辑
# ...

# 输出结果
echo '{"continue": true, "suppressOutput": true}'
```

---

## 🎯 常见使用场景

### 1. 安全检查（PreToolUse）

```python
# security_hook.py
file_path = input_data.get("tool_input", {}).get("file_path", "")

# 检查是否在编辑敏感文件
if ".env" in file_path or "credentials" in file_path:
    print("⚠️ 警告：正在编辑敏感文件！", file=sys.stderr)
    # sys.exit(2)  # 取消注释可阻止操作
```

### 2. 日志记录（PostToolUse）

```python
# logger_hook.py
tool_name = input_data.get("tool_name")
tool_input = input_data.get("tool_input")

with open("tool_log.txt", "a") as f:
    f.write(f"{session_id} | {tool_name} | {tool_input}\n")
```

### 3. 自动保存上下文（UserPromptSubmit）

```python
# context_saver.py
prompt = input_data.get("prompt", "")
project = os.path.basename(cwd)

with open(f"{project}_prompts.log", "a") as f:
    f.write(f"[{datetime.now()}] {prompt}\n")
```

---

## ⚙️ 完整配置示例

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python ~/.claude/hooks/save_prompt.py",
            "timeout": 5
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python ~/.claude/hooks/check_security.py",
            "timeout": 10
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python ~/.claude/hooks/log_tool.py",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

---

## 🔧 调试技巧

### 查看输入数据

```python
#!/usr/bin/env python3
import json
import sys

input_data = json.loads(sys.stdin.read())

# 将输入保存到文件用于调试
with open("/tmp/hook_debug.json", "w") as f:
    json.dump(input_data, f, indent=2)

print(json.dumps({"continue": True, "suppressOutput": True}))
```

### 测试 Hook

```bash
# 手动测试 hook
echo '{"session_id":"test","cwd":"/tmp"}' | python your_hook.py
```

---

## ⚠️ 注意事项

1. **超时设置**：建议设置合理的 timeout（默认 120 秒）
2. **错误处理**：Hook 脚本应该健壮，避免因错误中断 Claude
3. **性能影响**：Hook 在每次事件时执行，保持脚本轻量
4. **输出格式**：确保输出有效的 JSON
5. **路径问题**：使用绝对路径或 `~/.claude/hooks/` 存放脚本

---

## 🚀 快速开始

1. 创建 hooks 目录：
```bash
mkdir -p ~/.claude/hooks
```

2. 创建你的第一个 hook：
```bash
cat > ~/.claude/hooks/my_first_hook.py << 'EOF'
#!/usr/bin/env python3
import json
import sys

input_data = json.loads(sys.stdin.read())
print(json.dumps({"continue": True, "suppressOutput": True}))
EOF
chmod +x ~/.claude/hooks/my_first_hook.py
```

3. 在配置中添加 hook：
```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [{
          "type": "command",
          "command": "python ~/.claude/hooks/my_first_hook.py"
        }]
      }
    ]
  }
}
```

4. 重启 Claude Code

---

**详细文档**：参考 [Claude Code Hooks Architecture](https://docs.anthropic.com/claude-code/hooks)
