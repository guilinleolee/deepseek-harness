#!/usr/bin/env node
/**
 * GSD Workstreams Script
 *
 * GSD并行波次执行工作流管理脚本
 *
 * @version 1.0.0
 * @author Dragon Engine Team + GSD
 */

const fs = require('fs');
const path = require('path');

// ANSI颜色
const colors = {
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  reset: '\x1b[0m'
};

// 状态文件
const STATE_DIR = path.join(process.cwd(), '.gsd-workstreams');
const STATE_FILE = path.join(STATE_DIR, 'state.json');
const WORKSTREAMS_FILE = path.join(STATE_DIR, 'workstreams.json');

// 确保状态目录存在
function ensureStateDir() {
  if (!fs.existsSync(STATE_DIR)) {
    fs.mkdirSync(STATE_DIR, { recursive: true });
  }
}

// 加载状态
function loadState() {
  try {
    if (fs.existsSync(STATE_FILE)) {
      return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
    }
  } catch (error) {
    // Ignore
  }
  return { activeWorkstream: null };
}

// 保存状态
function saveState(state) {
  ensureStateDir();
  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

// 加载工作流列表
function loadWorkstreams() {
  try {
    if (fs.existsSync(WORKSTREAMS_FILE)) {
      return JSON.parse(fs.readFileSync(WORKSTREAMS_FILE, 'utf8'));
    }
  } catch (error) {
    // Ignore
  }
  return [];
}

// 保存工作流列表
function saveWorkstreams(workstreams) {
  ensureStateDir();
  fs.writeFileSync(WORKSTREAMS_FILE, JSON.stringify(workstreams, null, 2));
}

// 生成ID
function generateId() {
  return `ws-${Date.now().toString(36)}`;
}

// 列出工作流
function listWorkstreams() {
  console.log(`\n${colors.cyan}═══════════════════════════════════════════${colors.reset}`);
  console.log(`${colors.cyan}GSD Workstreams${colors.reset}`);
  console.log(`${colors.cyan}═══════════════════════════════════════════${colors.reset}\n`);

  const workstreams = loadWorkstreams();
  const state = loadState();

  if (workstreams.length === 0) {
    console.log(`${colors.yellow}No workstreams found.${colors.reset}`);
    console.log(`\nUse "gsd-workstreams create <name>" to create a new workstream.`);
    return;
  }

  console.log(`${colors.yellow}Active Workstreams:${colors.reset}\n`);

  workstreams.forEach((ws, index) => {
    const isActive = ws.id === state.activeWorkstream;
    const statusColor = ws.status === 'completed' ? colors.green :
                       ws.status === 'paused' ? colors.yellow : colors.blue;
    const activeIndicator = isActive ? `${colors.green}*${colors.reset} ` : '  ';

    console.log(`${activeIndicator}${index + 1}. ${ws.name} ${statusColor}[${ws.status}]${colors.reset}`);
    console.log(`   ID: ${ws.id}`);
    console.log(`   Waves: ${ws.waves.length}`);
    console.log(`   Created: ${ws.createdAt}`);
    console.log();
  });

  console.log(`${colors.cyan}───────────────────────────────────────────${colors.reset}`);
  console.log(`Total: ${workstreams.length} workstreams`);
}

// 创建工作流
function createWorkstream(name, description = '') {
  console.log(`\n${colors.green}Creating workstream: ${name}${colors.reset}\n`);

  const workstreams = loadWorkstreams();

  // 检查是否已存在
  if (workstreams.some(ws => ws.name === name)) {
    console.log(`${colors.red}Error: Workstream "${name}" already exists.${colors.reset}`);
    return;
  }

  const newWorkstream = {
    id: generateId(),
    name,
    description,
    status: 'active',
    waves: [],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };

  workstreams.push(newWorkstream);
  saveWorkstreams(workstreams);

  // 设置为活动工作流
  const state = loadState();
  state.activeWorkstream = newWorkstream.id;
  saveState(state);

  console.log(`${colors.green}✓ Created workstream: ${name}${colors.reset}`);
  console.log(`  ID: ${newWorkstream.id}`);
  console.log(`\nUse "gsd-wave add --parallel 'task1,task2'" to add waves.`);
}

// 切换工作流
function switchWorkstream(nameOrId) {
  const workstreams = loadWorkstreams();

  const ws = workstreams.find(w => w.name === nameOrId || w.id === nameOrId);

  if (!ws) {
    console.log(`${colors.red}Error: Workstream "${nameOrId}" not found.${colors.reset}`);
    return;
  }

  const state = loadState();
  state.activeWorkstream = ws.id;
  saveState(state);

  console.log(`${colors.green}✓ Switched to workstream: ${ws.name}${colors.reset}`);
  console.log(`  Status: ${ws.status}`);
  console.log(`  Waves: ${ws.waves.length}`);
}

// 完成工作流
function completeWorkstream(nameOrId) {
  const workstreams = loadWorkstreams();
  const state = loadState();

  const wsIndex = workstreams.findIndex(w => w.name === nameOrId || w.id === nameOrId);

  if (wsIndex === -1) {
    console.log(`${colors.red}Error: Workstream "${nameOrId}" not found.${colors.reset}`);
    return;
  }

  const ws = workstreams[wsIndex];
  ws.status = 'completed';
  ws.updatedAt = new Date().toISOString();
  ws.completedAt = new Date().toISOString();

  saveWorkstreams(workstreams);

  // 如果是当前活动工作流，清除活动状态
  if (state.activeWorkstream === ws.id) {
    state.activeWorkstream = null;
    saveState(state);
  }

  console.log(`${colors.green}✓ Completed workstream: ${ws.name}${colors.reset}`);
  console.log(`  Total waves: ${ws.waves.length}`);
  console.log(`  Duration: ${Math.round((new Date(ws.completedAt) - new Date(ws.createdAt)) / 1000 / 60)} minutes`);
}

// 查看状态
function showStatus(verbose = false) {
  console.log(`\n${colors.cyan}═══════════════════════════════════════════${colors.reset}`);
  console.log(`${colors.cyan}GSD Workstreams Status${colors.reset}`);
  console.log(`${colors.cyan}═══════════════════════════════════════════${colors.reset}\n`);

  const state = loadState();
  const workstreams = loadWorkstreams();

  if (!state.activeWorkstream) {
    console.log(`${colors.yellow}No active workstream.${colors.reset}`);
    console.log(`\nUse "gsd-workstreams create <name>" to create a new workstream.`);
    return;
  }

  const ws = workstreams.find(w => w.id === state.activeWorkstream);

  if (!ws) {
    console.log(`${colors.red}Error: Active workstream not found.${colors.reset}`);
    return;
  }

  console.log(`${colors.green}Active Workstream: ${ws.name}${colors.reset}`);
  console.log(`  ID: ${ws.id}`);
  console.log(`  Status: ${ws.status}`);
  console.log(`  Created: ${ws.createdAt}`);

  if (ws.waves.length === 0) {
    console.log(`\n${colors.yellow}No waves defined.${colors.reset}`);
    console.log(`Use "gsd-wave add --parallel 'task1,task2'" to add waves.`);
    return;
  }

  console.log(`\n${colors.yellow}Waves:${colors.reset}\n`);

  ws.waves.forEach((wave, index) => {
    const statusColor = wave.status === 'completed' ? colors.green :
                       wave.status === 'running' ? colors.blue : colors.yellow;
    console.log(`  Wave ${index + 1} [${wave.type}] ${statusColor}[${wave.status}]${colors.reset}`);

    if (verbose) {
      wave.tasks.forEach((task, taskIndex) => {
        const taskStatus = task.status || 'pending';
        const taskColor = taskStatus === 'completed' ? colors.green :
                         taskStatus === 'running' ? colors.blue : colors.yellow;
        console.log(`    ${taskIndex + 1}. ${task.name} ${taskColor}[${taskStatus}]${colors.reset}`);
      });
    }

    if (wave.checkpoint) {
      console.log(`    Checkpoint: ${wave.checkpoint.status || 'pending'}`);
    }
    console.log();
  });
}

// 删除工作流
function deleteWorkstream(nameOrId) {
  const workstreams = loadWorkstreams();
  const state = loadState();

  const wsIndex = workstreams.findIndex(w => w.name === nameOrId || w.id === nameOrId);

  if (wsIndex === -1) {
    console.log(`${colors.red}Error: Workstream "${nameOrId}" not found.${colors.reset}`);
    return;
  }

  const ws = workstreams[wsIndex];

  // 如果是当前活动工作流，清除活动状态
  if (state.activeWorkstream === ws.id) {
    state.activeWorkstream = null;
    saveState(state);
  }

  workstreams.splice(wsIndex, 1);
  saveWorkstreams(workstreams);

  console.log(`${colors.yellow}✓ Deleted workstream: ${ws.name}${colors.reset}`);
}

// 添加波次
function addWave(type, tasksStr, requireUserApproval = false) {
  const state = loadState();
  const workstreams = loadWorkstreams();

  if (!state.activeWorkstream) {
    console.log(`${colors.red}Error: No active workstream.${colors.reset}`);
    console.log(`Use "gsd-workstreams create <name>" first.`);
    return;
  }

  const ws = workstreams.find(w => w.id === state.activeWorkstream);

  if (!ws) {
    console.log(`${colors.red}Error: Active workstream not found.${colors.reset}`);
    return;
  }

  const tasks = tasksStr.split(',').map(t => t.trim()).filter(t => t);

  const wave = {
    id: `wave-${Date.now().toString(36)}`,
    type: type === 'serial' ? 'serial' : 'parallel',
    tasks: tasks.map(t => ({
      id: `task-${Date.now().toString(36)}-${Math.random().toString(36).substr(2, 5)}`,
      name: t,
      status: 'pending'
    })),
    status: 'pending',
    checkpoint: {
      requireUserApproval,
      status: 'pending'
    }
  };

  ws.waves.push(wave);
  ws.updatedAt = new Date().toISOString();
  saveWorkstreams(workstreams);

  console.log(`${colors.green}✓ Added wave to ${ws.name}${colors.reset}`);
  console.log(`  Type: ${wave.type}`);
  console.log(`  Tasks: ${tasks.join(', ')}`);
  console.log(`  User Approval: ${requireUserApproval ? 'Required' : 'Auto'}`);
}

// 主入口
function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  const param = args[1];
  const options = {};

  // 解析选项
  for (let i = 2; i < args.length; i++) {
    if (args[i].startsWith('--')) {
      const key = args[i].slice(2);
      const value = args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : true;
      options[key] = value;
      if (value !== true) i++;
    }
  }

  switch (command) {
    case 'list':
    case 'ls':
      listWorkstreams();
      break;

    case 'create':
      if (!param) {
        console.log(`${colors.red}Error: Workstream name required.${colors.reset}`);
        console.log(`Usage: gsd-workstreams create <name>`);
        return;
      }
      createWorkstream(param, options.description || '');
      break;

    case 'switch':
      if (!param) {
        console.log(`${colors.red}Error: Workstream name or ID required.${colors.reset}`);
        console.log(`Usage: gsd-workstreams switch <name|id>`);
        return;
      }
      switchWorkstream(param);
      break;

    case 'complete':
    case 'done':
      if (!param) {
        console.log(`${colors.red}Error: Workstream name or ID required.${colors.reset}`);
        console.log(`Usage: gsd-workstreams complete <name|id>`);
        return;
      }
      completeWorkstream(param);
      break;

    case 'delete':
    case 'rm':
      if (!param) {
        console.log(`${colors.red}Error: Workstream name or ID required.${colors.reset}`);
        console.log(`Usage: gsd-workstreams delete <name|id>`);
        return;
      }
      deleteWorkstream(param);
      break;

    case 'status':
      showStatus(options.verbose || options.v);
      break;

    case 'wave':
      if (!param) {
        console.log(`${colors.red}Error: Wave action required.${colors.reset}`);
        console.log(`Usage: gsd-workstreams wave add --parallel "task1,task2"`);
        return;
      }
      if (param === 'add') {
        const tasks = options.parallel || options.serial || options.tasks;
        if (!tasks) {
          console.log(`${colors.red}Error: Tasks required.${colors.reset}`);
          console.log(`Usage: gsd-workstreams wave add --parallel "task1,task2"`);
          return;
        }
        addWave(options.serial ? 'serial' : 'parallel', tasks, options['require-approval']);
      }
      break;

    default:
      console.log(`
${colors.cyan}GSD Workstreams - 并行波次执行工作流管理${colors.reset}

Usage:
  node gsd-workstreams.js <command> [options]

Commands:
  list                    列出所有工作流
  create <name>           创建新工作流
  switch <name|id>        切换到指定工作流
  complete <name|id>      完成工作流
  delete <name|id>        删除工作流
  status                  查看当前工作流状态
  wave add                添加波次

Options:
  --parallel "tasks"      并行波次任务（逗号分隔）
  --serial "tasks"        串行波次任务（逗号分隔）
  --require-approval      检查点需要用户确认
  --verbose, -v           详细输出

Examples:
  gsd-workstreams create release-v1.0
  gsd-workstreams wave add --parallel "构建前端,构建后端,运行测试"
  gsd-workstreams wave add --serial "部署测试环境,验证测试环境,部署生产环境" --require-approval
  gsd-workstreams status --verbose
  gsd-workstreams complete release-v1.0
`);
  }
}

main();