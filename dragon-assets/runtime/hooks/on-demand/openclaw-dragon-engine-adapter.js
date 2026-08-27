#!/usr/bin/env node
/**
 * =============================================================
 * OpenClaw + Dragon Engine Task Queue Adapter
 * =============================================================
 * Integrates OpenClaw zero-polling with Dragon Engine V7.1
 * task queue system for enhanced task orchestration.
 *
 * Features:
 * - Automatic task creation from Claude Code completion events
 * - Priority inference from task metadata
 * - Agent recommendation based on task type
 * - Result persistence and tracking
 *
 * Integration: Dragon Engine V7.1 + OpenClaw Protocol
 * Author: Dragon Engine Team
 * Created: 2026-02-25
 * =============================================================
 */

const fs = require('fs').promises;
const path = require('path');

// Configuration
const CONFIG = {
  stateDir: path.join(process.env.HOME || process.env.USERPROFILE, '.openclaw/workspace/state'),
  dragonQueuePath: '.claude/task-queue.json',
  openclawResultFile: 'cc-result.json',
};

// Task type to agent mapping (Dragon Engine V7.1)
const AGENT_MAPPING = {
  analysis: { agent: '00analyst', priority: 'high' },
  investigation: { agent: '01investigator', priority: 'high' },
  architecture: { agent: '02architect', priority: 'high' },
  build: { agent: '03builder', priority: 'normal' },
  test: { agent: '04validator', priority: 'normal' },
  security: { agent: '05security-reviewer', priority: 'high' },
  review: { agent: '06code-reviewer', priority: 'normal' },
  documentation: { agent: '07scribe', priority: 'low' },
  publish: { agent: '08publisher', priority: 'low' },
  default: { agent: 'general-purpose', priority: 'normal' },
};

// Task keywords for type inference (order matters - more specific first)
const TASK_KEYWORDS = {
  test: ['unit test', 'integration test', 'e2e test', 'test', 'verify', 'validate', 'check'],
  security: ['security', 'vulnerability', 'audit', 'sanitize'],
  documentation: ['documentation', 'readme', 'guide', 'tutorial', 'document'],
  architecture: ['architecture', 'blueprint', 'design system'],
  analysis: ['analyze', 'investigate', 'research', 'study', 'examine'],
  investigation: ['archaeology', 'codebase', 'existing', 'legacy'],
  build: ['implement', 'build', 'create', 'develop', 'write code', 'write function'],
  review: ['review', 'code review'],
  publish: ['publish', 'deploy', 'release', 'distribute'],
};

// Infer task type from task name
function inferTaskType(taskName) {
  const lowerName = taskName.toLowerCase();

  for (const [type, keywords] of Object.entries(TASK_KEYWORDS)) {
    for (const keyword of keywords) {
      if (lowerName.includes(keyword)) {
        return type;
      }
    }
  }

  return 'default';
}

// Parse OpenClaw result
async function parseOpenClawResult() {
  const resultPath = path.join(CONFIG.stateDir, CONFIG.openclawResultFile);

  try {
    const content = await fs.readFile(resultPath, 'utf8');
    return JSON.parse(content);
  } catch (err) {
    console.error(`Failed to read OpenClaw result: ${err.message}`);
    return null;
  }
}

// Create Dragon Engine task from OpenClaw result
function createDragonTask(openclawResult) {
  const taskType = inferTaskType(openclawResult.task);
  const agentConfig = AGENT_MAPPING[taskType] || AGENT_MAPPING.default;

  return {
    id: `oc-${openclawResult.session_id}`,
    name: openclawResult.task,
    description: `OpenClaw task completion: ${openclawResult.task}`,
    type: taskType,
    priority: agentConfig.priority,
    status: 'completed',
    agent: agentConfig.agent,
    work_dir: openclawResult.work_dir,
    metadata: {
      session_id: openclawResult.session_id,
      hook_event: openclawResult.hook_event,
      completed_at: openclawResult.completed_at,
      duration: openclawResult.duration,
      transcript_path: openclawResult.transcript_path,
      file_tree: openclawResult.file_tree,
      source: 'openclaw-zero-polling',
    },
    completed_at: openclawResult.completed_at,
  };
}

