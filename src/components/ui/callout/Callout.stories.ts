import { calloutAppearances } from '../../../lib/ui';
import Callout from './Callout.astro';

/** A side note or an example. Not for errors. */
export default {
  title: 'Composites/Callout',
  component: Callout,
  tags: ['autodocs'],
  argTypes: { appearance: { control: 'inline-radio', options: calloutAppearances } },
};

export const Note = {
  args: {
    appearance: 'note',
    slots: { default: 'Your answers and rejected suggestions go into the fact base, so the next offer starts with more knowledge.' },
  },
};
export const Example = {
  args: {
    appearance: 'example',
    label: 'From testing',
    slots: { default: 'Sam Example pasted a CV as a scan, and the skill asked to check two dates it could not read.' },
  },
};
