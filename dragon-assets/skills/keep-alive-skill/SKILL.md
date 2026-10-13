---
license: UNKNOWN
triggers: ["keep alive skill", "Keep Alive SKILL"]
---
# Keep Alive SKILL

> 网页常亮与连接保持 —— 防止网页超时断开，保持浏览器标签页活跃

## L0: 一句话描述 (≤15字)
网页常亮不掉线自动保持

## L1: 使用场景 (50-100字)
当用户需要长时间保持网页活跃（如监控直播、保持会话、等待回调、持续抓取数据），或需要防止浏览器标签页因超时自动关闭时触发。支持本地浏览器常亮和远程浏览器连接保持。

## L2: 详细文档

### 核心能力

| 能力 | 说明 | 优先级 |
|------|------|--------|
| Tab常亮 | 防止标签页因超时/省电策略关闭 | P0 |
| 会话保持 | 维持登录状态不超时 | P0 |
| 自动刷新 | 定时刷新页面保持活跃 | P1 |
| 直播监控 | 持续监控直播/通知页面 | P1 |
| 断线重连 | 检测断连自动恢复 | P2 |

### 方案一：浏览器扩展（Chrome扩展）

**manifest.json**:
```json
{
  "manifest_version": 3,
  "name": "Keep Alive Tab",
  "version": "1.0",
  "permissions": ["activeTab", "storage", "tabs"],
  "background": {
    "service_worker": "background.js"
  },
  "action": {
    "default_popup": "popup.html",
    "default_icon": "icon.png"
  }
}
```

**background.js** - 常亮后台脚本:
```javascript
// 常亮核心: 定时发送心跳防止标签页休眠
const HEARTBEAT_INTERVAL = 30000; // 30秒心跳
const MAX_IDLE_TIME = 60000;        // 60秒无响应后强制唤醒

let heartbeatTimer = null;
let activeTabId = null;

function startHeartbeat(tabId) {
  activeTabId = tabId;
  stopHeartbeat();

  heartbeatTimer = setInterval(async () => {
    try {
      // 获取当前标签页信息
      const tab = await chrome.tabs.get(tabId);

      // 如果标签页被回收，强制刷新
      if (!tab.active || tab.discarded) {
        console.log('[KeepAlive] Tab discarded, reloading...');
        await chrome.tabs.reload(tabId);
      }

      // 发送心跳消息到content script
      try {
        await chrome.tabs.sendMessage(tabId, { type: 'heartbeat' });
      } catch (e) {
        // 内容脚本未加载，注入脚本
        await chrome.scripting.executeScript({
          target: { tabId: tabId },
          func: () => { window.dispatchEvent(new Event('keepalive-heartbeat')); }
        });
      }

      console.log(`[KeepAlive] Heartbeat sent to tab ${tabId} at ${new Date().toLocaleTimeString()}`);
    } catch (err) {
      console.error('[KeepAlive] Heartbeat error:', err.message);
      // 标签页已关闭，停止心跳
      stopHeartbeat();
    }
  }, HEARTBEAT_INTERVAL);

  console.log(`[KeepAlive] Started for tab ${tabId}`);
}

function stopHeartbeat() {
  if (heartbeatTimer) {
    clearInterval(heartbeatTimer);
    heartbeatTimer = null;
    console.log('[KeepAlive] Stopped');
  }
}

// 监听来自popup的消息
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === 'start' && msg.tabId) {
    startHeartbeat(msg.tabId);
    sendResponse({ status: 'started' });
  } else if (msg.action === 'stop') {
    stopHeartbeat();
    sendResponse({ status: 'stopped' });
  } else if (msg.action === 'status') {
    sendResponse({ active: heartbeatTimer !== null, tabId: activeTabId });
  }
});

// 监听标签页关闭
chrome.tabs.onRemoved.addListener((tabId) => {
  if (tabId === activeTabId) {
    stopHeartbeat();
    activeTabId = null;
  }
});

// 监听浏览器启动，自动恢复常亮标签页
chrome.runtime.onStartup.addListener(async () => {
  const stored = await chrome.storage.local.get(['lastTabId', 'autoResume']);
  if (stored.autoResume && stored.lastTabId) {
    try {
      await chrome.tabs.get(stored.lastTabId);
      startHeartbeat(stored.lastTabId);
    } catch (e) {
      // 标签页已不存在
    }
  }
});
```

