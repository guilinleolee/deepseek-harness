---
license: MIT
name: mano-cua
description: 桌面 GUI 自动化技能，通过自然语言描述驱动 VLA 模型执行视觉界面操作（点击、输入、滚动、拖拽等）。支持本地离线模式和云端模式。当用户需要自动操作桌面应用、浏览器、或执行需要视觉交互的任务时使用。触发词：CUA / GUI自动化 / 桌面操作 / 自动点击 / 自动化任务 / computer use agent / GUI automation
triggers: ["mano", "mano-cua", "CUA", "GUI automation", "桌面自动化", "GUI自动化", "computer use", "视觉自动化", "自动操作电脑"]
---

# mano-cua

桌面 GUI 自动化技能，通过自然语言描述驱动 VLA 模型执行视觉界面操作。

## 功能概述

- **自然语言驱动**：用日常语言描述任务，系统自动执行 GUI 操作
- **灵活推理模式**：
  - **本地模式**：模型本地运行，数据不离开设备，响应快速
  - **云端模式**：使用云端 API 服务（`mano.mininglamp.com`）
- **全面交互支持**：点击、输入、快捷键、滚动、拖拽、鼠标移动、截图、等待、应用启动、URL 导航
- **跨平台支持**：macOS（稳定）、Windows、Linux（Beta）

## 前置要求

- **图形桌面系统**：macOS / Windows / Linux
- **安装 mano-cua 二进制文件**（v1.1.0+ 推荐）

### 安装方法

**macOS / Linux (Homebrew)：**

```bash
brew install Mininglamp-AI/tap/mano-cua

# 更新到最新版本
brew upgrade Mininglamp-AI/tap/mano-cua
```

**Windows：**

从 [GitHub Releases](https://github.com/Mininglamp-AI/mano-skill/releases) 下载最新的 `mano-cua-windows.zip`，解压后将文件夹添加到 `PATH`。

## 使用方法

```bash
# 运行任务
mano-cua run "你的任务描述"

# 带选项运行（最小化UI面板，设置最大步数）
mano-cua run "任务" --minimize --max-steps 10

# 在浏览器中打开URL后再开始任务
mano-cua run "任务" --url "https://example.com"

# 先启动应用再开始任务
mano-cua run "任务" --app "Notes"

# 本地模式运行（设备端推理，仅限 macOS Apple Silicon）
mano-cua run "任务" --local

# 停止当前运行的任务
mano-cua stop
```

运行 `mano-cua --help` 或 `mano-cua <命令> --help` 查看完整参数选项。

> **注意**：每个设备同时只能运行一个任务。如需启动新任务，先用 `mano-cua stop` 停止当前任务。

## 配置

```bash
mano-cua config --list                        # 显示所有设置
mano-cua config --set max-steps 50            # 设置默认最大步数
mano-cua config --set minimize true           # 始终以最小化UI面板启动
mano-cua config --set disable-bash true       # 在云端模式禁用shell工具
```

## 本地模式

通过 MLX 在设备上完全离线运行 [Mano-P](https://huggingface.co/Mininglamp-2718/Mano-P) 模型。数据不离开机器。**需要 macOS Apple Silicon (M1+)**。

**首次设置：**

```bash
mano-cua check
mano-cua install-sdk
mano-cua install-model
```

**运行：**

```bash
mano-cua run "在Google搜索openai并打开第一个结果" --local --url "https://www.google.com"
mano-cua run "在小红书搜索iphone并打开第一篇帖子" --local --url "https://www.xiaohongshu.com" --minimize --max-steps 15
mano-cua run "创建一个标题为hello world的新备忘录" --local --app "Notes"
```

## 典型使用场景

```bash
# 浏览器自动化
mano-cua run "打开Chrome，搜索AI新闻，展示第一条结果" --minimize --max-steps 20

# 应用操作
mano-cua run "打开微信，找到FTY的聊天窗口，告诉他会议推迟到明天"

# 桌面任务
mano-cua run "在桌面创建一个report.txt文件，内容是'Q2营收汇总'，然后在Finder中给它打上红色标签"

# 本地模式（隐私优先）
mano-cua run "搜索openai并打开第一个结果" --local --url "https://www.google.com" --minimize
```

## 工作原理

每一步都会截取当前屏幕截图，结合任务描述发送给视觉模型分析。模型决定下一步操作后，本地客户端执行相应动作（点击、输入、滚动等）。

混合视觉模型：
- **Mano-P 模型**：处理简单直接的轻量级任务，响应快速
- **Claude（视觉分析）**：处理需要深度推理的复杂任务

系统会根据任务复杂度自动选择合适的模型。

**本地模式（`--local`）**下，Mano-P 模型通过 MLX 在本地运行，推理过程无网络请求。

## 支持的操作

- click（点击）
- type（输入文字）
- hotkey（快捷键）
- scroll（滚动）
- drag（拖拽）
- mouse move（鼠标移动）
- screenshot（截图）
- wait（等待）
- app launch（启动应用）

## 状态面板

任务运行时，屏幕右上角会显示一个小型的状态面板，用于：
- 显示实时任务状态和进度
- 提供任务管理功能（暂停/停止）
- 提醒用户正在运行自动化任务，避免意外干扰

## 权限要求

需要以下权限：
- **屏幕录制权限**
- **辅助功能权限**（键盘/鼠标控制）

在 **系统偏好设置 → 隐私与安全性** 中授予这些权限。

## 安全与隐私

- 用户必须在任务开始前明确描述任务内容。没有后台操作，没有定时扫描，没有持久连接。
- 敏感或不可逆操作（购买、输入凭据、删除数据）会触发确认提示，智能体暂停等待用户明确批准后再执行。
- 步数通过 `--max-steps` 限制，防止过度执行。
- 屏幕上的状态面板实时显示每个操作，用户可通过面板或 `mano-cua stop` 立即停止。
- 智能体在用户介入鼠标/键盘输入或会话结束时立即停止。
- 大多数操作本质上是可逆的（点击、滚动、输入可以撤销）。对于不可逆操作，应用上述确认机制。
- 云端模式下，仅在活跃的用户启动会话期间发送主显示器截图用于当前推理步骤的瞬态分析；不进行持续录制或后台监控。
- 对于隐私敏感任务，**本地模式（`--local`）** 完全在设备上运行推理，零网络调用。
- 智能体无法访问应用程序数据、API 或内部状态，只能看到屏幕上显示的内容并通过标准鼠标/键盘输入进行交互。

## 重要提示

- **任务运行期间不要使用鼠标或键盘。** 手动输入可能导致意外行为。
- **多显示器**：仅使用主显示器。所有鼠标移动、点击和截图都限制在该显示器内。

## 平台支持

- **macOS**：首选平台，测试最充分，稳定可用
- **Windows**：已完成适配，云端模式完全支持 GUI 自动化
- **Linux**：功能可用但测试较少，可能有小问题

## 项目信息

- **GitHub**：https://github.com/Mininglamp-AI/mano-skill
- **许可证**：MIT-0
