// test-xhs-pipeline.mjs · XHS 8 套模板 × 3 博主 = 24 用例
// 阶段 22 V2.1 · 2026-07-20
//
// 用法: node tests/test-xhs-pipeline.mjs
// 退出码: 0 = 全 PASS, 1 = 有 FAIL

import { recommendFromProfile, selectCoverStyle } from "../pipeline/cover-style-selector.mjs";
import { renderXHSTemplate } from "../pipeline/xhs-template-renderer.mjs";
import { publishXHSToPublisher, writePlaceholderPNG } from "../pipeline/to-xhs-publisher.mjs";
import { readFileSync, existsSync, mkdirSync, rmSync } from "node:fs";
import { resolve, join } from "node:path";

// ── 配置 ────────────────────────────────────────────────────────
const PROFILE_DIR = "C:/Users/li/.claude/ip-profiles";
const BLOGGERS = ["laoli_bro_2026", "outdoor_lily", "tech_vc_bro"];
const XHS_STYLES = [
  "xhs-press-top",
  "xhs-split-impact",
  "xhs-qa-popular",
  "xhs-checklist",
  "xhs-review-rank",
  "xhs-recommend",
  "xhs-collage-intro",
  "xhs-dark-workflow"
];

const PALETTE_OK = (s) => typeof s === "string" && s.includes("#FDFFA7");

// 检测"使用 X 黄色"(正向指令里的禁用色),允许"禁止 X 黄色"(硬约束本身)
const NO_BAD_YELLOW = (s) => {
  if (typeof s !== "string") return true;
  const banned = ["荧光黄", "柠檬黄", "金黄", "偏橙黄"];
  for (const color of banned) {
    // 匹配 "{禁止|不要|避免|不得} {...} 黄色" 视为硬约束,允许
    const constraintRe = new RegExp(`(禁止|不要|避免|不得|不许)([^。\\n]*?)${color}`);
    if (constraintRe.test(s)) continue;

    // 匹配其他地方出现该黄色(可能是 prompt 用错, fail)
    if (s.includes(color)) return false;
  }
  return true;
};

// ── 测试工具 ────────────────────────────────────────────────────
let pass = 0, fail = 0;
const failures = [];

function assert(cond, msg, ctx) {
  if (cond) {
    pass++;
    console.log(`  ✅ ${msg}`);
  } else {
    fail++;
    failures.push({ msg, ctx });
    console.log(`  ❌ ${msg}`);
    if (ctx) console.log(`     ctx: ${ctx}`);
  }
}

// ── 加载 profile ────────────────────────────────────────────────
function loadProfile(id) {
  const p = JSON.parse(readFileSync(resolve(PROFILE_DIR, id, "ip_profile_8dim.json"), "utf-8"));
  // 补 figure_1_url 和 default_title 给测试用
  p.figure_1_url = `https://example.com/${id}/photo_1.jpg`;
  p.default_title = `${p.blogger_name} 默认标题`;
  return p;
}

// ── 测试 1 · recommendFromProfile 决策合理性 ───────────────────
console.log("\n┌─ T1 · 自动推荐（3 博主） ─────────────────────────────");
const EXPECTED = {
  "laoli_bro_2026":  ["xhs-checklist", "xhs-dark-workflow", "xhs-split-impact"],  // 任一命中即可
  "outdoor_lily":    ["xhs-recommend", "xhs-collage-intro"],
  "tech_vc_bro":     ["xhs-review-rank", "xhs-qa-popular", "xhs-dark-workflow"]
};
for (const id of BLOGGERS) {
  const p = loadProfile(id);
  const r = recommendFromProfile(p);
  const expected = EXPECTED[id];
  const ok = expected.includes(r.style);
  assert(ok, `${id} → ${r.style} (期望任一: ${expected.join("|")})`);
}

