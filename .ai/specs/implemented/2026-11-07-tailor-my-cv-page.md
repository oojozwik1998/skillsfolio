# tailor-my-cv page

Status: implemented on 2026-11-07

## Goal

Add `tailor-my-cv`, the first external skill, to the catalog: a card on the list and a dedicated page that explains how it works and how to get it.

## Decisions (owner, 2026-11-07)

- The page copy is in English, translated from the owner's Polish mockup.
- The layout follows the mockup. The look follows `design.md`, not the mockup's colors and font.
- "Skill" uses the Info tokens and "You" uses the Warning tokens.
- The page is built now with the final repository link. Making the private `tailor-my-cv` repository public is a separate decision before publishing.

## Changes against the mockup

- Add an install section at the top: clone command, next steps, requirements, repository link.
- Use one label per actor, "You" or "Skill", instead of four variations.
- Move the two CV images out of the HTML into `public/images/tailor-my-cv/`.
- Replace text symbols with SVG icons.

## Structure

- `src/data/external-skills.ts`: catalog entries for skills kept in their own repository.
- `src/data/tailor-my-cv.ts`: page copy.
- `src/pages/skills/tailor-my-cv.astro`: the page. The panel does not edit it.
- `src/lib/skills.ts`: `repositoryUrl` and `cloneCommand`.

## Sections

1. Title, lead and install
2. The whole process on one picture: first-run lane and per-offer lane. Clicking a stage opens its details
3. Step by step: nine expandable steps
4. Layout comparison
5. Where the line of truth is
6. What the skill remembers
7. Where everything lives
8. Status note

## Out of scope

- Changes in the `tailor-my-cv` repository.
- A generic template for external skill pages. Add one when a second external skill needs it.

## Done criteria

- The catalog shows a card that opens `/skills/tailor-my-cv/`.
- The install command copies correctly.
- Clicking a stage in the process opens the matching step.
- `pnpm check` passes, including axe in light mode, dark mode and at phone width.
