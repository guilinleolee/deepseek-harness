/**
 * 落云宗企业平台 · 管理台操作面（控制台阶段首增量）。
 *
 * 在只读总览之上提供四个管理页与对应变更 API，全部仅限平台管理员
 * （复用网关 JWT 门禁，POST 另校验 Origin 同源）：
 * - /console            总览（实例状态、当月用量、漂移摘要、Relay 元日志尾）
 * - /console/members    成员与额度：建号、改额度、重置密码（一次性显示）、
 *   禁用/启用（禁用 = 登录阻断 + tokenEpoch+1 + 虚拟钥匙吊销，Relay 同步拒绝）
 * - /console/models     模型与权限：成员×模型授权矩阵（编辑活跃虚拟钥匙白名单）
 * - /console/instances  实例管理：重启/停止/启动（经 daemon 控制通道）
 * - /console/plugins    插件管理：期望态只读视图（投放仍走 CLI）
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

const SHELL = (title, active, manifest, body) => {
  const nav = [`总览|/console`, ...PAGES.map((p) => `${PAGE_TITLES[p]}|/console/${p}`)]
    .map((pair) => {
      const [label, href] = pair.split('|')
      const on = href === (active === '' ? '/console' : `/console/${active}`)
      return `<a class="${on ? 'on' : ''}" href="${href}">${label}</a>`
    }).join('')
  return `<!doctype html><meta charset="utf-8"><title>落云宗 · ${title}</title>
<style>
body{font-family:system-ui;background:#101426;color:#e8eaf6;margin:0;display:flex}
nav{width:190px;min-height:100vh;background:#0c101f;border-right:1px solid #39406e;padding:1.2rem .8rem;box-sizing:border-box}
nav a{display:block;color:#c5cae9;text-decoration:none;padding:.5rem .7rem;border-radius:6px;margin:.15rem 0}
nav a.on,nav a:hover{background:#232a4d}
main{flex:1;padding:1.6rem 2rem}
h1,h2{color:#c5cae9}table{border-collapse:collapse;margin:.6rem 0 1.4rem;width:100%}
td,th{border:1px solid #39406e;padding:.45rem .7rem;font-size:.9rem;text-align:left}
input,select,button{padding:.35rem .55rem;border-radius:5px;border:1px solid #39406e;background:#0c101f;color:#e8eaf6}
button{background:#4f6ef7;border:none;cursor:pointer;margin:.1rem}
button.warn{background:#b0434a}form.inline{display:inline-block;margin:.1rem}
a{color:#8ab4ff}.mut{color:#9fa8da;font-size:.88rem}
</style>
<nav><h1 style="font-size:1.1rem;margin:.2rem 0 1rem">落云宗</h1>${nav}</nav>
<main><h1>${title}</h1>${body}</main>`
}

/* ── 页面 ────────────────────────────────────────────────────────────────── */

function overviewPage({ manifest, getState, dataDir }) {
  const d = new Date()
  const month = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
  const state = getState()
  const usageMonth = readJson(dataDir, 'usage.json', { months: {} }).months[month] ?? {}
  const accounts = listAccounts(dataDir)
  const drift = readJson(dataDir, 'drift.json', { checks: {} }).checks
  const rows = manifest.instances.map((spec) => {
    const rec = state.instances[spec.id] ?? {}
    const mem = rec.memoryKB ? `${(rec.memoryKB / 1024).toFixed(1)} MB` : '—'
    const disk = rec.diskBytes !== null && rec.diskBytes !== undefined ? `${(rec.diskBytes / 1024 / 1024).toFixed(1)} MB` : '—'
    const a = accounts.find((x) => x.account === spec.account)
    const e = usageMonth[spec.account] ?? { tokensIn: 0, tokensOut: 0, requests: 0 }
    const used = e.tokensIn + e.tokensOut
    const quota = a?.monthlyTokens
    const usageText = Number.isFinite(quota) ? (used >= quota ? `🔴 ${used}/${quota}` : `${used}/${quota}`) : `${used}/不限`
    const c = drift[spec.id]
    const driftText = c === undefined ? '未检查' : (() => {
      const stale = c.diffs.filter((x) => x.stale).length
      const fresh = c.diffs.length - stale
      return c.diffs.length === 0 ? '✅ 对齐' : `🔴 ${stale} 超时 / 🟡 ${fresh} 新发现`
    })()
    return `<tr><td>${spec.id}</td><td>${esc(spec.account)}</td><td>${rec.state ?? '—'}</td><td>${spec.port}</td><td>${mem}</td><td>${disk}</td><td>${usageText}</td><td>${driftText}</td></tr>`
  }).join('')
  let relayTail = '<tr><td colspan="5">暂无转发记录</td></tr>'
  try {
    relayTail = readFileSync(join(dataDir, 'logs', 'relay.log'), 'utf8').trim().split('\n').slice(-10).map((line) => {
      try {
        const e = JSON.parse(line)
        return `<tr><td>${e.at}</td><td>${esc(e.account)}</td><td>${esc(e.model)}</td><td>${esc(e.upstream)}</td><td>${e.status}（${e.ms} ms）</td></tr>`
      } catch { return '' }
    }).join('')
  } catch { /* 无日志文件 */ }
  return SHELL('总览', '', manifest, `
<p class="mut">${month} · 服务器本地时区 · <a href="http://${manifest.gatewayHost}:${manifest.portalPort}/">员工入口</a></p>
<h2>实例与用量</h2><table><tr><th>实例</th><th>账号</th><th>状态</th><th>端口</th><th>内存</th><th>磁盘</th><th>本月 tokens</th><th>漂移</th></tr>${rows}</table>
<h2>Relay 转发（最近 10 条元数据）</h2><table><tr><th>时间</th><th>账号</th><th>模型</th><th>上游</th><th>状态</th></tr>${relayTail}</table>
<p class="mut">隐私边界：本页只聚合元数据，不包含任何会话或内容正文（任务书决定 5）。</p>`)
}

