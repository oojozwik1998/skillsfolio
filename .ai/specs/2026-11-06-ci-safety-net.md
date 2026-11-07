# CI safety net

Status: in progress

## Goal

Every pull request runs the same checks automatically, so a change cannot reach `main` unnoticed with a broken build, type errors, lint errors, failing tests or accessibility violations.

## Checks

| Check | Command | What it covers |
|---|---|---|
| Build | `pnpm build` | The site builds and skill metadata is valid |
| Types | `pnpm typecheck` | TypeScript and `.astro` files |
| Lint | `pnpm lint` | Code rules and accessibility rules in markup |
| Unit tests | `pnpm test` | `src/lib/`, with a 100% coverage threshold |
| Browser tests | `pnpm test:e2e` | Built site: routes, install command, phone width, axe in light and dark mode |

`pnpm check` runs all of them locally.

## Decisions

- Browser tests replace the course's testcontainers scaffold, because the project has no database. They need no Docker.
- The panel runs only in local development, so browser tests do not cover it. It needs a manual check after changes to `keystatic.config.ts`.

## Done criteria

- `pnpm check` passes locally.
- The workflow runs on GitHub after the first push. It cannot be verified before that.
