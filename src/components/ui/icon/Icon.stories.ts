import { iconNames } from '../../../lib/ui';
import Icon from './Icon.astro';

/** Decorative 16 px icons drawn with the text color. Hidden from screen readers. */
export default {
  title: 'Primitives/Icon',
  component: Icon,
  tags: ['autodocs'],
  argTypes: { name: { control: 'inline-radio', options: iconNames } },
};

export const ArrowRight = { args: { name: 'arrow-right' } };
export const ChevronDown = { args: { name: 'chevron-down' } };
export const Loop = { args: { name: 'loop' } };
export const SubtleColor = { args: { name: 'arrow-right', class: 'text-text-subtle' } };
export const RotatedByParent = { args: { name: 'chevron-down', class: 'rotate-180' } };
