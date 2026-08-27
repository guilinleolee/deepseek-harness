/**
 * HyperFrames Registry - Entry Point
 * Auto-discovers and registers all component files
 * v1.1.0
 */

(function () {
  'use strict';

  const Registry = {
    version: '1.1.0',
    components: {},

    /**
     * Initialize registry and load all components
     * @param {object} opts
     * @param {string[]} opts.paths - Array of component file paths to load
     * @param {boolean} opts.autoDiscover - Auto-discover components via data-component attributes
     * @param {HTMLElement} opts.root - Root element for auto-discovery (default: document.body)
     */
    init(opts) {
      opts = Object.assign({
        paths: [],
        autoDiscover: false,
        root: document.body,
      }, opts);

      // Ensure __registry exists
      if (typeof window !== 'undefined') {
        if (!window.__registry) window.__registry = {};
        if (!window.__timelines) window.__timelines = {};
        if (!window.__sceneConfigs) window.__sceneConfigs = {};
      }

      // Load specified component paths
      if (opts.paths && opts.paths.length) {
        opts.paths.forEach(path => this._loadScript(path));
      }

      // Auto-discover canvas elements with data-component attribute
      if (opts.autoDiscover && document.readyState !== 'loading') {
        this._autoDiscover();
      } else if (opts.autoDiscover) {
        document.addEventListener('DOMContentLoaded', () => this._autoDiscover());
      }

      return this;
    },

    /**
     * Get a component by name
     * @param {string} name
     * @returns {object|null}
     */
    get(name) {
      if (window.__registry && window.__registry[name]) {
        return window.__registry[name];
      }
      // Try legacy window globals
      const legacyMap = {
        'particle-orbit': 'ParticleOrbit',
        'particle-bloom': 'ParticleBloom',
        'particle-spiral': 'ParticleSpiral',
        'text-reveal': 'TextReveal',
        'text-split': 'TextSplit',
        'chart-bar': 'ChartBar',
        'chart-line': 'ChartLine',
      };
      if (legacyMap[name] && window[legacyMap[name]]) {
        return window[legacyMap[name]];
      }
      return null;
    },

    /**
     * Mount a component onto a canvas element
     * @param {HTMLElement} canvas - Canvas or container element
     * @param {string} componentName - Component name
     * @param {...any} args - Additional arguments passed to component mount()
     * @returns {object|null} - GSAP timeline if available
     */
    mount(canvas, componentName, ...args) {
      const component = this.get(componentName);
      if (!component) {
        console.warn(`[Registry] Component "${componentName}" not found.`);
        return null;
      }

      if (typeof component.mount === 'function') {
        component.mount(canvas, ...args);
      }

      // Return animation timeline if available
      if (typeof component.getAnim === 'function') {
        return component.getAnim(canvas);
      }
      return null;
    },

    /**
     * Unmount a component from a canvas element
     * @param {HTMLElement} canvas - Canvas element
     * @param {string} componentName - Component name
     */
    unmount(canvas, componentName) {
      const component = this.get(componentName);
      if (component && typeof component.unmount === 'function') {
        component.unmount(canvas);
      }
    },

    /**
     * List all registered components
     * @returns {string[]}
     */
    list() {
      const names = [];
      if (window.__registry) {
        for (const key in window.__registry) {
          names.push(key);
        }
      }
      return names;
    },

    /**
     * Auto-discover data-component elements and mount them
     * @private
     */
    _autoDiscover() {
      const root = this._opts && this._opts.root ? this._opts.root : document.body;
      const canvases = root.querySelectorAll('[data-component]');
      canvases.forEach(el => {
        const name = el.dataset.component;
        const args = el.dataset.componentArgs ? JSON.parse(el.dataset.componentArgs) : [];
        if (name && !el.__registryMounted) {
          el.__registryMounted = true;
          this.mount(el, name, ...args);
        }
      });
    },

    /**
     * Dynamically load a script file
     * @param {string} path
     * @private
     */
    _loadScript(path) {
      if (typeof document === 'undefined') return;
      const existing = document.querySelector(`script[src="${path}"]`);
      if (existing) return;

      const script = document.createElement('script');
      script.src = path;
      script.async = false;
      document.head.appendChild(script);
    },

    /**
     * Load all registry components from bundled or individual files
     * Call this after DOM is ready to auto-initialize
     */
    bootstrap() {
      const basePath = window.__registryBasePath || './registry/';
      const components = [
        'utils.js',
        'particle-orbit.js',
        'particle-bloom.js',
        'particle-spiral.js',
        'text-reveal.js',
        'text-split.js',
        'chart-bar.js',
        'chart-line.js',
      ];

      components.forEach(file => {
        this._loadScript(basePath + file);
      });

      // Auto-discover after scripts load
      setTimeout(() => this._autoDiscover(), 100);
    },
  };

  // Export
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = Registry;
  } else if (typeof window !== 'undefined') {
    window.__HFRegistry = Registry;
  }
})();
