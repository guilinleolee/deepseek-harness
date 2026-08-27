#!/usr/bin/env node
/**
 * Auth Capture - Chrome CDP认证捕获工具
 *
 * 通过Chrome DevTools Protocol自动捕获AI平台认证信息
 *
 * @version 1.0.0
 */

const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');
const os = require('os');

// 配置
const CDP_PORT = process.env.CDP_PORT || 9222;
const CDP_HOST = process.env.CDP_HOST || 'localhost';
const CONFIG_DIR = process.env.ZERO_TOKEN_CONFIG_DIR ||
  path.join(os.homedir(), '.openclaw-zero-state');

// 平台认证配置
const PLATFORM_AUTH_CONFIG = {
  deepseek: {
    name: 'DeepSeek',
    url: 'https://chat.deepseek.com/',
    authType: 'token+cookie',
    tokenPattern: /"accessToken":"([^"]+)"/,
    tokenUrl: 'https://chat.deepseek.com/api/auth/session',
    cookieDomains: ['.deepseek.com'],
    requiredCookies: ['__Secure-next-auth.session-token'],
    storageKeys: ['token', 'accessToken']
  },
  claude: {
    name: 'Claude Web',
    url: 'https://claude.ai/',
    authType: 'sessionKey+cookie',
    tokenPattern: /"sessionKey":"([^"]+)"/,
    storageKeys: ['sessionKey', 'claude-session-key'],
    cookieDomains: ['.claude.ai'],
    requiredCookies: ['sessionKey']
  },
  chatgpt: {
    name: 'ChatGPT Web',
    url: 'https://chatgpt.com/',
    authType: 'accessToken+cookie',
    tokenPattern: /"accessToken":"([^"]+)"/,
    tokenUrl: 'https://chatgpt.com/api/auth/session',
    storageKeys: ['accessToken', '__Secure-next-auth.session-token'],
    cookieDomains: ['.chatgpt.com', '.openai.com']
  },
  gemini: {
    name: 'Gemini Web',
    url: 'https://gemini.google.com/',
    authType: 'cookie',
    cookieDomains: ['.google.com'],
    requiredCookies: ['__Secure-1PSID', '__Secure-1PSIDTS', '__Secure-1PSIDCC']
  },
  qwen: {
    name: 'Qwen International',
    url: 'https://tongyi.aliyun.com/',
    authType: 'token',
    tokenPattern: /"token":"([^"]+)"/,
    storageKeys: ['token', 'X-XSRF-TOKEN'],
    cookieDomains: ['.aliyun.com']
  },
  qwen_cn: {
    name: 'Qwen China',
    url: 'https://qianwen.aliyun.com/',
    authType: 'token',
    tokenPattern: /"token":"([^"]+)"/,
    storageKeys: ['token'],
    cookieDomains: ['.aliyun.com']
  },
  kimi: {
    name: 'Kimi',
    url: 'https://kimi.moonshot.cn/',
    authType: 'token',
    tokenPattern: /"token":"([^"]+)"/,
    storageKeys: ['token', 'accessToken'],
    cookieDomains: ['.moonshot.cn']
  },
  doubao: {
    name: 'Doubao',
    url: 'https://www.doubao.com/',
    authType: 'token',
    tokenPattern: /"token":"([^"]+)"/,
    storageKeys: ['token', 'csrf_token'],
    cookieDomains: ['.doubao.com']
  },
  grok: {
    name: 'Grok Web',
    url: 'https://grok.x.ai/',
    authType: 'cookie',
    cookieDomains: ['.x.ai'],
    requiredCookies: ['sessionid', 'csrftoken']
  },
  glm: {
    name: 'GLM Web',
    url: 'https://chatglm.cn/',
    authType: 'token',
    tokenPattern: /"token":"([^"]+)"/,
    storageKeys: ['token', 'accessToken'],
    cookieDomains: ['.chatglm.cn']
  }
};

/**
 * CDP客户端
 */
class CDPClient {
  constructor(host = CDP_HOST, port = CDP_PORT) {
    this.host = host;
    this.port = port;
    this.ws = null;
    this.messageId = 0;
    this.pendingMessages = new Map();
  }

