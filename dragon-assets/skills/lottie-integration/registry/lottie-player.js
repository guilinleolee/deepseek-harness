/**
 * LottiePlayer - Hyperframes Registry Atom Component
 *
 * lottie-web integration for AE animation playback.
 * Provides GSAP-compatible timeline interface for seamless hyperframes orchestration.
 *
 * @see ../prompts/web-embed-guide.md
 * @see ../prompts/ae-export-guide.md
 */
(function () {
  'use strict';

  class LottiePlayer {
    static id = 'lottie-player';
    static category = 'media';
    static integrationCost = 'zero';
    static requiresCanvas = false;

    constructor() {
      this.anim = null;
      this.container = null;
      this.opts = {};
      this._loaded = false;
      this._readyCallbacks = [];
    }

    /**
     * Mount lottie animation to container.
     *
     * @param {HTMLElement} container - DOM element to mount into
     * @param {Object} opts - Configuration options
     * @param {string} [opts.renderer='svg'] - Renderer: 'svg' | 'canvas' | 'html'
     * @param {boolean} [opts.loop=false] - Loop playback
     * @param {boolean} [opts.autoplay=false] - Auto-start playback
     * @param {string|null} [opts.path=null] - Path to .json file (or .lottie for dotlottie)
     * @param {Object|null} [opts.data=null] - Inline animation data (preferred for CORS)
     * @param {number} [opts.speed=1] - Playback speed multiplier
     * @returns {Promise<this>}
     */
    mount(container, opts = {}) {
      this.container = container;
      this.opts = Object.assign(
        {
          renderer: 'svg',
          loop: false,
          autoplay: false,
          path: null,
          data: null,
          speed: 1,
        },
        opts
      );

      // Ensure lottie-web is loaded
      if (typeof window.lottie === 'undefined') {
        console.error(
          '[LottiePlayer] lottie-web not found. Include: ' +
            'https://cdn.jsdelivr.net/npm/lottie-web@5.12.2/build/player/lottie.min.js'
        );
        return Promise.reject(
          new Error('lottie-web not loaded. Add the CDN script tag.')
        );
      }

      // Validate configuration
      if (!this.opts.path && !this.opts.data) {
        return Promise.reject(
          new Error('[LottiePlayer] Must provide opts.path or opts.data')
        );
      }

      // Destroy existing instance
      if (this.anim) {
        this.anim.destroy();
        this.anim = null;
      }

      // Load animation
      return new Promise((resolve, reject) => {
        try {
          this.anim = window.lottie.loadAnimation({
            container: container,
            renderer: this.opts.renderer,
            loop: this.opts.loop,
            autoplay: this.opts.autoplay,
            path: this.opts.path,
            animationData: this.opts.data,
          });

          // Apply speed
          if (this.opts.speed !== 1) {
            this.anim.setSpeed(this.opts.speed);
          }

          // Wait for DOM loaded before resolving
          this.anim.addEventListener('DOMLoaded', () => {
            this._loaded = true;
            this._readyCallbacks.forEach((cb) => cb(this.anim));
            this._readyCallbacks = [];
            resolve(this);
          });

          // Error handling
          this.anim.addEventListener('error', (e) => {
            console.error('[LottiePlayer] Animation error:', e);
            reject(new Error(`[LottiePlayer] Animation failed to load: ${this.opts.path}`));
          });
        } catch (err) {
          reject(err);
        }
      });
    }

    /**
     * Wait for animation to be ready.
     *
     * @param {Function} callback
     */
    onReady(callback) {
      if (this._loaded && this.anim) {
        callback(this.anim);
      } else {
        this._readyCallbacks.push(callback);
      }
    }

    /**
     * Get GSAP-compatible timeline interface.
     * Use this for integration with hyperframes GSAP timelines.
     *
     * @returns {Object} GSAP-compatible timeline
     */
    getAnim() {
      const self = this;
      return {
        // Playback controls
        play() {
          if (self.anim) self.anim.play();
        },
        pause() {
          if (self.anim) self.anim.pause();
        },
        stop() {
          if (self.anim) self.anim.stop();
        },
        destroy() {
          if (self.anim) self.anim.destroy();
          self.anim = null;
        },

        // Speed and direction
        setSpeed(speed) {
          if (self.anim) self.anim.setSpeed(speed);
        },
        setDirection(dir) {
          if (self.anim) self.anim.setDirection(dir);
        },

        // Frame seeking
        // @param {number} value - Frame number or time in seconds (if useWebAnimationsTime)
        // @param {boolean} [isFrame=true] - true=frame number, false=seconds
        goToAndPlay(value, isFrame = true) {
          if (self.anim) self.anim.goToAndPlay(value, isFrame);
        },
        goToAndStop(value, isFrame = true) {
          if (self.anim) self.anim.goToAndStop(value, isFrame);
        },

        // Time-based seeking (seconds)
        // @param {number} time - Time in seconds
        seek(time) {
          if (self.anim) {
            const frame = time * self.anim.frameRate;
            self.anim.goToAndStop(frame, true);
          }
        },

        // Progress (0-1)
        // @returns {number} Current progress 0-1
        get progress() {
          if (!self.anim) return 0;
          const total = self.anim.totalFrames;
          const current = self.anim.currentFrame;
          return total > 0 ? current / total : 0;
        },

        // Duration in seconds
        // @returns {number}
        get duration() {
          if (!self.anim) return 0;
          return self.anim.totalFrames / self.anim.frameRate;
        },

        // Total frames
        // @returns {number}
        get totalFrames() {
          return self.anim ? self.anim.totalFrames : 0;
        },

        // Current frame
        // @returns {number}
        get currentFrame() {
          return self.anim ? self.anim.currentFrame : 0;
        },

        // Frame rate
        // @returns {number}
        get frameRate() {
          return self.anim ? self.anim.frameRate : 0;
        },

        // Is playing
        // @returns {boolean}
        get isPlaying() {
          return self.anim ? self.anim.isPlaying : false;
        },

        // Events
        on(event, callback) {
          if (self.anim) self.anim.addEventListener(event, callback);
        },
        off(event, callback) {
          if (self.anim) self.anim.removeEventListener(event, callback);
        },

        // Loop segment (loop from frame A to frame B)
        // @param {number} start
        // @param {number} end
        // @param {boolean} [forceFlag=true]
        setSegment(start, end, forceFlag = true) {
          if (self.anim) self.anim.setSegment(start, end, forceFlag);
        },
      };
    }

    /**
     * Unmount and cleanup.
     */
    unmount() {
      if (this.anim) {
        this.anim.destroy();
        this.anim = null;
      }
      this.container = null;
      this.opts = {};
      this._loaded = false;
      this._readyCallbacks = [];
    }
  }

  // ── Registry registration ────────────────────────────────────────────────

  if (typeof window !== 'undefined') {
    // Standard registry
    window.__registry = window.__registry || {};
    window.__registry['lottie-player'] = LottiePlayer;

    // HF Registry bridge (supports both naming conventions)
    if (window.__HFRegistry) {
      window.__HFRegistry.register('lottie-player', LottiePlayer);
    }

    // Expose constructor for direct instantiation
    window.LottiePlayer = LottiePlayer;

    // Auto-discover data-component elements
    window.__HFRegistry =
      window.__HFRegistry ||
      {
        _components: {},
        register(id, cls) {
          this._components[id] = cls;
        },
        init(opts = {}) {
          const autoDiscover = opts.autoDiscover !== false;
          if (!autoDiscover) return;

          // Observe DOM for new elements
          const observer = new MutationObserver(() => {
            document
              .querySelectorAll('[data-component="lottie-player"]')
              .forEach((el) => {
                if (el.dataset.componentMounted) return;
                el.dataset.componentMounted = 'true';

                try {
                  const args = el.dataset.componentArgs
                    ? JSON.parse(el.dataset.componentArgs)
                    : {};
                  const player = new LottiePlayer();
                  player.mount(el, args);
                } catch (err) {
                  console.error('[LottiePlayer] Auto-mount error:', err);
                }
              });
          });

          observer.observe(document.body, {
            childList: true,
            subtree: true,
          });

          // Initial scan
          document
            .querySelectorAll('[data-component="lottie-player"]')
            .forEach((el) => {
              if (el.dataset.componentMounted) return;
              el.dataset.componentMounted = 'true';

              const args = el.dataset.componentArgs
                ? JSON.parse(el.dataset.componentArgs)
                : {};
              const player = new LottiePlayer();
              player.mount(el, args);
            });
        },
      };
  }

  // ── Usage examples (for reference) ──────────────────────────────────────
  /*
  // Example 1: Standalone playback
  const container = document.getElementById('lottie-container');
  const player = new LottiePlayer();
  await player.mount(container, {
    renderer: 'svg',
    loop: true,
    autoplay: true,
    path: './animations/logo.json',   // or data: inlineAnimationData
  });

  // Example 2: GSAP Timeline integration
  const anim = player.getAnim();
  const tl = gsap.timeline({ paused: true });
  tl.call(() => anim.play(), null, 0);
  tl.to('.logo', { opacity: 1, scale: 1, duration: 0.5 }, 0.5);
  tl.call(() => anim.pause(), null, 3.0);
  window.__timelines['brand-intro'] = tl;
  tl.play();

  // Example 3: dotLottie with loop and poster
  const dotPlayer = new LottiePlayer();
  await dotPlayer.mount(document.getElementById('dot-container'), {
    path: './animations/logo.lottie',
    loop: true,
    autoplay: true,
    // dotLottie loads from .lottie ZIP (set renderer: 'canvas' for dotLottie)
    renderer: 'canvas',
  });

  // Example 4: Auto-mount via data-component
  // <canvas id="lottie-hero"
  //   data-component="lottie-player"
  //   data-component-args='{"path":"hero.json","loop":false,"autoplay":false}'>
  // </canvas>
  // window.__HFRegistry.init({ autoDiscover: true });

  // Example 5: Event listeners
  const anim = player.getAnim();
  anim.on('complete', () => console.log('Animation complete'));
  anim.on('loopComplete', () => console.log('Loop complete'));
  anim.on('enterFrame', (e) => console.log('Frame:', e.currentTime));

  // Example 6: Control methods
  anim.setSpeed(0.5);      // Half speed
  anim.setDirection(-1);   // Reverse playback
  anim.seek(2.5);          // Jump to 2.5 seconds
  anim.goToAndPlay(30);    // Jump to frame 30 and play
  */
})();
