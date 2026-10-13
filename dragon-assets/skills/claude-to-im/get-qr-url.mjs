// Get QR code URL and print it
import { startLoginQr } from './src/adapters/weixin/weixin-api.js';

console.log('Fetching QR code URL from WeChat...');
const resp = await startLoginQr();
console.log('QR_URL:' + resp.qrcode_img_content);
console.log('QR_ID:' + resp.qrcode);
