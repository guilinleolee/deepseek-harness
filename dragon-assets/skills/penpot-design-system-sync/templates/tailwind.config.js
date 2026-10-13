/**
 * Tailwind CSS Configuration
 * Extends default theme with Penpot design tokens.
 */

const tokens = require('./tokens/tokens.json');

/**
 * Convert Style Dictionary tokens to Tailwind format.
 */
function convertTokensToTailwind(tokens) {
  const config = {
    colors: {},
    fontFamily: {},
    spacing: {},
    borderRadius: {},
    boxShadow: {},
    fontSize: {},
    lineHeight: {}
  };

  // Process colors
  if (tokens.color) {
    for (const [name, token] of Object.entries(tokens.color)) {
      if (token.$value) {
        config.colors[name] = token.$value;
      }
    }
  }

  // Process typography
  if (tokens.typography) {
    for (const [name, token] of Object.entries(tokens.typography)) {
      if (token.$value) {
        if (token.$value.fontFamily) {
          config.fontFamily[name] = token.$value.fontFamily.$value;
        }
        if (token.$value.fontSize) {
          config.fontSize[name] = token.$value.fontSize.$value;
        }
        if (token.$value.lineHeight) {
          config.lineHeight[name] = token.$value.lineHeight.$value;
        }
      }
    }
  }

  // Process spacing
  if (tokens.spacing) {
    for (const [name, token] of Object.entries(tokens.spacing)) {
      if (token.$value) {
        config.spacing[name] = token.$value;
      }
    }
  }

  // Process border radius
  if (tokens.borderRadius) {
    for (const [name, token] of Object.entries(tokens.borderRadius)) {
      if (token.$value) {
        config.borderRadius[name] = token.$value;
      }
    }
  }

  // Process shadows
  if (tokens.shadow) {
    for (const [name, token] of Object.entries(tokens.shadow)) {
      if (token.$value) {
        config.boxShadow[name] = token.$value;
      }
    }
  }

  return config;
}

/**
 * Generate semantic tokens from primitive tokens.
 */
function generateSemanticTokens(tokens) {
  const semantic = {};

  // Color semantic tokens
  if (tokens.color) {
    const primitives = tokens.color;

    semantic.extend = {
      colors: {
        // Background
        'background': primitives['white']?.$value || '#ffffff',
        'background-subtle': primitives['gray-50']?.$value || '#f9fafb',
        'background-muted': primitives['gray-100']?.$value || '#f3f4f6',

        // Foreground (text)
        'foreground': primitives['gray-900']?.$value || '#111827',
        'foreground-muted': primitives['gray-600']?.$value || '#4b5563',

        // Primary
        'primary': primitives['blue-500']?.$value || '#3b82f6',
        'primary-foreground': primitives['white']?.$value || '#ffffff',
        'primary-hover': primitives['blue-600']?.$value || '#2563eb',
        'primary-active': primitives['blue-700']?.$value || '#1d4ed8',

        // Secondary
        'secondary': primitives['gray-100']?.$value || '#f3f4f6',
        'secondary-foreground': primitives['gray-900']?.$value || '#111827',

        // Accent
        'accent': primitives['amber-400']?.$value || '#fbbf24',
        'accent-foreground': primitives['gray-900']?.$value || '#111827',

        // Destructive
        'destructive': primitives['red-500']?.$value || '#ef4444',
        'destructive-foreground': primitives['white']?.$value || '#ffffff',

        // Border
        'border': primitives['gray-200']?.$value || '#e5e7eb',
        'border-hover': primitives['gray-300']?.$value || '#d1d5db',

        // Ring
        'ring': primitives['blue-500']?.$value || '#3b82f6',
      }
    };
  }

  return semantic;
}

module.exports = {
  // Penpot design tokens
  ...generateSemanticTokens(tokens),

  // Custom theme extension
  theme: {
    extend: {
      // Use tokens from converted JSON
      ...convertTokensToTailwind(tokens),

      // Animation utilities
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
      },

      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
    },
  },

  // Plugins
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
    require('@tailwindcss/aspect-ratio'),
  ],
};

/*
 * Usage:
 *
 * 1. Place this file as tailwind.config.js
 * 2. Ensure tokens.json exists from Style Dictionary build
 * 3. Run: npx tailwindcss -o dist/styles.css --watch
 *
 * Token naming convention (Penpot → Tailwind):
 * - color-primary-500 → colors.primary (use semantic aliases)
 * - spacing-4 → spacing.4
 * - radius-md → borderRadius.md
 * - shadow-sm → boxShadow.sm
 */
