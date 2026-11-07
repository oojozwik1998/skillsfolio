import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { skillIdFromPath, skillSchema } from './lib/skills';

const skills = defineCollection({
  loader: glob({
    base: './skills',
    pattern: '*/SKILL.md',
    generateId: ({ entry, data }) => skillIdFromPath(entry, data.name),
  }),
  schema: skillSchema,
});

export const collections = { skills };
