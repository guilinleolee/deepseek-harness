/**
 * SupermemoryBridge end-to-end test with extended timeouts.
 * Tests: recall (with model download), store, and re-call.
 */
import { SupermemoryBridge } from "./dist/supermemory-test.mjs";

const bridge = new SupermemoryBridge({ mcpServerPath: "D:/NODE/npm-global/node_modules/supermemory-mcp/dist/index.js" });
console.log("Starting SupermemoryBridge...");
await bridge.start();

// Wait longer for model download + initialization (up to 2 minutes for first run)
console.log("Waiting for MCP server + model initialization (up to 120s)...");
const MAX_INIT_WAIT = 120_000;
const POLL_INTERVAL = 5_000;
let waited = 0;
let serverReady = false;

while (waited < MAX_INIT_WAIT) {
  await new Promise(r => setTimeout(r, POLL_INTERVAL));
  waited += POLL_INTERVAL;
  // Try a lightweight ping
  try {
    const result = await bridge.search("ping", 1);
    console.log(`MCP server ready after ${waited / 1000}s`);
    serverReady = true;
    break;
  } catch (e) {
    console.log(`Still waiting... (${waited / 1000}s elapsed, last error: ${e.message})`);
  }
}

if (!serverReady) {
  console.error("FATAL: MCP server did not respond within 120s");
  bridge.stop();
  process.exit(1);
}

// Test 1: recall (no memories yet — should return "无相关记忆")
console.log("\n--- Test 1: recall() — empty DB ---");
const recall1 = await bridge.recall("测试查询");
console.log("recall1:", JSON.stringify(recall1, null, 2));

// Test 2: store a conversation
console.log("\n--- Test 2: store() ---");
const storeResult = await bridge.store(
  "用户: 帮我写一个Hello World程序",
  "助手: 当然可以！\n\n以下是Python版本:\n\nprint('Hello, World!')\n\nJavaScript版本:\nconsole.log('Hello, World!');",
  { type: "session", importance: 1, metadata: { channelType: "test", channelId: "999", userId: "test-user" } }
);
console.log("storeResult:", JSON.stringify(storeResult, null, 2));

// Test 3: recall after storing
console.log("\n--- Test 3: recall() — after store ---");
await new Promise(r => setTimeout(r, 1000));
const recall2 = await bridge.recall("Hello World程序");
console.log("recall2:", JSON.stringify(recall2, null, 2));

// Test 4: search
console.log("\n--- Test 4: search() ---");
const search1 = await bridge.search("Hello World");
console.log("search1:", JSON.stringify(search1, null, 2));

bridge.stop();
console.log("\nAll tests complete.");
process.exit(0);
