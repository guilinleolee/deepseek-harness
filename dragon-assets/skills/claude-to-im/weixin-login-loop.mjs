// WeChat login: fetch QR, save HTML, poll status
import fs from 'node:fs';
import path from 'node:path';
import QRCode from 'qrcode';
import { startLoginQr } from './src/adapters/weixin/weixin-api.js';
import { listWeixinAccounts, upsertWeixinAccount } from './src/weixin-store.js';
import { loadConfig } from './src/config.js';
import { DEFAULT_BASE_URL, DEFAULT_CDN_BASE_URL } from './src/adapters/weixin/weixin-types.js';

const RUNTIME_DIR = path.join(process.env.CTI_HOME || path.join(process.env.HOME || 'C:\\Users\\li', '.claude-to-im'), 'runtime');
const HTML_PATH = path.join(RUNTIME_DIR, 'weixin-login.html');

function escapeHtml(t) {
  return t.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
}

function buildHtml(qrSvg, qrId) {
  return `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/><title>WeChat Login</title><style>
body{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Helvetica Neue",sans-serif;background:linear-gradient(180deg,#f6fbf8 0%,#eef5ff 100%);display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
.card{background:rgba(255,255,255,0.95);border-radius:24px;padding:40px;max-width:500px;text-align:center;box-shadow:0 20px 50px rgba(36,82,167,0.12)}
h1{font-size:24px;margin:0 0 16px;color:#14213d}
p{color:#5b6b86;line-height:1.6;margin:8px 0}
ol{text-align:left;margin:20px 0;padding-left:24px;color:#14213d}
li{margin:8px 0}
.qr{margin:24px 0;display:flex;justify-content:center}
.qr svg,.qr img{width:260px;height:260px;border-radius:16px;padding:12px;background:white;border:1px solid rgba(20,33,61,0.08)}
.status{font-weight:bold;padding:12px;border-radius:8px;margin-top:16px}
.waiting{background:#fff3cd;color:#856404}
.scanned{background:#d4edda;color:#155724}
.success{background:#d1ecf1;color:#0c5460}
</style></head><body>
<div class="card">
  <h1>微信扫码登录 Claude-to-IM</h1>
  <p>用手机微信扫描下方二维码，确认授权</p>
  <div class="qr" id="qrcode">${qrSvg}</div>
  <div class="status waiting" id="status">等待扫码...</div>
  <ol>
    <li>打开手机微信扫一扫</li>
    <li>扫描上方二维码</li>
    <li>在手机上点"确认登录"</li>
    <li>等待下方状态变为"登录成功"</li>
  </ol>
  <p>QR ID: <code id="qr-id">${escapeHtml(qrId)}</code></p>
</div>
<script>
  // Auto-refresh status display (the actual polling happens in CLI)
  let dotCount = 0;
  function animate() {
    const el = document.getElementById('status');
    if (el.textContent === '等待扫码...' || el.textContent.startsWith('等待')) {
      dotCount = (dotCount + 1) % 4;
      el.textContent = '等待扫码' + '.'.repeat(dotCount);
    }
    setTimeout(animate, 1000);
  }
  animate();
</script>
</body></html>`;
}

async function saveHtml(qrSvg, qrId) {
  fs.mkdirSync(RUNTIME_DIR, { recursive: true });
  fs.writeFileSync(HTML_PATH, buildHtml(qrSvg, qrId), 'utf-8');
}

