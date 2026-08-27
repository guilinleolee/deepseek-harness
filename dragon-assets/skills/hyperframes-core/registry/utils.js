/**
 * HyperFrames Registry - Shared Utilities
 * v1.1.0
 */

const HF = {
  /**
   * Random number in [min, max)
   */
  rand(min, max) {
    return min + Math.random() * (max - min);
  },

  /**
   * Random integer in [min, max]
   */
  randInt(min, max) {
    return Math.floor(this.rand(min, max + 1));
  },

  /**
   * Hex color to rgba
   */
  hexToRgba(hex, alpha = 1) {
    const h = hex.replace('#', '');
    const r = parseInt(h.substring(0, 2), 16);
    const g = parseInt(h.substring(2, 4), 16);
    const b = parseInt(h.substring(4, 6), 16);
    return `rgba(${r},${g},${b},${alpha})`;
  },

  /**
   * Lerp between two values
   */
  lerp(a, b, t) {
    return a + (b - a) * t;
  },

  /**
   * Clamp value to [min, max]
   */
  clamp(val, min, max) {
    return Math.max(min, Math.min(max, val));
  },

  /**
   * Distance between two points
   */
  dist(x1, y1, x2, y2) {
    const dx = x2 - x1;
    const dy = y2 - y1;
    return Math.sqrt(dx * dx + dy * dy);
  },

  /**
   * Easing: ease-out cubic
   */
  easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
  },

  /**
   * Easing: ease-in-out cubic
   */
  easeInOutCubic(t) {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  },

  /**
   * Get CSS variable value
   */
  cssVar(name, fallback = '#6366f1') {
    return getComputedStyle(document.documentElement)
      .getPropertyValue(name).trim() || fallback;
  },

  /**
   * Theme colors extracted from :root
   */
  theme: {
    primary() { return this.cssVar('--primary', '#6366f1'); },
    secondary() { return this.cssVar('--secondary', '#8b5cf6'); },
    accent() { return this.cssVar('--accent', '#06b6d4'); },
    background() { return this.cssVar('--background', '#0f0f23'); },
    text() { return this.cssVar('--text', '#f1f5f9'); },
    particle() { return this.cssVar('--particle', 'rgba(99,102,241,0.8)'); },
  },
};

if (typeof window !== 'undefined') {
  window.__HF = HF;
}
