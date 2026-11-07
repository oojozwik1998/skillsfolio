# Decyzje - Skills Folio

> Wygenerowane ze stanu JSON przez ds-architect. Nie edytuj ręcznie - zmiana zostanie wykryta i generowanie się zatrzyma.

| ID | Stage | Tytuł | Wybór | Uzasadnienie | Dotyczy | Date |
|---|---|---|---|---|---|---|
| D-001 | 0 | Code target, prototype depth, design.md as the source of truth | approved | The site is already in code; design.md holds the approved tokens; prototype covers the three existing screens |  | 2026-11-07 |
| D-002 | 0 | Storybook with @storybook-astro/framework | approved | Official Storybook has no Astro renderer; the community framework 1.15 matches Astro 7, Vitest 5 and TypeScript 6. The first code batch verifies it; fallback is a /design-system page in Astro | storybook | 2026-11-07 |
| D-003 | G0 | Components in src/components/ui, state files public in the repo | approved | Single app, no monorepo; state files contain no private data |  | 2026-11-07 |
| D-004 | G1 | Shortlist: 12 components plus Prose | approved | Card, LinkCard, Button, Copy command, Inline code, Text link, Badge, Disclosure, Icon, Page header, Section header, Callout; Prose stays a style; Process flow excluded; Table decided later |  | 2026-11-07 |
| D-005 | 1 | Card and LinkCard as separate components | alternative | Owner prefers a clear split between a static block and a link, accepting two places for the shared look | component:card | 2026-11-07 |
| D-006 | G2 | Visual direction review skipped | skipped | design.md stays the source of truth for the look (D-001) |  | 2026-11-07 |
| D-007 | 3 | Actor tokens color.actor.skill and color.actor.you | approved | Same values as info and warning, without their status meaning; contrast 10.4 and 11.5 | color.actor | 2026-11-07 |
| D-008 | 3 | Cards exactly as design.md: padding 2rem, 2rem between children, no border | alternative | Owner keeps design.md as is, accepting looser cards that blend with the page background in light mode | component:card, space.inset.card, space.stack.card | 2026-11-07 |
| D-009 | 3 | heading-small line height 1.3 | approved | Two-line titles on phones were cramped at 1.1; one value replaces the overrides in code | heading-small | 2026-11-07 |
| D-010 | G3 | Foundations approved | approved | design.md tokens imported 1:1 plus approved additions: actor colors, code text style, border widths 1px and 2px, card spacing tokens; light and dark by system setting; WCAG 2.2 AA baseline; primary button deferred for contrast; additions written back to design.md |  | 2026-11-07 |
| D-011 | G4 | Blueprint and four code batches | approved | B1 foundations and Storybook first to verify D-002, then primitives, composites, patterns with screen migration; owner approves each batch; B1 starts in a new session |  | 2026-11-07 |
| D-012 | 5 | Dark theme follows the system setting without JavaScript | approved | Exporter also emits a prefers-color-scheme dark block for :root without data-theme=light; data-theme still overrides, used by Storybook | themes | 2026-11-07 |
| D-013 | 5 | Rem units in code for font sizes and spacing | approved | Reopens D-010 for units only: blueprint keeps px, exporter writes rem (16px = 1rem) except border widths, so browser text size settings keep working (WCAG 1.4.4); no visual change at default size | text-styles, space | 2026-11-07 |
| D-014 | 5 | B1 foundations accepted | approved | pnpm check exit 0; Storybook on Astro 7 verified; foundations reviewed in Color, Typography and Spacing stories | foundation:color, foundation:typography, foundation:spacing | 2026-11-07 |
