import type { StorybookConfig } from '@storybook-astro/framework';

const config: StorybookConfig = {
  stories: ['../src/components/ui/**/*.stories.@(ts|tsx)'],
  addons: ['@storybook/addon-docs', '@storybook/addon-a11y'],
  core: { disableTelemetry: true },
  framework: {
    name: '@storybook-astro/framework',
    options: {},
  },
};

export default config;
