/**
 * HyperFrames Registry - Particle Spiral (向心螺旋)
 * Particles spiral inward toward center
 * v1.1.0
 */

(function() {
  const COMPONENT_ID = 'particle-spiral';

  const ParticleSpiral = {
    particles: [],
    animFrame: null,
    canvas: null,
    ctx: null,

    defaults: {
      count: 50,
      minRadius: 200,
      maxRadius: 400,
      minSpeed: 0.3,
      maxSpeed: 1.2,
      minSize: 1,
      maxSize: 2.5,
      colors: null,
      spiralStrength: 0.015, // how fast particles spiral inward
      angleOffset: 0.1, // angular offset per frame (creates spiral)
    },

    mount(canvas) {
      this.canvas = canvas;
      this.ctx = canvas.getContext('2d');
      this._init();
      this._start();
    },

    unmount() {
      this._stop();
      if (this.ctx && this.canvas) {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
      }
      this.particles = [];
      this.canvas = null;
      this.ctx = null;
    },

    _init() {
      const opts = Object.assign({}, this.defaults);
      this.particles = [];

      for (let i = 0; i < opts.count; i++) {
        const r = opts.minRadius + Math.random() * (opts.maxRadius - opts.minRadius);
        const angle = Math.random() * Math.PI * 2;
        const speed = opts.minSpeed + Math.random() * (opts.maxSpeed - opts.minSpeed);
        const size = opts.minSize + Math.random() * (opts.maxSize - opts.minSize);
        const themeColors = ['--primary', '--secondary', '--accent'];
        const colorName = themeColors[Math.floor(Math.random() * themeColors.length)];
        const color = this._getCssVar(colorName) || 'rgba(99,102,241,0.8)';

        this.particles.push({
          r,
          angle,
          speed,
          size,
          color,
          opacity: 0.4 + Math.random() * 0.5,
          spiral: opts.spiralStrength,
          angleOff: opts.angleOffset * (Math.random() > 0.5 ? 1 : -1),
        });
      }
    },

    _start() {
      const loop = () => {
        this._draw();
        this.animFrame = requestAnimationFrame(loop);
      };
      loop();
    },

    _stop() {
      if (this.animFrame) {
        cancelAnimationFrame(this.animFrame);
        this.animFrame = null;
      }
    },

    _draw() {
      if (!this.ctx || !this.canvas) return;
      const w = this.canvas.width;
      const h = this.canvas.height;
      const cx = w / 2;
      const cy = h / 2;
      const opts = this.defaults;

      this.ctx.clearRect(0, 0, w, h);

      for (const p of this.particles) {
        // Spiral inward
        p.r -= p.speed * p.spiral * 10;
        // Rotate
        p.angle += p.angleOff;
        // Shrink as it gets closer
        const sizeRatio = Math.max(0.2, p.r / opts.maxRadius);

        // Reset if too close to center
        if (p.r < 5) {
          p.r = opts.maxRadius;
          p.angle = Math.random() * Math.PI * 2;
          p.opacity = 0.4 + Math.random() * 0.5;
        }

        const x = cx + p.r * Math.cos(p.angle);
        const y = cy + p.r * Math.sin(p.angle);

        this.ctx.beginPath();
        this.ctx.arc(x, y, p.size * sizeRatio, 0, Math.PI * 2);
        this.ctx.fillStyle = p.color;
        this.ctx.globalAlpha = p.opacity * sizeRatio;
        this.ctx.fill();
      }
      this.ctx.globalAlpha = 1;
    },

    _getCssVar(name) {
      try {
        return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
      } catch { return null; }
    },

    // Add extra particle burst
    inject(count) {
      const opts = this.defaults;
      for (let i = 0; i < (count || 15); i++) {
        const r = opts.minRadius + Math.random() * (opts.maxRadius - opts.minRadius);
        const angle = Math.random() * Math.PI * 2;
        const speed = opts.minSpeed + Math.random() * (opts.maxSpeed - opts.minSpeed);
        const size = opts.minSize + Math.random() * (opts.maxSize - opts.minSize);
        const themeColors = ['--primary', '--secondary', '--accent'];
        const colorName = themeColors[Math.floor(Math.random() * themeColors.length)];
        const color = this._getCssVar(colorName) || 'rgba(99,102,241,0.8)';
        this.particles.push({
          r, angle, speed, size, color,
          opacity: 0.7,
          spiral: opts.spiralStrength,
          angleOff: opts.angleOffset * (Math.random() > 0.5 ? 1 : -1),
        });
      }
    },

    resize(w, h) {
      if (this.canvas) { this.canvas.width = w; this.canvas.height = h; }
    },
  };

  if (typeof window !== 'undefined') {
    if (!window.__registry) window.__registry = {};
    window.__registry[COMPONENT_ID] = ParticleSpiral;
  }
})();
