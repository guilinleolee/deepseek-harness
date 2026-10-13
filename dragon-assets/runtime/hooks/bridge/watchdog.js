
/**
 * Watchdog.js - 看门狗进程
 * 天龙引擎Bridge系统 V1.0
 *
 * 职责：
 * 1. 定期检查心跳时间戳
 * 2. 检测死锁/僵死状态
 * 3. 触发强制恢复
 * 4. 检测父进程存活
 *
 * 三层保险第三层：
 * - Layer 1 (Shell): EXIT trap - 自动善后
 * - Layer 2 (Python): BaseException - 捕获所有异常
 * - Layer 3 (Watchdog): 超时检测 - 检测死锁/僵死状态
 *
 * 解决问题：
 * - 进程僵死（僵尸进程）
 * - 死锁状态
 * - 无限循环
 * - 父进程意外死亡
 */

const fs = require('fs').promises;
const fsSync = require('fs');
const path = require('path');
const os = require('os');

class Watchdog {
  constructor(config = {}) {
    this.taskId = process.env.WATCHDOG_TASK_ID || config.taskId;
    this.statePath = process.env.WATCHDOG_STATE_PATH || config.statePath;
    this.logPath = process.env.WATCHDOG_LOG_PATH || config.logPath;

    // 配置
    this.interval = parseInt(
      process.env.WATCHDOG_INTERVAL || config.interval || '30000',
      10
    );
    this.maxHeartbeatAge = parseInt(
      process.env.WATCHDOG_MAX_HEARTBEAT_AGE || config.maxHeartbeatAge || '90000',
      10
    );
    this.forceKill = process.env.WATCHDOG_FORCE_KILL === 'true' || config.forceKill || false;

    // 状态
    this.running = true;
    this.checkCount = 0;
    this.lastStatus = null;

    // 父进程ID（用于检测父进程存活）
    this.ppid = process.ppid;
  }

  /**
   * 启动看门狗
   */
  async start() {
    this.log(`[Watchdog] Started for task ${this.taskId}`);
    this.log(`[Watchdog] Interval: ${this.interval}ms`);
    this.log(`[Watchdog] Max heartbeat age: ${this.maxHeartbeatAge}ms`);
    this.log(`[Watchdog] Force kill: ${this.forceKill}`);
    this.log(`[Watchdog] Parent PID: ${this.ppid}`);

    // 发送启动通知
    process.send?.({ type: 'started', taskId: this.taskId });

    while (this.running) {
      await this.check();
      await this.sleep(this.interval);
    }

    this.log('[Watchdog] Stopped');
  }

  /**
   * 执行检查
   */
  async check() {
    this.checkCount++;

    try {
      const state = await this.readState();

      if (!state) {
        this.log(`[Watchdog] Check #${this.checkCount}: No state file found`);
        return;
      }

      const heartbeatAge = Date.now() - (state.heartbeat || 0);
      const status = state.status || 'unknown';

      // 记录状态变化
      if (status !== this.lastStatus) {
        this.log(`[Watchdog] Status changed: ${this.lastStatus} -> ${status}`);
        this.lastStatus = status;
      }

      // 详细检查日志（每10次记录一次）
      if (this.checkCount % 10 === 0) {
        this.log(`[Watchdog] Check #${this.checkCount}: status=${status}, heartbeat_age=${heartbeatAge}ms`);
      }

      // 1. 检查心跳是否过期
      if (heartbeatAge > this.maxHeartbeatAge && status === 'running') {
        this.log(`[Watchdog] ⚠️ HEARTBEAT EXPIRED! Age: ${heartbeatAge}ms (max: ${this.maxHeartbeatAge}ms)`);
        await this.triggerRecovery(state, 'heartbeat_expired');
        return;
      }

      // 2. 检查是否处于僵死状态
      if (status === 'stuck' || status === 'deadlocked') {
        this.log(`[Watchdog] ⚠️ DETECTED STUCK/DEADLOCKED STATE`);
        await this.triggerRecovery(state, status);
        return;
      }

      // 3. 检查父进程是否存活
      if (!this.isParentAlive()) {
        this.log(`[Watchdog] ⚠️ PARENT PROCESS DIED (PPID: ${this.ppid})`);
        await this.triggerRecovery(state, 'parent_died');
        return;
      }

      // 4. 检查是否长时间运行（超过预期的3倍）
      if (state.started_at) {
        const runtime = Date.now() - new Date(state.started_at).getTime();
        const maxRuntime = this.maxHeartbeatAge * 3;

        if (runtime > maxRuntime && status === 'running') {
          this.log(`[Watchdog] ⚠️ LONG RUNNING TASK DETECTED: ${runtime}ms`);
          // 不立即触发恢复，只是警告
          process.send?.({
            type: 'warning',
            reason: 'long_running',
            runtime: runtime
          });
        }
      }

    } catch (error) {
      this.log(`[Watchdog] Check failed: ${error.message}`);

      // 连续失败检测
      if (this.checkCount > 3) {
        this.log(`[Watchdog] ⚠️ MULTIPLE CHECK FAILURES`);
      }
    }
  }

