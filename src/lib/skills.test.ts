import { describe, expect, it } from 'vitest';
import { installCommand, skillIdFromPath, skillSchema, sortByName, sourceUrl } from './skills';

describe('skillSchema', () => {
  const valid = { name: 'my-skill-2', description: 'Does something useful.' };

  it('accepts valid metadata', () => {
    expect(skillSchema.parse(valid)).toEqual(valid);
  });

  it.each(['My-Skill', 'my_skill', 'my skill', '-my-skill', 'my-skill-', 'my--skill', ''])(
    'rejects the name "%s"',
    (name) => {
      expect(skillSchema.safeParse({ ...valid, name }).success).toBe(false);
    },
  );

  it.each([
    ['empty', ''],
    ['blank', '   '],
    ['too long', 'a'.repeat(1025)],
  ])('rejects a description that is %s', (_label, description) => {
    expect(skillSchema.safeParse({ ...valid, description }).success).toBe(false);
  });

  it('rejects missing fields', () => {
    expect(skillSchema.safeParse({}).success).toBe(false);
  });
});

describe('skillIdFromPath', () => {
  it('returns the folder when it equals the name', () => {
    expect(skillIdFromPath('my-skill/SKILL.md', 'my-skill')).toBe('my-skill');
  });

  it('throws when the name differs from the folder', () => {
    expect(() => skillIdFromPath('my-skill/SKILL.md', 'other')).toThrow('must equal the folder name "my-skill"');
  });

  it('throws when the name is missing', () => {
    expect(() => skillIdFromPath('my-skill/SKILL.md', undefined)).toThrow('name "undefined"');
  });
});

describe('installCommand', () => {
  it('builds the skills CLI command', () => {
    expect(installCommand('owner/repo', 'my-skill')).toBe('npx skills add owner/repo --skill my-skill');
  });
});

describe('sourceUrl', () => {
  it('points to the skill folder on GitHub', () => {
    expect(sourceUrl('owner/repo', 'my-skill')).toBe('https://github.com/owner/repo/tree/main/skills/my-skill');
  });
});

describe('sortByName', () => {
  it('sorts by name without changing the input', () => {
    const input = [{ data: { name: 'zebra' } }, { data: { name: 'alpha' } }];

    expect(sortByName(input).map((skill) => skill.data.name)).toEqual(['alpha', 'zebra']);
    expect(input[0]?.data.name).toBe('zebra');
  });
});
