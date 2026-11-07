import InlineCode from './InlineCode.astro';

/** Short code, paths and commands inside text. Use Copy command for anything the reader should copy. */
export default {
  title: 'Primitives/Inline code',
  component: InlineCode,
  tags: ['autodocs'],
};

export const Default = { args: { slots: { default: 'cv-rules.md' } } };
export const LongValue = {
  args: { slots: { default: 'applications/2026-11-acme-senior-product-designer/offer-with-a-very-long-name.md' } },
  parameters: { viewport: { defaultViewport: 'mobile1' } },
};
