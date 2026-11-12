---
name: inspiration-board
description: A permanent inspiration board per topic (website, logo, packaging...) that helps the user name what exactly they like in visual references. Captures links as screenshots, opens a local board where the user sorts inspirations into sections and pins areas with notes (like / don't like), names each pin as a precise feature with multiple-choice questions and keeps one living direction per topic that grows round by round. The board also opens without the agent, from a double-click file, so inspirations can be added any time. Use when the user says "what do I like in these inspirations", "let's pin these references", "add this to my inspiration board", "analyze my inspirations", "name what I like here", "break down this moodboard", "inspiration board", or pastes links saying they like them. Not for finding new inspiration.
argument-hint: "[topic] [links...]"
allowed-tools: Bash, Read, Write, Edit, AskUserQuestion
---

# Inspiration board

Goal: the user ends up with **named, specific features** ("tight tracking in large headings, display sizes only"), not vague praise, collected in one permanent board per topic. You analyze only what the user brings. You do not search for new inspiration.

Talk to the user in their language, briefly and without developer jargon. When you must use a technical term, explain it in plain words. Write feature names, explanations and the direction in the user's language. The board interface is in English.

`SKILL_DIR` = the folder of this file. Scripts: `scripts/board.py` (everything), `scripts/crop.py` (crops for analysis), `scripts/capture.py` (used by board.py). Everything runs locally; the board server listens on 127.0.0.1 only. Nothing leaves the computer except fetching the pages the user pasted.

## Requirements

- Python 3.9 or newer.
- Pillow for crops (`python3 -m pip install --user Pillow`). Ask before installing.
- Google Chrome, Chromium or Edge for page screenshots. Without it, links to direct images still work and the user can upload screenshots.

## Concepts

- **Topic** = one permanent board, a folder `inspirations/<topic-slug>/` without a date. Areas of a project are separate topics (Website, Logo, Packaging).
- **Round** = one analysis pass. Every reopening of a topic adds a round; earlier work is kept.
- **Section** = a category inside a topic (typography, color, hero...). The user creates sections on the board and drags inspirations into them; each inspiration is in one section or in "Unsorted". Features also carry a category, by default the section of their source inspiration.
- **Direction** = 2-3 sentences that tie the topic together, kept up to date round by round.
- **Waiting** = pins and overall notes that are new or edited since they were last named.

`board.json` in the topic folder is the single source of truth. `inspirations.md` is generated from it after every round; never edit the markdown by hand.

## Step 0 - Where and which topic

1. `python3 SKILL_DIR/scripts/board.py where` prints the inspirations folder for the current place (`dir`, `reason`).
   - `reason: "ask"` (no project here): ask once where topics outside projects should live, recommending `~/Inspirations/`. Save it with `board.py config --library <dir>` and run `where` again.
   - In a git repository, `git_ignored: false` means screenshots would end up in the repository. Ask once whether to add `inspirations/` to `.gitignore` (the list of files git skips), recommending yes: screenshots are third-party material and can be heavy. Add it only after a yes.
2. Find the topic: `board.py find <dir> "<name>"`. If nothing matches, run `board.py topics <dir>` and ask whether to use an existing topic or create a new one (offer 2-3 names based on the request).
3. New topic: `board.py init <dir> --topic "<Name>" --language <code of the conversation language>`. This also writes the double-click launcher `Open board.command` into the inspirations folder.

Then pick the mode below.

## Mode A - Quick add (no board, no analysis)

When the user only wants to drop links or files into a topic ("add this to Website", "save these for the logo"):

1. `board.py add <topic_dir> <link_or_file> [...]` (page screenshots take ~20 s each, so use a 300000 ms timeout).
2. Report in one or two lines what was added and how many notes are waiting. Do not open the board.

## Mode B - Session (pin, then analyze)

1. Add the user's links and files as in mode A.
2. Start the board in the background (Bash `run_in_background: true`): `board.py serve <topic_dir>`. It prints `BOARD_URL ...` and opens the browser on the topic.
3. Tell the user briefly:
   - the topic is a board of sections: add sections (there are one-click suggestions) and drag inspirations into them,
   - click an inspiration to pin it; its section can also be picked there,
   - click the image to comment on a spot, drag to mark an area, hold Alt for "don't like",
   - each inspiration has an "Overall" note; notes can be vague because you will ask,
   - click **Done** at the end. The board closes and you get a signal.
4. Wait. The server exits on "Done" and prints `BOARD_DONE items=N pins=M waiting=W`, and you are notified then. Do not poll. If the user writes "done" in the chat instead, stop the server and continue (everything is saved as they go).
5. Go to "Analysis round".

## Mode C - Analysis of what waits

When the user pinned things on their own ("analyze Website", "name what I pinned"), run `board.py status <topic_dir>`, tell them how many notes wait, and go to "Analysis round". Nothing waits → say so and offer to open the board.

## The board without the agent

The user can open the boards any time by double-clicking `Open board.command` in the inspirations folder (macOS), or with `python3 SKILL_DIR/scripts/board.py open <inspirations_dir>` on any system. They get a topics screen, can create topics, add links and images, sort inspirations into sections and pin. A banner shows how many notes wait and offers to copy a request for you. The server stops about a minute after the last tab closes. If the launcher reports that the skill was not found, run `board.py init` for any existing topic in that folder to rewrite it.

## Analysis round

1. `python3 SKILL_DIR/scripts/crop.py <topic_dir>` prints a manifest of what waits: per inspiration its section, the overall note, waiting pins (id, number, like / don't like, note, crop path, whether it was edited) and overview images with pins drawn. It also lists the sections, the direction and the existing features.
2. **Look at (Read) every crop** and the overview of every inspiration in the manifest. Analyze what you see in the crop, not only the note. A point comment (`"type": "point"`) is about the element under the ring, not the whole crop.
3. For each waiting pin:
   - **Precise note** (names a feature visible in the crop): use it, sharpening the vocabulary if needed. Do not ask.
   - **Vague or empty note** ("nice", "vibe", "this"): ask **one** question with a multiple-choice question tool (for example AskUserQuestion) if you have one, otherwise in the chat. Give 2-4 candidates based on what is visible in the crop, named precisely, each with a short plain-language explanation. Allow several answers, because it is often two things at once. Use the vocabulary below.
   - If the feature looks context-dependent (works in headings, not body text; in the logo, not in icons), add a second question about where it applies.
   - **Edited pin** that already has features: check whether the edit changes them; if yes, update those features (same `id`).
   - Give every feature a category: by default leave it out and it takes the section of its source inspiration; set it when the feature clearly belongs elsewhere. Reuse an existing feature (same `id`, add the new source) when the pin shows the same thing.
   - If inspirations are still in "Unsorted", you may propose sections for them in `sort` (only unsorted ones are moved).
4. Do the same for waiting overall notes, focusing on what the pins do not cover.
5. Name "don't like" pins too; they go to the avoid list (`"list": "avoid"`).
6. Propose the updated direction (2-3 sentences, mentioning features by name) and get approval: "Correct" / "Almost - I'll fix it" / "No".
7. Write the round to a temporary file and apply it: `board.py round <topic_dir> <file.json>`.

```json
{
  "focus": "typography, color",
  "summary": "one line about this round",
  "categories": [{"id": "patterns", "name": "Patterns"}],
  "sort": [{"item": "i9", "category": "typography"}],
  "features": [
    {"id": "f3", "scope": "headings only", "sources": [{"item": "i7", "pin": "p2"}]},
    {"name": "Tight tracking in display headings", "plain": "letters set close together, only at large sizes",
     "scope": "headings 48 px and up", "category": "typography", "list": "take",
     "sources": [{"item": "i7", "pin": "p1"}, {"item": "i2", "pin": null}]}
  ],
  "reviewed": [{"item": "i7", "pin": "p1"}, {"item": "i7", "pin": "p2"}, {"item": "i2", "pin": null}],
  "direction": "Approved direction text."
}
```

- A feature with `id` updates that feature; without `id` it creates a new one. Send only the fields you change, plus new `sources`.
- `pin: null` means the overall note of that inspiration.
- `reviewed` lists everything you named this round, including pins that gave no feature. Only these stop waiting.
- `categories` is needed only for new sections. Vocabulary ids (`typography`, `color`, `layout`, `logo`, `image`, `ui`, `motion`, `material`) create the section automatically when used.
- To drop a feature that no longer holds, send `"status": "dropped"`.

## Summary

Show: the path of `inspirations.md`, the direction, what changed in this round (new, changed, dropped features, inspirations you sorted) and the 5-8 most important features. The board does not show features; `inspirations.md` is where the user reads the result. End with one next step (for example "use these features as the brief for the logo?").

## Vocabulary for candidates

Always pair a precise name with a short plain-language explanation.

- **Typography:** typeface class (grotesque, neo-grotesque, geometric, humanist, serif, slab, mono, display), stroke contrast, x-height, width (condensed / extended), tracking and kerning, leading, type scale (size contrast), small caps, ligatures, terminals, aperture, optical alignment, line breaks.
- **Color:** palette (mono, analogous, complementary), temperature, saturation, lightness contrast, accent color and its share (e.g. 90/10), neutrals with an undertone, duotone, gradient (linear, mesh, grainy).
- **Layout and composition:** grid (modular, column, broken), asymmetry, whitespace, rhythm and repetition, hierarchy, scale, cropping, alignment, information density, full-bleed, layering.
- **Logo and mark:** symbol, wordmark, combination, monogram, geometric construction, negative space, stroke weight, corner rounding, modularity, legibility at small sizes, system (variants, responsive logo).
- **Image and illustration:** style (flat, isometric, 3D, hand-drawn, collage), texture and grain, line (weight, constant or variable), lighting, depth of field, framing, art direction (consistency, one photographer), retouching and grading.
- **Web / UI:** density, corner radii, shadows and elevation, borders, hover states, navigation, microtypography, iconography (outline, filled).
- **Motion:** easing, duration, scroll-linked effects, reveal, parallax, hover feedback. If a skill for naming animation effects is available, use it.
- **Material and print / packaging:** paper, finishes (embossing, spot varnish, foil), printing (offset, screen print, risograph), material, pack shape.
- **Overall impression (always with a concrete feature):** calm vs energy, raw vs warm, luxury, craft, technical, playful. Never leave an impression alone; name the feature that creates it.

## Capture details

`board.py add` picks the method itself: a direct image link is downloaded; Pinterest, Dribbble, Behance, Savee, Cosmos, Are.na and Unsplash pages give their main image (`og:image`); other pages get **up to 8 screens of 1440×900** in headless Chrome, scrolled like a person with the mouse wheel, one screenshot per screen, cookie banners closed automatically. One page = one inspiration with several screens.

Do not go back to one full-page screenshot: sections sized to the screen height (100vh) stretch to thousands of pixels and content that appears on scroll stays empty.

When the result has `"blocked": true` or the capture failed:
1. If you have a browser-control tool, open the link, close the cookie banner, scroll and save up to ~6 screenshots, then add them as one inspiration: `board.py add <topic_dir> <shot1> <shot2> ... --frames`.
2. Otherwise, or if the page needs a login or captcha, do not work around it. Ask the user to take a screenshot and drop it on the board.

Users can also add images directly on the board: "Upload image", paste from the clipboard, or drop files. A link pasted outside a text field is added as an inspiration.

`board.py recapture <topic_dir> <item_id> [...]` re-takes the screenshots of a link. Its pins are lost (their positions belonged to the old images), so check first whether any pin has a note and tell the user. Stop a running session server before `recapture` and start it again after.

## Old sessions

Folders from the previous version (dated, with `pins.json` and no `board.json`) appear on the topics screen as "Old format" and open read-only. Do not convert or edit them. New work goes to topic boards.

## Errors

- `No module named PIL`: Pillow is missing. Ask, then `python3 -m pip install --user Pillow`.
- Port in use: the server takes the next free port and prints it in `BOARD_URL`.
- "Google Chrome not found": install Chrome or set the `CHROME_PATH` environment variable to the browser file. Until then, use direct image links and uploads.
- HEIC or TIFF files outside macOS: ask the user to convert them to JPG or PNG.
- Empty or cut screenshot (a page that loads content in an unusual way): use the browser-tool fallback above.
