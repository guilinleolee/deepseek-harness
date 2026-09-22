/**
 * 落云宗企业平台 · 管理台（视觉层按 5 页设计图打磨）。
 *
 * 页面与操作 API（逻辑与上一增量一致，仅升级视觉与少量只读增强：
 * 成员搜索、实例筛选标签与日志查看、模型展示元数据、实例页授权/生效对比）：
 * - /console            总览：统计卡 + 实例与用量 + Relay 元日志尾
 * - /console/members    成员与额度：搜索、建号、改额度、重置密码、禁用/启用
 * - /console/models     模型与权限：上游提供方、可用模型（含展示元数据）、授权矩阵
 * - /console/instances  实例管理：统计卡 + 筛选标签 + 日志查看 + 重启/停止/启动
 * - /console/plugins    插件管理：统计卡 + 平台默认插件集 + 期望态视图
 * 全部仅限平台管理员（网关 JWT 门禁，POST 另校验 Origin 同源）；
 * 页面只渲染元数据，不触碰会话/内容正文（任务书决定 5）。
 */
import { readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { addAccount, listAccounts, loadAccounts, saveAccounts, setPassword } from './gateway.mjs'
import { issueVkey, listUpstreams, revokeVkey, setQuota, setVkeyModels } from './relay.mjs'

const PAGES = ['members', 'models', 'instances', 'plugins']
const PAGE_TITLES = { members: '成员与额度', models: '模型与权限', instances: '实例管理', plugins: '插件管理' }

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

function readJson(dataDir, file, fallback) {
  try {
    return JSON.parse(readFileSync(join(dataDir, file), 'utf8'))
  } catch {
    return fallback
  }
}

/* ── 设计系统 ────────────────────────────────────────────────────────────── */

const CSS = `
:root{--bg:#0b1022;--panel:#141a33;--panel2:#1a2140;--line:#2c3560;--line2:#39406e;
--text:#e8eaf6;--muted:#9aa4d4;--faint:#6a74a8;--accent:#43d6c5;--blue:#6f9bff;
--green:#3ddc97;--red:#ff6b6b;--yellow:#ffd166}
*{box-sizing:border-box}
body{margin:0;display:flex;font-family:system-ui,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
color:var(--text);background:radial-gradient(1100px 520px at 72% -8%,#1c2452 0%,var(--bg) 58%) fixed}
nav{width:216px;min-height:100vh;background:linear-gradient(180deg,#0e142c 0%,#0b1022 100%);
border-right:1px solid var(--line);padding:1.1rem .75rem;display:flex;flex-direction:column}
.brand{display:flex;align-items:center;gap:.55rem;padding:.2rem .5rem 1rem}
.brand .mark{width:30px;height:30px;border-radius:8px;background:linear-gradient(135deg,#43d6c5,#2a9d8f);
display:grid;place-items:center;font-weight:700;color:#06231f}
.brand .name{font-weight:600;letter-spacing:.08em}
.brand .sub{font-size:.68rem;color:var(--faint);letter-spacing:.14em}
.navgroup{font-size:.68rem;letter-spacing:.16em;color:var(--faint);margin:1rem .6rem .3rem;
display:flex;align-items:center;gap:.4rem}
.navgroup svg{width:12px;height:12px;stroke:var(--faint)}
nav a.item{display:flex;align-items:center;gap:.5rem;color:#c5cae9;text-decoration:none;
padding:.48rem .7rem;border-radius:7px;margin:.12rem 0;font-size:.92rem}
nav a.item:hover{background:#232a4d}
nav a.item.on{background:#232a4d;color:#fff;box-shadow:inset 2px 0 0 var(--accent)}
nav .spacer{flex:1}
.me{display:flex;align-items:center;gap:.55rem;padding:.6rem .5rem;border-top:1px solid var(--line);margin-top:.8rem}
main{flex:1;padding:1.5rem 2.2rem 2.5rem;min-width:0}
.pagehead{display:flex;align-items:flex-end;justify-content:space-between;border-bottom:1px solid var(--line);padding-bottom:.9rem;margin-bottom:1.3rem}
.pagehead h1{margin:0;font-size:1.45rem;letter-spacing:.02em}
.pagehead .sub{color:var(--muted);font-size:.9rem;margin-top:.3rem}
.statusbadge{display:flex;align-items:center;gap:.45rem;font-size:.85rem;color:var(--muted);
border:1px solid var(--line);border-radius:999px;padding:.35rem .8rem}
.dot{width:8px;height:8px;border-radius:50%;background:var(--green);box-shadow:0 0 6px var(--green)}
.dot.warn{background:var(--yellow);box-shadow:0 0 6px var(--yellow)}
.dot.bad{background:var(--red);box-shadow:0 0 6px var(--red)}
.statgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:.9rem;margin:.2rem 0 1.4rem}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:.85rem 1rem}
.stat .k{font-size:.78rem;color:var(--muted)}
.stat .v{font-size:1.55rem;font-weight:600;margin-top:.25rem}
.stat .n{font-size:.75rem;color:var(--faint);margin-top:.2rem}
h2.sect{font-size:1.02rem;color:#c5cae9;margin:1.6rem 0 .4rem}
table{border-collapse:collapse;margin:.5rem 0 1.3rem;width:100%;background:rgba(20,26,51,.6)}
td,th{border:1px solid var(--line);padding:.5rem .75rem;font-size:.88rem;text-align:left;vertical-align:top}
th{color:var(--muted);font-weight:500;font-size:.78rem;letter-spacing:.05em;background:rgba(12,16,31,.55)}
.chip{display:inline-block;padding:.14rem .55rem;border-radius:999px;font-size:.76rem;line-height:1.3}
.chip.green{background:rgba(61,220,151,.12);color:#7ef0c0;border:1px solid rgba(61,220,151,.35)}
.chip.blue{background:rgba(111,155,255,.12);color:#9fbcff;border:1px solid rgba(111,155,255,.35)}
.chip.red{background:rgba(255,107,107,.12);color:#ff9d9d;border:1px solid rgba(255,107,107,.35)}
.chip.yellow{background:rgba(255,209,102,.12);color:#ffe08a;border:1px solid rgba(255,209,102,.35)}
.chip.gray{background:rgba(154,164,212,.1);color:var(--muted);border:1px solid var(--line2)}
.chip.teal{background:rgba(67,214,197,.12);color:#7ff0e0;border:1px solid rgba(67,214,197,.35)}
.bar{width:130px;height:6px;border-radius:3px;background:#232a4d;overflow:hidden;vertical-align:middle;display:inline-block}
.bar i{display:block;height:100%;border-radius:3px}
.avatar{width:30px;height:30px;border-radius:50%;display:inline-grid;place-items:center;
font-size:.8rem;font-weight:600;color:#0b1022;vertical-align:middle;margin-right:.5rem}
.btn{padding:.3rem .65rem;border-radius:6px;border:1px solid var(--line2);background:var(--panel2);
color:var(--text);cursor:pointer;font-size:.82rem;margin:.12rem .18rem .12rem 0;text-decoration:none;display:inline-block}
.btn:hover{border-color:var(--accent);color:#fff}
.btn.warn{border-color:rgba(255,107,107,.5);color:#ff9d9d}
.btn.primary{background:var(--accent);border-color:var(--accent);color:#06231f;font-weight:600}
.btn:disabled{opacity:.45;cursor:not-allowed}
.tabs{display:flex;gap:.4rem;margin:.3rem 0 .8rem}
.tabs a{padding:.28rem .85rem;border-radius:999px;border:1px solid var(--line2);color:var(--muted);
text-decoration:none;font-size:.84rem}
.tabs a.on{background:rgba(67,214,197,.12);border-color:var(--accent);color:#7ff0e0}
input,select,button{font-family:inherit}
input,select{padding:.35rem .55rem;border-radius:5px;border:1px solid var(--line2);background:#0c101f;color:var(--text)}
button{padding:.35rem .7rem;border-radius:6px;border:1px solid var(--line2);background:var(--panel2);color:var(--text);cursor:pointer}
button.primary{background:var(--accent);border-color:var(--accent);color:#06231f;font-weight:600}
form.panel{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:1rem 1.1rem;display:inline-block}
pre.log{background:#0a0e1e;border:1px solid var(--line);border-radius:8px;padding:.9rem;overflow:auto;
font-size:.78rem;line-height:1.5;max-height:60vh}
footer{margin-top:3rem;text-align:center;color:var(--faint);font-size:.8rem;letter-spacing:.1em}
a{color:var(--blue)}
.searchbox{display:flex;gap:.4rem;align-items:center;margin-bottom:.6rem}
.searchbox input{width:220px}
`

const ICONS = {
  grid: '<svg viewBox="0 0 16 16" fill="none" stroke-width="1.5"><rect x="1.5" y="1.5" width="5" height="5" rx="1"/><rect x="9.5" y="1.5" width="5" height="5" rx="1"/><rect x="1.5" y="9.5" width="5" height="5" rx="1"/><rect x="9.5" y="9.5" width="5" height="5" rx="1"/></svg>',
  shield: '<svg viewBox="0 0 16 16" fill="none" stroke-width="1.5"><path d="M8 1.5 13.5 3.5v4c0 3.2-2.3 5.8-5.5 7-3.2-1.2-5.5-3.8-5.5-7v-4L8 1.5z"/></svg>',
  pulse: '<svg viewBox="0 0 16 16" fill="none" stroke-width="1.5"><path d="M1.5 8.5h3l1.5-4 3 8 1.5-4h4"/></svg>',
  user: '<svg viewBox="0 0 16 16" fill="none" stroke-width="1.5"><circle cx="8" cy="5" r="3"/><path d="M2 14.5c.8-3 3-4.5 6-4.5s5.2 1.5 6 4.5"/></svg>',
}

const stateChip = (state) => {
  const map = {
    running: ['运行中', 'green'], starting: ['启动中', 'blue'], restarting: ['重启中', 'yellow'],
    stopped: ['已停止', 'gray'], crashed: ['已崩溃', 'red'], unhealthy: ['异常', 'red'], failed: ['失败', 'red'],
  }
  const [label, cls] = map[state] ?? [state ?? '—', 'gray']
  return `<span class="chip ${cls}">${label}</span>`
}

const AVATAR_COLORS = ['#43d6c5', '#6f9bff', '#ffd166', '#ff9d9d', '#b388ff', '#7ef0c0']
const avatar = (name) => {
  const ch = [...String(name || '?')][0]
  const sum = [...String(name || '')].reduce((a, c) => a + c.codePointAt(0), 0)
  return `<span class="avatar" style="background:${AVATAR_COLORS[sum % AVATAR_COLORS.length]}">${esc(ch)}</span>`
}

const roleChip = (role) => {
  const map = { admin: ['管理员', 'red'], auditor: ['审计员', 'yellow'], employee: ['成员', 'blue'] }
  const [label, cls] = map[role] ?? [role, 'gray']
  return `<span class="chip ${cls}">${label}</span>`
}

const quotaCell = (used, quota) => {
  if (!Number.isFinite(quota)) return `${used} <span class="chip gray">不限</span>`
  const pct = Math.min(100, Math.round((used / Math.max(1, quota)) * 100))
  const color = pct >= 100 ? 'var(--red)' : pct >= 70 ? 'var(--yellow)' : 'var(--green)'
  const mark = pct >= 100 ? ' 🔴' : ''
  return `<span class="bar"><i style="width:${pct}%;background:${color}"></i></span> <span style="font-size:.82rem">${used}/${quota}${mark}</span>`
}

const nowStamp = () => {
  const d = new Date()
  const p = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}

const activeVkeyFor = (dataDir, account) => {
  const vkeys = readJson(dataDir, 'vkeys.json', { vkeys: [] }).vkeys
  return [...vkeys].reverse().find((v) => v.account === account && !v.revoked)
}

/* ── 页面外壳 ────────────────────────────────────────────────────────────── */

const SUBTITLES = {
  总览: '实例、用量与漂移，一屏掌握',
  成员与额度: '身份、角色、Token 额度',
  模型与权限: '企业允许的模型及角色可见性',
  实例管理: '所有 DSH 实例的进程、资源与配置对齐（含实例设置）',
  插件管理: '第三方插件的安装范围、版本与生效状态',
  实例日志: '实例运行日志（最近 80 行）',
}

function SHELL(title, active, manifest, getState, dataDir, body) {
  const state = getState()
  const states = manifest.instances.map((s) => state.instances[s.id]?.state ?? 'stopped')
  const badge = states.every((s) => s === 'running')
    ? '<span class="dot"></span> 全部服务正常'
    : states.some((s) => ['crashed', 'failed', 'unhealthy'].includes(s))
      ? '<span class="dot bad"></span> 存在异常实例'
      : '<span class="dot warn"></span> 服务启动中'
  const admin = listAccounts(dataDir).find((a) => a.role === 'admin')
  const item = (label, href, icon, on) =>
    `<a class="item ${on ? 'on' : ''}" href="${href}"><span style="width:14px;height:14px;display:inline-grid">${icon}</span>${label}</a>`
  const nav = `
<div class="navgroup">${ICONS.grid} 概览</div>
${item('总览', '/console', ICONS.grid, active === '')}
<div class="navgroup">${ICONS.shield} 管理</div>
${PAGES.map((p) => item(PAGE_TITLES[p], `/console/${p}`, ICONS.shield, active === p)).join('')}
<div class="navgroup">${ICONS.pulse} 运行</div>
${item('系统状态', '/console/instances', ICONS.pulse, false)}
<div class="spacer"></div>
${item('员工工作区', `http://${manifest.gatewayHost}:${manifest.portalPort}/`, ICONS.user, false)}
<div class="me">${avatar(admin?.displayName ?? '管')}<div><div style="font-size:.86rem">${esc(admin?.displayName ?? '管理员')}</div><div style="font-size:.72rem;color:var(--faint)">${esc(admin?.role === 'admin' ? '管理员 · 平台' : '')}</div></div></div>`
  return `<!doctype html><html lang="zh"><head><meta charset="utf-8"><title>落云宗 · ${title}</title><style>${CSS}</style></head>
<body>
<nav><div class="brand"><span class="mark">落</span><div><div class="name">落云宗</div><div class="sub">DASHBOARD CONSOLE</div></div></div>${nav}</nav>
<main>
<div class="pagehead"><div><h1>${title}</h1><div class="sub">${esc(SUBTITLES[title] ?? '')}</div></div><div class="statusbadge">${badge}<span>${nowStamp()}</span></div></div>
${body}
<footer>落云宗 · 企业 AI 管理台</footer>
</main></body></html>`
}

/* ── 页面：总览 ──────────────────────────────────────────────────────────── */

function overviewPage({ manifest, getState, dataDir }) {
  const month = (() => { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}` })()
  const state = getState()
  const usageMonth = readJson(dataDir, 'usage.json', { months: {} }).months[month] ?? {}
  const accounts = listAccounts(dataDir)
  const drift = readJson(dataDir, 'drift.json', { checks: {} }).checks
  const running = manifest.instances.filter((s) => state.instances[s.id]?.state === 'running').length
  const monthTokens = accounts.reduce((sum, a) => {
    const e = usageMonth[a.account]
    return sum + (e ? e.tokensIn + e.tokensOut : 0)
  }, 0)
  const driftBad = manifest.instances.filter((s) => (drift[s.id]?.diffs ?? []).length > 0).length
  const stats = `<div class="statgrid">
<div class="stat"><div class="k">实例</div><div class="v">${running} <span style="font-size:.85rem;color:var(--muted)">/ ${manifest.instances.length} 运行中</span></div><div class="n">一人一实例 · 独立目录</div></div>
<div class="stat"><div class="k">本月 Token 用量</div><div class="v">${monthTokens.toLocaleString()}</div><div class="n">${month} · 服务器本地时区</div></div>
<div class="stat"><div class="k">配置漂移</div><div class="v">${driftBad === 0 ? '✅' : driftBad}</div><div class="n">${driftBad === 0 ? '授权集与生效集对齐' : '个实例存在差异'}</div></div>
<div class="stat"><div class="k">账号</div><div class="v">${accounts.length}</div><div class="n">成员与管理员</div></div>
</div>`
  const rows = manifest.instances.map((spec) => {
    const rec = state.instances[spec.id] ?? {}
    const mem = rec.memoryKB ? `${(rec.memoryKB / 1024).toFixed(1)} MB` : '—'
    const disk = rec.diskBytes !== null && rec.diskBytes !== undefined ? `${(rec.diskBytes / 1024 / 1024).toFixed(1)} MB` : '—'
    const a = accounts.find((x) => x.account === spec.account)
    const e = usageMonth[spec.account] ?? { tokensIn: 0, tokensOut: 0, requests: 0 }
    const used = e.tokensIn + e.tokensOut
    const c = drift[spec.id]
    const driftText = c === undefined ? '<span class="chip gray">未检查</span>' : (() => {
      const stale = c.diffs.filter((x) => x.stale).length
      const fresh = c.diffs.length - stale
      return c.diffs.length === 0 ? '<span class="chip green">对齐</span>' : `<span class="chip red">🔴 ${stale}</span> <span class="chip yellow">🟡 ${fresh}</span>`
    })()
    return `<tr><td>${avatar(a?.displayName)}${esc(a?.displayName ?? spec.id)}</td><td>${stateChip(rec.state)}</td><td>${spec.port}</td><td>${mem}</td><td>${disk}</td><td>${used}</td><td>${driftText}</td><td><a class="btn" href="/console/instances">管理</a></td></tr>`
  }).join('')
  let relayTail = '<tr><td colspan="5">暂无转发记录</td></tr>'
  try {
    relayTail = readFileSync(join(dataDir, 'logs', 'relay.log'), 'utf8').trim().split('\n').slice(-8).map((line) => {
      try {
        const e = JSON.parse(line)
        return `<tr><td>${e.at.slice(5, 19)}</td><td>${esc(e.account)}</td><td>${esc(e.model)}</td><td>${esc(e.upstream)}</td><td>${e.status}（${e.ms} ms）</td></tr>`
      } catch { return '' }
    }).join('')
  } catch { /* 无日志文件 */ }
  return `
${stats}
<h2 class="sect">实例与用量</h2><table><tr><th>成员</th><th>状态</th><th>端口</th><th>内存</th><th>磁盘</th><th>本月 tokens</th><th>漂移</th><th></th></tr>${rows}</table>
<h2 class="sect">Relay 转发（最近 8 条元数据）</h2><table><tr><th>时间</th><th>账号</th><th>模型</th><th>上游</th><th>状态</th></tr>${relayTail}</table>
<p class="mut" style="font-size:.82rem">隐私边界：本页只聚合元数据，不包含任何会话或内容正文（任务书决定 5）。</p>`
}

