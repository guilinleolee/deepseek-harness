// 一次性组装脚本：从部件文件拼装 console.mjs。用完即删。
// 零模板字符串、零转义问题——全部用字符串数组 + join。
import { readFileSync, writeFileSync } from 'node:fs'

const consoleFile = new URL('./console.mjs', import.meta.url)

// 读取部件
const modelRows = readFileSync(new URL('./part-modelRows.txt', import.meta.url), 'utf8')
const instances = readFileSync(new URL('./part-instances.txt', import.meta.url), 'utf8')
const plugins = readFileSync(new URL('./part-plugins.txt', import.meta.url), 'utf8')

let s = readFileSync(consoleFile, 'utf8')

// 1) modelRows：插入 modelsPage 的 matrix 调用前
const matrixAnchor = '  const matrix = modelsMatrix({ dataDir, accounts, catalog })'
if (!s.includes(matrixAnchor)) { console.error('matrix anchor missing'); process.exit(1) }
s = s.replace(matrixAnchor, modelRows + '\n' + matrixAnchor)

// 2) instancesPage：插入 handleApi 前
const apiAnchor = 'async function handleApi({ req, res, path, dataDir, manifest }) {'
if (!s.includes(apiAnchor)) { console.error('handleApi anchor missing'); process.exit(1) }
s = s.replace(apiAnchor, instances + '\n\n' + apiAnchor)

// 3) pluginsPage：插入 json( 前
const jsonAnchor = 'function json(res, status, value) {'
if (!s.includes(jsonAnchor)) { console.error('json anchor missing'); process.exit(1) }
s = s.replace(jsonAnchor, plugins + '\n\n' + jsonAnchor)

writeFileSync(consoleFile, s)
console.log('all three functions inserted')
