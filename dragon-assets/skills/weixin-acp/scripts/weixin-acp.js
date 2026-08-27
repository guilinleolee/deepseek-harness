#!/usr/bin/env node
/**
 * weixin-acp 启动脚本
 * 用于启动 Claude Code 微信桥接服务
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const WEIXIN_DATA_DIR = process.env.WEIXIN_DATA_DIR || path.join(process.env.HOME, '.weixin-acp');
const PID_FILE = path.join(WEIXIN_DATA_DIR, 'weixin-acp.pid');
const LOG_FILE = path.join(WEIXIN_DATA_DIR, 'weixin-acp.log');

// 确保数据目录存在
if (!fs.existsSync(WEIXIN_DATA_DIR)) {
  fs.mkdirSync(WEIXIN_DATA_DIR, { recursive: true });
}

const commands = {
  start: () => {
    console.log('🚀 启动微信 Claude Code 桥接服务...\n');

    // 检查是否已运行
    if (fs.existsSync(PID_FILE)) {
      const pid = fs.readFileSync(PID_FILE, 'utf-8');
      try {
        process.kill(pid, 0);
        console.log('⚠️  服务已在运行中 (PID: ' + pid + ')');
        console.log('   如需重启，请先运行: weixin-acp stop');
        return;
      } catch (e) {
        // 进程不存在，继续启动
      }
    }

    const child = spawn('npx', ['weixin-acp', 'claude-code'], {
      detached: true,
      stdio: ['ignore', fs.openSync(LOG_FILE, 'a'), fs.openSync(LOG_FILE, 'a')],
      shell: true
    });

    fs.writeFileSync(PID_FILE, child.pid.toString());

    console.log('✅ 服务已启动 (PID: ' + child.pid + ')');
    console.log('📝 日志文件: ' + LOG_FILE);
    console.log('\n📱 请扫描二维码登录微信...\n');

    child.unref();
  },

  stop: () => {
    if (!fs.existsSync(PID_FILE)) {
      console.log('⚠️  服务未运行');
      return;
    }

    const pid = fs.readFileSync(PID_FILE, 'utf-8');
    try {
      process.kill(pid, 'SIGTERM');
      fs.unlinkSync(PID_FILE);
      console.log('✅ 服务已停止 (PID: ' + pid + ')');
    } catch (e) {
      console.log('⚠️  进程不存在，清理 PID 文件');
      fs.unlinkSync(PID_FILE);
    }
  },

  status: () => {
    if (!fs.existsSync(PID_FILE)) {
      console.log('⚠️  服务未运行');
      return;
    }

    const pid = fs.readFileSync(PID_FILE, 'utf-8');
    try {
      process.kill(pid, 0);
      console.log('✅ 服务运行中 (PID: ' + pid + ')');
      console.log('📝 日志文件: ' + LOG_FILE);

      // 显示最后10行日志
      if (fs.existsSync(LOG_FILE)) {
        console.log('\n📋 最近日志:');
        const logs = require('child_process')
          .execSync('tail -10 "' + LOG_FILE + '"')
          .toString();
        console.log(logs);
      }
    } catch (e) {
      console.log('⚠️  进程已退出，PID 文件需要清理');
      fs.unlinkSync(PID_FILE);
    }
  },

  logs: () => {
    if (!fs.existsSync(LOG_FILE)) {
      console.log('⚠️  日志文件不存在');
      return;
    }
    spawn('tail', ['-f', LOG_FILE], { stdio: 'inherit' });
  }
};

const cmd = process.argv[2] || 'start';
if (commands[cmd]) {
  commands[cmd]();
} else {
  console.log('用法: weixin-acp [start|stop|status|logs]');
  console.log('');
  console.log('命令:');
  console.log('  start   启动微信桥接服务');
  console.log('  stop    停止服务');
  console.log('  status  查看服务状态');
  console.log('  logs    查看实时日志');
}