/* ── 页面：成员与额度 ────────────────────────────────────────────────────── */

function membersPage({ dataDir, manifest, getState, query }) {
  const q = (query.get('q') ?? '').trim().toLowerCase()
  const d = new Date()
  const month = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
  const usage = readJson(dataDir, 'usage.json', { months: {} }).months[month] ?? {}
  const state = getState()
  const all = listAccounts(dataDir)
  const accounts = q === '' ? all : all.filter((a) => a.account.toLowerCase().includes(q) || String(a.displayName ?? '').toLowerCase().includes(q))
  const rows = accounts.map((a) => {
    const e = usage[a.account] ?? { tokensIn: 0, tokensOut: 0, requests: 0 }
    const used = e.tokensIn + e.tokensOut
    const vk = activeVkeyFor(dataDir, a.account)
    const chips = vk === undefined ? '<span class="chip gray">无钥匙</span>' : vk.models === '*'
      ? '<span class="chip teal">全部模型</span>'
      : vk.models.slice(0, 3).map((m) => `<span class="chip teal">${esc(m)}</span>`).join('') + (vk.models.length > 3 ? `<span class="chip gray">+${vk.models.length - 3}</span>` : '')
    const quota = a.monthlyTokens
    return `<tr><td>${avatar(a.displayName)}${esc(a.displayName)}</td><td>${esc(a.account)}</td><td>${roleChip(a.role)}</td><td>${esc(a.instanceId)}</td>
<td>${chips}</td><td>${a.disabled ? '<span class="chip red">已禁用</span>' : '<span class="chip green">正常</span>'}</td>
<td>${quotaCell(used, Number.isFinite(quota) ? quota : Number.POSITIVE_INFINITY)}</td><td>${e.requests}</td>
<td>
<form class="inline" onsubmit="api(event,'/console/api/member/quota',this)"><input type="hidden" name="account" value="${esc(a.account)}"><input name="tokens" size="8" placeholder="额度/空=不限"><button>改额度</button></form>
<form class="inline" onsubmit="api(event,'/console/api/member/reset-password',this)"><input type="hidden" name="account" value="${esc(a.account)}"><button>重置密码</button></form>
${a.disabled
    ? `<form class="inline" onsubmit="api(event,'/console/api/member/enable',this)"><input type="hidden" name="account" value="${esc(a.account)}"><button>启用</button></form>`
    : `<form class="inline" onsubmit="api(event,'/console/api/member/disable',this)"><input type="hidden" name="account" value="${esc(a.account)}"><button class="warn">禁用</button></form>`}</td></tr>`
  }).join('')
  const instanceOptions = manifest.instances.map((s) => `<option value="${s.id}">${s.id}（${esc(s.account)} · ${state.instances[s.id]?.state ?? '—'}）</option>`).join('')
  return `
<form class="searchbox" method="get"><input name="q" value="${esc(q)}" placeholder="搜索姓名 / 账号"><button class="primary">搜索</button>${q !== '' ? `<a class="btn" href="/console/members">清除</a>` : ''}</form>
<table><tr><th>成员</th><th>账号</th><th>角色</th><th>实例</th><th>可见模型</th><th>状态</th><th>本月已用/额度</th><th>请求</th><th>操作</th></tr>${rows || '<tr><td colspan="9">无匹配成员</td></tr>'}</table>
<h2 class="sect">添加成员</h2>
<form class="panel" onsubmit="createMember(event)">
<div style="margin-bottom:.5rem">账号 <input name="account" placeholder="name@company" required> 显示名 <input name="displayName"> 角色 <select name="role"><option value="employee">成员</option><option value="auditor">审计员</option></select></div>
<div>实例 <select name="instance">${instanceOptions}</select> 密码 <input name="password" placeholder="留空自动生成"> <button class="primary">创建</button></div>
</form>
<pre id="out" class="log" style="max-height:none"></pre>
<p class="mut" style="font-size:.82rem">禁用 = 立即下线 + 吊销虚拟钥匙（Relay 同步拒绝）；启用 = 重新签发钥匙（模型白名单沿用历史）。重置/创建的密码只显示一次。</p>
<script>
async function api(ev,path,form){ev.preventDefault();
 const f=new FormData(form||ev.target);const payload={};f.forEach((v,k)=>payload[k]=v);
 const r=await fetch(path,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(payload)});
 const t=await r.text();let msg=t;try{msg=JSON.stringify(JSON.parse(t))}catch{}
 if(path.includes('reset-password')&&r.ok){const p=JSON.parse(t).password;alert('新密码（只显示一次）：'+p)}
 document.getElementById('out').textContent='HTTP '+r.status+' '+msg;
 if(r.ok)setTimeout(()=>location.reload(),800)}
async function createMember(ev){await api(ev,'/console/api/member/create',true)}
</script>`
}

