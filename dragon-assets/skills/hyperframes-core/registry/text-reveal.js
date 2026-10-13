/**
 * HyperFrames Registry - Text Reveal
 * Reveals text character by character or line by line
 * v1.1.0
 */

(function() {
  const COMPONENT_ID = 'text-reveal';

  const TextReveal = {
    defaults: {
      mode: 'chars', // 'chars' | 'words' | 'lines'
      staggerDelay: 0.05, // seconds per unit
      duration: 0.4, // seconds per unit reveal
      ease: 'power2.out',
      cursor: true,
      cursorChar: '|',
      cursorBlink: 0.6, // seconds
    },

    /**
     * Reveal text in a container element
     * @param {HTMLElement} container
     * @param {object} opts
     * @returns {gsap.core.Timeline}
     */
    reveal(container, opts) {
      opts = Object.assign({}, this.defaults, opts);

      if (!container) return null;

      const text = container.textContent || '';
      container.textContent = '';
      container.style.visibility = 'visible';

      let units = [];

      if (opts.mode === 'chars') {
        units = text.split('').map(ch => {
          const span = document.createElement('span');
          span.className = 'tr-char';
          span.textContent = ch === ' ' ? '\u00A0' : ch;
          span.style.display = 'inline-block';
          span.style.opacity = '0';
          container.appendChild(span);
          return span;
        });
      } else if (opts.mode === 'words') {
        const words = text.split(/\s+/);
        units = words.map(word => {
          const span = document.createElement('span');
          span.className = 'tr-word';
          span.textContent = word;
          span.style.display = 'inline-block';
          span.style.opacity = '0';
          span.style.marginRight = '0.3em';
          container.appendChild(span);
          return span;
        });
      } else if (opts.mode === 'lines') {
        const lines = text.split('\n');
        units = lines.map(line => {
          const div = document.createElement('div');
          div.className = 'tr-line';
          div.textContent = line;
          div.style.opacity = '0';
          div.style.display = 'block';
          container.appendChild(div);
          return div;
        });
      }

      // Create timeline
      const tl = window.gsap ? window.gsap.timeline({ paused: true }) : null;

      if (tl) {
        units.forEach((el, i) => {
          tl.to(el, {
            opacity: 1,
            duration: opts.duration,
            ease: opts.ease,
          }, i * opts.staggerDelay);
        });
      }

      return tl;
    },

    /**
     * Glitch effect on text
     * @param {HTMLElement} el
     */
    glitch(el) {
      if (!el || !window.gsap) return;
      const tl = window.gsap.timeline({ paused: true });
      tl.to(el, {
        skewX: 10,
        duration: 0.05,
        ease: 'none',
        yoyo: true,
        repeat: 3,
      })
      .to(el, {
        skewX: -5,
        duration: 0.03,
        ease: 'none',
        yoyo: true,
        repeat: 2,
      })
      .to(el, { skewX: 0, duration: 0.1 });
      return tl;
    },

    /**
     * Typewriter effect with cursor
     * @param {HTMLElement} el
     * @param {string} text
     * @param {number} cps chars per second
     */
    typewriter(el, text, cps = 30) {
      if (!el || !window.gsap) return;
      el.textContent = '';

      const tl = window.gsap.timeline({ paused: true });
      let displayText = '';

      for (let i = 0; i < text.length; i++) {
        displayText += text[i];
        tl.call(() => { el.textContent = displayText; }, null, i / cps);
      }

      return tl;
    },
  };

  if (typeof window !== 'undefined') {
    if (!window.__registry) window.__registry = {};
    window.__registry[COMPONENT_ID] = TextReveal;
  }
})();
