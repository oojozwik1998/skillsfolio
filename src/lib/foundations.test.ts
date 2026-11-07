import { describe, expect, it } from 'vitest';
import { numericScale, tokensByPrefix } from './foundations';

const tokens = {
  'color.surface.canvas': 'var(--a)',
  'color.text.default': 'var(--b)',
  'color.mist.50': 'var(--c)',
  'space.16': 'var(--d)',
  'space.4': 'var(--e)',
  'space.inset.card': 'var(--f)',
};

describe('tokensByPrefix', () => {
  it('keeps tokens under the given prefixes only', () => {
    expect(tokensByPrefix(tokens, ['color.surface', 'color.text'])).toEqual([
      { id: 'color.surface.canvas', cssVar: 'var(--a)' },
      { id: 'color.text.default', cssVar: 'var(--b)' },
    ]);
  });
});

describe('numericScale', () => {
  it('returns numeric steps sorted by size and skips named tokens', () => {
    expect(numericScale(tokens, 'space').map(({ id }) => id)).toEqual(['space.4', 'space.16']);
  });
});
