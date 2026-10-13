---
license: UNKNOWN
name: image-first-website-design
description: IMAGE-FIRST WEBSITE DESIGN TO CODE. When an image or screenshot is provided, generate the image first, then analyze it, then implement. Mandatory image-first rule enforced. Combinatorial variation engine for design exploration.
triggers: ["taste image to code", "SKILL: IMAGE-FIRST WEBSITE DESIGN TO CODE"]
---

# SKILL: IMAGE-FIRST WEBSITE DESIGN TO CODE

> **MANDATORY RULE (Rule #1):** When an image, screenshot, or visual reference is provided — **ALWAYS generate the image first, analyze it, then implement the code.**

## 1. Core Principle

This skill ensures that when you receive a design image, screenshot, reference, or visual mockup, you follow the **IMAGE-FIRST WORKFLOW** before touching any code:

```
RECEIVE IMAGE → GENERATE IMAGE VARIATION → ANALYZE & ANNOTATE → IMPLEMENT CODE
```

This prevents generic, "AI slop" implementations and forces genuinely creative, image-driven development.

## 2. The IMAGE-FIRST WORKFLOW

### Phase 1: Image Generation & Variation

When given a visual reference or design direction, **generate multiple image variations** before writing code. Use the **Combinatorial Variation Engine** (Section 3) to explore the design space.

**Generate images that:**
- Match the provided reference's layout, mood, and color palette
- Explore adjacent variations (different aspect ratios, color shifts, typography changes)
- Use high-quality image generation tools (DALL-E, Midjourney, Stable Diffusion, etc.)

### Phase 2: Analysis & Annotation

Study the generated images and extract:

**Layout Structure:**
- Grid system (columns, gutters, margins)
- Section hierarchy (hero → features → CTA)
- Spatial relationships (padding, gaps, alignment)

**Typography:**
- Font families (display, body, mono)
- Size scale (fluid or fixed)
- Weight distribution
- Letter-spacing patterns

**Color Palette:**
- Background tones (light/dark/accent)
- Text hierarchy (primary/secondary/muted)
- Accent colors (CTAs, highlights)
- Gradient usage (if any)

**Visual Elements:**
- Image treatment (rounded corners, shadows, overlays)
- Icon style (line, solid, duotone)
- Decorative elements (dividers, backgrounds)
- Motion indicators (hover states visible in static)

### Phase 3: Implementation

Translate annotations into production code:

**For Web (HTML/CSS/JS):**
- Use CSS custom properties for the extracted color palette
- Match typography exactly using Google Fonts
- Replicate layout with modern CSS (Grid, Flexbox)
- Add micro-interactions for hover/active states

**For React/Vue/Svelte:**
- Extract reusable components (Button, Card, Navbar)
- Use component libraries matching the style (Tailwind, shadcn/ui, Radix)
- Build variants from the combinatorial exploration

## 3. COMBINATORIAL VARIATION ENGINE

For any given design direction, generate the following variation packs:

### 4-Section Pack (Minimum)
| Variation | Purpose |
|-----------|---------|
| **A: Original** | Exact match to reference |
| **B: Color Shift** | Warm → Cool or vice versa |
| **C: Typography Swap** | Serif display → Sans-serif display |
| **D: Density Change** | Spacious → Compact or vice versa |

### 8-Section Pack (Standard)
Adds 4 more variations:
| Variation | Purpose |
|-----------|---------|
| **E: Dark Mode** | Inverted palette |
| **F: Editorial** | Magazine-style layout |
| **G: Minimal** | Maximum whitespace |
| **H: Brutalist** | Raw, high-contrast |

### 12-Section Pack (Maximum)
Adds 4 more variations:
| Variation | Purpose |
|-----------|---------|
| **I: Glassmorphism** | Blurred glass effects |
| **J: Neon Accent** | Glowing CTAs |
| **K: Organic** | Curved shapes, soft shadows |
| **L: Retro** | Vintage colors, typewriter fonts |

## 4. ANTI-AI-SLOP RULES

These rules prevent generic, template-like outputs:

**ABSOLUTE BANS:**
- ❌ `border-radius: 8px` on everything (only use 0, 4, 12, 24, 9999px)
- ❌ Gradient backgrounds on hero sections (use solid or mesh)
- ❌ "Get Started" / "Learn More" as CTA text
- ❌ Inter font (use Geist, Satoshi, or distinctive alternatives)
- ❌ 3-column equal grids as hero layout
- ❌ Circular avatars as the only image style
- ❌ Generic placeholder images (use realistic, contextual ones)
- ❌ "Elevate your..." / "Seamless..." / "Next-gen..." copywriting
- ❌ Floating card syndrome (all cards at same elevation)
- ❌ Single-tone shadows (use layered, colored shadows)

**REQUIRED PRACTICES:**
- ✅ Every section has intentional spacing rhythm
- ✅ Typography scale has clear hierarchy (at least 3 sizes)
- ✅ Color palette has exactly 1 accent color (max 60% saturation)
- ✅ Images are contextually relevant to the content
- ✅ Micro-interactions on at least 3 interactive elements
- ✅ Layout uses asymmetric balance (not centered-everything)

## 5. RULE REFERENCE (35 Named Rules)

### Layout Rules
1. **No Floating Cards** — Cards must be anchored or have directional shadows
2. **Intentional Whitespace** — Sections breathe with purpose, not uniformity
3. **Asymmetric Balance** — Left-heavy or right-heavy, never perfectly centered
4. **Z-Pattern Reading** — Guide the eye with visual weight placement
5. **Density Mapping** — High-density areas contrast with open areas

### Typography Rules
6. **Scale Discipline** — Minimum 3 distinct sizes, maximum 6
7. **Weight Contrast** — Heavy + Light creates hierarchy, not just size
8. **No Inter** — Every project gets a distinctive typeface
9. **Tracking Intent** — Tight for display, loose for metadata
10. **Line-Height Math** — 1.2 for display, 1.6+ for body

### Color Rules
11. **Single Accent** — One hero color, everything else is neutral
12. **No Neon** — Saturation capped at 70% for accents
13. **Temperature Consistency** — All neutrals in one temperature (warm or cool)
14. **Shadows Match Hue** — Shadow color tints toward the background
15. **Contrast on Purpose** — Dark text on dark bg ONLY for decorative elements

### Interaction Rules
16. **Hover Feedback** — Every clickable element responds
17. **Staggered Reveals** — Lists animate in sequence, not simultaneously
18. **Spring Physics** — `cubic-bezier(0.34, 1.56, 0.64, 1)` for bounce
19. **No Instant Transitions** — Minimum 200ms for any state change
20. **Active States Matter** — Buttons compress, inputs highlight

### Image Rules
21. **No Generic Stock** — Contextually specific imagery
22. **Aspect Ratio Rhythm** — Mix 16:9, 4:3, 1:1, 2:3 deliberately
23. **Treatment Consistency** — All images share a style (all rounded or all sharp)
24. **No Broken Unsplash** — Use picsum.photos or SVG placeholders
25. **Overlay Strategy** — Images underlays or overtext with clear hierarchy

### Component Rules
26. **No Nested Cards** — Card-inside-card is always wrong
27. **Input States** — Default, Focus, Error, Disabled must all be designed
28. **Icon Consistency** — Same stroke width, same style family throughout
29. **Button Hierarchy** — Primary, Secondary, Ghost, Destructive — each distinct
30. **No Bare Inputs** — Labels, helpers, and error states always designed

### Code Rules
31. **CSS Custom Properties** — Extract all design tokens as variables
32. **No Magic Numbers** — Spacing in multiples of 4px or 8px
33. **Mobile-First** — Design mobile first, enhance upward
34. **Reduced Motion** — Respect `prefers-reduced-motion`
35. **GPU-Safe Animations** — Only transform and opacity animate

## 6. THE ANTI-NESTED-BOX RULE

This is the single most important rule for avoiding generic AI output:

> **NEVER nest cards inside containers that have the same background color.**

```
❌ WRONG:  White page → White card → White card (no visual separation)
✅ RIGHT:   White page → White card with SHADOW → Colored accent border
✅ RIGHT:   White page → Gray card → White inner card
✅ RIGHT:   Dark page → Dark card → Lighter inset card
```

The key is **visual separation through value contrast, not just borders.**

## 7. OUTPUT FORMAT

When implementing, always include:

```markdown
### Design Tokens Extracted
- Primary: [hex]
- Secondary: [hex]
- Accent: [hex]
- Font Display: [Google Font name]
- Font Body: [Google Font name]
- Spacing Unit: [value in px]
- Border Radius Scale: [array of values]
- Shadow System: [description]

### Layout Decisions
- Grid: [columns] with [gutter]px gutter
- Max Width: [value]
- Section Rhythm: [py values for each section]

### Component Inventory
| Component | States | Notes |
|-----------|--------|-------|
| Button | default, hover, active, disabled | [behavior description] |
| Card | default, hover | [shadow/shape description] |
| Input | default, focus, error, disabled | [border/color description] |

### Anti-Pattern Checklist
- [ ] No nested cards without value contrast
- [ ] No generic placeholder text
- [ ] No centered-everything layout
- [ ] Typography has weight contrast, not just size contrast
- [ ] Single accent color with restrained saturation
```

## 8. INTEGRATION WITH CODEX

When using this skill with Claude's Codex:

1. **Receive the image** — Acknowledge the visual reference
2. **Generate variations** — Use image generation tools to create 4-8 variations
3. **Annotate** — Extract design tokens using the checklist in Section 7
4. **Plan** — Write SPEC.md before touching code
5. **Implement** — Build component by component, testing each
6. **Review** — Compare output against original image and annotations
7. **Refine** — Iterate until match is pixel-faithful

## 9. WHEN NO IMAGE IS PROVIDED

If the user describes a design verbally (without an image), **YOU MUST generate an image first** before writing code:

```
USER: "Make a landing page for a SaaS product"
↓
YOUR RESPONSE: "I'll generate a few design variations first, then implement..."
↓
[Generate 4-8 image variations using the Combinatorial Variation Engine]
↓
[Analyze and annotate the best variation]
↓
[Implement the code]
```

This is non-negotiable. Verbal descriptions are prompts for image generation, not for code.
