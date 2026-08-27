/**
 * HyperFrames Registry - Particle Bloom (离心扩散)
 * Particles burst outward from center
 * v1.1.0
 */

(function() {
  const COMPONENT_ID = 'particle-bloom';

  const ParticleBloom = {
    particles: [],
    animFrame: null,
    canvas: null,
    ctx: null,

    defaults: {
      count: 60,
      minSpeed: 0.3,
      maxSpeed: 1.5,
      minSize: 1,
      maxSize: 3,
      colors: null,
      lifespan: 180, // frames
      friction: 0.98,
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
        const angle = Math.random() * Math.PI * 2;
        const speed = opts.minSpeed + Math.random() * (opts.maxSpeed - opts.minSpeed);
        const size = opts.minSize + Math.random() * (opts.maxSize - opts.minSize);
        const themeColors = ['--primary', '--secondary', '--accent'];
        const colorName = themeColors[Math.floor(Math.random() * themeColors.length)];
        const color = this._getCssVar(colorName) || 'rgba(99,102,241,0.8)';

        this.particles.push({
          x: 0, y: 0, // center-relative
          dx: Math.cos(angle) * speed,
          dy: Math.sin(angle) * speed,
          size,
          color,
          opacity: 0.6 + Math.random() * 0.4,
          life: opts.lifespan,
          maxLife: opts.lifespan,
          friction: opts.friction,
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

      this.ctx.clearRect(0, 0, w, h);

      for (const p of this.particles) {
        // Update
        p.x += p.dx;
        p.y += p.dy;
        p.dx *= p.friction;
        p.dy *= p.friction;
        p.life--;

        // Fade out
        const lifeRatio = p.life / p.maxLife;
        p.opacity = lifeRatio * 0.8;

        // Respawn if dead
        if (p.life <= 0) {
          const angle = Math.random() * Math.PI * 2;
          const speed = this.defaults.minSpeed + Math.random() * (this.defaults.maxSpeed - this.defaults.minSpeed);
          p.x = 0; p.y = 0;
          p.dx = Math.cos(angle) * speed;
          p.dy = Math.sin(angle) * speed;
          p.life = p.maxLife;
        }

        const absX = cx + p.x;
        const absY = cy + p.y;

        this.ctx.beginPath();
        this.ctx.arc(absX, absY, p.size * lifeRatio, 0, Math.PI * 2);
        this.ctx.fillStyle = p.color;
        this.ctx.globalAlpha = p.opacity;
        this.ctx.fill();
      }
      this.ctx.globalAlpha = 1;
    },

    _getCssVar(name) {
      try {
        return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
      } catch { return null; }
    },

    burst(count) {
      // Trigger a new burst
      const opts = this.defaults;
      for (let i = 0; i < (count || 20); i++) {
        if (this.particles.length < 200) {
          const angle = Math.random() * Math.PI * 2;
          const speed = opts.minSpeed + Math.random() * (opts.maxSpeed - opts.minSpeed);
          const size = opts.minSize + Math.random() * (opts.maxSize - opts.minSize);
          const themeColors = ['--primary', '--secondary', '--accent'];
          const colorName = themeColors[Math.floor(Math.random() * themeColors.length)];
          const color = this._getCssVar(colorName) || 'rgba(99,102,241,0.8)';
          this.particles.push({
            x: 0, y: 0,
            dx: Math.cos(angle) * speed,
            dy: Math.sin(angle) * speed,
            size,
            color,
            opacity: 0.6 + Math.random() * 0.4,
            life: opts.lifespan,
            maxLife: opts.lifespan,
            friction: opts.friction,
          });
        }
      }
    },

    resize(w, h) {
      if (this.canvas) { this.canvas.width = w; this.canvas.height = h; }
    },
  };

  if (typeof window !== 'undefined') {
    if (!window.__registry) window.__registry = {};
    window.__registry[COMPONENT_ID] = ParticleBloom;
  }
})();
