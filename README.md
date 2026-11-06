# Skills Folio

A public catalog of agent skills by Oskar Jóźwik. Browse the skills, open one and install it with a single command:

```sh
npx skills add oojozwik1998/skills-folio --skill <name>
```

## Architecture

The site has no database. Skill files in this repository are the single source of truth.

```
skills/<name>/SKILL.md
    ├── Astro site      builds the public pages
    ├── Keystatic panel edits the files during local development
    └── skills CLI      installs a skill straight from this repository
```

| Path | Purpose |
|---|---|
| `skills/` | Skill content |
| `keystatic.config.ts` | Panel definition |
| `src/content.config.ts` | Loads skills into the site and validates them |
| `src/lib/skills.ts` | Skill schema and logic |
| `src/config.ts` | Site name and repository |
| `src/pages/` | Routes: `/` and `/skills/<name>/` |
| `src/styles/global.css` | Tokens from `design.md` |
| `.ai/` | Specs, run logs and lessons for AI agents, see `AGENTS.md` |

## Run locally

Requires Node.js 22.23.4 or later and pnpm.

```sh
pnpm install
pnpm dev
```

- Site: http://localhost:4321
- Panel: http://localhost:4321/keystatic

To build the static site: `pnpm build`, then `pnpm preview`.

No environment variables are needed yet.

## Add a skill

Use the panel, or create `skills/<name>/SKILL.md`:

```md
---
name: my-skill
description: What the skill does and when to use it.
---

Instructions for the agent.
```

`name` must be lowercase with hyphens and equal the folder name. Otherwise the build stops.