/* ── 页面：模型与权限 ────────────────────────────────────────────────────── */

function modelsPage({ dataDir }) {
  const upstreams = listUpstreams(dataDir).filter((x) => !x.revoked)
  const catalog = []
  for (const u of upstreams) for (const m of u.models) if (!catalog.includes(m)) catalog.push(m)
  const metaFor = (m) => {
    for (const u of upstreams) if (u.modelMeta?.[m]) return u.modelMeta[m]
    return null
  }
  const accounts = listAccounts(dataDir)
  const upstreamRows = upstreams.map((u) => `
<tr><td>${esc(u.name)}</td><td>${esc(u.baseURL)}</td><td><span class="chip gray">${esc(u.keyFingerprint ?? '—')}</span></td><td>${u.models.length}</td><td><span class="chip green">已接入</span></td></tr>`).join('')
  const modelRows = catalog.map((m) => {
    const u = upstreams.find((x) => x.models.includes(m))
    const meta = metaFor(m)
    const usedBy = accounts.filter((a) => {
      const vk = activeVkeyFor(dataDir, a.account)
      return vk !== undefined && (vk.models === '*' || vk.models.includes(m))
    }).length
    return `<tr><td>${esc(m)}</td><td>${esc(u?.name ?? '—')}</td><td>${meta ? esc(meta.context) : '—'} / ${meta ? esc(meta.maxOutput) : '—'}</td>
<td>${meta ? esc(meta.mIn) : '—'}</td><td>${meta ? esc(meta.mOut) : '—'}</td><td>${meta ? esc(meta.mCacheR) : '—'}</td><td>${meta ? esc(meta.mCacheW) : '—'}</td>
<td>${usedBy}</td><td><span class="chip green">已启用</span></td></tr>`
  }).join('')
  const matrix = modelsMatrix({ dataDir, accounts, catalog })
  return `
<h2 class="sect">上游提供方 <span class="mut" style="font-size:.8rem">真实 Key 只存在于 Relay 进程</span></h2>
<table><tr><th>提供方</th><th>端点（BaseURL）</th><th>上游 Key</th><th>模型数</th><th>状态</th></tr>${upstreamRows}</table>
<h2 class="sect">可用模型</h2>
<table><tr><th>模型</th><th>提供方</th><th>上下文 / 最大输出</th><th>输入倍率</th><th>输出倍率</th><th>缓存读</th><th>缓存写</th><th>成员可见</th><th>状态</th></tr>${modelRows}</table>
<h2 class="sect">成员实际可见的模型矩阵</h2>
${matrix}
<p class="mut" style="font-size:.82rem">改授权不用碰员工电脑：保存替换该成员虚拟钥匙的白名单，Relay 下一请求即强制生效。</p>`
}

