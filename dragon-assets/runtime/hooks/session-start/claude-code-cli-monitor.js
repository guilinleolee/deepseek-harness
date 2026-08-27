#!/usr/bin/env node
/**
 * Claude Code CLI 进程监控器
 *
 * 功能：
 * 1. 监控Claude Code CLI进程状态
 * 2. 检测交互阻塞（AskUserQuestion等待）
 * 3. 自动恢复中断的会话
 * 4. 结果输出捕获和通知
 *
 * 使用方式：
 * node claude-code-cli-monitor.js --session-id my-project --timeout 300000
 */

const { spawn, exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const EventEmitter = require('events');

class ClaudeCodeMonitor extends EventEmitter {
  constructor(options = {}) {
    super();

    this.sessionId = options.sessionId || `session-${Date.now()}`;
    this.projectDir = options.projectDir || process.cwd();
    this.timeout = options.timeout || 300000; // 5分钟
    this.heartbeatInterval = options.heartbeatInterval || 30000; // 30秒
    this.maxRetries = options.maxRetries || 3;
    this.permissionMode = options.permissionMode || 'acceptEdits';

    this.process = null;
    this.lastHeartbeat = Date.now();
    this.retryCount = 0;
    this.outputBuffer = [];
    this.isBlocked = false;
    this.blockedReason = null;
  }

  /**
   * 启动Claude Code CLI
   */
  async start(prompt) {
    console.log(`[Monitor] Starting Claude Code CLI with session: ${this.sessionId}`);

    const args = [
      '--session-id', this.sessionId,
      '--permission-mode', this.permissionMode
    ];

    if (prompt) {
      args.push(prompt);
    }

    // 使用PTY模式启动
    this.process = spawn('claude', args, {
      cwd: this.projectDir,
      shell: true,
      env: { ...process.env, TERM: 'xterm-256color' }
    });

    this._setupProcessHandlers();
    this._startHeartbeat();

    return new Promise((resolve, reject) => {
      this.on('complete', resolve);
      this.on('error', reject);
      this.on('blocked', (reason) => {
        console.warn(`[Monitor] Blocked: ${reason}`);
      });
    });
  }

  /**
   * 恢复中断的会话
   */
  async resume() {
    console.log(`[Monitor] Resuming session: ${this.sessionId}`);

    this.process = spawn('claude', [
      '--resume',
      '--session-id', this.sessionId
    ], {
      cwd: this.projectDir,
      shell: true,
      env: { ...process.env, TERM: 'xterm-256color' }
    });

    this._setupProcessHandlers();
    this.retryCount++;

    return new Promise((resolve, reject) => {
      this.on('complete', resolve);
      this.on('error', reject);
    });
  }

  /**
   * 设置进程事件处理器
   */
  _setupProcessHandlers() {
    // 捕获标准输出
    this.process.stdout.on('data', (data) => {
      const output = data.toString();
      this.lastHeartbeat = Date.now();
      this.outputBuffer.push(output);
      this._checkForBlocking(output);
      this.emit('output', output);
    });

    // 捕获标准错误
    this.process.stderr.on('data', (data) => {
      const error = data.toString();
      this.lastHeartbeat = Date.now();
      this.outputBuffer.push(`[ERROR] ${error}`);
      this.emit('error', error);
    });

    // 进程退出
    this.process.on('close', (code, signal) => {
      console.log(`[Monitor] Process exited with code: ${code}, signal: ${signal}`);

      if (code === 0) {
        this.emit('complete', {
          sessionId: this.sessionId,
          output: this.outputBuffer.join('\n'),
          exitCode: code
        });
      } else if (this.retryCount < this.maxRetries) {
        console.log(`[Monitor] Retrying... (${this.retryCount + 1}/${this.maxRetries})`);
        setTimeout(() => this.resume(), 5000);
      } else {
        this.emit('error', {
          message: `Max retries (${this.maxRetries}) exceeded`,
          sessionId: this.sessionId,
          output: this.outputBuffer.join('\n')
        });
      }
    });

    // 进程错误
    this.process.on('error', (err) => {
      console.error(`[Monitor] Process error: ${err.message}`);
      this.emit('error', err);
    });
  }

  /**
   * 启动心跳检测
   */
  _startHeartbeat() {
    this.heartbeatTimer = setInterval(() => {
      const elapsed = Date.now() - this.lastHeartbeat;

      if (elapsed > this.timeout) {
        console.warn(`[Monitor] No heartbeat for ${elapsed}ms, checking status...`);

        // 检查是否是交互阻塞
        if (this._checkIfBlocked()) {
          this.emit('blocked', this.blockedReason);
          this._handleBlocking();
        } else {
          // 可能是进程卡死，尝试恢复
          this.emit('timeout', { elapsed, sessionId: this.sessionId });
          this._killAndRecover();
        }
      } else {
        this.emit('heartbeat', { elapsed, sessionId: this.sessionId });
      }
    }, this.heartbeatInterval);
  }

  /**
   * 检查输出中的阻塞信号
   */
  _checkForBlocking(output) {
    // 检测AskUserQuestion等待
    const blockingPatterns = [
      /waiting for user input/i,
      /please confirm/i,
      /do you want to/i,
      /\?\s*$/m,  // 以问号结尾
      /select an option/i,
      /press enter/i
    ];

    for (const pattern of blockingPatterns) {
      if (pattern.test(output)) {
        this.isBlocked = true;
        this.blockedReason = `Detected blocking pattern: ${pattern}`;
        return true;
      }
    }

    return false;
  }

  /**
   * 检查是否处于阻塞状态
   */
  _checkIfBlocked() {
    if (this.isBlocked) {
      return true;
    }

    // 检查最近的输出
    const recentOutput = this.outputBuffer.slice(-10).join('\n');
    return this._checkForBlocking(recentOutput);
  }

  /**
   * 处理交互阻塞
   */
  _handleBlocking() {
    console.log(`[Monitor] Handling blocking: ${this.blockedReason}`);

    // 根据阻塞类型自动响应
    const autoResponses = {
      'Do you want to continue?': 'y\n',
      'Do you want to proceed?': 'y\n',
      'Press Enter to continue': '\n',
      'Please confirm': 'y\n',
      'Select an option': '1\n'  // 选择第一个选项
    };

    // 查找匹配的自动响应
    for (const [pattern, response] of Object.entries(autoResponses)) {
      if (this.blockedReason.toLowerCase().includes(pattern.toLowerCase())) {
        console.log(`[Monitor] Auto-responding: ${response.trim()}`);
        this.process.stdin.write(response);
        this.isBlocked = false;
        this.blockedReason = null;
        return;
      }
    }

    // 无法自动响应，通知用户
    this.emit('blocked', {
      reason: this.blockedReason,
      recentOutput: this.outputBuffer.slice(-20).join('\n')
    });
  }

  /**
   * 杀死进程并恢复
   */
  _killAndRecover() {
    console.log('[Monitor] Killing process and attempting recovery...');

    if (this.process) {
      this.process.kill('SIGTERM');

      // 等待5秒后恢复
      setTimeout(() => {
        if (this.retryCount < this.maxRetries) {
          this.resume();
        }
      }, 5000);
    }
  }

  /**
   * 停止监控
   */
  stop() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
    }

    if (this.process) {
      this.process.kill('SIGTERM');
    }
  }

  /**
   * 获取状态报告
   */
  getStatus() {
    return {
      sessionId: this.sessionId,
      projectDir: this.projectDir,
      isRunning: this.process !== null,
      isBlocked: this.isBlocked,
      blockedReason: this.blockedReason,
      lastHeartbeat: this.lastHeartbeat,
      elapsedSinceHeartbeat: Date.now() - this.lastHeartbeat,
      retryCount: this.retryCount,
      outputLines: this.outputBuffer.length
    };
  }
}

// CLI入口
if (require.main === module) {
  const args = process.argv.slice(2);
  const options = {};

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--session-id') {
      options.sessionId = args[++i];
    } else if (args[i] === '--project-dir') {
      options.projectDir = args[++i];
    } else if (args[i] === '--timeout') {
      options.timeout = parseInt(args[++i]);
    } else if (args[i] === '--max-retries') {
      options.maxRetries = parseInt(args[++i]);
    }
  }

  const monitor = new ClaudeCodeMonitor(options);

  monitor.on('output', (output) => {
    process.stdout.write(output);
  });

  monitor.on('error', (err) => {
    console.error('Error:', err);
    process.exit(1);
  });

  monitor.on('complete', (result) => {
    console.log('\n[Monitor] Task completed successfully!');
    console.log(`Session ID: ${result.sessionId}`);
    process.exit(0);
  });

  monitor.on('blocked', (info) => {
    console.warn('\n[Monitor] Blocked! Requires user attention:');
    console.warn(info);
  });

  // 从标准输入读取prompt
  let prompt = '';
  process.stdin.on('data', (data) => {
    prompt += data;
  });

  process.stdin.on('end', () => {
    monitor.start(prompt.trim() || undefined);
  });
}

module.exports = { ClaudeCodeMonitor };