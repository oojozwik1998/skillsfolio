import { describe, expect, it } from 'vitest';
import { badgeClasses, badgeTones, buttonClasses, iconNames, iconPaths, linkClasses, linkTones } from './ui';

describe('icons', () => {
  it('has path data for every icon name', () => {
    expect(Object.keys(iconPaths)).toEqual([...iconNames]);
    for (const name of iconNames) expect(iconPaths[name]).toMatch(/^M/);
  });
});

describe('linkClasses', () => {
  it('defaults to the default tone', () => {
    expect(linkClasses()).toContain('text-text-default');
  });

  it.each(linkTones)('uses the label style and underlines on hover for the %s tone', (tone) => {
    expect(linkClasses(tone)).toMatch(/type-label .*hover:underline/);
  });

  it('uses subtle text for the subtle tone', () => {
    expect(linkClasses('subtle')).toContain('text-text-subtle');
  });
});

describe('badgeClasses', () => {
  it.each(badgeTones)('uses the %s actor colors', (tone) => {
    expect(badgeClasses(tone)).toContain(`bg-actor-${tone}-background text-actor-${tone}-text`);
  });
});

describe('buttonClasses', () => {
  it('defaults to the secondary appearance with a 44px control height', () => {
    const classes = buttonClasses();
    expect(classes).toContain('bg-action-secondary-background');
    expect(classes).toContain('h-(--ds-size-control-md)');
  });

  it('applies hover and pressed colors only while enabled', () => {
    expect(buttonClasses('secondary')).toMatch(/enabled:hover:bg-action-secondary-hovered .*enabled:active:bg-action-secondary-pressed/);
  });

  it('has a disabled look that does not rely on opacity', () => {
    expect(buttonClasses()).toContain('disabled:text-text-subtle');
    expect(buttonClasses()).not.toContain('opacity');
  });
});
