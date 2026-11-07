import Foundations from './Foundations.astro';

export default {
  title: 'Foundations',
  component: Foundations,
  argTypes: {
    section: { control: 'inline-radio', options: ['color', 'typography', 'spacing'] },
  },
};

export const Color = { args: { section: 'color' } };
export const Typography = { args: { section: 'typography' } };
export const Spacing = { args: { section: 'spacing' } };
