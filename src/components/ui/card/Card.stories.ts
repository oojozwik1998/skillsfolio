import { cardAccents } from '../../../lib/ui';
import Card from './Card.astro';

const content = '<h3 class="type-heading-small">Always</h3><ul class="type-text-medium list-disc pl-5"><li>Facts come from your CV or your answers.</li><li>Dates and titles stay exactly as written.</li></ul>';

/**
 * Static block for related content. Per design.md (decision D-008) it has no border,
 * 2rem padding and 2rem between children. Use Link card when the whole block navigates.
 */
export default {
  title: 'Composites/Card',
  component: Card,
  tags: ['autodocs'],
  argTypes: { accent: { control: 'inline-radio', options: cardAccents } },
};

export const Default = { args: { accent: 'none', slots: { default: content } } };
export const Success = { args: { accent: 'success', slots: { default: content } } };
export const Warning = { args: { accent: 'warning', slots: { default: content } } };
export const Danger = { args: { accent: 'danger', slots: { default: content } } };
export const Empty = { args: { accent: 'none', slots: { default: '<p class="type-text-medium text-text-subtle">Nothing here yet.</p>' } } };
