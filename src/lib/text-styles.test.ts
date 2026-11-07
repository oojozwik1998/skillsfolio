import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { generatedTextStyles, utilityTextStyles } from './text-styles';

const read = (path: string) => readFileSync(new URL(path, import.meta.url), 'utf8');

describe('utilityTextStyles', () => {
  it('reads type-* utilities, maps font aliases and fills a zero letter spacing', () => {
    const css = '@utility type-body { font-family: var(--font-body); font-size: 1rem; }';
    expect(utilityTextStyles(css)).toEqual({
      body: {
        'font-family': 'var(--ds-font-family-body)',
        'font-size': '1rem',
        'letter-spacing': '0em',
      },
    });
  });

  it('keeps unknown values and skips text without a colon', () => {
    const css = '@utility type-x { font-family: serif; stray; letter-spacing: -0.01em }';
    expect(utilityTextStyles(css)).toEqual({ x: { 'font-family': 'serif', 'letter-spacing': '-0.01em' } });
  });
});

describe('design-system text styles', () => {
  it('match the type-* utilities used by the site', () => {
    const site = utilityTextStyles(read('../styles/global.css'));
    const generated = generatedTextStyles(read('../components/ui/tokens/text-styles.css'));
    expect(Object.keys(generated).length).toBeGreaterThan(0);
    expect(site).toEqual(generated);
  });

  it('are all shown in the Foundations story', () => {
    const story = read('../components/ui/foundations/Foundations.astro');
    const shown = [...story.matchAll(/'type-([a-z-]+)'/g)].map(([, name]) => name);
    expect(shown).toEqual(Object.keys(utilityTextStyles(read('../styles/global.css'))));
  });
});
