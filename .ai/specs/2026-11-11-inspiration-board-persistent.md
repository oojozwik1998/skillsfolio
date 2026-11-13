# Inspiration board: a permanent home for inspirations

Status: approved by the owner for the public catalog on 2026-11-12. The analysis round (test scenario 6) has not yet run on real pins.

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
| 8 | ~~Direction tab on the board~~ Revised 11.11 after the first test: no Direction tab. Features and direction live in the board data and are read in `inspirations.md`. | The owner found the tab hard to understand: an abstract form with text-only features. |
| 9 | ~~Full editing of features on the board~~ Revised 11.11: features are not edited on the board. Corrections go through the agent. | Follows from 8. |
| 10 | ~~User-owned fields and conflicts~~ Revised 11.11: dropped together with board editing; the agent updates features directly and lists the changes in the round summary. | Nothing left to protect once the board does not edit features. |
| 11 | Pins made without the agent show as a "N pins waiting to be named" counter. The "Send to agent" button is hidden in standalone mode. Analysis runs when the user asks the agent. | Nobody listens for "Send to agent" without a session. |
| 12 | The existing dated session stays in the old format. No migration. | Owner choice; only one old session exists. |
| 13 | Topics outside any project go to a library folder, default `~/Inspirations/`. The skill asks once and remembers the choice in a small settings file. | No hard-coded personal path, sensible default. |
| 14 | Nothing from `inspirations/` goes into git. The skill asks once per repo to add it to `.gitignore`, recommending yes. | Screenshots are third-party material, heavy, and risky in client or public repos. |
| 15 | A topic opens as a board split into **sections**, one per category, plus "Unsorted". Each card has "new" and "waiting" badges; a click opens the single-item pinning view. | Revised 11.11: sections replace the category filter. |
| 16 | Areas of a project are separate topics. Inside a topic, **each inspiration belongs to one section** (category). The user drags inspirations between sections or picks the section in the pinning view. New inspirations land in "Unsorted"; the agent may sort unsorted ones during analysis. Features still carry a category for the markdown, by default the section of their source. | Revised 11.11: the owner wants to categorize on the board itself. |
| 17 | A new topic starts with no sections. "Add section" offers the skill vocabulary as one-click suggestions (typography, color, layout and composition, logo and mark, image and illustration, web/UI, motion, material and print) and accepts custom names. Sections can be renamed; deleting a section moves its inspirations to "Unsorted". | Revised 11.11: empty default sections cluttered the board. |
| 18 | Build everything in one pass, test once at the end against the scenarios below. | Owner choice. |
| 19 | Board UI in English only. The agent still talks in the user's language and writes feature names and direction in that language. | Simplest public version. |
| 20 | Source lives in `skills/inspiration-board/`. `~/.claude/skills/inspiration-board` becomes a symlink to it, after a backup of the current folder. | One version for the owner and everyone else. |
| 21 | Revised 13.11 after the first real session: the old header "Done" button ended the session from any view, so the owner clicked it in the single-item view to close that inspiration and sent unfinished pins to the agent. Now **"Done" in the single-item view only closes it** (back to the topic board, also <kbd>Esc</kbd>). Ending a session is a separate **"Send to agent"** button, shown only on the topic board in session mode, which opens a confirmation with a summary (inspirations, pins, notes waiting, inspirations without pins) and "Keep pinning" as the default choice. | "Done" next to an open item reads as "close this"; sending work to the agent must be a deliberate, confirmed step. |

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
- `direction`: `text`, `updated_round`
- `features[]`: `id`, `name`, `plain` (plain-language explanation), `scope`, `category`, `list` (`take` | `avoid`), `sources[]` (item + pin), `status` (`active` | `dropped`), `added_round`, `updated_round`
- `rounds[]`: `n`, `date`, `focus`, `summary`, counts of items added, pins named, features added, changed, dropped
- `items[]`: as today (`id`, `source`, `frames`, `w`, `h`, `note`, `removed`, `pins[]`) plus `added_round` and `category` (section id, empty = Unsorted)
- `pins[]`: as today plus `feature_ids[]` and `named_note`. A pin is waiting when it has no features or `note != named_note`.

All logic that reads or changes this model (waiting pins, merge of client edits, sections, markdown generation) lives in plain functions in one module, separate from the HTTP server, so it can be unit-tested.

## Server and board

- `board.py open <inspirations_dir>`: topics screen, all topics in the folder, standalone mode.
- `board.py serve <topic_dir>`: session mode started by the agent, with the "Send to agent" button (topic board only, with a confirmation); exits after sending and prints `BOARD_DONE`.
- Standalone mode exits after about a minute without a heartbeat from any open tab.
- Board views: topics screen → topic board with sections (drag between sections, add / rename / delete sections, badges, add by link / upload / paste / drop) → single-item pinning view with a section picker.
- Every interactive element has hover and focus states; empty states for no topics, no items, empty sections; works at phone width for reading.

## Agent flow (SKILL.md)

1. Resolve topic: match existing topic or create one. Resolve location: project `inspirations/`, or library folder from settings (ask once).
2. Quick add: `board.py add` only, report what was added and how many pins wait. No board, no analysis.
3. Session: add items, start `serve`, wait for `BOARD_DONE`.
4. Analyze only waiting pins (crops, overviews), ask at most one question per unclear pin, assign category (default: the section of the source inspiration); optionally sort unsorted inspirations into sections.
5. Merge: new features in, existing ones updated; propose the updated direction for approval.
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
5. Standalone pinning: counter shows waiting pins, no "Send to agent" button, server stops after closing the tab.
10. Session: "Done" and <kbd>Esc</kbd> in the single-item view return to the topic board and the server keeps running; "Send to agent" opens a confirmation, "Keep pinning" closes it without sending, only the confirm button ends the session.
6. Analysis round: only waiting pins are asked about; features get categories; markdown regenerates with round history.
7. Add sections (suggested and custom), drag inspirations between them, rename a section, delete one (its inspirations go to Unsorted).
8. Pick a section from the pinning view; the markdown groups inspirations by section.
9. Grid with 30+ items stays usable; phone-width reading works.

## Resolved questions

- Automated tests: yes. Stdlib `unittest` tests for the data module (`skills/inspiration-board/tests/`), run by `pnpm test:skills`, included in `pnpm check` and as a CI job. No coverage tool is installed for Python, so coverage is not enforced there; every function in the data module gets at least one test.
- Catalog page: requirements go into a "Requirements" section of `SKILL.md`, which the page already renders. No board screenshots for now.

## Done criteria

- All test scenarios pass on the owner's machine.
- `pnpm test:skills` passes.
- `pnpm check` passes with the skill in `skills/`.
- The owner approves the skill for the public catalog before any push.