  /**
   * 获取Chrome调试信息
   */
  async getDebugInfo() {
    return new Promise((resolve, reject) => {
      http.get(`http://${this.host}:${this.port}/json/version`, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            resolve(JSON.parse(data));
          } catch (e) {
            reject(new Error('Failed to parse debug info'));
          }
        });
      }).on('error', reject);
    });
  }

  /**
   * 获取所有页面
   */
  async getPages() {
    return new Promise((resolve, reject) => {
      http.get(`http://${this.host}:${this.port}/json/list`, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            resolve(JSON.parse(data));
          } catch (e) {
            reject(new Error('Failed to parse pages'));
          }
        });
      }).on('error', reject);
    });
  }

  /**
   * 查找目标平台页面
   */
  async findPlatformPage(platformConfig) {
    const pages = await this.getPages();
    const targetUrl = platformConfig.url;

    return pages.find(page => page.url && page.url.startsWith(targetUrl));
  }

  /**
   * 通过WebSocket发送CDP命令
   */
  async sendCommand(ws, method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = ++this.messageId;
      const message = JSON.stringify({ id, method, params });

      const timeout = setTimeout(() => {
        this.pendingMessages.delete(id);
        reject(new Error(`Command timeout: ${method}`));
      }, 30000);

      this.pendingMessages.set(id, { resolve, reject, timeout });
      ws.send(message);
    });
  }

  /**
   * 获取页面Cookies
   */
  async getCookies(ws) {
    const result = await this.sendCommand(ws, 'Network.getAllCookies');
    return result.cookies || [];
  }

  /**
   * 获取LocalStorage
   */
  async getLocalStorage(ws, origin) {
    const result = await this.sendCommand(ws, 'DOMStorage.getDOMStorageItems', {
      storageId: {
        securityOrigin: origin,
        isLocalStorage: true
      }
    });
    return result.entries || [];
  }

  /**
   * 执行脚本获取认证信息
   */
  async executeScript(ws, script) {
    const result = await this.sendCommand(ws, 'Runtime.evaluate', {
      expression: script,
      returnByValue: true
    });
    return result.result?.value;
  }
}

/**
 * 认证捕获器
 */
class AuthCapture {
  constructor() {
    this.cdpClient = new CDPClient();
    this.ensureConfigDir();
  }

  /**
   * 确保配置目录存在
   */
  ensureConfigDir() {
    if (!fs.existsSync(CONFIG_DIR)) {
      fs.mkdirSync(CONFIG_DIR, { recursive: true });
    }
  }

  /**
   * 检查Chrome CDP连接
   */
  async checkConnection() {
    try {
      const info = await this.cdpClient.getDebugInfo();
      console.log('✅ Chrome CDP Connected');
      console.log(`   Browser: ${info.Browser}`);
      console.log(`   WebSocket: ${info.webSocketDebuggerUrl}`);
      return true;
    } catch (error) {
      console.error('❌ Chrome CDP not available');
      console.error('   Please start Chrome with --remote-debugging-port=9222');
      console.error('');
      console.error('   Example:');
      console.error('   Windows: chrome.exe --remote-debugging-port=9222 --user-data-dir=%USERPROFILE%\\.chrome-debug');
      console.error('   macOS/Linux: google-chrome --remote-debugging-port=9222 --user-data-dir=~/.chrome-debug');
      return false;
    }
  }

