/**
 * HyperFrames Registry - Text Split
 * Splits text into spans for per-character animation
 * v1.1.0
 */

(function() {
  const COMPONENT_ID = 'text-split';

  const TextSplit = {
    /**
     * Split element text into individual character spans
     * @param {HTMLElement|string} target
     * @param {object} opts
     * @returns {HTMLElement[]} spans
     */
    split(target, opts = {}) {
      const el = typeof target === 'string'
        ? document.querySelector(target)
        : target;

      if (!el) return [];

      const text = el.textContent || '';
      el.innerHTML = '';
      el.style.visibility = 'visible';

      const chars = text.split('').map((ch, i) => {
        const span = document.createElement('span');
        span.className = opts.className || 'ts-char';
        span.textContent = ch === ' ' ? '\u00A0' : ch;
        span.style.display = opts.inline ? 'inline-block' : 'inline-block';
        span.style.overflow = 'hidden';
        span.dataset.index = i;
        el.appendChild(span);
        return span;
      });

      return chars;
    },

    /**
     * Split into word spans
     * @param {HTMLElement|string} target
     * @returns {HTMLElement[]}
     */
    splitWords(target) {
      const el = typeof target === 'string'
        ? document.querySelector(target)
        : target;

      if (!el) return [];

      const words = el.textContent.trim().split(/\s+/);
      el.innerHTML = '';
      el.style.visibility = 'visible';

      return words.map((word, i) => {
        const span = document.createElement('span');
        span.className = 'ts-word';
        span.textContent = word;
        span.style.display = 'inline-block';
        span.style.overflow = 'hidden';
        span.style.marginRight = '0.25em';
        span.dataset.index = i;
        el.appendChild(span);
        return span;
      });
    },

    /**
     * Wave effect: chars animate with staggered delays
     * @param {HTMLElement[]} chars
     * @param {object} opts
     */
    wave(chars, opts = {}) {
      if (!window.gsap || !chars.length) return null;

      opts = Object.assign({
        y: -20,
        duration: 0.5,
        stagger: 0.03,
        ease: 'power3.out',
        delay: 0,
      }, opts);

      const tl = window.gsap.timeline({ paused: true });
      tl.fromTo(chars,
        { y: opts.y, opacity: 0 },
        { y: 0, opacity: 1, duration: opts.duration, stagger: opts.stagger, ease: opts.ease },
        opts.delay
      );
      return tl;
    },

    /**
     * Gradient text reveal (clip-path wipe)
     * @param {HTMLElement[]} chars
     * @param {object} opts
     */
    clipReveal(chars, opts = {}) {
      if (!window.gsap || !chars.length) return null;

      opts = Object.assign({
        duration: 0.6,
        stagger: 0.02,
        ease: 'power2.inOut',
        direction: 'left', // 'left' | 'right' | 'center'
      }, opts);

      const tl = window.gsap.timeline({ paused: true });

      if (opts.direction === 'left') {
        tl.fromTo(chars,
          { clipPath: 'inset(0 100% 0 0)' },
          { clipPath: 'inset(0 0% 0 0)', duration: opts.duration, stagger: opts.stagger, ease: opts.ease }
        );
      } else if (opts.direction === 'right') {
        tl.fromTo(chars,
          { clipPath: 'inset(0 0 0 100%)' },
          { clipPath: 'inset(0 0 0 0%)', duration: opts.duration, stagger: opts.stagger, ease: opts.ease }
        );
      } else {
        // Center expand
        tl.fromTo(chars,
          { clipPath: 'inset(0 50% 0 50%)' },
          { clipPath: 'inset(0 0% 0 0%)', duration: opts.duration, stagger: opts.stagger, ease: opts.ease }
        );
      }

      return tl;
    },

    /**
     * Blur reveal: chars go from blur to sharp
     * @param {HTMLElement[]} chars
     * @param {object} opts
     */
    blurReveal(chars, opts = {}) {
      if (!window.gsap || !chars.length) return null;

      opts = Object.assign({
        blur: 10,
        duration: 0.6,
        stagger: 0.02,
        ease: 'power2.out',
      }, opts);

      const tl = window.gsap.timeline({ paused: true });
      tl.fromTo(chars,
        { filter: `blur(${opts.blur}px)`, opacity: 0 },
        { filter: 'blur(0px)', opacity: 1, duration: opts.duration, stagger: opts.stagger, ease: opts.ease }
      );
      return tl;
    },
  };

  if (typeof window !== 'undefined') {
    if (!window.__registry) window.__registry = {};
    window.__registry[COMPONENT_ID] = TextSplit;
  }
})();
