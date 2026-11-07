import { addons } from 'storybook/manager-api';
import { themes } from 'storybook/theming';

// Storybook's own interface (sidebar, toolbar, panels) in dark.
addons.setConfig({ theme: themes.dark });
