import AsciiField from './AsciiField.astro';

/**
 * Decorative field of large dot-matrix letters behind the home page hero. Letters keep changing,
 * faint waves drift through them, and dots scatter under the mouse, then spring back.
 * Hidden from screen readers; static with reduced motion.
 */
export default {
  title: 'Patterns/ASCII field',
  component: AsciiField,
  tags: ['autodocs'],
  parameters: { layout: 'fullscreen' },
};

/** Preview layout: fills the width at a fixed height. Hover to scatter the dots. */
export const Contained = { args: { layout: 'contained' } };
