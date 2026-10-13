#!/usr/bin/env node
/**
 * =============================================================
 * OpenClaw Zero-Polling Integration Test Suite
 * =============================================================
 * Tests the OpenClaw + Claude Code + Dragon Engine integration
 *
 * Tests:
 * - Hook script execution
 * - State file creation
 * - Deduplication mechanism
 * - Lock acquisition/release
 * - Dragon Engine queue sync
 *
 * Author: Dragon Engine Team
 * Created: 2026-02-25
 * =============================================================
 */

const fs = require('fs').promises;
const path = require('path');
const { execSync } = require('child_process');

// Test configuration
const CONFIG = {
  stateDir: path.join(process.env.HOME || process.env.USERPROFILE, '.openclaw/workspace/state'),
  hookScript: path.join(process.env.HOME || process.env.USERPROFILE, '.claude/hooks/openclaw-zero-polling-hook.js'),
  testTimeout: 5000,
};

// Color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

// Test result tracker
const testResults = {
  passed: 0,
  failed: 0,
  skipped: 0,
};

// Test helper
async function test(name, fn) {
  try {
    log(`\n🧪 Testing: ${name}`, 'blue');
    await fn();
    testResults.passed++;
    log(`✅ PASSED: ${name}`, 'green');
  } catch (err) {
    testResults.failed++;
    log(`❌ FAILED: ${name}`, 'red');
    log(`   Error: ${err.message}`, 'red');
  }
}

// Cleanup helper
async function cleanup() {
  const files = ['cc-result.json', 'cc-complete.lock', 'cc-task.json'];

  for (const file of files) {
    try {
      await fs.unlink(path.join(CONFIG.stateDir, file));
    } catch {
      // File doesn't exist, ignore
    }
  }
}

// Test 1: State directory exists
async function testStateDirExists() {
  const stats = await fs.stat(CONFIG.stateDir);
  if (!stats.isDirectory()) {
    throw new Error('State directory is not a directory');
  }
}

// Test 2: Hook script exists and is executable
async function testHookScriptExists() {
  const stats = await fs.stat(CONFIG.hookScript);
  if (!stats.isFile()) {
    throw new Error('Hook script is not a file');
  }
}

// Test 3: Hook script creates result file
async function testHookCreatesResult() {
  const testData = JSON.stringify({
    sessionId: 'test-session-' + Date.now(),
    transcriptPath: '/path/to/transcript',
    cwd: process.cwd(),
    hookEventName: 'Stop',
  });

  // Import and run hook
  const hook = require(CONFIG.hookScript);
  await hook(testData);

  // Check if result file was created
  const resultPath = path.join(CONFIG.stateDir, 'cc-result.json');
  const stats = await fs.stat(resultPath);

  if (!stats.isFile()) {
    throw new Error('Result file was not created');
  }

  // Verify result content
  const result = JSON.parse(await fs.readFile(resultPath, 'utf8'));
  if (result.session_id !== JSON.parse(testData).sessionId) {
    throw new Error('Result file has incorrect session ID');
  }
}

// Test 4: Deduplication mechanism
async function testDeduplication() {
  const testData = JSON.stringify({
    sessionId: 'test-session-' + Date.now(),
    transcriptPath: '/path/to/transcript',
    cwd: process.cwd(),
    hookEventName: 'Stop',
  });

  const hook = require(CONFIG.hookScript);

  // First call should create result
  await hook(testData);

  const resultPath = path.join(CONFIG.stateDir, 'cc-result.json');
  const firstStats = await fs.stat(resultPath);

  // Second call should be deduplicated
  await hook(testData);

  const secondStats = await fs.stat(resultPath);

  // File should not have been modified
  if (secondStats.mtimeMs !== firstStats.mtimeMs) {
    throw new Error('Deduplication failed - file was modified');
  }
}

// Test 5: Lock mechanism
async function testLockMechanism() {
  const lockPath = path.join(CONFIG.stateDir, 'cc-complete.lock');

  // Create a manual lock
  await fs.writeFile(lockPath, '99999');

  const testData = JSON.stringify({
    sessionId: 'test-session-' + Date.now(),
    transcriptPath: '/path/to/transcript',
    cwd: process.cwd(),
    hookEventName: 'Stop',
  });

  const hook = require(CONFIG.hookScript);

  // Hook should skip due to lock
  await hook(testData);

  // Lock should still exist
  const stats = await fs.stat(lockPath);
  if (!stats.isFile()) {
    throw new Error('Lock file was removed');
  }
}