**popup.html** - 简单UI:
```html
<!DOCTYPE html>
<html>
<head><style>
  body { width: 200px; padding: 10px; font-family: sans-serif; }
  .status { font-size: 12px; color: #666; margin-bottom: 10px; }
  .active { color: green; font-weight: bold; }
  .inactive { color: red; }
  button { width: 100%; padding: 8px; margin: 4px 0; cursor: pointer; }
  input[type="number"] { width: 60px; }
</style></head>
<body>
  <div class="status" id="status">状态: 未激活</div>
  <div>
    <label>心跳间隔(秒): <input type="number" id="interval" value="30" min="5" max="300"></label>
  </div>
  <button id="startBtn">▶ 启动常亮</button>
  <button id="stopBtn">■ 停止常亮</button>
  <label><input type="checkbox" id="autoResume"> 浏览器启动时自动恢复</label>
</body>
</html>
```

**popup.js**:
```javascript
document.getElementById('startBtn').onclick = async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (tab) {
    chrome.runtime.sendMessage({ action: 'start', tabId: tab.id });
    document.getElementById('status').textContent = '状态: 激活中';
    document.getElementById('status').className = 'status active';
  }
};

document.getElementById('stopBtn').onclick = () => {
  chrome.runtime.sendMessage({ action: 'stop' });
  document.getElementById('status').textContent = '状态: 已停止';
  document.getElementById('status').className = 'status inactive';
};

document.getElementById('autoResume').onchange = (e) => {
  chrome.storage.local.set({ autoResume: e.target.checked });
};

// 初始化状态
chrome.runtime.sendMessage({ action: 'status' }, (resp) => {
  if (resp && resp.active) {
    document.getElementById('status').textContent = `状态: 激活 (Tab ${resp.tabId})`;
    document.getElementById('status').className = 'status active';
  }
});
```

### 方案二：Python脚本（无浏览器扩展场景）

**keep_alive.py** - 本地HTTP服务+自动刷新:
```python
#!/usr/bin/env python3
"""Keep Alive - HTTP服务 + 页面定时刷新"""
import http.server
import socketserver
import threading
import time
import sys
import os
import re
import argparse
from urllib.parse import urlparse

PORT = 8765
REFRESH_INTERVAL = 30  # 秒
KEEPALIVE_HTML = '''
<!DOCTYPE html>
<html>
<head>
  <title>Keep Alive Monitor</title>
  <meta http-equiv="refresh" content="{interval}">
  <style>
    body {{ font-family: monospace; background: #1a1a2e; color: #eee; padding: 20px; }}
    .info {{ background: #16213e; padding: 15px; border-radius: 8px; margin: 10px 0; }}
    .online {{ color: #00ff88; }}
    .time {{ color: #888; font-size: 12px; }}
    a {{ color: #4fc3f7; }}
  </style>
</head>
<body>
  <h2>🌐 Keep Alive Monitor</h2>
  <div class="info">
    <div>状态: <span class="online">● 在线</span></div>
    <div>启动时间: {start_time}</div>
    <div>运行时长: <span id="duration">{duration}</span></div>
    <div>刷新间隔: {interval} 秒</div>
    <div>刷新次数: {refresh_count}</div>
  </div>
  <div class="info">
    <h3>📋 监控页面</h3>
    {target_pages}
  </div>
  <div class="time" id="now">{now}</div>
  <script>
    let start = Date.now();
    let count = {refresh_count};
    setInterval(() => {{
      document.getElementById('duration').textContent =
        Math.floor((Date.now() - start) / 1000) + ' 秒';
      document.getElementById('now').textContent = new Date().toLocaleString();
    }}, 1000);
  </script>
</body>
</html>
'''

class KeepAliveHandler(http.server.SimpleHTTPRequestHandler):
    refresh_count = 0
    start_time = time.strftime("%Y-%m-%d %H:%M:%S")

    def do_GET(self):
        if self.path == '/' or self.path == '/status':
            interval = int(REFRESH_INTERVAL)
            # 获取运行时长
            start_ts = time.mktime(time.strptime(self.start_time, "%Y-%m-%d %H:%M:%S"))
            duration = int(time.time() - start_ts)
            html = KEEPALIVE_HTML.format(
                interval=interval,
                start_time=self.start_time,
                duration=f"{duration} 秒",
                refresh_count=self.refresh_count,
                target_pages="<p>当前无监控目标</p>",
                now=time.strftime("%Y-%m-%d %H:%M:%S")
            )
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        else:
            super().do_GET()

    def log_message(self, format, *args):
        # 减少日志噪音
        if 'keepalive' not in args[0].lower():
            print(f"[KeepAlive] {args[0]}")

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

def keep_alive_monitor(urls: list, interval: int = REFRESH_INTERVAL):
    """后台线程：定期刷新指定URL(通过HEAD请求保持连接)"""
    import requests
    while True:
        for url in urls:
            try:
                resp = requests.head(url, timeout=10, allow_redirects=True)
                print(f"[KeepAlive] {url} -> {resp.status_code}")
            except Exception as e:
                print(f"[KeepAlive] {url} -> Error: {e}")
        time.sleep(interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Keep Alive HTTP Server')
    parser.add_argument('--port', type=int, default=PORT, help='HTTP服务器端口')
    parser.add_argument('--interval', type=int, default=REFRESH_INTERVAL, help='刷新间隔(秒)')
    parser.add_argument('--urls', nargs='*', default=[], help='需要保持活跃的URL列表')
    args = parser.parse_args()

    # 启动URL监控线程
    if args.urls:
        t = threading.Thread(target=keep_alive_monitor, args=(args.urls, args.interval), daemon=True)
        t.start()
        print(f"[KeepAlive] 监控线程已启动: {args.urls}")

    # 启动HTTP服务
    print(f"[KeepAlive] HTTP服务启动: http://localhost:{args.port}")
    print(f"[KeepAlive] 刷新间隔: {args.interval}秒")
    print(f"[KeepAlive] 监控面板: http://localhost:{args.port}/status")
    print(f"[KeepAlive] 保持浏览器打开此页面以激活常亮")

    server = ThreadedHTTPServer(("localhost", args.port), KeepAliveHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[KeepAlive] 服务器已停止")
        server.shutdown()
```

