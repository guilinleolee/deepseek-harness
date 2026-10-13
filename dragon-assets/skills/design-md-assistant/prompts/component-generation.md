# Component Generation Prompt

Generate UI components that match a specific company's design system.

## Input

Company: {company_name}
Design File: {design_file_path}
Component Type: {component_type}
Framework: {framework} (react/vue/html)
Variant: {variant} (optional)

## Generation Guidelines

### 1. Parse Design Tokens
Extract from DESIGN.md:
- Colors (primary, secondary, semantic)
- Typography (font family, sizes, weights)
- Spacing (scale values)
- Border radius
- Shadows
- Transitions

### 2. Component Types Supported

| Type | Description | Key Features |
|------|-------------|--------------|
| button | Interactive button | variants, sizes, states, icons |
| card | Content container | header, body, footer, media |
| input | Form field | label, placeholder, validation, types |
| navigation | Nav bar/menu | links, active state, responsive |
| pricing-table | Pricing comparison | tiers, features, CTAs |
| form | Multi-field form | inputs, labels, validation, submit |
| hero | Landing hero | headline, subhead, CTA, media |
| footer | Page footer | links, copyright, social |
| modal | Dialog overlay | header, body, footer, animations |
| sidebar | Side panel | nav items, collapsible, responsive |

### 3. Code Requirements

#### React (.tsx)
```tsx
import React from 'react';
// Use CSS-in-JS or inline styles
// Include prop types
// Support variants (primary, secondary, outline, ghost)
// Support sizes (sm, md, lg)
// Handle disabled states
```

#### Vue (.vue)
```vue
<template>
  <!-- Semantic HTML -->
</template>
<script setup>
// Use defineProps
// Type-safe with TypeScript
</script>
<style scoped>
/* Scoped styles matching design tokens */
</style>
```

#### HTML + CSS
```html
<!-- Semantic markup -->
<!-- CSS variables for design tokens -->
<!-- BEM naming convention -->
```

### 4. Design Token Mapping

| Design Token | CSS Variable | Usage |
|---------------|-------------|-------|
| primary | `--{company}-primary` | Main actions |
| secondary | `--{company}-secondary` | Secondary actions |
| text | `--{company}-text` | Body text |
| background | `--{company}-background` | Page background |
| border | `--{company}-border` | Borders and dividers |
| radius | `--{company}-radius` | Border radius |
| shadow-sm | `--{company}-shadow-sm` | Small shadows |
| shadow-md | `--{company}-shadow-md` | Medium shadows |

### 5. Component API Design

```tsx
// React Example: Button
interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  onClick?: () => void;
}
```

### 6. State Handling

Document all states:
- **Default**: Normal appearance
- **Hover**: Mouse over (colors, transforms)
- **Active/Pressed**: Clicking (scale, colors)
- **Focus**: Keyboard focus (outline, ring)
- **Disabled**: Non-interactive (opacity, cursor)
- **Loading**: Async state (spinner, disabled)
- **Error**: Validation failure (border, message)
- **Success**: Completed action (colors, icon)

### 7. Accessibility

- Semantic HTML (`<button>`, `<a>`, `<input>`)
- ARIA labels where needed
- Focus visible states
- Color contrast compliance
- Keyboard navigation
- Screen reader text

## Output Structure

### File Naming
```
{component-type}.{tsx|vue|html}
{component-type}-variants.{tsx|vue|html}
{component-type}.module.css (if separate)
```

### Required Sections

1. **Header**: Design token imports
2. **Component Definition**: Main component with props
3. **Sub-components**: Related smaller components
4. **Variant Definitions**: Style objects for variants
5. **Size Definitions**: Style objects for sizes
6. **Usage Example**: Code example showing usage
7. **Accessibility Notes**: A11y implementation details

### Code Quality Standards

1. **Type Safety**: Full TypeScript types
2. **No Magic Numbers**: Use design token variables
3. **Composition**: Small, reusable parts
4. **Documentation**: JSDoc comments
5. **Testing Ready**: Accessible selectors
6. **Responsive**: Mobile-first approach

## Example Output

```tsx
// components/StripeButton.tsx
import React from 'react';
import styles from './StripeButton.module.css';

/**
 * Stripe-styled button component
 * Follows Stripe's design system with subtle shadows and precise spacing
 */
export interface StripeButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
}

export const StripeButton: React.FC<StripeButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  onClick
}) => {
  const classNames = [
    styles.button,
    styles[variant],
    styles[size],
    loading && styles.loading,
    disabled && styles.disabled
  ].filter(Boolean).join(' ');

  return (
    <button
      className={classNames}
      disabled={disabled || loading}
      onClick={onClick}
      aria-busy={loading}
    >
      {loading ? (
        <span className={styles.spinner} aria-label="Loading" />
      ) : (
        children
      )}
    </button>
  );
};
```

## Validation Checklist

- [ ] Colors match DESIGN.md tokens
- [ ] Typography matches font family and sizes
- [ ] Spacing uses design system scale
- [ ] Border radius matches specification
- [ ] Shadows match elevation levels
- [ ] Transitions have correct duration
- [ ] All states implemented (hover, focus, active, disabled)
- [ ] Accessibility requirements met
- [ ] Responsive behavior documented
- [ ] Usage example provided
