# Blueprint design systemu - Skills Folio

> Wygenerowane ze stanu JSON przez ds-architect. Nie edytuj ręcznie - zmiana zostanie wykryta i generowanie się zatrzyma.

Themes: light, dark

## Principles

- WCAG 2.2 AA as the target; automated checks are evidence, not certification
- Controls at least 44px high; focus ring 2px border.focus with 2px offset
- Never use color alone to show state
- Respect prefers-reduced-motion
- Light and dark mode follow the system setting
- Only tokens in components: no raw colors, sizes or off-scale spacing
- Emphasis through color (text.default over text.subtle), not font weight; only Poppins 400 is loaded
- Primary button is out of the prototype: white on action-primary is 4.0:1, below 4.5:1 for 14px text

## Tokeny

| ID | Type | Tier | Value | Status | Description |
|---|---|---|---|---|---|
| color.white | color | primitive | oklch(1 0 0) | approved |  |
| color.red.700 | color | primitive | oklch(0.505 0.213 27.518) | approved |  |
| color.red.400 | color | primitive | oklch(0.704 0.191 22.216) | approved |  |
| color.orange.950 | color | primitive | oklch(0.266 0.079 36.259) | approved |  |
| color.orange.700 | color | primitive | oklch(0.553 0.195 38.402) | approved |  |
| color.orange.400 | color | primitive | oklch(0.75 0.183 55.934) | approved |  |
| color.orange.200 | color | primitive | oklch(0.901 0.076 70.697) | approved |  |
| color.mist.950 | color | primitive | oklch(0.148 0.004 228.8) | approved |  |
| color.mist.900 | color | primitive | oklch(0.218 0.008 223.9) | approved |  |
| color.mist.800 | color | primitive | oklch(0.275 0.011 216.9) | approved |  |
| color.mist.700 | color | primitive | oklch(0.378 0.015 216) | approved |  |
| color.mist.600 | color | primitive | oklch(0.45 0.017 213.2) | approved |  |
| color.mist.50 | color | primitive | oklch(0.987 0.002 197.1) | approved |  |
| color.mist.300 | color | primitive | oklch(0.872 0.007 219.6) | approved |  |
| color.mist.200 | color | primitive | oklch(0.925 0.005 214.3) | approved |  |
| color.mist.100 | color | primitive | oklch(0.963 0.002 197.1) | approved |  |
| color.green.700 | color | primitive | oklch(0.527 0.154 150.069) | approved |  |
| color.green.400 | color | primitive | oklch(0.792 0.209 151.711) | approved |  |
| color.blue.950 | color | primitive | oklch(0.282 0.091 267.935) | approved |  |
| color.blue.700 | color | primitive | oklch(0.488 0.243 264.376) | approved |  |
| color.blue.400 | color | primitive | oklch(0.707 0.165 254.624) | approved |  |
| color.blue.200 | color | primitive | oklch(0.882 0.059 254.128) | approved |  |
| color.azure-radiance.700 | color | primitive | oklch(0.55 0.179 257) | approved |  |
| color.azure-radiance.300 | color | primitive | oklch(0.85 0.087 234) | approved |  |
| color.surface.canvas | color | semantic | light: {color.mist.50}; dark: {color.mist.950} | approved | Page background |
| color.surface.default | color | semantic | light: {color.white}; dark: {color.mist.900} | approved | Cards, code blocks and other raised surfaces |
| color.surface.subtle | color | semantic | light: {color.mist.100}; dark: {color.mist.800} | approved | Inline code, callouts and quiet fills |
| color.surface.hovered | color | semantic | light: {color.mist.100}; dark: {color.mist.800} | approved | Hover fill of link cards and disclosures |
| color.text.default | color | semantic | light: {color.mist.950}; dark: {color.white} | approved | Body text and headings |
| color.text.subtle | color | semantic | light: {color.mist.600}; dark: {color.mist.300} | approved | Secondary text, leads and quiet links |
| color.border.default | color | semantic | light: color-mix(in srgb, oklch(0.148 0.004 228.8) 20%, transparent); dark: color-mix(in srgb, oklch(0.987 0.002 197.1) 25%, transparent) | approved | Stronger dividers, dashed callout outline, open disclosure |
| color.border.subtle | color | semantic | light: color-mix(in srgb, oklch(0.148 0.004 228.8) 7%, transparent); dark: color-mix(in srgb, oklch(0.987 0.002 197.1) 12%, transparent) | approved | Card and table outlines, dividers |
| color.border.focus | color | semantic | light: {color.azure-radiance.700}; dark: {color.azure-radiance.300} | approved | Focus ring |
| color.action.secondary.background | color | semantic | light: {color.mist.50}; dark: {color.mist.900} | approved | Secondary button fill |
| color.action.secondary.hovered | color | semantic | light: {color.mist.100}; dark: {color.mist.800} | approved | Secondary button hover |
| color.action.secondary.pressed | color | semantic | light: {color.mist.200}; dark: {color.mist.950} | approved | Secondary button pressed |
| color.action.secondary.border | color | semantic | light: {color.mist.200}; dark: {color.mist.700} | approved | Secondary button outline |
| color.action.secondary.text | color | semantic | light: {color.mist.950}; dark: {color.white} | approved | Secondary button label |
| color.success.border | color | semantic | light: {color.green.400}; dark: {color.green.700} | approved | Accent edge for positive cards |
| color.danger.border | color | semantic | light: {color.red.400}; dark: {color.red.700} | approved | Accent edge for cautionary cards |
| color.actor.skill.background | color | semantic | light: {color.blue.200}; dark: {color.blue.950} | approved | Stages and badges for steps the skill performs (background). Same values as design.md info-background, without its status meaning. |
| color.actor.skill.border | color | semantic | light: {color.blue.400}; dark: {color.blue.700} | approved | Stages and badges for steps the skill performs (border). Same values as design.md info-border, without its status meaning. |
| color.actor.skill.text | color | semantic | light: {color.blue.950}; dark: {color.blue.200} | approved | Stages and badges for steps the skill performs (text). Same values as design.md info-text, without its status meaning. |
| color.actor.you.background | color | semantic | light: {color.orange.200}; dark: {color.orange.950} | approved | Stages and badges for steps the user performs (background). Same values as design.md warning-background, without its status meaning. |
| color.actor.you.border | color | semantic | light: {color.orange.400}; dark: {color.orange.700} | approved | Stages and badges for steps the user performs (border). Same values as design.md warning-border, without its status meaning. |
| color.actor.you.text | color | semantic | light: {color.orange.950}; dark: {color.orange.200} | approved | Stages and badges for steps the user performs (text). Same values as design.md warning-text, without its status meaning. |
| radius.2 | dimension | primitive | 2px | approved |  |
| radius.6 | dimension | primitive | 6px | approved |  |
| radius.12 | dimension | primitive | 12px | approved |  |
| radius.16 | dimension | primitive | 16px | approved |  |
| space.2 | dimension | primitive | 2px | approved |  |
| space.4 | dimension | primitive | 4px | approved |  |
| space.6 | dimension | primitive | 6px | approved |  |
| space.8 | dimension | primitive | 8px | approved |  |
| space.12 | dimension | primitive | 12px | approved |  |
| space.16 | dimension | primitive | 16px | approved |  |
| space.20 | dimension | primitive | 20px | approved |  |
| space.24 | dimension | primitive | 24px | approved |  |
| space.28 | dimension | primitive | 28px | approved |  |
| space.32 | dimension | primitive | 32px | approved |  |
| space.36 | dimension | primitive | 36px | approved |  |
| space.40 | dimension | primitive | 40px | approved |  |
| space.44 | dimension | primitive | 44px | approved |  |
| space.48 | dimension | primitive | 48px | approved |  |
| space.56 | dimension | primitive | 64px | approved |  |
| space.80 | dimension | primitive | 80px | approved |  |
| space.96 | dimension | primitive | 96px | approved |  |
| space.112 | dimension | primitive | 112px | approved |  |
| space.128 | dimension | primitive | 128px | approved |  |
| space.144 | dimension | primitive | 144px | approved |  |
| space.160 | dimension | primitive | 160px | approved |  |
| space.192 | dimension | primitive | 192px | approved |  |
| space.256 | dimension | primitive | 256px | approved |  |
| space.320 | dimension | primitive | 320px | approved |  |
| size.control.md | dimension | semantic | {space.44} | approved | Button height and minimum touch target |
| size.icon.sm | dimension | semantic | {space.16} | approved | Inline icons: arrows, chevrons |
| border.width.default | dimension | primitive | 1px | approved |  |
| border.width.strong | dimension | primitive | 2px | approved | Focus ring and card accent edge (replaces the off-scale 3px) |
| font.family.display | fontFamily | primitive | ["Mona Sans Variable","Mona Sans","sans-serif"] | approved | Self-hosted via @fontsource-variable/mona-sans (OFL) |
| font.family.body | fontFamily | primitive | ["Poppins","sans-serif"] | approved | Self-hosted via @fontsource/poppins (OFL), weight 400 only |
| font.family.code | fontFamily | primitive | ["ui-monospace","SF Mono","Menlo","monospace"] | approved | System monospace; not defined in design.md yet |
| space.inset.card | dimension | semantic | {space.32} | approved | Card padding (design.md) |
| space.stack.card | dimension | semantic | {space.32} | approved | Gap between card children (design.md) |