function modelsMatrix({ dataDir, accounts, catalog }) {
  const rows = accounts.map((a) => {
    const vk = activeVkeyFor(dataDir, a.account)
    const cells = catalog.map((m) => {
      const on = vk !== undefined && (vk.models === '*' || vk.models.includes(m))
      return `<td><input type="checkbox" form="matrix" name="${esc(a.account)}|${m}" ${on ? 'checked' : ''}></td>`
    }).join('')
    return `<tr><td>${avatar(a.displayName)}${esc(a.displayName)}</td><td>${esc(a.account)}</td>${cells}</tr>`
  }).join('')
  const head = catalog.map((m) => `<th>${esc(m)}</th>`).join('')
  return `<form id="matrix" onsubmit="saveMatrix(event)">
<table><tr><th>成员</th><th>账号</th>${head}</tr>${rows}</table>
<button class="primary">保存矩阵</button></form>
<pre id="out" class="log" style="max-height:none"></pre>
<script>
async function saveMatrix(ev){ev.preventDefault();
 const f=new FormData(ev.target);const byAccount={};
 for(const [k,v] of f.entries()){if(!v)continue;const [account,model]=k.split('|');(byAccount[account]??=[]).push(model)}
 for(const [account,models] of Object.entries(byAccount)){
  const r=await fetch('/console/api/member/models',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({account,models})});
  if(!r.ok){document.getElementById('out').textContent='保存失败: '+account;return}}
 document.getElementById('out').textContent='矩阵已保存，已生效';setTimeout(()=>location.reload(),600)}
</script>`
}

