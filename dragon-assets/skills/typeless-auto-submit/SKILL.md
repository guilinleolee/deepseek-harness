---
license: UNKNOWN
github_repo: AllenHu0829/typeless-auto-submit.git
github_hash: 7d9945c18c35ff89bd7663d1d1cac3dd59ff0624
last_updated: 2026-04-25
source_type: derived
triggers: ["typeless auto submit", "typeless-auto-submit - 免手操作语音交互"]
---
# typeless-auto-submit - 免手操作语音交互

> **版本**: V1.0 | **来源**: [AllenHu0829/typeless-auto-submit](https://github.com/AllenHu0829/typeless-auto-submit) | **集成日期**: 2026-03-29

## 核心价值

为 Claude Code 提供**全程免手操作**的语音交互能力，填补天龙引擎在**语音交互**领域的关键空白。

```
┌─────────────────────────────────────────────────────────────┐
│  typeless-auto-submit 核心能力                               │
├─────────────────────────────────────────────────────────────┤
│  🎤 语音输入 → Fn键触发听写，说完再按Fn，自动提交           │
│  🔊 语音输出 → Claude响应通过TTS实时朗读                    │
│  ⌨️ 免手操作 → 全程无需键盘，双手解放                       │
│  🍎 macOS原生 → IOKit HID深度集成，无侵入                   │
└─────────────────────────────────────────────────────────────┘
```

## 技术架构

| 组件 | 技术 | 功能 |
|------|------|------|
| **dictation-auto-submit** | Swift + IOKit HID | Fn键监听 + 自动提交 |
| **voice-response.sh** | Bash + macOS say | TTS语音输出 |
| **voice-toggle.sh** | Bash | 语音模式控制 |
| **launchd守护进程** | plist | 开机自启 |

## 核心流程

### 语音输入流程
```
Fn键 → 激活macOS听写 → 说话 → Fn键 → 结束听写 → [2.5s延迟] → 自动发送Enter → Claude处理
```

### 语音输出流程
```
Claude响应 → Stop Hook触发 → 文本提取 → 净化处理 → TTS朗读
```

## 安装配置

### 前置条件
- macOS 13+
- Claude Code CLI
- Ghostty / Terminal / iTerm2 / Warp / Kitty / Alacritty
- macOS Dictation 已启用
- Xcode Command Line Tools

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/AllenHu0829/typeless-auto-submit.git
cd typeless-auto-submit

# 2. 编译Swift二进制
mkdir -p ~/.claude/hooks
swiftc -o ~/.claude/hooks/dictation-auto-submit \
  dictation-auto-submit.swift \
  -framework IOKit -framework Foundation -framework CoreGraphics

# 3. 安装Shell脚本
cp voice-response.sh ~/.claude/hooks/
cp voice-toggle.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/voice-response.sh ~/.claude/hooks/voice-toggle.sh

# 4. 配置Stop Hook
# 添加到 ~/.claude/settings.json
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "bash ~/.claude/hooks/voice-response.sh",
        "async": true
      }]
    }]
  }
}

# 5. 授权权限
# System Settings > Privacy & Security 添加:
# - Input Monitoring (检测Fn键)
# - Accessibility (发送Enter到终端)

# 6. 启动服务
touch ~/.claude/voice-enabled
~/.claude/hooks/dictation-auto-submit &
```

## 使用命令

### 语音控制
```bash
# 语音开关
voice-toggle.sh on/off/status

# 切换语音
voice-toggle.sh voice Tingting    # 中文
voice-toggle.sh voice Samantha     # 英文
voice-toggle.sh voice Alex        # 英文

# 调节语速 (WPM)
voice-toggle.sh rate 180         # 慢速
voice-toggle.sh rate 220         # 正常
voice-toggle.sh rate 280         # 快速
```

### 语音输入
```
按 Fn → 开始听写 → 说话 → 按 Fn → 结束 → 等待2.5s → 自动提交
```

## 与天龙引擎协同

### 1. 桌面自动化增强 (17-04 桌面自动化工程师)
```
当前: turix-desktop-agent 操作GUI，但输入仍需键盘
升级: typeless-auto-submit 提供语音输入能力
效果: 真正实现"动口不动手"的桌面自动化
```

### 2. 多模态交互升级 (全部岗位)
```
场景: 双手忙碌时（驾驶、烹饪、运动）仍可使用Claude Code
流程: 语音输入 → Claude处理 → TTS输出
```

### 3. 无障碍访问 (全部岗位)
```
场景: 行动不便用户通过语音使用Claude Code
价值: 无障碍访问能力
```

### 4. IM平台语音控制 (47-03 IM运营师)
```
场景: Telegram/Discord/QQ 控制天龙引擎
流程: 语音消息 → ASR转文字 → Claude处理 → TTS输出
```

## 岗位升级

| 岗位 | 升级内容 | 提升 |
|------|---------|------|
| **17-04 桌面自动化工程师** | 语音输入能力增强 | 质的飞跃 |
| **47-03 IM运营师** | 语音控制IM Bot | 质的飞跃 |
| **全部岗位** | 多模态交互支持 | 用户体验+200% |

## 文本净化规则

voice-response.sh 会自动净化Claude响应：

```bash
# 移除内容
- 代码块和内联代码
- Markdown表格
- URLs和文件路径
- 多余空白

# 智能处理
- 提取关键句子（最多3行，300字符）
- 中英文标点转换（。vs.）
- 多段落合并
```

## 局限性

| 限制 | 说明 | 缓解 |
|------|------|------|
| 平台限制 | 仅macOS | Windows需重写 |
| 终端依赖 | 需终端支持AppleScript | 仅支持主流终端 |
| 权限要求 | 需Input Monitoring+Accessibility | 用户手动授权 |
| 中文优化 | 默认Tingting语音 | 可扩展更多语音 |
| 延迟 | 2.5s固定延迟 | 可配置 |

## 文件路径

| 文件 | 路径 |
|------|------|
| Swift源码 | `~/.claude/hooks/dictation-auto-submit` |
| TTS Hook | `~/.claude/hooks/voice-response.sh` |
| 语音控制 | `~/.claude/hooks/voice-toggle.sh` |
| 状态文件 | `~/.claude/voice-enabled` |

## 相关技能

| 技能 | 协同方式 |
|------|---------|
| **turix-desktop-agent** | 桌面自动化 + 语音输入 = 免手操作闭环 |
| **claude-to-im** | IM平台 + 语音控制 = 移动端语音交互 |
| **openai-whisper** | ASR转文字（IM语音消息处理） |
