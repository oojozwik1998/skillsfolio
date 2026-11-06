# App template

Status: in progress

## Goal

A working starting point for a public catalog of agent skills. Visitors browse skills, open a skill and copy its install command. The owner edits skills in a panel. The repository itself is the install source for the `skills` CLI.

## Stack

| Piece | Choice | Why |
|---|---|---|
| Site | Astro 7, TypeScript (strict) | Content-first, static output, no JavaScript by default |
| Styling | Tailwind CSS 4 | Semantic tokens from `design.md` become the only available colors |
| Panel | Keystatic, local storage | Edits files in the repo, needs no database |
| Validation | Zod | A skill with bad metadata stops the build |

## Layout

Single app, no monorepo.

```
skills/<name>/SKILL.md     Skill source: read by the site, the panel and the skills CLI
keystatic.config.ts        Panel definition
src/content.config.ts      Loads skills into Astro
src/config.ts              Site name and repository
src/lib/skills.ts          Schema and skill logic
src/components/            UI pieces
src/layouts/               Page shell
src/pages/                 Routes
src/styles/global.css      Tokens from design.md and text styles
```

## Behavior

- `/` lists all skills by name, with an empty state when there are none.
- `/skills/<name>/` shows the description, the install command with a copy button, a source link and the instructions.
- `/keystatic` opens the panel during local development only.
- Install command: `npx skills add <owner>/<repo> --skill <name>`.

## Skill rules

- Skill files follow the `skills` CLI format: `skills/<name>/SKILL.md` with `name` and `description` in the frontmatter.
- `name` is lowercase with hyphens and must equal the folder name. A mismatch stops the build.
- The panel keeps only `name`, `description` and the body. Other frontmatter fields are dropped when a skill is saved there.

## Out of scope

- Deployment and online panel access. These need GitHub mode, a hosting choice and a server adapter, because the panel has server routes.
- Search, filters and categories.
- Importing real skills. Each one needs the owner's approval first.
- Skills kept in their own repository, listed as a card with a link and installed by downloading that repository instead of `npx skills add`. `tailor-my-cv` is the first case. This needs its own spec, because such skills have no `SKILL.md` in `skills/`.

## Done criteria

- Install and build pass.
- The dev server serves `/`, `/skills/example-skill/` and `/keystatic`.
- The built output contains the install command for the example skill.
- README describes the architecture and how to run the project.
