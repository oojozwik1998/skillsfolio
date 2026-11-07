import js from '@eslint/js';
import astro from 'eslint-plugin-astro';
import tseslint from 'typescript-eslint';

export default [
  {
    ignores: ['dist/', 'storybook-static/', '.astro/', 'coverage/', 'playwright-report/', 'test-results/', 'tailor-my-cv/'],
  },
  js.configs.recommended,
  ...tseslint.configs.strict,
  ...astro.configs.recommended,
  ...astro.configs['flat/jsx-a11y-recommended'],
];
