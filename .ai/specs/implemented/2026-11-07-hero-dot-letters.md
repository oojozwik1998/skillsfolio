# Hero variant: dot-matrix letters

Status: implemented

## Goal

A second version of the animated hero background, to compare with the character field and keep one. Same idea as the character field, but the letters are much larger and drawn from dots. Under the mouse the dots scatter. When the mouse moves away they spring back into letters.

## Behaviour

- Letters `A-Z 0-9` drawn from a 5 × 7 dot matrix, dots 2px on a 5px pitch, so one letter is about 25 × 35 px.
- About 40% of letters change every second, like the flicker of the character field. Dots fade quickly between the old and the new letter.
- The same faint drifting wave shapes as the character field set the brightness.
- Mouse within ~200px breaks letters apart over a wide area: each dot drifts out at its own angle (up to about 75° off straight) with its own strength and a light random kick. Motion stays calm: gentle push, weak spring, no jitter. A spring pulls every dot back to its place, with damping, so letters re-form smoothly. Displaced dots are slightly brighter.
- Physics runs every animation frame (about 6,000 to 17,000 dots on a desktop hero, simple arithmetic only).
- Same as the character field: decorative (`aria-hidden`), pauses off screen or in a background tab, static with reduced motion and no reaction to the mouse, touch ignored.

## Decision

The owner compared both variants on the home page and in Storybook and kept the dot letters. The character field, the `variant` prop and the `?hero` switch were removed.

## Code

- `src/lib/ascii-field.ts`: glyphs, waves, field creation, letter swaps, physics, drawing and the animation controller, 100% unit-tested. It replaces the character field logic.
- `src/components/ui/ascii-field/AsciiField.astro` keeps its name and the `layout` prop.

## Done criteria

- `pnpm check` passes.
- The owner compared both variants and picked the dot letters; the other variant and the `?hero` switch are removed.
