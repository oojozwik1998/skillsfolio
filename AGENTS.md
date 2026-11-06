# skills-folio - Agent Guide

Public catalog of Oskar's own agent skills. Visitors browse skills, read their details and install them with `npx skills add`.

Owner: Oskar (senior product designer, not a developer). Explain developer terms in plain words when reporting to him, and answer in the language of his message.

## Repository structure

| Path | Purpose | Rule |
|---|---|---|
| `.ai/specs/` | Active specifications, named `YYYY-MM-DD-slug.md` | Write or update a spec before any non-trivial code change |
| `.ai/specs/implemented/` | Specs that are fully built | Move a spec here when its done criteria pass |
| `.ai/specs/archive/` | Abandoned or replaced specs | Keep them with a one-line reason at the top |
| `.ai/runs/` | Logs of autonomous AI runs, named `YYYY-MM-DD-slug.md` | Every autonomous run writes a log: goal, steps, checks, result |
| `.ai/lessons.md` | Index of lessons learned | Add one line per lesson |
| `.ai/lessons/` | Detail for lessons that need more than one line | Record a lesson after every fixed bug or correction |
| `design.md` | Design tokens and visual rules | Source of truth for colors, typography, spacing and radii |

Private working notes stay local and are ignored by git: `meetings/`, `tasks/`, `project-state.md`.

## Stack and layout

Astro 7 with strict TypeScript, Tailwind CSS 4, Keystatic and Zod. Single app with static output and no database. Do not add a database, a server adapter or a UI framework without a spec the owner approved.

- `skills/<name>/SKILL.md` is the only source of skill content. The site, the panel and the `skills` CLI all read it.
- `/tailor-my-cv/` is a separate repository with personal data. Never add it to this repository or copy from it.
- The panel runs in local development only, at `/keystatic`.
- See `README.md` for the architecture and `.ai/specs/` for detail.

## Engineering standards

Detail: `.ai/specs/2026-11-06-engineering-standards.md`.

- **Logic:** keep it in `src/lib/` as plain TypeScript. `.astro` files only fetch and render. Copy `src/lib/skills.ts` and `src/pages/skills/[name].astro` as patterns.
- **Skills:** the name is lowercase with hyphens and equals its folder. Invalid metadata must stop the build.
- **Design:** `design.md` is the source of truth. Use semantic utilities and `type-*` text styles only, and define light and dark values together.
- **UI states:** every interactive element has hover and focus states, every list has an empty state, and layouts work at phone width.
- **Types:** no `any` and no `@ts-ignore`. Derive types from Zod schemas.
- **Dependencies:** TypeScript stays on 6.0 until `@astrojs/check` and `typescript-eslint` support 7.

## Working rules

- **Plan first:** plan any task with more than a few steps before coding, and put detail into the spec. If work goes off track, stop and re-plan instead of pushing on.
- **Verify every change:** run the validation commands and show the output before calling work done. A change is not done until it has passed a real check.
- **Replace weak fixes:** if a fix turns out mediocre, discard it and implement the clean solution rather than patching on top.
- **Record lessons:** after every correction or fixed bug, add a rule to `.ai/lessons.md` so the mistake is not repeated. If a lesson applies to every task, add it to this file as well.
- **Fix bugs from evidence:** start from the bug report, the failing check or the logs, and find the cause before changing code.
- **Keep context clean:** hand separate research or side tasks to subagents when the tool supports them.
- **Reuse repeated work:** turn anything done repeatedly into a script or a skill.

## Public repository and confidentiality

This repository is public, so everything committed here is published on push.

- Never commit client names, client data, meeting notes, credentials or `.env` files.
- A skill enters `skills/` only after Oskar approves that specific skill.
- `.ai/specs`, `.ai/runs` and `.ai/lessons` are public too: write them without private or client details.
- Never push, open a PR or change GitHub settings without showing Oskar what leaves the computer and getting an explicit "ok".