// ── 测试 2 · 24 用例: 8 风格 × 3 博主 ─────────────────────────
console.log("\n┌─ T2 · 8 风格 × 3 博主 = 24 用例 ──────────────────────");
for (const blogger of BLOGGERS) {
  console.log(`\n  ▸ ${blogger}`);
  const profile = loadProfile(blogger);

  for (const style of XHS_STYLES) {
    const params = {
      style,
      figure_1:        profile.figure_1_url,
      expression:      "thumb-up",
      extra_materials: "0",
      background:      "warm-indoor",
      font_style:      "variety-bold",
      font_color:      "fdffa7-default",
      title:           `${blogger} ${style} 测试标题`
    };

    let result, err;
    try {
      result = await renderXHSTemplate(style, params, profile);
    } catch (e) {
      err = e;
    }

    const tag = `${style}/${blogger.split("_")[0]}`;
    if (err) {
      assert(false, `${tag} 渲染失败: ${err.message.slice(0, 80)}`);
      continue;
    }

    // 必须包含 #FDFFA7
    assert(PALETTE_OK(result.prompt), `${tag} 包含 #FDFFA7`);

    // 不能含禁用黄色措辞
    assert(NO_BAD_YELLOW(result.prompt), `${tag} 不含禁用黄色措辞`);

    // 必须含 3:4
    assert(result.prompt.includes("3:4"), `${tag} 含 3:4 比例`);

    // prompt 长度合理（300-3000 字）
    assert(result.prompt.length >= 300 && result.prompt.length <= 3000,
      `${tag} prompt 长度合理 (${result.prompt.length})`,
      result.prompt.length < 300 ? `过短: ${result.prompt.slice(0, 100)}` : null);

    // meta 字段完整
    assert(result.meta?.style_id === style, `${tag} meta.style_id 正确`);
    assert(result.meta?.palette === "#FDFFA7", `${tag} meta.palette 正确`);
    assert(result.meta?.aspect_ratio === "3:4", `${tag} meta.aspect_ratio 正确`);
  }
}

// ── 测试 3 · selectCoverStyle autoRecommend 端到端 ────────────
console.log("\n┌─ T3 · selectCoverStyle autoRecommend 端到端 ─────────");
for (const id of BLOGGERS) {
  const profile = loadProfile(id);
  let result, err;
  try {
    result = await selectCoverStyle({
      profile,
      autoRecommend: true,
      preAnswers: { figure_1: profile.figure_1_url, title: `${id} 自动推荐测试` }
    });
  } catch (e) {
    err = e;
  }

  if (err) {
    assert(false, `${id} autoRecommend 端到端: ${err.message.slice(0, 80)}`);
  } else {
    assert(!!result.style, `${id} autoRecommend → ${result.style}`);
    assert(PALETTE_OK(result.prompt), `${id} autoRecommend prompt 含 #FDFFA7`);
    assert(NO_BAD_YELLOW(result.prompt), `${id} autoRecommend prompt 无禁用黄色`);
    assert(result.prompt.includes("3:4"), `${id} autoRecommend prompt 含 3:4`);
  }
}

// ── 测试 4 · 边界条件 ─────────────────────────────────────────
console.log("\n┌─ T4 · 边界条件 ─────────────────────────────────────");
{
  // autoRecommend 但缺 profile
  let threw = false;
  try {
    await selectCoverStyle({ autoRecommend: true, preAnswers: {} });
  } catch (e) {
    threw = e.message.includes("profile") || e.message.includes("requires");
  }
  assert(threw, "autoRecommend 缺 profile 应抛错");
}
{
  // autoRecommend 但缺 figure_1
  let threw = false;
  const p = loadProfile("laoli_bro_2026");
  delete p.figure_1_url;
  try {
    await selectCoverStyle({ profile: p, autoRecommend: true, preAnswers: { title: "x" } });
  } catch (e) {
    threw = e.message.includes("figure_1") || e.message.includes("Q2");
  }
  assert(threw, "autoRecommend 缺 figure_1_url 应抛错");
}
{
  // 未知风格
  let threw = false;
  try {
    await renderXHSTemplate("xhs-unknown-style", { title: "x" }, {});
  } catch (e) {
    threw = e.message.includes("未知") || e.message.includes("不存在");
  }
  assert(threw, "未知风格应抛错");
}

