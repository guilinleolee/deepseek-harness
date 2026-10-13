// palette-rules.mjs · 博主全息 → guizang 主题启发式
// 阶段 19 V2.0 · 10 套覆盖 guizang 全部 10 主题
// 来源：stage 17 V1.0 的 PALETTE_HEURISTICS（5 套）→ 扩展到 10 套

/**
 * PALETTE_HEURISTICS 规则表
 *  - label: 内部标签（描述用）
 *  - theme_or_accent: guizang 主题 key
 *    · Editorial 6 套 → data-theme: ink-classic | indigo-porcelain | forest-ink | kraft-paper | dune | midnight-ink
 *    · Swiss 4 套    → data-accent: ikb | lemon-yellow | lemon-green | safety-orange
 *  - family: 'editorial' | 'swiss' 决定用 data-theme 还是 data-accent
 *  - hexes: 触发该主题的 hex 集合（dim_8.spec.color_palette 与之相交）
 *  - weight: 匹配权重（越高越优先）
 */
export const PALETTE_HEURISTICS = [
  // ───── Editorial 6 套 ─────
  { label: "kraft-classic",   family: "editorial", theme: "kraft-paper",      hexes: ["#2a1e13", "#eedfc7", "#e0d0b6", "#3a2a1d"], weight: 1 },
  { label: "kraft-laoli",    family: "editorial", theme: "kraft-paper",      hexes: ["#2c3e50", "#ecf0f1", "#1a1a1a", "#7f8c8d"], weight: 2 }, // laoli 实际色
  { label: "indigo-classic",  family: "editorial", theme: "indigo-porcelain", hexes: ["#0a1f3d", "#f1f3f5", "#e4e8ec", "#152a4a"], weight: 1 },
  { label: "indigo-extra",    family: "editorial", theme: "indigo-porcelain", hexes: ["#1f3a68", "#f4f6f8"], weight: 1 },
  { label: "forest-classic",  family: "editorial", theme: "forest-ink",       hexes: ["#1a2e1f", "#f5f1e8", "#ece7da", "#253d2c"], weight: 1 },
  { label: "forest-extra",    family: "editorial", theme: "forest-ink",       hexes: ["#2d4a3e", "#f0ece1"], weight: 1 },
  { label: "ink-classic",     family: "editorial", theme: "ink-classic",      hexes: ["#0a0a0b", "#f3f0e8", "#ebe6da", "#68625a"], weight: 1 },
  { label: "dune-classic",    family: "editorial", theme: "dune",             hexes: ["#1f1a14", "#f0e6d2", "#e3d7bf", "#2d2620"], weight: 1 },
  { label: "midnight-classic",family: "editorial", theme: "midnight-ink",     hexes: ["#0e0d0c", "#ece2cf", "#d4a04a", "#1a1714"], weight: 1 },
  { label: "midnight-gold",   family: "editorial", theme: "midnight-ink",     hexes: ["#0a0a0a", "#c8a04a", "#1a1714", "#2a1e13"], weight: 1 },
  // ───── Swiss 4 套（按 accent 色锚） ─────
  { label: "swiss-ikb",       family: "swiss",     theme: "ikb",              hexes: ["#002fa7", "#fafaf8", "#0a0a0a", "#737373"], weight: 1 },
  { label: "swiss-lemon-y",   family: "swiss",     theme: "lemon-yellow",     hexes: ["#ffd500", "#fafaf8", "#0a0a0a", "#737373"], weight: 1 },
  { label: "swiss-lemon-g",   family: "swiss",     theme: "lemon-green",      hexes: ["#c5e803", "#fafaf8", "#0a0a0a", "#737373"], weight: 1 },
  { label: "swiss-orange",    family: "swiss",     theme: "safety-orange",    hexes: ["#ff6b35", "#fafaf8", "#0a0a0a", "#ffffff"], weight: 1 },
];

/**
 * 正常化 hex 字符串（小写 + 去 #）
 */
