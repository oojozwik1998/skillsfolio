import type { Preview } from '@storybook-astro/framework';
import '@fontsource-variable/mona-sans';
import '@fontsource/poppins/400.css';
import '../src/styles/global.css';

const preview: Preview = {
  globalTypes: {
    theme: {
      description: 'Color theme',
      toolbar: {
        title: 'Theme',
        icon: 'mirror',
        items: [
          { value: 'system', title: 'System' },
          { value: 'light', title: 'Light' },
          { value: 'dark', title: 'Dark' },
        ],
        dynamicTitle: true,
      },
    },
  },
  initialGlobals: { theme: 'system' },
  decorators: [
    (story, context) => {
      // Stories are prerendered on the server, where there is no document.
      if (typeof document !== 'undefined') {
        const theme = String(context.globals.theme ?? 'system');
        if (theme === 'system') delete document.documentElement.dataset.theme;
        else document.documentElement.dataset.theme = theme;
      }
      return story();
    },
  ],
  parameters: {
    a11y: { test: 'error' },
  },
};

export default preview;
