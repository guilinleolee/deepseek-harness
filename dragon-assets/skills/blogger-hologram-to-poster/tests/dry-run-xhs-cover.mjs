// dry-run-xhs-cover.mjs · XHS 封面端到端 dry-run
// 阶段 22 V2.1 · 2026-07-20
//
// 用法:
//   node tests/dry-run-xhs-cover.mjs --blogger laoli_bro_2026 [--style xhs-checklist] [--design-style xhs_atutun]
//
// 输出:
//   output/<blogger>-<style>.prompt.md
//   output/<blogger>-<style>.meta.json
//
// 退出码:
//   0 = 成功 · 1 = 失败 · 2 = 参数错误

import { selectCoverStyle, recommendFromProfile } from "../pipeline/cover-style-selector.mjs";
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { resolve, join } from "node:path";

const PROFILE_DIR = "C:/Users/li/.claude/ip-profiles";
const OUTPUT_DIR = resolve(process.cwd(), "output");

// ── 参数解析 ────────────────────────────────────────────────────
function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    if (argv[i].startsWith("--")) {
      args[argv[i].slice(2)] = argv[i + 1];
      i++;
    }
  }
  return args;
}

const args = parseArgs(process.argv);
const blogger = args.blogger || "laoli_bro_2026";
const style   = args.style || null;
const designStyle = args["design-style"] || null;
const profilePath = resolve(PROFILE_DIR, blogger, "ip_profile_8dim.json");

if (!existsSync(profilePath)) {
  console.error(`❌ 博主 profile 不存在: ${profilePath}`);
  process.exit(2);
}

// ── 加载 profile ────────────────────────────────────────────────
const profile = JSON.parse(readFileSync(profilePath, "utf-8"));
profile.id = blogger;
profile.figure_1_url = profile.dim_8_ip_visual?.anchor?.image_path
  ? `local://${profile.dim_8_ip_visual.anchor.image_path}`
  : `https://example.com/${blogger}/photo_1.jpg`;
profile.default_title = `${profile.blogger_name} 7 个真实踩坑`;

// design_style 注入（模拟 V3.0 第 9 维）
if (designStyle) profile.design_style = designStyle;

// ── dry-run 选择风格 ───────────────────────────────────────────
let selectedStyle;
if (style) {
  selectedStyle = style;
  console.log(`[DRY-RUN] 手动指定风格: ${style}`);
} else {
  selectedStyle = recommendFromProfile(profile).style;
  console.log(`[DRY-RUN] 自动推荐风格: ${selectedStyle} (design_style=${designStyle || "(无)"})`);
}

// ── 调用 selectCoverStyle 端到端 ───────────────────────────────
const result = await selectCoverStyle({
  profile,
  autoRecommend: true,
  preAnswers: {
    style:    selectedStyle,
    figure_1: profile.figure_1_url,
    title:    profile.default_title
  }
});

// ── 输出文件 ───────────────────────────────────────────────────
mkdirSync(OUTPUT_DIR, { recursive: true });
const baseName = `${blogger}-${selectedStyle}`;
const promptPath = join(OUTPUT_DIR, `${baseName}.prompt.md`);
const metaPath   = join(OUTPUT_DIR, `${baseName}.meta.json`);

const promptDoc = `# XHS 封面 Prompt · dry-run
- blogger: ${blogger}
- style: ${selectedStyle}
- design_style: ${designStyle || "(未指定)"}
- generated_at: ${result.meta.timestamp}

---

${result.prompt}
`;

writeFileSync(promptPath, promptDoc, "utf-8");
writeFileSync(metaPath, JSON.stringify({
  ...result.meta,
  blogger,
  selected_style: selectedStyle,
  pre_answers: result.params,
  prompt_path: promptPath,
  prompt_length: result.prompt.length,
  prompt: result.prompt,  // V2.2 让 meta 直接带 prompt(to-xhs-publisher 可直接读)
  dry_run: true,
  note: "dry-run 模式：不调 gpt-image-2，仅验证 pipeline 端到端"
}, null, 2), "utf-8");

// ── 校验 ──────────────────────────────────────────────────────
const validations = [
  { name: "prompt 非空",          pass: !!result.prompt },
  { name: "含 #FDFFA7",            pass: result.prompt.includes("#FDFFA7") },
  { name: "含 3:4 竖版",           pass: result.prompt.includes("3:4") },
  { name: "meta.style_id 一致",    pass: result.meta.style_id === selectedStyle },
  { name: "ip_consent 字段在",    pass: "ip_consent" in result.meta }
];

console.log("\n[DRY-RUN] 端到端校验:");
let allPass = true;
for (const v of validations) {
  console.log(`  ${v.pass ? "✅" : "❌"} ${v.name}`);
  if (!v.pass) allPass = false;
}

console.log(`\n[DRY-RUN] 输出:`);
console.log(`  - ${promptPath} (${result.prompt.length} chars)`);
console.log(`  - ${metaPath}`);
console.log(`\n[DRY-RUN] prompt 前 200 字:`);
console.log("─".repeat(60));
console.log(result.prompt.slice(0, 200));
console.log("─".repeat(60));

process.exit(allPass ? 0 : 1);