## Style tekstu

| ID | Family | Weight | Size | Line height | Letter spacing | Status |
|---|---|---|---|---|---|---|
| display-large | {font.family.display} | 500 | 64px | 1 | -0.05em | approved |
| display-small | {font.family.display} | 500 | 44px | 1 | -0.05em | approved |
| heading-large | {font.family.body} | 400 | 28px | 1.1 | -0.01em | approved |
| heading-medium | {font.family.body} | 400 | 24px | 1.2 | -0.005em | approved |
| heading-small | {font.family.body} | 400 | 18px | 1.3 | 0em | approved |
| text-large | {font.family.body} | 400 | 18px | 1.5 | 0em | approved |
| text-medium | {font.family.body} | 400 | 14px | 1.5 | 0em | approved |
| text-small | {font.family.body} | 400 | 12px | 1.333 | 0em | approved |
| label | {font.family.body} | 400 | 14px | 1.5 | 0em | approved |
| code | {font.family.code} | 400 | 13px | 1.5 | 0em | approved |

## Komponenty

### Icon (`icon`)

- Status: proposed · tier: primitive · priority: P1
- Purpose: Decorative SVG icons drawn with currentColor
- Variants: name = arrow-right / chevron-down / loop
- States: default
- Accessibility: aria-hidden by default; never the only carrier of meaning
- Evidence: screen:tailor-my-cv
- QA: figma n/a · code pending · parity n/a