  /**
   * 读取状态文件
   */
  async readState() {
    try {
      const content = await fs.readFile(this.statePath, 'utf8');
      return JSON.parse(content);
    } catch (error) {
      if (error.code === 'ENOENT') {
        return null;
      }
      throw error;
    }
  }

  /**
   * 检查父进程是否存活
   */
  isParentAlive() {
    try {
      // 发送信号0只检查进程是否存在
      process.kill(this.ppid, 0);
      return true;
    } catch (e) {
      return false;
    }
  }

  /**
   * 触发恢复操作
   */
  async triggerRecovery(state, reason) {
    this.log(`[Watchdog] 🔴 TRIGGERING RECOVERY: ${reason}`);

    // 发送通知
    process.send?.({
      type: 'recovery_triggered',
      reason: reason,
      taskId: this.taskId,
      state: state
    });

    // 1. 更新状态
    const updatedState = {
      ...state,
      status: 'watchdog_recovery',
      watchdog_triggered: true,
      watchdog_reason: reason,
      watchdog_triggered_at: new Date().toISOString(),
      watchdog_check_count: this.checkCount
    };

    await this.atomicWrite(this.statePath, updatedState);

    // 2. 写入通知文件
    const notifyPath = path.join(
      path.dirname(this.statePath),
      'notifications',
      `watchdog-${Date.now()}.json`
    );

    try {
      await fs.mkdir(path.dirname(notifyPath), { recursive: true });
      await this.atomicWrite(notifyPath, {
        type: 'watchdog_recovery',
        task_id: state.task_id,
        reason: reason,
        triggered_at: new Date().toISOString(),
        original_status: state.status,
        heartbeat_age: Date.now() - (state.heartbeat || 0)
      });
    } catch (e) {
      this.log(`[Watchdog] Failed to write notification: ${e.message}`);
    }

    // 3. 强制终止（如果配置允许）
    if (this.forceKill && state.pid) {
      this.log(`[Watchdog] Force killing process ${state.pid}`);

      try {
        process.kill(state.pid, 'SIGKILL');
        this.log(`[Watchdog] Process ${state.pid} killed`);
      } catch (e) {
        this.log(`[Watchdog] Failed to kill process: ${e.message}`);
      }
    }

    // 4. 退出看门狗
    this.running = false;
  }

  /**
   * 原子写入文件
   */
  async atomicWrite(filePath, data) {
    const tempPath = `${filePath}.tmp.${process.pid}`;

    await fs.writeFile(tempPath, JSON.stringify(data, null, 2), 'utf8');

    // Windows兼容
    if (process.platform === 'win32') {
      try {
        await fs.unlink(filePath);
      } catch (e) {
        // 忽略
      }
    }

    await fs.rename(tempPath, filePath);
  }

  /**
   * 写入日志
   */
  log(message) {
    const timestamp = new Date().toISOString();
    const logEntry = `${timestamp} ${message}\n`;

    // 尝试写入日志文件
    try {
      fsSync.appendFileSync(this.logPath, logEntry, 'utf8');
    } catch (e) {
      // 日志写入失败不应影响执行
    }

    // 同时输出到控制台
    console.log(message);
  }

  /**
   * 休眠
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * 停止看门狗
   */
  stop() {
    this.log('[Watchdog] Stop requested');
    this.running = false;
  }
}

// =============================================================
// CLI入口
// =============================================================

if (require.main === module) {
  const watchdog = new Watchdog();

  // 处理信号
  process.on('SIGTERM', () => {
    console.log('[Watchdog] Received SIGTERM, stopping...');
    watchdog.stop();
  });

  process.on('SIGINT', () => {
    console.log('[Watchdog] Received SIGINT, stopping...');
    watchdog.stop();
  });

  // 处理IPC消息
  process.on('message', (msg) => {
    if (msg.command === 'stop') {
      watchdog.stop();
    }
  });

  // 启动
  watchdog.start().catch((error) => {
    console.error('[Watchdog] Fatal error:', error);
    process.exit(1);
  });
}

module.exports = Watchdog;