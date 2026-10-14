/**
 * 漂移 plugin-version 比对的纯函数验证（introspect.pluginSpecDrifts）：
 * 本地路径插件的期望存储（`resolve()` 落盘的 `\` 绝对路径）与安装记录
 * （包管理器写入的 `link:` + `/`）是同一路径的两种书写形式，规范化后不得
 * 误报；真实差异仍须报出且 detail 保留两侧原文。
 *
 * 运行：node test/drift-spec-verify.mjs
 */
import { pluginSpecDrifts } from '../introspect.mjs'

let passed = 0
let failed = 0
const check = (name, cond) => {
  if (cond === true) { passed += 1; console.log(`  ok  ${name}`) } else { failed += 1; console.error(`FAIL  ${name}`) }
}

const WANTED = { name: 'kabage-tool-guard', spec: 'D:\\deepseek-harness\\platform\\plugins\\kabage-tool-guard' }
const LINKED = { name: 'kabage-tool-guard', spec: 'link:D:/deepseek-harness/platform/plugins/kabage-tool-guard' }
const BARE = { name: '@weibaohui/dsh-file-share', spec: '@weibaohui/dsh-file-share' }

check('link:+正斜杠安装记录 vs 反斜杠期望路径不误报（实际部署形态）', pluginSpecDrifts([WANTED], [LINKED]).length === 0)
check('规范化与比对方向无关', pluginSpecDrifts(
  [{ name: 'p', spec: 'link:/srv/plugins/p' }],
  [{ name: 'p', spec: '/srv/plugins/p' }],
).length === 0)
check('裸包名期望跳过版本比对（存在性归 compareSets）', pluginSpecDrifts([BARE], [{ name: BARE.name, spec: '1.2.3' }]).length === 0)
const versioned = pluginSpecDrifts(
  [{ name: 'kabage-tool-guard', spec: 'D:\\x\\guard' }],
  [{ name: 'kabage-tool-guard', spec: 'link:D:/x/other' }],
)
check('规范化后仍不同的路径报 plugin-version', versioned.length === 1 && versioned[0].kind === 'plugin-version')
check('detail 保留两侧原始书写形式', versioned[0]?.detail === 'kabage-tool-guard（期望 D:\\x\\guard，实际 link:D:/x/other）')
check('未安装的差异不在此函数职责内（plugin-missing 负责）', pluginSpecDrifts([WANTED], []).length === 0)

console.log(`通过 ${passed}，失败 ${failed}`)
process.exit(failed === 0 ? 0 : 1)
