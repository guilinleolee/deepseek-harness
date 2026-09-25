/**
 * 卡巴格企业平台 · 管理台（视觉层按 5 页设计图打磨 + 栏目规划 v2 一期）。
 *
 * 页面与操作 API：
 * - /console            总览：统计卡 + 告警卡（额度将尽/失败登录/审计摘要）+ 实例与用量
 * - /console/members    成员与额度：搜索、建号、点数额度、重置密码、禁用/启用
 * - /console/roles      部门与角色：分组倍率编辑 + 角色权限矩阵只读展示（栏目 v2 六节）
 * - /console/models     模型与权限：上游提供方、可用模型（含倍率行内编辑）、授权矩阵
 * - /console/instances  实例管理：统计卡 + 筛选标签 + 日志查看 + 重启/停止/启动
 * - /console/plugins    插件管理：统计卡 + 平台默认插件集 + 期望态视图
 * - /console/audit      安全与审计：审计日志筛选/导出 + 登录安全设置（栏目 v2 一期）
 * 页面与只读 GET API 放行 admin/auditor（employee 拒入）；变更类 POST 仅 admin，
 * auditor 得 403「审计员为只读角色」。全部变更端点与登录/配额/导出/安全设置
 * 事件在 data/audit.jsonl 留痕（audit.mjs，result=ok/deny/fail）。
 */
import { readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { addAccount, getOrCreateSecret, listAccounts, loadAccounts, saveAccounts, setPassword, updateAccount } from './gateway.mjs'
import { addModel, issueVkey, listUpstreams, monthKey, removeModel, removeUpstream, revokeVkey, setQuota, setUpstream, setVkeyModels } from './relay.mjs'
import { pluginCatalog } from './plugins-gov.mjs'
import { auditAppend, auditQuery, clientIp } from './audit.mjs'
import { checkPasswordPolicy, generatePassword, loadSecurityConfig, saveSecurityConfig } from './security.mjs'
import { fmtPoints, initQuotas, loadRatios, resolveRatios, setGroupRatio, setModelRatio } from './quotas.mjs'
import { denyForRole, loadToolPolicy, saveToolPolicy, syncAllHomes, syncInstanceHome, TOOL_GROUPS } from './toolpolicy.mjs'
import { createInvite, listOpenInvites, revokeInvite } from './invites.mjs'
import { clearTwofa, deriveKey, isTwofaEnabled } from './totp.mjs'
import { loadNotifyConfig, NOTIFY_SUBJECT_PREFIX, saveNotifyConfig, sendMail } from './notify.mjs'
import { authenticateServiceToken } from './service-tokens.mjs'
import { isValidEntityName } from './gateway.mjs'

const PAGES = ['members', 'roles', 'models', 'instances', 'plugins', 'audit']
const PAGE_TITLES = { members: '成员与额度', roles: '部门与角色', models: '模型与权限', instances: '实例管理', plugins: '插件管理', audit: '安全与审计' }

const esc = (s) => String(s)
  .replace(/&/g, '&amp;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;')
  .replace(/'/g, '&#39;')

function readJson(dataDir, file, fallback) {
  try {
    return JSON.parse(readFileSync(join(dataDir, file), 'utf8'))
  } catch {
    return fallback
  }
}

/* ── 设计系统 ────────────────────────────────────────────────────────────── */

const CSS = `:root{--bg:#f6f7f9;--panel:#ffffff;--line:#e5e7eb;--line2:#d1d5db;
--text:#1f2937;--muted:#6b7280;--faint:#9ca3af;--accent:#2563eb;--blue:#2563eb;
--green:#059669;--red:#dc2626;--yellow:#d97706}
*{box-sizing:border-box}
body{margin:0;display:flex;font-family:system-ui,-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
color:var(--text);background:var(--bg)}
nav{width:216px;min-height:100vh;background:#ffffff;border-right:1px solid var(--line);padding:1.1rem .75rem;display:flex;flex-direction:column}
.brand{display:flex;align-items:center;gap:.55rem;padding:.2rem .5rem 1rem}
.brand .mark{width:30px;height:30px;border-radius:8px;background:var(--accent);display:grid;place-items:center;font-weight:700;color:#fff}
.brand .name{font-weight:600;letter-spacing:.08em;color:#111827}
.brand .sub{font-size:.68rem;color:var(--faint);letter-spacing:.14em}
.navgroup{font-size:.68rem;letter-spacing:.16em;color:var(--faint);margin:1rem .6rem .3rem;
display:flex;align-items:center;gap:.4rem}
.navgroup svg{width:12px;height:12px;stroke:var(--faint)}
nav a.item{display:flex;align-items:center;gap:.5rem;color:#374151;text-decoration:none;
padding:.48rem .7rem;border-radius:7px;margin:.12rem 0;font-size:.92rem}
nav a.item:hover{background:#f3f4f6}
nav a.item.on{background:#eff6ff;color:var(--accent);box-shadow:inset 2px 0 0 var(--accent)}
nav .spacer{flex:1}
.me{display:flex;align-items:center;gap:.55rem;padding:.6rem .5rem;border-top:1px solid var(--line);margin-top:.8rem}
main{flex:1;padding:1.5rem 2.2rem 2.5rem;min-width:0}
.pagehead{display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line);padding-bottom:.9rem;margin-bottom:1.3rem}
.backbtn{width:32px;height:32px;border-radius:50%;border:1px solid var(--line2);background:#fff;color:#374151;display:grid;place-items:center;text-decoration:none;font-size:1rem;flex-shrink:0}
.backbtn:hover{border-color:var(--accent);color:var(--accent)}
.pagehead h1{margin:0;font-size:1.4rem;color:#111827}
.pagehead .sub{color:var(--muted);font-size:.9rem;margin-top:.3rem}
.statusbadge{display:flex;align-items:center;gap:.45rem;font-size:.85rem;color:var(--muted);
border:1px solid var(--line);border-radius:999px;padding:.35rem .8rem;background:#fff}
.dot{width:8px;height:8px;border-radius:50%;background:var(--green)}
.dot.warn{background:var(--yellow)}
.dot.bad{background:var(--red)}
.statgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:.9rem;margin:.2rem 0 1.4rem}
.stat{background:#fff;border:1px solid var(--line);border-radius:10px;padding:.85rem 1rem}
.stat .k{font-size:.78rem;color:var(--muted)}
.stat .v{font-size:1.55rem;font-weight:600;margin-top:.25rem;color:#111827}
.stat .n{font-size:.75rem;color:var(--faint);margin-top:.2rem}
h2.sect{font-size:1.02rem;color:#111827;margin:1.6rem 0 .4rem}
table{border-collapse:collapse;margin:.5rem 0 1.3rem;width:100%;background:#fff}
td,th{border:1px solid var(--line);padding:.5rem .75rem;font-size:.88rem;text-align:left;vertical-align:top}
th{color:var(--muted);font-weight:500;font-size:.78rem;letter-spacing:.05em;background:#f9fafb}
.chip{display:inline-block;padding:.14rem .55rem;border-radius:999px;font-size:.76rem;line-height:1.3}
.chip.green{background:#ecfdf5;color:#059669;border:1px solid #a7f3d0}
.chip.blue{background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe}
.chip.red{background:#fef2f2;color:#dc2626;border:1px solid #fecaca}
.chip.yellow{background:#fffbeb;color:#b45309;border:1px solid #fde68a}
.chip.gray{background:#f9fafb;color:var(--muted);border:1px solid var(--line)}
.chip.teal{background:#f0fdfa;color:#0d9488;border:1px solid #99f6e4}
.chip.purple{background:#f5f3ff;color:#7c3aed;border:1px solid #ddd6fe}
.bar{width:130px;height:6px;border-radius:3px;background:#e5e7eb;overflow:hidden;vertical-align:middle;display:inline-block}
.bar i{display:block;height:100%;border-radius:3px}
.avatar{width:30px;height:30px;border-radius:50%;display:inline-grid;place-items:center;
font-size:.8rem;font-weight:600;color:#fff;vertical-align:middle;margin-right:.5rem}
.btn{padding:.3rem .65rem;border-radius:6px;border:1px solid var(--line2);background:#fff;
color:#374151;cursor:pointer;font-size:.82rem;margin:.12rem .18rem .12rem 0;text-decoration:none;display:inline-block}
.btn:hover{border-color:var(--accent);color:var(--accent)}
.btn.warn{border-color:#fecaca;color:#dc2626}
.btn.primary{background:var(--accent);border-color:var(--accent);color:#fff;font-weight:600}
.btn:disabled{opacity:.45;cursor:not-allowed}
.tabs{display:flex;gap:.4rem;margin:.3rem 0 .8rem}
.tabs a{padding:.28rem .85rem;border-radius:999px;border:1px solid var(--line2);color:var(--muted);
text-decoration:none;font-size:.84rem;background:#fff}
.tabs a.on{background:#eff6ff;border-color:var(--accent);color:var(--accent)}
input,select,button{font-family:inherit}
input,select{padding:.35rem .55rem;border-radius:6px;border:1px solid var(--line2);background:#fff;color:var(--text)}
button{padding:.35rem .7rem;border-radius:6px;border:1px solid var(--line2);background:#fff;color:#374151;cursor:pointer}
button.primary{background:var(--accent);border-color:var(--accent);color:#fff;font-weight:600}
form.panel{background:#fff;border:1px solid var(--line);border-radius:10px}
pre.log{background:#fff;border:1px solid var(--line);border-radius:8px;padding:.9rem;overflow:auto;
font-size:.78rem;line-height:1.5;max-height:60vh;color:#374151}
footer{margin-top:3rem;text-align:center;color:var(--faint);font-size:.8rem;letter-spacing:.1em}
a{color:var(--accent)}
.searchbox{display:flex;gap:.4rem;align-items:center;margin-bottom:.6rem}
.searchbox input{width:220px}
.flabel{font-size:.85rem;color:var(--muted);margin:.3rem 0 .25rem}
.hinttext{font-size:.78rem;color:var(--faint);margin:.15rem 0 .5rem}
select{min-width:220px}
.chip.purple{background:#f5f3ff;color:#7c3aed;border:1px solid #ddd6fe}
.mmtable input[type=text],.mmtable input:not([type]){width:100%}
.adv{margin-top:1rem}
.adv summary{cursor:pointer;color:#374151;font-size:.92rem;list-style:none}
.adv summary::before{content:'▸ '}.adv[open] summary::before{content:'▾ '}
.advbody{border:1px solid var(--line);border-radius:10px;padding:1rem 1.2rem;margin-top:.5rem;background:#fff}
.cfgrow{display:flex;justify-content:space-between;align-items:center;border:1px solid var(--line);border-radius:8px;padding:.6rem .9rem;margin:.5rem 0;font-size:.9rem;background:#fff}
.editorwrap{display:flex;background:#fff;border:1px solid var(--line2);border-radius:6px;overflow:hidden}
.gutter{padding:.7rem .5rem;color:#9ca3af;font-family:Consolas,monospace;font-size:.85rem;text-align:right;user-select:none;min-width:2rem;white-space:pre;background:#f9fafb}
.editorwrap textarea{flex:1;border:none;resize:vertical;font-family:Consolas,monospace;font-size:.85rem;line-height:1.5;color:#1f2937}
.hint{background:#fffbeb;border:1px solid #fde68a;color:#92400e;border-radius:6px;padding:.5rem .8rem;font-size:.85rem}
.switch{display:inline-flex;align-items:center;gap:.35rem;cursor:pointer}
.switch input{display:none}
.switch .slider{width:30px;height:16px;border-radius:999px;background:#d1d5db;position:relative;transition:background .15s}
.switch .slider::after{content:'';position:absolute;left:2px;top:2px;width:12px;height:12px;border-radius:50%;background:#fff;transition:left .15s}
.switch input:checked+.slider{background:var(--accent)}
.switch input:checked+.slider::after{left:16px}
.presetbox{background:#fff;border:1px solid var(--line);border-radius:10px;padding:1rem 1.1rem;margin-bottom:1rem}
.preset{border:1px solid var(--line2);background:#fff;color:#374151}
.preset.on{background:#eff6ff;border-color:var(--accent);color:var(--accent)}`

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

const AVATAR_COLORS = ['#43d6c5', '#6f9bff', '#b45309', '#ff9d9d', '#b388ff', '#7ef0c0']
const avatar = (name) => {
  const ch = [...String(name || '?')][0]
  const sum = [...String(name || '')].reduce((a, c) => a + c.codePointAt(0), 0)
  return `<span class="avatar" style="background:${AVATAR_COLORS[sum % AVATAR_COLORS.length]}">${esc(ch)}</span>`
}

const roleChip = (role) => {
  const map = { admin: ['管理员', 'red'], auditor: ['审计员', 'yellow'], employee: ['成员', 'blue'] }
  const [label, cls] = map[role] ?? [role, 'gray']
  return `<span class="chip ${cls}">${esc(label)}</span>`
}

const auditResultChip = (result) => {
  const map = { ok: ['成功', 'green'], deny: ['拒绝', 'yellow'], fail: ['失败', 'red'] }
  const [label, cls] = map[result] ?? [result ?? '—', 'gray']
  return `<span class="chip ${cls}">${esc(label)}</span>`
}

/** 审计 detail 的表格摘要：JSON 序列化并截断，只含标量元数据。 */
const detailSummary = (detail) => {
  if (detail === null || detail === undefined) return '—'
  const text = JSON.stringify(detail)
  return text.length > 160 ? `${text.slice(0, 157)}…` : text
}

/** 用量进度条（点数 / 旧制 tokens 共用渲染）；quota 非有限数 = 不限。 */
const usageCell = (used, quota) => {
  if (!Number.isFinite(quota)) return `${fmtPoints(used)} <span class="chip gray">不限</span>`
  const pct = Math.min(100, Math.round((used / Math.max(1, quota)) * 100))
  const color = pct >= 100 ? 'var(--red)' : pct >= 70 ? 'var(--yellow)' : 'var(--green)'
  const mark = pct >= 100 ? ' 🔴' : ''
  return `<span class="bar"><i style="width:${pct}%;background:${color}"></i></span> <span style="font-size:.82rem">${fmtPoints(used)}/${fmtPoints(quota)}${mark}</span>`
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
  安全与审计: '审计日志查询导出与登录安全设置',
  部门与角色: '部门分组倍率与角色权限矩阵',
  实例日志: '实例运行日志（最近 80 行）',
}

function SHELL(title, active, manifest, getState, dataDir, body, back) {
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
${item('个人中心', '/me', ICONS.user, false)}
<div class="me">${avatar(admin?.displayName ?? '管')}<div><div style="font-size:.86rem">${esc(admin?.displayName ?? '管理员')}</div><div style="font-size:.72rem;color:var(--faint)">${esc(admin?.role === 'admin' ? '管理员 · 平台' : '')}</div></div></div>`
  return `<!doctype html><html lang="zh"><head><meta charset="utf-8"><title>卡巴格 · ${title}</title><style>${CSS}</style></head>
<body>
<nav><div class="brand"><span class="mark">卡</span><div><div class="name">卡巴格</div><div class="sub">DASHBOARD CONSOLE</div></div></div>${nav}</nav>
<main>
<div class="pagehead"><div style="display:flex;align-items:center;gap:.7rem">${back ? `<a class="backbtn" href="${back}" title="返回">←</a>` : ''}<div><h1>${title}</h1><div class="sub">${esc(SUBTITLES[title] ?? '')}</div></div></div><div class="statusbadge">${badge}<span>${nowStamp()}</span></div></div>
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
  // 告警卡（栏目 v2 一期）：额度将尽成员（点数口径，旧制 tokens 账号按旧口径并入）
  // + 24h 失败登录计数 + 最近 5 条审计事件摘要。
  const exhausted = accounts.filter((a) => {
    const e = usageMonth[a.account]
    if (Number.isFinite(a.monthlyPoints)) return (e?.points ?? 0) >= a.monthlyPoints
    if (Number.isFinite(a.monthlyTokens)) return (e ? e.tokensIn + e.tokensOut : 0) >= a.monthlyTokens
    return false
  })
  const dayAgoMs = Date.now() - 24 * 3_600_000
  const recentFails = auditQuery({ actionPrefix: 'auth.login_fail', limit: 2000 })
  const fail24h = recentFails.filter((e) => Date.parse(e.ts ?? '') >= dayAgoMs).length
  const recentEvents = auditQuery({ limit: 5 })
  const alertStats = `<div class="statgrid">
<div class="stat"><div class="k">额度将尽成员</div><div class="v">${exhausted.length}</div><div class="n">本月用量已达月度额度（点数 · 旧制 tokens 并入）</div></div>
<div class="stat"><div class="k">24 小时失败登录</div><div class="v">${fail24h}</div><div class="n">auth.login_fail 审计事件</div></div>
</div>
<h2 class="sect">最近审计事件</h2><table><tr><th>时间</th><th>账号</th><th>动作</th><th>对象</th><th>结果</th></tr>${recentEvents.map((e) => `<tr><td>${esc(String(e.ts ?? '').replace('T', ' ').slice(0, 19))}</td><td>${esc(e.actor?.account ?? '—')}</td><td><span class="chip gray">${esc(e.action ?? '—')}</span></td><td>${esc(e.target ?? '—')}</td><td>${auditResultChip(e.result)}</td></tr>`).join('') || '<tr><td colspan="5">暂无审计事件</td></tr>'}</table>`
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
${alertStats}
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
  const twofaKey = deriveKey(getOrCreateSecret(dataDir))
  const departments = [...new Set(all.map((a) => a.department ?? '未分配'))]
  const accounts = all.filter((a) => {
    if (q !== '' && !a.account.toLowerCase().includes(q) && !String(a.displayName ?? '').toLowerCase().includes(q)) return false
    if (depFilter !== '' && (a.department ?? '未分配') !== depFilter) return false
    return true
  })
  const rows = accounts.map((a) => {
    const e = usage[a.account] ?? { tokensIn: 0, tokensOut: 0, requests: 0, points: 0 }
    const usedPoints = e.points ?? 0
    const usedTokens = e.tokensIn + e.tokensOut
    // 额度列点数口径（蓝图六）；monthlyPoints 未定义而存在旧 monthlyTokens 的
    // 账号按旧 tokens 判据展示并标注「旧制」。
    const quotaCellHtml = Number.isFinite(a.monthlyPoints)
      ? usageCell(usedPoints, a.monthlyPoints)
      : Number.isFinite(a.monthlyTokens)
        ? `${usageCell(usedTokens, a.monthlyTokens)} <span class="chip yellow" title="未设点数额度，按旧制 monthlyTokens 判定">旧制 tokens</span>`
        : `${usageCell(usedPoints, Number.NaN)} <span class="chip gray">点数</span>`
    const vk = activeVkeyFor(dataDir, a.account)
    const chips = vk === undefined ? '<span class="chip gray">无钥匙</span>' : vk.models === '*'
      ? '<span class="chip teal">全部模型</span>'
      : vk.models.slice(0, 3).map((m) => `<span class="chip teal">${esc(m)}</span>`).join('') + (vk.models.length > 3 ? `<span class="chip gray">+${vk.models.length - 3}</span>` : '')
    const roleOptions = ['admin', 'auditor', 'employee'].map((r) => {
      const [label] = { admin: ['管理员'], auditor: ['审计员'], employee: ['成员'] }[r]
      return `<option value="${r}" ${a.role === r ? 'selected' : ''}>${label}</option>`
    }).join('')
    return `<tr><td>${avatar(a.displayName)}${esc(a.displayName)}</td><td>${esc(a.account)}</td>
<td>${esc(a.department ?? '未分配')}</td><td>${roleChip(a.role)}</td><td>${esc(a.instanceId)}</td>
<td>${chips}</td><td>${a.disabled ? '<span class="chip red">已禁用</span>' : '<span class="chip green">正常</span>'}</td>
<td>${quotaCellHtml}</td><td>${e.requests}</td>
<td>
<form class="inline" onsubmit="api(event,'/console/api/member/update',this)"><input type="hidden" name="account" value="${esc(a.account)}"><input name="department" size="6" value="${esc(a.department ?? '未分配')}" title="部门"><button>改部门</button></form>
<form class="inline" onsubmit="api(event,'/console/api/member/update',this)"><input type="hidden" name="account" value="${esc(a.account)}"><select name="role">${roleOptions}</select><button>改角色</button></form>
<form class="inline" onsubmit="api(event,'/console/api/member/quota',this)"><input type="hidden" name="account" value="${esc(a.account)}"><input name="points" size="8" placeholder="点数额度/空=不限"><button>改额度</button></form>
<form class="inline" onsubmit="api(event,'/console/api/member/reset-password',this)"><input type="hidden" name="account" value="${esc(a.account)}"><button>重置密码</button></form>
${a.disabled
    ? `<form class="inline" onsubmit="api(event,'/console/api/member/enable',this)"><input type="hidden" name="account" value="${esc(a.account)}"><button>启用</button></form>`
    : `<form class="inline" onsubmit="api(event,'/console/api/member/disable',this)"><input type="hidden" name="account" value="${esc(a.account)}"><button class="warn">禁用</button></form>`}
${isTwofaEnabled(dataDir, twofaKey, a.account)
    ? `<form class="inline" onsubmit="resetTwofa(event,'${esc(a.account)}')"><button class="warn" title="账号丢失认证器时由管理员解除绑定">重置2FA</button></form>`
    : ''}</td></tr>`
  }).join('')
  const instanceOptions = manifest.instances.map((s) => `<option value="${s.id}">${s.id}（${state.instances[s.id]?.state ?? '—'}）</option>`).join('')
  const depOptions = departments.map((dep) => `<option value="${esc(dep)}">${esc(dep)}</option>`).join('')
  // 待用邀请（未撤销/未用/未过期），过期时间升序（阶段 10）。
  const inviteRows = listOpenInvites(dataDir).map((i) => `<tr><td><code>${esc(i.id)}</code></td><td>${esc(i.department)}</td><td>${roleChip(i.role)}</td><td>${esc(i.instanceId)}</td><td>${esc(String(i.expiresAt).replace('T', ' ').slice(0, 16))}</td><td><form class="inline" onsubmit="revokeInvite(event,'${esc(i.id)}')"><button class="warn">撤销</button></form></td></tr>`).join('')
  return `
<form class="searchbox" method="get" style="margin:0 0 .6rem"><input name="q" value="${esc(q)}" placeholder="搜索姓名 / 账号"><button class="primary">搜索</button><select name="dep" onchange="this.form.submit()"><option value="">全部部门</option>${depOptions}</select>${q !== '' || depFilter !== '' ? '<a class="btn" href="/console/members">清除</a>' : ''}</form>
<table><tr><th>成员</th><th>账号</th><th>部门</th><th>角色</th><th>实例</th><th>可见模型</th><th>状态</th><th>本月点数 已用/额度</th><th>请求</th><th>操作</th></tr>${rows || '<tr><td colspan="10">无匹配成员</td></tr>'}</table>
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
<h2 class="sect">邀请注册（阶段 10）</h2>
<form class="panel" onsubmit="createInvite(event)">
<div style="margin-bottom:.5rem">部门 <input name="department" placeholder="如 设计部（留空=未分配）"> 角色 <select name="role"><option value="employee">成员</option><option value="auditor">审计员</option></select> 实例 <select name="instanceId">${instanceOptions}</select> 有效期 <input name="expiresInHours" size="4" value="72" title="小时"> 小时 <button class="primary">生成邀请链接</button></div>
</form>
<table><tr><th>邀请 ID</th><th>部门</th><th>角色</th><th>实例</th><th>过期时间</th><th>操作</th></tr>${inviteRows || '<tr><td colspan="6">暂无待用邀请</td></tr>'}</table>
<p class="mut" style="font-size:.82rem">链接一次性（注册即作废）、含预设部门/角色/实例；明文链接只在生成响应里显示一次，平台只存哈希。撤销后链接立即失效。</p>
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
async function createInvite(ev){ev.preventDefault();
 const f=new FormData(ev.target);const payload={};f.forEach((v,k)=>payload[k]=v);
 const r=await fetch('/console/api/invite/create',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(payload)});
 const j=await r.json().catch(()=>({}));
 if(r.ok){document.getElementById('out').textContent='邀请已创建（注册链接只显示一次，请立即复制转交）：\\n'+location.origin+j.registerUrl+'\\n过期时间：'+j.expiresAt}
 else document.getElementById('out').textContent='HTTP '+r.status+' '+(j.error||'')}
async function revokeInvite(ev,id){ev.preventDefault();
 if(!confirm('撤销邀请 '+id+'？链接将立即失效'))return;
 const r=await fetch('/console/api/invite/revoke',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({id})});
 if(r.ok)setTimeout(()=>location.reload(),600);else alert('撤销失败: '+await r.text())}
async function resetTwofa(ev,account){ev.preventDefault();
 if(!confirm('重置 '+account+' 的两步验证绑定？其下次登录将只需密码（丢失认证器的救援操作）'))return;
 const r=await fetch('/console/api/member/2fa/reset',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({account})});
 if(r.ok)setTimeout(()=>location.reload(),600);else alert('重置失败: '+await r.text())}
</script>`
}

/* ── 页面：部门与角色 ────────────────────────────────────────────────────── */

function rolesPage({ dataDir }) {
  initQuotas(dataDir)
  const accounts = listAccounts(dataDir)
  const departments = [...new Set(accounts.map((a) => a.department ?? '未分配'))].sort()
  const ratios = loadRatios()
  const rows = departments.map((dep) => {
    const count = accounts.filter((a) => (a.department ?? '未分配') === dep).length
    const configured = ratios.groups[dep] !== undefined
    return `<tr><td>${esc(dep)}</td><td>${count}</td>
<td>${configured ? '<span class="chip blue">自定义</span>' : '<span class="chip gray">缺省 1</span>'}</td>
<td><form class="inline" onsubmit="setGroupRatio(event,'${esc(dep)}')"><input name="ratio" size="6" value="${ratios.groups[dep] ?? 1}" title="分组倍率"><button class="${configured ? 'btn' : 'primary'}">保存倍率</button></form></td></tr>`
  }).join('')
  // 角色权限点矩阵（蓝图第三节，本期只读展示）；实例内工具组已可编辑（阶段 9）。
  const MATRIX = [
    ['管理台登录', ['✅', '✅（本期落地）', '❌（仅实例子域）']],
    ['总览 / 实例 / 模型 / 插件页', ['读写', '只读', '—']],
    ['成员列表查看', ['读写', '只读', '—']],
    ['成员变更操作', ['✅', '❌', '—']],
    ['审计日志查看 / 导出', ['✅', '✅（核心职责）', '—']],
    ['安全设置修改', ['✅', '❌（只读展示）', '—']],
  ]
  const matrixRows = MATRIX.map(([point, cells]) =>
    `<tr><td>${esc(point)}</td>${cells.map((c) => `<td>${esc(c)}</td>`).join('')}</tr>`).join('')
  // 实例内工具 RBAC（阶段 9）：勾选 = 允许该工具组；保存即写 data/toolpolicy.json
  // 并全量下发实例 home 的 tool-policy.json（实例侧 guard 插件 mtime 热生效）。
  const GROUP_LABELS = { command: '命令行', fs: '文件', network: '联网' }
  const policy = loadToolPolicy(dataDir)
  const roleSwitchRow = (role, label, editable) => {
    const deny = denyForRole(policy, role)
    const cells = TOOL_GROUPS.map((group) => editable
      ? `<label style="margin-right:.9rem;white-space:nowrap"><input type="checkbox" name="${role}-${group}" ${deny.includes(group) ? '' : 'checked'}> ${GROUP_LABELS[group]}</label>`
      : `<span class="chip gray">${GROUP_LABELS[group]}${deny.includes(group) ? ' 禁' : ' 允'}</span>`)
    return `<tr><td>${roleChip(role)} ${esc(label)}</td>${cells.map((c) => `<td>${c}</td>`).join('')}</tr>`
  }
  const toolPolicySection = `
<h2 class="sect">实例内工具组策略（保存即下发，热生效）</h2>
<form class="panel" onsubmit="saveToolPolicy(event)" style="padding:1rem">
<table style="margin:.4rem 0 .8rem"><tr><th>角色</th><th>命令行（bash/pwsh/terminal_*）</th><th>文件（read/write/edit/glob/grep 等）</th><th>联网（web_search/web_fetch）</th></tr>
${roleSwitchRow('admin', '管理员', false)}
${roleSwitchRow('auditor', '审计员', true)}
${roleSwitchRow('employee', '成员', true)}
</table>
<button class="primary">保存工具策略并下发</button>
<span class="mut" style="font-size:.82rem;margin-left:.8rem">勾选 = 允许；admin 固定全开。策略按实例归属账号的角色写到实例 home 的 tool-policy.json，实例内 guard 插件拒绝越权调用并回流审计（guard.deny）。</span>
</form>`
  return `
<h2 class="sect">部门与分组倍率</h2>
<table><tr><th>部门</th><th>成员数</th><th>倍率来源</th><th>分组倍率（消耗点 × 分组倍率）</th></tr>${rows || '<tr><td colspan="4">暂无部门</td></tr>'}</table>
<p class="mut" style="font-size:.82rem">分组倍率存于 data/ratios.json（groups），保存后 Relay 下一请求即按新倍率计点；成员所属部门在成员页维护。中小企业平铺部门，不做部门树。</p>
<h2 class="sect">角色权限点矩阵（只读展示）</h2>
<table><tr><th>权限点</th><th>admin 管理员</th><th>auditor 审计员</th><th>employee 成员</th></tr>${matrixRows}</table>
<p class="mut" style="font-size:.82rem">本期固定三角色（admin/auditor/employee），矩阵只读展示；实例内工具组策略见下方可编辑面板（阶段 9 已落地）。</p>
${toolPolicySection}
<pre id="out" class="log" style="max-height:none"></pre>
<script>
async function setGroupRatio(ev, dep){ev.preventDefault();
 const f=new FormData(ev.target);
 const r=await fetch('/console/api/department/group-ratio',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({department:dep,ratio:Number(f.get('ratio'))})});
 const t=await r.text();document.getElementById('out').textContent='HTTP '+r.status+' '+t;
 if(r.ok)setTimeout(()=>location.reload(),800)}
async function saveToolPolicy(ev){ev.preventDefault();
 const GROUPS=['command','fs','network'];const ROLES=['auditor','employee'];const payload={roles:{}};
 for(const role of ROLES){payload.roles[role]={deny:GROUPS.filter(function(g){return !document.querySelector('input[name="'+role+'-'+g+'"]').checked})}}
 const r=await fetch('/console/api/toolpolicy',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(payload)});
 const t=await r.text();document.getElementById('out').textContent='HTTP '+r.status+' '+t;
 if(r.ok)setTimeout(()=>location.reload(),800)}
</script>`
}

function newProviderPage() {
  const PRESETS = [
    { name: 'Claude Official', baseURL: 'https://api.anthropic.com', website: 'https://www.anthropic.com', note: 'Anthropic 官方', models: '' },
    { name: '胜算云', baseURL: '', website: '', note: '中转站，请填写请求地址', models: '' },
    { name: 'PatewayAI', baseURL: '', website: '', note: '中转站，请填写请求地址', models: '' },
    { name: '火山Agentplan', baseURL: 'https://ark.cn-beijing.volces.com/api/v3', website: 'https://www.volcengine.com', note: '火山方舟', models: '' },
    { name: 'BytePlus', baseURL: 'https://ark.ap-southeast.bytepluses.com/api/v3', website: 'https://www.byteplus.com', note: '字节国际', models: '' },
    { name: 'DouBaoSeed', baseURL: 'https://ark.cn-beijing.volces.com/api/v3', website: 'https://www.volcengine.com', note: '豆包 Seed', models: '' },
    { name: 'CCSub', baseURL: '', website: '', note: '中转站，请填写请求地址', models: '' },
    { name: 'Gemini Native', baseURL: 'https://generativelanguage.googleapis.com/v1beta/openai', website: 'https://ai.google.dev', note: 'Google Gemini', models: '' },
    { name: 'DeepSeek', baseURL: 'https://api.deepseek.com', website: 'https://platform.deepseek.com', note: 'DeepSeek 官方', models: 'deepseek-chat,deepseek-reasoner' },
    { name: 'OpenCode Go', baseURL: '', website: '', note: '中转站，请填写请求地址', models: '' },
    { name: 'Zhipu GLM', baseURL: 'https://open.bigmodel.cn/api/paas/v4', website: 'https://open.bigmodel.cn', note: '智谱 GLM 官方', models: 'glm-4.7,glm-5.2,glm-5.3,glm-5.3-flash' },
    { name: 'Zhipu GLM en', baseURL: 'https://api.z.ai/api/paas/v4', website: 'https://z.ai', note: '智谱国际', models: 'glm-4.7,glm-5.2,glm-5.3,glm-5.3-flash' },
    { name: 'Baidu Qianfan Coding Plan', baseURL: 'https://qianfan.baidubce.com/v2', website: 'https://cloud.baidu.com', note: '百度千帆', models: '' },
    { name: 'Bailian', baseURL: 'https://dashscope.aliyuncs.com/compatible-mode/v1', website: 'https://www.aliyun.com/product/bailian', note: '阿里云百炼', models: '' },
    { name: 'Bailian For Coding', baseURL: 'https://dashscope.aliyuncs.com/compatible-mode/v1', website: 'https://www.aliyun.com/product/bailian', note: '阿里云百炼 Coding', models: '' },
    { name: 'Kimi', baseURL: 'https://api.moonshot.cn/v1', website: 'https://platform.moonshot.cn', note: '月之暗面', models: 'kimi-k2-0905-preview' },
    { name: 'Kimi For Coding', baseURL: 'https://api.kimi.com/coding/v1', website: 'https://www.kimi.com', note: 'Kimi For Coding', models: '' },
    { name: 'StepFun', baseURL: 'https://api.stepfun.com/v1', website: 'https://platform.stepfun.com', note: '阶跃星辰', models: '' },
    { name: 'StepFun en', baseURL: 'https://api.stepfun.com/v1', website: 'https://platform.stepfun.com', note: '阶跃星辰国际', models: '' },
    { name: 'ModelScope', baseURL: 'https://api-inference.modelscope.cn/v1', website: 'https://modelscope.cn', note: '魔搭社区', models: '' },
    { name: 'KAT-Coder', baseURL: '', website: '', note: '请填写请求地址', models: '' },
    { name: 'Longcat', baseURL: 'https://api.longcat.chat/openai/v1', website: 'https://longcat.chat', note: '美团 Longcat', models: '' },
    { name: 'MiniMax', baseURL: 'https://api.minimaxi.com/v1', website: 'https://platform.minimaxi.com', note: 'MiniMax 官方', models: 'MiniMax-M2' },
    { name: 'MiniMax en', baseURL: 'https://api.minimax.io/v1', website: 'https://www.minimax.io', note: 'MiniMax 国际', models: 'MiniMax-M2' },
    { name: 'BaiLing', baseURL: '', website: '', note: '中转站，请填写请求地址', models: '' },
    { name: 'AiHubMix', baseURL: 'https://aihubmix.com/v1', website: 'https://aihubmix.com', note: '中转站', models: '' },
    { name: 'CherryIN', baseURL: '', website: '', note: '中转站，请填写请求地址', models: '' },
    { name: 'SiliconFlow', baseURL: 'https://api.siliconflow.cn/v1', website: 'https://siliconflow.cn', note: '硅基流动', models: '' },
    { name: 'SiliconFlow en', baseURL: 'https://api.siliconflow.com/v1', website: 'https://siliconflow.com', note: '硅基流动国际', models: '' },
    { name: 'DMXAPI', baseURL: 'https://www.dmxapi.cn/v1', website: 'https://www.dmxapi.cn', note: '中转站', models: '' },
    { name: 'PackyCode', baseURL: '', website: '', note: '中转站，请填写请求地址', models: '' },
    { name: 'APIKEY.FUN', baseURL: '', website: '', note: '中转站，请填写请求地址', models: '' },
    { name: 'APINebula', baseURL: '', website: '', note: '中转站，请填写请求地址', models: '' },
    { name: 'AtlasCloud', baseURL: '', website: '', note: '中转站，请填写请求地址', models: '' },
    { name: 'SudoCode', baseURL: '', website: '', note: '中转站，请填写请求地址', models: '' },
    { name: 'ClaudeAPI', baseURL: '', website: '', note: '中转站，请填写请求地址', models: '' },
    { name: 'ClaudeCN', baseURL: '', website: '', note: '中转站，请填写请求地址', models: '' },
    { name: 'RunAPI', baseURL: '', website: '', note: '中转站，请填写请求地址', models: '' },
    { name: 'RelaxyCode', baseURL: '', website: '', note: '中转站，请填写请求地址', models: '' },
    { name: 'Cubence', baseURL: '', website: '', note: '中转站，请填写请求地址', models: '' },
    { name: 'AIGoCode', baseURL: '', website: '', note: '中转站，请填写请求地址', models: '' },
    { name: 'RightCode', baseURL: '', website: '', note: '中转站，请填写请求地址', models: '' },
    { name: 'AICodeMirror', baseURL: '', website: '', note: '中转站，请填写请求地址', models: '' },
    { name: 'CrazyRouter', baseURL: '', website: '', note: '中转站，请填写请求地址', models: '' },
    { name: 'SSSAiCode', baseURL: '', website: '', note: '中转站，请填写请求地址', models: '' },
    { name: '优云智算', baseURL: '', website: '', note: '中转站，请填写请求地址', models: '' },
    { name: '优云智算Coding Plan', baseURL: '', website: '', note: '中转站，请填写请求地址', models: '' },
    { name: 'Micu', baseURL: '', website: '', note: '中转站，请填写请求地址', models: '' },
    { name: 'CTok.ai', baseURL: '', website: '', note: '中转站，请填写请求地址', models: '' },
    { name: 'E-FlowCode', baseURL: '', website: '', note: '中转站，请填写请求地址', models: '' },
    { name: 'OpenRouter', baseURL: 'https://openrouter.ai/api/v1', website: 'https://openrouter.ai', note: 'OpenRouter', models: '' },
    { name: 'TheRouter', baseURL: '', website: '', note: '中转站，请填写请求地址', models: '' },
    { name: 'Novita AI', baseURL: 'https://api.novita.ai/v3/openai', website: 'https://novita.ai', note: 'Novita AI', models: '' },
    { name: 'GitHub Copilot', baseURL: '', website: '', note: '需 Copilot 订阅鉴权，请填写请求地址', models: '' },
    { name: 'Codex', baseURL: '', website: '', note: '请填写请求地址', models: '' },
    { name: 'LemonData', baseURL: '', website: '', note: '中转站，请填写请求地址', models: '' },
    { name: 'Nvidia', baseURL: 'https://integrate.api.nvidia.com/v1', website: 'https://build.nvidia.com', note: 'NVIDIA NIM', models: '' },
    { name: 'PIPELLM', baseURL: '', website: '', note: '中转站，请填写请求地址', models: '' },
    { name: 'Xiaomi MiMo', baseURL: '', website: '', note: '小米 MiMo，请填写请求地址', models: '' },
    { name: 'Xiaomi MiMo Token Plan (China)', baseURL: '', website: '', note: '小米 MiMo，请填写请求地址', models: '' },
    { name: 'AWS Bedrock (AKSK)', baseURL: '', website: 'https://aws.amazon.com/bedrock', note: '需 AKSK 鉴权配置', models: '' },
    { name: 'AWS Bedrock (API Key)', baseURL: '', website: 'https://aws.amazon.com/bedrock', note: '需 API Key 鉴权配置', models: '' },
  ]
  const chips = `<button type="button" class="chip gray preset on" data-i="-1">自定义配置</button>` +
    PRESETS.map((p, i) => `<button type="button" class="chip gray preset" data-i="${i}">${esc(p.name)}</button>`).join('')
  const presetData = JSON.stringify(PRESETS)
  return `
<div class="presetbox">
<div class="k" style="font-size:.78rem;color:var(--muted);margin-bottom:.5rem">预设供应商 <span class="mut">（点选自动填充请求地址；自定义配置需手动填写所有必填字段）</span></div>
<div style="display:flex;flex-wrap:wrap;gap:.4rem">${chips}</div>
<p style="color:#b45309;font-size:.82rem;margin:.6rem 0 0">💡 自定义配置需手动填写所有必填字段</p>
</div>
<h2 class="sect">供应商信息</h2>
<form id="pform" class="panel" style="display:block;max-width:100%" onsubmit="addProvider(event)">
<div class="formrow2">
<div><div class="flabel">供应商名称</div><input name="name" style="width:100%" placeholder="例如：Claude 官方" required></div>
<div><div class="flabel">备注</div><input name="note" style="width:100%" placeholder="例如：公司专用账号"></div>
</div>
<div style="margin-top:.9rem"><div class="flabel">官网链接</div><input name="website" style="width:100%" placeholder="https://example.com（可选）"></div>
<div style="margin-top:.9rem"><div class="flabel">API Key</div><input name="apiKey" style="width:100%" placeholder="只需要填这里，下方配置会自动填充" required></div>
<div style="margin-top:.9rem;display:flex;align-items:center;justify-content:space-between">
<div style="display:flex;align-items:center;gap:.6rem"><span class="flabel" style="margin:0">请求地址</span>
<label class="switch" title="开启后直接填写完整端点 URL（含 /chat/completions）"><input type="checkbox" id="fullurl"><span class="slider"></span><span style="font-size:.8rem;color:var(--muted)">完整 URL</span></label></div>
<span class="mut" style="font-size:.85rem">⚙ 管理与测速</span>
</div>
<div><input name="baseURL" style="width:100%" placeholder="https://your-api-endpoint.com" id="baseurl-input"></div>
<div class="hint">💡 填写兼容 OpenAI Chat Completions 的服务端点地址，不要以斜杠结尾</div>
<div style="margin-top:.9rem"><div class="flabel">模型列表（逗号分隔）</div><input name="models" style="width:100%" placeholder="如 glm-4.7,glm-5.2（供成员矩阵授权）"></div>
<details class="adv"><summary>∨ 高级选项</summary>
<div class="advbody">
<p class="mut" style="font-size:.85rem;margin:.2rem 0 .6rem">包含 API 格式、认证字段、模型映射等配置。大多数场景下保持默认即可。</p>
<div class="flabel">API 格式</div>
<select name="apiFormat" id="apifmt" onchange="onApiFmt(this.value)">
<option value="anthropic" selected>Anthropic Messages（原生）</option>
<option value="openai">OpenAI Chat Completions（兼容）</option>
</select>
<p class="hinttext">选择供应商 API 的输入格式</p>
<div class="flabel">认证字段</div>
<select name="authEnv">
<option value="ANTHROPIC_AUTH_TOKEN">ANTHROPIC_AUTH_TOKEN（默认）</option>
<option value="ANTHROPIC_API_KEY">ANTHROPIC_API_KEY</option>
<option value="OPENAI_API_KEY">OPENAI_API_KEY</option>
</select>
<p class="hinttext">选择写入配置的认证环境变量名</p>
<div style="display:flex;align-items:center;justify-content:space-between;margin-top:.9rem">
<div class="flabel" style="margin:0">模型映射</div>
<div><button type="button" class="btn" onclick="mmQuick()">一键设置</button><button type="button" class="btn" onclick="alert('获取模型列表：需供应商支持 /models 接口，待接入')">获取模型列表</button></div>
</div>
<p class="mut" style="font-size:.82rem;margin:.2rem 0 .4rem">显示名称只影响 /model 菜单；1M 只是给 Claude Code 的上下文能力声明。</p>
<table class="mmtable"><tr><th>模型角色</th><th>显示名称</th><th>实际请求模型</th><th>声明支持 1M</th></tr>
<tr><td><span class="chip blue">Sonnet</span></td><td><input name="mm-display-sonnet" placeholder="MiniMax-M3"></td><td><input name="mm-actual-sonnet" placeholder="MiniMax-M3"></td><td><input type="checkbox" name="mm-1m-sonnet"></td></tr>
<tr><td><span class="chip purple">Opus</span></td><td><input name="mm-display-opus" placeholder="MiniMax-M2.7-highspeed"></td><td><input name="mm-actual-opus" placeholder="MiniMax-M2.7-highspeed"></td><td><input type="checkbox" name="mm-1m-opus"></td></tr>
<tr><td><span class="chip gray">Haiku</span></td><td><input name="mm-display-haiku" placeholder="MiniMax-M2.7"></td><td><input name="mm-actual-haiku" placeholder="MiniMax-M2.7"></td><td><input type="checkbox" name="mm-1m-haiku"></td></tr>
</table>
<div class="flabel" style="margin-top:.9rem">默认兜底模型</div>
<input name="fallbackModel" style="width:100%" placeholder="MiniMax-M3">
<p class="hinttext">仅在请求没有明确落到 Sonnet、Opus 或 Haiku 角色时使用；通常可以留空。</p>
<div style="display:flex;align-items:center;justify-content:space-between;margin-top:1rem">
<div style="font-weight:600">配置 JSON</div>
<div style="display:flex;align-items:center;gap:.6rem"><label style="display:flex;align-items:center;gap:.3rem;font-size:.85rem"><input type="checkbox" checked> 写入通用配置</label><a href="#" onclick="return false" style="font-size:.85rem">编辑通用配置</a></div>
</div>
<div style="display:flex;flex-wrap:wrap;gap:.9rem;margin:.6rem 0">
<label style="display:flex;align-items:center;gap:.3rem;font-size:.85rem"><input type="checkbox" data-key="includeCoAuthoredBy" onchange="cfgKey(this)"> 隐藏 AI 署名</label>
<label style="display:flex;align-items:center;gap:.3rem;font-size:.85rem"><input type="checkbox" data-key="teammatesMode" onchange="cfgKey(this)"> Teammates 模式</label>
<label style="display:flex;align-items:center;gap:.3rem;font-size:.85rem"><input type="checkbox" data-key="enableToolSearch" onchange="cfgKey(this)"> 启用 Tool Search</label>
<label style="display:flex;align-items:center;gap:.3rem;font-size:.85rem"><input type="checkbox" data-key="maxThinking" onchange="cfgKey(this)"> 最大强度思考</label>
<label style="display:flex;align-items:center;gap:.3rem;font-size:.85rem"><input type="checkbox" data-key="disableAutoUpdate" onchange="cfgKey(this)"> 禁用自动升级</label>
</div>
<div class="editorwrap"><div class="gutter" id="gutter">1</div><textarea id="cfgjson" rows="8" spellcheck="false">{
  "env": {},
  "includeCoAuthoredBy": false
}</textarea></div>
<div style="margin:.4rem 0 1rem"><a href="#" onclick="fmtJson();return false" style="font-size:.85rem">⚡ 格式化</a></div>
<div class="cfgrow"><span>🧪 模型测试配置</span><span class="mut">使用单独配置（待接入）</span></div>
<div class="cfgrow"><span>💰 计费配置</span><span class="mut">使用单独配置（待接入）</span></div>
</div>
</details>
<div style="display:flex;justify-content:flex-end;gap:.6rem;margin-top:1.2rem">
<button type="button" class="btn" onclick="location.href='/console/models'">取消</button>
<button type="submit" class="btn primary">＋ 添加</button>
</div>
</form>
<p class="mut" style="font-size:.82rem">添加后该供应商立即进入 Relay 上游表；成员可在“模型与权限”矩阵中被授权其模型。真实 Key 仅存于服务端，页面只显示指纹。“模型测试/计费配置”为待接入项。</p>
<script>
var PRESETS = ${JSON.stringify(PRESETS)};
document.querySelectorAll('.preset').forEach(function(b){
 b.addEventListener('click',function(){
  document.querySelectorAll('.preset').forEach(function(x){x.classList.remove('on')});b.classList.add('on');
  var i=parseInt(b.dataset.i);var f=document.getElementById('pform');
  if(i<0){f.baseURL.value='';f.website.value='';f.note.value='';f.models.value='';return}
  var p=PRESETS[i];f.baseURL.value=p.baseURL;f.website.value=p.website;f.note.value=p.note||'';f.models.value=p.models||'';
  f.name.focus()})
})
function cfgKey(cb){try{var o=JSON.parse(document.getElementById('cfgjson').value||'{}');o[cb.dataset.key]=cb.checked;document.getElementById('cfgjson').value=JSON.stringify(o,null,2)}catch(e){cb.checked=!cb.checked;alert('JSON 格式错误，无法修改')}}
function fmtJson(){try{var o=JSON.parse(document.getElementById('cfgjson').value);document.getElementById('cfgjson').value=JSON.stringify(o,null,2);syncGutter()}catch(e){alert('JSON 格式错误')}}
function syncGutter(){var t=document.getElementById('cfgjson');var g=document.getElementById('gutter');if(!t||!g)return;
 var n=t.value.split('
').length;var s='';for(var i=1;i<=n;i++)s+=i+'
';g.textContent=s}
document.addEventListener('input',function(e){if(e.target&&e.target.id==='cfgjson')syncGutter()});
async function addProvider(ev){ev.preventDefault();
 var f=document.getElementById('pform');var fd=new FormData(f);var payload={};fd.forEach(function(v,k){payload[k]=v});
 payload.fullUrl=document.getElementById('fullurl').checked;
 payload.configJSON=document.getElementById('cfgjson').value;
 payload.modelMapping=['sonnet','opus','haiku'].map(function(role){
  return {role:role,display:f.elements['mm-display-'+role]?f.elements['mm-display-'+role].value:'',actual:f.elements['mm-actual-'+role]?f.elements['mm-actual-'+role].value:'',support1M:f.elements['mm-1m-'+role]?f.elements['mm-1m-'+role].checked:false}
 }).filter(function(m){return m.display||m.actual});
 var r=await fetch('/console/api/provider/add',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(payload)});
 if(r.ok){location.href='/console/models'}else{document.getElementById('out2').textContent='HTTP '+r.status+' '+await r.text()}}
</script>`
}

function modelsPage({ dataDir }) {
  initQuotas(dataDir)
  const upstreams = listUpstreams(dataDir).filter((x) => !x.revoked)
  const catalog = []
  for (const u of upstreams) for (const m of u.models) if (!catalog.includes(m)) catalog.push(m)
  const metaFor = (m) => {
    for (const u of upstreams) if (u.modelMeta?.[m]) return u.modelMeta[m]
    return null
  }
  const accounts = listAccounts(dataDir)
  const P_COLORS = ['#43d6c5', '#6f9bff', '#ffd166', '#ff9d9d', '#b388ff', '#7ef0c0', '#f5a623']
  const providerCards = upstreams.map((u) => {
    const sum = [...u.name].reduce((a, c) => a + c.codePointAt(0), 0)
    const color = P_COLORS[sum % P_COLORS.length]
    return `<div class="pcard">
      <span class="picon" style="background:${color}">${esc([...u.name][0].toUpperCase())}</span>
      <div class="pinfo"><div class="pname">${esc(u.name)}</div><a class="plink" href="${esc(u.website || u.baseURL)}" target="_blank" rel="noopener">${esc(u.baseURL)}</a></div>
      <div class="pmeta"><span class="chip gray">模型 ${u.models.length} 个</span> <span class="chip gray">${esc(u.keyFingerprint ?? '—')}</span></div>
      <div class="pacts">
        <form class="inline" onsubmit="addModelTo(event,'${esc(u.name)}')"><input name="model" size="12" placeholder="模型 ID"><button class="btn">＋ 添加模型</button></form>
        <form class="inline" onsubmit="delProvider(event,'${esc(u.name)}')"><button class="btn warn" title="删除供应商">🗑</button></form>
      </div>
    </div>`
  }).join('\n')
  const providerCardsBlock = `
  <div class="pcardlist">${providerCards || '<div class="pcard">暂无供应商</div>'}</div>
  <form class="panel" onsubmit="addProvider(event)" style="margin-top:.8rem">
  <div>供应商名称 <input name="name" size="28" placeholder="例如：Zhipu GLM" required> ｜ 请求地址 <input name="baseURL" size="40" placeholder="https://…" required> ｜ API Key <input name="apiKey" size="24" placeholder="sk-…" required> ｜ 模型 <input name="models" size="20" placeholder="逗号分隔"> <button class="primary">添加供应商</button></div>
  </form>
  <h2 class="sect">可用模型</h2>`
  const modelRows = catalog.map((m) => {
    const u = upstreams.find((x) => x.models.includes(m))
    const meta = metaFor(m)
    const ratio = resolveRatios(m, undefined)
    const usedBy = accounts.filter((a) => {
      const vk = activeVkeyFor(dataDir, a.account)
      return vk !== undefined && (vk.models === '*' || vk.models.includes(m))
    }).length
    const del = `<button class="warn" onclick="removeModel('${esc(u?.name ?? '')}','${esc(m)}',${usedBy})">删除</button>`
    const ratioForm = `<form class="inline" onsubmit="setRatio(event,'${esc(m)}')"><input name="ratio" size="3" value="${ratio.ratio}" title="模型倍率">/<input name="completionRatio" size="3" value="${ratio.completionRatio}" title="补全倍率"><button class="btn">存</button></form>`
    return `<tr><td>${esc(m)}</td><td>${esc(u?.name ?? '—')}</td><td>${meta ? esc(meta.context) : '—'} / ${meta ? esc(meta.maxOutput) : '—'}</td>
<td>${meta ? esc(meta.mIn) : '—'}</td><td>${meta ? esc(meta.mOut) : '—'}</td><td>${meta ? esc(meta.mCacheR) : '—'}</td><td>${meta ? esc(meta.mCacheW) : '—'}</td>
<td>${ratioForm}</td><td>${usedBy}</td><td><span class="chip green">已启用</span></td><td>${del}</td></tr>`
  }).join('')
  const matrix = modelsMatrix({ dataDir, accounts, catalog })
  return `
<div style="margin-bottom:.8rem;text-align:right"><a class="btn primary" href="/console/providers/new">＋ 新建模型供应商</a></div>
<h2 class="sect">模型供应商列表</h2>
<table><tr><th>提供方</th><th>端点（BaseURL）</th><th>上游 Key</th><th>模型数</th><th>状态</th></tr>${providerCardsBlock}</table>
<h2 class="sect">可用模型</h2>
<table><tr><th>模型</th><th>提供方</th><th>上下文 / 最大输出</th><th>输入倍率</th><th>输出倍率</th><th>缓存读</th><th>缓存写</th><th>计费倍率/补全（编辑）</th><th>成员可见</th><th>状态</th><th>操作</th></tr>${modelRows}</table>
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
async function addModelTo(ev, upstream) {ev.preventDefault();
 const f = new FormData(ev.target); const payload = { upstream, model: f.get('model') }
 if (!payload.model) { alert('请填写模型 ID'); return }
 const r = await fetch('/console/api/model/add', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload) })
 const t = await r.text(); alert((r.ok ? '已添加: ' : '失败: ') + t); if (r.ok) setTimeout(() => location.reload(), 600)}
async function delProvider(ev, name) {ev.preventDefault();
 if (!confirm('删除供应商 ' + name + '？其模型将一并移除')) return
 const r = await fetch('/console/api/provider/remove', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ name }) })
 if (r.ok) setTimeout(() => location.reload(), 600); else alert('删除失败: ' + await r.text())}
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
async function setRatio(ev,model){ev.preventDefault();
 const f=new FormData(ev.target);
 const r=await fetch('/console/api/model/ratio',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({model:model,ratio:Number(f.get('ratio')),completionRatio:Number(f.get('completionRatio'))})});
 const t=await r.text();alert((r.ok?'倍率已保存（下一请求生效）: ':'失败: ')+t);if(r.ok)setTimeout(()=>location.reload(),600)}
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

function instancesPage({ manifest, getState, dataDir, query }) {
  const state = getState()
  const drift = readJson(dataDir, 'drift.json', { checks: {} }).checks
  const filter = query.get('state') ?? 'all'
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

function instanceLogPage({ manifest, dataDir, query }) {
  const id = query.get('id') ?? ''
  if (!manifest.instances.some((s) => s.id === id)) return '<p class="bad">未知实例</p>'
  let content = '(无日志)'
  try {
    content = readFileSync(join(dataDir, 'logs', `${id}.log`), 'utf8').trim().split('\n').slice(-80).map(esc).join('\n')
  } catch { /* 尚无日志 */ }
  return `<p><a href="/console/instances">← 实例管理</a></p><pre class="log">${content}</pre>`
}

function pluginsPage({ dataDir, manifest, getState, runner }) {
  const desired = readJson(dataDir, 'plugins.json', { instances: {} })
  const catalog = pluginCatalog(dataDir)
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
      try { return JSON.parse(readFileSync(file, 'utf8')).dsh?.profile?.bundles ?? [] } catch { return [] }
    }
    return []
  })()
  const stats = `<div class="statgrid">
<div class="stat"><div class="k">已接入插件</div><div class="v">${names.size} 个</div><div class="n">第三方插件与平台共享一个进程树</div></div>
<div class="stat"><div class="k">待生效实例</div><div class="v">${staged}</div><div class="n">暂存后等待重启的改动</div></div>
<div class="stat"><div class="k">投放方式</div><div class="v" style="font-size:1rem">页面 / CLI</div><div class="n">真启动预检强制 · 装坏自动拦截</div></div>
<div class="stat"><div class="k">执行模型</div><div class="v" style="font-size:1rem">串行队列</div><div class="n">任务落盘，页面轮询取状态</div></div>
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
  const instanceChecks = manifest.instances.map((s) => `<label style="margin-right:.8rem"><input type="checkbox" name="id-${s.id}" checked> ${s.id}</label>`).join('')
  const instanceOptions = manifest.instances.map((s) => `<option value="${s.id}">${s.id}</option>`).join('')
  return `
${stats}
<h2 class="sect">投放插件（npm / Git / 本地路径）</h2>
<form class="panel" onsubmit="pushPlugin(event)">
<div style="margin-bottom:.5rem">插件 <input name="spec" size="44" placeholder="@weibaohui/dsh-file-share 或本地路径" required></div>
<div style="margin-bottom:.5rem">目标实例 ${instanceChecks} ｜ <label><input type="checkbox" name="skip-precheck"> 跳过预检（不推荐）</label></div>
<button class="primary">预检并暂存（异步执行）</button>
</form>
<form class="panel" onsubmit="removePlugin(event)">
卸载插件 <input name="spec" size="30" placeholder="插件名"> 实例 <select name="ids"><option value="all">全部</option>${instanceOptions}</select>
<button class="warn">卸载并重启</button>
</form>
<h2 class="sect">投放任务（每 4 秒自动刷新）</h2>
<table><tr><th>任务</th><th>类型</th><th>目标</th><th>状态</th><th>输出</th><th>更新时间</th></tr><tbody id="jobsbody"><tr><td colspan="6">加载中…</td></tr></tbody></table>
<h2 class="sect">平台默认插件集</h2>
<p class="mut" style="font-size:.85rem">每个实例 profile 在此集合之上叠加第三方插件。<span style="font-size:.85rem">${bundles || '—'}</span></p>
<h2 class="sect">插件 × 实例（期望态）</h2>
<table><tr><th>实例</th><th>实例状态</th><th>插件</th><th>版本 / 状态</th></tr>${rows}</table>
<p class="mut" style="font-size:.82rem">投放为异步任务（串行执行）：预检失败自动拦截、任何实例均不安装；暂存后在实例管理页重启生效；卸载自带重启。</p>
<pre id="out2" class="mut"></pre>
<script>
const STATE_CHIP={queued:['排队中','gray'],running:['执行中','yellow'],done:['完成','green'],failed:['失败','red']}
function escJs(s){return String(s??'').replace(/&/g,'&amp;').replace(/</g,'&lt;')}
function chipJs(s){const pair=STATE_CHIP[s]||[s,'gray'];return '<span class="chip '+pair[1]+'">'+pair[0]+'</span>'}
async function refreshJobs(){
 try{const r=await fetch('/console/api/plugin/jobs');if(!r.ok)return;
  const jobs=(await r.json()).jobs||[];const tb=document.getElementById('jobsbody');if(!tb)return;
  tb.innerHTML=jobs.length===0?'<tr><td colspan="6">暂无任务</td></tr>':jobs.map(function(j){
   const out=escJs((j.error?('[失败] '+j.error+'\\n'):'')+(j.output||'').slice(-280))
   return '<tr><td>'+escJs(j.id)+'</td><td>'+escJs(j.type)+'</td><td>'+escJs((j.spec||'')+(j.ids?' → '+j.ids:''))+'</td><td>'+chipJs(j.state)+'</td>'+
    '<td style="max-width:380px;white-space:pre-wrap;font-size:.74rem">'+out+'</td><td style="font-size:.74rem">'+escJs(j.updatedAt||'')+'</td></tr>'
  }).join('')
 }catch{}
}
async function postJob(payload){const r=await fetch('/console/api/plugin/job',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(payload)});
 const t=await r.text();document.getElementById('out2').textContent='HTTP '+r.status+' '+t;
 if(r.ok){refreshJobs();setInterval(refreshJobs,4000)}else{refreshJobs()}}
async function pushPlugin(ev){ev.preventDefault();const f=new FormData(ev.target);
 const ALL_IDS=${JSON.stringify(manifest.instances.map(function(x){return x.id}))};
 const ids=ALL_IDS.filter(function(id){return f.get('id-'+id)==='on'});
 if(ids.length===0){document.getElementById('out2').textContent='至少选择一个目标实例';return}
 await postJob({type:'push',spec:f.get('spec'),ids:ids,skipPrecheck:f.get('skip-precheck')==='on'})}
async function removePlugin(ev){ev.preventDefault();const f=new FormData(ev.target);
 await postJob({type:'remove',spec:f.get('spec'),ids:f.get('ids')})}
setInterval(refreshJobs,4000);refreshJobs()
</script>`
}

/* ── 审计埋点映射（蓝图第四节 action 命名）────────────────────────────────── */

/** 变更端点 → 审计 action。 */
const AUDIT_ACTION_BY_PATH = {
  '/console/api/member/create': 'member.create',
  '/console/api/member/update': 'member.update',
  '/console/api/member/quota': 'member.quota_change',
  '/console/api/member/reset-password': 'member.reset_password',
  '/console/api/member/disable': 'member.disable',
  '/console/api/member/enable': 'member.enable',
  '/console/api/idp/import': 'member.idp_import',
  '/console/api/provider/add': 'provider.add',
  '/console/api/provider/remove': 'provider.remove',
  '/console/api/model/add': 'model.add',
  '/console/api/model/remove': 'model.remove',
  '/console/api/model/ratio': 'model.ratio_change',
  '/console/api/department/group-ratio': 'quota.group_ratio_change',
  '/console/api/member/models': 'member.models_change',
  '/console/api/instance/start': 'instance.start',
  '/console/api/instance/stop': 'instance.stop',
  '/console/api/instance/restart': 'instance.restart',
  '/console/api/security/config': 'security.config_change',
  '/console/api/toolpolicy': 'toolpolicy.change',
  '/console/api/invite/create': 'invite.create',
  '/console/api/invite/revoke': 'invite.revoke',
  '/console/api/member/2fa/reset': 'security.2fa_reset',
  '/console/api/notify/config': 'security.notify_change',
}

/** 端点（+请求体）→ 审计 action：member/update 带角色时记 role_change，
 *  plugin/job 按任务类型细分；未知路径返回 null（不审计）。 */
function auditActionFor(path, body = {}) {
  if (path === '/console/api/plugin/job') {
    return ['push', 'remove', 'activate'].includes(body.type) ? `plugin.${body.type}` : 'plugin.job'
  }
  if (path === '/console/api/member/update' && body.role !== undefined) return 'member.role_change'
  return AUDIT_ACTION_BY_PATH[path] ?? null
}

/** 审计 target：供应商名 / 模型 id / 实例 id / 插件 spec / 部门名 / 成员账号。 */
function auditTargetFor(path, body = {}) {
  if (path === '/console/api/toolpolicy') return 'tool-policy'
  if (path.startsWith('/console/api/invite/')) return typeof body.id === 'string' && body.id !== '' ? body.id : null
  if (path.startsWith('/console/api/provider/')) return typeof body.name === 'string' ? body.name : null
  if (path === '/console/api/model/add' || path === '/console/api/model/remove' || path === '/console/api/model/ratio') return typeof body.model === 'string' ? body.model : null
  if (path === '/console/api/department/group-ratio') return typeof body.department === 'string' ? body.department : null
  if (path.startsWith('/console/api/instance/')) return typeof body.id === 'string' ? body.id : null
  if (path === '/console/api/plugin/job') return typeof body.spec === 'string' ? body.spec : null
  return typeof body.account === 'string' && body.account !== '' ? body.account : null
}

/** 审计页/审计 API 的查询串 → auditQuery 过滤参数。 */
const auditFiltersFromQuery = (query) => ({
  actionPrefix: query.get('action') ?? '',
  actor: query.get('actor') ?? '',
  result: query.get('result') ?? '',
})

// 账号/钥匙类变更（建号、额度、密码、禁启用、属性、IdP 同步）串行执行：
// 它们是 accounts.json/vkeys.json 的读改写热点，HTTP 并发下不做队列会丢更新。
// 导出供 sso 绑定等跨模块写入复用同一把锁（阶段 12 审查 P2-3）。
let accountQueue = Promise.resolve()
export const withAccountLock = (fn) => {
  const next = accountQueue.then(fn, fn)
  accountQueue = next.catch(() => {})
  return next
}

/* ── 页面：安全与审计 ────────────────────────────────────────────────────── */

function auditPage({ dataDir, query, role }) {
  const filters = auditFiltersFromQuery(query)
  const events = auditQuery({ ...filters, limit: 500 })
  const config = loadSecurityConfig(dataDir)
  const isAdmin = role === 'admin'
  const notifyConfig = loadNotifyConfig(dataDir)
  const actionOptions = [
    ['', '全部动作'], ['auth', 'auth · 登录'], ['member', 'member · 成员'], ['provider', 'provider · 供应商'],
    ['model', 'model · 模型'], ['instance', 'instance · 实例'], ['plugin', 'plugin · 插件'],
    ['quota', 'quota · 配额'], ['audit', 'audit · 审计'], ['security', 'security · 安全'],
    ['guard', 'guard · 工具拦截'], ['invite', 'invite · 邀请'],
  ].map(([value, label]) => `<option value="${value}" ${filters.actionPrefix === value ? 'selected' : ''}>${label}</option>`).join('')
  const resultOptions = [['ok', '成功'], ['deny', '拒绝'], ['fail', '失败']]
    .map(([value, label]) => `<option value="${value}" ${filters.result === value ? 'selected' : ''}>${label}</option>`).join('')
  const rows = events.map((e) => `<tr><td style="white-space:nowrap">${esc(String(e.ts ?? '').replace('T', ' ').slice(0, 19))}</td>
<td>${esc(e.actor?.account ?? '—')}</td><td>${esc(e.actor?.ip ?? '—')}</td>
<td><span class="chip gray">${esc(e.action ?? '—')}</span></td><td>${esc(e.target ?? '—')}</td>
<td>${auditResultChip(e.result)}</td>
<td style="max-width:340px;word-break:break-all;font-size:.76rem">${esc(detailSummary(e.detail))}</td></tr>`).join('')
  const exportParams = new URLSearchParams()
  if (filters.actionPrefix) exportParams.set('action', filters.actionPrefix)
  if (filters.actor) exportParams.set('actor', filters.actor)
  if (filters.result) exportParams.set('result', filters.result)
  const exportHref = `/console/api/audit/export${exportParams.size > 0 ? `?${exportParams}` : ''}`
  const secField = (name, label, max) =>
    `<div class="flabel">${label}</div><input name="${name}" type="number" min="1" ${max ? `max="${max}"` : ''} value="${config[name]}" ${isAdmin ? '' : 'disabled'}>`
  // 软强制两步验证（阶段 11A）：勾选角色登录且未绑定时仅提醒（不硬锁）。
  const r2faCheck = (role, label) =>
    `<label style="margin-right:.9rem"><input type="checkbox" name="r2fa-${role}" ${config.require2faRoles.includes(role) ? 'checked' : ''} ${isAdmin ? '' : 'disabled'}> ${label}</label>`
  const r2faRow = ['admin', 'auditor', 'employee'].map((role) => r2faCheck(role, { admin: '管理员', auditor: '审计员', employee: '成员' }[role])).join('')
  return `
<form class="searchbox" method="get" style="margin:0 0 .6rem">
<select name="action">${actionOptions}</select>
<input name="actor" value="${esc(filters.actor)}" placeholder="账号关键词" style="width:180px">
<select name="result"><option value="">全部结果</option>${resultOptions}</select>
<button class="primary">筛选</button>
<a class="btn" href="${exportHref}">导出 JSONL</a>
</form>
<table><tr><th>时间</th><th>账号</th><th>IP</th><th>动作</th><th>对象</th><th>结果</th><th>详情</th></tr>${rows || '<tr><td colspan="7">暂无审计事件</td></tr>'}</table>
<p class="mut" style="font-size:.82rem">审计日志只追加（data/audit.jsonl）、不可删改；此处倒序展示，单次最多 500 条；导出不受 500 限制，含全部命中事件。</p>
<h2 class="sect">安全设置</h2>
<form class="panel" onsubmit="saveSecurity(event)" style="padding:1rem">
<div style="display:flex;gap:1.4rem;flex-wrap:wrap">
<div>${secField('loginWindowMinutes', '登录失败统计窗口（分钟）', 1440)}</div>
<div>${secField('loginMaxFails', '窗口内最大失败次数', 100)}</div>
<div>${secField('lockoutMinutes', '锁定时长（分钟）', 1440)}</div>
<div>${secField('passwordMinLength', '密码最小长度', 128)}</div>
<div>${secField('passwordMinClasses', '密码最少字符类别', 3)}</div>
</div>
<div style="margin-top:.9rem">${isAdmin
    ? '<button class="primary">保存安全设置</button>'
    : '<span class="chip gray">审计员为只读角色，安全设置仅管理员可改</span>'}</div>
</form>
<h2 class="sect">两步验证（TOTP，阶段 11A）</h2>
<form class="panel" onsubmit="saveSecurity(event)" style="padding:1rem">
<p class="mut" style="margin:.2rem 0 .5rem">勾选的角色在登录但尚未绑定两步验证时会收到绑定提醒（软强制，不拒绝登录；成员在 /me 个人中心完成绑定，丢失认证器由成员页「重置2FA」救援）。硬强制属后续版本。</p>
<div style="display:flex;align-items:center;flex-wrap:wrap">${r2faRow}</div>
<div style="margin-top:.9rem">${isAdmin ? '<button class="primary">保存两步验证要求</button>' : '<span class="chip gray">审计员为只读角色</span>'}</div>
</form>
<h2 class="sect">邮件通知（阶段 11B）</h2>
<form class="panel" onsubmit="saveNotify(event)" style="padding:1rem">
<div style="display:flex;gap:1.2rem;flex-wrap:wrap;align-items:end">
<div><div class="flabel">模式</div><select name="mode" ${isAdmin ? '' : 'disabled'}>
${['off', 'file', 'smtp'].map((m) => `<option value="${m}" ${notifyConfig.mode === m ? 'selected' : ''}>${m === 'off' ? '关闭' : m === 'file' ? 'file（写 data/outbox/）' : 'smtp（真实发信）'}</option>`).join('')}
</select></div>
<div><div class="flabel">SMTP 主机</div><input name="host" value="${esc(notifyConfig.smtp.host)}" ${isAdmin ? '' : 'disabled'}></div>
<div><div class="flabel">端口</div><input name="port" type="number" value="${notifyConfig.smtp.port}" style="width:90px" ${isAdmin ? '' : 'disabled'}></div>
<div><label style="margin:0 0 .4rem"><input type="checkbox" name="secure" ${notifyConfig.smtp.secure ? 'checked' : ''} ${isAdmin ? '' : 'disabled'}> TLS 直连</label></div>
<div><div class="flabel">发件人（From）</div><input name="from" value="${esc(notifyConfig.smtp.from)}" ${isAdmin ? '' : 'disabled'}></div>
</div>
<div style="display:flex;gap:1.2rem;flex-wrap:wrap;margin-top:.6rem;align-items:end">
<div><div class="flabel">SMTP 用户名</div><input name="user" value="${esc(notifyConfig.smtp.auth.user)}" ${isAdmin ? '' : 'disabled'}></div>
<div><div class="flabel">SMTP 密码（留空 = 不改；已保存${notifyConfig.smtp.auth.passEnc !== '' ? '：是' : '：否'}）</div><input name="pass" type="password" placeholder="••••••" ${isAdmin ? '' : 'disabled'}></div>
<div style="flex:1;min-width:260px"><div class="flabel">管理员抄送（逗号分隔，配额告警同时抄送）</div><input name="adminNotify" value="${esc(notifyConfig.adminNotify.join(', '))}" ${isAdmin ? '' : 'disabled'}></div>
</div>
<div style="margin-top:.9rem">${isAdmin
    ? '<button class="primary">保存通知设置</button>'
    : '<span class="chip gray">审计员为只读角色</span>'} <span class="mut" style="font-size:.8rem;margin-left:.8rem">触发点：配额跨 80%（每账号每月一次，抄送管理员）、建号/禁用/重置密码（通知本人，绝不含密码原文）。</span></div>
</form>
<pre id="out" class="log" style="max-height:none"></pre>
<script>
async function saveSecurity(ev){ev.preventDefault();
 const f=new FormData(ev.target);const payload={};f.forEach((v,k)=>{if(v!=='')payload[k]=Number(v)});
 payload.require2faRoles=['admin','auditor','employee'].filter(function(r){var el=document.querySelector('input[name="r2fa-'+r+'"]');return el&&el.checked});
 const r=await fetch('/console/api/security/config',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(payload)});
 const t=await r.text();document.getElementById('out').textContent='HTTP '+r.status+' '+t;
 if(r.ok)setTimeout(()=>location.reload(),800)}
async function saveNotify(ev){ev.preventDefault();
 var f=new FormData(ev.target);
 var r=await fetch('/console/api/notify/config',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({
  mode:f.get('mode'),
  smtp:{host:f.get('host'),port:Number(f.get('port')),secure:f.get('secure')==='on',user:f.get('user'),pass:f.get('pass'),from:f.get('from')},
  adminNotify:String(f.get('adminNotify')||'').split(',').map(function(s){return s.trim()}).filter(Boolean)})});
 var t=await r.text();document.getElementById('out').textContent='HTTP '+r.status+' '+t;
 if(r.ok)setTimeout(()=>location.reload(),800)}
</script>`
}

async function handleApi({ req, res, path, dataDir, manifest, actor, twofaKey }) {
  const body = await readBody(req)
  const account = typeof body.account === 'string' ? body.account : ''
  const action = auditActionFor(path, body)
  const target = auditTargetFor(path, body)
  // 变更端点 result=ok/fail 都留痕（蓝图验收 1）；detail 只放标量元数据，
  // 密码与 API Key 原文绝不入审计（隐私红线）。
  const audit = (result, detail = null) => {
    if (action !== null) void auditAppend({ actor, action, target, result, detail })
  }
  const ok = (value, detail) => { audit('ok', detail ?? null); json(res, 200, value) }
  const fail = (status, message) => { audit('fail', { error: message }); json(res, status, { error: message }) }
  // 账号/钥匙类变更进串行队列（accounts.json/vkeys.json 读改写热点）；
  // 任务内部自带 try/catch 保证请求必被响应，队列链不吞错。
  const runLocked = (fn) => withAccountLock(async () => {
    try {
      await fn()
    } catch (error) {
      audit('fail', { error: String(error?.message ?? error) })
      json(res, 400, { error: String(error?.message ?? error) })
    }
  })
  // 按清单 spec 重发某实例的工具策略文件（账号角色变更/建号后；阶段 9）。
  const resyncHome = (instanceId) => {
    const spec = manifest.instances.find((s) => s.id === instanceId)
    if (spec !== undefined) syncInstanceHome(dataDir, spec)
  }
  try {
    switch (path) {
      case '/console/api/member/create': {
        runLocked(async () => {
          const password = body.password || generatePassword()
          const policy = checkPasswordPolicy(password, account, loadSecurityConfig(dataDir))
          if (!policy.ok) { fail(400, policy.message); return }
          const created = addAccount(dataDir, {
            account,
            instanceId: body.instance,
            role: body.role === 'auditor' ? 'auditor' : 'employee',
            displayName: body.displayName || undefined,
            password,
          })
          const { token } = issueVkey(dataDir, { account: created.account, instanceId: created.instanceId, models: '*' })
          // 新账号落在已有实例上：按实例归属账号的当前角色补发策略文件（阶段 9）。
          resyncHome(created.instanceId)
          // 通知本人（阶段 11B）：建号邮件不含密码原文（密码只在本响应显示一次）。
          void sendMail({ to: created.account, subject: `${NOTIFY_SUBJECT_PREFIX} 账号已创建`, text: `您的卡巴格企业平台账号 ${created.account} 已创建（实例 ${created.instanceId}）。请使用管理员发放的密码登录（本邮件不含密码）。` })
          ok({ ok: true, account: created.account, instance: created.instanceId, password, vkey: token }, { role: created.role, instanceId: created.instanceId })
        })
        return
      }
      case '/console/api/member/quota': {
        runLocked(async () => {
          const points = body.points === '' || body.points === undefined || body.points === null ? null : Number(body.points)
          if (!Number.isInteger(points) || points < 0) { fail(400, 'points 必须是非负整数，留空 = 不限'); return }
          const before = loadAccounts(dataDir).accounts.find((a) => a.account === account)?.monthlyPoints ?? null
          setQuota(dataDir, { account, monthlyPoints: points })
          ok({ ok: true, quota: points ?? '不限', unit: 'points' }, { from: before, to: points })
        })
        return
      }
      case '/console/api/member/reset-password': {
        runLocked(async () => {
          const password = generatePassword()
          setPassword(dataDir, account, password)
          // 通知本人（阶段 11B）：重置邮件绝不包含新密码原文（密码只对管理员一次性显示）。
          void sendMail({ to: account, subject: `${NOTIFY_SUBJECT_PREFIX} 密码已被重置`, text: `您的卡巴格企业平台账号 ${account} 的密码已被管理员重置，全部已登录设备已下线。新密码不在本邮件中，请联系管理员获取。` })
          ok({ ok: true, password })
        })
        return
      }
      case '/console/api/member/disable': {
        runLocked(async () => {
          const store = loadAccounts(dataDir)
          const rec = store.accounts.find((a) => a.account === account)
          if (rec === undefined) { fail(404, '账号不存在'); return }
          rec.disabled = true
          saveAccounts(dataDir, store)
          try { revokeVkey(dataDir, { account }) } catch { /* 本就没有钥匙 */ }
          // 通知本人（阶段 11B）：账号被禁用。
          void sendMail({ to: account, subject: `${NOTIFY_SUBJECT_PREFIX} 账号已被禁用`, text: `您的卡巴格企业平台账号 ${account} 已被管理员禁用。如有疑问请联系管理员。` })
          ok({ ok: true })
        })
        return
      }
      case '/console/api/member/enable': {
        runLocked(async () => {
          const store = loadAccounts(dataDir)
          const rec = store.accounts.find((a) => a.account === account)
          if (rec === undefined) { fail(404, '账号不存在'); return }
          rec.disabled = false
          saveAccounts(dataDir, store)
          const history = readJson(dataDir, 'vkeys.json', { vkeys: [] }).vkeys.filter((v) => v.account === account)
          const models = history.at(-1)?.models ?? '*'
          issueVkey(dataDir, { account, instanceId: rec.instanceId, models })
          ok({ ok: true, models })
        })
        return
      }
      case '/console/api/member/update': {
        runLocked(async () => {
          const patch = {}
          if (body.role !== undefined) patch.role = body.role
          if (body.department !== undefined) patch.department = body.department
          if (body.displayName !== undefined) patch.displayName = body.displayName
          const updated = updateAccount(dataDir, account, patch)
          // 角色变更 → 该账号所在实例的策略文件立即按实例归属账号的新角色重写
          // （实例侧 guard mtime 热生效，无需重启；阶段 9）。
          if (patch.role !== undefined) resyncHome(updated.instanceId)
          ok({ ok: true, role: updated.role, department: updated.department ?? '未分配' }, { fields: patch })
        })
        return
      }
      case '/console/api/idp/import': {
        runLocked(async () => {
          const members = Array.isArray(body.members) ? body.members : []
          if (members.length === 0) { fail(400, 'members 不能为空'); return }
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
              const password = generatePassword()
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
          ok({ ok: true, ...result }, { created: result.created.length, updated: result.updated.length, unchanged: result.unchanged, missingDisabled: result.missingDisabled.length })
          // 名册批量落了部门/角色：全量重发策略文件（幂等，三实例各一文件）。
          if (result.created.length + result.updated.length > 0) syncAllHomes(dataDir, manifest)
        })
        return
      }
      case '/console/api/provider/add': {
        const name = typeof body.name === 'string' ? body.name.trim() : ''
        const baseURL = typeof body.baseURL === 'string' ? body.baseURL.trim() : ''
        if (name === '' || baseURL === '') { fail(400, '供应商名称与请求地址必填'); return }
        if (listUpstreams(dataDir).some((u) => u.name === name)) { fail(409, '供应商已存在: ' + name); return }
        const models = typeof body.models === 'string' ? body.models.split(',').map((x) => x.trim()).filter(Boolean) : []
        if (models.length === 0) { fail(400, '至少提供一个模型 ID（后续可在模型页“增加模型”补充——该表单已移除，重新添加即可）'); return }
        try {
          setUpstream(dataDir, {
            name, baseURL, models,
            apiKey: body.apiKey,
            note: body.note || undefined,
            website: body.website || undefined,
            apiFormat: body.apiFormat === 'openai' ? 'openai' : 'anthropic',
            authEnv: typeof body.authEnv === 'string' ? body.authEnv : undefined,
            modelMapping: Array.isArray(body.modelMapping) ? body.modelMapping : undefined,
            fallbackModel: typeof body.fallbackModel === 'string' ? body.fallbackModel : undefined,
            configJSON: typeof body.configJSON === 'string' ? body.configJSON : undefined,
            fullUrl: body.fullUrl === true,
          })
          ok({ ok: true, name, models }, { models })
        } catch (error) {
          fail(400, String(error?.message ?? error))
        }
        return
      }
      case '/console/api/provider/remove': {
        const name = typeof body.name === 'string' ? body.name : ''
        try {
          removeUpstream(dataDir, { name })
          ok({ ok: true })
        } catch (error) {
          fail(400, String(error?.message ?? error))
        }
        return
      }
      case '/console/api/model/add': {
        if (typeof body.upstream !== 'string' || typeof body.model !== 'string' || body.model === '') {
          fail(400, 'upstream 与 model 必填')
          return
        }
        const meta = {}
        for (const k of ['context', 'maxOutput', 'mIn', 'mOut', 'mCacheR', 'mCacheW']) {
          if (typeof body[k] === 'string' && body[k] !== '') meta[k] = body[k]
        }
        try {
          addModel(dataDir, { upstream: body.upstream, model: body.model, meta: Object.keys(meta).length ? meta : undefined })
          ok({ ok: true, upstream: body.upstream, model: body.model }, { upstream: body.upstream })
        } catch (error) {
          fail(400, String(error?.message ?? error))
        }
        return
      }
      case '/console/api/model/remove': {
        if (typeof body.upstream !== 'string' || typeof body.model !== 'string') {
          fail(400, 'upstream 与 model 必填')
          return
        }
        try {
          removeModel(dataDir, { upstream: body.upstream, model: body.model })
          ok({ ok: true })
        } catch (error) {
          fail(400, String(error?.message ?? error))
        }
        return
      }
      case '/console/api/member/models': {
        const models = body.models === '*' ? '*' : Array.isArray(body.models) ? body.models.filter((m) => typeof m === 'string') : []
        setVkeyModels(dataDir, { account, models })
        ok({ ok: true, models }, { count: models === '*' ? '全部' : models.length })
        return
      }
      case '/console/api/instance/restart':
      case '/console/api/instance/stop':
      case '/console/api/instance/start': {
        const id = typeof body.id === 'string' ? body.id : ''
        if (!manifest.instances.some((s) => s.id === id)) { fail(404, '未知实例'); return }
        const op = path.split('/').at(-1)
        enqueueInstanceControl(dataDir, op, id)
        ok({ ok: true, action: op, id })
        return
      }
      case '/console/api/model/ratio': {
        initQuotas(dataDir)
        const model = typeof body.model === 'string' ? body.model.trim() : ''
        if (model === '') { fail(400, '模型 ID 必填'); return }
        const old = resolveRatios(model, undefined)
        try {
          const next = setModelRatio(dataDir, model, { ratio: Number(body.ratio), completionRatio: Number(body.completionRatio) })
          ok({ ok: true, model, ratio: next.ratio, completionRatio: next.completionRatio }, { old: { ratio: old.ratio, completionRatio: old.completionRatio }, new: next })
        } catch (error) {
          fail(400, String(error?.message ?? error))
        }
        return
      }
      case '/console/api/department/group-ratio': {
        initQuotas(dataDir)
        const department = typeof body.department === 'string' ? body.department.trim() : ''
        if (department === '') { fail(400, '部门名必填'); return }
        const old = resolveRatios(undefined, department)
        try {
          const groupRatio = setGroupRatio(dataDir, department, Number(body.ratio))
          ok({ ok: true, department, groupRatio }, { old: { groupRatio: old.groupRatio }, new: { groupRatio } })
        } catch (error) {
          fail(400, String(error?.message ?? error))
        }
        return
      }
      case '/console/api/security/config': {
        const patch = {}
        for (const key of ['loginWindowMinutes', 'loginMaxFails', 'lockoutMinutes', 'passwordMinLength', 'passwordMinClasses']) {
          if (body[key] !== undefined) patch[key] = Number(body[key])
        }
        if (body.require2faRoles !== undefined) patch.require2faRoles = body.require2faRoles
        if (Object.keys(patch).length === 0) { fail(400, '未提供任何要修改的安全参数'); return }
        const old = loadSecurityConfig(dataDir)
        let next
        try {
          next = saveSecurityConfig(dataDir, patch)
        } catch (error) {
          fail(400, String(error?.message ?? error))
          return
        }
        ok({ ok: true, config: next }, { old, new: next })
        return
      }
      case '/console/api/toolpolicy': {
        const old = loadToolPolicy(dataDir)
        let next
        try {
          next = saveToolPolicy(dataDir, body.roles)
        } catch (error) {
          fail(400, String(error?.message ?? error))
          return
        }
        // 保存即下发：全量重写实例 home 的 tool-policy.json（实例侧 guard
        // mtime 热生效）；写文件动作并入本条 toolpolicy.change 审计。
        const synced = syncAllHomes(dataDir, manifest)
        ok(
          { ok: true, policy: next, synced },
          { old, new: next, syncedInstances: synced.filter((r) => !r.skipped).map((r) => r.id) },
        )
        return
      }
      case '/console/api/invite/create': {
        // 邀请只发放 employee/auditor（admin 由既有管理员在成员页创建）；
        // 明文 code 只随本响应出现一次，审计与存储只落哈希。
        const role = body.role === 'auditor' ? 'auditor' : 'employee'
        const instanceId = typeof body.instanceId === 'string' ? body.instanceId : ''
        if (!manifest.instances.some((s) => s.id === instanceId)) { fail(400, '未知实例'); return }
        const department = typeof body.department === 'string' && body.department.trim() !== '' ? body.department.trim() : '未分配'
        if (!isValidEntityName(department)) { fail(400, '部门名格式非法（允许字母数字、@._- 与中文，1–64 字符）'); return }
        try {
          const { id, code, expiresAt } = createInvite(dataDir, {
            department,
            role,
            instanceId,
            expiresInHours: body.expiresInHours === undefined || body.expiresInHours === '' ? undefined : Number(body.expiresInHours),
          })
          ok({ ok: true, id, registerUrl: `/register?code=${code}`, expiresAt }, { role, department, instanceId })
        } catch (error) {
          fail(400, String(error?.message ?? error))
        }
        return
      }
      case '/console/api/invite/revoke': {
        const id = typeof body.id === 'string' ? body.id : ''
        if (!revokeInvite(dataDir, id)) { fail(404, '邀请不存在或已使用/已撤销'); return }
        ok({ ok: true })
        return
      }
      case '/console/api/member/2fa/reset': {
        // admin 救援：清指定账号的 2FA 绑定（账号丢失认证器时）。
        if (account === '') { fail(400, 'account 必填'); return }
        if (!loadAccounts(dataDir).accounts.some((a) => a.account === account)) { fail(404, '账号不存在'); return }
        if (!clearTwofa(dataDir, account)) { fail(404, '该账号未绑定两步验证'); return }
        ok({ ok: true, account })
        return
      }
      case '/console/api/notify/config': {
        // 通知设置（阶段 11B）：admin-only；pass 明文只在请求出现一次（回显打码）。
        try {
          const config = saveNotifyConfig(dataDir, {
            mode: body.mode,
            smtp: typeof body.smtp === 'object' && body.smtp !== null ? {
              host: body.smtp.host, port: body.smtp.port, secure: body.smtp.secure,
              user: body.smtp.user, pass: typeof body.smtp.pass === 'string' && body.smtp.pass !== '' ? body.smtp.pass : undefined,
              from: body.smtp.from,
            } : undefined,
            adminNotify: body.adminNotify,
          }, twofaKey)
          ok({ ok: true, config: { ...config, smtp: { ...config.smtp, auth: { ...config.smtp.auth, passEnc: config.smtp.auth.passEnc !== '' ? '(已保存)' : '' } } } }, { mode: config.mode, host: config.smtp.host, from: config.smtp.from, adminNotify: config.adminNotify, hasPassword: config.smtp.auth.passEnc !== '' })
        } catch (error) {
          fail(400, String(error?.message ?? error))
        }
        return
      }
      default:
        json(res, 404, { error: 'unknown console api' })
    }
  } catch (error) {
    audit('fail', { error: String(error?.message ?? error) })
    json(res, 400, { error: String(error?.message ?? error) })
  }
}

/**
 * 处理 /console 路径的全部请求（gateway 在裸 portal 分支里调用）。
 * 认证由 gateway 计算后传入；页面与只读 GET API 放行 admin/auditor，
 * employee 拒入；变更类 POST 仅 admin（auditor 得 403「审计员为只读角色」，
 * 拒绝也以 result=deny 留痕）。带 Origin 的 POST 校验同源
 * （配合 SameSite=Strict 双重 CSRF 防线），跨源拒绝同样留痕。
 * @returns true 表示已响应，gateway 不再处理。
 */
/** service token（readonly）允许的只读 API 白名单（阶段 12：member 列表/用量、audit 查询、toolpolicy 读）。 */
const SERVICE_READONLY_API_PATHS = new Set([
  '/console/api/member/list',
  '/console/api/member/usage',
  '/console/api/audit',
  '/console/api/toolpolicy',
])

export function handleConsole({ req, res, url, auth: jwtAuth, loginPage, manifest, getState, dataDir, runner, twofaKey }) {
  if (!url.pathname.startsWith('/console')) return false
  const path = url.pathname
  const query = url.searchParams
  // 服务令牌认证（阶段 12）：`Authorization: Bearer kbsvc-…` 命中即等价角色
  // （admin=管理员、readonly=只读白名单）。mtime 缓存读取，撤销下一请求生效；
  // actor.account 记 `svc:<名称>` 与人区分。仅对 /console/api/* 生效。
  let auth = jwtAuth
  let serviceAuth = null
  const bearer = /^Bearer (kbsvc-[\w-]+)$/.exec(req.headers.authorization ?? '')?.[1]
  if (bearer !== undefined) {
    serviceAuth = authenticateServiceToken(dataDir, bearer)
    if (serviceAuth !== null) auth = { record: { account: `svc:${serviceAuth.id}`, role: serviceAuth.role }, payload: null }
  }
  const actor = auth.error === undefined
    ? { account: auth.record.account, role: auth.record.role, ip: clientIp(req) }
    : null
  const isApiPath = path.startsWith('/console/api/')

  if (req.method === 'GET') {
    // 服务令牌：页面路由一律 401；readonly 只放行白名单端点。
    if (serviceAuth !== null && !isApiPath) {
      json(res, 401, { error: 'service token 仅允许 /console/api/* 端点' })
      return true
    }
    if (serviceAuth !== null && serviceAuth.role === 'readonly' && !SERVICE_READONLY_API_PATHS.has(path)) {
      // 白名单外拒绝同样留 deny 痕（P2-8），actor 记 svc: 身份。
      void auditAppend({ actor, action: 'security.service_token_denied', target: path, result: 'deny', detail: { role: 'readonly' } })
      json(res, 403, { error: 'readonly 服务令牌仅允许只读白名单端点' })
      return true
    }
    if (auth.error !== undefined) {
      res.writeHead(401, { 'content-type': 'text/html; charset=utf-8' })
      res.end(loginPage())
      return true
    }
    if (serviceAuth === null && auth.record.role !== 'admin' && auth.record.role !== 'auditor') {
      res.writeHead(403, { 'content-type': 'text/plain; charset=utf-8' })
      res.end('管理台仅限平台管理员与审计员。')
      return true
    }
    if (path === '/console/providers/new') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' })
      res.end(SHELL('添加模型供应商', 'models', manifest, getState, dataDir, newProviderPage(), '/console/models'))
      return true
    }
    if (path === '/console/api/plugin/jobs') {
      json(res, 200, { jobs: runner.list() })
      return true
    }
    if (path === '/console/api/toolpolicy') {
      json(res, 200, { policy: loadToolPolicy(dataDir) })
      return true
    }
    // 成员列表（阶段 12 数据源：user_list 工具/服务令牌白名单端点）。
    if (path === '/console/api/member/list') {
      const d = new Date()
      const month = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
      const usage = readJson(dataDir, 'usage.json', { months: {} }).months[month] ?? {}
      const members = listAccounts(dataDir).map((a) => {
        const e = usage[a.account] ?? {}
        return {
          account: a.account, displayName: a.displayName, department: a.department,
          role: a.role, instanceId: a.instanceId, disabled: a.disabled,
          monthlyPoints: a.monthlyPoints ?? null, pointsUsed: e.points ?? 0,
          tokensIn: e.tokensIn ?? 0, tokensOut: e.tokensOut ?? 0, requests: e.requests ?? 0,
        }
      })
      json(res, 200, { month, members })
      return true
    }
    // 单成员当月用量（阶段 12 数据源：user_quota_query 工具）。
    if (path === '/console/api/member/usage') {
      const account = query.get('account') ?? ''
      if (account === '') { json(res, 400, { error: 'account 查询参数必填' }); return true }
      // loadAccounts（原始记录）而非 listAccounts 映射：monthlyPoints/monthlyTokens 在映射中被裁剪。
      const record = loadAccounts(dataDir).accounts.find((a) => a.account === account)
      if (record === undefined) { json(res, 404, { error: `账号不存在: ${account}` }); return true }
      const d = new Date()
      const month = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
      const e = readJson(dataDir, 'usage.json', { months: {} }).months[month]?.[account] ?? {}
      const points = e.points ?? 0
      const tokens = (e.tokensIn ?? 0) + (e.tokensOut ?? 0)
      const remainingPoints = Number.isFinite(record.monthlyPoints) ? Math.max(0, record.monthlyPoints - points) : null
      json(res, 200, {
        account, month,
        points, monthlyPoints: record.monthlyPoints ?? null, remainingPoints,
        tokensIn: e.tokensIn ?? 0, tokensOut: e.tokensOut ?? 0,
        tokensUsed: tokens, monthlyTokens: record.monthlyTokens ?? null,
        requests: e.requests ?? 0,
        legacy: !(Number.isFinite(record.monthlyPoints) || Number.isFinite(record.monthlyTokens)) ? false : !Number.isFinite(record.monthlyPoints),
        unlimited: !Number.isFinite(record.monthlyPoints) && !Number.isFinite(record.monthlyTokens),
      })
      return true
    }
    if (path === '/console/api/audit') {
      const limitParam = Number.parseInt(query.get('limit') ?? '', 10)
      json(res, 200, { events: auditQuery({ ...auditFiltersFromQuery(query), limit: Number.isInteger(limitParam) && limitParam > 0 ? limitParam : undefined }) })
      return true
    }
    if (path === '/console/api/audit/export') {
      const filters = auditFiltersFromQuery(query)
      const events = auditQuery({ ...filters, limit: 1_000_000 })
      // 导出动作本身入审计（auditor 也可导出，是其核心职责）。
      void auditAppend({ actor, action: 'audit.export', target: 'audit.jsonl', result: 'ok', detail: { actionPrefix: filters.actionPrefix || null, actor: filters.actor || null, result: filters.result || null, count: events.length } })
      res.writeHead(200, {
        'content-type': 'application/x-ndjson; charset=utf-8',
        'content-disposition': 'attachment; filename="audit-export.jsonl"',
      })
      res.end(events.map((e) => JSON.stringify(e)).join('\n') + (events.length > 0 ? '\n' : ''))
      return true
    }
    const ctx = { dataDir, manifest, getState, query }
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' })
    if (path === '/console') res.end(SHELL('总览', '', manifest, getState, dataDir, overviewPage(ctx)))
    else if (path === '/console/members') res.end(SHELL('成员与额度', 'members', manifest, getState, dataDir, membersPage(ctx)))
    else if (path === '/console/roles') res.end(SHELL('部门与角色', 'roles', manifest, getState, dataDir, rolesPage(ctx)))
    else if (path === '/console/models') {
      const html = SHELL('模型与权限', 'models', manifest, getState, dataDir, modelsPage(ctx))
      res.end(html)
    }
    else if (path === '/console/instances') res.end(SHELL('实例管理', 'instances', manifest, getState, dataDir, instancesPage(ctx)))
    else if (path === '/console/instances/log') res.end(SHELL('实例日志', 'instances', manifest, getState, dataDir, instanceLogPage(ctx)))
    else if (path === '/console/plugins') res.end(SHELL('插件管理', 'plugins', manifest, getState, dataDir, pluginsPage({ ...ctx, runner })))
    else if (path === '/console/audit') res.end(SHELL('安全与审计', 'audit', manifest, getState, dataDir, auditPage({ ...ctx, role: auth.record.role })))
    else { res.writeHead(404, { 'content-type': 'text/plain; charset=utf-8' }); res.end('unknown console page') }
    return true
  }

  if (req.method === 'POST' && path.startsWith('/console/api/')) {
    if (auth.error !== undefined) { json(res, 401, { error: 'unauthenticated' }); return true }
    if (auth.record.role !== 'admin') {
      const deniedAction = auditActionFor(path)
      if (deniedAction !== null) {
        void auditAppend({ actor, action: deniedAction, result: 'deny', detail: { reason: auth.record.role === 'auditor' ? 'auditor-readonly' : 'role-forbidden' } })
      }
      json(res, 403, { error: auth.record.role === 'auditor' ? '审计员为只读角色' : '仅平台管理员可执行变更操作' })
      return true
    }
    const origin = req.headers.origin
    if (origin !== undefined) {
      let sameOrigin = true
      try {
        sameOrigin = new URL(origin).host === (req.headers.host ?? '')
      } catch { sameOrigin = false }
      if (!sameOrigin) {
        const deniedAction = auditActionFor(path)
        if (deniedAction !== null) {
          void auditAppend({ actor, action: deniedAction, result: 'deny', detail: { reason: 'origin-check' } })
        }
        json(res, 403, { error: 'cross-origin refused' })
        return true
      }
    }
    if (path === '/console/api/plugin/job') {
      void readBody(req).then((body) => {
        const jobAction = auditActionFor(path, body)
        try {
          const job = runner.enqueue({ type: body.type, spec: body.spec, ids: body.ids, skipPrecheck: body.skipPrecheck })
          void auditAppend({ actor, action: jobAction, target: auditTargetFor(path, body), result: 'ok', detail: { type: body.type, ids: body.ids ?? 'all' } })
          json(res, 200, { ok: true, job: { id: job.id, state: job.state } })
        } catch (error) {
          void auditAppend({ actor, action: jobAction, target: auditTargetFor(path, body), result: 'fail', detail: { type: body.type, error: String(error?.message ?? error) } })
          json(res, 409, { error: String(error?.message ?? error) })
        }
      })
      return true
    }
    void handleApi({ req, res, path, dataDir, manifest, actor, twofaKey }).catch((error) => {
      console.error('[console] api crashed:', error?.stack ?? error)
      try { json(res, 500, { error: 'console api crashed' }) } catch { /* 已响应 */ }
    })
    return true
  }
  return false
}