### 方案三：浏览器控制台脚本（临时使用）

**console_keepalive.js** - 粘贴到浏览器控制台:
```javascript
// 粘贴到浏览器F12 -> Console执行
(function keepAlive() {
  const interval = 30000; // 30秒心跳
  let count = 0;

  // 发送心跳请求(可自定义)
  const heartbeat = () => {
    count++;
    console.log(`[KeepAlive] 心跳 #${count} @ ${new Date().toLocaleTimeString()}`);

    // 方案1: 发送无意义请求保持连接
    // fetch(location.href, {mode: 'no-cors'});

    // 方案2: 模拟用户活跃(防省电)
    const evt = new Event('mousemove');
    document.dispatchEvent(evt);
  };

  setInterval(heartbeat, interval);
  console.log('[KeepAlive] 已激活，每30秒发送心跳');
  console.log('[KeepAlive] 关闭控制台或刷新页面以停止');
})();
```

### 天龙引擎集成

| 天龙岗位 | 集成方式 |
|----------|-----------|
| 17-04桌面自动化 | 配合Turix-CUA保持浏览器活跃 |
| 01调研师 | 长时间监控任务保持连接 |
| 35-02社媒运营 | 直播/通知页面常亮监控 |
| 09-02编排 | 编排长时间运行任务的连接保持 |

### 使用命令

```bash
# 启动常亮HTTP服务
python3 ~/.claude/skills/keep-alive-skill/scripts/keep_alive.py --port 8765 --interval 30

# 监控指定URL
python3 ~/.claude/skills/keep-alive-skill/scripts/keep_alive.py \
  --urls "https://example.com" "https://stream.example.com" \
  --interval 15

# 安装Chrome扩展后点击扩展图标启动常亮
```

### 适用场景

| 场景 | 推荐方案 |
|------|---------|
| 临时使用 | 浏览器控制台脚本 |
| 长时间监控 | Python HTTP服务 |
| 浏览器标签页常亮 | Chrome扩展 |
| 批量URL保持连接 | Python多线程监控 |

### 限制与注意事项

1. **浏览器省电策略**: 某些浏览器/系统会强制关闭后台标签页
2. **服务器限制**: 部分网站有请求频率限制，频繁刷新可能触发封禁
3. **资源占用**: 长时间运行的HTTP服务会持续占用系统资源
4. **隐私安全**: 心跳请求可能暴露浏览行为

## 文件结构

```
keep-alive-skill/
├── SKILL.md                    # 本文件
├── extension/
│   ├── manifest.json           # Chrome扩展配置
│   ├── background.js           # 后台服务脚本
│   ├── popup.html             # 弹窗UI
│   ├── popup.js               # 弹窗逻辑
│   └── icon.png               # 扩展图标
├── scripts/
│   └── keep_alive.py          # Python脚本
└── README.md                   # 使用说明
```

## 版本信息

- **版本**: 1.0.0
- **更新日期**: 2026-05-07
- **来源**: ChromeAppHeroes Keep Alive Tab 理念 + 独立开发
- **_stars**: N/A