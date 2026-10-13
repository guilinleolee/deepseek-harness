#!/usr/bin/env node
/**
 * GSD TDD Workflow Script
 *
 * 三阶段原子化TDD工作流脚本
 *
 * @version 1.0.0
 * @author Dragon Engine Team + GSD
 */

const { execSync } = require('child_process');
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
const STATE_FILE = path.join(process.cwd(), '.gsd-tdd-state.json');

// 测试框架检测
function detectTestFramework() {
  const cwd = process.cwd();

  if (fs.existsSync(path.join(cwd, 'jest.config.js')) ||
      fs.existsSync(path.join(cwd, 'jest.config.ts'))) {
    return { runner: 'jest', cmd: 'npx jest', ext: '.test.ts' };
  }

  if (fs.existsSync(path.join(cwd, 'vitest.config.ts')) ||
      fs.existsSync(path.join(cwd, 'vitest.config.js'))) {
    return { runner: 'vitest', cmd: 'npx vitest run', ext: '.test.ts' };
  }

  if (fs.existsSync(path.join(cwd, 'pytest.ini')) ||
      fs.existsSync(path.join(cwd, 'setup.cfg'))) {
    return { runner: 'pytest', cmd: 'python -m pytest', ext: '_test.py' };
  }

  if (fs.existsSync(path.join(cwd, 'go.mod'))) {
    return { runner: 'go', cmd: 'go test ./...', ext: '_test.go' };
  }

  if (fs.existsSync(path.join(cwd, 'Cargo.toml'))) {
    return { runner: 'cargo', cmd: 'cargo test', ext: '.rs' };
  }

  return { runner: 'unknown', cmd: 'npm test', ext: '.test.ts' };
}

// Git操作
function gitExec(command) {
  try {
    return execSync(command, { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] });
  } catch (error) {
    return { error: true, message: error.message };
  }
}

function isGitClean() {
  const result = gitExec('git status --porcelain');
  return result && !result.error && result.trim() === '';
}

function getCurrentBranch() {
  return gitExec('git branch --show-current').trim();
}

// 状态管理
function loadState() {
  try {
    if (fs.existsSync(STATE_FILE)) {
      return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
    }
  } catch (error) {
    // Ignore
  }
  return null;
}