function membersPage({ dataDir, manifest, getState }) {
  const d = new Date()
  const month = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
  const usage = readJson(dataDir, 'usage.json', { months: {} }).months[month] ?? {}
  const state = getState()
  const rows = listAccounts(dataDir).map((a) => {
    const e = usage[a.account] ?? { tokensIn: 0, tokensOut: 0, requests: 0 }
    const used = e.tokensIn + e.tokensOut
    const quota = a.monthlyTokens
    const quotaText = Number.isFinite(quota) ? `${used}/${quota}` : `${used}/不限`
    return `<tr><td>${esc(a.displayName)}</td><td>${esc(a.account)}</td><td>${esc(a.role)}</td><td>${esc(a.instanceId)}</td>
<td>${a.disabled ? '🔴 已禁用' : '🟢 正常'}</td><td>${quotaText}</td><td>${e.requests}</td>
<td><form class="inline" onsubmit="api(event,'/console/api/member/quota',this)"><input type="hidden" name="account" value="${esc(a.account)}"><input name="tokens" size="9" placeholder="新额度/留空不限"><button>改额度</button></form>
<form class="inline" onsubmit="api(event,'/console/api/member/reset-password',this)"><input type="hidden" name="account" value="${esc(a.account)}"><button>重置密码</button></form>
${a.disabled
    ? `<form class="inline" onsubmit="api(event,'/console/api/member/enable',this)"><input type="hidden" name="account" value="${esc(a.account)}"><button>启用</button></form>`
    : `<form class="inline" onsubmit="api(event,'/console/api/member/disable',this)"><input type="hidden" name="account" value="${esc(a.account)}"><button class="warn">禁用</button></form>`}</td></tr>`
  }).join('')
  const instanceOptions = manifest.instances.map((s) => `<option value="${s.id}">${s.id}（${esc(s.account)} · ${state.instances[s.id]?.state ?? '—'}）</option>`).join('')
  return SHELL('成员与额度', 'members', manifest, `
<table><tr><th>成员</th><th>账号</th><th>角色</th><th>实例</th><th>状态</th><th>本月已用/额度</th><th>请求</th><th>操作</th></tr>${rows}</table>
<h2>添加成员</h2>
<form onsubmit="createMember(event)">
账号 <input name="account" placeholder="name@company" required>
显示名 <input name="displayName">
角色 <select name="role"><option value="employee">员工</option><option value="auditor">审计员</option></select>
实例 <select name="instance">${instanceOptions}</select>
密码 <input name="password" placeholder="留空自动生成">
<button>创建</button></form>
<pre id="out" class="mut"></pre>
<p class="mut">禁用 = 立即下线 + 吊销虚拟钥匙（Relay 同步拒绝）；启用 = 重新签发钥匙（模型白名单沿用历史）。重置/创建的密码只显示一次。</p>
<script>
async function api(ev,path,form){ev.preventDefault();
 const f=new FormData(form||ev.target);const payload={};f.forEach((v,k)=>payload[k]=v);
 const r=await fetch(path,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(payload)});
 const t=await r.text();let msg=t;try{msg=JSON.stringify(JSON.parse(t))}catch{}
 if(path.includes('reset-password')&&r.ok){const p=JSON.parse(t).password;alert('新密码（只显示一次）：'+p)}
 document.getElementById('out').textContent='HTTP '+r.status+' '+msg;
 if(r.ok)setTimeout(()=>location.reload(),800)}
async function createMember(ev){await api(ev,'/console/api/member/create',true)}
</script>`)
}

