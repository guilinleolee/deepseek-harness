// catalog-secondary-placeholders.mjs · 一次性盘点工具
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { homedir } from "node:os";

const tplDir = join(homedir(), ".claude/skills/gpt-image-2-prompt-library/templates/xhs/styles/");
const files = readdirSync(tplDir).filter(f => f.endsWith(".md"));
const placeholderRe = /\[([^\]]+)\]/g;
const secondary = new Map();

for (const f of files) {
  const md = readFileSync(join(tplDir, f), "utf-8");
  const m = md.match(/^```[a-zA-Z]*\n([\s\S]*?)\n```/m);
  if (!m) continue;
  const tpl = m[1];
  let match;
  while ((match = placeholderRe.exec(tpl)) !== null) {
    const key = match[1];
    const isSecondary = key.includes("/") || key.includes("，例如") || key.includes(",例如") || /[1-9]\./.test(key);
    if (isSecondary && !secondary.has(key)) secondary.set(key, []);
    if (isSecondary) secondary.get(key).push(f);
  }
}

console.log("二级占位符(待处理): " + secondary.size);
for (const [k, fs] of [...secondary.entries()]) {
  console.log("  [" + k + "] x" + fs.length + " in " + [...new Set(fs)].join(","));
}