// Test 6: Dragon Engine adapter
async function testDragonEngineAdapter() {
  const adapterPath = path.join(
    process.env.HOME || process.env.USERPROFILE,
    '.claude/hooks/openclaw-dragon-engine-adapter.js'
  );

  const adapter = require(adapterPath);

  // Create test task
  const dragonTask = adapter.createDragonTask({
    session_id: 'test-session-' + Date.now(),
    hook_event: 'Stop',
    task: 'Implement user authentication',
    work_dir: '/path/to/project',
    status: 'completed',
    completed_at: new Date().toISOString(),
    duration: '5m30s',
    transcript_path: '/path/to/transcript',
    file_tree: 'file1.js\nfile2.js',
  });

  if (dragonTask.type !== 'build') {
    throw new Error(`Expected task type 'build', got '${dragonTask.type}'`);
  }

  if (dragonTask.agent !== '03builder') {
    throw new Error(`Expected agent '03builder', got '${dragonTask.agent}'`);
  }

  if (dragonTask.priority !== 'normal') {
    throw new Error(`Expected priority 'normal', got '${dragonTask.priority}'`);
  }
}

// Test 7: Task type inference
async function testTaskTypeInference() {
  const adapterPath = path.join(
    process.env.HOME || process.env.USERPROFILE,
    '.claude/hooks/openclaw-dragon-engine-adapter.js'
  );

  const adapter = require(adapterPath);

  const testCases = [
    { task: 'Analyze performance bottleneck', expectedType: 'analysis' },
    { task: 'Design system architecture', expectedType: 'architecture' },
    { task: 'Implement new feature', expectedType: 'build' },
    { task: 'Write unit tests', expectedType: 'test' },
    { task: 'Security audit', expectedType: 'security' },
    { task: 'Code review', expectedType: 'review' },
    { task: 'Write documentation', expectedType: 'documentation' },
    { task: 'Deploy to production', expectedType: 'publish' },
  ];

  for (const testCase of testCases) {
    const dragonTask = adapter.createDragonTask({
      session_id: 'test',
      hook_event: 'Stop',
      task: testCase.task,
      work_dir: '/path',
      status: 'completed',
      completed_at: new Date().toISOString(),
      duration: '1m',
      transcript_path: '/path',
      file_tree: '',
    });

    if (dragonTask.type !== testCase.expectedType) {
      throw new Error(
        `Task "${testCase.task}" inferred as "${dragonTask.type}", expected "${testCase.expectedType}"`
      );
    }
  }
}

// Main test runner
async function runTests() {
  log('🐉 OpenClaw Zero-Polling Integration Test Suite', 'blue');
  log('=' .repeat(50), 'blue');

  // Ensure state directory exists
  await fs.mkdir(CONFIG.stateDir, { recursive: true });

  // Run tests
  await test('State directory exists', testStateDirExists);
  await test('Hook script exists', testHookScriptExists);
  await test('Hook creates result file', testHookCreatesResult);
  await cleanup();
  await test('Deduplication mechanism', testDeduplication);
  await cleanup();
  await test('Lock mechanism', testLockMechanism);
  await cleanup();
  await test('Dragon Engine adapter', testDragonEngineAdapter);
  await test('Task type inference', testTaskTypeInference);

  // Final cleanup
  await cleanup();

  // Print summary
  log('\n' + '='.repeat(50), 'blue');
  log('Test Summary:', 'blue');
  log(`  ✅ Passed: ${testResults.passed}`, 'green');
  log(`  ❌ Failed: ${testResults.failed}`, testResults.failed > 0 ? 'red' : 'green');
  log(`  ⏭️  Skipped: ${testResults.skipped}`, 'yellow');
  log('=' .repeat(50), 'blue');

  // Exit with appropriate code
  process.exit(testResults.failed > 0 ? 1 : 0);
}

// Run tests
runTests().catch(err => {
  log(`\n💥 Test suite failed: ${err.message}`, 'red');
  console.error(err);
  process.exit(1);
});