/* ── 页面：实例管理 ──────────────────────────────────────────────────────── */

function instancesPage({ manifest, getState, dataDir, query }) {
  const state = getState()
  const filter = query.get('state') ?? 'all'
  const drift = readJson(dataDir, 'drift.json', { checks: {} }).checks
  const needsAttention = (s) => ['crashed', 'unhealthy', 'failed', 'restarting'].includes(s)
  const match = (s) => filter === 'all' || (filter === 'attention' ? needsAttention(s) : filter === s)
  const shown = manifest.instances.filter((spec) => match(state.instances[spec.id]?.state ?? 'stopped'))
  const running = manifest.instances.filter((s) => state.instances[s.id]?.state === 'running').length
  const attention = manifest.instances.filter((s) => needsAttention(state.instances[s.id]?.state ?? 'stopped')).length
  const totalDisk = manifest.instances.reduce((sum, s) => sum + (state.instances[s.id]?.diskBytes ?? 0), 0)
  const stats = `<div class="statgrid">
<div class="stat"><div class="k">实例数</div><div class="v">${running} <span style="font-size:.85rem;color:var(--muted)">/ ${manifest.instances.length} 运行中</span></div><div class="n">一人一实例 · 独立目录</div></div>
<div class="stat"><div class="k">需处理</div><div class="v">${attention}</div><div class="n">待重启或异常的实例</div></div>
<div class="stat"><div class="k">异常实例</div><div class="v">${manifest.instances.filter((s) => ['crashed', 'failed'].includes(state.instances[s.id]?.state)).length}</div><div class="n">supervisor 自动重启守护</div></div>
<div class="stat"><div class="k">磁盘占用</div><div class="v">${(totalDisk / 1024 / 1024).toFixed(1)} MB</div><div class="n">全部 home 合计</div></div>
</div>`
  const tab = (key, label) => `<a class="${filter === key ? 'on' : ''}" href="/console/instances${key === 'all' ? '' : `?state=${key}`}">${label}</a>`
  const tabs = `<div class="tabs">${tab('all', `全部 (${manifest.instances.length})`)}${tab('running', '运行中')}${tab('attention', '需处理')}${tab('stopped', '已停止')}</div>`
  const accounts = listAccounts(dataDir)
  const rows = shown.map((spec) => {
    const rec = state.instances[spec.id] ?? { state: '—' }
    const mem = rec.memoryKB ? `${(rec.memoryKB / 1024).toFixed(1)} MB` : '—'
    const disk = rec.diskBytes !== null && rec.diskBytes !== undefined ? `${(rec.diskBytes / 1024 / 1024).toFixed(1)} MB` : '—'
    const a = accounts.find((x) => x.account === spec.account)
    const vk = activeVkeyFor(dataDir, spec.account)
    const granted = vk === undefined ? '—' : vk.models === '*' ? '全部' : `${vk.models.length} 个`
    const effCount = drift[spec.id]?.effectiveSet?.models?.length
    const driftMark = effCount !== undefined && vk !== undefined && vk.models !== '*' && vk.models.length !== effCount
      ? ' <span class="chip red">差异</span>' : ''
    const eff = effCount === undefined ? '—' : `${effCount} 个${driftMark}`
    const uptime = rec.startedAt && rec.pid ? `${Math.round((Date.now() - rec.startedAt) / 60000)} 分钟` : '—'
    const lastActivity = rec.health?.lastOkAt ? new Date(rec.health.lastOkAt).toISOString().slice(5, 16).replace('T', ' ') : '—'
    const ops = ['restart', 'stop', 'start'].map((op) => {
      const disabled = (op === 'start' && rec.pid) || (op === 'restart' && !rec.pid)
      return `<form class="inline" onsubmit="api(event,'/console/api/instance/${op}')"><input type="hidden" name="id" value="${spec.id}"><button ${disabled ? 'disabled' : ''}>${op === 'restart' ? '重启' : op === 'stop' ? '停止' : '启动'}</button></form>`
    }).join('')
    return `<tr><td>${avatar(a?.displayName)}${esc(a?.displayName ?? spec.id)}<div style="font-size:.72rem;color:var(--faint)">${esc(spec.account)}</div></td>
<td>${stateChip(rec.state)}</td>
<td>:${spec.port}<div style="font-size:.72rem;color:var(--faint)">pid ${rec.pid ?? '—'} · uid ${spec.uid}</div><div style="font-size:.72rem;color:var(--faint)">隔离 ${spec.id}</div></td>
<td>已授权 ${granted} → 实例内渲染 ${eff}</td>
<td>内存 ${mem}<div style="font-size:.72rem;color:var(--faint)">磁盘 ${disk}</div></td>
<td>${uptime}<div style="font-size:.72rem;color:var(--faint)">活动 ${lastActivity}</div></td>
<td>${ops}<a class="btn" href="/console/instances/log?id=${spec.id}">日志</a></td></tr>`
  }).join('')
  return `
${stats}
${tabs}
<table><tr><th>成员</th><th>状态</th><th>端口 · 进程 · 隔离</th><th>模型（已授权 → 实例内渲染）</th><th>资源</th><th>运行时长 · 最后活动</th><th>操作</th></tr>${rows || '<tr><td colspan="7">该筛选下无实例</td></tr>'}</table>
<p class="mut" style="font-size:.82rem">「同步配置」与「重发说明」属插件治理生效链（阶段 6），当前经 CLI 投放后重启即对齐；日志为运行日志，不含会话内容。</p>
<script>
async function api(ev,path){ev.preventDefault();
 const f=new FormData(ev.target);const payload={};f.forEach((v,k)=>payload[k]=v);
 const r=await fetch(path,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(payload)});
 if(r.ok)setTimeout(()=>location.reload(),900)}
</script>`
}

