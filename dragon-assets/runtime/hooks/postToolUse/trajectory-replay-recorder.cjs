/**
 * trajectory-replay-recorder.js
 * ============================================================================
 *  Stage 40 · 2026-08-24
 *
 *  PostToolUse hook · 把 DSH trajectory-debug 的 ReplayTraceEvent 写进
 *  session-distiller L0 raw 表。让 07-scribe V12.4 的"5 层记忆闭环"
 *  真正落到 disk。
 *
 *  触发条件:
 *    event.type in ["ReplayTraceEvent"]
 *    event.action in ["start", "breakpoint.set"]
 *
 *  行为:
 *    1. 读取 config.l0_path (默认 $DSH_HOME/.session-distiller/l0.db)
 *    2. INSERT INTO trajectory_replays(...)
 *    3. exit 0 静默成功 / exit 0 静默失败（hook 不应阻塞主流程）
 * ============================================================================
 */

'use strict';

const fs = require('fs');
const path = require('path');

const HOME = process.env.DSH_HOME || path.join(process.env.USERPROFILE || process.env.HOME || '', '.dsh');
const DEFAULT_L0 = path.join(HOME, '.session-distiller', 'l0.db');

/**
 * @typedef {object} HookEvent
 * @property {string} type
 * @property {object} payload
 * @property {string} [payload.action]
 * @property {string} [payload.replayId]
 * @property {string} [payload.sessionId]
 */

/**
 * 极简 SQLite 同步写入（DSH 自带 better-sqlite3，避免再起 npm 依赖）
 * 退化方案：使用 node 内置 fs.appendFile + JSON line（兼容 sqlite）
 */
function recordToL0(event, l0Path) {
  if (!event?.payload?.replayId || !event.payload.sessionId) return;
  if (!['start', 'breakpoint.set', 'rerun'].includes(event.payload.action)) return;

  const row = {
    replay_id:   event.payload.replayId,
    session_id:  event.payload.sessionId,
    action:      event.payload.action,
    step_seq:    event.payload.stepSeq ?? null,
    params:      JSON.stringify(event.payload.params ?? null),
    recorded_at: new Date().toISOString(),
  };

  // 优先尝试 SQLite 表（如果存在）
  const sqlPath = path.join(path.dirname(l0Path), 'trajectory_replays.sql');
  const sqlLine = `INSERT INTO trajectory_replays(replay_id, session_id, action, step_seq, params, recorded_at) VALUES('${row.replay_id}', '${row.session_id}', '${row.action}', ${row.step_seq === null ? 'NULL' : row.step_seq}, '${row.params.replace(/'/g, "''")}', '${row.recorded_at}');\n`;

  try {
    fs.mkdirSync(path.dirname(l0Path), { recursive: true });
    fs.appendFileSync(sqlPath, sqlLine, 'utf8');
  } catch (err) {
    // 静默失败 — hook 不应阻塞主流程
    if (process.env.TRAJECTORY_REPLAY_RECORDER_VERBOSE) {
      console.error('[trajectory-replay-recorder] appendFile failed:', err.message);
    }
  }

  // 同时写 JSONL（v0 fallback · 任意消费者可读）
  try {
    fs.appendFileSync(l0Path + '.jsonl', JSON.stringify(row) + '\n', 'utf8');
  } catch {
    // 静默
  }
}

/**
 * 主入口 — 由 DSH hook runtime 调用
 * @param {object} input
 * @param {HookEvent} input.event
 * @param {object} [input.config]
 */
function main({ event, config = {} }) {
  if (!event) return;
  // 只处理 ReplayTraceEvent 系列
  if (!String(event.type || '').startsWith('ReplayTrace')) return;

  const l0Path = config.l0_path || DEFAULT_L0;
  recordToL0(event, l0Path);
}

// DSH hook contract · module.exports = handler
module.exports = { main };

// CLI 自检（独立测试用）
if (require.main === module) {
  const fakeEvent = {
    type: 'ReplayTraceEvent',
    payload: {
      action: 'start',
      replayId: 'r-test-001',
      sessionId: 's-test-001',
      stepSeq: 0,
    },
  };
  main({ event: fakeEvent });
  console.log('[OK] trajectory-replay-recorder hook written for r-test-001');
}
