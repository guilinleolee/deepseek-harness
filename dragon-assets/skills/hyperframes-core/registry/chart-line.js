/**
 * HyperFrames Registry - Chart Line (折线图动画)
 * Animated line chart component
 * v1.1.0
 */

(function() {
  const COMPONENT_ID = 'chart-line';

  const ChartLine = {
    defaults: {
      strokeColor: '--primary',
      strokeWidth: 2.5,
      dotRadius: 4,
      dotColor: '--accent',
      fillColor: '--primary',
      fillOpacity: 0.15,
      animDuration: 1.2,
      dotDelay: 0.3,
      ease: 'power2.inOut',
      showDots: true,
      showArea: true,
      showGrid: true,
      gridLines: 4,
      labelFont: '11px -apple-system, sans-serif',
      labelColor: '--text',
    },

    /**
     * Mount a line chart into container
     * @param {HTMLElement} container
     * @param {number[]} data - Y values
     * @param {string[]} labels - X labels
     * @param {object} opts
     */
    mount(container, data, labels, opts) {
      if (!container || !data || !data.length) return;

      opts = Object.assign({}, this.defaults, opts);
      container.innerHTML = '';
      container.style.position = 'relative';
      container.style.width = '100%';
      container.style.height = '100%';

      const W = container.clientWidth || 600;
      const H = container.clientHeight || 300;
      const padTop = 20, padBottom = 40, padLeft = 10, padRight = 10;
      const chartW = W - padLeft - padRight;
      const chartH = H - padTop - padBottom;

      const maxVal = Math.max(...data);
      const minVal = Math.min(...data, 0);
      const range = maxVal - minVal || 1;

      const stepX = chartW / (data.length - 1 || 1);

      // SVG container
      const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.setAttribute('width', W);
      svg.setAttribute('height', H);
      svg.style.position = 'absolute';
      svg.style.top = '0';
      svg.style.left = '0';
      svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
      container.appendChild(svg);

      // Grid lines
      if (opts.showGrid) {
        for (let i = 0; i <= opts.gridLines; i++) {
          const y = padTop + (chartH / opts.gridLines) * i;
          const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
          line.setAttribute('x1', padLeft);
          line.setAttribute('y1', y);
          line.setAttribute('x2', W - padRight);
          line.setAttribute('y2', y);
          line.setAttribute('stroke', 'rgba(255,255,255,0.06)');
          line.setAttribute('stroke-width', '1');
          svg.appendChild(line);
        }
      }

      // Calculate points
      const points = data.map((val, i) => {
        const x = padLeft + i * stepX;
        const y = padTop + chartH - ((val - minVal) / range) * chartH;
        return { x, y };
      });

      // Build path string
      const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');

      // Area fill path
      let areaD = pathD;
      if (opts.showArea) {
        areaD += ` L ${points[points.length - 1].x} ${padTop + chartH} L ${padLeft} ${padTop + chartH} Z`;
      }

      // Area
      if (opts.showArea) {
        const area = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        const fill = this._hexToRgba(this._getCssVar(opts.fillColor) || '#6366f1', opts.fillOpacity);
        area.setAttribute('d', areaD);
        area.setAttribute('fill', fill);
        area.style.opacity = '0';
        area.dataset.type = 'area';
        svg.appendChild(area);
      }

      // Line path
      const linePath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      const stroke = this._getCssVar(opts.strokeColor) || '#6366f1';
      linePath.setAttribute('d', pathD);
      linePath.setAttribute('fill', 'none');
      linePath.setAttribute('stroke', stroke);
      linePath.setAttribute('stroke-width', opts.strokeWidth);
      linePath.setAttribute('stroke-linecap', 'round');
      linePath.setAttribute('stroke-linejoin', 'round');
      const lineLen = linePath.getTotalLength ? linePath.getTotalLength() : 500;
      linePath.style.strokeDasharray = lineLen;
      linePath.style.strokeDashoffset = lineLen;
      linePath.dataset.type = 'line';
      svg.appendChild(linePath);

      // Dots
      if (opts.showDots) {
        const dotColor = this._getCssVar(opts.dotColor) || '#06b6d4';
        points.forEach((p, i) => {
          const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
          circle.setAttribute('cx', p.x);
          circle.setAttribute('cy', p.y);
          circle.setAttribute('r', opts.dotRadius);
          circle.setAttribute('fill', dotColor);
          circle.style.opacity = '0';
          circle.style.transform = `scale(0)`;
          circle.style.transformOrigin = `${p.x}px ${p.y}px`;
          circle.dataset.type = 'dot';
          circle.dataset.delay = opts.dotDelay + i * 0.05;
          svg.appendChild(circle);
        });
      }

      // Labels
      if (labels && labels.length) {
        const labelGroup = document.createElement('div');
        labelGroup.style.position = 'absolute';
        labelGroup.style.bottom = '8px';
        labelGroup.style.left = `${padLeft}px`;
        labelGroup.style.right = `${padRight}px`;
        labelGroup.style.display = 'flex';
        labelGroup.style.justifyContent = 'space-between';
        labelGroup.style.font = opts.labelFont;
        labelGroup.style.color = this._getCssVar(opts.labelColor) || '#f1f5f9';
        labelGroup.style.opacity = '0';
        labelGroup.dataset.type = 'labels';

        labels.forEach(lbl => {
          const span = document.createElement('span');
          span.textContent = lbl;
          labelGroup.appendChild(span);
        });
        container.appendChild(labelGroup);
      }

      // Store state
      container.__hfChart = { svg, points, lineLen, opts };
    },

    /**
     * Get animation timeline
     * @param {HTMLElement} container
     */
    getAnim(container) {
      if (!window.gsap || !container || !container.__hfChart) return null;

      const { svg, lineLen, opts } = container.__hfChart;
      const tl = window.gsap.timeline({ paused: true });

      // Line draw
      const linePath = svg.querySelector('[data-type="line"]');
      if (linePath) {
        tl.to(linePath, {
          strokeDashoffset: 0,
          duration: opts.animDuration,
          ease: opts.ease,
        }, 0);
      }

      // Area fade
      const area = svg.querySelector('[data-type="area"]');
      if (area) {
        tl.to(area, { opacity: 1, duration: opts.animDuration * 0.5, ease: 'power2.out' }, opts.animDuration * 0.5);
      }

      // Dots pop in
      const dots = svg.querySelectorAll('[data-type="dot"]');
      if (dots.length) {
        dots.forEach(dot => {
          const delay = parseFloat(dot.dataset.delay) || 0;
          tl.to(dot, { opacity: 1, scale: 1, duration: 0.3, ease: 'back.out(2)' }, delay);
        });
      }

      // Labels
      const labels = container.querySelector('[data-type="labels"]');
      if (labels) {
        tl.to(labels, { opacity: 0.7, duration: 0.4 }, opts.animDuration * 0.8);
      }

      return tl;
    },

    _getCssVar(name) {
      try {
        return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
      } catch { return null; }
    },

    _hexToRgba(hex, alpha) {
      try {
        const h = hex.replace('#', '');
        const r = parseInt(h.substring(0, 2), 16);
        const g = parseInt(h.substring(2, 4), 16);
        const b = parseInt(h.substring(4, 6), 16);
        return `rgba(${r},${g},${b},${alpha})`;
      } catch { return hex; }
    },
  };

  if (typeof window !== 'undefined') {
    if (!window.__registry) window.__registry = {};
    window.__registry[COMPONENT_ID] = ChartLine;
  }
})();
