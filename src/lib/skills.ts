import { z } from 'zod';

export const SKILL_NAME_PATTERN = /^[a-z0-9]+(-[a-z0-9]+)*$/;

export const skillSchema = z.object({
  name: z.string().regex(SKILL_NAME_PATTERN, 'Use lowercase letters, digits and hyphens.'),
  description: z.string().trim().min(1).max(1024),
});

/** Uses the folder as the skill id and stops the build when `name` differs from it. */
export function skillIdFromPath(entryPath: string, name: unknown): string {
  const folder = entryPath.split('/')[0] ?? '';
  if (name !== folder) {
    throw new Error(`Skill "${entryPath}": name "${String(name)}" must equal the folder name "${folder}".`);
  }
  return folder;
}

export function installCommand(repository: string, skillName: string): string {
  return `npx skills add ${repository} --skill ${skillName}`;
}

export function sourceUrl(repository: string, skillName: string): string {
  return `https://github.com/${repository}/tree/main/skills/${skillName}`;
}

export function sortByName<T extends { data: { name: string } }>(skills: readonly T[]): T[] {
  return [...skills].sort((a, b) => a.data.name.localeCompare(b.data.name));
}
