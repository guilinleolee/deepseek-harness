# Design Extraction Prompt

Extract design specifications from a website URL for creating a DESIGN.md file.

## Input

Website URL: {url}
Design Focus: {focus} (e.g., "payment flow", "landing page", "dashboard")

## Extraction Checklist

### 1. Visual Theme
- Overall aesthetic and mood
- Color temperature (warm/cool/neutral)
- Design language (minimal, playful, enterprise, etc.)
- Brand personality conveyed

### 2. Color Palette
Extract ALL colors found:
- Primary brand color(s)
- Secondary colors
- Accent colors
- Semantic colors (success, warning, error, info)
- Neutral colors (backgrounds, text, borders)
- Dark mode colors (if applicable)

Format: `#RRGGBB` or `rgb(r,g,b)` with semantic labels

### 3. Typography Rules
- Font families (primary, secondary, monospace)
- Font weights used
- Heading hierarchy (h1-h6 sizes)
- Body text size
- Line heights
- Letter spacing

### 4. Component Stylings
Document styles for:
- **Buttons**: padding, border-radius, shadow, states (hover, active, disabled)
- **Inputs**: border, padding, focus states, error states
- **Cards**: shadow, border-radius, padding, background
- **Navigation**: layout, item spacing, active states
- **Forms**: label styles, error messages, validation states

### 5. Layout Principles
- Grid system (columns, gutters, margins)
- Spacing scale (verify actual values)
- Responsive breakpoints
- Container widths

### 6. Depth & Elevation
- Shadow levels (sm, md, lg, etc.)
- Border styles
- Dividers
- Z-index layers

### 7. Motion & Animation
- Transition durations
- Easing functions
- Hover effects
- Loading states
- Micro-interactions

### 8. Do's and Don'ts
Based on observation:
- Design patterns to follow
- Design patterns to avoid

## Output Format

```markdown
# {Company Name} Design System

## Visual Theme
[2-3 sentences describing the overall aesthetic]

## Color Palette
| Token | Value | Usage |
|-------|-------|-------|
| primary | #XXXXXX | Main brand color |
| secondary | #XXXXXX | Secondary elements |
...

## Typography
- Font Family: "Primary Font", fallback
- Headings: {sizes}
- Body: {size}/ {line-height}
- Weights: {list}

## Component Stylings
### Buttons
[Detailed button styles with all states]

### Cards
[Card component specifications]

[Continue for all major components]

## Layout
- Grid: {columns} columns
- Spacing Scale: {values}
- Breakpoints: {values}

## Depth
- Shadows: [list with values]
- Borders: [styles]

## Motion
- Transitions: {duration} {easing}
- Animations: [patterns observed]

## Do's and Don'ts
### Do
- [Positive patterns]

### Don't
- [Patterns to avoid]
```

## Quality Standards

1. **Accuracy**: Verify colors with actual values, not estimates
2. **Completeness**: Cover all visible component types
3. **Actionability**: Include specific CSS values, not vague descriptions
4. **Context**: Note where each pattern is used in the UI
5. **Edge Cases**: Document hover/focus/disabled/loading states