/* ── 页面：实例日志 ──────────────────────────────────────────────────────── */

function instanceLogPage({ manifest, dataDir, query }) {
  const id = query.get('id') ?? ''
  if (!manifest.instances.some((s) => s.id === id)) return '<p class="bad">未知实例</p>'
  let content = '(无日志)'
  try {
    content = readFileSync(join(dataDir, 'logs', `${id}.log`), 'utf8').trim().split('\n').slice(-80).map(esc).join('\n')
  } catch { /* 尚无日志 */ }
  return `<p><a href="/console/instances">← 实例管理</a></p><pre class="log">${content}</pre>`
}

/* ── 页面：插件管理 ──────────────────────────────────────────────────────── */

function pluginsPage({ dataDir, manifest, getState }) {
  const desired = readJson(dataDir, 'plugins.json', { instances: {} })
  const state = getState()
  const names = new Set()
  let staged = 0
  for (const list of Object.values(desired.instances)) {
    for (const p of list) {
      if (p.state !== 'removed') names.add(p.name)
      if (p.state === 'staged') staged += 1
    }
  }
  const profileBundles = (() => {
    for (const spec of manifest.instances) {
      const file = join(dataDir, 'homes', spec.id, 'profiles', 'web', 'package.json')
      try {
        return JSON.parse(readFileSync(file, 'utf8')).dsh?.profile?.bundles ?? []
      } catch { /* 取第一个可用 profile */ }
    }
    return []
  })()
  const stats = `<div class="statgrid">
<div class="stat"><div class="k">已接入插件</div><div class="v">${names.size} 个</div><div class="n">第三方插件与平台共享一个进程树</div></div>
<div class="stat"><div class="k">需要安装</div><div class="v">${staged} 个实例</div><div class="n">平台默认认为新增实例自动生效</div></div>
<div class="stat"><div class="k">待生效</div><div class="v">${staged} 个实例</div><div class="n">暂存后等待重启的改动</div></div>
<div class="stat"><div class="k">投放方式</div><div class="v" style="font-size:1rem">CLI</div><div class="n">真启动预检强制 · 装坏自动拦截</div></div>
</div>`
  const rows = manifest.instances.map((spec) => {
    const list = desired.instances[spec.id] ?? []
    const items = list.length === 0
      ? '<td colspan="2">—</td>'
      : list.map((p) => `<td>${esc(p.name)}</td><td>${esc(p.spec === p.name ? '(最新)' : p.spec)} · ${p.state === 'removed' ? '<span class="chip gray">已移除</span>' : p.state === 'staged' ? '<span class="chip yellow">暂存（重启生效）</span>' : `<span class="chip green">${esc(p.state)}</span>`}</td>`).join('')
    const running = state.instances[spec.id]?.state === 'running'
    return `<tr><td>${spec.id}</td><td>${running ? '<span class="chip green">运行中</span>' : stateChip(state.instances[spec.id]?.state)}</td>${items}</tr>`
  }).join('')
  const bundles = profileBundles.map((b) => `<span class="chip blue">${esc(b)}</span>`).join(' ')
  return `
${stats}
<h2 class="sect">平台默认插件集</h2>
<p class="mut" style="font-size:.85rem">每个实例 profile 在此集合之上叠加第三方插件。<span style="font-size:.85rem">${bundles || '—'}</span></p>
<h2 class="sect">插件 × 实例（期望态）</h2>
<table><tr><th>实例</th><th>实例状态</th><th>插件</th><th>版本 / 状态</th></tr>${rows}</table>
<p class="mut" style="font-size:.82rem">插件投放（含真启动预检）当前经 CLI：<code>node supervisor.mjs plugin-push --plugin &lt;spec&gt; --ids &lt;id&gt;</code>；暂存后重启生效，装坏由预检拦截。异步投放任务队列落地后，此页将接管安装/暂存/预检/回滚操作。</p>`
}

