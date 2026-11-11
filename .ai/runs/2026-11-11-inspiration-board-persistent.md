# Inspiration board: permanent topic boards

Goal: build the spec `.ai/specs/2026-11-11-inspiration-board-persistent.md` in one pass.

## Steps

1. Copied the skill from the local skills folder into `skills/inspiration-board/` and kept a backup outside the repository.
2. Added `scripts/model.py`: the board data model (topics, items, waiting pins, user edits, rounds, conflicts, markdown) as plain functions.
3. Rewrote `scripts/board.py`: topic commands, quick add, round and accept, session server and standalone server with an idle stop, launcher file.
4. Rewrote `assets/board.html` in English: topics screen, topic grid with a category filter, pinning view, Direction tab with full editing and categories, light and dark themes.
5. Updated `scripts/crop.py` (only waiting pins, stable crop names) and `scripts/capture.py` (finds Chrome on macOS, Linux and Windows).
6. Rewrote `SKILL.md` in English for public use, with a Requirements section.
7. Added `tests/test_model.py`, `pnpm test:skills`, the CI job and the skill page to the browser-test routes.
8. Replaced the local skill folder with a symlink to the repository copy.

## Checks

- `pnpm check`: passed (build, types, lint, unit tests, skill tests, Storybook build, 22 browser tests).
- Integration run on a temporary project: init, add, crop, round, conflicting round, accept, markdown output.
- Board driven in a browser (Playwright): editing a feature, adding a category, dropping and adding features, drawing a pin, phone width, dark mode, old-format read-only view. No page errors.
- Standalone server stopped by itself after the tabs closed.

## Result

Built. Waiting for the owner to walk through the manual test scenarios in the spec on a real topic.