function saveState(state) {
  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

function clearState() {
  if (fs.existsSync(STATE_FILE)) {
    fs.unlinkSync(STATE_FILE);
  }
}

// 运行测试
function runTests(testFile = null) {
  const framework = detectTestFramework();
  const cmd = testFile ? `${framework.cmd} ${testFile}` : framework.cmd;

  console.log(`\n${colors.cyan}Running tests: ${cmd}${colors.reset}\n`);

  try {
    const result = execSync(cmd, { encoding: 'utf8', stdio: 'inherit' });
    return { success: true };
  } catch (error) {
    return { success: false };
  }
}

// 提交变更
function commitChanges(phase, message) {
  const status = gitExec('git status --porcelain');

  if (!status || status.error || status.trim() === '') {
    console.log(`${colors.yellow}No changes to commit${colors.reset}`);
    return false;
  }

  gitExec('git add -A');

  const commitMsg = `${phase}: ${message}

GSD TDD Phase: ${phase}
Timestamp: ${new Date().toISOString()}
`;

  const result = gitExec(`git commit -m "${commitMsg.replace(/"/g, '\\"')}"`);

  if (result && !result.error) {
    console.log(`${colors.green}Committed: ${phase}: ${message}${colors.reset}`);
    return true;
  } else {
    console.log(`${colors.red}Commit failed: ${result?.message || 'Unknown error'}${colors.reset}`);
    return false;
  }
}

// RED阶段
function redPhase(testCase) {
  console.log(`\n${colors.red}═══════════════════════════════════════════${colors.reset}`);
  console.log(`${colors.red}RED Phase: Write Failing Test${colors.reset}`);
  console.log(`${colors.red}═══════════════════════════════════════════${colors.reset}\n`);

  const state = loadState() || {};
  state.phase = 'red';
  state.testCase = testCase;
  state.startTime = new Date().toISOString();
  saveState(state);

  console.log(`Test Case: ${testCase}`);
  console.log(`\n${colors.yellow}Instructions:${colors.reset}`);
  console.log('1. Write a failing test for the specified behavior');
  console.log('2. Run the test to confirm it fails');
  console.log('3. Use "gsd-tdd red-commit" when ready to commit');

  console.log(`\n${colors.cyan}Template:${colors.reset}`);
  console.log(`
describe('[Feature]', () => {
  it('${testCase}', async () => {
    // Arrange
    // Act
    // Assert
    expect(true).toBe(false); // Placeholder - should fail
  });
});
`);
}

function redCommit() {
  console.log(`\n${colors.red}Verifying RED phase...${colors.reset}\n`);

  // 运行测试，应该失败
  const result = runTests();

  if (result.success) {
    console.log(`${colors.red}Warning: Tests are passing. The test should fail to be valid RED phase.${colors.reset}`);
    console.log(`${colors.yellow}Please ensure the test fails for the right reason (feature not implemented).${colors.reset}`);
    return;
  }

  // 测试正确失败
  console.log(`${colors.green}Tests failed as expected (RED phase validated)${colors.reset}`);

  const state = loadState();
  const message = state?.testCase || 'add failing test';
  commitChanges('test', message);

  // 更新状态
  state.phase = 'red_complete';
  state.redCommitTime = new Date().toISOString();
  saveState(state);

  console.log(`\n${colors.green}RED phase complete. Use "gsd-tdd green" to proceed.${colors.reset}`);
}

// GREEN阶段
function greenPhase() {
  console.log(`\n${colors.green}═══════════════════════════════════════════${colors.reset}`);
  console.log(`${colors.green}GREEN Phase: Minimal Implementation${colors.reset}`);
  console.log(`${colors.green}═══════════════════════════════════════════${colors.reset}\n`);

  const state = loadState();

  if (!state || state.phase !== 'red_complete') {
    console.log(`${colors.red}Error: Must complete RED phase first${colors.reset}`);
    return;
  }

  state.phase = 'green';
  saveState(state);

  console.log(`\n${colors.yellow}Instructions:${colors.reset}`);
  console.log('1. Write minimal code to make tests pass');
  console.log('2. Do NOT add extra features or refactoring');
  console.log('3. Use "gsd-tdd green-commit" when tests pass');
}

function greenCommit() {
  console.log(`\n${colors.green}Verifying GREEN phase...${colors.reset}\n`);

  // 运行测试，应该通过
  const result = runTests();

  if (!result.success) {
    console.log(`${colors.red}Error: Tests are still failing. Fix the implementation first.${colors.reset}`);
    return;
  }

  console.log(`${colors.green}All tests passing!${colors.reset}`);

  const state = loadState();
  const message = state?.testCase || 'implement feature';
  commitChanges('feat', message);

  // 更新状态
  state.phase = 'green_complete';
  state.greenCommitTime = new Date().toISOString();
  saveState(state);

  console.log(`\n${colors.green}GREEN phase complete. Use "gsd-tdd refactor" to proceed.${colors.reset}`);
}

// REFACTOR阶段
function refactorPhase() {
  console.log(`\n${colors.magenta}═══════════════════════════════════════════${colors.reset}`);
  console.log(`${colors.magenta}REFACTOR Phase: Clean Up${colors.reset}`);
  console.log(`${colors.magenta}═══════════════════════════════════════════${colors.reset}\n`);

  const state = loadState();

  if (!state || state.phase !== 'green_complete') {
    console.log(`${colors.red}Error: Must complete GREEN phase first${colors.reset}`);
    return;
  }

  state.phase = 'refactor';
  saveState(state);

  console.log(`\n${colors.yellow}Instructions:${colors.reset}`);
  console.log('1. Clean up code (extract methods, improve names, remove duplication)');
  console.log('2. Do NOT change behavior');
  console.log('3. Use "gsd-tdd refactor-commit" when done');
}

function refactorCommit() {
  console.log(`\n${colors.magenta}Verifying REFACTOR phase...${colors.reset}\n`);

  // 运行测试，应该仍然通过
  const result = runTests();

  if (!result.success) {
    console.log(`${colors.red}Error: Tests failed! Refactoring broke something. Fix it.${colors.reset}`);
    return;
  }

  console.log(`${colors.green}All tests still passing after refactoring!${colors.reset}`);

  // 检查是否有变更
  if (isGitClean()) {
    console.log(`${colors.yellow}No changes to commit - refactoring did not change any files.${colors.reset}`);
  } else {
    const state = loadState();
    const message = state?.testCase || 'refactor code';
    commitChanges('refactor', message);
  }

  // 更新状态
  const state = loadState();
  state.phase = 'refactor_complete';
  state.refactorCommitTime = new Date().toISOString();
  saveState(state);

  console.log(`\n${colors.green}REFACTOR phase complete. TDD cycle finished!${colors.reset}`);
  console.log(`Use "gsd-tdd complete" to see the summary.`);
}

// 完成周期
function completeCycle() {
  console.log(`\n${colors.cyan}═══════════════════════════════════════════${colors.reset}`);
  console.log(`${colors.cyan}TDD Cycle Complete${colors.reset}`);
  console.log(`${colors.cyan}═══════════════════════════════════════════${colors.reset}\n`);

  const state = loadState();

  if (!state) {
    console.log(`${colors.red}No active TDD cycle found.${colors.reset}`);
    return;
  }

  console.log(`Feature: ${state.testCase || 'Unknown'}`);
  console.log(`\n${colors.yellow}Timeline:${colors.reset}`);
  console.log(`  Started: ${state.startTime || 'N/A'}`);
  console.log(`  RED: ${state.redCommitTime || 'N/A'}`);
  console.log(`  GREEN: ${state.greenCommitTime || 'N/A'}`);
  console.log(`  REFACTOR: ${state.refactorCommitTime || 'N/A'}`);

  // 显示提交历史
  console.log(`\n${colors.yellow}Commit History:${colors.reset}`);
  gitExec('git log --oneline -5');

  // 清理状态
  clearState();
  console.log(`\n${colors.green}TDD cycle state cleared. Ready for new cycle.${colors.reset}`);
}

// 查看状态
function showStatus() {
  console.log(`\n${colors.cyan}GSD TDD Status${colors.reset}\n`);

  const state = loadState();

  if (!state) {
    console.log(`${colors.yellow}No active TDD cycle. Use "gsd-tdd start <feature>" to begin.${colors.reset}`);
    return;
  }

  console.log(`Current Phase: ${state.phase}`);
  console.log(`Test Case: ${state.testCase}`);
  console.log(`Started: ${state.startTime}`);

  // 显示Git状态
  console.log(`\n${colors.yellow}Git Status:${colors.reset}`);
  gitExec('git status -s');
}

// 主入口
function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  const param = args[1];

  switch (command) {
    case 'start':
      redPhase(param || 'new feature');
      break;

    case 'red':
      redPhase(param || 'new test');
      break;

    case 'red-commit':
      redCommit();
      break;

    case 'green':
      greenPhase();
      break;

    case 'green-commit':
      greenCommit();
      break;

    case 'refactor':
      refactorPhase();
      break;

    case 'refactor-commit':
      refactorCommit();
      break;

    case 'verify':
      runTests();
      break;

    case 'status':
      showStatus();
      break;

    case 'complete':
      completeCycle();
      break;

    case 'abort':
      clearState();
      console.log(`${colors.yellow}TDD cycle aborted.${colors.reset}`);
      break;

    default:
      console.log(`
${colors.cyan}GSD TDD Workflow${colors.reset}

Usage:
  node gsd-tdd.js start <feature>    Start new TDD cycle
  node gsd-tdd.js red <test-case>    RED phase: create failing test
  node gsd-tdd.js red-commit         Commit failing test
  node gsd-tdd.js green              GREEN phase: implement code
  node gsd-tdd.js green-commit       Commit implementation
  node gsd-tdd.js refactor           REFACTOR phase: clean up
  node gsd-tdd.js refactor-commit    Commit refactoring
  node gsd-tdd.js verify             Run tests
  node gsd-tdd.js status             Show current status
  node gsd-tdd.js complete           Complete and summarize
  node gsd-tdd.js abort              Abort current cycle
`);
  }
}

main();