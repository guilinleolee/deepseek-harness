import { readFileSync, writeFileSync } from 'node:fs'

// 1) ContentWorkbench: independent per-source state; panels degrade
//    separately; error details surface in-panel + console.
const workbenchHead = readFileSync('packages/client/ui-content-studio/src/client/ContentWorkbench.tsx', 'utf8')
console.log('workbench bytes before:', workbenchHead.length)