// ── 测试 5 · 二级占位符 0 剩余（V2.2） ────────────────────────
console.log("\n┌─ T5 · 二级占位符全替换（V2.2） ───────────────────────");
const SUB_TEST_CASES = [
  { style: "xhs-press-top",     params: { title: "爆款标题", expression: "shock" } },
  { style: "xhs-split-impact",  params: { title: "产品经理三大软技能", expression: "open-explain", title_blocks: ["产品经理", "三大", "软技能"] } },
  { style: "xhs-qa-popular",    params: { title: "什么是 RAG", expression: "chin-puzzled", qa_labels: "beginner" } },
  { style: "xhs-checklist",     params: { title: "从 0 搭建", expression: "point-title", list_topic: "install", position_lrc: "right" } },
  { style: "xhs-review-rank",   params: { title: "5 款产品", expression: "shock", position_3way: "left-bottom", list_topic: "tools" } },
  { style: "xhs-recommend",     params: { title: "5 款工具", expression: "thumb-up", position_vertical: "top" } },
  { style: "xhs-collage-intro", params: { title: "AI 入门", expression: "fist-confident", card_topic: "ai-agents" } },
  { style: "xhs-dark-workflow", params: { title: "效率流", expression: "shock", list_topic: "efficiency" } }
];
for (const c of SUB_TEST_CASES) {
  const r = await renderXHSTemplate(c.style, c.params, {});
  const remaining = (r.prompt.match(/\[[^\]]+\]/g) || []);
  assert(remaining.length === 0, `${c.style} 二级占位符全 0 剩余${remaining.length ? ` (剩: ${remaining.slice(0,3).join(" ")})` : ""}`);
}

// ── 测试 6 · publisher 入表（V2.2） ────────────────────────────
console.log("\n┌─ T6 · publisher 入表（V2.2 to-xhs-publisher.mjs） ────");
const PUB_TMP_DIR = resolve(process.cwd(), "tests/.tmp_pub");
mkdirSync(PUB_TMP_DIR, { recursive: true });

for (const id of BLOGGERS) {
  const profile = loadProfile(id);
  const meta = JSON.parse(readFileSync(resolve(process.cwd(), "output", `${id}-${EXPECTED[id][0]}.meta.json`), "utf-8"));

  let result, err;
  try {
    result = await publishXHSToPublisher({
      prompt: meta.prompt,
      meta,
      profile,
      outputDir: PUB_TMP_DIR,
      dryRun: false,
      runPublisher: true
    });
  } catch (e) {
    err = e;
  }

  if (err) {
    assert(false, `${id} publisher 入表: ${err.message.slice(0, 80)}`);
  } else {
    assert(!!result.tasksPath, `${id} publisher tasksPath 存在`);
    assert(result.published === true, `${id} publisher 入表成功（成功 1/1）`);
    assert(existsSync(result.tasksPath), `${id} tasks-xhs.jsonl 文件存在`);
    // 校验 JSONL 内容
    const content = readFileSync(result.tasksPath, "utf-8");
    const firstLine = JSON.parse(content.trim().split("\n")[0]);
    assert(firstLine.blogger_id === id, `${id} tasks.jsonl 第 1 行 blogger_id 正确`);
    assert(firstLine.platforms?.includes("xiaohongshu"), `${id} tasks.jsonl 含 xiaohongshu 平台`);
  }
}

// 清理临时
try { rmSync(PUB_TMP_DIR, { recursive: true, force: true }); } catch {}

// ── 汇总 ─────────────────────────────────────────────────────
console.log("\n" + "─".repeat(60));
console.log(`PASS: ${pass} · FAIL: ${fail} · TOTAL: ${pass + fail}`);
if (fail > 0) {
  console.log("\n失败用例:");
  for (const f of failures) console.log(`  - ${f.msg}`);
  process.exit(1);
} else {
  console.log("\n✅ 全部通过");
  process.exit(0);
}