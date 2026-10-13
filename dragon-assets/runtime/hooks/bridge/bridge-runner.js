
/**
 * Bridge Runner - 调度室
 * 天龙引擎Bridge系统 V1.0
 *
 * 职责：
 * 1. 任务调度和状态监控
 * 2. 启动Watchdog看门狗进程
 * 3. 原子状态写入
 * 4. 通知回调
 *
 * 三层保险协调：
 * - Layer 1 (Shell): EXIT trap自动善后
 * - Layer 2 (Python): BaseException万能兜底
 * - Layer 3 (Watchdog): 看门狗超时检测
 */

const { spawn, fork } = require('child_process');
const fs = require('fs').promises;
const fsSync = require('fs');
const path = require('path');
const os = require('os');

class BridgeRunner {
  constructor(config = {}) {
    this.config = {
      bridgePath: config.bridgePath || path.join(__dirname, 'bridge.sh'),
      watchdogPath: config.watchdogPath || path.join(__dirname, 'watchdog.js'),
      stateDir: config.stateDir || path.join(os.homedir(), '.claude', 'state', 'bridge'),
      timeout: config.timeout || 300000, // 5分钟
      watchdogInterval: config.watchdogInterval || 30000, // 30秒检查
      maxHeartbeatAge: config.maxHeartbeatAge || 90000, // 90秒
      maxRetries: config.maxRetries || 3,
      ...config
    };

    // 确保状态目录存在
    this.ensureStateDir();

    // 活跃任务追踪
    this.activeRuns = new Map(); // taskId -> {process, watchdog, startTime}
  }

  /**
   * 确保状态目录存在
   */
  async ensureStateDir() {
    const dirs = [
      this.config.stateDir,
      path.join(this.config.stateDir, 'logs'),
      path.join(this.config.stateDir, 'history')
    ];

    for (const dir of dirs) {
      try {
        await fs.mkdir(dir, { recursive: true });
      } catch (e) {
        // 忽略已存在错误
      }
    }
  }

