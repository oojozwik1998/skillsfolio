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

## Public repository and confidentiality

This repository is public, so everything committed here is published on push.

- Never commit client names, client data, meeting notes, credentials or `.env` files.
- A skill enters `skills/` only after Oskar approves that specific skill.
- `.ai/specs`, `.ai/runs` and `.ai/lessons` are public too: write them without private or client details.
- Never push, open a PR or change GitHub settings without showing Oskar what leaves the computer and getting an explicit "ok".