// Load Dragon Engine task queue
async function loadDragonQueue() {
  try {
    const content = await fs.readFile(CONFIG.dragonQueuePath, 'utf8');
    return JSON.parse(content);
  } catch (err) {
    // Queue doesn't exist, create new
    return {
      version: '1.0.0',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      tasks: [],
      stats: {
        total: 0,
        pending: 0,
        in_progress: 0,
        completed: 0,
        failed: 0,
      },
    };
  }
}

// Save Dragon Engine task queue
async function saveDragonQueue(queue) {
  queue.updated_at = new Date().toISOString();

  // Recalculate stats
  queue.stats = {
    total: queue.tasks.length,
    pending: queue.tasks.filter(t => t.status === 'pending').length,
    in_progress: queue.tasks.filter(t => t.status === 'in_progress').length,
    completed: queue.tasks.filter(t => t.status === 'completed').length,
    failed: queue.tasks.filter(t => t.status === 'failed').length,
  };

  await fs.writeFile(
    CONFIG.dragonQueuePath,
    JSON.stringify(queue, null, 2),
    'utf8'
  );
}

// Add task to Dragon Engine queue
async function addTaskToQueue(dragonTask) {
  const queue = await loadDragonQueue();

  // Check if task already exists
  const existingIndex = queue.tasks.findIndex(t => t.id === dragonTask.id);

  if (existingIndex >= 0) {
    // Update existing task
    queue.tasks[existingIndex] = dragonTask;
  } else {
    // Add new task
    queue.tasks.push(dragonTask);
  }

  await saveDragonQueue(queue);

  return queue;
}

// Main integration function
async function integrateWithDragonEngine() {
  console.log('🐉 OpenClaw + Dragon Engine Integration');
  console.log('==========================================');

  // Parse OpenClaw result
  const openclawResult = await parseOpenClawResult();

  if (!openclawResult) {
    console.error('❌ No OpenClaw result found');
    return;
  }

  console.log(`📋 Task: ${openclawResult.task}`);
  console.log(`⏱️  Duration: ${openclawResult.duration}`);
  console.log(`📁 Work Dir: ${openclawResult.work_dir}`);

  // Create Dragon Engine task
  const dragonTask = createDragonTask(openclawResult);

  console.log(`🎯 Task Type: ${dragonTask.type}`);
  console.log(`🤖 Recommended Agent: ${dragonTask.agent}`);
  console.log(`⚡ Priority: ${dragonTask.priority}`);

  // Add to Dragon Engine queue
  const queue = await addTaskToQueue(dragonTask);

  console.log(`\n✅ Task added to Dragon Engine queue`);
  console.log(`📊 Queue Stats: ${queue.stats.completed}/${queue.stats.total} completed`);

  // Display recent tasks
  const recentTasks = queue.tasks
    .filter(t => t.status === 'completed')
    .slice(-5)
    .reverse();

  console.log(`\n📜 Recent Completed Tasks:`);
  recentTasks.forEach((task, index) => {
    console.log(`   ${index + 1}. [${task.priority}] ${task.name} (${task.duration || 'N/A'})`);
  });
}

// CLI command handler
async function handleCommand(command, args) {
  switch (command) {
    case 'status':
      await showStatus();
      break;
    case 'sync':
      await integrateWithDragonEngine();
      break;
    default:
      console.log('Usage: node openclaw-dragon-engine-adapter.js <status|sync>');
  }
}

// Show status
async function showStatus() {
  const queue = await loadDragonQueue();

  console.log('🐉 Dragon Engine Task Queue Status');
  console.log('==================================');
  console.log(`Total Tasks: ${queue.stats.total}`);
  console.log(`Pending: ${queue.stats.pending}`);
  console.log(`In Progress: ${queue.stats.in_progress}`);
  console.log(`Completed: ${queue.stats.completed}`);
  console.log(`Failed: ${queue.stats.failed}`);
  console.log(`Updated: ${queue.updated_at}`);

  const openclawTasks = queue.tasks.filter(t => t.metadata?.source === 'openclaw-zero-polling');
  console.log(`\n📡 OpenClaw Integration: ${openclawTasks.length} tasks`);
}

// Allow direct execution
if (require.main === module) {
  const command = process.argv[2] || 'sync';
  handleCommand(command, process.argv.slice(3))
    .catch(console.error);
}

module.exports = {
  integrateWithDragonEngine,
  createDragonTask,
  addTaskToQueue,
  loadDragonQueue,
  saveDragonQueue,
};
