import { badgeTones } from '../../../lib/ui';
import Badge from './Badge.astro';

/** Says who performs a step. The label is always visible, so color is never the only signal. */
export default {
  title: 'Primitives/Badge',
  component: Badge,
  tags: ['autodocs'],
  argTypes: { tone: { control: 'inline-radio', options: badgeTones } },
};

export const Skill = { args: { tone: 'skill', slots: { default: 'Skill' } } };
export const You = { args: { tone: 'you', slots: { default: 'You' } } };
