/**
 * 卡巴格企业平台 · 员工个人中心与邀请注册（栏目规划 v2 阶段 10，门户员工侧）。
 *
 * 挂在网关裸 portal 主机上的公开/自服务路由（gateway.mjs 调用本模块）：
 * - GET  /me                 个人中心（已认证）：资料卡 / 改密 / 本人当月用量 /
 *                            最近登录 + 下线所有设备。admin/auditor 同样可用
 *                            （不重定向：两类角色同样有本人用量与设备管理需求，
 *                            页顶提供「返回管理台」），employee 为主要受众。
 * - POST /api/me/password    改密：校验当前密码 + 新密码策略 → 重哈希 +
 *                            tokenEpoch+1 全端下线（需重新登录）。审计
 *                            member.self_password_change（ok/fail 都留痕，
 *                            detail 只含原因码，绝不含密码）。
 * - POST /api/me/revoke-all  下线所有设备（tokenEpoch+1）。审计 auth.revoke_all。
 * - GET  /register?code=     免登录注册页：展示邀请预设（部门/角色/有效期）。
 * - POST /api/register       免登录注册端点：按 IP 复用登录速率限制参数
 *                            （security.json，独立计数桶，daemon 生命周期内
 *                            内存累计）；code 常数时间校验 → 建号（addAccount
 *                            同一函数：白名单+密码策略+scrypt）→ 签发虚拟钥匙
 *                            → 标记邀请已用 → 同步该实例 tool-policy（阶段 9）
 *                            → 审计 member.register（fail detail 只含原因码）。
 * - GET  /login              登录页直达（已认证按角色跳 /me 或入口页）。
 *
 * 隐私红线不变：审计与页面只含元数据，永不落密码/密钥/会话正文。
 */
import { readFileSync } from 'node:fs'
import { join } from 'node:path'

import { addAccount, loadAccounts, revokeAccountTokens, setPassword, verifyPassword } from './gateway.mjs'
import { issueVkey } from './relay.mjs'
import { auditAppend, auditQuery, clientIp } from './audit.mjs'
import { checkPasswordPolicy, createLoginRateGuard, loadSecurityConfig } from './security.mjs'
import { fmtPoints } from './quotas.mjs'
import { syncInstanceHome } from './toolpolicy.mjs'
import { consumeInvite, inviteRejectMessage, validateInvite } from './invites.mjs'
import { clearTwofa, confirmSecret, generateTotpSecret, getTwofaRecord, otpauthUrl, setPendingSecret } from './totp.mjs'

const ROLE_LABELS = { admin: '管理员', auditor: '审计员', employee: '成员' }