  /**
   * 捕获平台认证
   */
  async capturePlatform(platform) {
    const config = PLATFORM_AUTH_CONFIG[platform];
    if (!config) {
      throw new Error(`Unknown platform: ${platform}`);
    }

    console.log(`\n🔍 Capturing ${config.name}...`);

    // 查找平台页面
    const page = await this.cdpClient.findPlatformPage(config);
    if (!page) {
      console.log(`❌ No open tab found for ${config.name}`);
      console.log(`   Please open ${config.url} in Chrome and login first`);
      return null;
    }

    console.log(`✅ Found tab: ${page.url}`);

    // 连接到页面的WebSocket
    const WebSocket = require('ws');
    const ws = new WebSocket(page.webSocketDebuggerUrl);

    // 设置消息处理器
    ws.on('message', (data) => {
      try {
        const response = JSON.parse(data.toString());
        const pending = this.cdpClient.pendingMessages.get(response.id);
        if (pending) {
          clearTimeout(pending.timeout);
          this.cdpClient.pendingMessages.delete(response.id);
          if (response.error) {
            pending.reject(new Error(response.error.message || 'CDP error'));
          } else {
            pending.resolve(response.result);
          }
        }
      } catch (e) {
        // Ignore parse errors
      }
    });

    return new Promise((resolve, reject) => {
      ws.on('open', async () => {
        try {
          // 启用必要的域
          await this.cdpClient.sendCommand(ws, 'Network.enable');
          await this.cdpClient.sendCommand(ws, 'Runtime.enable');

          const auth = {
            platform,
            name: config.name,
            capturedAt: new Date().toISOString(),
            expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
          };

          // 获取Cookies
          const cookies = await this.cdpClient.getCookies(ws);
          const relevantCookies = cookies.filter(c =>
            config.cookieDomains?.some(d => c.domain.endsWith(d))
          );

          if (relevantCookies.length > 0) {
            auth.cookies = relevantCookies.map(c => ({
              name: c.name,
              value: c.value,
              domain: c.domain,
              path: c.path,
              secure: c.secure,
              httpOnly: c.httpOnly
            }));
            console.log(`   📦 Cookies: ${relevantCookies.length}`);
          }

          // 获取LocalStorage
          try {
            const url = new URL(page.url);
            const storage = await this.cdpClient.getLocalStorage(ws, url.origin);

            if (storage.length > 0) {
              auth.localStorage = {};
              for (const [key, value] of storage) {
                if (config.storageKeys?.includes(key) || key.includes('token') || key.includes('Token')) {
                  auth.localStorage[key] = value;
                }
              }
              console.log(`   📦 LocalStorage: ${Object.keys(auth.localStorage).length} tokens`);
            }
          } catch (e) {
            // LocalStorage may not be available
          }

          // 执行脚本获取token
          if (config.tokenPattern || config.tokenUrl) {
            try {
              // 尝试从页面获取token
              const tokenScript = config.tokenPattern
                ? `
                  (function() {
                    const patterns = ${JSON.stringify([config.tokenPattern.source])};
                    const html = document.documentElement.outerHTML;
                    for (const pattern of patterns) {
                      const match = html.match(new RegExp(pattern));
                      if (match && match[1]) return match[1];
                    }
                    // 检查localStorage
                    for (let i = 0; i < localStorage.length; i++) {
                      const key = localStorage.key(i);
                      const value = localStorage.getItem(key);
                      for (const pattern of patterns) {
                        if (value && value.match(new RegExp(pattern))) {
                          const m = value.match(new RegExp(pattern));
                          if (m && m[1]) return m[1];
                        }
                      }
                    }
                    return null;
                  })()
                `
                : `localStorage.getItem('token') || localStorage.getItem('accessToken')`;

              const token = await this.cdpClient.executeScript(ws, tokenScript);
              if (token) {
                auth.token = token;
                console.log(`   🔑 Token: ${token.substring(0, 20)}...`);
              }
            } catch (e) {
              console.log(`   ⚠️  Token extraction failed: ${e.message}`);
            }
          }

          ws.close();

          // 保存认证信息
          this.saveAuth(platform, auth);

          console.log(`✅ ${config.name} captured successfully`);
          resolve(auth);

        } catch (error) {
          ws.close();
          reject(error);
        }
      });

      ws.on('error', reject);
    });
  }

  /**
   * 保存认证信息
   */
  saveAuth(platform, auth) {
    const authFile = path.join(CONFIG_DIR, `${platform}-auth.json`);
    fs.writeFileSync(authFile, JSON.stringify(auth, null, 2));
    console.log(`   💾 Saved to: ${authFile}`);
  }

