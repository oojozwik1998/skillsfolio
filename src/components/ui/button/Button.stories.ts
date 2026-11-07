import { buttonAppearances } from '../../../lib/ui';
import Button from './Button.astro';

/**
 * Native button for actions such as copying. Use Text link for navigation.
 * Hover, pressed and focus come from the browser; tab to the button to see the focus ring.
 */
export default {
  title: 'Primitives/Button',
  component: Button,
  tags: ['autodocs'],
  argTypes: {
    appearance: { control: 'inline-radio', options: buttonAppearances },
    type: { control: 'inline-radio', options: ['button', 'submit', 'reset'] },
    disabled: { control: 'boolean' },
  },
};

export const Default = { args: { appearance: 'secondary', slots: { default: 'Copy' } } };
export const Disabled = { args: { appearance: 'secondary', disabled: true, slots: { default: 'Copy' } } };
export const LongLabel = { args: { appearance: 'secondary', slots: { default: 'Copy failed, try again' } } };
