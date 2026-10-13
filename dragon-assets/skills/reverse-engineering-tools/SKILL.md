---
license: UNKNOWN
github_repo: CuriousLearnerDev/Online_tools
github_hash: 1ccce0d74a00b23f5744e6e39da303b4feac8d12
triggers: ["reverse engineering tools", "reverse-engineering-tools"]
---
# reverse-engineering-tools

## L0: 一句话描述 (≤15字)
逆向工程工具全家桶

## L1: 使用场景 (50-100字)
APK反编译、DEX转JAR、二进制分析、协议逆向等专业逆向工程场景。配合05安全师漏洞分析和07记录师文档归档，实现完整的逆向分析工作流。

## L2: 详细文档

### 来源项目
> [CuriousLearnerDev/Online_tools](https://github.com/CuriousLearnerDev/Online_tools) - 安全工具编排平台

### 工具分类注册表

| 分类 | 工具数量 | 代表工具 |
|------|---------|---------|
| **Android逆向** | 8+ | APKTool, JADX, JD-GUI, CFR, Procyon |
| **iOS逆向** | 5+ | Class-dump, Theos, Frida, Hopper, ldid |
| **二进制分析** | 10+ | Radare2, Ghidra, IDA Pro, Binary Ninja |
| **协议分析** | 6+ | Wireshark, tshark, mitmproxy, Burp Suite |
| **固件分析** | 4+ | binwalk, firmware-mod-kit,固件提取工具 |

### 核心命令速查

```bash
# Android逆向
apk_decompile()    # APK反编译为Smali
jadx_decompile()   # APK反编译为Java源码
dex_to_jar()      # DEX转JAR
apktool_rebuild() # 重新打包APK

# 二进制分析
radare2_analyze() # Radare2全流程分析
ghidra_import()   # Ghidra导入分析
ida_pro_scan()    # IDA Pro自动化扫描

# 协议分析
mitmproxy_capture()  # 中间人流量捕获
wireshark_filter()    # Wireshark协议过滤
burp_intruder()       # Burp暴力破解参数

# 固件分析
binwalk_extract()  # Binwalk固件提取
firmware_rebuild() # 固件重打包
```

### MCP Server配置

```json
{
  "mcpServers": {
    "reverse-engineering": {
      "command": "python3",
      "args": ["~/.claude/skills/reverse-engineering-tools/scripts/re_tools_server.py"]
    }
  }
}
```

### 与05安全师协同

| 逆向发现 | 安全分析 |
|---------|---------|
| API端点提取 | 接口漏洞扫描 |
| 加密算法识别 | 密码学审计 |
| 硬编码密钥 | 密钥泄露检测 |
| 通信协议 | 协议安全评估 |

### 与07记录师协同

逆向分析完成后自动生成报告：
- 关键发现摘要
- 代码片段归档
- 漏洞证据截图
- 修复建议文档

### 天龙岗位升级

| 岗位 | 版本 | 新增能力 |
|------|------|---------|
| **17-05安全渗透工程师** | 新增 | Android/iOS逆向+二进制分析 |
| **05安全师** | V8.84→V8.91 | 逆向辅助分析 |