/* ── 路由入口 ────────────────────────────────────────────────────────────── */

function json(res, status, value) {
  res.writeHead(status, { 'content-type': 'application/json; charset=utf-8' })
  res.end(JSON.stringify(value))
}

function readBody(req) {
  return new Promise((resolveBody) => {
    let raw = ''
    req.on('data', (c) => { raw += c })
    req.on('end', () => {
      try { resolveBody(JSON.parse(raw || '{}')) } catch { resolveBody({}) }
    })
  })
}

function enqueueInstanceControl(dataDir, action, id) {
  writeFileSync(join(dataDir, 'control.json'), `${JSON.stringify({ action, id, at: Date.now() })}\n`)
}

async function handleApi({ req, res, path, dataDir, manifest }) {
  const body = await readBody(req)
  const account = typeof body.account === 'string' ? body.account : ''
  try {
    switch (path) {
      case '/console/api/member/create': {
        const password = body.password || `LyZ-${Math.random().toString(36).slice(2, 11)}`
        const record = addAccount(dataDir, {
          account,
          instanceId: body.instance,
          role: body.role === 'auditor' ? 'auditor' : 'employee',
          displayName: body.displayName || undefined,
          password,
        })
        const { token } = issueVkey(dataDir, { account: record.account, instanceId: record.instanceId, models: '*' })
        json(res, 200, { ok: true, account: record.account, instance: record.instanceId, password, vkey: token })
        return
      }
      case '/console/api/member/quota': {
        const tokens = body.tokens === '' || body.tokens === undefined || body.tokens === null ? null : Number(body.tokens)
        if (!Number.isInteger(tokens) || tokens < 0) { json(res, 400, { error: 'tokens 必须是非负整数，留空 = 不限' }); return }
        setQuota(dataDir, { account, monthlyTokens: tokens })
        json(res, 200, { ok: true, quota: tokens ?? '不限' })
        return
      }
      case '/console/api/member/reset-password': {
        const password = `LyZ-${Math.random().toString(36).slice(2, 11)}`
        setPassword(dataDir, account, password)
        json(res, 200, { ok: true, password })
        return
      }
      case '/console/api/member/disable': {
        const store = loadAccounts(dataDir)
        const rec = store.accounts.find((a) => a.account === account)
        if (rec === undefined) { json(res, 404, { error: '账号不存在' }); return }
        rec.disabled = true
        saveAccounts(dataDir, store)
        try { revokeVkey(dataDir, { account }) } catch { /* 本就没有钥匙 */ }
        json(res, 200, { ok: true })
        return
      }
      case '/console/api/member/enable': {
        const store = loadAccounts(dataDir)
        const rec = store.accounts.find((a) => a.account === account)
        if (rec === undefined) { json(res, 404, { error: '账号不存在' }); return }
        rec.disabled = false
        saveAccounts(dataDir, store)
        const history = readJson(dataDir, 'vkeys.json', { vkeys: [] }).vkeys.filter((v) => v.account === account)
        const models = history.at(-1)?.models ?? '*'
        issueVkey(dataDir, { account, instanceId: rec.instanceId, models })
        json(res, 200, { ok: true, models })
        return
      }
      case '/console/api/member/models': {
        const models = body.models === '*' ? '*' : Array.isArray(body.models) ? body.models.filter((m) => typeof m === 'string') : []
        setVkeyModels(dataDir, { account, models })
        json(res, 200, { ok: true, models })
        return
      }
      case '/console/api/instance/restart':
      case '/console/api/instance/stop':
      case '/console/api/instance/start': {
        const id = typeof body.id === 'string' ? body.id : ''
        if (!manifest.instances.some((s) => s.id === id)) { json(res, 404, { error: '未知实例' }); return }
        const action = path.split('/').at(-1)
        enqueueInstanceControl(dataDir, action, id)
        json(res, 200, { ok: true, action, id })
        return
      }
      default:
        json(res, 404, { error: 'unknown console api' })
    }
  } catch (error) {
    json(res, 400, { error: String(error?.message ?? error) })
  }
}