  /**
   * 执行任务 - 核心入口
   * @param {Object} task - 任务对象
   * @returns {Promise<Object>} 执行结果
   */
  async run(task) {
    const taskId = task.id || `task-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const statePath = path.join(this.config.stateDir, 'state.json');
    const logPath = path.join(this.config.stateDir, 'logs', `bridge-${Date.now()}.log`);

    console.log(`🌉 [Bridge] 启动任务 ${taskId}`);
    this.log(logPath, `Bridge Runner started for task ${taskId}`);

    // 1. 初始化状态
    await this.initState(statePath, taskId, task, logPath);

    // 2. 启动Watchdog看门狗进程
    const watchdog = this.startWatchdog(taskId, statePath, logPath);

    // 3. 启动bridge.sh子进程
    const childProcess = spawn('bash', [this.config.bridgePath], {
      env: {
        ...process.env,
        BRIDGE_TASK_ID: taskId,
        BRIDGE_TASK_JSON: JSON.stringify(task),
        BRIDGE_STATE_PATH: statePath,
        BRIDGE_LOG_PATH: logPath,
        BRIDGE_TIMEOUT: Math.floor(this.config.timeout / 1000).toString(),
        WATCHDOG_INTERVAL: this.config.watchdogInterval.toString()
      },
      stdio: ['ignore', 'pipe', 'pipe']
    });

    // 4. 记录活跃任务
    this.activeRuns.set(taskId, {
      process: childProcess,
      watchdog: watchdog,
      startTime: Date.now(),
      statePath: statePath,
      logPath: logPath
    });

    // 5. 监听输出
    childProcess.stdout?.on('data', (data) => {
      this.log(logPath, `[STDOUT] ${data.toString().trim()}`);
    });

    childProcess.stderr?.on('data', (data) => {
      this.log(logPath, `[STDERR] ${data.toString().trim()}`);
    });

    // 6. 返回Promise
    return new Promise((resolve, reject) => {
      childProcess.on('close', async (code) => {
        const result = await this.handleCompletion(taskId, code, statePath, logPath);

        // 停止Watchdog
        if (watchdog) {
          watchdog.kill();
        }

        // 清理活跃任务
        this.activeRuns.delete(taskId);

        if (code === 0) {
          console.log(`✅ [Bridge] 任务完成 ${taskId}`);
          resolve(result);
        } else {
          console.log(`❌ [Bridge] 任务失败 ${taskId} (exit code: ${code})`);
          reject(new Error(result.error || `Bridge execution failed with code ${code}`));
        }
      });

      childProcess.on('error', (err) => {
        this.log(logPath, `[ERROR] Process error: ${err.message}`);
        if (watchdog) {
          watchdog.kill();
        }
        this.activeRuns.delete(taskId);
        reject(err);
      });
    });
  }

  /**
   * 启动Watchdog看门狗进程
   */
  startWatchdog(taskId, statePath, logPath) {
    try {
      const watchdog = fork(this.config.watchdogPath, [], {
        env: {
          ...process.env,
          WATCHDOG_TASK_ID: taskId,
          WATCHDOG_STATE_PATH: statePath,
          WATCHDOG_LOG_PATH: logPath,
          WATCHDOG_INTERVAL: this.config.watchdogInterval.toString(),
          WATCHDOG_MAX_HEARTBEAT_AGE: this.config.maxHeartbeatAge.toString()
        },
        stdio: ['ignore', 'pipe', 'pipe', 'ipc']
      });

      watchdog.on('message', (msg) => {
        this.log(logPath, `[WATCHDOG] ${JSON.stringify(msg)}`);
      });

      watchdog.stderr?.on('data', (data) => {
        this.log(logPath, `[WATCHDOG ERROR] ${data.toString().trim()}`);
      });

      this.log(logPath, `Watchdog started for task ${taskId}`);
      return watchdog;
    } catch (e) {
      this.log(logPath, `[WARN] Failed to start watchdog: ${e.message}`);
      return null;
    }
  }

  /**
   * 初始化状态文件（原子写入）
   */
  async initState(statePath, taskId, task, logPath) {
    const state = {
      task_id: taskId,
      status: 'initialized',
      started_at: new Date().toISOString(),
      pid: process.pid,
      task: {
        id: task.id,
        content: task.content,
        priority: task.priority,
        agent: task.agent
      },
      result: null,
      error: null,
      watchdog_triggered: false,
      heartbeat: Date.now(),
      bridge_version: '1.0.0'
    };

    await this.atomicWrite(statePath, state);
    this.log(logPath, `State initialized for task ${taskId}`);
  }

  /**
   * 原子写入状态文件
   * 机制：先写临时文件，再原子重命名
   */
  async atomicWrite(filePath, data) {
    const tempPath = `${filePath}.tmp.${process.pid}`;
    const lockPath = `${filePath}.lock`;

    // 获取锁
    await this.acquireLock(lockPath);

    try {
      // 写入临时文件
      await fs.writeFile(tempPath, JSON.stringify(data, null, 2), 'utf8');

      // 原子重命名（跨平台处理）
      if (process.platform === 'win32') {
        // Windows: 先删除目标文件
        try {
          await fs.unlink(filePath);
        } catch (e) {
          // 忽略文件不存在错误
        }
      }

      await fs.rename(tempPath, filePath);
    } finally {
      // 释放锁
      await this.releaseLock(lockPath);
    }
  }

  /**
   * 获取文件锁
   */
  async acquireLock(lockPath, timeout = 5000) {
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
      try {
        // 尝试创建锁文件（排他模式）
        const fd = fsSync.openSync(lockPath, 'wx');
        fsSync.writeSync(fd, process.pid.toString());
        fsSync.closeSync(fd);
        return true;
      } catch (e) {
        if (e.code === 'EEXIST') {
          // 检查锁是否过期
          try {
            const stats = fsSync.statSync(lockPath);
            if (Date.now() - stats.mtimeMs > timeout) {
              // 锁过期，删除并重试
              fsSync.unlinkSync(lockPath);
              continue;
            }
          } catch (e) {
            // 忽略错误
          }

          // 等待一段时间后重试
          await new Promise(r => setTimeout(r, 100));
        } else {
          throw e;
        }
      }
    }

    throw new Error('Lock acquisition timeout');
  }

  /**
   * 释放文件锁
   */
  async releaseLock(lockPath) {
    try {
      await fs.unlink(lockPath);
    } catch (e) {
      // 忽略错误
    }
  }

  /**
   * 处理任务完成
   */
  async handleCompletion(taskId, exitCode, statePath, logPath) {
    let state;

    try {
      const content = await fs.readFile(statePath, 'utf8');
      state = JSON.parse(content);
    } catch (e) {
      state = { task_id: taskId, status: 'unknown' };
    }

    // 更新状态
    state.status = exitCode === 0 ? 'completed' : 'failed';
    state.completed_at = new Date().toISOString();
    state.exit_code = exitCode;

    await this.atomicWrite(statePath, state);
    this.log(logPath, `Task ${taskId} completed with status: ${state.status}`);

    // 保存历史记录
    await this.saveHistory(taskId, state);

    // 触发通知回调
    await this.notifyCallback(state, logPath);

    return state;
  }

  /**
   * 保存历史记录
   */
  async saveHistory(taskId, state) {
    const historyPath = path.join(this.config.stateDir, 'history', `${taskId}.json`);

    try {
      await fs.writeFile(historyPath, JSON.stringify(state, null, 2), 'utf8');
    } catch (e) {
      // 忽略错误
    }
  }

  /**
   * 通知回调
   * 与现有天龙引擎通信协议集成
   */
  async notifyCallback(state, logPath) {
    // 方式1：写入OpenClaw状态文件（如果存在）
    const openclawPath = path.join(
      os.homedir(),
      '.openclaw',
      'workspace',
      'state',
      'cc-result.json'
    );

    try {
      await fs.mkdir(path.dirname(openclawPath), { recursive: true });
      await fs.writeFile(openclawPath, JSON.stringify({
        session_id: state.task_id,
        status: state.status,
        completed_at: state.completed_at,
        result: state.result,
        error: state.error
      }, null, 2), 'utf8');
      this.log(logPath, 'Callback written to OpenClaw state');
    } catch (e) {
      this.log(logPath, `[WARN] Failed to write OpenClaw callback: ${e.message}`);
    }

    // 方式2：写入天龙引擎通知文件
    const dragonNotifyPath = path.join(
      os.homedir(),
      '.claude',
      'state',
      'bridge',
      'notifications',
      `${state.task_id}.json`
    );

    try {
      await fs.mkdir(path.dirname(dragonNotifyPath), { recursive: true });
      await fs.writeFile(dragonNotifyPath, JSON.stringify({
        type: 'task_completed',
        task_id: state.task_id,
        status: state.status,
        timestamp: new Date().toISOString(),
        data: state
      }, null, 2), 'utf8');
    } catch (e) {
      // 忽略错误
    }
  }

  /**
   * 中止任务
   */
  async abort(taskId) {
    const run = this.activeRuns.get(taskId);

    if (!run) {
      throw new Error(`Task ${taskId} not found or already completed`);
    }

    console.log(`🛑 [Bridge] 中止任务 ${taskId}`);

    // 更新状态
    const state = {
      task_id: taskId,
      status: 'aborted',
      aborted_at: new Date().toISOString()
    };

    await this.atomicWrite(run.statePath, state);

    // 终止进程
    run.process.kill('SIGTERM');

    // 停止Watchdog
    if (run.watchdog) {
      run.watchdog.kill();
    }

    this.activeRuns.delete(taskId);

    return state;
  }

  /**
   * 获取任务状态
   */
  async getStatus(taskId) {
    const statePath = path.join(this.config.stateDir, 'state.json');
    const historyPath = path.join(this.config.stateDir, 'history', `${taskId}.json`);

    // 先检查当前状态
    try {
      const content = await fs.readFile(statePath, 'utf8');
      const state = JSON.parse(content);
      if (state.task_id === taskId) {
        return state;
      }
    } catch (e) {
      // 忽略错误
    }

    // 再检查历史记录
    try {
      const content = await fs.readFile(historyPath, 'utf8');
      return JSON.parse(content);
    } catch (e) {
      throw new Error(`Task ${taskId} not found`);
    }
  }

  /**
   * 获取所有活跃任务
   */
  getActiveTasks() {
    const tasks = [];

    for (const [taskId, run] of this.activeRuns) {
      tasks.push({
        task_id: taskId,
        started_at: new Date(run.startTime).toISOString(),
        duration: Date.now() - run.startTime
      });
    }

    return tasks;
  }

  /**
   * 写入日志
   */
  log(logPath, message) {
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] ${message}\n`;

    try {
      fsSync.appendFileSync(logPath, logEntry, 'utf8');
    } catch (e) {
      // 日志写入失败不应影响执行
    }
  }
}

