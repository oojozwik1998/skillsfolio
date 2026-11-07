import { linkTones } from '../../../lib/ui';
import TextLink from './TextLink.astro';

/** Navigation to another page or site. Underlines on hover; focus shows the focus ring. Text names the destination. */
export default {
  title: 'Primitives/Text link',
  component: TextLink,
  tags: ['autodocs'],
  argTypes: { tone: { control: 'inline-radio', options: linkTones } },
};

export const Default = { args: { href: '/', tone: 'default', slots: { default: 'Skills Folio' } } };
export const Subtle = { args: { href: '/', tone: 'subtle', slots: { default: 'All skills' } } };
export const LongText = {
  args: { href: '/', tone: 'subtle', slots: { default: 'View the source of this skill in the GitHub repository' } },
};