/**
 * 处理 /console 路径的全部请求（gateway 在裸 portal 分支里调用）。
 * 认证由 gateway 计算后传入；页面需登录且仅 admin；POST API 仅 admin，
 * 并在带 Origin 时校验同源（配合 SameSite=Strict 双重 CSRF 防线）。
 * @returns true 表示已响应，gateway 不再处理。
 */
export function handleConsole({ req, res, url, auth, loginPage, manifest, getState, dataDir }) {
  if (!url.pathname.startsWith('/console')) return false
  const path = url.pathname
  const query = url.searchParams

  if (req.method === 'GET') {
    if (auth.error !== undefined) {
      res.writeHead(401, { 'content-type': 'text/html; charset=utf-8' })
      res.end(loginPage())
      return true
    }
    if (auth.record.role !== 'admin') {
      res.writeHead(403, { 'content-type': 'text/plain; charset=utf-8' })
      res.end('管理台仅限平台管理员。')
      return true
    }
    const ctx = { dataDir, manifest, getState, query }
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' })
    if (path === '/console') res.end(SHELL('总览', '', manifest, getState, dataDir, overviewPage(ctx)))
    else if (path === '/console/members') res.end(SHELL('成员与额度', 'members', manifest, getState, dataDir, membersPage(ctx)))
    else if (path === '/console/models') res.end(SHELL('模型与权限', 'models', manifest, getState, dataDir, modelsPage(ctx)))
    else if (path === '/console/instances') res.end(SHELL('实例管理', 'instances', manifest, getState, dataDir, instancesPage(ctx)))
    else if (path === '/console/instances/log') res.end(SHELL('实例日志', 'instances', manifest, getState, dataDir, instanceLogPage(ctx)))
    else if (path === '/console/plugins') res.end(SHELL('插件管理', 'plugins', manifest, getState, dataDir, pluginsPage(ctx)))
    else { res.writeHead(404, { 'content-type': 'text/plain; charset=utf-8' }); res.end('unknown console page') }
    return true
  }

  if (req.method === 'POST' && path.startsWith('/console/api/')) {
    if (auth.error !== undefined) { json(res, 401, { error: 'unauthenticated' }); return true }
    if (auth.record.role !== 'admin') { json(res, 403, { error: 'admin only' }); return true }
    const origin = req.headers.origin
    if (origin !== undefined) {
      try {
        if (new URL(origin).host !== (req.headers.host ?? '')) { json(res, 403, { error: 'cross-origin refused' }); return true }
      } catch { json(res, 403, { error: 'bad origin' }); return true }
    }
    void handleApi({ req, res, path, dataDir, manifest }).catch(() => json(res, 500, { error: 'console api crashed' }))
    return true
  }
  return false
}
