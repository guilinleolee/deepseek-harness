# macOS 装机全流程 · 实操清单

> **主机要求**:macOS 14+ (arm64 或 x86_64 universal binary)
> **来源**:[Anionex/dsh-computer-use README § Quick start](https://github.com/Anionex/dsh-computer-use#quick-start)

## 1. 系统准备

### 1.1 操作系统

```sh
sw_vers                              # 应输出 macOS 14.x 或更高
uname -m                             # 应输出 arm64(Apple Silicon)或 x86_64(Intel)
```

### 1.2 Node.js(本地构建才需要,生产用不到)

```sh
node --version                       # 应 >= 22.19.0 或 >= 24.0.0
```

如果版本不对:
```sh
brew install node@24                 # 或 nvm install 24
```

### 1.3 DeepSeek Harness

```sh
dsh --version                        # 确认 DSH 已装
dsh --profile web --dump-config      # 看 Web Profile 当前配置
dsh --profile headless --dump-config # 看 Headless Profile 当前配置
```

## 2. macOS TCC 权限(必须)

### 2.1 Accessibility(必需)

System Settings → Privacy & Security → Accessibility:
- 找到 DSH host(或 `dsh-web` / `Electron` / `node`),开启 toggle

### 2.2 Screen Recording(仅截图需要)

System Settings → Privacy & Security → Screen Recording:
- 同上,找到 DSH host,开启 toggle

### 2.3 Input Monitoring(部分 macOS 版本需要)

System Settings → Privacy & Security → Input Monitoring:
- 同上,部分 macOS 上 pointer 输入需要

### 2.4 Bundle 自助跳转

Web Settings → Computer Use 面板里有按钮一键跳转对应隐私面板(点击后用户必须手动 Allow)。

## 3. 装 Bundle

### 3.1 装到 Web Profile

```sh
dsh plugin --profile web add @anionex/dsh-computer-use
```

### 3.2 装到 Headless Profile

```sh
dsh plugin --profile headless add @anionex/dsh-computer-use
```

### 3.3 验证挂载

```sh
dsh --profile web --dump-config | grep computer-use
dsh --profile headless --dump-config | grep computer-use
```

预期输出:
```yaml
computer-use:
  package: '@anionex/dsh-computer-use'
  ...
```

### 3.4 ❌ 禁用旧包名

```sh
# 这个包名从未发布到 npm,会失败
dsh plugin --profile web add @dsh-external/dsh-computer-use
# Error: 404 Not Found
```

如果 profile / manifest / 旧文档里引用 `@dsh-external/dsh-computer-use`,**必须先替换为 `@anionex/dsh-computer-use`** 再装。

## 4. 重启 host + 新 Session

```sh
# 1. 停掉当前 dsh web 进程
pkill -f "dsh web"  # 或 Ctrl+C

# 2. 重启
dsh web &

# 3. 新开一个 Session(host 重载 Bundle + Skill catalog)
# GUI: 点击 New Session
# CLI: 重连
```

## 5. 加载 Skill

在新 Session 内:
```text
/computer-use
```

加载后 Bundle 默认只暴露的 `computer_use_activate` 不变,完整 12 Tools(`computer_click` / `computer_observe` / `computer_set_value` / `computer_type_text` / `computer_press_key` / `computer_scroll` / `computer_drag` / `computer_perform_action` / `computer_wait` / `computer_confirm` / `computer_list_apps`)才出现。

## 6. 第一次端到端验证

Skill 加载后尝试:
```text
Use Computer Use to inspect the running DSH Computer Use Fixture,
enable its deterministic option, and report the fresh status.
Prefer Accessibility elements and do not reuse an old observation.
```

预期:`computer_list_apps` 列出 DSH Computer Use Fixture(bundle id 在 grants 或经用户首次审批) → `computer_observe` 拿到观测 → `computer_click` 点 "Deterministic" 开关 → `computer_wait` 等新观测。

## 7. 卸载

```sh
dsh plugin --profile web remove @anionex/dsh-computer-use
dsh plugin --profile headless remove @anionex/dsh-computer-use
```

卸载会注销 Skill + 取消 helper 工作 + 释放 observations + 关闭 grants + 关闭 confirmations。**截图文件 + `computer_use_state` sidecar 保留**(用户自行清理)。

## Windows / Linux 用户

```sh
# 装 Bundle 是允许的,只是 Tools 不注册
dsh plugin --profile web add @anionex/dsh-computer-use
dsh --profile web --dump-config | grep computer-use

# Web Settings 会报告:
# COMPUTER_UNSUPPORTED_PLATFORM
```

可以装,但功能不可用。**等迁移到 macOS 14+ 主机再使用**。

## 相关链接

- [[../../SKILL.md]] · 主 SKILL.md(L1 节)
- [[error-codes.md]] · 4 类错误码映射
- [上游 Quick start](https://github.com/Anionex/dsh-computer-use#quick-start)
- [上游 Removal](https://github.com/Anionex/dsh-computer-use#removal)