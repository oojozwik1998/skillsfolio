import { badgeTones } from '../../../lib/ui';
import Disclosure from './Disclosure.astro';

const body =
  '<ul class="type-text-medium list-disc space-y-1 pl-5"><li>The skill checks your tools and whether your files are excluded from git.</li><li>It asks for your CV.</li></ul>';

/**
 * Expandable section built on native details/summary. Enter and Space toggle it;
 * a link to its id opens it. The chevron is decorative.
 */
export default {
  title: 'Patterns/Disclosure',
  component: Disclosure,
  tags: ['autodocs'],
  argTypes: {
    badge: { control: 'inline-radio', options: [undefined, ...badgeTones] },
    open: { control: 'boolean' },
  },
};

export const Closed = { args: { id: 'step-1', number: 1, title: 'You add your CV', badge: 'you', slots: { default: body } } };
export const Open = { args: { id: 'step-2', number: 2, title: 'It builds a fact base', badge: 'skill', open: true, slots: { default: body } } };
export const TitleOnly = { args: { id: 'faq-1', title: 'What happens to my data?', slots: { default: body } } };
export const LongTitle = {
  args: {
    id: 'step-9',
    number: 9,
    title: 'It decides what to do when the offer asks for something your CV does not show',
    badge: 'skill',
    slots: { default: body },
  },
};
