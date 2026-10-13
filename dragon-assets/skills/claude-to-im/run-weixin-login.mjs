// Temporary wrapper script to run WeChat QR login
import { runWeixinLogin } from './src/weixin-login.js';
import { cpus } from 'node:os';

console.log('[run-weixin-login] Starting WeChat QR login...');

runWeixinLogin()
  .then((result) => {
    console.log('[run-weixin-login] Login complete:', result);
    process.exit(0);
  })
  .catch((err) => {
    console.error('[run-weixin-login] Error:', err instanceof Error ? err.message : String(err));
    process.exit(1);
  });

// Keep process alive with periodic heartbeat
const interval = setInterval(() => {
  // Write a heartbeat to stderr so we know the process is alive
  console.error('[run-weixin-login] Still polling...');
}, 30000);