function normHex(s) {
  return s.trim().toLowerCase().replace(/^#/, "#").padStart(7, "#"); // "#xxxxxx" 形式
}

/**
 * detect_palette_v2: 从博主全息 dim_8.spec.color_palette 推断 guizang theme
 * @param {string[]} colorPalette - 博主全息里的色板（hex 数组）
 * @returns {{ theme: string, family: 'editorial'|'swiss', confidence: number, label: string }}
 */
export function detectPalette(colorPalette) {
  const set = new Set(colorPalette.map(normHex));
  let best = { theme: "ink-classic", family: "editorial", confidence: 0, label: "default-fallback" };

  for (const rule of PALETTE_HEURISTICS) {
    const hexes = new Set(rule.hexes.map(normHex));
    // 计算交集
    let overlap = 0;
    for (const h of set) if (hexes.has(h)) overlap += 1;
    const confidence = overlap * rule.weight;
    if (confidence > best.confidence) {
      best = {
        theme: rule.theme,
        family: rule.family,
        confidence,
        label: rule.label,
      };
    }
  }

  return best;
}

/**
 * applyDesignStyle: 如果博主全息有显式第 9 维 design_style（huashu 40 风格库），
 *   直接覆盖 detectPalette 的推断结果。
 * @param {string|undefined} designStyle - e.g. "editorial" / "kraft-paper" / "midnight-ink" / "swiss-ikb"
 * @returns {{ theme: string, family: 'editorial'|'swiss', source: 'design_style'|'auto' }}
 */
export function applyDesignStyle(designStyle) {
  if (!designStyle) return null;
  const ds = designStyle.toLowerCase().trim();

  // huashu 40 风格库 → guizang 主题映射
  const HUASHU_TO_GUIZANG = {
    // Editorial family
    "editorial":           { theme: "ink-classic",      family: "editorial" },
    "monochrome-minimal":  { theme: "ink-classic",      family: "editorial" },
    "kraft-paper":         { theme: "kraft-paper",      family: "editorial" },
    "kraft":               { theme: "kraft-paper",      family: "editorial" },
    "dune":                { theme: "dune",             family: "editorial" },
    "midnight-ink":        { theme: "midnight-ink",     family: "editorial" },
    "midnight":            { theme: "midnight-ink",     family: "editorial" },
    "indigo-porcelain":    { theme: "indigo-porcelain", family: "editorial" },
    "indigo":              { theme: "indigo-porcelain", family: "editorial" },
    "forest-ink":          { theme: "forest-ink",       family: "editorial" },
    "forest":              { theme: "forest-ink",       family: "editorial" },
    // Swiss family
    "swiss-ikb":           { theme: "ikb",              family: "swiss" },
    "swiss-lemon":         { theme: "lemon-yellow",     family: "swiss" },
    "swiss-lemon-y":       { theme: "lemon-yellow",     family: "swiss" },
    "swiss-lemon-g":       { theme: "lemon-green",      family: "swiss" },
    "swiss-orange":        { theme: "safety-orange",    family: "swiss" },
    "swiss":               { theme: "ikb",              family: "swiss" }, // 默认 Swiss → IKB
  };

  const mapped = HUASHU_TO_GUIZANG[ds];
  if (!mapped) return null;
  return { ...mapped, source: "design_style" };
}

/**
 * 生成 HTML 注入字符串（<html data-theme|data-accent=...>）
 * @param {{ theme: string, family: 'editorial'|'swiss' }} choice
 * @returns {string}  e.g. `data-theme="kraft-paper"` 或 `data-accent="ikb"`
 */
export function themeAttr(choice) {
  return choice.family === "swiss" ? `data-accent="${choice.theme}"` : `data-theme="${choice.theme}"`;
}

/**
 * 选种子模板路径
 */
export function seedTemplatePath(choice, skillRoot) {
  const fname = choice.family === "swiss" ? "template-swiss-card.html" : "template-editorial-card.html";
  return `${skillRoot}/assets/${fname}`;
}