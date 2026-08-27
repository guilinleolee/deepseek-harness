/**
 * HyperFrames Registry - Particle Orbit (椭圆轨道)
 * Particles move in elliptical orbits around center
 * v1.1.0
 */

(function() {
  const COMPONENT_ID = 'particle-orbit';

  const ParticleOrbit = {
    particles: [],
    animFrame: null,
    canvas: null,
    ctx: null,

    defaults: {
      count: 40,
      minRadius: 80,
      maxRadius: 250,
      minSpeed: 0.005,
      maxSpeed: 0.02,
      minSize: 1.5,
      maxSize: 3.5,
      colors: null, // use theme colors
      opacity: 0.7,
      orbitEccentricity: 0.3, // ellipse horizontal stretch
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
        // Random color from theme
        const themeColors = ['--primary', '--secondary', '--accent'];
        const colorName = themeColors[Math.floor(Math.random() * themeColors.length)];
        const color = this._getCssVar(colorName) || 'rgba(99,102,241,0.8)';

        this.particles.push({
          r,
          angle,
          speed: speed * (Math.random() > 0.5 ? 1 : -1),
          size,
          color,
          opacity: opts.opacity * (0.5 + Math.random() * 0.5),
          // ellipse eccentricity per particle
          ecc: 0.2 + Math.random() * opts.orbitEccentricity,
          // vertical oscillation
          yOffset: (Math.random() - 0.5) * 30,
          yFreq: 0.5 + Math.random() * 1.5,
          yAmp: 5 + Math.random() * 15,
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

      const time = performance.now() * 0.001;

      for (const p of this.particles) {
        p.angle += p.speed;

        // Ellipse orbit: x stretched by ecc
        const x = cx + p.r * Math.cos(p.angle) * (1 + p.ecc);
        const y = cy + p.r * Math.sin(p.angle) * 0.8 + p.yOffset + Math.sin(time * p.yFreq + p.angle) * p.yAmp;

        this.ctx.beginPath();
        this.ctx.arc(x, y, p.size, 0, Math.PI * 2);
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

    // Expose for external control
    resize(w, h) {
      if (this.canvas) {
        this.canvas.width = w;
        this.canvas.height = h;
      }
    },
  };

  if (typeof window !== 'undefined') {
    if (!window.__registry) window.__registry = {};
    window.__registry[COMPONENT_ID] = ParticleOrbit;
  }
})();
