# Design system handoff - Skills Folio

Status as of 2026-11-07. Target: code only (no Figma library), prototype depth.

## What exists

| Layer | Where | Notes |
|---|---|---|
| Tokens | `src/components/ui/tokens/` | Generated from `design-system/blueprint.json` (values from `design.md`): `tokens.css`, `text-styles.css`, `tokens.dtcg.json`, `tokens.ts`. Do not edit by hand. |
| Tailwind utilities | `src/styles/global.css` | Semantic color, radius and font utilities point at the `--ds-*` variables. `type-*` utilities mirror the generated text styles; a unit test keeps them in sync. |
| Components | `src/components/ui/<name>/` | One Astro component and one story file per component. Variant logic in `src/lib/ui.ts`. |
| Docs | Storybook (`pnpm storybook`) | Foundations, Primitives, Composites, Patterns. Theme switch in the toolbar: System, Light, Dark. |

### Components

| Component | Export | Tier | Used on |
|---|---|---|---|
| Icon | `Icon` | primitive | Process diagram arrows, loop note, step chevrons |
| Inline code | `InlineCode` (+ `inline-code` utility) | primitive | Install copy, code in rendered skill text and data files |
| Text link | `TextLink` | primitive | Site name, back links, source links |
| Badge | `Badge` | primitive | Actor labels on steps |
| Button | `Button` | primitive | Copy action |
| Card | `Card` | composite | Truth and memory cards |
| Link card | `LinkCard` | composite | Catalog list |
| Copy command | `CopyCommand` | composite | Install commands |
| Callout | `Callout` | composite | Loop note, "From testing" examples |
| Disclosure | `Disclosure` | composite | Step by step; opens from any link to its id |
| Page header | `PageHeader` | pattern | All pages (the only h1) |
| Section header | `SectionHeader` | pattern | Sections on tailor-my-cv |

All 12 pass typecheck, lint, unit tests (100% coverage of `src/lib`), browser tests with axe and the Storybook build. All are `needs_review`: Astro is not the skill's fully supported stack, so a developer should review them.

### Exception register

No approved exceptions. Component code uses tokens only.

## Usage rules

1. Import components from `src/components/ui/<name>/<Name>.astro`. Do not restyle them from the outside beyond layout (margins, width, grid placement).
2. Use semantic utilities (`bg-surface-default`, `text-text-subtle`) and `type-*` text styles. No raw colors or sizes.
3. Navigation uses `TextLink` or `LinkCard`; actions use `Button`.
4. One `PageHeader` per page. Sections use `SectionHeader` with `<section aria-labelledby={id}>`.
5. Text that the reader should copy goes in `CopyCommand`, not `InlineCode`.
6. Color never carries meaning alone: badges always show a text label, card accents are decoration.

## Changing tokens

1. Change the value in `design.md` and in the blueprint through the ds-architect skill (`ds.mjs`), never by editing generated files.
2. Regenerate: `node <ds-code skill>/scripts/export-tokens.mjs --out src/components/ui/tokens`. It writes rem units (except border widths) and a dark block that follows the system setting.
3. If a text style changed, update the matching `type-*` utility in `global.css`; `pnpm test` fails until they match.
4. Run `pnpm check`.

## Setup

1. `pnpm install` (esbuild's install script is denied on purpose in `pnpm-workspace.yaml`; it is not needed).
2. First run on a new machine: `pnpm exec playwright install chromium`.
3. `pnpm storybook` opens Storybook on port 6006 (telemetry is off).
4. `pnpm check` runs build, typecheck, lint, unit tests, the Storybook build and browser tests.
5. If a dev server already uses port 4321, run browser tests with `E2E_PORT=4329 pnpm test:e2e`.

## Open items

| Item | Why it matters | Effort |
|---|---|---|
| Developer review of the 12 components | Required for the `review` support tier: prop APIs, attribute forwarding in `TextLink` and `Button`, the Disclosure script | ~1-2 h for a developer |
| Poppins 500 is not loaded | `font-medium` ("From testing:" label) renders at 400; load the weight or drop the bold | ~5 min |
| Token `size-56` equals 4rem (64px) in `design.md` | The name does not match the value | ~2 min |
| Disabled button state is subtle in light mode | Not required by WCAG; needs a `disabled` token if it should be clearer | decision |
| Table and file list keep their borders | Cards follow D-008 without borders; two container styles sit on one page. Table component was deferred (D-004) | decision |
| Storybook accessibility checks run only in the UI | Automated axe checks cover the site pages, not each story | ~30 min to add the Storybook test runner |
| Primary button | Deferred: white on action-primary is 4.0:1 | decision |
| `Install` heading on the skill page | Stays `heading-small`; `SectionHeader` only has `heading-large` | decision |
| Prose styles (`.skill-body`) | Kept as a style, not a component (D-004) | - |

Automated checks are supporting evidence only and do not certify WCAG conformance. Manual keyboard and screen reader checks remain on the review list.
