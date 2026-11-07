import { collection, config, fields } from '@keystatic/core';
import { SKILL_NAME_PATTERN } from './src/lib/skills';

export default config({
  storage: { kind: 'local' },
  collections: {
    skills: collection({
      label: 'Skills',
      path: 'skills/*/SKILL',
      slugField: 'name',
      format: { contentField: 'body' },
      entryLayout: 'content',
      schema: {
        name: fields.slug({
          name: {
            label: 'Name',
            description: 'Lowercase with hyphens, e.g. my-skill.',
            validation: {
              isRequired: true,
              pattern: {
                regex: SKILL_NAME_PATTERN,
                message: 'Use lowercase letters, digits and hyphens.',
              },
            },
          },
        }),
        description: fields.text({
          label: 'Description',
          description: 'What the skill does and when to use it.',
          multiline: true,
          validation: { isRequired: true, length: { min: 1, max: 1024 } },
        }),
        body: fields.markdoc({
          label: 'Instructions',
          extension: 'md',
        }),
      },
    }),
  },
});
