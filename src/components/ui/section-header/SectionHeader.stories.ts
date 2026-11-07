import SectionHeader from './SectionHeader.astro';

/** h2 and optional subtitle for a page section. Label the section with aria-labelledby set to the same id. */
export default {
  title: 'Patterns/Section header',
  component: SectionHeader,
  tags: ['autodocs'],
};

export const WithSubtitle = {
  args: { id: 'steps-heading', title: 'Step by step', subtitle: 'The examples come from tests with a fictional person.' },
};
export const TitleOnly = { args: { id: 'truth-heading', title: 'Where the line of truth is' } };
