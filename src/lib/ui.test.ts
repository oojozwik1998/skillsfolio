import { describe, expect, it } from 'vitest';
import {
  badgeClasses,
  badgeLabels,
  badgeTones,
  buttonClasses,
  calloutClasses,
  cardAccents,
  cardClasses,
  copyLabels,
  copyToClipboard,
  disclosureId,
  iconNames,
  iconPaths,
  linkCardClasses,
  linkClasses,
  linkTones,
  pageHeaderSizes,
  pageTitleClasses,
} from './ui';

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

describe('cardClasses', () => {
  it('has no border and uses the card spacing tokens by default', () => {
    const classes = cardClasses();
    expect(classes).toContain('p-(--ds-space-inset-card)');
    expect(classes).toContain('gap-(--ds-space-stack-card)');
    expect(classes).not.toMatch(/\bborder\b|border-t/);
  });

  it.each(cardAccents.filter((accent) => accent !== 'none'))('adds a strong top edge for the %s accent', (accent) => {
    expect(cardClasses(accent)).toContain('border-t-(length:--ds-border-width-strong)');
  });

  it('uses the you color for the warning accent', () => {
    expect(cardClasses('warning')).toContain('border-t-actor-you-border');
  });
});

describe('linkCardClasses', () => {
  it('changes the surface on hover', () => {
    expect(linkCardClasses).toContain('hover:bg-surface-hovered');
  });
});

describe('calloutClasses', () => {
  it('draws a dashed border for notes by default', () => {
    expect(calloutClasses()).toContain('border-dashed');
  });

  it('has no border for examples', () => {
    expect(calloutClasses('example')).not.toContain('border');
  });
});

describe('copyToClipboard', () => {
  it('reports success after writing the text', async () => {
    const written: string[] = [];
    const clipboard = { writeText: (text: string) => Promise.resolve(void written.push(text)) };
    await expect(copyToClipboard(clipboard, 'npx skills add x')).resolves.toBe(copyLabels.copied);
    expect(written).toEqual(['npx skills add x']);
  });

  it('reports a failure when writing is refused', async () => {
    const clipboard = { writeText: () => Promise.reject(new Error('denied')) };
    await expect(copyToClipboard(clipboard, 'x')).resolves.toBe(copyLabels.failed);
  });

  it('reports a failure when there is no clipboard', async () => {
    await expect(copyToClipboard(undefined, 'x')).resolves.toBe(copyLabels.failed);
  });
});

describe('badgeLabels', () => {
  it('has a visible label for every tone', () => {
    expect(Object.keys(badgeLabels)).toEqual([...badgeTones]);
  });
});

describe('pageTitleClasses', () => {
  it('drops large titles to display-small on phones by default', () => {
    expect(pageTitleClasses()).toContain('type-display-small sm:type-display-large');
  });

  it.each(pageHeaderSizes)('lets long %s titles wrap', (size) => {
    expect(pageTitleClasses(size)).toContain('break-words');
  });

  it('keeps small titles at display-small', () => {
    expect(pageTitleClasses('small')).not.toContain('display-large');
  });
});

describe('disclosureId', () => {
  it('joins the prefix and the number', () => {
    expect(disclosureId('step', 5)).toBe('step-5');
  });
});
