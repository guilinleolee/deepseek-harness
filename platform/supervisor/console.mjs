/**
 * 卡巴格企业平台 · 管理台（视觉层按 5 页设计图打磨）。
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
import { addAccount, listAccounts, loadAccounts, saveAccounts, setPassword, updateAccount } from './gateway.mjs'
import { addModel, issueVkey, listUpstreams, removeModel, revokeVkey, setQuota, setUpstream, setVkeyModels } from './relay.mjs'
import { pluginCatalog } from './plugins-gov.mjs'

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
  return `<!doctype html><html lang="zh"><head><meta charset="utf-8"><title>卡巴格 · ${title}</title><style>${CSS}</style></head>
<body>
<nav><div class="brand"><span class="mark">卡</span><div><div class="name">卡巴格</div><div class="sub">DASHBOARD CONSOLE</div></div></div>${nav}</nav>
<main>
<div class="pagehead"><div><h1>${title}</h1><div class="sub">${esc(SUBTITLES[title] ?? '')}</div></div><div class="statusbadge">${badge}<span>${nowStamp()}</span></div></div>
${body}
<footer>卡巴格 · 企业 AI 管理台</footer>
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
  const depFilter = query.get('dep') ?? ''
  const d = new Date()
  const month = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
  const usage = readJson(dataDir, 'usage.json', { months: {} }).months[month] ?? {}
  const state = getState()
  const all = listAccounts(dataDir)
  const departments = [...new Set(all.map((a) => a.department ?? '未分配'))]
  const accounts = all.filter((a) => {
    if (q !== '' && !a.account.toLowerCase().includes(q) && !String(a.displayName ?? '').toLowerCase().includes(q)) return false
    if (depFilter !== '' && (a.department ?? '未分配') !== depFilter) return false
    return true
  })
  const rows = accounts.map((a) => {
    const e = usage[a.account] ?? { tokensIn: 0, tokensOut: 0, requests: 0 }
    const used = e.tokensIn + e.tokensOut
    const vk = activeVkeyFor(dataDir, a.account)
    const chips = vk === undefined ? '<span class="chip gray">无钥匙</span>' : vk.models === '*'
      ? '<span class="chip teal">全部模型</span>'
      : vk.models.slice(0, 3).map((m) => `<span class="chip teal">${esc(m)}</span>`).join('') + (vk.models.length > 3 ? `<span class="chip gray">+${vk.models.length - 3}</span>` : '')
    const quota = a.monthlyTokens
    const roleOptions = ['admin', 'auditor', 'employee'].map((r) => {
      const [label] = { admin: ['管理员'], auditor: ['审计员'], employee: ['成员'] }[r]
      return `<option value="${r}" ${a.role === r ? 'selected' : ''}>${label}</option>`
    }).join('')
    return `<tr><td>${avatar(a.displayName)}${esc(a.displayName)}</td><td>${esc(a.account)}</td>
<td>${esc(a.department ?? '未分配')}</td><td>${roleChip(a.role)}</td><td>${esc(a.instanceId)}</td>
<td>${chips}</td><td>${a.disabled ? '<span class="chip red">已禁用</span>' : '<span class="chip green">正常</span>'}</td>
<td>${quotaCell(used, Number.isFinite(quota) ? quota : Number.POSITIVE_INFINITY)}</td><td>${e.requests}</td>
<td>
<form class="inline" onsubmit="api(event,'/console/api/member/update',this)"><input type="hidden" name="account" value="${esc(a.account)}"><input name="department" size="6" value="${esc(a.department ?? '未分配')}" title="部门"><button>改部门</button></form>
<form class="inline" onsubmit="api(event,'/console/api/member/update',this)"><input type="hidden" name="account" value="${esc(a.account)}"><select name="role">${roleOptions}</select><button>改角色</button></form>
<form class="inline" onsubmit="api(event,'/console/api/member/quota',this)"><input type="hidden" name="account" value="${esc(a.account)}"><input name="tokens" size="8" placeholder="额度/空=不限"><button>改额度</button></form>
<form class="inline" onsubmit="api(event,'/console/api/member/reset-password',this)"><input type="hidden" name="account" value="${esc(a.account)}"><button>重置密码</button></form>
${a.disabled
    ? `<form class="inline" onsubmit="api(event,'/console/api/member/enable',this)"><input type="hidden" name="account" value="${esc(a.account)}"><button>启用</button></form>`
    : `<form class="inline" onsubmit="api(event,'/console/api/member/disable',this)"><input type="hidden" name="account" value="${esc(a.account)}"><button class="warn">禁用</button></form>`}</td></tr>`
  }).join('')
  const instanceOptions = manifest.instances.map((s) => `<option value="${s.id}">${s.id}（${state.instances[s.id]?.state ?? '—'}）</option>`).join('')
  const depOptions = departments.map((dep) => `<option value="${esc(dep)}">${esc(dep)}</option>`).join('')
  return `
<div class="searchbox" method="get">
<form class="searchbox" method="get" style="margin:0"><input name="q" value="${esc(q)}" placeholder="搜索姓名 / 账号"><button class="primary">搜索</button><select name="dep" onchange="this.form.submit()"><option value="">全部部门</option>${depOptions}</select>${q !== '' || depFilter !== '' ? '<a class="btn" href="/console/members">清除</a>' : ''}</form>
</div>
<table><tr><th>成员</th><th>账号</th><th>部门</th><th>角色</th><th>实例</th><th>可见模型</th><th>状态</th><th>本月已用/额度</th><th>请求</th><th>操作</th></tr>${rows || '<tr><td colspan="10">无匹配成员</td></tr>'}</table>
<h2 class="sect">添加成员</h2>
<form class="panel" onsubmit="createMember(event)">
<div style="margin-bottom:.5rem">账号 <input name="account" placeholder="name@company" required> 显示名 <input name="displayName"> 部门 <input name="department" placeholder="如 设计部"></div>
<div style="margin-bottom:.5rem">角色 <select name="role"><option value="employee">成员</option><option value="auditor">审计员</option><option value="admin">管理员</option></select> 实例 <select name="instance">${instanceOptions}</select></div>
<div>密码 <input name="password" placeholder="留空自动生成"> <button class="primary">创建</button></div>
</form>
<h2 class="sect">IdP 名册同步</h2>
<form class="panel" onsubmit="importIdp(event)">
<div style="margin-bottom:.5rem"><span class="mut">粘贴 IdP/HR 导出的名册 JSON（字段：account、displayName、department、role、instance）：</span></div>
<textarea name="roster" rows="6" style="width:100%" placeholder='[{"account":"wang@company","displayName":"小王","department":"设计部","role":"employee","instance":"e02"}]'></textarea>
<div style="margin:.5rem 0">默认实例 <select name="instance">${instanceOptions}</select> ｜ <label><input type="checkbox" name="disable-missing"> 名册中不存在的账号自动禁用</label> <button class="primary">导入同步</button></div>
</form>
<p class="mut" style="font-size:.82rem">同步对账：名册中没有的账号创建（随机密码，需转交）；已有的更新部门/角色/显示名；勾选自动禁用后，名册缺失的非管理员账号将被禁用并下线。OIDC/LDAP 直连属待接入（接口已留）。</p>
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
async function importIdp(ev){ev.preventDefault();
 let members=[];try{members=JSON.parse(ev.target.roster.value||'[]')}catch{document.getElementById('out').textContent='名册 JSON 格式错误';return}
 const payload={members,defaultInstance:ev.target.instance.value,disableMissing:ev.target['disable-missing'].checked};
 const r=await fetch('/console/api/idp/import',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(payload)});
 const j=await r.json();
 if(r.ok){document.getElementById('out').textContent='同步完成：新建 '+j.created.length+'、更新 '+j.updated.length+'、无变化 '+j.unchanged+'、禁用缺失 '+(j.missingDisabled||[]).length+(j.created.length?('\\n新账号凭证：\\n'+j.created.map(c=>c.account+' / '+c.password).join('\\n')):'');
 if(j.created.length===0)setTimeout(()=>location.reload(),1200)}else{document.getElementById('out').textContent='HTTP '+r.status+' '+JSON.stringify(j)}}
</script>`
}

function newProviderPage() {
  const PRESETS = [
    { name: 'DeepSeek', baseURL: 'https://api.deepseek.com', website: 'https://platform.deepseek.com', note: 'DeepSeek 官方', models: 'deepseek-chat,deepseek-reasoner' },
    { name: 'Zhipu GLM', baseURL: 'https://open.bigmodel.cn/api/paas/v4', website: 'https://open.bigmodel.cn', note: '智谱 GLM 官方', models: 'glm-4.7,glm-5.2,glm-5.3,glm-5.3-flash' },
    { name: 'Kimi', baseURL: 'https://api.moonshot.cn/v1', website: 'https://platform.moonshot.cn', note: '月之暗面', models: 'kimi-k2-0905-preview' },
    { name: 'MiniMax', baseURL: 'https://api.minimaxi.com/v1', website: 'https://platform.minimaxi.com', note: 'MiniMax 官方', models: 'MiniMax-M2' },
    { name: 'SiliconFlow', baseURL: 'https://api.siliconflow.cn/v1', website: 'https://siliconflow.cn', note: '硅基流动', models: '' },
    { name: 'OpenRouter', baseURL: 'https://openrouter.ai/api/v1', website: 'https://openrouter.ai', note: '', models: '' },
    { name: 'ModelScope', baseURL: 'https://api-inference.modelscope.cn/v1', website: 'https://modelscope.cn', note: '魔搭社区', models: '' },
  ]
  const chips = `<button type="button" class="chip gray preset on" data-i="-1">自定义配置</button>` +
    PRESETS.map((p, i) => `<button type="button" class="chip gray preset" data-i="${i}">${esc(p.name)}</button>`).join('')
  return `
<div class="presetbox">
<div class="k" style="font-size:.78rem;color:var(--muted);margin-bottom:.5rem">预设供应商 <span class="mut">（点选自动填充请求地址；自定义配置需手动填写所有必填字段）</span></div>
<div style="display:flex;flex-wrap:wrap;gap:.4rem">${chips}</div>
<p style="color:#ffd166;font-size:.82rem;margin:.6rem 0 0">💡 自定义配置需手动填写所有必填字段</p>
</div>
<h2 class="sect">供应商信息</h2>
<form id="pform" class="panel" style="display:block;max-width:860px" onsubmit="addProvider(event)">
<div style="margin-bottom:.7rem">供应商名称 <input name="name" size="34" placeholder="例如：公司专用账号" required> ｜ 备注 <input name="note" size="30" placeholder="例如：公司专用账号"></div>
<div style="margin-bottom:.7rem">官网链接 <input name="website" size="44" placeholder="https://example.com（可选）"></div>
<div style="margin-bottom:.7rem">API Key <input name="apiKey" size="44" placeholder="只需要填这里，下方配置会自动填充" required></div>
<div style="margin-bottom:.7rem">请求地址 <input name="baseURL" size="44" placeholder="https://your-api-endpoint.com" required>
<span class="mut" style="font-size:.82rem">（兼容 OpenAI Chat Completions 的服务端点地址，不要以斜杠结尾）</span></div>
<div style="margin-bottom:.7rem">模型列表（逗号分隔） <input name="models" size="44" placeholder="如 glm-4.7,glm-5.2（供成员矩阵授权）"></div>
<div style="display:flex;justify-content:flex-end;gap:.6rem;margin-top:1rem">
<button type="button" class="btn" onclick="location.href='/console/models'">取消</button>
<button class="primary">＋ 添加</button>
</div>
</form>
<p class="mut" style="font-size:.82rem">添加后该供应商立即进入 Relay 上游表；成员可在“模型与权限”矩阵中被授权其模型。真实 Key 仅存于服务端，页面只显示指纹。</p>
<script>
const PRESETS=${'${'}JSON.stringify(PRESETS)${'}'};
document.querySelectorAll('.preset').forEach(function(b){
 b.addEventListener('click',function(){
  document.querySelectorAll('.preset').forEach(function(x){x.classList.remove('on')});b.classList.add('on');
  var i=parseInt(b.dataset.i);var f=document.getElementById('pform');
  if(i<0){f.baseURL.value='';f.website.value='';f.note.value='';f.models.value='';return}
  var p=PRESETS[i];f.baseURL.value=p.baseURL;f.website.value=p.website;f.note.value=p.note||'';f.models.value=p.models||'';
  f.name.focus()})
})
</script>`
}

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
    const del = `<button class="warn" onclick="removeModel('${esc(u?.name ?? '')}','${esc(m)}',${usedBy})">删除</button>`
    return `<tr><td>${esc(m)}</td><td>${esc(u?.name ?? '—')}</td><td>${meta ? esc(meta.context) : '—'} / ${meta ? esc(meta.maxOutput) : '—'}</td>
<td>${meta ? esc(meta.mIn) : '—'}</td><td>${meta ? esc(meta.mOut) : '—'}</td><td>${meta ? esc(meta.mCacheR) : '—'}</td><td>${meta ? esc(meta.mCacheW) : '—'}</td>
<td>${usedBy}</td><td><span class="chip green">已启用</span></td><td>${del}</td></tr>`
  }).join('')
  const upstreamOptions = upstreams.map((u) => `<option value="${esc(u.name)}">${esc(u.name)}</option>`).join('')
  const matrix = modelsMatrix({ dataDir, accounts, catalog })
  return `
<div style="margin-bottom:.8rem;text-align:right"><a class="btn primary" href="/console/providers/new">＋ 新建模型供应商</a></div>
<h2 class="sect">上游提供方 <span class="mut" style="font-size:.8rem">真实 Key 只存在于 Relay 进程</span></h2>
<table><tr><th>提供方</th><th>端点（BaseURL）</th><th>上游 Key</th><th>模型数</th><th>状态</th></tr>${upstreamRows}</table>
<h2 class="sect">可用模型</h2>
<table><tr><th>模型</th><th>提供方</th><th>上下文 / 最大输出</th><th>输入倍率</th><th>输出倍率</th><th>缓存读</th><th>缓存写</th><th>成员可见</th><th>状态</th><th>操作</th></tr>${modelRows}</table>
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
async function removeModel(upstream,model,usedBy){
 if(!confirm('删除模型 '+model+'？'+(usedBy>0?('（'+usedBy+' 个成员的白名单仍引用它，调用将收到"无上游"提示）'):'')))return;
 const r=await fetch('/console/api/model/remove',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({upstream:upstream,model:model})});
 if(r.ok)setTimeout(()=>location.reload(),600);else alert('删除失败: '+await r.text())}
</script>`
}

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
  writeFileSync(join(dataDir, 'control.json'), `${JSON.stringify({ action, id, at: Date.now() })}
`)
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
      case '/console/api/member/update': {
        const record = updateAccount(dataDir, account, {
          role: body.role,
          department: body.department,
          displayName: body.displayName,
        })
        json(res, 200, { ok: true, role: record.role, department: record.department ?? '未分配' })
        return
      }
      case '/console/api/idp/import': {
        const members = Array.isArray(body.members) ? body.members : []
        if (members.length === 0) { json(res, 400, { error: 'members 不能为空' }); return }
        const defaultInstance = typeof body.defaultInstance === 'string' ? body.defaultInstance : manifest.instances[0].id
        const result = { created: [], updated: [], unchanged: 0, missingDisabled: [] }
        const seen = new Set()
        for (const m of members) {
          if (!m.account) continue
          seen.add(m.account)
          const role = ['admin', 'auditor', 'employee'].includes(m.role) ? m.role : 'employee'
          const store = loadAccounts(dataDir)
          const rec = store.accounts.find((a) => a.account === m.account)
          if (rec === undefined) {
            const password = `LyZ-${Math.random().toString(36).slice(2, 11)}`
            const record = addAccount(dataDir, {
              account: m.account,
              instanceId: m.instance ?? defaultInstance,
              role,
              displayName: m.displayName || undefined,
              department: m.department ?? '未分配',
              password,
            })
            const { token } = issueVkey(dataDir, { account: record.account, instanceId: record.instanceId, models: '*' })
            result.created.push({ account: record.account, password, vkey: token, instance: record.instanceId })
          } else {
            let changed = false
            if (m.department !== undefined && m.department !== rec.department) { rec.department = m.department; changed = true }
            if (role !== rec.role) { rec.role = role; changed = true }
            if (m.displayName !== undefined && m.displayName !== rec.displayName) { rec.displayName = m.displayName; changed = true }
            if (rec.disabled === true) { rec.disabled = false; changed = true }
            if (changed) { saveAccounts(dataDir, store); result.updated.push({ account: m.account }) } else result.unchanged += 1
          }
        }
        if (body.disableMissing === true) {
          const store = loadAccounts(dataDir)
          for (const rec of store.accounts) {
            if (!seen.has(rec.account) && !rec.disabled && rec.role !== 'admin') {
              rec.disabled = true
              rec.tokenEpoch = (rec.tokenEpoch ?? 0) + 1
              try { revokeVkey(dataDir, { account: rec.account }) } catch { /* 无钥匙 */ }
              result.missingDisabled.push(rec.account)
            }
          }
          saveAccounts(dataDir, store)
        }
        json(res, 200, { ok: true, ...result })
        return
      }
      case '/console/api/provider/add': {
        const name = typeof body.name === 'string' ? body.name.trim() : ''
        const baseURL = typeof body.baseURL === 'string' ? body.baseURL.trim() : ''
        if (name === '' || baseURL === '') { json(res, 400, { error: '供应商名称与请求地址必填' }); return }
        if (listUpstreams(dataDir).some((u) => u.name === name)) { json(res, 409, { error: '供应商已存在: ' + name }); return }
        const models = typeof body.models === 'string' ? body.models.split(',').map((x) => x.trim()).filter(Boolean) : []
        if (models.length === 0) { json(res, 400, { error: '至少提供一个模型 ID（后续可在供应商管理里补充）' }); return }
        try {
          setUpstream(dataDir, { name, baseURL, models, apiKey: body.apiKey, note: body.note || undefined, website: body.website || undefined })
          json(res, 200, { ok: true, name, models })
        } catch (error) {
          json(res, 400, { error: String(error?.message ?? error) })
        }
        return
      }
      case '/console/api/model/add': {
        if (typeof body.upstream !== 'string' || typeof body.model !== 'string' || body.model === '') {
          json(res, 400, { error: 'upstream 与 model 必填' })
          return
        }
        const meta = {}
        for (const k of ['context', 'maxOutput', 'mIn', 'mOut', 'mCacheR', 'mCacheW']) {
          if (typeof body[k] === 'string' && body[k] !== '') meta[k] = body[k]
        }
        try {
          addModel(dataDir, { upstream: body.upstream, model: body.model, meta: Object.keys(meta).length ? meta : undefined })
          json(res, 200, { ok: true, upstream: body.upstream, model: body.model })
        } catch (error) {
          json(res, 400, { error: String(error?.message ?? error) })
        }
        return
      }
      case '/console/api/model/remove': {
        if (typeof body.upstream !== 'string' || typeof body.model !== 'string') {
          json(res, 400, { error: 'upstream 与 model 必填' })
          return
        }
        try {
          removeModel(dataDir, { upstream: body.upstream, model: body.model })
          json(res, 200, { ok: true })
        } catch (error) {
          json(res, 400, { error: String(error?.message ?? error) })
        }
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
export function handleConsole({ req, res, url, auth, loginPage, manifest, getState, dataDir, runner }) {
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
    if (path === '/console/providers/new') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' })
      res.end(SHELL('添加模型供应商', 'models', manifest, getState, dataDir, newProviderPage()))
      return true
    }
    if (path === '/console/api/plugin/jobs') {
      json(res, 200, { jobs: runner.list() })
      return true
    }
    const ctx = { dataDir, manifest, getState, query }
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' })
    if (path === '/console') res.end(SHELL('总览', '', manifest, getState, dataDir, overviewPage(ctx)))
    else if (path === '/console/members') res.end(SHELL('成员与额度', 'members', manifest, getState, dataDir, membersPage(ctx)))
    else if (path === '/console/models') res.end(SHELL('模型与权限', 'models', manifest, getState, dataDir, modelsPage(ctx)))
    else if (path === '/console/instances') res.end(SHELL('实例管理', 'instances', manifest, getState, dataDir, instancesPage(ctx)))
    else if (path === '/console/instances/log') res.end(SHELL('实例日志', 'instances', manifest, getState, dataDir, instanceLogPage(ctx)))
    else if (path === '/console/plugins') res.end(SHELL('插件管理', 'plugins', manifest, getState, dataDir, pluginsPage({ ...ctx, runner })))
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
    if (path === '/console/api/plugin/job') {
      void readBody(req).then((body) => {
        try {
          const job = runner.enqueue({ type: body.type, spec: body.spec, ids: body.ids, skipPrecheck: body.skipPrecheck })
          json(res, 200, { ok: true, job: { id: job.id, state: job.state } })
        } catch (error) {
          json(res, 409, { error: String(error?.message ?? error) })
        }
      })
      return true
    }
    void handleApi({ req, res, path, dataDir, manifest }).catch((error) => {
      console.error('[console] api crashed:', error?.stack ?? error)
      try { json(res, 500, { error: 'console api crashed' }) } catch { /* 已响应 */ }
    })
    return true
  }
  return false
}