const esc = (s) => String(s)
  .replace(/&/g, '&amp;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;')
  .replace(/'/g, '&#39;')

const PORTAL_CSS = `:root{--line:#e5e7eb;--text:#1f2937;--muted:#6b7280;--accent:#2563eb;--green:#059669;--red:#dc2626}
*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
color:var(--text);background:#f6f7f9;display:flex;justify-content:center;padding:2.2rem 1rem}
.wrap{width:100%;max-width:760px}
.head{display:flex;align-items:baseline;justify-content:space-between;margin-bottom:1rem}
.head h1{margin:0;font-size:1.35rem}.head a{font-size:.88rem}
.card{background:#fff;border:1px solid var(--line);border-radius:10px;padding:1.1rem 1.3rem;margin-bottom:1rem}
.card h2{margin:0 0 .7rem;font-size:1rem;color:#111827}
.kv{display:grid;grid-template-columns:96px 1fr;gap:.45rem .8rem;font-size:.92rem}
.kv .k{color:var(--muted)}
.bar{width:220px;height:6px;border-radius:3px;background:#e5e7eb;overflow:hidden;vertical-align:middle;display:inline-block}
.bar i{display:block;height:100%;border-radius:3px;background:var(--green)}
input,button,select{font-family:inherit}
label{display:block;font-size:.82rem;color:var(--muted);margin:.55rem 0 .2rem}
input{width:100%;padding:.5rem .6rem;border-radius:6px;border:1px solid #d1d5db;background:#fff;color:var(--text)}
button{margin-top:.9rem;padding:.5rem 1rem;border-radius:6px;border:none;background:var(--accent);color:#fff;font-weight:600;cursor:pointer}
button.danger{background:#fff;border:1px solid #fecaca;color:var(--red)}
.msg{margin-top:.6rem;font-size:.86rem;color:var(--red);min-height:1.2em}
.okmsg{color:var(--green)}
table{border-collapse:collapse;width:100%;margin-top:.3rem}
td,th{border:1px solid var(--line);padding:.42rem .6rem;font-size:.86rem;text-align:left}
th{color:var(--muted);font-weight:500;font-size:.76rem;background:#f9fafb}
.chip{display:inline-block;padding:.1rem .5rem;border-radius:999px;font-size:.74rem;background:#fffbeb;color:#b45309;border:1px solid #fde68a}
.mut{color:var(--muted);font-size:.8rem}
.invite{background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:.9rem 1.2rem;margin-bottom:1rem;font-size:.92rem}`

const page = (title, body) => `<!doctype html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>卡巴格 · ${title}</title><style>${PORTAL_CSS}</style></head><body><div class="wrap">${body}</div></body></html>`

function json(res, status, value) {
  // 已响应时吞掉 writeHead 异常（对齐 console.mjs：请求必被响应，二次响应无害化）。
  try {
    res.writeHead(status, { 'content-type': 'application/json; charset=utf-8' })
    res.end(JSON.stringify(value))
  } catch { /* 已响应 */ }
}

function readJsonBody(req) {
  return new Promise((resolveBody) => {
    let raw = ''
    req.on('data', (c) => { raw += c })
    req.on('end', () => {
      try { resolveBody(JSON.parse(raw || '{}')) } catch { resolveBody({}) }
    })
  })
}

/** POST 同源校验（配合 SameSite=Strict 的双重 CSRF 防线，与管理台一致）。 */
function sameOrigin(req) {
  const origin = req.headers.origin
  if (origin === undefined) return true
  try {
    return new URL(origin).host === (req.headers.host ?? '')
  } catch {
    return false
  }
}

const monthKeyNow = () => {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
}

const usageEntryOf = (dataDir, account) => {
  try {
    const usage = JSON.parse(readFileSync(join(dataDir, 'usage.json'), 'utf8'))
    return usage.months?.[monthKeyNow()]?.[account] ?? {}
  } catch {
    return {}
  }
}

/** 本人当月用量区块：点数口径（旧制 tokens 账号按旧口径并标注）。 */
function usageHtml(record, dataDir) {
  const entry = usageEntryOf(dataDir, record.account)
  const usedPoints = entry.points ?? 0
  const usedTokens = (entry.tokensIn ?? 0) + (entry.tokensOut ?? 0)
  const bar = (used, quota) => {
    const pct = Math.min(100, Math.round((used / Math.max(1, quota)) * 100))
    const color = pct >= 100 ? 'var(--red)' : pct >= 70 ? '#d97706' : 'var(--green)'
    return `<span class="bar"><i style="width:${pct}%;background:${color}"></i></span> <span style="font-size:.88rem">${fmtPoints(used)}/${fmtPoints(quota)}</span>`
  }
  let line
  if (Number.isFinite(record.monthlyPoints)) {
    line = `${bar(usedPoints, record.monthlyPoints)} <span class="mut">点数</span>`
  } else if (Number.isFinite(record.monthlyTokens)) {
    line = `${bar(usedTokens, record.monthlyTokens)} <span class="mut">tokens</span> <span class="chip">旧制</span>`
  } else {
    line = `${fmtPoints(usedPoints)} 点 <span class="chip" style="background:#f9fafb;color:var(--muted);border:1px solid var(--line)">不限额度</span>`
  }
  return `<div class="card"><h2>本月用量（${monthKeyNow()} · 服务器本地时区）</h2>
<div class="kv"><span class="k">额度消耗</span><span>${line}</span>
<span class="k">请求次数</span><span>${entry.requests ?? 0}</span></div></div>`
}

/** 两步验证卡片（阶段 11A + P1-1 三态）：未绑定→开始绑定；待确认→密钥+确认码；已启用→关闭；损坏→管理员救援提示。 */
function twofaCard(record, dataDir, twofaKey) {
  const rec = getTwofaRecord(dataDir, twofaKey, record.account)
  let body
  if (rec.state === 'broken') {
    body = `<p style="color:var(--red);margin:.2rem 0">⚠ 两步验证配置损坏（如认证器密钥仍有效，登录将提示联系管理员）。请让管理员在管理台「成员与额度」页执行「重置2FA」后重新绑定。</p>`
  } else if (rec.state === 'ok' && rec.enabled) {
    body = `<p style="color:var(--green);margin:.2rem 0">✅ 已启用（${esc((rec.confirmedAt ?? '').replace('T', ' ').slice(0, 16) || '时间未知')} 确认）。登录需输入认证器 6 位验证码。</p>
<form onsubmit="tfaDisable(event)"><label>当前密码（确认后关闭）</label><input type="password" id="tfapw" autocomplete="current-password" required><div class="msg" id="tfamsg"></div><button class="danger">关闭两步验证</button></form>`
  } else if (rec.state === 'ok' && rec.pending) {
    const link = otpauthUrl({ secret: rec.secret, account: record.account })
    body = `<p style="margin:.2rem 0">绑定进行中：在认证器中手工添加密钥，或打开链接。</p>
<p><code style="word-break:break-all">${esc(rec.secret)}</code></p>
<p class="mut" style="word-break:break-all"><a href="${esc(link)}">${esc(link)}</a></p>
<form onsubmit="tfaConfirm(event)"><label>输入认证器显示的 6 位验证码确认</label><input id="tfacode" inputmode="numeric" maxlength="6" required><div class="msg" id="tfamsg"></div><button>确认绑定</button></form>`
  } else {
    body = `<p style="margin:.2rem 0">尚未启用。绑定后登录需输入认证器 6 位验证码（防密码泄露后被直接登录）。</p>
<button class="ghost" onclick="tfaSetup()">开始绑定</button>
<div id="tfasetup" style="display:none">
<p style="margin:.5rem 0 .2rem">在认证器中手工添加以下密钥（base32）：</p>
<p><code id="tfasec" style="word-break:break-all"></code></p>
<p class="mut" style="word-break:break-all"><a id="tfalink" href="#"></a></p>
<form onsubmit="tfaConfirm(event)"><label>输入认证器显示的 6 位验证码确认</label><input id="tfacode" inputmode="numeric" maxlength="6" required><div class="msg" id="tfamsg"></div><button>确认绑定</button></form>
</div>`
  }
  return `<div class="card"><h2>两步验证（TOTP）</h2>${body}</div>`
}

/** 个人中心页：资料 / 用量 / 改密 / 设备 / 两步验证。 */
function mePage({ record, dataDir, manifest, twofaKey }) {
  const spec = manifest.instances.find((s) => s.id === record.instanceId)
  const workspaceUrl = spec !== undefined
    ? `http://${spec.id}.${(manifest.gatewayHost ?? 'localhost').split(':')[0]}:${manifest.portalPort}/`
    : null
  const backLink = record.role === 'employee'
    ? (workspaceUrl !== null ? `<a href="${esc(workspaceUrl)}">进入我的工作区 →</a>` : '')
    : '<a href="/console">返回管理台 →</a>'
  // 最近登录用 actor 全等（exact）过滤：子串账号（a@x 与 ba@x）不会混入。
  const devices = auditQuery({ actionPrefix: 'auth.login_success', actor: record.account, limit: 5, exact: true })
  // 软强制横幅（阶段 11A）：角色被要求绑定但尚未启用——仅提醒，不硬锁
  // （硬强制属阶段 11b，避免管理员误配置把自己锁死）。
  const twofaRec = getTwofaRecord(dataDir, twofaKey, record.account)
  const twoFaRequired = loadSecurityConfig(dataDir).require2faRoles.includes(record.role)
  const twofaEnabledOk = twofaRec.state === 'ok' && twofaRec.enabled
  const enrollBanner = twoFaRequired && !twofaEnabledOk
    ? `<div class="invite">⚠ 管理员已要求「${esc(ROLE_LABELS[record.role] ?? record.role)}」角色绑定两步验证。绑定前每次登录都会收到本提醒；请使用下方「两步验证」卡片完成绑定。</div>`
    : ''
  const deviceRows = devices.map((e) => {
    const t = String(e.ts ?? '').replace('T', ' ').slice(5, 16)
    return `<tr><td>${esc(t)}</td><td>${esc(e.actor?.ip ?? '—')}</td></tr>`
  }).join('')
  return page('个人中心', `
<div class="head"><h1>卡巴格 · 个人中心</h1>${backLink}</div>
${enrollBanner}
<div class="card"><h2>我的资料</h2>
<div class="kv">
<span class="k">显示名</span><span>${esc(record.displayName ?? record.account)}</span>
<span class="k">账号</span><span>${esc(record.account)}</span>
<span class="k">角色</span><span>${esc(ROLE_LABELS[record.role] ?? record.role)}</span>
<span class="k">部门</span><span>${esc(record.department ?? '未分配')}</span>
<span class="k">绑定实例</span><span>${esc(record.instanceId ?? '—')}${workspaceUrl !== null ? ` ｜ <a href="${esc(workspaceUrl)}">${esc(record.instanceId)} 工作区</a>` : ''}</span>
</div></div>
${usageHtml(record, dataDir)}
<div class="card"><h2>修改密码</h2>
<p class="mut" style="margin:.2rem 0 .4rem">修改成功后所有设备（含本机）立即下线，需用新密码重新登录。</p>
<form onsubmit="changePassword(event)">
<label>当前密码</label><input type="password" id="cur" autocomplete="current-password" required>
<label>新密码</label><input type="password" id="next" autocomplete="new-password" required>
<label>确认新密码</label><input type="password" id="next2" autocomplete="new-password" required>
<div class="msg" id="pwmsg"></div><button>更新密码</button>
</form></div>
<div class="card"><h2>设备管理</h2>
<p class="mut" style="margin:.2rem 0 .4rem">最近登录（最多 5 条，来自平台审计）：</p>
<table><tr><th>时间</th><th>IP</th></tr>${deviceRows || '<tr><td colspan="2">暂无登录记录</td></tr>'}</table>
<button class="danger" onclick="revokeAll()">下线所有设备</button>
<span class="mut" id="rvmsg" style="margin-left:.8rem"></span></div>
${twofaCard(record, dataDir, twofaKey)}
<script>
async function post(path,body){const r=await fetch(path,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)});return {status:r.status,body:await r.json().catch(()=>({}))}}
async function changePassword(ev){ev.preventDefault();
 var m=document.getElementById('pwmsg');m.className='msg';
 var r=await post('/api/me/password',{currentPassword:cur.value,newPassword:next.value,confirmPassword:next2.value});
 if(r.status===200){m.className='msg okmsg';m.textContent='密码已更新，所有设备已下线；3 秒后跳转登录页…';
  setTimeout(function(){location.href='/login'},3000);return}
 m.textContent=(r.body&&r.body.error)||('失败（HTTP '+r.status+'）')}
async function revokeAll(){var r=await post('/api/me/revoke-all',{});
 var m=document.getElementById('rvmsg');
 if(r.status===200){m.textContent='已下线所有设备，请重新登录';setTimeout(function(){location.href='/login'},1500)}
 else m.textContent=(r.body&&r.body.error)||'失败'}
async function tfaSetup(){var r=await post('/api/me/2fa/setup',{});
 if(r.status===200){document.getElementById('tfasetup').style.display='block';
  document.getElementById('tfasec').textContent=r.body.secret;
  var a=document.getElementById('tfalink');a.href=r.body.otpauth;a.textContent=r.body.otpauth}
 else{var m=document.getElementById('tfamsg');if(m)m.textContent=(r.body&&r.body.error)||'失败'}}
async function tfaConfirm(ev){ev.preventDefault();
 var m=document.getElementById('tfamsg');m.className='msg';
 var r=await post('/api/me/2fa/confirm',{code:tfacode.value});
 if(r.status===200){m.className='msg okmsg';m.textContent='两步验证已启用';setTimeout(function(){location.reload()},900);return}
 m.textContent=(r.body&&r.body.error)||('失败（HTTP '+r.status+'）')}
async function tfaDisable(ev){ev.preventDefault();
 var m=document.getElementById('tfamsg');m.className='msg';
 var r=await post('/api/me/2fa/disable',{password:tfapw.value});
 if(r.status===200){m.className='msg okmsg';m.textContent='已关闭两步验证';setTimeout(function(){location.reload()},900);return}
 m.textContent=(r.body&&r.body.error)||('失败（HTTP '+r.status+'）')}
</script>`)
}

/** 注册页：code 有效显示预设与表单，否则显示拒绝文案。code 只进表单与链接。 */
function registerPage({ verdict, code }) {
  if (!verdict.ok) {
    return page('邀请注册', `
<div class="head"><h1>卡巴格 · 邀请注册</h1></div>
<div class="card"><p style="margin:.2rem 0">${esc(inviteRejectMessage(verdict.reason))}</p>
<p class="mut">已有账号？<a href="/login">去登录</a></p></div>`)
  }
  const invite = verdict.invite
  return page('邀请注册', `
<div class="head"><h1>卡巴格 · 邀请注册</h1><a href="/login">已有账号？去登录</a></div>
<div class="invite">
<b>邀请有效</b> ｜ 部门：<b>${esc(invite.department)}</b> ｜ 角色：<b>${esc(ROLE_LABELS[invite.role] ?? invite.role)}</b> ｜ 实例：<b>${esc(invite.instanceId)}</b>
<div class="mut" style="margin-top:.3rem">有效期至 ${esc(invite.expiresAt)}（剩余 <span id="cd">…</span>），每个邀请仅可注册一次。</div>
</div>
<div class="card">
<form onsubmit="doRegister(event)">
<label>账号（邮箱）</label><input id="acc" placeholder="name@company" autocomplete="username" required>
<label>显示名（可选）</label><input id="dn" placeholder="如 小王">
<label>密码</label><input type="password" id="pw" autocomplete="new-password" required>
<label>确认密码</label><input type="password" id="pw2" autocomplete="new-password" required>
<div class="msg" id="msg"></div><button>注册并加入企业</button>
</form></div>
<script>
var CODE=${JSON.stringify(code)};var EXPIRES=${JSON.stringify(invite.expiresAt)};
function tick(){var left=Date.parse(EXPIRES)-Date.now();if(left<=0){document.getElementById('cd').textContent='已过期';return}
 var m=Math.floor(left/60000),h=Math.floor(m/60);document.getElementById('cd').textContent=h+' 小时 '+(m%60)+' 分钟'}
tick();setInterval(tick,1000);
async function doRegister(ev){ev.preventDefault();
 var m=document.getElementById('msg');m.textContent='';
 var r=await fetch('/api/register',{method:'POST',headers:{'content-type':'application/json'},
  body:JSON.stringify({code:CODE,account:acc.value,displayName:dn.value,password:pw.value,confirmPassword:pw2.value})});
 var j=await r.json().catch(function(){return{}});
 if(r.ok){m.className='msg okmsg';m.textContent='注册成功，正在跳转登录页…';setTimeout(function(){location.href='/login'},1500);return}
 m.textContent=(j&&j.error)||('注册失败（HTTP '+r.status+'）')}
</script>`)
}

/** 注册串行队列：invites.json 与 accounts.json 都是读改写热点，全局串行。 */
let registerQueue = Promise.resolve()

/** 注册限速器按 dataDir 缓存（计数桶必须跨请求存活，内存态随 daemon 重启清零）。 */
const registerGuards = new Map()
function registerGuardFor(dataDir) {
  let guard = registerGuards.get(dataDir)
  if (guard === undefined) {
    // 每次判定现读 security.json：管理台改动即时生效（与登录限速一致）。
    guard = createLoginRateGuard(() => {
      const config = loadSecurityConfig(dataDir)
      return {
        windowMs: config.loginWindowMinutes * 60_000,
        maxFails: config.loginMaxFails,
        lockoutMs: config.lockoutMinutes * 60_000,
      }
    })
    registerGuards.set(dataDir, guard)
  }
  return guard
}

/**
 * 处理门户员工侧路由（gateway 在裸 portal 主机分支调用；auth/twofaKey 由
 * 网关算好传入）。
 * @returns true 表示已响应，网关不再处理。
 */
export function handlePortal({ req, res, url, auth, dataDir, manifest, loginPage, twofaKey }) {
  const path = url.pathname
  const method = req.method

  if (method === 'GET' && path === '/login') {
    if (auth.error === undefined) {
      res.writeHead(303, { location: auth.record.role === 'employee' ? '/me' : '/' })
      res.end()
      return true
    }
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' })
    res.end(loginPage())
    return true
  }

  if (method === 'GET' && path === '/me') {
    if (auth.error !== undefined) {
      res.writeHead(401, { 'content-type': 'text/html; charset=utf-8' })
      res.end(loginPage())
      return true
    }
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' })
    res.end(mePage({ record: auth.record, dataDir, manifest, twofaKey }))
    return true
  }

  if (method === 'GET' && path === '/register') {
    // 明文 code 白名单（生成格式 inv-<base64url>）：畸形串不经哈希比较直接按
    // 无效渲染，防查询串内容回流页面（显式防御，不依赖 esc 兜底）。
    const raw = url.searchParams.get('code') ?? ''
    const code = /^inv-[A-Za-z0-9_-]+$/.test(raw) ? raw : ''
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' })
    res.end(registerPage({ verdict: code === '' ? { ok: false, reason: 'invalid_code' } : validateInvite(dataDir, code), code }))
    return true
  }

  if (method === 'POST' && path === '/api/me/password') return respondMePassword({ req, res, auth, dataDir })
  if (method === 'POST' && path === '/api/me/revoke-all') return respondRevokeAll({ req, res, auth, dataDir })
  if (method === 'POST' && path === '/api/me/2fa/setup') return respond2faSetup({ req, res, auth, dataDir, twofaKey })
  if (method === 'POST' && path === '/api/me/2fa/confirm') return respond2faConfirm({ req, res, auth, dataDir, twofaKey })
  if (method === 'POST' && path === '/api/me/2fa/disable') return respond2faDisable({ req, res, auth, dataDir, twofaKey })
  if (method === 'POST' && path === '/api/register') return respondRegister({ req, res, dataDir, manifest })
  return false
}

function respondMePassword({ req, res, auth, dataDir }) {
  if (auth.error !== undefined) { json(res, 401, { error: 'unauthenticated' }); return true }
  if (!sameOrigin(req)) { json(res, 403, { error: 'cross-origin refused' }); return true }
  void readJsonBody(req).then((body) => {
    const store = loadAccounts(dataDir)
    const record = store.accounts.find((a) => a.id === auth.payload.sub)
    const actor = { account: auth.record.account, role: auth.record.role, ip: clientIp(req) }
    const fail = (reason, message) => {
      void auditAppend({ actor, action: 'member.self_password_change', target: auth.record.account, result: 'fail', detail: { reason } })
      json(res, 400, { error: message })
    }
    if (record === undefined) { json(res, 401, { error: 'unauthenticated' }); return }
    if (typeof body.newPassword !== 'string' || body.newPassword === '') { fail('missing_password', '新密码不能为空'); return }
    if (!verifyPassword(record, String(body.currentPassword ?? ''))) { fail('wrong_password', '当前密码不正确'); return }
    if (body.confirmPassword !== undefined && body.confirmPassword !== body.newPassword) { fail('mismatch', '两次输入的新密码不一致'); return }
    const policy = checkPasswordPolicy(body.newPassword, record.account, loadSecurityConfig(dataDir))
    if (!policy.ok) { fail('weak_password', policy.message); return }
    // setPassword = 单次读改写：重哈希 + tokenEpoch+1（全端下线，含当前会话）。
    setPassword(dataDir, record.account, body.newPassword)
    void auditAppend({ actor, action: 'member.self_password_change', target: record.account, result: 'ok', detail: null })
    json(res, 200, { ok: true, message: '密码已更新，所有设备已下线，请重新登录' })
  })
  return true
}

function respondRevokeAll({ req, res, auth, dataDir }) {
  if (auth.error !== undefined) { json(res, 401, { error: 'unauthenticated' }); return true }
  if (!sameOrigin(req)) { json(res, 403, { error: 'cross-origin refused' }); return true }
  const epoch = revokeAccountTokens(dataDir, auth.record.account)
  void auditAppend({
    actor: { account: auth.record.account, role: auth.record.role, ip: clientIp(req) },
    action: 'auth.revoke_all',
    target: auth.record.account,
    result: 'ok',
    detail: { tokenEpoch: epoch },
  })
  json(res, 200, { ok: true, message: '已下线所有设备，请重新登录' })
  return true
}

/** 2FA 绑定第一步：生成密钥 → pending → 返回 base32 与 otpauth 链接（文本，不做二维码）。 */
function respond2faSetup({ req, res, auth, dataDir, twofaKey }) {
  if (auth.error !== undefined) { json(res, 401, { error: 'unauthenticated' }); return true }
  if (!sameOrigin(req)) { json(res, 403, { error: 'cross-origin refused' }); return true }
  const secret = generateTotpSecret()
  try {
    setPendingSecret(dataDir, twofaKey, auth.record.account, secret)
  } catch (error) {
    json(res, 400, { error: String(error?.message ?? error) })
    return true
  }
  json(res, 200, { secret, otpauth: otpauthUrl({ secret, account: auth.record.account }) })
  return true
}

/** 2FA 绑定第二步：验证码通过才 enabled（审计 security.2fa_enabled）。 */
function respond2faConfirm({ req, res, auth, dataDir, twofaKey }) {
  if (auth.error !== undefined) { json(res, 401, { error: 'unauthenticated' }); return true }
  if (!sameOrigin(req)) { json(res, 403, { error: 'cross-origin refused' }); return true }
  void readJsonBody(req).then((body) => {
    const verdict = confirmSecret(dataDir, twofaKey, auth.record.account, String(body.code ?? ''))
    if (!verdict.ok) {
      const message = verdict.reason === 'not_started' ? '请先点击「开始绑定」生成密钥'
        : verdict.reason === 'broken' ? '两步验证配置损坏，请联系管理员重置（管理台成员页→重置2FA）'
          : '验证码错误，请确认认证器时间与密钥后重试'
      json(res, 400, { error: message })
      return
    }
    void auditAppend({
      actor: { account: auth.record.account, role: auth.record.role, ip: clientIp(req) },
      action: 'security.2fa_enabled',
      target: auth.record.account,
      result: 'ok',
      detail: null,
    })
    json(res, 200, { ok: true, message: '两步验证已启用' })
  })
  return true
}

/** 2FA 解绑：验当前密码后关闭（审计 security.2fa_disabled，ok/fail 都留痕）。 */
function respond2faDisable({ req, res, auth, dataDir, twofaKey }) {
  if (auth.error !== undefined) { json(res, 401, { error: 'unauthenticated' }); return true }
  if (!sameOrigin(req)) { json(res, 403, { error: 'cross-origin refused' }); return true }
  void readJsonBody(req).then((body) => {
    const actor = { account: auth.record.account, role: auth.record.role, ip: clientIp(req) }
    const record = loadAccounts(dataDir).accounts.find((a) => a.id === auth.payload.sub)
    if (record === undefined || !verifyPassword(record, String(body.password ?? ''))) {
      void auditAppend({ actor, action: 'security.2fa_disabled', target: auth.record.account, result: 'fail', detail: { reason: 'wrong_password' } })
      json(res, 400, { error: '当前密码不正确' })
      return
    }
    if (!clearTwofa(dataDir, auth.record.account)) {
      json(res, 400, { error: '该账号未绑定两步验证' })
      return
    }
    void auditAppend({ actor, action: 'security.2fa_disabled', target: auth.record.account, result: 'ok', detail: null })
    json(res, 200, { ok: true, message: '两步验证已关闭' })
  })
  return true
}

/** 注册处理（公开端点）：按 IP 限速 → 串行（校验→建号→钥匙→消费→下发→审计）。 */
function respondRegister({ req, res, dataDir, manifest }) {
  if (!sameOrigin(req)) { json(res, 403, { error: 'cross-origin refused' }); return true }
  const guard = registerGuardFor(dataDir)
  const ip = clientIp(req)
  void readJsonBody(req).then((body) => {
    const actorOf = (role) => ({ account: String(body.account ?? ''), role, ip })
    const fail = (reason, message) => {
      guard.fail('', ip)
      void auditAppend({ actor: actorOf(null), action: 'member.register', target: null, result: 'fail', detail: { reason } })
      json(res, 400, { error: message })
    }
    const verdict = guard.check('', ip)
    if (!verdict.allowed) {
      void auditAppend({ actor: actorOf(null), action: 'member.register', target: null, result: 'deny', detail: { reason: 'rate_limited', retryAfterMinutes: verdict.retryAfterMinutes } })
      json(res, 429, { error: `注册尝试过于频繁，请约 ${verdict.retryAfterMinutes} 分钟后再试` })
      return
    }
    registerQueue = registerQueue.then(async () => {
      try {
        const invite = validateInvite(dataDir, String(body.code ?? ''))
        if (!invite.ok) { fail(invite.reason, inviteRejectMessage(invite.reason)); return }
        const account = typeof body.account === 'string' ? body.account.trim() : ''
        if (account === '') { fail('missing_account', '账号不能为空'); return }
        if (body.confirmPassword !== undefined && body.confirmPassword !== body.password) { fail('mismatch', '两次输入的密码不一致'); return }
        if (loadAccounts(dataDir).accounts.some((a) => a.account === account)) { fail('account_exists', `账号已存在: ${account}`); return }
        const policy = checkPasswordPolicy(String(body.password ?? ''), account, loadSecurityConfig(dataDir))
        if (!policy.ok) { fail('weak_password', policy.message); return }
        let created
        try {
          created = addAccount(dataDir, {
            account,
            instanceId: invite.invite.instanceId,
            role: invite.invite.role,
            displayName: typeof body.displayName === 'string' && body.displayName.trim() !== '' ? body.displayName.trim() : undefined,
            department: invite.invite.department,
            password: body.password,
          })
        } catch (error) {
          fail('invalid_account', String(error?.message ?? error))
          return
        }
        issueVkey(dataDir, { account: created.account, instanceId: created.instanceId, models: '*' })
        const consumed = consumeInvite(dataDir, String(body.code ?? ''), created.account)
        if (!consumed.ok) {
          // 串行队列下不应到达（校验与消费之间无并发窗口）；到达说明数据被
          // 外部并发修改——如实报错，账号保留由管理员处置。
          json(res, 409, { error: inviteRejectMessage(consumed.reason) })
          return
        }
        // 阶段 9 复用：按实例归属账号的角色重发该实例 tool-policy（热生效）。
        let policySynced = false
        const spec = manifest.instances.find((s) => s.id === created.instanceId)
        if (spec !== undefined) {
          try { syncInstanceHome(dataDir, spec); policySynced = true } catch (error) {
            console.error('[portal] 注册后策略下发失败:', error?.message ?? error)
          }
        }
        guard.success('', ip)
        void auditAppend({
          actor: { account: created.account, role: created.role, ip },
          action: 'member.register',
          target: created.account,
          result: 'ok',
          detail: { role: created.role, department: created.department, instanceId: created.instanceId, policySynced },
        })
        json(res, 200, { ok: true, account: created.account, instance: created.instanceId })
      } catch (error) {
        // 请求必被响应（对齐 console runLocked）：未预期抛错（如畸形字段类型
        // 打穿 addAccount 的 scrypt）转 500，客户端绝不挂死。
        const message = String(error?.message ?? error)
        console.error('[portal] 注册处理异常:', message)
        void auditAppend({ actor: actorOf(null), action: 'member.register', target: null, result: 'fail', detail: { reason: 'internal', error: message } })
        json(res, 500, { error: message })
      }
    })
    registerQueue = registerQueue.catch(() => {})
  })
  return true
}
