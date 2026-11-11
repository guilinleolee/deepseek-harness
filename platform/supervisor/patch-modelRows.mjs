// modelRows builder
const MR = '  const modelRows = catalog.map((m) => {\n'
+ '    const u = upstreams.find((x) => x.models.includes(m))\n'
+ '    const meta = metaFor(m)\n'
+ '    const usedBy = accounts.filter((a) => {\n'
+ "      const vk = activeVkeyFor(dataDir, a.account)\n"
+ "      return vk !== undefined && (vk.models === '*' || vk.models.includes(m))\n"
+ '    }).length\n'
+ "    const del = `<button class=\"warn\" onclick=\"removeModel('${esc(u?.name ?? '')}','${esc(m)}',${usedBy})\">删除</button>`\n"
+ '    return `<tr><td>${esc(m)}</td><td>${esc(u?.name ?? \u2014)}</td><td>${meta ? esc(meta.context) : \u2014} / ${meta ? esc(meta.maxOutput) : \u2014}</td>\n'
+ '<td>${meta ? esc(meta.mIn) : \u2014}</td><td>${meta ? esc(meta.mOut) : \u2014}</td><td>${meta ? esc(meta.mCacheR) : \u2014}</td><td>${meta ? esc(meta.mCacheW) : \u2014}</td>\n'
+ '<td>${usedBy}</td><td><span class="chip green">已启用</span></td><td>${del}</td></tr>`\n'
+ '  }).join(\'\')\n'
module.exports = { MR }
