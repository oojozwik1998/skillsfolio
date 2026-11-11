# Inspiration board: a permanent home for inspirations

Status: built, waiting for the owner to run the test scenarios

## Goal

Turn `inspiration-board` from a one-off session tool into a permanent place for inspirations per topic: easy to come back to, easy to add to without a full session, split into categories, with one living "direction" that grows round by round. Publish it in this catalog as a skill anyone can use.

## Problem today

- Every session creates a dated folder (`inspirations/YYYY-MM-DD-topic/`). Real use already broke this: one dated folder ended up holding two rounds on different days plus unrelated work folders.
- There is no way to split a topic into areas (typography, color, illustration...).
- There is no clear way to come back, add new items later or manage what is there. The board only exists while an agent session runs it.
- The skill is personal: Polish instructions, the owner's name, hard-coded paths, macOS-only tools, dependencies on private skills.

## Decisions

| # | Decision | Why |
|---|---|---|
| 1 | One board per topic: `inspirations/<topic-slug>/`, no date. Each reopening is a new round. A project can have several topics. | The unit people come back to is the topic, not the day. |
| 2 | The result file is a living document: current state on top, short round history at the bottom. | The current direction must be readable without reading every round. |
| 3 | A round analyzes only new pins and pins whose note changed, then checks new features against existing ones and proposes direction updates. | No re-asking about pins named weeks ago. |
| 4 | Two ways to add between sessions: quick add from chat, and a board that opens without the agent. | Inspiration shows up when there is no time for a session. |
| 5 | Public skill: English instructions, the agent speaks the user's language, no personal names, paths or private-tool integrations. Other skills are optional ("if available"). | It ships in this public catalog. |
| 6 | Start without the agent: a double-click launcher file in `inspirations/` (macOS) plus one terminal command (all systems). The server stops when the tab closes. | A file to click is the lowest bar; a system service is too heavy to explain. |
| 7 | The launcher opens a topics screen: cards with thumbnail, item count, pins waiting, last round date, and "New topic". | Several topics per project need one entry point. |
| 8 | Features and direction live in the board data. The board has a "Direction" tab; the markdown file is generated from the same data. | One source of truth; markdown stays for agents and pasting elsewhere. |
| 9 | Full editing on the Direction tab: rename features, move between take/avoid, change category, edit direction text, drop/restore. | Owner choice. |
| 10 | User edits win. Any field the user edited is marked; a later round never overwrites it silently, but proposes "was / proposed / why" for approval. Untouched fields update automatically and are listed in the round summary. | Full editing must not be undone by the agent. |
| 11 | Pins made without the agent show as a "N pins waiting to be named" counter. The "Done" button is hidden in standalone mode. Analysis runs when the user asks the agent. | Nobody listens for "Done" without a session. |
| 12 | The existing dated session stays in the old format. No migration. | Owner choice; only one old session exists. |
| 13 | Topics outside any project go to a library folder, default `~/Inspirations/`. The skill asks once and remembers the choice in a small settings file. | No hard-coded personal path, sensible default. |
| 14 | Nothing from `inspirations/` goes into git. The skill asks once per repo to add it to `.gitignore`, recommending yes. | Screenshots are third-party material, heavy, and risky in client or public repos. |
| 15 | A topic opens as a grid of all items with "new" and "waiting" badges; a click opens the current single-item pinning view. | A permanent board grows to 30-40 items. |
| 16 | Areas of a project are separate topics. Inside a topic, every feature has a category, assigned by the agent and editable. Direction is grouped by category; the grid filters by category. | One inspiration often gives features from several areas. |
| 17 | Categories start from the skill vocabulary (typography, color, layout and composition, logo and mark, image and illustration, web/UI, motion, material and print). Users add and rename categories on the board. Empty categories are hidden. | Consistent default, room for project-specific areas. |
| 18 | Build everything in one pass, test once at the end against the scenarios below. | Owner choice. |
| 19 | Board UI in English only. The agent still talks in the user's language and writes feature names and direction in that language. | Simplest public version. |
| 20 | Source lives in `skills/inspiration-board/`. `~/.claude/skills/inspiration-board` becomes a symlink to it, after a backup of the current folder. | One version for the owner and everyone else. |

### Assumed defaults (owner can override)

- Per-round focus question becomes optional; categories carry the split.
- The per-item "Overall" note stays.
- Quick add matches the topic by name; with no match, the agent asks whether to create a new topic.
- Legacy dated folders (with `pins.json` and no `board.json`) appear on the topics screen as cards marked "old format" and open read-only, without the Direction tab.
- Result file name: `inspirations.md`.

