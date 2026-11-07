import { pageHeaderSizes } from '../../../lib/ui';
import PageHeader from './PageHeader.astro';

/** Title and lead at the top of a page. Holds the page's only h1. Large titles shrink on phones. */
export default {
  title: 'Patterns/Page header',
  component: PageHeader,
  tags: ['autodocs'],
  argTypes: { size: { control: 'inline-radio', options: pageHeaderSizes } },
};

const lead = 'Agent skills by Oskar Jóźwik. Browse them and install any one with a single command.';

export const Large = { args: { title: 'designskills', lead, size: 'large' } };
export const SmallWithBackLink = {
  args: { title: 'example-skill', lead: 'A short example that shows how a skill is described.', backHref: '/', size: 'small' },
};
export const LongTitle = {
  args: { title: 'tailor-my-cv-with-a-very-long-name-that-has-to-wrap', backHref: '/', size: 'small' },
};
export const TitleOnly = { args: { title: 'designskills', size: 'large' } };
