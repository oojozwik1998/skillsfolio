import AsciiField from './AsciiField.astro';

/**
 * Decorative field of random characters behind the home page hero. Large wave shapes drift
 * through it and a soft glow follows the mouse. Hidden from screen readers; static with reduced motion.
 */
export default {
  title: 'Patterns/ASCII field',
  component: AsciiField,
  tags: ['autodocs'],
  parameters: { layout: 'fullscreen' },
};

/** Preview layout: fills the width at a fixed height. Hover to see the glow. */
export const Contained = { args: { layout: 'contained' } };
