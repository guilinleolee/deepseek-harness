/**
 * 配额点数与倍率冒烟测试（零测试框架，node 直接运行）。
 *
 * 在临时目录验证：ratios.json 缺省生成与 mtime 缓存生效、resolveRatios
 * 未配置回退/配置生效、非法倍率（≤0/非有限数）拒绝落盘、estimatePoints /
 * tokensToPoints 公式手算对账。不触碰生产 data/ 与 8460/9400 端口。
 *
 * 运行：node test/quota-points-smoke.mjs
 */
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { estimatePoints, initQuotas, loadRatios, resolveRatios, setGroupRatio, setModelRatio, tokensToPoints } from '../quotas.mjs'

const DATA = mkdtempSync(join(tmpdir(), 'lyz-quota-smoke-'))
let passed = 0
let failed = 0
const check = (name, cond) => {
  if (cond === true) { passed += 1; console.log(`  ok  ${name}`) } else { failed += 1; console.error(`FAIL  ${name}`) }
}
const near = (a, b, eps = 1e-9) => Math.abs(a - b) < eps
const throws = (fn) => {
  try {
    fn()
    return false
  } catch {
    return true
  }
}

/* ── 1. 缺省生成与未配置回退 ─────────────────────────────────────────────── */
console.log('# 缺省生成与未配置回退')
initQuotas(DATA)
const fresh = loadRatios()
check('缺省 ratios.json 自动生成', existsSync(join(DATA, 'ratios.json')))
check('缺省结构 models/groups 空、补全缺省 3',
  Object.keys(fresh.models).length === 0 && Object.keys(fresh.groups).length === 0 && fresh.defaultCompletionRatio === 3)
const r = resolveRatios('unknown-model', '未知部门')
check('未配置模型 ratio=1', r.ratio === 1)
check('未配置模型 completionRatio=defaultCompletionRatio(3)', r.completionRatio === 3)
check('未配置部门 groupRatio=1', r.groupRatio === 1)
check('resolveRatios 缺省参数（undefined 模型/部门）同回退', near(resolveRatios().ratio, 1) && near(resolveRatios().groupRatio, 1))

/* ── 2. 配置生效与 mtime 缓存刷新 ────────────────────────────────────────── */
console.log('# 配置生效')
setModelRatio(DATA, 'glm-5.3', { ratio: 2, completionRatio: 3 })
setGroupRatio(DATA, '设计部', 1.5)
const r2 = resolveRatios('glm-5.3', '设计部')
check('模型倍率写入后 resolve 立即生效', r2.ratio === 2 && r2.completionRatio === 3)
check('部门倍率写入后 resolve 立即生效', r2.groupRatio === 1.5)
check('其他模型不受影响', resolveRatios('other-model', '设计部').ratio === 1)
check('其他部门不受影响', resolveRatios('glm-5.3', '工程部').groupRatio === 1)
const persisted = JSON.parse(readFileSync(join(DATA, 'ratios.json'), 'utf8'))
check('落盘结构对齐蓝图示例', persisted.models['glm-5.3'].ratio === 2 && persisted.groups['设计部'] === 1.5 && persisted.defaultCompletionRatio === 3)

/* ── 3. 非法值拒绝落盘 ──────────────────────────────────────────────────── */
console.log('# 非法倍率拒绝')
check('ratio=0 被拒', throws(() => setModelRatio(DATA, 'x', { ratio: 0, completionRatio: 3 })))
check('ratio=-1 被拒', throws(() => setModelRatio(DATA, 'x', { ratio: -1, completionRatio: 3 })))
check('ratio=NaN 被拒', throws(() => setModelRatio(DATA, 'x', { ratio: Number.NaN, completionRatio: 3 })))
check('ratio=Infinity 被拒', throws(() => setModelRatio(DATA, 'x', { ratio: Number.POSITIVE_INFINITY, completionRatio: 3 })))
check('completionRatio=0 被拒', throws(() => setModelRatio(DATA, 'x', { ratio: 1, completionRatio: 0 })))
check('分组倍率 -2 被拒', throws(() => setGroupRatio(DATA, '设计部', -2)))
check('分组倍率非数值被拒（NaN）', throws(() => setGroupRatio(DATA, '设计部', Number('abc'))))
check('空模型 ID 被拒', throws(() => setModelRatio(DATA, '  ', { ratio: 1, completionRatio: 3 })))
check('空部门名被拒', throws(() => setGroupRatio(DATA, '', 1)))
check('被拒值不落盘（x 模型未出现）', resolveRatios('x', '设计部').ratio === 1)
check('被拒后原配置完好', resolveRatios('glm-5.3', '设计部').ratio === 2 && resolveRatios('glm-5.3', '设计部').groupRatio === 1.5)