## Layout

```
<project>/inspirations/
  Open board.command        # macOS launcher, double-click
  <topic-slug>/
    board.json              # single source of truth
    inspirations.md         # generated from board.json
    images/                 # frames, crops, overviews
~/.config/inspiration-board/config.json   # { "library_dir": "..." }
```

## Data model (`board.json`, version 2)

- `topic`, `slug`, `created`, `language`
- `categories[]`: `id`, `name`, `custom`
- `direction`: `text`, `user_edited`, `updated_round`
- `features[]`: `id`, `name`, `plain` (plain-language explanation), `scope`, `category`, `list` (`take` | `avoid`), `sources[]` (item + pin), `status` (`active` | `dropped`), `user_edited[]` (field names), `added_round`, `updated_round`
- `rounds[]`: `n`, `date`, `focus`, `summary`, counts of items added, pins named, features added, changed, dropped
- `items[]`: as today (`id`, `source`, `frames`, `w`, `h`, `note`, `removed`, `pins[]`) plus `added_round`
- `pins[]`: as today plus `feature_ids[]` and `named_note`. A pin is waiting when it has no features or `note != named_note`.

All logic that reads or changes this model (waiting pins, merge of client edits, user-edit protection, markdown generation) lives in plain functions in one module, separate from the HTTP server, so it can be unit-tested.

## Server and board

- `board.py open <inspirations_dir>`: topics screen, all topics in the folder, standalone mode.
- `board.py serve <topic_dir>`: session mode started by the agent, with the "Done" button; exits on "Done" and prints `BOARD_DONE`.
- Standalone mode exits after about a minute without a heartbeat from any open tab.
- Board views: topics screen → topic grid (category filter, badges, add by link / upload / paste / drop) → single-item pinning view (as today) and the Direction tab (grouped by category, full editing, category management).
- Every interactive element has hover and focus states; empty states for no topics, no items, no features; works at phone width for reading.

## Agent flow (SKILL.md)

1. Resolve topic: match existing topic or create one. Resolve location: project `inspirations/`, or library folder from settings (ask once).
2. Quick add: `board.py add` only, report what was added and how many pins wait. No board, no analysis.
3. Session: add items, start `serve`, wait for `BOARD_DONE`.
4. Analyze only waiting pins (crops, overviews), ask at most one question per unclear pin, assign category.
5. Merge: new features in; untouched fields update; user-edited fields get a "was / proposed / why" question; propose the updated direction for approval.
6. Write `board.json`, regenerate `inspirations.md`, append the round, report: file path, direction, 5-8 key features, one next step.

## Portability work

- Find Chrome on macOS, Linux and Windows (today: macOS path only); clear message when missing.
- HEIC conversion uses macOS `sips`; on other systems show a clear "convert to JPG first" message.
- Remove the owner's name, Polish wording and personal paths from instructions; private skills become optional mentions.
- Document requirements on the skill page: Python 3.9+, Pillow, Google Chrome.

## Test scenarios (manual, before calling it done)

1. New topic in a git project: folder without date, `.gitignore` question, launcher file created.
2. New topic outside any project: library-folder question asked once, remembered next time.
3. Quick add of a link to an existing topic: item appears, board not opened.
4. Launcher double-click: topics screen lists topics plus the legacy Alpine folder (read-only).
5. Standalone pinning: counter shows waiting pins, no "Done" button, server stops after closing the tab.
6. Analysis round: only waiting pins are asked about; features get categories; markdown regenerates with round history.
7. Edit a feature name and direction on the board, run another round that touches that feature: agent proposes, does not overwrite.
8. Add, rename and filter by a custom category.
9. Grid with 30+ items stays usable; phone-width reading works.

## Resolved questions

- Automated tests: yes. Stdlib `unittest` tests for the data module (`skills/inspiration-board/tests/`), run by `pnpm test:skills`, included in `pnpm check` and as a CI job. No coverage tool is installed for Python, so coverage is not enforced there; every function in the data module gets at least one test.
- Catalog page: requirements go into a "Requirements" section of `SKILL.md`, which the page already renders. No board screenshots for now.

## Done criteria

- All test scenarios pass on the owner's machine.
- `pnpm test:skills` passes.
- `pnpm check` passes with the skill in `skills/`.
- The owner approves the skill for the public catalog before any push.
