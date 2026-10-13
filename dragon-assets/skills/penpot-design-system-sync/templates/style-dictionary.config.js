/**
 * Style Dictionary Configuration for Penpot Design System
 * Transforms design tokens to iOS, Android, and Web platforms.
 */

module.exports = {
  source: ['tokens/**/*.json'],

  // Platform configurations
  platforms: {
    // iOS (Swift)
    ios: {
      transforms: [
        'attribute/cti',
        'name/cti/camel',
        'color/css',
        'size/px',
        'asset/hios'
      ],
      buildPath: 'ios/DesignTokens/',
      options: {
        showFileHeader: true,
        outputReferences: true
      },
      files: [{
        destination: 'DesignTokens.swift',
        format: 'ios/swift/class',
        className: 'DesignTokens',
        packageName: 'DesignTokens',
        filter: {
          attributes: {
            category: 'color'
          }
        }
      }, {
        destination: 'TypographyTokens.swift',
        format: 'ios/swift/class',
        className: 'TypographyTokens',
        packageName: 'TypographyTokens',
        filter: {
          attributes: {
            category: 'typography'
          }
        }
      }, {
        destination: 'SpacingTokens.swift',
        format: 'ios/swift/class',
        className: 'SpacingTokens',
        packageName: 'SpacingTokens',
        filter: {
          attributes: {
            category: 'spacing'
          }
        }
      }]
    },

    // Android (XML)
    android: {
      transforms: [
        'attribute/cti',
        'name/cti/snake',
        'color/css',
        'size/dp'
      ],
      buildPath: 'android/src/main/res/values/',
      options: {
        showFileHeader: true,
        outputReferences: true
      },
      files: [{
        destination: 'colors.xml',
        format: 'android/colors',
        filter: {
          attributes: {
            category: 'color'
          }
        }
      }, {
        destination: 'dimens.xml',
        format: 'android/dimens',
        filter: {
          attributes: {
            category: 'spacing'
          }
        }
      }, {
        destination: 'typography.xml',
        format: 'android/resources',
        filter: {
          attributes: {
            category: 'typography'
          }
        }
      }]
    },

    // Web (CSS Custom Properties)
    web: {
      transforms: [
        'attribute/cti',
        'name/cti/kebab',
        'color/css',
        'size/px'
      ],
      buildPath: 'web/tokens/',
      options: {
        showFileHeader: true,
        outputReferences: true
      },
      files: [{
        destination: 'tokens.css',
        format: 'css/variables',
        options: {
          outputReferences: true,
          selector: ':root',
          format: 'css/variables'
        }
      }]
    },

    // SCSS
    scss: {
      transforms: [
        'attribute/cti',
        'name/cti/kebab',
        'color/css',
        'size/px'
      ],
      buildPath: 'scss/tokens/',
      options: {
        showFileHeader: true,
        outputReferences: true
      },
      files: [{
        destination: '_tokens.scss',
        format: 'scss/variables',
        options: {
          outputReferences: true
        }
      }]
    },

    // Tailwind CSS
    tailwind: {
      transforms: [
        'attribute/cti',
        'name/cti/kebab',
        'color/css',
        'size/px'
      ],
      buildPath: 'tailwind/',
      options: {
        showFileHeader: true
      },
      files: [{
        destination: 'tokens.config.js',
        format: 'javascript/module',
        options: {
          outputFormat: 'ES6'
        }
      }]
    },

    // Figma Tokens (JSON)
    figmatokens: {
      transformGroup: 'figma',
      buildPath: 'figma/',
      files: [{
        destination: 'tokens.json',
        format: 'json/flat',
        options: {
          outputReferences: true
        }
      }]
    },

    // Style Dictionary JSON (for tooling)
    json: {
      buildPath: 'json/',
      files: [{
        destination: 'tokens.json',
        format: 'json/flat',
        options: {
          outputReferences: true
        }
      }]
    }
  }
};

/*
 * Custom Transforms (add to transforms/ directory):
 *
 * transforms/penpotColor.js
 * transforms/penpotTypography.js
 * transforms/penpotSpacing.js
 */

/*
 * Usage:
 *
 * # Generate all platforms
 * style-dictionary build
 *
 * # Generate specific platform
 * style-dictionary build --config config.js --platform ios
 *
 * # Build with custom tokens
 * style-dictionary build --config config.js --source 'custom/**/*.json'
 */
