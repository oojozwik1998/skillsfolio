# Engineering standards

Status: approved by the owner on 2026-11-06

Minimal rules agents follow from the first feature on. Add a rule only when a real need appears.

## 1. Stack at a glance

| Technology | Version | Why |
|---|---|---|
| Astro | 7 | Content-first site with static output |
| TypeScript | 6.0 | Strict typing. Version 7 is not supported yet by `@astrojs/check` and `typescript-eslint` |
| Tailwind CSS | 4 | Styling limited to semantic tokens |
| Keystatic | 0.6 | Panel that edits repository files, no database |
| Zod | 4 | Validates skill metadata |
| ESLint | 10 | Linting, with the TypeScript, Astro and accessibility plugins |
| Vitest | 5 | Unit tests with coverage |
| Playwright + axe | 1.65 | Browser tests and automated accessibility checks on the built site |
| pnpm | 12 | Package manager |

## 2. Repository layout and boundaries

- Single app. No monorepo until a second app exists.
- Allowed imports: `pages` → `layouts`, `components`, `lib`, `config`. `components` → `lib`. `lib` imports only external packages, never Astro components.
- All logic lives in `src/lib/` as plain, testable TypeScript. `.astro` files only fetch data and render it.
- Static output is the default. A server adapter or a database requires an approved spec.

## 3. Domain concepts

- **Skill:** a capability an agent can install. Identified by `name`.
- **Hosted skill:** stored in `skills/<name>/SKILL.md` in this repository and installed with `npx skills add`.
- **External skill:** kept in its own repository, listed as a card with a link and installed by downloading that repository. Not implemented yet, needs its own spec.
- **Catalog:** the public list of skills.
- **Panel:** the owner's editing tool at `/keystatic`.

## 4. Naming conventions

| Thing | Convention | Example |
|---|---|---|
| Skill name and folder | lowercase with hyphens, identical | `skills/my-skill/` |
| Astro components and layouts | PascalCase | `SkillCard.astro` |
| TypeScript files | lowercase with hyphens | `src/lib/skills.ts` |
| Functions and variables | camelCase | `installCommand` |
| Routes | lowercase, trailing slash | `/skills/my-skill/` |
| Unit tests | next to the code | `src/lib/skills.test.ts` |
| Browser tests | `tests/e2e/` | `tests/e2e/catalog.spec.ts` |
| Specs and run logs | date and slug | `2026-11-06-app-template.md` |

## 5. Data and validation

- There are no backend services, API routes or database tables, so patterns for them are intentionally omitted.
- Skill frontmatter is validated by `skillSchema` in `src/lib/skills.ts`. Invalid data must stop the build, never render a broken page.
- The `skills` CLI format comes first: `name` and `description` stay valid for the CLI, and the catalog adds nothing that breaks installation.
- Before adding fields, note that the panel drops frontmatter fields missing from `keystatic.config.ts`, so add them in both places.

## 6. Frontend patterns

- Use Astro components. Add client-side JavaScript only where a feature needs it, as a small script in the component.
- `design.md` is the source of truth. Use only semantic utilities, such as `bg-surface-default` and `text-text-subtle`. The Tailwind default palette is disabled.
- Apply text styles as a unit with `type-*` utilities. Do not combine separate font size and weight classes.
- Define colors for both light and dark mode together.
- Every interactive element needs a visible focus state and hover state. Every list needs an empty state.
- Layouts must work at phone width with a 16 px side gutter and no horizontal page scroll.

## 7. Typing rules

- `astro/tsconfigs/strict` stays on. No `any`, no `@ts-ignore`.
- Derive types from Zod schemas with `z.infer` rather than declaring them twice.

## 8. Testing rules

- 100% unit coverage for `src/lib/` and every other plain TypeScript file with logic. New logic ships with its tests.
- `.astro` files are covered by browser tests against the built site, because that is what visitors receive. Each route has at least one test.
- Each route passes an axe accessibility check with no serious or critical violations, in light and dark mode.
- Fix the cause of a failing test. Do not remove or weaken it to make a check pass.

## 9. Environments, CI and delivery

- No environment variables yet. When one is added, document it in `.env.example` with a placeholder value. `.env` is never committed.
- Every pull request runs build, type check, lint, unit tests with coverage, and browser tests. The same checks run locally with one command: `pnpm check`.
- Do not merge a pull request unless all required checks are green.
- Pushing, opening a pull request and changing GitHub settings require the owner's explicit "ok" first.
- Anything committed here becomes public on push, see `AGENTS.md`.

## Sources

- Astro testing guide: https://docs.astro.build/en/guides/testing/
- `skills` CLI, creating skills: https://github.com/vercel-labs/skills/blob/main/docs/creating-skills.md
- Keystatic GitHub mode: https://keystatic.com/docs/github-mode
- Peer dependency ranges from the npm registry, checked 2026-11-06.
