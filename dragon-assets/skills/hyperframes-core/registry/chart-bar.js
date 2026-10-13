/**
 * HyperFrames Registry - Chart Bar (柱状图动画)
 * Animated bar chart component
 * v1.1.0
 */

(function() {
  const COMPONENT_ID = 'chart-bar';

  const ChartBar = {
    defaults: {
      barColor: '--primary',
      accentColor: '--accent',
      barRadius: 4,
      gap: 12,
      maxHeight: 200,
      labelFont: '12px -apple-system, sans-serif',
      labelColor: '--text',
      valueFont: 'bold 14px -apple-system, sans-serif',
      valueColor: '--accent',
      animDuration: 0.8,
      stagger: 0.1,
      ease: 'power3.out',
      showValues: true,
      showLabels: true,
    },

    /**
     * Mount and render a bar chart
     * @param {HTMLElement} container
     * @param {Array<{label, value, color?}>} data
     * @param {object} opts
     */
    mount(container, data, opts) {
      if (!container || !data || !data.length) return;

      opts = Object.assign({}, this.defaults, opts);
      container.innerHTML = '';
      container.style.display = 'flex';
      container.style.alignItems = 'flex-end';
      container.style.justifyContent = 'center';
      container.style.gap = `${opts.gap}px`;
      container.style.height = `${opts.maxHeight + 60}px`;

      const maxVal = Math.max(...data.map(d => d.value));

      data.forEach((item, i) => {
        const barWrap = document.createElement('div');
        barWrap.style.display = 'flex';
        barWrap.style.flexDirection = 'column';
        barWrap.style.alignItems = 'center';
        barWrap.style.gap = '6px';

        // Value label
        if (opts.showValues) {
          const valLabel = document.createElement('span');
          valLabel.className = 'bar-value';
          valLabel.textContent = item.value;
          valLabel.style.font = opts.valueFont;
          valLabel.style.color = this._getCssVar(opts.valueColor) || '#06b6d4';
          valLabel.style.opacity = '0';
          barWrap.appendChild(valLabel);
        }

        // Bar
        const bar = document.createElement('div');
        bar.className = `bar-item bar-item-${i}`;
        const barColor = item.color || this._getCssVar(opts.barColor) || '#6366f1';
        const heightPct = (item.value / maxVal) * opts.maxHeight;

        Object.assign(bar.style, {
          width: '40px',
          height: `${heightPct}px`,
          background: `linear-gradient(to top, ${barColor}, ${this._lighten(barColor)})`,
          borderRadius: `${opts.barRadius}px`,
          transformOrigin: 'bottom center',
          transform: 'scaleY(0)',
          transition: 'none',
        });

        bar.dataset.height = heightPct;
        bar.dataset.index = i;

        // Label
        if (opts.showLabels) {
          const label = document.createElement('span');
          label.className = 'bar-label';
          label.textContent = item.label;
          label.style.font = opts.labelFont;
          label.style.color = this._getCssVar(opts.labelColor) || '#f1f5f9';
          label.style.opacity = '0';
          label.style.textAlign = 'center';
          label.style.maxWidth = '50px';
          label.style.overflow = 'hidden';
          label.style.textOverflow = 'ellipsis';
          label.style.whiteSpace = 'nowrap';
          barWrap.appendChild(label);
        }

        barWrap.appendChild(bar);
        container.appendChild(barWrap);
      });
    },

    /**
     * Get animation timeline
     * @param {HTMLElement} container
     * @param {object} opts
     */
    getAnim(container, opts) {
      if (!window.gsap || !container) return null;
      opts = Object.assign({}, this.defaults, opts);

      const bars = container.querySelectorAll('.bar-item');
      const values = container.querySelectorAll('.bar-value');
      const labels = container.querySelectorAll('.bar-label');

      if (!bars.length) return null;

      const tl = window.gsap.timeline({ paused: true });

      // Bars scale in
      tl.to(bars, {
        scaleY: 1,
        duration: opts.animDuration,
        stagger: opts.stagger,
        ease: opts.ease,
      }, 0);

      // Values fade in
      if (values.length) {
        tl.to(values, {
          opacity: 1,
          duration: 0.4,
          stagger: opts.stagger,
          ease: 'power2.out',
        }, opts.animDuration * 0.5);
      }

      // Labels fade in
      if (labels.length) {
        tl.to(labels, {
          opacity: 0.7,
          duration: 0.4,
          stagger: opts.stagger,
          ease: 'power2.out',
        }, opts.animDuration * 0.7);
      }

      return tl;
    },

    _getCssVar(name) {
      try {
        return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
      } catch { return null; }
    },

    _lighten(hex) {
      // Simple lighten by 20%
      try {
        const h = hex.replace('#', '');
        const r = Math.min(255, parseInt(h.substring(0, 2), 16) + 50);
        const g = Math.min(255, parseInt(h.substring(2, 4), 16) + 50);
        const b = Math.min(255, parseInt(h.substring(4, 6), 16) + 50);
        return `rgb(${r},${g},${b})`;
      } catch { return hex; }
    },
  };

  if (typeof window !== 'undefined') {
    if (!window.__registry) window.__registry = {};
    window.__registry[COMPONENT_ID] = ChartBar;
  }
})();