### Inline code (`inline-code`)

- Status: proposed · tier: primitive · priority: P1
- Purpose: Short code, paths and commands inside text
- States: default
- Slots: default
- Accessibility: Plain code element, no extra semantics
- Evidence: screen:skill-detail, screen:tailor-my-cv
- QA: figma n/a · code pending · parity n/a

### Text link (`link`)

- Status: proposed · tier: primitive · priority: P1
- Purpose: Navigation to another page or site
- Variants: tone = default / subtle
- States: default, hover, focus-visible
- Slots: default
- Accessibility: Visible focus ring; Link text names the destination
- Evidence: screen:catalog, screen:skill-detail, screen:tailor-my-cv
- QA: figma n/a · code pending · parity n/a

### Badge (`badge`)

- Status: proposed · tier: primitive · priority: P1
- Purpose: Short status or actor label
- Variants: tone = skill / you
- States: default
- Slots: default
- Accessibility: Text label always present; color is never the only signal
- Evidence: screen:tailor-my-cv
- QA: figma n/a · code pending · parity n/a

### Button (`button`)

- Status: proposed · tier: primitive · priority: P0
- Purpose: Trigger an action on the page
- Variants: appearance = secondary
- States: default, hover, pressed, focus-visible, disabled
- Slots: default
- Accessibility: Native button element; Height at least 44px; Result announced through aria-live
- Evidence: screen:skill-detail, screen:tailor-my-cv
- QA: figma n/a · code pending · parity n/a

### Card (`card`)

- Status: proposed · tier: composite · priority: P0
- Purpose: Static block grouping related content
- Variants: accent = none / success / warning / danger
- States: default
- Slots: default
- Accessibility: Accent edge is decoration; the title carries the meaning
- Evidence: screen:tailor-my-cv
- QA: figma n/a · code pending · parity n/a

### Link card (`link-card`)

- Status: proposed · tier: composite · priority: P0
- Purpose: A card that opens another page
- States: default, hover, focus-visible
- Accessibility: One link per card; title is the accessible name; Visible focus ring
- Evidence: screen:catalog
- QA: figma n/a · code pending · parity n/a

### Copy command (`copy-command`)

- Status: proposed · tier: composite · priority: P0
- Purpose: Show a command and copy it in one click
- States: default, copied, copy failed
- Accessibility: Result announced through aria-live
- Depends on: button, inline-code
- Evidence: screen:skill-detail, screen:tailor-my-cv
- QA: figma n/a · code pending · parity n/a

### Callout (`callout`)

- Status: proposed · tier: composite · priority: P2
- Purpose: Draw attention to a side note or an example
- Variants: appearance = note / example
- States: default
- Slots: default, icon
- Accessibility: Not a live region; plain paragraph semantics
- Depends on: icon
- Evidence: screen:tailor-my-cv
- QA: figma n/a · code pending · parity n/a

### Disclosure (`disclosure`)

- Status: proposed · tier: composite · priority: P1
- Purpose: Expandable section with a summary line
- States: closed, open, hover, focus-visible
- Slots: default
- Accessibility: Keyboard: Enter and Space toggle; Chevron is decorative
- Depends on: badge, icon
- Evidence: screen:tailor-my-cv
- QA: figma n/a · code pending · parity n/a

### Page header (`page-header`)

- Status: proposed · tier: pattern · priority: P1
- Purpose: Title and lead at the top of a page
- Variants: size = large / small
- States: default
- Slots: default
- Accessibility: Contains the page's only h1
- Depends on: link
- Evidence: screen:catalog, screen:skill-detail, screen:tailor-my-cv
- QA: figma n/a · code pending · parity n/a

### Section header (`section-header`)

- Status: proposed · tier: pattern · priority: P2
- Purpose: Heading and optional subtitle for a page section
- States: default
- Accessibility: Renders h2; the section is labelled by it
- Evidence: screen:skill-detail, screen:tailor-my-cv
- QA: figma n/a · code pending · parity n/a

## Wyjątki

_brak_
