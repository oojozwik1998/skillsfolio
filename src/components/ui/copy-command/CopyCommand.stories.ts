import CopyCommand from './CopyCommand.astro';

/** Shows a command and copies it in one click. The result is announced to screen readers. */
export default {
  title: 'Composites/Copy command',
  component: CopyCommand,
  tags: ['autodocs'],
};

export const Default = { args: { command: 'npx skills add oojozwik1998/skills-folio --skill example-skill' } };
export const LongCommand = {
  args: { command: 'git clone https://github.com/oojozwik1998/tailor-my-cv.git my-applications-for-the-autumn-2026-search' },
};
