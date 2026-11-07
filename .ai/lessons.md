# Lessons

One line per lesson, newest first: `YYYY-MM-DD - what went wrong - the rule that prevents it`. Link to `.ai/lessons/<slug>.md` when more detail is needed.

- 2026-11-07 - An unanchored ignore rule, `tailor-my-cv/`, also hid `public/images/tailor-my-cv/`, and local tests still passed because the files were on disk - anchor ignore rules with a leading `/`, and check the list of committed files before pushing.
- 2026-11-06 - Importing `node:path` in `src/lib/skills.ts` broke the panel, because `keystatic.config.ts` runs in the browser and imports that file - keep anything the panel imports free of Node modules.
- 2026-11-06 - `astro check` hung with no output when a dependency failed to load, because Astro waited for an install prompt - run it with no terminal input and a time limit when it stalls, and keep `@emnapi/runtime` on the stable 1.x line so pnpm does not pick a beta.
- 2026-11-06 - The Keystatic collection used `fields` instead of `schema`, and the panel route still returned 200 - a 200 does not prove the panel works, so run `pnpm typecheck` and open the panel in a browser after changing `keystatic.config.ts`.
- 2026-11-06 - `git add -A` failed on a folder with its own repository - stage explicit paths, and keep separate repositories in `.gitignore`.