async function run() {
  const config = loadConfig();
  console.log('[weixin-login] Fetching QR code...');

  const resp = await startLoginQr();
  console.log('[weixin-login] QR ID:', resp.qrcode);
  console.log('[weixin-login] QR URL:', resp.qrcode_img_content);

  // Generate SVG and save HTML
  const svg = await QRCode.toString(resp.qrcode_img_content, {
    type: 'svg', errorCorrectionLevel: 'M', margin: 0, width: 260,
  });
  await saveHtml(svg, resp.qrcode);
  console.log('[weixin-login] HTML saved:', HTML_PATH);
  console.log('[weixin-login] Open this URL in your browser:');
  console.log('[weixin-login]   file:///C:/Users/li/.claude-to-im/runtime/weixin-login.html');
  console.log('[weixin-login] Scan the QR within ~20 seconds!');

  // QR status polling: use a SHORT timeout (3s) instead of the default 40s long-poll.
  // The QR code expires in ~20s, so 40s timeout only gives 1 poll attempt before expiry.
  // Short timeout + fast polling (~1s) maximizes attempts in the QR's ~20s window.
  const QR_POLL_TIMEOUT_MS = 3000; // 3 seconds — fast return to maximize poll count
  const POLL_INTERVAL_MS = 1000;   // 1 second between polls when waiting
  const QR_TTL_SECONDS = 20;       // QR expires in ~20 seconds on the server
  let scanned = false;
  let refreshCount = 0;
  const MAX_REFRESH = 5;
  const baseUrl = (config.weixinBaseUrl || DEFAULT_BASE_URL).replace(/\/+$/, '');

  // Helper: poll QR status with a SHORT timeout (bypass 40s pollLoginQrStatus)
  async function pollQrStatus(qrcode, timeoutMs) {
    const url = `${baseUrl}/ilink/bot/get_qrcode_status?qrcode=${encodeURIComponent(qrcode)}`;
    const res = await fetch(url, {
      method: 'GET',
      signal: AbortSignal.timeout(timeoutMs),
    });
    if (!res.ok) throw new Error(`QR poll failed: ${res.status}`);
    return res.json();
  }

  // Helper: long-poll QR status (blocking, for after-scan)
  async function longPollQrStatus(qrcode) {
    const url = `${baseUrl}/ilink/bot/get_qrcode_status?qrcode=${encodeURIComponent(qrcode)}`;
    const res = await fetch(url, {
      method: 'GET',
      signal: AbortSignal.timeout(40_000),
    });
    if (!res.ok) throw new Error(`QR long-poll failed: ${res.status}`);
    return res.json();
  }

  // Track dot count for countdown display
  let dotCount = 0;
  let qrCreatedAt = Date.now();

  while (true) {
    const elapsed = Math.floor((Date.now() - qrCreatedAt) / 1000);
    const remaining = Math.max(0, QR_TTL_SECONDS - elapsed);

    // Poll with a SHORT timeout so we don't block for 40s and miss the QR expiry window
    let pollResp;
    try {
      pollResp = await pollQrStatus(resp.qrcode, QR_POLL_TIMEOUT_MS);
    } catch (e) {
      if (e.name === 'TimeoutError') {
        // Timeout = server hasn't responded = user probably hasn't acted yet
        // Immediately poll again (no delay, to maximize attempts in the ~20s QR window)
      } else {
        console.error('[weixin-login] Poll error:', e.message);
      }
      continue;
    }

    const status = pollResp.status;

    if (status === 'wait') {
      if (!scanned) {
        dotCount = (dotCount + 1) % 4;
        const dots = '.'.repeat(dotCount + 1);
        // Clear line and show countdown
        process.stdout.write(`\r[weixin-login] Waiting for scan  ${dots}  QR expires in ~${remaining}s    `);
      }
      // Short timeout = fast return → poll again quickly (maximize attempts in QR's ~20s life)
      await new Promise(r => setTimeout(r, POLL_INTERVAL_MS));
    } else if (status === 'scaned') {
      if (!scanned) { console.log('\n[weixin-login] QR scanned! Please confirm in WeChat.'); scanned = true; }
      // After scan, switch to long-poll mode: block until server has new status
      // The server will hold this request until user confirms or QR expires
      while (true) {
        try {
          const lpResp = await longPollQrStatus(resp.qrcode);
          if (lpResp.status === 'confirmed') {
            if (!lpResp.bot_token || !lpResp.ilink_bot_id) {
              console.error('[weixin-login] Confirmed but no credentials returned!');
              process.exit(1);
            }
            const accountId = lpResp.ilink_bot_id.replace(/[@.]/g, '-');
            upsertWeixinAccount({
              accountId,
              userId: lpResp.ilink_user_id || '',
              baseUrl: config.weixinBaseUrl || lpResp.baseurl || DEFAULT_BASE_URL,
              cdnBaseUrl: config.weixinCdnBaseUrl || DEFAULT_CDN_BASE_URL,
              token: lpResp.bot_token,
              name: accountId,
              enabled: true,
            });
            console.log('\n[weixin-login] Login SUCCESS! Account: ' + accountId);
            console.log('[weixin-login] Now run: bash scripts/daemon.sh start');
            process.exit(0);
          } else if (lpResp.status === 'expired') {
            console.log('\n[weixin-login] QR expired after scan. Please refresh and try again.');
            process.exit(1);
          }
          // scaned again — keep waiting
          await new Promise(r => setTimeout(r, 3000));
        } catch (e) {
          if (e.name === 'TimeoutError') {
            // Long-poll timed out — just try again
          } else {
            console.error('[weixin-login] Long-poll error:', e.message);
          }
        }
      }
    } else if (status === 'confirmed') {
      if (!pollResp.bot_token || !pollResp.ilink_bot_id) {
        console.error('[weixin-login] Confirmed but no credentials returned!');
        process.exit(1);
      }
      const accountId = pollResp.ilink_bot_id.replace(/[@.]/g, '-');
      upsertWeixinAccount({
        accountId,
        userId: pollResp.ilink_user_id || '',
        baseUrl: config.weixinBaseUrl || pollResp.baseurl || DEFAULT_BASE_URL,
        cdnBaseUrl: config.weixinCdnBaseUrl || DEFAULT_CDN_BASE_URL,
        token: pollResp.bot_token,
        name: accountId,
        enabled: true,
      });
      console.log('\n[weixin-login] Login SUCCESS! Account: ' + accountId);
      console.log('[weixin-login] Now run: bash scripts/daemon.sh start');
      process.exit(0);
    } else if (status === 'expired') {
      process.stdout.write('\n'); // newline after countdown
      if (refreshCount >= MAX_REFRESH) {
        console.error('[weixin-login] QR expired too many times. Run again.');
        process.exit(1);
      }
      refreshCount++;
      console.log('[weixin-login] QR expired, refreshing (' + refreshCount + '/' + MAX_REFRESH + ')...');
      const r = await startLoginQr();
      resp.qrcode = r.qrcode; // Update with new QR ID!
      qrCreatedAt = Date.now(); // Reset timer for new QR
      dotCount = 0;
      const newSvg = await QRCode.toString(r.qrcode_img_content, {
        type: 'svg', errorCorrectionLevel: 'M', margin: 0, width: 260,
      });
      await saveHtml(newSvg, r.qrcode);
      scanned = false;
      // Immediately start polling (no delay) to maximize remaining time
      continue;
    }
  }
}

run().catch(e => {
  console.error('[weixin-login] Error:', e.message);
  process.exit(1);
});