// 导出
module.exports = BridgeRunner;

// CLI入口
if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];

  const runner = new BridgeRunner();

  switch (command) {
    case 'run':
      const taskJson = args[1];
      if (!taskJson) {
        console.error('Usage: bridge-runner.js run <task-json>');
        process.exit(1);
      }
      const task = JSON.parse(taskJson);
      runner.run(task)
        .then(result => console.log(JSON.stringify(result, null, 2)))
        .catch(err => {
          console.error(err.message);
          process.exit(1);
        });
      break;

    case 'status':
      const taskId = args[1];
      runner.getStatus(taskId)
        .then(state => console.log(JSON.stringify(state, null, 2)))
        .catch(err => {
          console.error(err.message);
          process.exit(1);
        });
      break;

    case 'abort':
      const abortTaskId = args[1];
      runner.abort(abortTaskId)
        .then(state => console.log(JSON.stringify(state, null, 2)))
        .catch(err => {
          console.error(err.message);
          process.exit(1);
        });
      break;

    case 'active':
      const activeTasks = runner.getActiveTasks();
      console.log(JSON.stringify(activeTasks, null, 2));
      break;

    default:
      console.log(`
Bridge Runner - 天龙引擎Bridge系统 V1.0

Usage:
  node bridge-runner.js run <task-json>    执行任务
  node bridge-runner.js status <task-id>   查看状态
  node bridge-runner.js abort <task-id>    中止任务
  node bridge-runner.js active             查看活跃任务
`);
  }
}