  /**
   * 加载认证信息
   */
  loadAuth(platform) {
    const authFile = path.join(CONFIG_DIR, `${platform}-auth.json`);
    if (fs.existsSync(authFile)) {
      const content = fs.readFileSync(authFile, 'utf-8');
      const auth = JSON.parse(content);

      // 检查是否过期
      if (auth.expiresAt && new Date(auth.expiresAt) < new Date()) {
        console.log(`⚠️  ${platform} auth expired`);
        return null;
      }

      return auth;
    }
    return null;
  }

  /**
   * 列出所有已保存的认证
   */
  listAuth() {
    const files = fs.readdirSync(CONFIG_DIR).filter(f => f.endsWith('-auth.json'));
    const result = [];

    for (const file of files) {
      const platform = file.replace('-auth.json', '');
      const auth = this.loadAuth(platform);
      if (auth) {
        result.push({
          platform,
          name: auth.name,
          capturedAt: auth.capturedAt,
          expiresAt: auth.expiresAt,
          hasToken: !!auth.token,
          hasCookies: !!(auth.cookies && auth.cookies.length > 0)
        });
      }
    }

    return result;
  }

  /**
   * 批量捕获多个平台
   */
  async captureMultiple(platforms) {
    const results = {};
    for (const platform of platforms) {
      try {
        results[platform] = await this.capturePlatform(platform);
      } catch (error) {
        console.error(`❌ Failed to capture ${platform}: ${error.message}`);
        results[platform] = null;
      }
    }
    return results;
  }
}

/**
 * 命令行入口
 */
async function main() {
  const args = process.argv.slice(2);
  const capture = new AuthCapture();

  // 解析参数
  const flags = {
    platform: null,
    list: false,
    check: false,
    all: false
  };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--platform' || args[i] === '-p') {
      flags.platform = args[++i]?.split(',');
    } else if (args[i] === '--list' || args[i] === '-l') {
      flags.list = true;
    } else if (args[i] === '--check' || args[i] === '-c') {
      flags.check = true;
    } else if (args[i] === '--all' || args[i] === '-a') {
      flags.all = true;
    }
  }

  console.log('\n🔐 Zero Token Auth Capture');
  console.log('='.repeat(50));

  // 检查连接
  if (!(await capture.checkConnection())) {
    process.exit(1);
  }

  // 执行操作
  if (flags.check) {
    // 仅检查连接
    console.log('\n✅ Chrome CDP is ready');
  } else if (flags.list) {
    // 列出已保存的认证
    const auths = capture.listAuth();
    console.log('\n📋 Saved Authentications:');
    if (auths.length === 0) {
      console.log('   No saved authentications');
    } else {
      for (const auth of auths) {
        console.log(`   ✅ ${auth.name} (${auth.platform})`);
        console.log(`      Token: ${auth.hasToken ? '✅' : '❌'}`);
        console.log(`      Cookies: ${auth.hasCookies ? '✅' : '❌'}`);
        console.log(`      Expires: ${auth.expiresAt}`);
      }
    }
  } else if (flags.all) {
    // 捕获所有平台
    const platforms = Object.keys(PLATFORM_AUTH_CONFIG);
    console.log(`\n🎯 Capturing all ${platforms.length} platforms...`);
    await capture.captureMultiple(platforms);
  } else if (flags.platform) {
    // 捕获指定平台
    await capture.captureMultiple(flags.platform);
  } else {
    // 显示帮助
    console.log('\nUsage:');
    console.log('  node auth-capture.js --platform <platforms>   Capture specific platforms');
    console.log('  node auth-capture.js --all                    Capture all platforms');
    console.log('  node auth-capture.js --list                   List saved authentications');
    console.log('  node auth-capture.js --check                  Check Chrome CDP connection');
    console.log('\nSupported Platforms:');
    for (const [id, config] of Object.entries(PLATFORM_AUTH_CONFIG)) {
      console.log(`  ${id.padEnd(10)} - ${config.name}`);
    }
  }

  console.log('\n' + '='.repeat(50));
}

// 导出
module.exports = { AuthCapture, CDPClient, PLATFORM_AUTH_CONFIG };

// 运行
if (require.main === module) {
  main().catch(console.error);
}