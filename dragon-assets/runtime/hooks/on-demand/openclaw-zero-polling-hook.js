#!/usr/bin/env node
/**
 * =============================================================
 * OpenClaw Zero-Polling Hook - Claude Code Callback
 * =============================================================
 * Triggered by Claude Code hooks when a task completes (Stop)
 * or session ends (SessionEnd). Writes results to a state file
 * for OpenClaw to read, achieving zero-polling event-driven sync.
 *
 * Integration: Dragon Engine V7.1 + OpenClaw Protocol
 * Author: Dragon Engine Team
 * Created: 2026-02-25
 * =============================================================
 */

const fs = require('fs').promises;
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const CONFIG = {
  stateDir: path.join(process.env.HOME || process.env.USERPROFILE, '.openclaw/workspace/state'),
  taskFile: 'cc-task.json',
  resultFile: 'cc-result.json',
  lockFile: 'cc-complete.lock',
  logFile: 'cc-hook.log',
  dedupWindow: 60000, // 60 seconds
  lockTimeout: 30000, // 30 seconds
};

// Logger
async function log(message) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] ${message}\n`;
  const logPath = path.join(CONFIG.stateDir, CONFIG.logFile);

  try {
    await fs.appendFile(logPath, logMessage);
  } catch (err) {
    // Silently fail if logging fails
  }
}

// Ensure state directory exists
async function ensureStateDir() {
  try {
    await fs.mkdir(CONFIG.stateDir, { recursive: true });
  } catch (err) {
    await log(`ERROR: Failed to create state dir: ${err.message}`);
  }
}

// Check deduplication
async function shouldSkip() {
  const resultPath = path.join(CONFIG.stateDir, CONFIG.resultFile);

  try {
    const stats = await fs.stat(resultPath);
    const age = Date.now() - stats.mtimeMs;

    if (age < CONFIG.dedupWindow) {
      await log(`Dedup: result file is ${Math.floor(age / 1000)}s old (< ${CONFIG.dedupWindow / 1000}s), skipping`);
      return true;
    }
  } catch (err) {
    // File doesn't exist, proceed
  }

  return false;
}

// Acquire lock
async function acquireLock() {
  const lockPath = path.join(CONFIG.stateDir, CONFIG.lockFile);

  try {
    const stats = await fs.stat(lockPath);
    const age = Date.now() - stats.mtimeMs;

    if (age < CONFIG.lockTimeout) {
      await log(`Lock exists and is ${Math.floor(age / 1000)}s old, skipping`);
      return false;
    }
  } catch (err) {
    // Lock file doesn't exist
  }

  try {
    await fs.writeFile(lockPath, process.pid.toString());
    return true;
  } catch (err) {
    await log(`ERROR: Failed to acquire lock: ${err.message}`);
    return false;
  }
}

// Release lock
async function releaseLock() {
  const lockPath = path.join(CONFIG.stateDir, CONFIG.lockFile);

  try {
    await fs.unlink(lockPath);
  } catch (err) {
    // Lock file doesn't exist or can't be removed
  }
}

// Calculate duration
function calculateDuration(dispatchedAt) {
  if (!dispatchedAt) return 'unknown';

  try {
    const start = new Date(dispatchedAt);
    const end = new Date();
    const elapsed = Math.floor((end - start) / 1000);

    if (elapsed >= 3600) {
      const hours = Math.floor(elapsed / 3600);
      const minutes = Math.floor((elapsed % 3600) / 60);
      const seconds = elapsed % 60;
      return `${hours}h${minutes}m${seconds}s`;
    } else if (elapsed >= 60) {
      const minutes = Math.floor(elapsed / 60);
      const seconds = elapsed % 60;
      return `${minutes}m${seconds}s`;
    } else {
      return `${elapsed}s`;
    }
  } catch (err) {
    return 'unknown';
  }
}

// Collect file tree
function collectFileTree(workDir, maxLines = 30) {
  try {
    const result = execSync(
      `find "${workDir}" -maxdepth 3 \\( -not -path "*/node_modules/*" -and -not -path "*/.git/*" -and -not -path "*/dist/*" -and -not -path "*/__pycache__/*" -and -not -name ".DS_Store" \\) 2>/dev/null | head -${maxLines}`,
      { encoding: 'utf8', maxBuffer: 1024 * 1024 }
    );

    return result.trim().split('\n').map(p => p.replace(workDir + '/', '')).join('\n');
  } catch (err) {
    return '';
  }
}

// Main hook function
async function onTaskComplete(input) {
  await log('Hook triggered: onTaskComplete');

  // Parse input
  const data = JSON.parse(input);
  const { sessionId, transcriptPath, cwd, hookEventName } = data;

  await log(`Event=${hookEventName} SessionID=${sessionId} CWD=${cwd}`);

  // Check deduplication
  if (await shouldSkip()) {
    return;
  }

  // Acquire lock
  if (!(await acquireLock())) {
    return;
  }

  try {
    // Read task info
    const taskPath = path.join(CONFIG.stateDir, CONFIG.taskFile);
    let taskName = 'unknown';
    let taskDispatched = '';
    let workDir = cwd;

    try {
      const taskData = JSON.parse(await fs.readFile(taskPath, 'utf8'));
      taskName = taskData.task || 'unknown';
      taskDispatched = taskData.dispatched_at || '';
      workDir = taskData.work_dir || cwd;
      await log(`Task file found: ${taskName}`);
    } catch (err) {
      await log('No task file found, using defaults');
    }

    // Calculate duration
    const duration = calculateDuration(taskDispatched);
    const completedAt = new Date().toISOString();

    // Collect file tree
    const fileTree = collectFileTree(workDir);

    // Write result JSON
    const result = {
      session_id: sessionId,
      hook_event: hookEventName,
      task: taskName,
      work_dir: workDir,
      status: 'completed',
      completed_at: completedAt,
      duration: duration,
      transcript_path: transcriptPath,
      file_tree: fileTree,
    };

    const resultPath = path.join(CONFIG.stateDir, CONFIG.resultFile);
    await fs.writeFile(resultPath, JSON.stringify(result, null, 2));
    await log(`Result written to ${resultPath}`);

    // TODO: Send wake event to OpenClaw CLI
    // This would require OpenClaw CLI integration
    // await sendWakeEvent(result);

    await log('Hook completed successfully');
  } catch (err) {
    await log(`ERROR: Hook failed: ${err.message}`);
  } finally {
    await releaseLock();
  }
}

// Export for Claude Code hooks
module.exports = async function(input) {
  await ensureStateDir();
  await onTaskComplete(input);
};

// Allow direct execution for testing
if (require.main === module) {
  const testData = JSON.stringify({
    sessionId: 'test-session-123',
    transcriptPath: '/path/to/transcript',
    cwd: process.cwd(),
    hookEventName: 'Stop',
  });

  module.exports(testData).catch(console.error);
}
