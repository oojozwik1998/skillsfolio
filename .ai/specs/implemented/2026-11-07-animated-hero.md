# Animated hero background

Status: implemented

## Goal

The home page hero gets a quiet, animated background: a field of random monospace characters that keep changing, with drifting brighter patches. The title and lead stay fully readable.

## Behaviour

- A `<canvas>` covers the top of the page at full viewport width, behind the content. It is decorative: `aria-hidden`, no pointer events.
- Characters come from `A-Z a-z 0-9`, drawn in the code font in the subtle text color, so light and dark mode follow the tokens.
- Characters are small (9px on a 6 × 12 px grid).
- Brightness comes from large, abstract wave shapes: sine ribbons whose coordinates are bent by slower sine waves, with soft S-curve edges. They swell, drift and fade. Kept faint so they read as texture.
- Hover (mouse only): a soft glow around the pointer brightens characters and swaps them faster. Both fade to zero at the edge of the radius, so the glow has no rim. Touch and reduced motion do not trigger it.
- A share of characters swaps each tick, which makes the field flicker.
- A CSS mask fades the field out toward the bottom and dims it behind the title.
- About 20 frames per second. Animation pauses when the hero is off screen or the tab is hidden.
- `prefers-reduced-motion: reduce` draws one static frame and does not animate.
- The grid is rebuilt on resize and scaled for high-density screens.

## Code

- `src/lib/ascii-field.ts`: grid creation, character swaps, brightness, frame drawing and the animation controller. Browser APIs are passed in, so everything is unit-tested at 100%.
- `src/components/ui/ascii-field/AsciiField.astro`: markup, mask and a short script that wires the controller to the page.
- `src/pages/index.astro`: renders the field above the page header.

## Done criteria

- `pnpm check` passes.
- Browser test: the home page renders the canvas, hidden from assistive technology, and no horizontal scroll at phone width.
- Checked by eye in light and dark mode, desktop and phone width.
