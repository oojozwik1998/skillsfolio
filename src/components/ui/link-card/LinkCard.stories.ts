import LinkCard from './LinkCard.astro';

/** A card that opens another page. The whole card is one link; the title is its name. */
export default {
  title: 'Composites/Link card',
  component: LinkCard,
  tags: ['autodocs'],
  argTypes: { headingLevel: { control: 'inline-radio', options: [2, 3] } },
};

export const Default = {
  args: { href: '/skills/example-skill/', title: 'example-skill', description: 'A short example that shows how a skill is described.' },
};
export const LongContent = {
  args: {
    href: '/skills/tailor-my-cv/',
    title: 'tailor-my-cv-with-a-much-longer-name',
    description:
      'Paste a job offer. The skill assesses your fit and makes a CV for that offer, in your layout and using only true facts. With each application, it knows more about you.',
  },
};
