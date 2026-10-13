#!/usr/bin/env node
/**
 * 天龙引擎 V7.5 - Session Hook (JavaScript 包装器)
 * userPromptSubmit 触发点
 *
 * 功能：
 * - 检测当前会话是否存在
 * - 若不存在则创建新会话
 * - 保存用户消息
 * - 更新会话时间戳
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const crypto = require('crypto');

// 数据库路径
const DB_PATH = path.join(os.homedir(), '.claude', '.claude.db');
const STATE_PATH = path.join(os.homedir(), '.claude', '.session-state.json');

/**
 * 生成 UUID
 */
function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

/**
 * 读取会话状态
 */
function readState() {
  try {
    if (fs.existsSync(STATE_PATH)) {
      const content = fs.readFileSync(STATE_PATH, 'utf-8');
      return JSON.parse(content);
    }
  } catch (e) {
    // ignore
  }
  return { currentSessionId: null, sessions: {} };
}

/**
 * 写入会话状态
 */
function writeState(state) {
  const dir = path.dirname(STATE_PATH);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  fs.writeFileSync(STATE_PATH, JSON.stringify(state, null, 2));
}

/**
 * Hook 主函数
 */
function main() {
  const args = process.argv.slice(2);
  const prompt = args[0] || '';
  const context = args[1] ? JSON.parse(args[1]) : {};

  const now = Date.now();
  const state = readState();

  // 获取或创建当前会话
  let sessionId = state.currentSessionId;
  let isNew = false;

  // 检查当前会话是否有效（超过 1 小时未活动则创建新会话）
  const ONE_HOUR = 60 * 60 * 1000;
  if (sessionId && state.sessions[sessionId]) {
    const lastActive = state.sessions[sessionId].lastActiveAt;
    if (now - lastActive > ONE_HOUR) {
      sessionId = null;
    }
  }

  if (!sessionId) {
    // 创建新会话
    sessionId = uuidv4();
    isNew = true;

    state.sessions[sessionId] = {
      id: sessionId,
      title: prompt.slice(0, 50),
      createdAt: now,
      lastActiveAt: now,
      status: 'active',
      metadata: {
        projectPath: context.cwd || process.cwd(),
        agentId: context.agentId || null,
        model: context.model || null,
      },
    };

    // 归档旧会话
    for (const [id, session] of Object.entries(state.sessions)) {
      if (id !== sessionId && session.status === 'active') {
        state.sessions[id].status = 'archived';
      }
    }
  }

  // 更新会话
  state.currentSessionId = sessionId;
  state.sessions[sessionId].lastActiveAt = now;
  state.sessions[sessionId].messageCount = (state.sessions[sessionId].messageCount || 0) + 1;

  writeState(state);

  // 输出结果
  const result = {
    sessionId,
    isNew,
    title: state.sessions[sessionId].title,
  };

  console.log(JSON.stringify(result));
}

// 如果直接运行
if (require.main === module) {
  main();
}

module.exports = { main, readState, writeState, uuidv4 };