function modelsPage({ dataDir, manifest }) {
  const catalog = []
  for (const u of listUpstreams(dataDir).filter((x) => !x.revoked)) for (const m of u.models) if (!catalog.includes(m)) catalog.push(m)
  const vkeys = readJson(dataDir, 'vkeys.json', { vkeys: [] }).vkeys
  const accounts = listAccounts(dataDir)
  const rows = accounts.map((a) => {
    const vk = [...vkeys].reverse().find((v) => v.account === a.account && !v.revoked)
    const cells = catalog.map((m) => {
      const on = vk !== undefined && (vk.models === '*' || vk.models.includes(m))
      return `<td><input type="checkbox" form="matrix" name="${esc(a.account)}|${m}" ${on ? 'checked' : ''}></td>`
    }).join('')
    return `<tr><td>${esc(a.displayName)}</td><td>${esc(a.account)}</td>${cells}</tr>`
  }).join('')
  const head = catalog.map((m) => `<th>${esc(m)}</th>`).join('')
  return SHELL('模型与权限', 'models', manifest, `
<p class="mut">勾选 = 该成员的虚拟钥匙可转发该模型；去掉勾后下一请求即被 Relay 拒绝（服务器强制）。保存替换该成员的完整白名单。</p>
<form id="matrix" onsubmit="saveMatrix(event)">
<table><tr><th>成员</th>${head}</tr>${rows}</table>
<button>保存矩阵</button></form>
<h2>上游提供方</h2><table><tr><th>名称</th><th>BaseURL</th><th>模型</th><th>Key</th></tr>
${listUpstreams(dataDir).map((u) => `<tr><td>${esc(u.name)}</td><td>${esc(u.baseURL)}</td><td>${u.models.map(esc).join(', ')}</td><td>${esc(u.keyFingerprint ?? '—')}</td></tr>`).join('')}</table>
<pre id="out" class="mut"></pre>
<script>
async function saveMatrix(ev){ev.preventDefault();
 const f=new FormData(ev.target);const byAccount={};
 for(const [k,v] of f.entries()){if(!v)continue;const [account,model]=k.split('|');(byAccount[account]??=[]).push(model)}
 for(const [account,models] of Object.entries(byAccount)){
  const r=await fetch('/console/api/member/models',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({account,models})});
  if(!r.ok){document.getElementById('out').textContent='保存失败: '+account;return}}
 document.getElementById('out').textContent='矩阵已保存';setTimeout(()=>location.reload(),600)}
</script>`)
}

function instancesPage({ manifest, getState }) {
  const state = getState()
  const rows = manifest.instances.map((spec) => {
    const rec = state.instances[spec.id] ?? { state: '—' }
    const ops = ['restart', 'stop', 'start'].map((op) => {
      const disabled = (op === 'start' && rec.pid) || (op === 'restart' && !rec.pid)
      return `<form class="inline" onsubmit="api(event,'/console/api/instance/${op}')"><input type="hidden" name="id" value="${spec.id}"><button ${disabled ? 'disabled' : ''}>${op === 'restart' ? '重启' : op === 'stop' ? '停止' : '启动'}</button></form>`
    }).join('')
    return `<tr><td>${spec.id}</td><td>${esc(spec.account)}</td><td>${rec.state}</td><td>${spec.port}</td><td>${spec.uid}</td><td>${ops}</td></tr>`
  }).join('')
  return SHELL('实例管理', 'instances', manifest, `
<table><tr><th>实例</th><th>账号</th><th>状态</th><th>端口</th><th>uid</th><th>操作</th></tr>${rows}</table>
<p class="mut">操作经 daemon 控制通道执行（与 CLI 同一机制）；刷新页面查看最新状态。</p>
<pre id="out" class="mut"></pre>
<script>
async function api(ev,path){ev.preventDefault();
 const f=new FormData(ev.target);const payload={};f.forEach((v,k)=>payload[k]=v);
 const r=await fetch(path,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(payload)});
 document.getElementById('out').textContent='HTTP '+r.status+' '+await r.text();
 if(r.ok)setTimeout(()=>location.reload(),900)}
</script>`)
}

function pluginsPage({ dataDir, manifest, getState }) {
  const desired = readJson(dataDir, 'plugins.json', { instances: {} })
  const state = getState()
  const rows = manifest.instances.map((spec) => {
    const list = desired.instances[spec.id] ?? []
    const items = list.length === 0
      ? '<td colspan="2">—</td>'
      : list.map((p) => `<td>${esc(p.name)}</td><td>${esc(p.spec === p.name ? '(最新)' : p.spec)} · ${p.state === 'removed' ? '已移除' : p.state === 'staged' ? '暂存（重启生效）' : p.state}</td>`).join('')
    const running = state.instances[spec.id]?.state === 'running'
    return `<tr><td>${spec.id}</td><td>${running ? '运行中' : (state.instances[spec.id]?.state ?? '—')}</td>${items}</tr>`
  }).join('')
  return SHELL('插件管理', 'plugins', manifest, `
<table><tr><th>实例</th><th>实例状态</th><th>插件</th><th>版本/状态</th></tr>${rows}</table>
<p class="mut">插件投放（含真启动预检）当前经 CLI：<code>node supervisor.mjs plugin-push --plugin &lt;spec&gt; --ids &lt;id&gt;</code>。异步投放任务队列落地后，此页将接管安装/暂存/预检/回滚操作。</p>`)
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
        const models = Array.isArray(body.models) ? body.models.filter((m) => typeof m === 'string') : []
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
    const ctx = { dataDir, manifest, getState }
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' })
    if (path === '/console') res.end(overviewPage(ctx))
    else if (path === '/console/members') res.end(membersPage(ctx))
    else if (path === '/console/models') res.end(modelsPage(ctx))
    else if (path === '/console/instances') res.end(instancesPage(ctx))
    else if (path === '/console/plugins') res.end(pluginsPage(ctx))
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