/* ── 4. 计点公式手算对账 ─────────────────────────────────────────────────── */
console.log('# 计点公式对账')
const base = { ratio: 1, completionRatio: 3, groupRatio: 1 }
check('缺省倍率 (100,20) = 100 + 20×3 = 160', near(tokensToPoints(100, 20, base), 160))
check('模型倍率 2：(100,20) = 200 + 120 = 320', near(tokensToPoints(100, 20, { ratio: 2, completionRatio: 3, groupRatio: 1 }), 320))
check('分组倍率 1.5：320 × 1.5 = 480', near(tokensToPoints(100, 20, { ratio: 2, completionRatio: 3, groupRatio: 1.5 }), 480))
check('自定义补全倍率 2：(100×2 + 20×2×2) = 280', near(tokensToPoints(100, 20, { ratio: 2, completionRatio: 2, groupRatio: 1 }), 280))
check('0 tokens 计 0 点', near(tokensToPoints(0, 0, base), 0))
check('非有限输入按 0 计', near(tokensToPoints(Number.NaN, Number.POSITIVE_INFINITY, base), 0))
check('预扣估点同公式：(1000,1024) = 1000 + 3072 = 4072', near(estimatePoints(1000, 1024, base), 4072))
check('预扣与实结同倍率下公式一致', near(estimatePoints(100, 20, { ratio: 2, completionRatio: 3, groupRatio: 1.5 }), tokensToPoints(100, 20, { ratio: 2, completionRatio: 3, groupRatio: 1.5 })))

/* ── 5. 原型链污染键过滤（写入拒绝 + 读取剔除）──────────────────────────── */
console.log('# 原型链污染键过滤')
for (const bad of ['__proto__', 'constructor', 'prototype']) {
  check(`模型键 ${bad} 写入被拒`, throws(() => setModelRatio(DATA, bad, { ratio: 2, completionRatio: 3 })))
  check(`部门键 ${bad} 写入被拒`, throws(() => setGroupRatio(DATA, bad, 2)))
}
// 手改文件注入危险键：读取侧剔除并回写干净形态
writeFileSync(join(DATA, 'ratios.json'), `${JSON.stringify({
  models: { '__proto__': { ratio: 9, completionRatio: 9 }, 'ok-model': { ratio: 3, completionRatio: 2 } },
  defaultCompletionRatio: 3,
  groups: { constructor: 9, '设计部': 2 },
}, null, 2)}\n`)
const cleaned = loadRatios()
// 用 hasOwn 判定：obj['__proto__'] 会命中 Object.prototype 的 getter，不代表 own 键存在。
check('危险模型键被剔除、合法键保留', !Object.hasOwn(cleaned.models, '__proto__') && cleaned.models['ok-model']?.ratio === 3)
check('危险部门键被剔除、合法键保留', !Object.hasOwn(cleaned.groups, 'constructor') && cleaned.groups['设计部'] === 2)
const rr = resolveRatios('__proto__', '__proto__')
check('危险键 resolve 回退缺省（计点不产 NaN）', rr.ratio === 1 && rr.completionRatio === 3 && rr.groupRatio === 1 && Number.isFinite(tokensToPoints(100, 20, rr)))
const onDisk = JSON.parse(readFileSync(join(DATA, 'ratios.json'), 'utf8'))
check('剔除后回写文件无危险键', !Object.hasOwn(onDisk.models, '__proto__') && !Object.hasOwn(onDisk.groups, 'constructor') && onDisk.groups['设计部'] === 2)

rmSync(DATA, { recursive: true, force: true })
console.log(`\n通过 ${passed}，失败 ${failed}`)
if (failed > 0) process.exit(1)
